from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.session import get_session
from models import  Projects, Folders, Assets # model Asset đã tạo ở models/asset.py

router = APIRouter( tags=["Assets"])

@router.get("/assets")
def get_assets(session: Session = Depends(get_session)):
    
    try:
        statement = select(Assets)
        results = session.exec(statement).all()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
    
@router.get("/images")
def get_images(session: Session = Depends(get_session)):
    
    try:
        statement = select(Assets).where(Assets.is_image == True)
        results = session.exec(statement).all()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")

@router.get("/videos")
def get_videos(session: Session = Depends(get_session)):
   
    try:
        statement = select(Assets).where(Assets.is_image == False)
        results = session.exec(statement).all()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
   
@router.get("/get_user_assets/{user_id}") 
def get_user_assets(user_id: int, session: Session = Depends(get_session)):
    """
    Lấy tất cả assets của user dùng ORM
    """
    try:
        statement = (
            select(Assets).where(Assets.access_control == True)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == user_id)
        )
        results = session.exec(statement).all()
        return {"status": "success", "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn ORM: {str(e)}")