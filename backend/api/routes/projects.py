from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from db.session import get_session
from models.projects import Projects
from dependencies.dependencies import get_current_user

router = APIRouter(tags=["Projects"])

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False

@router.get("/projects")
def get_projects(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Lấy danh sách projects của user hiện tại
    """
    try:
        statement = select(Projects).where(Projects.user_id == current_user.id)
        results = session.exec(statement).all()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")

@router.post("/projects")
def create_project(
    project_data: ProjectCreateRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tạo mới một project cho user hiện tại
    """
    try:
        # Tạo project với user_id từ current_user
        new_project = Projects(
            user_id=current_user.id,
            name=project_data.name,
            description=project_data.description,
            is_default=project_data.is_default
        )
        
        session.add(new_project)
        session.commit()
        session.refresh(new_project)
        
        return {"status": "success", "data": new_project}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm project: {e}")

@router.put("/projects/{project_id}")
def update_project(project_id: int, project_update: Projects, session: Session = Depends(get_session)):
    """
    Sửa thông tin một project
    """
    project = session.get(Projects, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    try:
        update_data = project_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        session.add(project)
        session.commit()
        session.refresh(project)
        return {"status": "success", "data": project}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật project: {e}")

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    """
    Xóa một project
    """
    project = session.get(Projects, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    try:
        session.delete(project)
        session.commit()
        return {"status": "success", "message": "Xóa project thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa project: {e}")
