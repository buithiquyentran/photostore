from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.session import get_session
from models.assets import Assets  # model Asset đã tạo ở models/asset.py

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/images")
def get_images(session: Session = Depends(get_session)):
    """
    Lấy danh sách các hình ảnh từ bảng assets
    """
    try:
        statement = select(Assets).where(Assets.is_image == True)
        results = session.exec(statement).all()
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
