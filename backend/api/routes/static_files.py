"""
Route để serve static files (uploads) với kiểm tra quyền truy cập
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session, select
from pathlib import Path
import os
from fastapi.responses import RedirectResponse

from models import Assets, Projects, Folders, Users
from dependencies.dependencies import get_current_user
from db.session import get_session
from db.crud_tag import (
    get_tags_for_asset,

)
from fastapi import Query
from fastapi import  status

from db.crud_thumbnail import get_or_create_thumbnail
router = APIRouter(tags=["Static Files"])

UPLOAD_DIR = Path("uploads")



from fastapi.responses import FileResponse
import os

@router.get("/uploads/{file_path:path}")
async def get_upload(file_path: str):
    file_path = os.path.join("uploads", file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="image/jpeg")

@router.get("/thumbnail/{asset_id}", response_class=RedirectResponse)
# Get or create thumbnail
def get_thumbnail(
    asset_id: int,
    w: int = Query(..., ge=50, le=2000, description="Width in pixels"),
    h: int = Query(..., ge=50, le=2000, description="Height in pixels"),
    format: str = Query("webp", regex="^(webp|jpg|jpeg|png)$", description="Output format"),
    q: int = Query(80, ge=10, le=100, description="Quality (10-100)"),
    session: Session = Depends(get_session)
):
    """
    Get or create thumbnail for an image file.
    Returns redirect to the thumbnail URL.
    
    Parameters:
    - asset_id: ID of the original file
    - w: Width in pixels (50-2000)
    - h: Height in pixels (50-2000) 
    - format: Output format (webp, jpg, jpeg, png)
    - q: Quality 10-100 (default 80)
    """
    try:
        # Get or create thumbnail
        thumbnail = get_or_create_thumbnail(
            session=session,
            asset_id=asset_id,
            width=w,
            height=h,
            format=format,
            quality=q
        )
        
        # Redirect to thumbnail URL
        return RedirectResponse(url=thumbnail.file_url, status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/metadata/{file_path:path}")
async def get_metadata(file_path: str,session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    asset = session.exec(select(Assets).where(Assets.path == file_path)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    folder = session.exec(select(Folders).where(Folders.id == asset.folder_id)).first() if asset else None
    tags = get_tags_for_asset(session, asset.id)
    
    if not folder:
        raise HTTPException(404, "Folder not found")
    
    user  = session.exec(select(Users)
            .join(Projects, Users.id == Projects.user_id)
            .join(Folders, Projects.id == Folders.project_id)
            .where(Folders.id == asset.folder_id)
        ).first()
    if not user:
        raise HTTPException(404, "Owner not found")
    if current_user.id != user.id:
        raise HTTPException(403, "Forbidden")
    result = asset.dict()
    result["location"] = folder.name
    result["tags"] = tags
    
    return {"status": 'success', "data": result}

@router.get("/nextprev/metadata/{file_path:path}")
def get_next_prev(file_path: str, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    asset = session.exec(select(Assets).where(Assets.path == file_path)).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Assets not found")
    user  = session.exec(select(Users)
            .join(Projects, Users.id == Projects.user_id)
            .join(Folders, Projects.id == Folders.project_id)
            .join(Assets, Folders.id == Assets.folder_id)
            .where(Assets.id == asset.id)
        ).first()
    if not user:
        raise HTTPException(404, "Owner not found")
    if current_user.id != user.id:
        raise HTTPException(401, "Unauthorized")
    statement = (
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == current_user.id)
        )
   # prev: ảnh có id nhỏ hơn trong cùng project
    prev_asset = session.exec(
        statement.where(Assets.id < asset.id).order_by(Assets.id.desc()).limit(1)
    ).first()

    # next: ảnh có id lớn hơn trong cùng project
    next_asset = session.exec(
        statement.where(Assets.id > asset.id).order_by(Assets.id.asc()).limit(1)
    ).first()

    return {
        "prev": {"path": prev_asset.path} if prev_asset else None,
        "next": {"path": next_asset.path} if next_asset else None,
    }
