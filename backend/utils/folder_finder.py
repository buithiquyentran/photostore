"""
Find folders by path slugs
"""
from sqlmodel import Session, select
from models.folders import Folders
from fastapi import HTTPException


def find_folder_by_path(session: Session, project_id: int, path_slugs: str) -> Folders:
    """
    Tìm folder theo path slugs.
    
    Args:
        session: Database session
        project_id: ID của project
        path_slugs: Path slugs (e.g. "parent-slug/child-slug")
        
    Returns:
        Folders object
        
    Raises:
        HTTPException nếu không tìm thấy folder
    """
    # Split path thành các slugs
    slugs = [s for s in path_slugs.split("/") if s]
    if not slugs:
        raise HTTPException(400, "Folder path không hợp lệ")
    
    current_folder = None
    parent_id = None
    
    # Traverse path từng cấp một
    for slug in slugs:
        folder = session.exec(
            select(Folders)
            .where(Folders.project_id == project_id)
            .where(Folders.parent_id == parent_id)  # None cho root folders
            .where(Folders.slug == slug)
        ).first()
        
        if not folder:
            # Nếu là slug cuối cùng, báo lỗi
            if slug == slugs[-1]:
                raise HTTPException(
                    404, 
                    f"Không tìm thấy folder với slug '{slug}' trong path '{path_slugs}'"
                )
            # Nếu là slug trung gian, báo lỗi chi tiết hơn
            raise HTTPException(
                404,
                f"Không tìm thấy folder cha '{slug}' trong path '{path_slugs}'"
            )
        
        current_folder = folder
        parent_id = folder.id
    
    return current_folder
