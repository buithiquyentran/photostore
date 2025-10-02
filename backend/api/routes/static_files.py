"""
Route để serve static files (uploads) với kiểm tra quyền truy cập
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from pathlib import Path
import os

from models import Assets, Projects, Folders
from dependencies.dependencies import get_optional_user
from db.session import get_session

router = APIRouter(tags=["Static Files"])

UPLOAD_DIR = Path("uploads")

@router.get("/uploads/{project_slug}/{folder_path:path}/{filename}")
async def get_upload(
    project_slug: str,
    folder_path: str,
    filename: str,
    session: Session = Depends(get_session),
    current_user = Depends(get_optional_user)  # Optional vì file có thể public
):
    """
    Serve uploaded files với kiểm tra quyền truy cập:
    - Nếu file is_private=true thì phải có token hợp lệ
    - Nếu file is_private=false thì cho phép truy cập trực tiếp
    """
    try:
        # Tìm asset dựa vào path
        full_path = f"{project_slug}/{folder_path}/{filename}"
        
        # Tìm asset theo system_name (filename)
        asset = session.exec(
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Assets.system_name == filename)
            .where(Projects.slug == project_slug)
        ).first()
        
        if not asset:
            raise HTTPException(status_code=404, detail="File not found")
            
        # Kiểm tra quyền truy cập
        if asset.is_private:
            if not current_user:
                raise HTTPException(status_code=401, detail="Missing token")
                
            # Kiểm tra owner
            project = session.exec(
                select(Projects)
                .where(Projects.id == asset.project_id)
            ).first()
            
            if not project or project.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Build file path
        file_path = UPLOAD_DIR / project_slug / folder_path / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
            
        # Serve file
        return FileResponse(
            file_path,
            media_type=asset.file_type,
            filename=asset.name  # Trả về original filename khi download
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
