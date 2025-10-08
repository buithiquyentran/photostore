"""
Route để serve static files (uploads) với kiểm tra quyền truy cập
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session, select
from pathlib import Path
import os

from models import Assets, Projects, Folders, Users
from dependencies.dependencies import get_current_user
from db.session import get_session

router = APIRouter(tags=["Static Files"])

UPLOAD_DIR = Path("uploads")

# @router.get("/uploads/{project_slug}/{folder_path:path}/{filename}")
# async def get_upload(
#     project_slug: str,
#     folder_path: str,
#     filename: str,
#     session: Session = Depends(get_session),
#     current_user = Depends(get_optional_user)  # Optional vì file có thể public
# ):
#     """
#     Serve uploaded files với kiểm tra quyền truy cập:
#     - Nếu file is_private=true thì phải có token hợp lệ
#     - Nếu file is_private=false thì cho phép truy cập trực tiếp
#     """
#     try:
#         # Tìm asset dựa vào path
#         full_path = f"{project_slug}/{folder_path}/{filename}"
        
#         # Tìm asset theo system_name (filename)
#         asset = session.exec(
#             select(Assets)
#             .join(Folders, Assets.folder_id == Folders.id)
#             .join(Projects, Folders.project_id == Projects.id)
#             .where(Assets.system_name == filename)
#             .where(Projects.slug == project_slug)
#         ).first()
        
#         if not asset:
#             raise HTTPException(status_code=404, detail="File not found")
            
#         # Kiểm tra quyền truy cập
#         if asset.is_private:
#             if not current_user:
#                 raise HTTPException(status_code=401, detail="Missing token")
                
#             # Kiểm tra owner
#             project = session.exec(
#                 select(Projects)
#                 .where(Projects.id == asset.project_id)
#             ).first()
            
#             if not project or project.user_id != current_user.id:
#                 raise HTTPException(status_code=403, detail="Access denied")
        
#         # Build file path
#         file_path = UPLOAD_DIR / project_slug / folder_path / filename
        
#         if not file_path.exists():
#             raise HTTPException(status_code=404, detail="File not found")
            
#         # Serve file
#         return FileResponse(
#             file_path,
#             media_type=asset.file_type,
#             filename=asset.name  # Trả về original filename khi download
#         )
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from fastapi.responses import FileResponse
import os

@router.get("/uploads/{file_path:path}")
async def get_upload(file_path: str):
    file_path = os.path.join("uploads", file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="image/jpeg")

@router.get("/assets/get-by-folder/{folder_path:path}")
async def get_upload(folder_path: str, session: Session = Depends(get_session)):
    abs_path = os.path.join("uploads", folder_path).replace("\\", "/")
    # Nếu là thư mục → query tất cả assets trong folder đó
    if os.path.isdir(abs_path):
        # Bỏ prefix "uploads/" để so khớp với DB path
        db_folder_path = folder_path.rstrip("/")

        # Truy vấn tất cả asset có folder_path trùng
        assets = session.exec(
            select(Assets)
            .where(Assets.folder_path == db_folder_path)
            .where(Assets.is_deleted == False)
        ).all()

        if not assets:
            raise HTTPException(404, "No assets found in this folder")

        data = []
        for a in assets:
            data.append({
                "id": a.id,
                "name": a.name,
                "system_name": a.system_name,
                "path": a.path,
                "file_url": a.file_url,
                "width": a.width,
                "height": a.height,
                "file_type": a.file_type,
                "created_at": a.created_at,
            })

        return JSONResponse(content={"status": 1, "count": len(data), "data": data})

    # Nếu không phải file hoặc folder → 404
    raise HTTPException(404, "Invalid file path")
@router.get("/metadata/{file_path:path}")
async def get_metadata(file_path: str,session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    asset = session.exec(select(Assets).where(Assets.path == file_path)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    folder = session.exec(select(Folders).where(Folders.id == asset.folder_id)).first() if asset else None
    
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
