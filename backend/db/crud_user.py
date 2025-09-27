from sqlmodel import Session
from fastapi import HTTPException
from sqlalchemy import text
from pathlib import Path
from uuid import uuid4
import os, io
from PIL import Image
from fastapi.responses import JSONResponse, FileResponse
import mimetypes
from fastapi import UploadFile
from io import BytesIO

from db.crud_asset import add_asset


RESOURCE_DIR = "uploads/public_assets"   # Thư mục chứa ảnh mặc định
UPLOAD_DIR = Path("uploads") 
async def add_user_with_assets(session: Session, email: str, username: str, sub: str):
    try:
        # 1. Tạo user
        result = session.execute(
            text("CALL register(:p_email, :p_sub, :p_name)")
            .bindparams(p_email=email, p_sub=sub, p_name=username)
        )

        user = result.mappings().first()
        if not user:
            raise HTTPException(status_code=401, detail="Register failed")
        
        user_id, project_id, folder_id= user["user_id"], user["project_id"] , user["folder_id"]

        
        # 2. Upload 10 ảnh public mặc định
        results = []
    
        for file_path in Path(RESOURCE_DIR).glob("*"):
            filename = file_path.name
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type or not mime_type.startswith(("image/", "video/")):
                raise HTTPException(400, f"File {filename} không hợp lệ (chỉ hỗ trợ image/video)")

            # đọc bytes từ file hệ thống
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            size = len(file_bytes)

            # lấy dimension nếu là ảnh
            width = height = None
            if mime_type.startswith("image/"):
                try:
                    with Image.open(io.BytesIO(file_bytes)) as im:
                        width, height = im.size
                except Exception:
                    raise HTTPException(400, f"Ảnh {filename} không hợp lệ")

            # tên file lưu
            ext = os.path.splitext(filename)[1].lower() or ".bin"
            new_filename = f"{uuid4().hex}{ext}"

            # relative path (lưu trong DB)
            object_path = f"{user_id}/{project_id}/Default Folder/{new_filename}"

            # absolute path (lưu trong ổ cứng)
            save_path = os.path.join(UPLOAD_DIR, object_path).replace("\\", "/")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Lưu file vào local
            with open(save_path, "wb") as f:
                f.write(file_bytes)

            try:
                asset_id = add_asset(
                    session=session,
                    user_id=user_id,
                    folder_id=folder_id,
                    path=object_path,
                    name=new_filename,
                    format=mime_type,
                    width=width, height=height,
                    file_size=size,
                    is_private=False  
                )
            except Exception as e:
                if os.path.exists(save_path):
                    os.remove(save_path)
                raise HTTPException(status_code=500, detail=f"DB insert failed: {e}")

            file_path_resolved = (UPLOAD_DIR / object_path).resolve()
            results.append({
                "status": 1,
                "id": asset_id,
                "path": object_path,
                "preview_url": f"/uploads/{object_path}",
                "width": width, "height": height, "file_size": size,
                "mime_type": mime_type,
                "is_private": False,
            })

        session.commit()   # commit 1 lần cuối cùng
        return {"status": 1, "data": results}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading default assets: {e}")