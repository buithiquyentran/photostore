from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from fastapi import Query

from typing import Optional
from starlette.responses import JSONResponse

from db.session import get_session
from models import  Projects, Folders, Assets , Users, Embeddings
from dependencies.dependencies import get_current_user
from utils.folder_finder import find_folder_by_path

from utils.build_tree import build_tree
from utils.slug import create_slug
router = APIRouter(prefix="/folders", tags=["Folders"])

@router.get("/all")
def get_folders(
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

from pydantic import BaseModel, Field, validator

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
        select(Projects).where(Projects.slug == req.project_slug)).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Bạn không có quyền tạo folder trong project này"
        )
        
    # 2. Validate parent_id (nếu có)
    parent_folder = None
    if req.folder_slug:
        parent_folder = session.exec(
        select(Folders).where(Folders.slug == req.folder_slug)).first()
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
    # 3. Check duplicate folder name trong cùng level
    if parent_folder :
        duplicate = session.exec(
            select(Folders)
            .where(Folders.project_id == project.id)
            .where(Folders.parent_id == parent_folder.id)
            .where(Folders.name == req.name)
        ).first()
    
        if duplicate:
            raise HTTPException(
                status_code=409, 
                detail=f"Folder '{req.name}' đã tồn tại trong cùng cấp"
            )
    
        # Check duplicate slug trong cùng level
        existing_folder = session.exec(
            select(Folders)
            .where(Folders.project_id == project.id)
            .where(Folders.parent_id == parent_folder.id)
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
                    .where(Folders.parent_id == parent_folder.id)
                    .where(Folders.slug == new_slug)
                ).first()
                if not existing_folder:
                    folder_slug = new_slug
                    break
                counter += 1
        
    try:
        # 5. Tạo folder mới
        new_folder = Folders(
            name=req.name,
            slug=folder_slug,
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

@router.get("/contents")
def get_folder_contents(
    path: str = Query(..., description="Ví dụ: demo_app/children"),
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        parts = path.split("/")
        project_slug = parts[0]
        folder_path = "/".join(parts[1:])
        # 🔹 Tìm project theo slug
        project = session.exec(
            select(Projects)
            .join(Users, Users.id == Projects.user_id)
            .where((Users.id == current_user.id) & (Projects.slug == project_slug))
        ).first()

        if not project:
            raise HTTPException(404, "Project not found")
        if not folder_path:
            folders = session.exec(select(Folders).where ((project.id == Folders.project_id) & (Folders.parent_id == None)))
            return {
                "status": 1,
                "folders": [f.model_dump() for f in folders],
                "assets": [],
            }
        # 🔹 Tìm folder theo đường dẫn (dùng hàm helper)
        folder = find_folder_by_path(session, project.id, folder_path)

        if not folder:
            raise HTTPException(404, "Folder not found")
        

        # 🔹 Lấy các folder con
        child_folders = session.exec(
            select(Folders)
            .where((Folders.parent_id == folder.id) & (Folders.project_id == project.id))
        ).all()

        # 🔹 Lấy assets trong folder đó
        assets = session.exec(
            select(Assets)
            .where((Assets.folder_id == folder.id) & (Assets.is_deleted == False))
        ).all()

        return {
            "status": 1,
            "folders": [f.model_dump() for f in child_folders],
            "assets": [a.model_dump() for a in assets],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
