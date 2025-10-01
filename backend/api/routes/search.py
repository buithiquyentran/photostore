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

router = APIRouter(prefix="/search", tags=["Search"])


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
            user_id=current_user.id
        )
        
        # Format response
        results = []
        for asset in assets:
            results.append({
                "id": asset.id,
                "name": asset.name,
                "path": asset.path,
                "width": asset.width,
                "height": asset.height,
                "format": asset.format,
                "folder_id": asset.folder_id,
                "is_favorite": asset.is_favorite,
                "created": asset.created.isoformat()
            })
        
        return {
            "status": 1,
            "data": results,
            "total": len(results),
            "query_type": "image"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/text")
def search_by_text_query(
    query: str = Form(...),
    project_id: Optional[int] = Form(None),  # Optional - nếu None thì search tất cả projects của user
    folder_id: Optional[int] = Form(None),
    k: int = Form(10),
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
            user_id=current_user.id
        )
        
        # Format response
        results = []
        for asset in assets:
            results.append({
                "id": asset.id,
                "name": asset.name,
                "path": asset.path,
                "width": asset.width,
                "height": asset.height,
                "format": asset.format,
                "folder_id": asset.folder_id,
                "is_favorite": asset.is_favorite,
                "created": asset.created.isoformat()
            })
        
        return {
            "status": 1,
            "data": results,
            "total": len(results),
            "query": query,
            "query_type": "text"
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

