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
import traceback
from db.crud_asset import add_asset
from sqlmodel import Session, select
from fastapi import HTTPException
from models import Users, Projects, Folders  # import các model của em
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from db.crud_embedding import create_embedding_for_asset
from utils.path_builder import build_full_path, build_file_url
from utils.folder_finder import find_folder_by_path
from utils.filename_utils import truncate_filename, split_filename, sanitize_filename
from core.config import settings

# Constants
MAX_FILENAME_LENGTH = 255  # Maximum length for filename in DB

def register_user(session: Session, email: str, sub: str, username: str):
    """
    Thay thế hoàn toàn cho thủ tục MySQL register().
    Tạo user + project + folder mặc định trong 1 transaction.
    """
    try:
        # 1️⃣ Bắt đầu transaction
        # session.begin()

        # 2️⃣ Kiểm tra email đã tồn tại chưa
        user_exists = session.exec(select(Users).where(Users.email == email)).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="Email already exists")

        # 3️⃣ Thêm user mới
        new_user = Users(email=email, sub=sub, username=username)
        session.add(new_user)
        session.flush()  # flush để có new_user.id mà chưa commit
        print("🧩 Step 1: create user")
        # 4️⃣ Thêm project mặc định
        default_project = Projects(
            user_id=new_user.id,
            name="Default Project",
            slug=f"default-project",
            is_default=True
        )
        session.add(default_project)
        session.flush()
        print("🧩 Step 2: uploading assets")
        # 5️⃣ Thêm folder mặc định
        default_folder = Folders(
            project_id=default_project.id,
            name="Home",
            slug="home",
            path="default-project/home", 
            is_default=True
        )
        session.add(default_folder)
        session.flush()
        # 6️⃣ Commit nếu mọi thứ ok
        session.commit()

        # 7️⃣ Trả dữ liệu
        return {
            "user_id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "is_superuser": new_user.is_superuser,
            "project_id": default_project.id,
            "folder_id": default_folder.id,
        }

    except HTTPException:
        session.rollback()
        raise
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


RESOURCE_DIR = "uploads/public_assets"   # Thư mục chứa ảnh mặc định
UPLOAD_DIR = Path("uploads") 

async def add_user_with_assets(session: Session, email: str, username: str, sub: str):
    try:
        # 1. Tạo user
        user = register_user(session, email=email, sub=sub, username=username)
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
            storage_filename = f"{uuid4().hex}{ext}"
                
            # relative path (lưu trong DB)
            # Build full path từ project và folder slugs
            folder_path = build_full_path(session, project_id, folder_id)
            object_path = f"{folder_path}/{storage_filename}"
            path = f"{user_id}/{folder_path}/{storage_filename}"

            # absolute path (lưu trong ổ cứng)
            save_path = os.path.join(UPLOAD_DIR, path).replace("\\", "/")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Lưu file vào local
            with open(save_path, "wb") as f:
                f.write(file_bytes)

            try:
                # Truncate original filename nếu quá dài
                safe_filename = truncate_filename(filename, MAX_FILENAME_LENGTH)
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                file_url = build_file_url(session, project_id, folder_id, storage_filename, base_url)
                
                 # Lưu asset vào database
                asset_id = add_asset(
                    session=session,
                    project_id=project_id,
                    folder_id=folder_id,
                    name=safe_filename,  # Tên file gốc đã được truncate
                    system_name=storage_filename,  # UUID filename
                    file_extension=ext,
                    file_type=mime_type,
                    format=mime_type,  # Sử dụng MIME type làm format
                    file_size=size,
                    path=object_path,
                    file_url=file_url,
                    folder_path=folder_path,
                    width=width,
                    height=height,
                    is_private=False,
                    is_image= True
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
        print("🧩 Step 3: add_asset done ->", asset_id)

        session.commit()   # commit 1 lần cuối cùng
        return {"status": 1, "data": results}

    except Exception as e:
        session.rollback()
        print("❌ Error in add_user_with_assets:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error uploading default assets: {e}")
