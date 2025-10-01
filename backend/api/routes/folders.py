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

from pydantic import BaseModel, Field, validator

class FolderCreateRequest(BaseModel):
    project_id: int = Field(..., description="ID của project chứa folder này")
    parent_id: Optional[int] = Field(None, description="ID của folder cha (None nếu là root folder)")
    name: str = Field(..., min_length=1, max_length=100, description="Tên folder")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate folder name"""
        # Remove leading/trailing spaces
        v = v.strip()
        if not v:
            raise ValueError("Tên folder không được để trống")
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Tên folder không được chứa các ký tự: {', '.join(invalid_chars)}")
        return v

@router.post("/create")
def create_folder(
    req: FolderCreateRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tạo folder mới trong project.
    
    - Bắt buộc phải chỉ định project_id
    - Validate project thuộc về user hiện tại
    - Validate parent_id (nếu có) thuộc về cùng project
    - Check duplicate folder name trong cùng level
    """
    # 1. Validate project tồn tại và thuộc về user
    project = session.get(Projects, req.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Bạn không có quyền tạo folder trong project này"
        )
    
    # 2. Validate parent_id (nếu có)
    if req.parent_id:
        parent_folder = session.get(Folders, req.parent_id)
        
        if not parent_folder:
            raise HTTPException(status_code=404, detail="Folder cha không tồn tại")
        
        # Parent folder phải thuộc về cùng project
        if parent_folder.project_id != req.project_id:
            raise HTTPException(
                status_code=400, 
                detail="Folder cha phải thuộc về cùng project"
            )
    
    # 3. Check duplicate folder name trong cùng level
    duplicate = session.exec(
        select(Folders)
        .where(Folders.project_id == req.project_id)
        .where(Folders.parent_id == req.parent_id)
        .where(Folders.name == req.name)
    ).first()
    
    if duplicate:
        raise HTTPException(
            status_code=409, 
            detail=f"Folder '{req.name}' đã tồn tại trong cùng cấp"
        )
    
    # 4. Tạo folder mới
    try:
        new_folder = Folders(
            name=req.name,
            parent_id=req.parent_id,
            project_id=req.project_id,
            is_default=False
        )
        
        session.add(new_folder)
        session.commit()
        session.refresh(new_folder)
        
        return {
            "status": 1,
            "message": "Folder đã được tạo thành công",
            "data": new_folder
        }
    
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Lỗi khi tạo folder: {str(e)}"
        )
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
