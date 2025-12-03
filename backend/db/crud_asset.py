# from sqlmodel import Session
from unittest import case
from fastapi import Depends ,HTTPException
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.sql import literal
from pydantic import BaseModel
import os

from models import Assets, Projects,Tags, TagsDetail, Users, Folders
from utils.folder_finder import find_folder_by_path

from dependencies.dependencies import get_current_user
from db.session import get_session

from typing import List, Optional

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

class AssetUpdate(BaseModel):
    is_private: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_deleted: Optional[bool] = None

def update (
    session: Session,
    asset_id: int,
    update : AssetUpdate
):
    """
    Cập nhật thông tin của asset.

    Args:
        session: Database session
        asset_id: ID của asset cần cập nhật
        kwargs: Các trường cần cập nhật và giá trị mới

    Returns:
        Assets: Đối tượng asset đã được cập nhật
    """
    asset = session.get(Assets, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if update.is_private is not None:
        asset.is_private = update.is_private 
    if update.is_favorite is not None:
        asset.is_favorite = update.is_favorite
        
    if update.is_deleted is not None:
        asset.is_deleted = update.is_deleted
        
    if update.is_deleted is True:
        # Nếu đánh dấu xóa, bỏ đánh dấu yêu thích
        asset.is_favorite = False
    if update.is_private is not None or update.is_favorite is not None or update.is_deleted is not None:
        asset.updated_at = int(datetime.utcnow().timestamp())
    session.add(asset)
    session.commit()
    session.refresh(asset)

    return asset

def delete(session: Session, asset: any, user_id: int, permanently: bool = False):
    """Xóa asset khỏi database"""
    try:
        if permanently:
            # Xóa vĩnh viễn - xóa file và record
            if asset.path:
                file_path = os.path.join("uploads", str(user_id), asset.path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"[INFO] Deleted file: {file_path}")
            
            session.delete(asset)
            session.commit()
            print(f"[INFO] Permanently deleted asset ID: {asset.id}")
        else:
            # Xóa mềm - chỉ đánh dấu is_deleted
            asset.is_deleted = True
            asset.is_favorite = False  # Bỏ yêu thích khi xóa
            asset.updated_at = int(datetime.utcnow().timestamp())
            session.add(asset)
            session.commit()
            session.refresh(asset)
            print(f"[INFO] Soft deleted asset ID: {asset.id}")
            
    except Exception as file_err:
        session.rollback()
        print(f"[ERROR] Không thể xóa asset: {file_err}")
        raise
    
def sort_type ( 
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),  
       
    keyword: Optional[str] = None,
    match_type: Optional[str] = "start-with",  # "start-with" hoặc "equal-to"
    
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    file_extension: Optional[str] = None,
    is_favorite : Optional[bool] = None,
    is_deleted: Optional[bool] = None,
    is_private: Optional[bool] = None,
    is_image: Optional[bool] = None,
    shape: Optional[str] = None,  # "landscape", "portrait", "square"
    tag: Optional[str] = None,
    folder_path: Optional[str] = None,
    ):
    statement = (
            select(Assets)
            .join(Projects, Assets.project_id == Projects.id)
            .where(Projects.user_id == current_user.id)
        )
    child_folders = []
    if folder_path:
        parts = folder_path.split("/")
        project_slug = parts[0]
        folder_path = "/".join(parts[1:])
        # Tìm project theo slug
        project = session.exec(
            select(Projects)
            .join(Users, Users.id == Projects.user_id)
            .where((Users.id == current_user.id) & (Projects.slug == project_slug))
        ).first()

        if not project:
            raise HTTPException(404, "Project not found")
        
        # Lấy các folder con
        if folder_path:
            # Tìm folder theo đường dẫn (dùng hàm helper)
            folder = find_folder_by_path(session, project.id, folder_path)
            if not folder:
                raise HTTPException(404, "Folder not found")
            # Lấy assets trong folder đó
            statement =statement.where(Assets.folder_id == folder.id)
            # Lấy folder con trong folder đó
            child_folders = session.exec(
            select(Folders)
            .where((Folders.parent_id == folder.id) & (Folders.project_id == project.id))).all()
            
        else :
            # Lấy tất cả folder con ở cấp cao nhất của project
            child_folders = session.exec(select(Folders).where ((project.id == Folders.project_id) & (Folders.parent_id == None)))
            child_folders = [f.model_dump() for f in child_folders]
            print("Project_id:", project.id) #9
            print("Child folders:", child_folders)
            #  Assets bây giờ rỗng
            statement = select(Assets).where(literal(False))

        

    if is_favorite is not None:
        statement = statement.where(Assets.is_favorite == is_favorite)
    if is_deleted is not None:
        statement = statement.where(Assets.is_deleted == is_deleted)
    if is_private is not None:
        statement = statement.where(Assets.is_private == is_private)
    if is_image is not None:
        statement = statement.where(Assets.is_image == is_image)
    if file_extension:
        # Ensure the extension doesn't have a leading dot
        clean_extension = file_extension.lstrip('.')
        statement = statement.where(Assets.file_extension.ilike(f"%{clean_extension}%"))
    if keyword:
        if match_type == "start-with":
            statement = statement.where(Assets.name.ilike(f"{keyword}%"))
        elif match_type == "equal-to":
            statement = statement.where(Assets.name.ilike(f"{keyword}"))
    if start_date:
        start_timestamp = int(start_date.timestamp())
        statement = statement.where(Assets.created_at >= start_timestamp)
    if end_date:
        end_timestamp = int(end_date.timestamp())
        statement = statement.where(Assets.created_at <= end_timestamp)
    if shape:
        if shape == "landscape":
            statement = statement.where(Assets.width > Assets.height)
        elif shape == "portrait":
            statement = statement.where(Assets.height > Assets.width)
        elif shape == "square":
            statement = statement.where(
                (Assets.width >= Assets.height * 0.95) &
                (Assets.width <= Assets.height * 1.05)
            )
    if tag:
        statement = (
            statement
            .join(TagsDetail, TagsDetail.source_id == Assets.id)
            .join(Tags, Tags.id == TagsDetail.tag_id)
            .where(
                TagsDetail.source_type == "assets",
                Tags.name.ilike(f"%{tag}%")
            )
        )
    assets= session.exec(statement).all()
    asset_ids_list = [asset.id for asset in assets]
    return asset_ids_list, child_folders

def display_order(
    session: Session, 
    asset_ids_list: Optional[List[int]] = None,
    sort_by: Optional[str] = "date",     #  "date", "name", "size"
    sort_order: Optional[str] = "desc",  # "asc" hoặc "desc"
    skip: int = 0, 
    limit: int = 100
):
    query = session.query(Assets)

    # Lọc theo danh sách ID đã có (nếu có)
    if asset_ids_list:
        query = query.filter(Assets.id.in_(asset_ids_list))

    if sort_by == "date":
        query = query.order_by(
            Assets.created_at.asc() if sort_order == "asc" else Assets.created_at.desc()
        )
    elif sort_by == "name":
        query = query.order_by(
            Assets.name.asc() if sort_order == "asc" else Assets.name.desc()
        )
    elif sort_by == "size":
        query = query.order_by(
            Assets.file_size.asc() if sort_order == "asc" else Assets.file_size.desc()
        )
    else:
        # Mặc định: sort theo ngày mới nhất
        query = query.order_by(Assets.created_at.desc())

    total = query.count()
    files = query.offset(skip).limit(limit).all()

    return {"total": total, "files": files}