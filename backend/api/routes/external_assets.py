from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from PIL import Image
from sqlalchemy.orm import Session
from db.session import get_session
from sqlmodel import Session, select
from uuid import uuid4
import io
import os

from pathlib import Path
from fastapi.responses import JSONResponse, FileResponse
from typing import List



from dependencies.external_auth import verify_external_request
from db.session import get_session

from models import  Projects, Folders, Users, Assets

from db.crud_asset import add_asset
from db.crud_embedding import create_embedding_for_asset
from services.api_client.api_client_service import get_client_by_key
from services.api_client.signature import generate_signature
from db.crud_folder import get_or_create_folder
from core.security import get_current_user, get_optional_user

router = APIRouter(prefix="/external/assets", tags=["External Assets"])
BUCKET_NAME = "photostore"

UPLOAD_DIR = Path("uploads")

@router.post("/upload")
async def upload_asset_external(
    files: List[UploadFile] = File(...),

    folder_name: str | None = Form(None), 
    client=Depends(verify_external_request),  # Check API key + signature
    session: Session = Depends(get_session),
    is_private: bool = False
):
    results = []
    if folder_name:
        folder = get_or_create_folder(session, client.id, folder_name)
    else:

        folder = session.exec(
            select(Folders).where(
                Folders.project_id == client.id,
                Folders.is_default == True
            )
        ).first()
    if not folder:
        raise HTTPException(404, "Không tìm thấy folder phù hợp")
    folder_id = folder.id
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

            # tên file lưu
            ext = os.path.splitext(file.filename or "")[1].lower() or ".bin"
            filename = f"{uuid4().hex}{ext}"

            # relative path (lưu trong DB)
            object_path = f"{client.user_id}/{client.id}/{folder.name}/{filename}"

            # absolute path (lưu trong ổ cứng)
            save_path = os.path.join(UPLOAD_DIR, object_path).replace("\\", "/")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Lưu file vào local
            with open(save_path, "wb") as f:
                f.write(file_bytes)

            try:
                # Lưu asset vào database
                asset_id = add_asset(
                    session=session,
                    user_id=client.user_id,
                    folder_id=folder_id,
                    url=object_path,
                    name=file.filename or filename,
                    format=file.content_type,
                    width=width, height=height,
                    file_size=size,
                    is_private=is_private   
                )
                
                # 🔥 TỰ ĐỘNG TẠO EMBEDDING cho ảnh (External API)
                # Chỉ tạo embedding nếu là file IMAGE (không phải video)
                if file.content_type.startswith("image/"):
                    try:
                        embedding = create_embedding_for_asset(
                            session=session,
                            asset_id=asset_id,
                            image_bytes=file_bytes
                        )
                        if embedding:
                            print(f"✅ [External API] Created embedding for asset {asset_id}")
                        else:
                            print(f"⚠️ [External API] Failed to create embedding for asset {asset_id}")
                    except Exception as emb_err:
                        # Không raise error, chỉ log warning
                        print(f"⚠️ [External API] Embedding creation failed for asset {asset_id}: {emb_err}")
                    
                    # 🏷️ TỰ ĐỘNG ĐÁNH TAG cho ảnh (External API)
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
                            print(f"✅ [External API] Auto-tagged asset {asset_id} with {len(tags)} tags: {', '.join(tags)}")
                        else:
                            print(f"⚠️ [External API] No tags generated for asset {asset_id}")
                    except Exception as tag_err:
                        # Không raise error, chỉ log warning
                        print(f"⚠️ [External API] Auto-tagging failed for asset {asset_id}: {tag_err}")

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
                "path": object_path,
                "preview_url": FileResponse(file_path),
                "width": width, "height": height, "file_size": size,
                "mime_type": file.content_type,
                "is_private": is_private,   
            })


        return {"status": 1, "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# @router.post("/{asset_id}")
# def get_asset(asset_id: int, session: Session = Depends(get_session), client=Depends(verify_external_request),  # Check API key + signature
# ):
#     asset = session.exec(select(Assets).where(Assets.id == asset_id)).first()
#     if not asset:
#         raise HTTPException(404, "Asset not found")
#     project= session.exec(select(Projects)
#             .join(Folders, Projects.id == Folders.project_id)
#             .join(Assets, Folders.id == Assets.folder_id)
#             .where(Projects.id == client.id)
#         ).first()
#     if not project:
#         raise HTTPException(404, "Owner not found")
#     # fix path separator
#     safe_path = asset.replace("\\", "/")
#     file_path = (UPLOAD_DIR / safe_path).resolve()
#     if not file_path.exists():
#         raise HTTPException(404, "File not found")
#     # 🔒 Check quyền
#     if asset.is_private:
#         if client is None:
#             raise HTTPException(401, "Unauthorized")
#         try:
#             current_project_id = int(client.id)   # 👈 convert sang int
#         except ValueError:
#             raise HTTPException(401, "Invalid user id in token")

#         if current_project_id != project.id:
#             raise HTTPException(401, "Unauthorized")

#     return FileResponse(file_path)

# from fastapi import Request

# @router.post("/")
# def get_all_assets(
#     folder_id: int | None = None,
#     client=Depends(verify_external_request),  # check api_key + signature
#     session: Session = Depends(get_session),
#     request: Request = None
# ):
#     query = select(Assets).join(Folders).where(Folders.project_id == client.id)

#     if folder_id:
#         query = query.where(Assets.folder_id == folder_id)

#     assets = session.exec(query).all()
#     if not assets:
#         return {"status": 1, "data": []}

#     results = []
#     for asset in assets:
#         # API URL cho client dùng
#         asset_url = str(request.base_url) + f"external/assets/{asset.id}"

#         results.append({
#             "id": asset.id,
#             "name": asset.name,
#             "url": asset_url,     # 👈 trả URL API thay vì đường dẫn file local
#             "width": asset.width,
#             "height": asset.height,
#             "file_size": asset.file_size,
#             "mime_type": asset.format,
#             "is_private": asset.is_private,
#             "folder_id": asset.folder_id,
#             "created": asset.created.isoformat() if asset.created_at else None,
#         })

#     return {"status": 1, "data": results}
