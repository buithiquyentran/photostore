from fastapi import APIRouter, Depends, HTTPException
import secrets
from sqlmodel import Session, select

from db.session import get_session
from models import Projects, Folders

def create_api_client(user_id: int, name: str, session: Session = Depends(get_session)):
    api_key = secrets.token_hex(16)      # random 32 ký tự
    api_secret = secrets.token_hex(32)   # random 64 ký tự

    client = Projects(
        user_id=user_id,
        name=name,
        api_key=api_key,
        api_secret=api_secret
    )
    session.add(client)
    session.commit()
    session.refresh(client)

    # Tạo folder mặc định cho project vừa tạo
    default_folder = Folders(
        name="Default",
        project_id=client.id,
        is_default=True
    )
    session.add(default_folder)
    session.commit()
    session.refresh(default_folder)
    return client
def get_all_clients(session: Session = Depends(get_session)):
    statement = select(Projects)
    results = session.exec(statement).all()
    return {"status": "success", "data": results}

def get_client_by_key(api_key: str, session: Session = Depends(get_session)):
    statement = select(Projects).where(Projects.api_key == api_key)
    client = session.exec(statement).first()
    return client
