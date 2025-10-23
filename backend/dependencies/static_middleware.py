"""
Middleware để kiểm tra quyền truy cập static files
"""
from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session, select
from pathlib import Path
import os

from models import Assets, Projects, Folders, Users, Thumbnails
from dependencies.dependencies import get_key, ALGORITHM
from jose import jwt, JWTError
from db.session import engine
import time, hmac, hashlib
from fastapi import Request

UPLOAD_DIR = Path("uploads")
async def verify_static_access(request: Request, call_next):
    path = request.url.path
    if not path.startswith("/uploads/"):
        return await call_next(request)
    # -----------------------------
    # 1️⃣ Trường hợp THUMBNAIL
    # -----------------------------
    if  path.startswith("/uploads/thumbnail/"):
        filename = path.split("/")[-1]  # VD: 274_800x800.webp
        base_id = filename.split("_")[0]  # asset_id = 274

        # Lấy thumbnail record (nếu có)
        with Session(engine) as session:
            thumb = session.exec(
                select(Thumbnails).where(Thumbnails.asset_id == base_id)
            ).first()

            if not thumb:
                return JSONResponse(status_code=404, content={"status": "error", "message": "Thumbnail not found"})

            # Tìm file gốc để kiểm tra quyền
            asset = session.get(Assets, thumb.asset_id)
            if not asset:
                return JSONResponse(status_code=404, content={"status": "error", "message": "Original asset not found"})

            project = session.get(Projects, asset.project_id)
            if not project:
                return JSONResponse(status_code=404, content={"status": "error", "message": "Project not found"})

            # ✅ File public → cho phép ngay
            if not asset.is_private:
                return FileResponse(
                    os.path.join("uploads", "thumbnails", filename),
                    media_type=asset.file_type or "image/webp"
                )

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
                    if not user or user.id != project.user_id:
                        return JSONResponse(status_code=403, content={"status": "error", "message": "Permission denied"})

                    # ✅ OK
                    return FileResponse(
                        os.path.join("uploads", "thumbnails", filename),
                        media_type=asset.file_type or "image/webp"
                    )
                except JWTError:
                    return JSONResponse(status_code=401, content={"status": "error", "message": "Invalid token"})

            # Nếu có API key → xác thực external
            elif api_key:
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

                return FileResponse(
                    os.path.join("uploads", "thumbnails", filename),
                    media_type=asset.file_type or "image/webp"
                )

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
            return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})

        user_id = path_parts[2]
        project_slug = path_parts[3]
        filename = path_parts[-1]
        folder_path = "/".join(path_parts[4:-1])
        file_path = (UPLOAD_DIR / user_id / project_slug / folder_path / filename).resolve()

        if not file_path.exists():
            return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})

        with Session(engine) as session:
            asset = session.exec(
                select(Assets)
                .join(Folders, Assets.folder_id == Folders.id)
                .join(Projects, Folders.project_id == Projects.id)
                .where(Assets.system_name == filename)
                .where(Projects.slug == project_slug)
            ).first()

            if not asset:
                return JSONResponse(status_code=404, content={"status": "error", "message": "File not found"})

            project = session.get(Projects, asset.project_id)
            if not project:
                return JSONResponse(status_code=404, content={"status": "error", "message": "Project not found"})

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

                    if project.user_id != current_user.id:
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

    """
    Middleware để kiểm tra quyền truy cập static files.
    - Nếu path không bắt đầu bằng /uploads -> bypass
    - Nếu file is_private=false -> cho phép truy cập
    - Nếu file is_private=true -> kiểm tra token
    """  
    try:
        # Extract path components
        path_parts = path.split("/")
        if len(path_parts) < 4:  # /uploads/project/file
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found 1"
                }
            )
        user_id = path_parts[2]
        project_slug = path_parts[3]
        filename = path_parts[-1]
        folder_path = "/".join(path_parts[4:-1])
        
        # Check if file exists
        file_path = (UPLOAD_DIR / user_id / project_slug / folder_path / filename).resolve()
        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found 2"
                }
            )
            
        # Find asset in database
        with Session(engine) as session:
            try:
                # Get asset with project info
                asset = session.exec(
                    select(Assets)
                    .join(Folders, Assets.folder_id == Folders.id)
                    .join(Projects, Folders.project_id == Projects.id)
                    .where(Assets.system_name == filename)
                    .where(Projects.slug == project_slug)
                ).first()
                
                if not asset:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": "error",
                            "message": "File not found 3"
                        }
                    )
                
                # Get project for access control
                project = session.get(Projects, asset.project_id)
                if not project:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": "error",
                            "message": "File not found 4"
                        }
                    )
                
                # Public file - allow access
                if not asset.is_private:
                    return FileResponse(
                        file_path,
                        media_type=asset.file_type,
                        # filename=asset.name
                    )
                
                # Private file - check token
                token = request.headers.get("Authorization")
                if not token:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "status": "error",
                            "message": "This file is private and requires authentication"
                        }
                    )
                
                # Validate token
                # Validate token format
                token_value = token.replace("Bearer ", "").strip()
                if not token_value:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "status": "error",
                            "message": "Invalid token format"
                        }
                    )

                try:
                    # Parse token thành payload
                    key = get_key(token_value)
                    payload = jwt.decode(
                        token_value,
                        key,
                        algorithms=[ALGORITHM],
                        options={"verify_aud": False}
                    )
                    
                    if not payload or not payload.get("sub"):
                        return JSONResponse(
                            status_code=401,
                            content={
                                "status": "error",
                                "message": "Invalid or expired token"
                            }
                        )
                    
                    # Tìm user trong database
                    sub = payload.get("sub")
                    current_user = session.exec(select(Users).where(Users.sub == sub)).first()
                    
                    if not current_user:
                        # User chưa tồn tại trong database, tạo mới từ token info
                        email = payload.get("email")
                        username = payload.get("preferred_username") or email
                        
                        if not email:
                            return JSONResponse(
                                status_code=401,
                                content={
                                    "status": "error",
                                    "message": "Invalid token: missing email"
                                }
                            )
                            
                        current_user = Users(
                            sub=sub,
                            email=email,
                            username=username,
                            is_superuser=False
                        )
                        session.add(current_user)
                        session.commit()
                        session.refresh(current_user)
                        print(f"✅ Created new user in DB: {current_user.email} (id: {current_user.id})")
                    
                    # Check ownership
                    if project.user_id != current_user.id:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "status": "error",
                                "message": "You don't have permission to access this file"
                            }
                        )
                    
                    # Owner access - serve file
                    return FileResponse(
                        file_path,
                        media_type=asset.file_type,
                        # filename=asset.name
                    )
                    
                except JWTError:
                    return JSONResponse(
                        status_code=401,
                        content={
                            "status": "error",
                            "message": "Invalid or expired token"
                        }
                    )
                except Exception as e:
                    print(f"❌ Error validating token: {e}")
                    return JSONResponse(
                        status_code=500,
                        content={
                            "status": "error",
                            "message": "Internal server error"
                        }
                    )
                    
            except Exception:
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "message": "Internal server error"
                    }
                )
                
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )