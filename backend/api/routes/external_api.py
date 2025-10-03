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
        results = search_by_image(
            session=session,
            project_id=project.id,
            image=image,
            folder_id=folder_id,
            k=k,
            user_id=None  # Không cần user_id vì đã có project_id
        )
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Search failed"
            }
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
        results = search_by_text(
            session=session,
            project_id=project.id,
            query_text=query,  # Đúng tên tham số là query_text, không phải query
            k=k,
            folder_id=folder_id,
            user_id=None  # Không cần user_id vì đã có project_id
        )
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        import traceback
        print(f"[ERROR] Search failed: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": f"Search failed: {str(e)}"
            }
        )
