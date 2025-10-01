from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.session import get_session
from models.projects import Projects

router = APIRouter(tags=["Projects"])

@router.get("/projects")
def get_projects(session: Session = Depends(get_session)):
    """
    Lấy danh sách các hình ảnh từ bảng Projects
    """
    try:
        statement = select(Projects)
        results = session.exec(statement).all()
        return {"status": 1, "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")

@router.post("/projects")
def create_project(project: Projects, session: Session = Depends(get_session)):
    """
    Thêm mới một project
    """
    try:
        session.add(project)
        session.commit()
        session.refresh(project)
        return {"status": 1, "data": project}
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
        return {"status": 1, "data": project}
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
        return {"status": 1, "message": "Xóa project thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa project: {e}")
