"""
Build file paths and URLs from slugs
"""
from sqlmodel import Session, select
from models.folders import Folders
from models.projects import Projects


def build_full_path(session: Session, project_id: int, folder_id: int) -> str:
    """
    Build full path từ project và folder slugs.
    
    Args:
        session: Database session
        project_id: ID của project
        folder_id: ID của folder
        
    Returns:
        Full path dạng: "user_id/project-slug/parent-folder-slug/child-folder-slug"
    """
    # Get project slug
    project = session.get(Projects, project_id)
    if not project:
        return ""
    
    path_parts = [str(project.user_id), project.slug]
    
    # Build folder path
    current_folder = session.get(Folders, folder_id)
    folder_slugs = []
    
    # Traverse up to root folder
    while current_folder:
        folder_slugs.insert(0, current_folder.slug)
        if current_folder.parent_id:
            current_folder = session.get(Folders, current_folder.parent_id)
        else:
            break

    path_parts.extend(folder_slugs)
    return "/".join(path_parts)


def build_file_url(session: Session, project_id: int, folder_id: int, filename: str, base_url: str) -> str:
    """
    Build file URL với full path.
    
    Args:
        session: Database session
        project_id: ID của project
        folder_id: ID của folder
        filename: Tên file
        base_url: Base URL (e.g., http://localhost:8000)
        
    Returns:
        Full URL: "http://localhost:8000/uploads/user_id/project-slug/folder-path/file.jpg"
    """
    full_path = build_full_path(session, project_id, folder_id)
    if not full_path:
        return f"{base_url}/uploads/{filename}"
    
    return f"{base_url}/uploads/{full_path}/{filename}"
