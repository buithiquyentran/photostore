from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from starlette.responses import JSONResponse

from db.session import get_session
from models import  Projects, Folders, Assets , Users, Embeddings
from dependencies.dependencies import get_current_user
from utils.build_tree import build_tree
router = APIRouter(prefix="/users/folders", tags=["Folders"])

@router.get("/all")
def get_folders(session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    try:
        folders = session.exec(select(Folders).join(Projects, Projects.id == Folders.project_id).join(Users, Users.id == Projects.user_id).where(Users.id == current_user.id)).all()
        data = build_tree(folders)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Lỗi khi lấy danh sách folder: {e}"})

    return {"status": 1, "data": data}

from pydantic import BaseModel

class FolderCreateRequest(BaseModel):
    parent_id: Optional[int] = None
    name: str

@router.post("/create")
def create_folder(
    req: FolderCreateRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    try:
        if req.parent_id:
            parent = session.get(Folders, req.parent_id)
            if not parent:
                raise HTTPException(status_code=404, detail="Folder cha không tồn tại")
            project_id = parent.project_id
            
        else:
            
            # lấy project default của user
            project = session.exec(
                select(Projects).where(Projects.user_id == current_user.id, Projects.is_default == True)
            ).first()
            if not project:
                return JSONResponse (status_code=404, content={"detail": "User không có project default"})
            project_id = project.id
         # ✅ Check tồn tại folder cùng cấp
        exists = session.exec(
            select(Folders)
            .where(Folders.project_id == project_id)
            .where(Folders.parent_id == req.parent_id)
            .where(Folders.name == req.name)
        ).first()

        if exists:
            return JSONResponse (status_code=400, content={"detail": f"Folder '{req.name}' đã tồn tại trong cùng cấp"})
        new_folder = Folders(
            name=req.name,
            parent_id=req.parent_id,
            project_id=project_id,
            is_default=False
        )

        session.add(new_folder)
        session.commit()
        session.refresh(new_folder)

        return {"status": 1, "data": new_folder}

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Lỗi khi tạo folder: {e}"})
@router.delete("/{folder_id}")
def delete_project(folder_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    folder = session.exec(select(Folders).where(Folders.id == folder_id)).first() 
    if not folder:
        raise HTTPException(404, "Folder not found")
    user  = session.exec(select(Users)
            .join(Projects, Users.id == Projects.user_id)
            .join(Folders, Projects.id == Folders.project_id)
            .where(Folders.id == folder.id)
        ).first()
    if not user:
        raise HTTPException(404, "Owner not found")
    if current_user.id != user.id:
        raise HTTPException(401, "Unauthorized")
    session.delete(folder)
    session.commit()
    return {"status": 1, "data": f"Folder {folder.name} deleted"}
