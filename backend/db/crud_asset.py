# from sqlmodel import Session
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime

from models import Assets
from db.session import get_session

def add_asset(
    session: Session,
    project_id: int,
    folder_id: int,
    name: str,
    system_name: str,
    file_extension: str,
    file_type: str,
    format: str,
    file_size: int,
    path: str,
    file_url: str,
    folder_path: str,
    width: int = None,
    height: int = None,
    is_private: bool = False,
    is_image: bool = True
):
    """
    Thêm asset mới vào database.

    Args:
        session: Database session
        project_id: ID của project
        folder_id: ID của folder
        name: Original filename
        file_extension: File extension (e.g., "jpg", "png")
        file_type: MIME type (e.g., "image/jpeg")
        file_size: File size in bytes
        path: Relative path using slugs
        file_url: Full URL to access the file
        folder_path: Full folder path using slugs
        width: Image width in pixels (optional)
        height: Image height in pixels (optional)
        is_private: True if file is private
        is_image: True if file is an image

    Returns:
        int: ID of the created asset
    """
    asset = Assets(
        project_id=project_id,
        folder_id=folder_id,
        name=name,
        system_name=system_name,
        file_extension=file_extension,
        file_type=file_type,
        format=format,
        file_size=file_size,
        path=path,
        file_url=file_url,
        folder_path=folder_path,
        width=width,
        height=height,
        is_image=is_image,
        is_private=is_private,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset.id
