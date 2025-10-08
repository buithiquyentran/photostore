"""
Search API Routes - Image & Text Search

Endpoints:
- POST /search/image - Tìm kiếm bằng ảnh
- POST /search/text - Tìm kiếm bằng text
- POST /search/rebuild - Rebuild FAISS index cho project
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from PIL import Image
import io
from typing import Optional

from db.session import get_session
from dependencies.dependencies import get_current_user
from services.search.embeddings_service import (
    search_by_image,
    search_by_text,
    rebuild_project_embeddings
)
from services.search.faiss_index import get_project_stats
from models.projects import Projects
from models.folders import Folders
from utils.path_builder import build_file_url, build_full_path
from core.config import settings

router = APIRouter(prefix="/search", tags=["Search"])


def format_asset_response(asset, session: Session) -> dict:
    """
    Format asset data giống như upload-images API response.
    """
    # Lấy thông tin project và folder
    folder = session.get(Folders, asset.folder_id) if asset.folder_id else None
    project = session.get(Projects, folder.project_id) if folder else None
    
    # Build file URL
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    file_url = build_file_url(session, project.id, folder.id, asset.system_name, base_url) if project and folder else ""
    
    # Build folder path using build_full_path function
    folder_path = build_full_path(session, project.id, folder.id) if project and folder else ""
    
    return {
        "status": 1,
        "id": asset.id,
        "name": asset.name,
        "original_name": asset.name,  # Giả sử name là original_name
        "system_name": asset.system_name,
        "file_url": file_url,
        "file_extension": asset.file_extension,
        "file_type": asset.file_type,
        "format": asset.format,
        "file_size": asset.file_size,
        "width": asset.width,
        "height": asset.height,
        "project_slug": project.slug if project else "",
        "folder_path": folder_path,
        "is_private": asset.is_private,
        "created_at": asset.created_at,
        "updated_at": asset.updated_at
    }


def validate_project_ownership(session: Session, project_id: int, user_id: int) -> Projects:
    """
    Validate project tồn tại và thuộc về user.
    
    Args:
        session: Database session
        project_id: ID của project
        user_id: ID của user
    
    Returns:
        Projects object nếu valid
    
    Raises:
        HTTPException nếu project không tồn tại hoặc không thuộc về user
    """
    project = session.get(Projects, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    
    if project.user_id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="Bạn không có quyền truy cập project này"
        )
    
    return project


@router.post("/image")
async def search_by_image_upload(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),  # Optional - nếu None thì search tất cả projects của user
    folder_id: Optional[int] = Form(None),
    k: int = Form(10),
    similarity_threshold: float = Form(0.7),  # Ngưỡng similarity (0.7 = 70% giống nhau)
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tìm kiếm ảnh tương tự bằng cách upload 1 ảnh.
    
    Args:
        file: File ảnh upload
        project_id: (Optional) ID của project cần tìm. Nếu None thì search tất cả projects của user
        folder_id: (Optional) Chỉ tìm trong folder này
        k: Số lượng kết quả trả về (default: 10)
    
    Returns:
        {
            "status": 1,
            "data": [...assets...],
            "total": <số lượng>
        }
    """
    try:
        # 🔒 SECURITY: Validate project ownership (nếu có project_id)
        if project_id:
            validate_project_ownership(session, project_id, current_user.id)
        
        # Đọc ảnh
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        
        # Tìm kiếm
        assets = search_by_image(
            session=session,
            project_id=project_id,
            image=image,
            k=k,
            folder_id=folder_id,
            user_id=current_user.id,
            similarity_threshold=similarity_threshold
        )
        
        # Format response giống như upload-images API
        results = []
        for asset in assets:
            formatted_asset = format_asset_response(asset, session)
            results.append({
                "file": formatted_asset,
                "message": "Search result",
                "result": True
            })
        
        return {
            "data": {
                "searchResults": results[0] if len(results) == 1 else results
            },
            "extensions": {
                "cost": {
                    "requestedQueryCost": 0,
                    "maximumAvailable": 50000
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/text")
def search_by_text_query(
    query: str = Form(...),
    project_id: Optional[int] = Form(None),  # Optional - nếu None thì search tất cả projects của user
    folder_id: Optional[int] = Form(None),
    k: int = Form(10),
    similarity_threshold: float = Form(0.7),  # Ngưỡng similarity (0.7 = 70% giống nhau)
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tìm kiếm ảnh bằng text query (semantic search).
    
    Args:
        query: Text query (e.g., "a cat on the sofa", "sunset beach")
        project_id: (Optional) ID của project cần tìm. Nếu None thì search tất cả projects của user
        folder_id: (Optional) Chỉ tìm trong folder này
        k: Số lượng kết quả trả về (default: 10)
    
    Returns:
        {
            "status": 1,
            "data": [...assets...],
            "total": <số lượng>,
            "query": "<text query>"
        }
    """
    try:
        # 🔒 SECURITY: Validate project ownership (nếu có project_id)
        if project_id:
            validate_project_ownership(session, project_id, current_user.id)
        
        # Tìm kiếm
        assets = search_by_text(
            session=session,
            project_id=project_id,
            query_text=query,
            k=k,
            folder_id=folder_id,
            user_id=current_user.id,
            similarity_threshold=similarity_threshold
        )
        
        # Format response giống như upload-images API
        results = []
        for asset in assets:
            formatted_asset = format_asset_response(asset, session)
            results.append({
                "file": formatted_asset,
                "message": "Search result",
                "result": True
            })
        
        return {
            "data": {
                "searchResults": results[0] if len(results) == 1 else results
            },
            "extensions": {
                "cost": {
                    "requestedQueryCost": 0,
                    "maximumAvailable": 50000
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/rebuild")
def rebuild_project_index(
    project_id: int = Form(...),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Rebuild FAISS index cho project từ database.
    
    Sử dụng khi:
    - Index bị lỗi
    - Sau khi restore database
    - Sau khi migration
    
    Args:
        project_id: ID của project cần rebuild
    
    Returns:
        {
            "status": 1,
            "message": "Index rebuilt successfully",
            "stats": {...}
        }
    """
    try:
        # 🔒 SECURITY: Validate project ownership
        validate_project_ownership(session, project_id, current_user.id)
        
        # Rebuild index
        rebuild_project_embeddings(session, project_id)
        
        # Get stats
        stats = get_project_stats(project_id)
        
        return {
            "status": 1,
            "message": f"Project {project_id} index rebuilt successfully",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")

@router.get("/rebuild-all")
def rebuild_all_projects_index(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Rebuild FAISS index cho tất cả projects của user.
    
    Sử dụng khi:
    - Các index bị lỗi
    - Sau khi restore database
    - Sau khi migration
    
    Returns:
        {
            "status": 1,
            "message": "All indexes rebuilt successfully",
            "projects": [...]
        }
    """
    try:
        # Lấy tất cả projects của user
        from models.projects import Projects
        user_projects = session.exec(
            select(Projects).where(Projects.user_id == current_user.id)
        ).all()
        
        if not user_projects:
            return {
                "status": 1,
                "message": "No projects found for user",
                "projects": []
            }
        
        # Rebuild index cho từng project
        results = []
        for project in user_projects:
            try:
                rebuild_project_embeddings(session, project.id)
                stats = get_project_stats(project.id)
                results.append({
                    "project_id": project.id,
                    "name": project.name,
                    "status": "success",
                    "stats": stats
                })
            except Exception as e:
                results.append({
                    "project_id": project.id,
                    "name": project.name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "status": 1,
            "message": "All indexes rebuilt",
            "projects": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")


@router.get("/stats/{project_id}")
def get_search_stats(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Lấy thống kê về FAISS index của project.
    
    Returns:
        {
            "project_id": <id>,
            "total_vectors": <số lượng vectors>,
            "indexed": true/false,
            "dimension": 512
        }
    """
    # 🔒 SECURITY: Validate project ownership
    validate_project_ownership(session, project_id, current_user.id)
    
    stats = get_project_stats(project_id)
    stats["project_id"] = project_id
    
    return stats

