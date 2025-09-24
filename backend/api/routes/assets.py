from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,Request,BackgroundTasks
from sqlmodel import Session, select, func
from fastapi import UploadFile, File, Form
from typing import List
from PIL import Image
import io, os
from uuid import uuid4
from datetime import datetime, timedelta
import io, faiss, json
import torch
import clip
import numpy as np
from pathlib import Path
from typing import Optional
from fastapi.responses import JSONResponse, FileResponse
from db.supabase_client import supabase
from db.session import get_session
from models import  Projects, Folders, Assets , Users, Embeddings
from core.security import get_current_user, get_optional_user
from db.crud_asset import add_asset
# from db.crud_embedding import add_embedding
# from db.crud_embedding import embed_image
from db.crud_folder import get_or_create_folder

# from services.embeddings_service import index, faiss_id_to_asset, embed_image, rebuild_faiss,add_embedding_to_faiss, ensure_user_index,search_user
# from services.search.embeddings_service import  embed_image,add_embedding_to_faiss, search_user,ensure_user_index, get_text_embedding, search_by_embedding

router = APIRouter(prefix="/assets",  tags=["Assets"])
BUCKET_NAME = "photostore"
BUCKET_NAME_PUBLIC = "images" 
UPLOAD_DIR = Path("uploads")
# @router.get("/images")
# def get_images(session: Session = Depends(get_session)):
    
#     try:
#         statement = select(Assets).where(Assets.is_image == True)
#         results = session.exec(statement).all()
#         return {"status": "success", "data": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")

# @router.get("/videos")
# def get_videos(session: Session = Depends(get_session)):
   
#     try:
#         statement = select(Assets).where(Assets.is_image == False)
#         results = session.exec(statement).all()
#         return {"status": "success", "data": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
   
@router.get("/count",)
def count(session: Session = Depends(get_session), id=Depends(get_current_user)):
    try:
        statement = select(func.count()).select_from(select(Assets)
        .join(Folders, Assets.folder_id == Folders.id)
        .join(Projects, Folders.project_id == Projects.id)
        .where(Projects.user_id == id))
        
        # statement = select(func.count()).select_from(Assets)
        total = session.exec(statement).one()
        return {"status": "success", "data": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đếm: {e}")
    
@router.get("/all")
def list_private_assets(
    id=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        statement = (
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == id)
        )
        results = session.exec(statement).all()
        # ensure_user_index(session, id)
        
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi ORM hoặc Supabase: {str(e)}")

# @router.get("/{asset_id}/signed-url")  
# def get_signed_url(asset_id: int, session: Session = Depends(get_session)):
#     asset = session.get(Assets, asset_id)
#     if not asset:
#         raise HTTPException(404, "Asset not found")

#     url = asset.url

#     # Nếu URL đã là public (bắt đầu bằng http), return luôn
#     if url.startswith("http://") or url.startswith("https://"):
#         return {"data": url}

#     # Nếu là private path => tạo signed URL
#     try:
#         signed = supabase.storage \
#             .from_(BUCKET_NAME) \
#             .create_signed_url(url, expires_in=60)  # 1 giờ
#         return {"data": signed.get("signedURL")}
#     except Exception as e:
#         raise HTTPException(500, f"Signed URL creation failed: {e}")

# @router.get("/{asset_id}")
# def get_asset(asset_id: int, session: Session = Depends(get_session), id: int|None = Depends(get_optional_user)):
#     asset = session.exec(select(Assets).where(Assets.id == asset_id)).first()
#     if not asset:
#         raise HTTPException(404, "Asset not found")
#     user  = session.exec(select(Users)
#             .join(Projects, Users.id == Projects.user_id)
#             .join(Folders, Projects.id == Folders.project_id)
#             .join(Assets, Folders.id == Assets.folder_id)
#             .where(Assets.id == asset.id)
#         ).first()
#     if not user:
#         raise HTTPException(404, "Owner not found")
#     # fix path separator
#     safe_path = asset.url.replace("\\", "/")
#     file_path = (UPLOAD_DIR / safe_path).resolve()
#     if not file_path.exists():
#         raise HTTPException(404, "File not found")
#     print(id, user.id)
#     # 🔒 Check quyền
#     if asset.is_private:
#         if id is None:
#             raise HTTPException(401, "Unauthorized")
#         try:
#             current_user_id = int(id)   # 👈 convert sang int
#         except ValueError:
#             raise HTTPException(401, "Invalid user id in token")

#         if current_user_id != user.id:
#             raise HTTPException(401, "Unauthorized")

#     return FileResponse(file_path)


@router.post("/upload-images")
async def upload_assets(
    files: List[UploadFile] = File(...),
    folder_name: str | None = Form(None), 
    is_private: bool = Form(False),  
    id=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    results = []

    # Tìm project mặc định của user
    project = session.exec(
        select(Projects).where(Projects.user_id == id, Projects.is_default == True)
    ).first()
    if not project:
        raise HTTPException(404, "Không tìm thấy project mặc định cho user")
    
    if folder_name:
        folder = get_or_create_folder(session, project.id, folder_name)
    else:
        folder = session.exec(
            select(Folders).where(
                Folders.project_id == project.id,
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
            object_path = f"{id}/{project.id}/{folder.name}/{filename}"

            # absolute path (lưu trong ổ cứng)
            save_path = os.path.join(UPLOAD_DIR, object_path).replace("\\", "/")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Lưu file vào local
            with open(save_path, "wb") as f:
                f.write(file_bytes)

            try:
                asset_id = add_asset(
                    session=session,
                    user_id=id,
                    folder_id=folder_id,
                    url=object_path,
                    name=file.filename or filename,
                    format=file.content_type,
                    width=width, height=height,
                    file_size=size,
                    is_private=is_private   # 👈 set giá trị từ form (hoặc mặc định False)
                )
                # embedding, vec = add_embedding(session=session, asset_id=asset_id, file_bytes=file_bytes)

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


# ====== Route search_image ======
# @router.post("/search")
# async def search_assets(
#     query_text: str | None = Form(None), 
#     file: UploadFile | None = File(None),
#     id=Depends(get_current_user),
#     k: int = 5,
#     session: Session = Depends(get_session),
# ):
#     try:
#         if file:  # search bằng ảnh
#             content = await file.read()
#             image = Image.open(io.BytesIO(content)).convert("RGB")
#             query_vec = embed_image(image)

#         elif query_text:  # search bằng text
#             query_vec = get_text_embedding(query_text)

#         else:
#             raise HTTPException(status_code=400, detail="Cần gửi query_text hoặc file ảnh")

#         # Gọi search chung
#         asset_ids = search_by_embedding(session=session, user_id=id, query_vec=query_vec, k=k)

#         # Lấy metadata asset từ DB
#         results = session.exec(
#             select(Assets).where(Assets.id.in_(asset_ids))
#         ).all()

#         return {"status": 1, "data": results}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
