# from sqlmodel import Session
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime

from models import Assets
from db.session import get_session

def add_asset(
    session: Session,
    user_id: int,
    name: str,
    format: str,
    url: str,
    width: int = None,
    height: int = None,
    file_size: int = None,
    folder_id: int = None,
    is_private: bool = False,
    is_image: bool = True
):
    asset = Assets(
        user_id=user_id,
        folder_id=folder_id,
        name=name,
        format=format,
        url=url,
        width=width,
        height=height,
        file_size=file_size,
        is_image=is_image,
        is_private=is_private,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset.id
