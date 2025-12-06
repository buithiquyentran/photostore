from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from fastapi import Query

from typing import Optional
from starlette.responses import JSONResponse
from pydantic import BaseModel, Field, validator


from db.session import get_session
from models import  Projects, Folders, Assets , Users, Embeddings
from dependencies.dependencies import get_current_user
from utils.folder_finder import find_folder_by_path

from utils.build_tree import build_tree
from utils.slug import create_slug
router = APIRouter(prefix="/folders", tags=["Folders"])

@router.get("/folder_tree")
def get_folder_tree(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    try:
        # Lấy tất cả folder thuộc user hiện tại (qua project)
        folders = (
            session.query(Folders)
            .join(Projects, Projects.id == Folders.project_id)
            .join(Users, Users.id == Projects.user_id)
            .filter(Users.id == current_user.id)
            .all()
        )

        # Lấy danh sách project để nhóm
        projects = (
            session.query(Projects)
            .join(Users, Users.id == Projects.user_id)
            .filter(Users.id == current_user.id)
            .all()
        )

        # Nhóm folder theo project
        project_dict = {}
        for p in projects:
            project_dict[p.id] = {
                "id": p.slug,
                "name": p.name,
                "slug" : p.slug,
                "children": []
            }

        # Gọi hàm build_tree để tạo cây thư mục cho từng project
        for p in projects:
            project_folders = [f for f in folders if f.project_id == p.id]
            tree = build_tree(project_folders)
            project_dict[p.id]["children"] = tree

        data = list(project_dict.values())

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": f"Lỗi khi lấy danh sách folder: {e}"}
        )

    return {"status": 1, "data": data}
@router.get("/all")
def get_all(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    try:
        # Lấy tất cả folder thuộc user hiện tại (qua project)
        folders = session.exec(
            select(Folders)
            .join(Projects, Projects.id == Folders.project_id)
            .join(Users, Users.id == Projects.user_id)
            .where((Users.id == current_user.id))
        ).all()
        return {"status": "success", "data": folders}

    except Exception as e:
        return JSONResponse(
            status_code=500, content={"detail": f"Lỗi khi lấy danh sách folder: {e}"}
        )


class FolderCreateRequest(BaseModel):
    project_slug: str = Field(..., description="SLUG của project chứa folder này")
    folder_slug: Optional[str] = Field(None, description="SLUG của folder cha (None nếu là root folder)")
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
    project = session.exec(
        select(Projects).where(Projects.slug == req.project_slug).where(Projects.user_id == current_user.id)).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    
     
    # 2. Validate parent_id (nếu có)
    parent_folder = None
    if req.folder_slug:
        parent_folder = session.exec(
        select(Folders)
        .join(Projects, Projects.id == Folders.project_id)
        .where(Folders.slug == req.folder_slug)
        .where(Projects.slug == req.project_slug)
        .where(Projects.user_id == current_user.id)).first()
        
        if not parent_folder:
            raise HTTPException(status_code=404, detail="Folder cha không tồn tại")
        
        # Parent folder phải thuộc về cùng project
        if parent_folder.project_id != project.id:
            raise HTTPException(
                status_code=400, 
                detail="Folder cha phải thuộc về cùng project"
            )
    # 4. Tạo slug từ name
    folder_slug = create_slug(req.name)
    
    # 3. Check duplicate folder slug trong cùng level
    existing_folder = session.exec(
            select(Folders)
            .where(Folders.project_id == project.id)
            .where(Folders.slug == folder_slug)
        ).first()
        
    if existing_folder:
        # Thêm suffix nếu slug đã tồn tại
        counter = 1
        while existing_folder:
            new_slug = f"{folder_slug}-{counter}"
            existing_folder = session.exec(
                select(Folders)
                .where(Folders.project_id == project.id)
                .where(Folders.slug == new_slug)
            ).first()
            if not existing_folder:
                folder_slug = new_slug
                break
            counter += 1
    if parent_folder:
        folder_path = f"{parent_folder.path}/{folder_slug}"
    else:
        folder_path = f"{project.slug}/{folder_slug}"  # root level    
    try:
        # 5. Tạo folder mới
        new_folder = Folders(
            name=req.name,
            slug=folder_slug,
            path=folder_path,
            parent_id= parent_folder.id if parent_folder else None,
            project_id=project.id,
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
def delete_folder(folder_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
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

