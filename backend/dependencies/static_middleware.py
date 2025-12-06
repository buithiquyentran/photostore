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

from urllib.parse import parse_qs

def parse_thumbnail_filename(filename: str):
    # 1. Tách phần ID và phần tham số (ngăn cách bởi dấu ?)
    if "_" not in filename:
        raise ValueError(f"Invalid filename format (missing query params): {filename}")
    
    id, query_part = filename.split("_", 1)
    
    # 2. Parse Asset ID
    if not id.isdigit():
        raise ValueError(f"Invalid Asset ID: {id}")
    asset_id = int(id)

    # 3. Parse các tham số bằng thư viện chuẩn parse_qs
    # parse_qs trả về dict dạng: {'width': ['500'], 'height': ['500']...}
    params = parse_qs(query_part)

    # Hàm phụ để lấy giá trị an toàn từ dict
    def get_val(key, default=None, required=True):
        values = params.get(key)
        if not values:
            if required:
                raise ValueError(f"Missing required parameter: {key}")
            return default
        return values[0]

    # 4. Trích xuất và ép kiểu
    try:
        width = int(get_val("w"))
        height = int(get_val("h"))
        # format mặc định là jpg nếu không truyền
        ext = get_val("format", default="webp", required=False)
        # quality mặc định là 80 nếu không truyền
        quality = int(get_val("q", default="80", required=False))
        
    except ValueError as e:
        raise ValueError(f"Invalid parameter value: {e}")

    return asset_id, width, height, ext.lower(), quality

# --- Test thử ---
# filename_input = "51?width=500&height=500&format=png&quality=90"  Kết quả: (51, 500, 500, 'png', 90)

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
    if path.startswith("/uploads/thumbnail/"):
        return await call_next(request)
    # -----------------------------
    # 1️⃣ Trường hợp THUMBNAIL
    # -----------------------------
    if  path.startswith("/uploads/public-thumbnail/"):
        filename = path.split("/")[-1]  # VD: 274_800x800.webp 
        print("Thumbnail filename:", filename)
        asset_id, width, height, ext, quality = parse_thumbnail_filename(filename)
        # Lấy thumbnail record (nếu có)
        with Session(engine) as session:
            asset = session.get(Assets, asset_id)
            if not asset:
                    return JSONResponse(status_code=404, content={"status": "error", "message": "Original asset not found"})
            user = session.exec(
                select(Users)
                .join(Projects, Users.id == Projects.user_id)
                .join(Assets, Projects.id == Assets.project_id)
                .where(Assets.id == asset_id)
            ).first()
            # ✅ File public → cho phép ngay
            if not asset.is_private:
                # Get or create thumbnail
                thumbnail = get_or_create_thumbnail(
                    session=session,
                    asset_id=asset_id,
                    user_id=user.id ,
                    width=width,
                    height=height,
                    format=ext,
                    quality=quality
                )
                file_path = os.path.join(f"uploads/{user.id}/thumbnails", thumbnail.filename)
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
                        user_id=user.id,
                        width=width,
                        height=height,
                        format=ext,
                        quality=quality
                    )
                    file_path = os.path.join(f"uploads/{user.id}/thumbnails", thumbnail.filename)
                    if not os.path.exists(file_path):
                        raise HTTPException(status_code=404, detail="File not found")
                    
                    # Determine correct media type
                    media_type = f"image/{ext}"
                    if ext in ["jpg", "jpeg"]:
                        media_type = "image/jpeg"
                    elif ext == "webp":
                        media_type = "image/webp"
                    elif ext == "png":
                        media_type = "image/png"
                    
                    return FileResponse(file_path, media_type=media_type)
                except JWTError:
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid token"})

            # Nếu có API key → xác thực external
            elif api_key:
                project = session.get(Projects, asset.project_id)
                 # Check if project is active
                if not project.is_active:
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "status": "error",
                            "message": "Project is not active. Please contact administrator."
                        }
                    )

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
                    user_id=user.id,
                    width=width,
                    height=height,
                    format=ext,
                    quality=quality
                )
                file_path = os.path.join(f"uploads/{user.id}/thumbnails", thumbnail.filename)
                if not os.path.exists(file_path):
                    raise HTTPException(status_code=404, detail="File not found")
                
                # Determine correct media type
                media_type = f"image/{ext}"
                if ext in ["jpg", "jpeg"]:
                    media_type = "image/jpeg"
                elif ext == "webp":
                    media_type = "image/webp"
                elif ext == "png":
                    media_type = "image/png"
                
                return FileResponse(file_path, media_type=media_type)

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
            if not user:
                raise HTTPException(404, "Owner not found")
            file_path = os.path.join("uploads", str(user.id), path)
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

   
