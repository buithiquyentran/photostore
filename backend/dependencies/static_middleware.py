"""
Middleware để kiểm tra quyền truy cập static files
"""
from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session, select
from pathlib import Path
import os
from fastapi import HTTPException

from models import Assets, Projects, Folders, Users, Thumbnails
from dependencies.dependencies import get_key, ALGORITHM
from jose import jwt, JWTError
from db.session import engine
import time, hmac, hashlib
from fastapi import Request

from db.crud_thumbnail import get_or_create_thumbnail

UPLOAD_DIR = Path("uploads")

def parse_thumbnail_filename(filename: str):
    import re
    m = re.match(r"(\d+)_(\d+)x(\d+)\.(\w+)", filename)
    if not m:
        raise ValueError(f"Invalid thumbnail filename format: {filename}")
    asset_id, width, height, ext = m.groups()
    return int(asset_id), int(width), int(height), ext.lower()


UPLOAD_DIR = Path("uploads")

async def verify_static_access(request: Request, call_next):
    """
    Middleware để kiểm tra quyền truy cập static files.
    - Nếu path không bắt đầu bằng /uploads -> bypass
    - Nếu file is_private=false -> cho phép truy cập
    - Nếu file is_private=true -> kiểm tra token
    """   
    path = request.url.path
    if not path.startswith("/uploads/"):
        return await call_next(request)
    # -----------------------------
    # 1️⃣ Trường hợp THUMBNAIL
    # -----------------------------
    if  path.startswith("/uploads/thumbnail/"):
        filename = path.split("/")[-1]  # VD: 274_800x800.webp 
        asset_id, w, h, format = parse_thumbnail_filename(filename)
        # Lấy thumbnail record (nếu có)
        with Session(engine) as session:
            asset = session.get(Assets, asset_id)
            if not asset:
                    return JSONResponse(status_code=404, content={"status": "error", "message": "Original asset not found"})
            # ✅ File public → cho phép ngay
            if not asset.is_private:
                # Get or create thumbnail
                thumbnail = get_or_create_thumbnail(
                    session=session,
                    asset_id=asset_id,
                    width=w,
                    height=h,
                    format=format,
                )
                file_path = os.path.join("uploads/thumbnails", thumbnail.filename)
                if not os.path.exists(file_path):
                    raise HTTPException(status_code=404, detail="File not found")
                
                return FileResponse(file_path, media_type="image/jpeg")

            # ⚠️ Nếu file private → xác thực giống như logic bên dưới
            token = request.headers.get("Authorization")
            api_key = request.headers.get("X-API-Key")

            # Nếu có token → xác thực user
            if token:
                token_value = token.replace("Bearer ", "").strip()
                try:
                    key = get_key(token_value)
                    payload = jwt.decode(token_value, key, algorithms=[ALGORITHM], options={"verify_aud": False})
                    sub = payload.get("sub")
                    user = session.exec(select(Users).where(Users.sub == sub)).first()
                    
                    # Tìm file gốc để kiểm tra quyền
                    asset = session.get(Assets, asset_id)
                    if not asset:
                        return JSONResponse(status_code=404, content={"status": "error", "message": "Original asset not found"})

                    if not user or user.id != asset.project_id:
                        return JSONResponse(status_code=403, content={"status": "error", "message": "Permission denied"})

                    # ✅ OK
                    # Get or create thumbnail
                    thumbnail = get_or_create_thumbnail(
                        session=session,
                        asset_id=asset_id,
                        width=w,
                        height=h,
                        format=format,
                    )
                    file_path = os.path.join("uploads/thumbnails", thumbnail.filename)
                    if not os.path.exists(file_path):
                        raise HTTPException(status_code=404, detail="File not found")
                    
                    return FileResponse(file_path, media_type="image/jpeg")
                except JWTError:
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid token"})

            # Nếu có API key → xác thực external
            elif api_key:
                project = session.get(Projects, asset.project_id)
                
                signature = request.headers.get("X-Signature")
                timestamp = request.headers.get("X-Timestamp")
                message = f"{timestamp}:{api_key}"
                expected_signature = hmac.new(
                    project.api_secret.encode(),
                    message.encode(),
                    hashlib.sha256
                ).hexdigest()

                if not hmac.compare_digest(signature, expected_signature):
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid signature"})

                # ✅ OK
                # Get or create thumbnail
                thumbnail = get_or_create_thumbnail(
                    session=session,
                    asset_id=asset_id,
                    width=w,
                    height=h,
                    format=format,
                )
                file_path = os.path.join("uploads/thumbnails", thumbnail.filename)
                if not os.path.exists(file_path):
                    raise HTTPException(status_code=404, detail="File not found")
                
                return FileResponse(file_path, media_type="image/jpeg")

            else:
                return JSONResponse(status_code=401, content={"status": "error", "message": "Unauthorized"})
    # -----------------------------
    # 2️⃣ Trường hợp file gốc 
    # -----------------------------
    try:
        # -----------------------------
        # Phân tích đường dẫn file
        # -----------------------------
        path_parts = path.split("/")
        
        if len(path_parts) < 4:
            return JSONResponse(status_code=404, content={"status": "error", "message": "File not found 1"})
        path = "/".join(path_parts[2:])
        print("path",path)
        with Session(engine) as session:
            asset = session.exec(
                select(Assets).where(Assets.path == path)    
            ).first()
            user = session.exec(
                select(Users)
                .join(Projects, Users.id == Projects.user_id)
                .join(Assets, Projects.id == Assets.project_id)
                .where(Assets.path == path)
            ).first()
            if not asset:
                return JSONResponse(status_code=404, content={"status": "error", "message": "File not found 2"})
            file_path = os.path.join("uploads", path)

            if not os.path.exists(file_path):
                return JSONResponse(status_code=404, content={"status": "error", "message": "File not found 3"})
            # -----------------------------
            # 2️⃣ File công khai -> cho phép
            # -----------------------------
            if not asset.is_private:
                return FileResponse(file_path, media_type=asset.file_type)
            
            # -----------------------------
            # 3️⃣ File private -> kiểm tra token hoặc API key
            # -----------------------------
            token = request.headers.get("Authorization")

            if token:
                # --- Xử lý xác thực người dùng (JWT) ---
                token_value = token.replace("Bearer ", "").strip()
                try:
                    key = get_key(token_value)
                    payload = jwt.decode(
                        token_value,
                        key,
                        algorithms=[ALGORITHM],
                        options={"verify_aud": False},
                    )

                    sub = payload.get("sub")
                    if not sub:
                        raise JWTError("Missing sub")

                    current_user = session.exec(select(Users).where(Users.sub == sub)).first()
                    if not current_user:
                        return JSONResponse(status_code=403, content={"status": "error", "message": "User not found"})

                    if user.id != current_user.id:
                        return JSONResponse(status_code=403, content={"status": "error", "message": "No permission"})

                    # ✅ Token hợp lệ -> trả file
                    return FileResponse(file_path, media_type=asset.file_type)

                except JWTError:
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid token"})

            else:
                # --- Xử lý xác thực external client ---
                api_key = request.headers.get("X-API-Key")
                signature = request.headers.get("X-Signature")
                timestamp = request.headers.get("X-Timestamp")

                if not (api_key and signature and timestamp):
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Authentication required"})

                # Kiểm tra hết hạn (5 phút)
                try:
                    ts = int(timestamp)
                except ValueError:
                    return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid timestamp"})
                
                if abs(time.time() - ts) > 300:
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Signature expired"})

                project = session.exec(select(Projects).where(Projects.api_key == api_key)).first()
                if not project:
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid API key"})

                message = f"{timestamp}:{api_key}"
                expected_signature = hmac.new(
                    project.api_secret.encode(),
                    message.encode(),
                    hashlib.sha256,
                ).hexdigest()

                if not hmac.compare_digest(signature, expected_signature):
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid signature"})

                # ✅ Client hợp lệ -> trả file
                return FileResponse(file_path, media_type=asset.file_type)

    except Exception as e:
        print(f"❌ Static middleware error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error"})

   
