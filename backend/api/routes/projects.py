from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.session import get_session
from models.projects import Projects  

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/projects")
def get_projects(session: Session = Depends(get_session)):
    """
    Lấy danh sách các hình ảnh từ bảng Projects
    """
    try:
        statement = select(Projects)
        results = session.exec(statement).all()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
