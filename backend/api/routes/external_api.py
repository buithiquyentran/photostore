"""
External API routes - truy cập thông qua API key
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from PIL import Image
import io

from db.session import get_session
from models import Projects, Folders, Assets
from dependencies.api_key_middleware import verify_api_key
from services.search.embeddings_service import search_by_image, search_by_text
from utils.slug import create_slug
from utils.path_builder import build_full_path, build_file_url
from core.config import settings

router = APIRouter(prefix="/external", tags=["External API"])


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


# ============================================
# Request/Response Models
# ============================================

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None

class FolderResponse(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int]
    created_at: datetime
    path: str

class AssetResponse(BaseModel):
    id: int
    name: str
    file_url: str
    file_type: str
    file_size: int
    width: Optional[int]
    height: Optional[int]
    created_at: datetime
    folder_path: str
    is_private: bool

# ============================================
# Folder Management
# ============================================

@router.post("/folders", response_model=FolderResponse)
async def create_folder(
    folder: FolderCreate,
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """
    Tạo folder mới trong project.
    Project được xác định tự động từ API key.
    """
    try:
        # Validate parent folder nếu có
        if folder.parent_id:
            parent = session.get(Folders, folder.parent_id)
            if not parent or parent.project_id != project.id:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "status": "error",
                        "message": "Parent folder not found"
                    }
                )

        # Tạo slug
        folder_slug = create_slug(folder.name)
        
        # Kiểm tra trùng tên trong cùng parent
        existing = session.exec(
            select(Folders)
            .where(
                Folders.project_id == project.id,
                Folders.parent_id == folder.parent_id,
                Folders.name == folder.name
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Folder with this name already exists"
                }
            )

        # Tạo folder mới
        new_folder = Folders(
            project_id=project.id,
            name=folder.name,
            slug=folder_slug,
            parent_id=folder.parent_id,
            description=folder.description
        )
        session.add(new_folder)
        session.commit()
        session.refresh(new_folder)

        # Build full path
        full_path = build_full_path(session, project.id, new_folder.id)

        return FolderResponse(
            id=new_folder.id,
            name=new_folder.name,
            slug=new_folder.slug,
            parent_id=new_folder.parent_id,
            created_at=new_folder.created_at,
            path=full_path
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )

@router.get("/folders", response_model=List[FolderResponse])
def list_folders(
    parent_id: Optional[int] = None,
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Lấy danh sách folders trong project"""
    try:
        query = select(Folders).where(
            Folders.project_id == project.id,
            Folders.parent_id == parent_id
        )
        folders = session.exec(query).all()

        return [
            FolderResponse(
                id=f.id,
                name=f.name,
                slug=f.slug,
                parent_id=f.parent_id,
                created_at=f.created_at,
                path=build_full_path(session, project.id, f.id)
            )
            for f in folders
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )

@router.delete("/folders/{folder_id}")
def delete_folder(
    folder_id: int,
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Xóa folder (chỉ xóa được folder trống)"""
    try:
        folder = session.get(Folders, folder_id)
        if not folder or folder.project_id != project.id:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": "Folder not found"
                }
            )

        # Kiểm tra folder có rỗng không
        has_children = session.exec(
            select(Folders).where(Folders.parent_id == folder_id)
        ).first() is not None

        has_assets = session.exec(
            select(Assets).where(Assets.folder_id == folder_id)
        ).first() is not None

        if has_children or has_assets:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Cannot delete non-empty folder"
                }
            )

        session.delete(folder)
        session.commit()

        return {
            "status": "success",
            "message": "Folder deleted"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )

# ============================================
# Asset Management
# ============================================

@router.post("/assets/upload", response_model=List[AssetResponse])
async def upload_assets(
    files: List[UploadFile] = File(...),
    folder_id: Optional[int] = Form(None),
    is_private: bool = Form(False),
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Upload files vào project/folder"""
    try:
        # Validate folder nếu có
        if folder_id:
            folder = session.get(Folders, folder_id)
            if not folder or folder.project_id != project.id:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "status": "error",
                        "message": "Folder not found"
                    }
                )

        results = []
        for file in files:
            # TODO: Implement file upload logic
            # Reuse logic từ user_assets.py
            pass

        return results

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )

@router.get("/assets", response_model=List[AssetResponse])
def list_assets(
    folder_id: Optional[int] = None,
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Lấy danh sách assets trong project/folder"""
    try:
        query = select(Assets).where(Assets.project_id == project.id)
        if folder_id is not None:
            query = query.where(Assets.folder_id == folder_id)
        assets = session.exec(query).all()

        return [
            AssetResponse(
                id=a.id,
                name=a.name,
                file_url=a.file_url,
                file_type=a.file_type,
                file_size=a.file_size,
                width=a.width,
                height=a.height,
                created_at=datetime.fromtimestamp(a.created_at),
                folder_path=a.folder_path,
                is_private=a.is_private
            )
            for a in assets
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )

@router.delete("/assets/{asset_id}")
def delete_asset(
    asset_id: int,
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Xóa asset"""
    try:
        asset = session.get(Assets, asset_id)
        if not asset or asset.project_id != project.id:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": "Asset not found"
                }
            )

        # TODO: Implement file deletion logic
        # Reuse logic từ user_assets.py

        session.delete(asset)
        session.commit()

        return {
            "status": "success",
            "message": "Asset deleted"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )

# ============================================
# Search
# ============================================

@router.post("/search/image")
async def search_by_image_api(
    file: UploadFile = File(...),
    folder_id: Optional[int] = Form(None),
    k: int = Form(10),
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Search bằng hình ảnh"""
    try:
        # Đọc file và chuyển thành PIL Image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Gọi service với image thay vì file
        assets = search_by_image(
            session=session,
            project_id=project.id,
            image=image,
            folder_id=folder_id,
            k=k,
            user_id=None  # Không cần user_id vì đã có project_id
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
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.post("/search/text")
def search_by_text_api(
    query: str = Form(...),
    folder_id: Optional[int] = Form(None),
    k: int = Form(10),
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Search bằng text"""
    try:
        print(f"[DEBUG] Text search: query='{query}', project_id={project.id}, folder_id={folder_id}, k={k}")
        assets = search_by_text(
            session=session,
            project_id=project.id,
            query_text=query,  # Đúng tên tham số là query_text, không phải query
            k=k,
            folder_id=folder_id,
            user_id=None  # Không cần user_id vì đã có project_id
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
        import traceback
        print(f"[ERROR] Search failed: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/search/text")
def search_by_text_external(
    q: str,  # Query text
    k: int = 10,
    similarity_threshold: float = 0.7,
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """
    Search images by text query using CLIP embeddings (External API with API key).
    
    GET /api/external/search/text?q=a+cat+on+sofa
    Headers: X-API-Key: your_api_key
    
    Uses CLIP to find images with content similar to text query.
    Searches only in the project associated with the API key.
    
    Args:
        q: Text query (e.g., "a cat on sofa", "sunset beach", "woman in white shirt")
        k: Number of results (default: 10)
        similarity_threshold: Minimum similarity 0-1 (default: 0.7 = 70%)
    
    Returns:
        Images with similar content to the query
    """
    try:
        # Search by CLIP embeddings in this project
        assets = search_by_text(
            session=session,
            project_id=project.id,  # Only search in API key's project
            query_text=q,
            k=k,
            folder_id=None,
            user_id=project.user_id,
            similarity_threshold=similarity_threshold
        )
        
        # Format response
        results = []
        for asset in assets:
            formatted_asset = format_asset_response(asset, session)
            results.append({
                "file": formatted_asset,
                "message": "Semantic search result",
                "result": True
            })
            
        return {
            "status": 1,
            "data": {
                "searchResults": results[0] if len(results) == 1 else results
            },
            "query": q,
            "method": "clip_embeddings",
            "project_id": project.id,
            "total": len(results),
            "similarity_threshold": similarity_threshold
        }
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Text search failed: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Text search failed: {str(e)}"
        )