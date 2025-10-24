"""
External API routes - truy cập thông qua API key
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import Query

from PIL import Image
import io
from pathlib import Path
from uuid import uuid4
import io
import os
from fastapi.responses import JSONResponse, FileResponse
import io, os, time
import traceback


from db.session import get_session
from models import Projects, Folders, Assets
from dependencies.api_key_middleware import verify_api_key
from services.search.embeddings_service import search_by_image, search_by_text
from utils.slug import create_slug
from utils.path_builder import build_full_path, build_file_url
from core.config import settings
from db.crud_asset import add_asset
from db.crud_embedding import create_embedding_for_asset
from utils.filename_utils import truncate_filename, split_filename, sanitize_filename
from utils.folder_finder import find_folder_by_path

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

# Ảnh private cho API client
# @router.get("/uploads/{path:path}")
# def get_external_image(path: str, project: Projects = Depends(verify_api_key)):
#     return FileResponse(f"uploads/{path}")


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
UPLOAD_DIR = Path("uploads")
# Constants
MAX_FILENAME_LENGTH = 255  # Maximum length for filename in DB
@router.post("/assets/upload")
async def upload_assets(
    files: List[UploadFile] = File(...),
    folder_slug: str | None = Form(None),  # Sử dụng slug thay vì name
    is_private: bool = Form(False),
    project: Projects = Depends(verify_api_key),
    session: Session = Depends(get_session)
):
    """Upload files vào project/folder"""
    results = []
    
    # Tìm folder theo path slugs hoặc default
    if folder_slug:
        # folder_slug có thể là path: "parent-slug/child-slug"
        try:
            folder = find_folder_by_path(session, project.id, folder_slug)
        except HTTPException as e:
            # Nếu không tìm thấy và là single slug, thử tạo mới ở root
            if "/" not in folder_slug:
                folder = Folders(
                    name=folder_slug.replace("-", " ").title(),  # thu-muc-moi → Thu Muc Moi
                    slug=folder_slug,
                    project_id=project.id,
                    parent_id=None,  # Root folder
                    is_default=False
                )
                session.add(folder)
                session.commit()
                session.refresh(folder)
            else:
                raise e
    else:
        # Tìm default folder
        folder = session.exec(
            select(Folders)
            .where(Folders.project_id == project.id)
            .where(Folders.is_default == True)
        ).first()
        if not folder:
            # Tạo default folder nếu chưa có
            folder = Folders(
                name="Home",
                slug="home",
                project_id=project.id,
                parent_id=None,
                is_default=True
            )
            session.add(folder)
            session.commit()
            session.refresh(folder)
    
    try:
        for file in files:
            # validate mime
            if not file.content_type or not file.content_type.startswith(("image/", "video/")):
                raise HTTPException(400, f"File {file.filename} không hợp lệ (chỉ hỗ trợ image/video)")

            # đọc bytes
            file_bytes = await file.read()
            size = len(file_bytes)

            # lấy dimension nếu là ảnh
            width = height = None
            if file.content_type.startswith("image/"):
                try:
                    with Image.open(io.BytesIO(file_bytes)) as im:
                        width, height = im.size
                except Exception:
                    raise HTTPException(400, f"Ảnh {file.filename} không hợp lệ")

            # Xử lý filename
            original_filename = file.filename or f"file_{uuid4().hex}"
            original_filename = sanitize_filename(original_filename)  # Remove invalid chars
            
            # Split filename và extension
            name, ext = split_filename(original_filename)
            if not ext:  # Nếu không có extension, dùng mime type
                if file.content_type == "image/jpeg":
                    ext = "jpg"
                elif file.content_type == "image/png":
                    ext = "png"
                elif file.content_type == "image/gif":
                    ext = "gif"
                elif file.content_type == "image/webp":
                    ext = "webp"
                else:
                    ext = "bin"
            
            # Tạo filename an toàn cho storage
            storage_filename = f"{uuid4().hex}.{ext}"
            
            # Truncate original filename nếu quá dài
            safe_filename = truncate_filename(original_filename, MAX_FILENAME_LENGTH)
            
            # Build full path từ project và folder slugs
            full_path = build_full_path(session, project.id, folder.id)
            
            # relative path (lưu trong DB)
            object_path = f"{full_path}/{storage_filename}"

            # absolute path (lưu trong ổ cứng)
            save_path = os.path.join(UPLOAD_DIR, object_path).replace("\\", "/")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Lưu file vào local
            with open(save_path, "wb") as f:
                f.write(file_bytes)

            try:
                # Build file URL với full path
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                file_url = build_file_url(session, project.id, folder.id, storage_filename, base_url)
                
                # Lưu asset vào database
                asset_id = add_asset(
                    session=session,
                    project_id=project.id,
                    folder_id=folder.id,
                    name=safe_filename,  # Tên file gốc đã được truncate
                    system_name=storage_filename,  # UUID filename
                    file_extension=ext,
                    file_type=file.content_type,
                    format=file.content_type,  # Sử dụng MIME type làm format
                    file_size=size,
                    path=object_path,
                    file_url=file_url,
                    folder_path=full_path,
                    width=width,
                    height=height,
                    is_private=is_private,
                    is_image=file.content_type.startswith("image/")
                )
                
                # 🔥 TỰ ĐỘNG TẠO EMBEDDING cho ảnh
                # Chỉ tạo embedding nếu là file IMAGE (không phải video)
                if file.content_type.startswith("image/"):
                    try:
                        embedding = create_embedding_for_asset(
                            session=session,
                            asset_id=asset_id,
                            image_bytes=file_bytes
                        )
                        if embedding:
                            print(f"✅ Created embedding for asset {asset_id}")
                        else:
                            print(f"⚠️ Failed to create embedding for asset {asset_id}")
                    except Exception as emb_err:
                        # Không raise error, chỉ log warning
                        # Upload vẫn thành công nhưng không có embedding
                        print(f"⚠️ Embedding creation failed for asset {asset_id}: {emb_err}")
    
            except Exception as e:
                if os.path.exists(save_path):
                    os.remove(save_path)
                raise HTTPException(status_code=500, detail=f"DB insert failed: {e}")

            preview_url = f"/uploads/{object_path}"
            safe_path = object_path.replace("\\", "/")
            file_path = (UPLOAD_DIR / safe_path).resolve()

            
            results.append({
                "status": 1,
                "id": asset_id,
                "name": safe_filename,  # Tên file gốc đã được truncate
                "original_name": original_filename,  # Tên file gốc trước khi truncate
                "system_name": storage_filename,  # UUID filename
                "file_url": file_url,
                "file_extension": ext,
                "file_type": file.content_type,
                "format": file.content_type,  # Sử dụng MIME type làm format
                "file_size": size,
                "width": width,
                "height": height,
                "project_slug": project.slug,
                "folder_path": full_path,  # Full path từ project → parent folders → current folder
                "is_private": is_private,
                "created_at": int(time.time()),
                "updated_at": int(time.time())
            })

        # Format response theo GraphQL style
        upload_results = []
        for result in results:
            upload_results.append({
                "file": result,
                "message": "File uploaded successfully",
                "result": True
            })
        
        return {
            "data": {
                "uploadFile": upload_results[0] if len(upload_results) == 1 else upload_results
            },
            "extensions": {
                "cost": {
                    "requestedQueryCost": 0,
                    "maximumAvailable": 50000
                }
            }
        }


    except Exception as e:
        print("Upload error:", str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


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

        try:
            if asset.path:
                file_path = os.path.join("uploads", asset.path)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as file_err:
            print(f"[WARNING] Không thể xóa: {file_err}")

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

@router.delete("/assets")
def delete_asset_by_url(file_url: str = Query(None, description="Xóa ảnh bằng file_url"), session: Session = Depends(get_session), project: Projects = Depends(verify_api_key)):
    asset = session.exec(
        select(Assets).where(Assets.file_url == file_url, Assets.project_id == project.id)
    ).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if os.path.exists(asset.path):
        os.remove(asset.path)

    session.delete(asset)
    session.commit()
    return {"message": "Asset deleted successfully"}

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
        return {"status": 1, "data": assets}
        
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