from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select, func
from fastapi import UploadFile, File, Form
from typing import List
from fastapi import Query
from PIL import Image
import io, os, time
from uuid import uuid4
from pathlib import Path
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from db.session import get_session
from models import  Projects, Folders, Assets , Users
from dependencies.dependencies import get_current_user
from db.crud_asset import add_asset
from db.crud_embedding import create_embedding_for_asset
from db.crud_thumbnail import generate_thumbnail_urls_for_file

from utils.path_builder import build_full_path, build_file_url
from utils.folder_finder import find_folder_by_path
from utils.filename_utils import truncate_filename, split_filename, sanitize_filename
from core.config import settings

# Constants
MAX_FILENAME_LENGTH = 255  # Maximum length for filename in DB
UPLOAD_DIR = Path("uploads")
router = APIRouter(prefix="/assets",  tags=["User Assets"])

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
    thumbnails = None
    if asset.file_type.startswith("image/"):
        thumbnails = generate_thumbnail_urls_for_file(asset.id)
    return {
        "status": 1,
        "id": asset.id,
        "name": asset.name,
        "path": asset.path, 
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
        "updated_at": asset.updated_at,
        "thumbnails": thumbnails
    }


@router.get("/count")
def count(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user),is_favorite: bool | None = Query(None, description="Lọc ảnh được đánh dấu yêu thích"),
    is_deleted: bool | None = Query(None, description="Lọc ảnh đã xóa")):
    try:
        statement = (select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == current_user.id))
        
        if is_favorite is not None:
            statement = statement.where(Assets.is_favorite == is_favorite)

        if is_deleted is not None:
            statement = statement.where(Assets.is_deleted == is_deleted)
        total = session.exec(select(func.count()).select_from(statement)).one()
        return {"status": 1, "data": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đếm: {e}")
    
@router.get("/all")
def list_assets(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    is_favorite: bool | None = Query(None, description="Lọc ảnh được đánh dấu yêu thích"),
    is_deleted: bool | None = Query(None, description="Lọc ảnh đã xóa"),
):
    try:
        statement = (
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == current_user.id)
        )
        if is_favorite is not None:
            statement = statement.where(Assets.is_favorite == is_favorite)

        if is_deleted is not None:
            statement = statement.where(Assets.is_deleted == is_deleted)
        assets = session.exec(statement).all()
        
        # Format response giống như upload-images API
        results = []
        for asset in assets:
            formatted_asset = format_asset_response(asset, session)
            results.append(
                formatted_asset
            )

        return {"status": 1, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")
class AssetUpdate(BaseModel):
    is_private: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_deleted: Optional[bool] = None

@router.patch("/{id}")
def update_asset(
    id: int,
    update: AssetUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        # 1. Tìm asset
        asset = session.exec(select(Assets).where(Assets.id == id)).first()
        if not asset:
            raise HTTPException(404, "Asset not found")

        # 2. Kiểm tra user sở hữu asset
        user = session.exec(
            select(Users)
            .join(Projects, Users.id == Projects.user_id)
            .join(Folders, Projects.id == Folders.project_id)
            .join(Assets, Folders.id == Assets.folder_id)
            .where(Assets.id == asset.id)
        ).first()

        if not user:
            raise HTTPException(404, "Owner not found")

        if current_user.id != user.id:
            raise HTTPException(401, "Unauthorized")

        # 3. Update các field
        if update.is_private is not None:
            asset.is_private = update.is_private
           
        if update.is_favorite is not None:
            asset.is_favorite = update.is_favorite
            print
        if update.is_deleted is not None:
            asset.is_deleted = update.is_deleted
            print("is_deleted",update.is_deleted)

        session.add(asset)
        session.commit()
        session.refresh(asset)

        return {
            "message": "Asset updated successfully",
            "asset": asset
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")

@router.delete("/{asset_id}")
def delete_asset(
    asset_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Xóa asset"""
    try:
        asset = session.get(Assets, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Assets not found")
        user  = session.exec(select(Users)
                .join(Projects, Users.id == Projects.user_id)
                .join(Folders, Projects.id == Folders.project_id)
                .join(Assets, Folders.id == Assets.folder_id)
                .where(Assets.id == asset.id)
            ).first()
        if not user:
            raise HTTPException(404, "Owner not found")
        if current_user.id != user.id:
            raise HTTPException(401, "Unauthorized")
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


@router.post("/upload-images")
async def upload_assets(
    current_user: dict = Depends(get_current_user),
    files: List[UploadFile] = File(...),
    folder_slug: str | None = Form(None),  # Sử dụng slug thay vì name
    project_slug: str | None = Form(None),  # Optional: Chỉ định project bằng slug
    is_private: bool = Form(False),  
    session: Session = Depends(get_session)
):
    results = []
    
    # Tìm project (theo slug hoặc default)
    if project_slug:
        project = session.exec(
            select(Projects)
            .where(Projects.user_id == current_user.id)
            .where(Projects.slug == project_slug)
        ).first()
        if not project:
            raise HTTPException(404, f"Không tìm thấy project với slug '{project_slug}'")
    else:
        project = session.exec(
            select(Projects)
            .where(Projects.user_id == current_user.id)
            .where(Projects.is_default == True)
        ).first()
        if not project:
            project = Projects(
            user_id=current_user.id,
            name="Default Project",
            slug=f"default-project-{current_user.id}",
            is_default=True
        )
        session.add(project)
        session.flush()
    
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
                
                 # Thumbnails
                    # Generate thumbnail URLs if file is an image
                
                thumbnails = None
                if file.content_type.startswith("image/"):
                    thumbnails = generate_thumbnail_urls_for_file(asset_id)
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
                    
                    # 🏷️ TỰ ĐỘNG ĐÁNH TAG cho ảnh
                    auto_tags = []  # Store tags for response
                    try:
                        from services.tagging_service import auto_tag_asset
                        # Open image từ bytes
                        image_for_tagging = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                        tags = auto_tag_asset(
                            session=session,
                            asset_id=asset_id,
                            image=image_for_tagging,
                            threshold=0.25,  # Cosine similarity threshold (0-1)
                            top_k=20  # Tăng lên 20 tags
                        )
                        auto_tags = tags  # Save for response
                        if tags:
                            print(f"✅ Auto-tagged asset {asset_id} with {len(tags)} tags: {', '.join(tags)}")
                        else:
                            print(f"⚠️ No tags generated for asset {asset_id}")
                    except Exception as tag_err:
                        # Không raise error, chỉ log warning
                        print(f"⚠️ Auto-tagging failed for asset {asset_id}: {tag_err}")
    
            except Exception as e:
                if os.path.exists(save_path):
                    os.remove(save_path)
                raise HTTPException(status_code=500, detail=f"DB insert failed: {e}")

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
                "auto_tags": auto_tags,  # ← Thêm danh sách tags tự động
                "tags_count": len(auto_tags),  # ← Số lượng tags
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "thumbnails": thumbnails
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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-by-folder/{folder_path:path}")
async def get_upload(folder_path: str, session: Session = Depends(get_session)):
    abs_path = os.path.join("uploads", folder_path).replace("\\", "/")
    # Nếu là thư mục → query tất cả assets trong folder đó
    if os.path.isdir(abs_path):
        # Bỏ prefix "uploads/" để so khớp với DB path
        db_folder_path = folder_path.rstrip("/")

        # Truy vấn tất cả asset có folder_path trùng
        assets = session.exec(
            select(Assets)
            .where(Assets.folder_path == db_folder_path)
            .where(Assets.is_deleted == False)
        ).all()

        if not assets:
            raise HTTPException(404, "No assets found in this folder")

        data = []
        for a in assets:
            data.append({
                "id": a.id,
                "name": a.name,
                "system_name": a.system_name,
                "path": a.path,
                "file_url": a.file_url,
                "width": a.width,
                "height": a.height,
                "file_type": a.file_type,
                "created_at": a.created_at,
            })

        return JSONResponse(content={"status": 1, "count": len(data), "data": data})

    # Nếu không phải file hoặc folder → 404
    raise HTTPException(404, "Invalid file path")

# ====== Route search_image ======
@router.post("/search")
async def search_assets(
    query_text: str | None = Form(None), 
    file: UploadFile | None = File(None),
    project_id: Optional[int] = Form(None),  # Optional - nếu None thì search tất cả projects của user
    folder_id: Optional[int] = Form(None),
    k: int = Form(20),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Tìm kiếm ảnh bằng hình ảnh hoặc text cho user đã đăng nhập.
    Endpoint này yêu cầu user authentication.
    
    Args:
        query_text: Text query (e.g., "a cat on the sofa")
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
            from api.routes.search import validate_project_ownership
            validate_project_ownership(session, project_id, current_user.id)
        
        # Import search services
        from services.search.embeddings_service import search_by_image, search_by_text
        
        assets = []
        if file:  # search bằng ảnh
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

        elif query_text:  # search bằng text
            # Tìm kiếm
            assets = search_by_text(
                session=session,
                project_id=project_id,
                query_text=query_text,
                k=k,
                folder_id=folder_id,
                user_id=current_user.id
            )

        else:
            raise HTTPException(status_code=400, detail="Cần gửi query_text hoặc file ảnh")

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