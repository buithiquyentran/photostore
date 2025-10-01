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
from fastapi import Request
import numpy as np
from pathlib import Path
from typing import Optional
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from db.session import get_session
from models import  Projects, Folders, Assets , Users, Embeddings
from dependencies.dependencies import get_optional_user, get_current_user
from db.crud_asset import add_asset
from db.crud_embedding import create_embedding_for_asset
from db.crud_folder import get_or_create_folder

# from services.embeddings_service import index, faiss_id_to_asset, embed_image, rebuild_faiss,add_embedding_to_faiss, ensure_user_index,search_user
# from services.search.embeddings_service import  embed_image,add_embedding_to_faiss, search_user,ensure_user_index, get_text_embedding, search_by_embedding

router = APIRouter(prefix="/users/assets",  tags=["User Assets"])
BUCKET_NAME = "photostore"
BUCKET_NAME_PUBLIC = "images" 
UPLOAD_DIR = Path("uploads")

@router.get("/{name}/metadata")
def get_asset_metadata(name: str, session: Session = Depends(get_session), current_user: dict = Depends(get_optional_user)):
    asset = session.exec(select(Assets).where(Assets.name == name)).first()
    folder = session.exec(select(Folders).where(Folders.id == asset.folder_id)).first() if asset else None
    if not asset:
        raise HTTPException(404, "Asset not found")
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
    result = asset.dict()
    result["location"] = folder.name
    return {"status": 1, "data": result}
@router.get("/{name}/nextprev/metadata")
def get_next_prev(name: str, session: Session = Depends(get_session), current_user: dict = Depends(get_optional_user)):
    asset = session.query(Assets).filter(Assets.name == name).first()
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
    statement = (
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == current_user.id)
        )
   # prev: ảnh có id nhỏ hơn trong cùng project
    prev_asset = session.exec(
        statement.where(Assets.id < asset.id).order_by(Assets.id.desc()).limit(1)
    ).first()

    # next: ảnh có id lớn hơn trong cùng project
    next_asset = session.exec(
        statement.where(Assets.id > asset.id).order_by(Assets.id.asc()).limit(1)
    ).first()

    return {
        "prev": {"name": prev_asset.name} if prev_asset else None,
        "next": {"name": next_asset.name} if next_asset else None,
    }
@router.get("/count",)
def count(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    try:
        statement = select(func.count()).select_from(select(Assets)
        .join(Folders, Assets.folder_id == Folders.id)
        .join(Projects, Folders.project_id == Projects.id)
        .where(Projects.user_id == current_user.id))
        
        # statement = select(func.count()).select_from(Assets)
        total = session.exec(statement).one()
        return {"status": "success", "data": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đếm: {e}")
    
@router.get("/all")
def list_private_assets(
    request: Request,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        statement = (
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == current_user.id)
        )
        results = session.exec(statement).all()
        # ensure_user_index(session, id)
        
        data = []
        for a in results:
            obj = a.dict()
            obj["url"] = f"{request.base_url}api/v1/assets/{a.id}"
            data.append(obj)

        return {"status": "success", "data": data}
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

@router.post("/upload-images")
async def upload_assets(
    current_user: dict = Depends(get_current_user),
    files: List[UploadFile] = File(...),
    folder_name: str | None = Form(None), 
    is_private: bool = Form(False),  
    session: Session = Depends(get_session)
):
    results = []
    print("current_user.id",current_user.id)
    # Tìm project mặc định của user
    project = session.exec(
        select(Projects).where(Projects.user_id == current_user.id, Projects.is_default == True)
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
            object_path = f"{current_user.id}/{project.id}/{folder.name}/{filename}"

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
                    user_id=current_user.id,
                    folder_id=folder_id,
                    path=object_path,
                    name=filename,
                    format=file.content_type,
                    width=width, height=height,
                    file_size=size,
                    is_private=is_private   # 👈 set giá trị từ form (hoặc mặc định False)
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
