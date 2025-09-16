from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from PIL import Image
from sqlalchemy.orm import Session
from db.session import get_session
from sqlmodel import Session, select
from uuid import uuid4
import io
import os
from dependencies.external_auth import verify_external_request
from db.supabase_client import supabase
from db.session import get_session
from models import  Projects, Folders, Users
from db.crud_asset import add_asset
from db.crud_embedding import add_embedding
from services.api_client.api_client_service import get_client_by_key
from services.api_client.signature import generate_signature

router = APIRouter(prefix="/external/assets", tags=["External Assets"])
BUCKET_NAME = "photostore"

@router.post("/signature")
def get_signature(api_key: str, api_secret: str, session: Session = Depends(get_session)):
    client = get_client_by_key(api_key=api_key, session=session)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid api_key")
    result = generate_signature(params={}, api_secret = api_secret, add_timestamp=True)

    return {
        "status_code": 200,
        "api_key": api_key,
        "signature": result["signature"],
        "params": result["params"]
    }

@router.post("/upload")
async def upload_asset_external(
    file: UploadFile = File(...),
    folder_name: str | None = Form(None), 
    client=Depends(verify_external_request),  # Check API key + signature
    session: Session = Depends(get_session)
):
    results = []
    if folder_name:
        # tìm folder theo tên trong project
        folder = session.exec(
            select(Folders).where(Folders.project_id == client.id, Folders.name == folder_name)
        ).first()

        if not folder:
            # nếu chưa có thì tạo mới
            folder = Folders(
                project_id=client.id,
                parent_id=None,       # root folder
                name=folder_name,
                is_default=False
            )
            session.add(folder)
            session.commit()
            session.refresh(folder)
    else:
        # dùng folder mặc định
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
        # for file in files:
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

        # path trong bucket (mỗi user 1 folder)
        ext = os.path.splitext(file.filename or "")[1].lower() or ".bin"
        object_path = f"{client.user_id}/{client.id}/{folder.name}/{uuid4().hex}{ext}"

        # upload (bucket private)
        supabase.storage.from_(BUCKET_NAME).upload(
            object_path,
            file_bytes,
            {"content-type": file.content_type, "x-upsert": "false"},
        )

        try:
            asset_id = add_asset(
                session=session,
                user_id=client.user_id,
                folder_id=folder_id,
                url=object_path,
                name=file.filename or object_path,
                format=file.content_type,
                width=width, height=height,
                file_size=size,
            )
            embedding, vec = add_embedding(session=session,asset_id=asset_id,file_bytes=file_bytes)
            # add_embedding_to_faiss(user_id = client.user_id, asset_id=asset_id, embedding=vec)
        except Exception as e:
            # rollback supabase nếu DB fail
            supabase.storage.from_(BUCKET_NAME).remove([object_path])
            raise HTTPException(status_code=500, detail=f"DB insert failed: {e}")

        # tạo signed url ngắn hạn để preview
        signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(object_path, 120)

        results.append({
            "status": 1,
            "id": asset_id,
            "path": object_path,
            "preview_url": signed.get("signedURL"),
            "width": width, "height": height, "file_size": size,
            "mime_type": file.content_type,
        })

        return {"status": 1, "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
