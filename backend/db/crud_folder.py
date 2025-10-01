from sqlmodel import Session, select
from models import Folders
def get_or_create_folder(session: Session, project_id: int, path: str) -> Folders:
    parts = [p.strip() for p in path.split("/") if p.strip()]
    parent_id = None
    folder = None

    for name in parts:
        folder = session.exec(
            select(Folders).where(
                Folders.project_id == project_id,
                Folders.parent_id == parent_id,
                Folders.name == name
            )
        ).first()

        if not folder:
            folder = Folders(
                project_id=project_id,
                parent_id=parent_id,
                name=name,
                is_default=False
            )
            session.add(folder)
            session.commit()
            session.refresh(folder)

        parent_id = folder.id

    return folder


def get_folder(session: Session, project_id: int, path: str) -> Folders:
    parts = [p.strip() for p in path.split("/") if p.strip()]
    folder = None
    parent_id = None

    for name in parts:
        folder = session.exec(
            select(Folders).where(
                Folders.project_id == project_id,
                Folders.parent_id == parent_id,
                Folders.name == name
            )
        ).first()

        if not folder:
            return None

        parent_id = folder.id

    return folder
