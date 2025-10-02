"""
Middleware để kiểm tra quyền truy cập static files
"""
from fastapi import Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session, select
from pathlib import Path
import os

from models import Assets, Projects, Folders, Users
from dependencies.dependencies import get_key, ALGORITHM
from jose import jwt, JWTError
from db.session import engine

UPLOAD_DIR = Path("uploads")

async def verify_static_access(request: Request, call_next):
    """
    Middleware để kiểm tra quyền truy cập static files.
    - Nếu path không bắt đầu bằng /uploads -> bypass
    - Nếu file is_private=false -> cho phép truy cập
    - Nếu file is_private=true -> kiểm tra token
    """
    # Bypass non-uploads paths
    if not request.url.path.startswith("/uploads/"):
        return await call_next(request)
        
    try:
        # Extract path components
        path_parts = request.url.path.split("/")
        if len(path_parts) < 4:  # /uploads/project/file
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found"
                }
            )
            
        project_slug = path_parts[2]
        filename = path_parts[-1]
        folder_path = "/".join(path_parts[3:-1])
        
        # Check if file exists
        file_path = (UPLOAD_DIR / project_slug / folder_path / filename).resolve()
        if not file_path.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "File not found"
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
                            "message": "File not found"
                        }
                    )
                
                # Get project for access control
                project = session.get(Projects, asset.project_id)
                if not project:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "status": "error",
                            "message": "File not found"
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