from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from PIL import Image
from fastapi import Request

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
# from db.crud_embedding import add_embedding
from services.api_client.api_client_service import get_client_by_key
from services.api_client.signature import generate_signature
from db.crud_folder import get_or_create_folder, get_folder

router = APIRouter(prefix="/external/assets", tags=["External Assets"])
BUCKET_NAME = "photostore"

UPLOAD_DIR = Path("uploads")

@router.post("/signature")
def get_signature(api_key: str, api_secret: str, session: Session = Depends(get_session)):
    client = get_client_by_key(api_key=api_key, session=session)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid api_key")
    result = generate_signature(params={}, api_secret = api_secret, add_timestamp=True)

    return {
        "api_key": api_key,
        "signature": result["signature"],
        "params": result["params"]
    }

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
    # else:

    #     folder = session.exec(
    #         select(Folders).where(
    #             Folders.project_id == client.id,
    #             Folders.is_default == True
    #         )
    #     ).first()
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
                asset_id = add_asset(
                    session=session,
                    user_id=client.user_id,
                    folder_id=folder_id,
                    path=object_path,
                    name= filename,
                    format=file.content_type,
                    width=width, height=height,
                    file_size=size,
                    is_private=is_private   
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
    
@router.post("/{folder_name}")
def get_asset(
    request: Request,
    folder_name: str, session: Session = Depends(get_session), client=Depends(verify_external_request),  # Check API key + signature
):
    try:
        if not client:
            raise HTTPException(status_code=401, detail="Unauthorized")
        if folder_name:
            folder = get_folder(session, client.id, folder_name)
            if not folder:
                raise HTTPException(404, "Folder không tồn tại")
        assets = (
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.id == client.id, Folders.id == folder.id)
        )
        results = session.exec(assets).all()
        # ensure_user_index(session, id)
        
        data = []
        for a in results:
            obj = a.dict()
            obj["url"] = f"{request.base_url}api/v1/assets/{a.name}"
            data.append(obj)

        return {"status": 1, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi: {str(e)}")



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
#             "path": asset_url,     # 👈 trả URL API thay vì đường dẫn file local
#             "width": asset.width,
#             "height": asset.height,
#             "file_size": asset.file_size,
#             "mime_type": asset.format,
#             "is_private": asset.is_private,
#             "folder_id": asset.folder_id,
#             "created": asset.created.isoformat() if asset.created_at else None,
#         })

#     return {"status": 1, "data": results}
