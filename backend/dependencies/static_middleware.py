"""
Middleware để kiểm tra quyền truy cập static files
"""
from fastapi import Request, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from pathlib import Path
import os

from models import Assets, Projects, Folders
from dependencies.dependencies import get_optional_user
from db.session import get_session, engine

UPLOAD_DIR = Path("uploads")

async def verify_static_access(request: Request, call_next):
    """
    Middleware để kiểm tra quyền truy cập static files.
    - Nếu path không bắt đầu bằng /uploads -> bypass
    - Nếu file is_private=false -> cho phép truy cập
    - Nếu file is_private=true -> kiểm tra token
    """
    if not request.url.path.startswith("/uploads/"):
        return await call_next(request)
        
    try:
        # Extract path components
        path_parts = request.url.path.split("/")
        if len(path_parts) < 4:  # /uploads/project/file
            print(f"❌ Invalid path: {request.url.path}")
            raise HTTPException(status_code=404, detail="Invalid path")
            
        project_slug = path_parts[2]
        filename = path_parts[-1]
        folder_path = "/".join(path_parts[3:-1])
        
        print(f"🔍 Looking for file:")
        print(f"  Project: {project_slug}")
        print(f"  Folder: {folder_path}")
        print(f"  File: {filename}")
        
        # Check if file exists
        file_path = UPLOAD_DIR / project_slug / folder_path / filename
        print(f"  Full path: {file_path.absolute()}")
        
        if not file_path.exists():
            print(f"❌ File not found at {file_path}")
            # Check if uploads directory exists
            if not UPLOAD_DIR.exists():
                print(f"❌ Uploads directory not found at {UPLOAD_DIR.absolute()}")
            # Check parent directories
            elif not (UPLOAD_DIR / project_slug).exists():
                print(f"❌ Project directory not found at {UPLOAD_DIR / project_slug}")
            elif not (UPLOAD_DIR / project_slug / folder_path).exists():
                print(f"❌ Folder directory not found at {UPLOAD_DIR / project_slug / folder_path}")
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            
        # Find asset
        with Session(engine) as session:
            asset = session.exec(
                select(Assets)
                .join(Folders, Assets.folder_id == Folders.id)
                .join(Projects, Folders.project_id == Projects.id)
                .where(Assets.system_name == filename)
                .where(Projects.slug == project_slug)
            ).first()
            
            if not asset:
                raise HTTPException(status_code=404, detail="File not found")
                
            # Public file - allow access
            if not asset.is_private:
                return FileResponse(
                    file_path,
                    media_type=asset.file_type,
                    filename=asset.name
                )
                
            # Private file - check token
            token = request.headers.get("Authorization")
            if not token:
                raise HTTPException(status_code=401, detail="Missing token")
                
            # Get user from token
            current_user = await get_optional_user(token.split(" ")[1], session)
            if not current_user:
                raise HTTPException(status_code=401, detail="Invalid token")
                
            # Check ownership
            project = session.exec(
                select(Projects)
                .where(Projects.id == asset.project_id)
            ).first()
            
            if not project or project.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
                
            # Owner access - serve file
            return FileResponse(
                file_path,
                media_type=asset.file_type,
                filename=asset.name
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
