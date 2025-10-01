# routers/api_clients.py
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

from db.session import get_session
from models.projects import Projects
from services.api_client.api_client_service import create_api_client , get_all_clients
from dependencies.dependencies import  get_current_user


router = APIRouter(prefix="/admin/clients", tags=["API Clients"])

@router.post("/")
def create_client(name: str | None = Form(None), current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Tạo mới API client (cấp key/secret cho đối tác)
    """
    client = create_api_client( user_id=current_user.id , name=name , session=session)
    return {"status": 1, "data": client}

@router.get("/")
def list_clients(session: Session = Depends(get_session)):
    """
    Xem danh sách các API client
    """
    return get_all_clients(session)
