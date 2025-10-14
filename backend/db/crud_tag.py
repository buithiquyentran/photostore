"""
CRUD Operations for Tags and TagsDetail
"""

from sqlalchemy.orm import Session
from sqlmodel import select
from typing import Optional, List
from datetime import datetime

from models import Tags, TagsDetail, Assets


def get_or_create_tag(session: Session, tag_name: str, note: Optional[str] = None) -> Tags:
    """
    Lấy tag nếu đã tồn tại, nếu chưa thì tạo mới.
    
    Args:
        session: Database session
        tag_name: Tên tag (sẽ được lowercase và trim)
        note: Ghi chú về tag (optional)
    
    Returns:
        Tags object
    """
    # Normalize tag name (lowercase, trim whitespace)
    normalized_name = tag_name.strip().lower()
    
    # Tìm tag đã tồn tại
    existing_tag = session.exec(
        select(Tags).where(Tags.name == normalized_name)
    ).first()
    
    if existing_tag:
        return existing_tag
    
    # Tạo tag mới
    new_tag = Tags(
        name=normalized_name,
        status=1,
        note=note
    )
    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)
    
    return new_tag


def add_tag_to_asset(
    session: Session,
    tag_id: int,
    asset_id: int
) -> TagsDetail:
    """
    Liên kết tag với asset.
    Nếu đã tồn tại thì không tạo duplicate.
    
    Args:
        session: Database session
        tag_id: ID của tag
        asset_id: ID của asset
    
    Returns:
        TagsDetail object
    """
    # Kiểm tra xem đã tồn tại chưa
    existing = session.exec(
        select(TagsDetail)
        .where(TagsDetail.tag_id == tag_id)
        .where(TagsDetail.source_type == "assets")
        .where(TagsDetail.source_id == asset_id)
    ).first()
    
    if existing:
        return existing
    
    # Tạo mới
    tag_detail = TagsDetail(
        tag_id=tag_id,
        source_type="assets",
        source_id=asset_id
    )
    session.add(tag_detail)
    session.commit()
    session.refresh(tag_detail)
    
    return tag_detail


def get_tags_for_asset(session: Session, asset_id: int) -> List[Tags]:
    """
    Lấy tất cả tags của một asset.
    
    Args:
        session: Database session
        asset_id: ID của asset
    
    Returns:
        List of Tags objects
    """
    tag_details = session.exec(
        select(TagsDetail)
        .where(TagsDetail.source_type == "assets")
        .where(TagsDetail.source_id == asset_id)
    ).all()
    
    tag_ids = [td.tag_id for td in tag_details]
    
    if not tag_ids:
        return []
    
    tags = session.exec(
        select(Tags).where(Tags.id.in_(tag_ids))
    ).all()
    
    return list(tags)


def remove_tag_from_asset(session: Session, tag_id: int, asset_id: int) -> bool:
    """
    Xóa liên kết giữa tag và asset.
    
    Args:
        session: Database session
        tag_id: ID của tag
        asset_id: ID của asset
    
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    tag_detail = session.exec(
        select(TagsDetail)
        .where(TagsDetail.tag_id == tag_id)
        .where(TagsDetail.source_type == "assets")
        .where(TagsDetail.source_id == asset_id)
    ).first()
    
    if not tag_detail:
        return False
    
    session.delete(tag_detail)
    session.commit()
    
    return True


def search_assets_by_tags(
    session: Session,
    tag_names: List[str],
    project_id: Optional[int] = None,
    folder_id: Optional[int] = None,
    match_all: bool = False
) -> List[Assets]:
    """
    Tìm kiếm assets theo tags.
    
    Args:
        session: Database session
        tag_names: List tên tags cần tìm
        project_id: Filter theo project (optional)
        folder_id: Filter theo folder (optional)
        match_all: True = phải match tất cả tags, False = match bất kỳ tag nào
    
    Returns:
        List of Assets objects
    """
    if not tag_names:
        return []
    
    # Normalize tag names
    normalized_names = [name.strip().lower() for name in tag_names]
    
    # Lấy tag IDs
    tags = session.exec(
        select(Tags).where(Tags.name.in_(normalized_names))
    ).all()
    
    if not tags:
        return []
    
    tag_ids = [tag.id for tag in tags]
    
    # Lấy asset IDs từ tags_detail
    tag_details = session.exec(
        select(TagsDetail)
        .where(TagsDetail.tag_id.in_(tag_ids))
        .where(TagsDetail.source_type == "assets")
    ).all()
    
    if not tag_details:
        return []
    
    # Group asset_ids by tag_id để check match_all
    asset_tag_map = {}  # {asset_id: set of tag_ids}
    for td in tag_details:
        if td.source_id not in asset_tag_map:
            asset_tag_map[td.source_id] = set()
        asset_tag_map[td.source_id].add(td.tag_id)
    
    # Filter based on match_all
    if match_all:
        # Phải có tất cả tags
        asset_ids = [
            asset_id for asset_id, found_tags in asset_tag_map.items()
            if found_tags.issuperset(set(tag_ids))
        ]
    else:
        # Có ít nhất 1 tag
        asset_ids = list(asset_tag_map.keys())
    
    if not asset_ids:
        return []
    
    # Query assets
    query = select(Assets).where(Assets.id.in_(asset_ids))
    
    if project_id:
        query = query.where(Assets.project_id == project_id)
    
    if folder_id:
        query = query.where(Assets.folder_id == folder_id)
    
    assets = session.exec(query).all()
    
    return list(assets)


def get_all_tags(session: Session, active_only: bool = True) -> List[Tags]:
    """
    Lấy tất cả tags.
    
    Args:
        session: Database session
        active_only: Chỉ lấy tags có status = 1
    
    Returns:
        List of Tags objects
    """
    query = select(Tags)
    
    if active_only:
        query = query.where(Tags.status == 1)
    
    tags = session.exec(query).all()
    
    return list(tags)


def update_tag(
    session: Session,
    tag_id: int,
    name: Optional[str] = None,
    status: Optional[int] = None,
    note: Optional[str] = None
) -> Optional[Tags]:
    """
    Cập nhật thông tin tag.
    
    Args:
        session: Database session
        tag_id: ID của tag
        name: Tên mới (optional)
        status: Status mới (optional)
        note: Note mới (optional)
    
    Returns:
        Updated Tags object hoặc None nếu không tìm thấy
    """
    tag = session.exec(select(Tags).where(Tags.id == tag_id)).first()
    
    if not tag:
        return None
    
    if name is not None:
        tag.name = name.strip().lower()
    
    if status is not None:
        tag.status = status
    
    if note is not None:
        tag.note = note
    
    tag.updated_at = int(datetime.utcnow().timestamp())
    
    session.add(tag)
    session.commit()
    session.refresh(tag)
    
    return tag


def delete_tag(session: Session, tag_id: int) -> bool:
    """
    Xóa tag và tất cả liên kết của nó.
    
    Args:
        session: Database session
        tag_id: ID của tag
    
    Returns:
        True nếu xóa thành công, False nếu không tìm thấy
    """
    tag = session.exec(select(Tags).where(Tags.id == tag_id)).first()
    
    if not tag:
        return False
    
    # Xóa tất cả tag_details liên quan
    tag_details = session.exec(
        select(TagsDetail).where(TagsDetail.tag_id == tag_id)
    ).all()
    
    for td in tag_details:
        session.delete(td)
    
    # Xóa tag
    session.delete(tag)
    session.commit()
    
    return True

