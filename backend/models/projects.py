from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Projects(SQLModel, table=True):
    __tablename__ = "projects"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(default=None)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    api_key : str = Field(default=None)
    api_secret :str = Field(default=None)
    # Quan hệ với User (1 user có nhiều projects)
    users: Optional["Users"] = Relationship(back_populates="projects")

    # Quan hệ với Folder (1 project có nhiều folders)
    folders: List["Folders"] = Relationship(back_populates="projects")
