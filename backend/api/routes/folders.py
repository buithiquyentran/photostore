from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.session import get_session
from models.folders import Folders  

router = APIRouter(tags=["Folders"])

@router.get("/folders")
def get_folders(session: Session = Depends(get_session)):
    try:
        statement = select(Folders)
        results = session.exec(statement).all()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")

@router.post("/folders")
def create_folder(folder: Folders, session: Session = Depends(get_session)):
    try:
        session.add(folder)
        session.commit()
        session.refresh(folder)
        return {"status": "success", "data": folder}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm folder: {e}")

@router.put("/folders/{folder_id}")
def update_project(folder_id: int, project_update: Folders, session: Session = Depends(get_session)):
    folder = session.get(Folders, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    try:
        update_data = project_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(folder, key, value)
        session.add(folder)
        session.commit()
        session.refresh(folder)
        return {"status": "success", "data": folder}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi cập nhật folder: {e}")

@router.delete("/folders/{folder_id}")
def delete_project(folder_id: int, session: Session = Depends(get_session)):
    folder = session.get(Folders, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Project không tồn tại")
    try:
        session.delete(folder)
        session.commit()
        return {"status": "success", "message": "Xóa folder thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa folder: {e}")
