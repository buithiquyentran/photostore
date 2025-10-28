from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


class Folders(SQLModel, table=True):
    __tablename__ = "folders"
    __table_args__ = (
        UniqueConstraint("project_id", "parent_id", "name", name="uq_project_parent_name"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    parent_id: Optional[int] = Field(default=None, foreign_key="folders.id")

    name: str = Field(max_length=100, nullable=False)
    slug: str = Field(max_length=150, nullable=False, index=True)  # URL-friendly version of name
    path: str = Field(max_length=500, nullable=False, description="Relative path using slugs")

    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_default: bool = Field(default=False)

    # Quan hệ với Project (1 project có nhiều folders)
    projects: Optional["Projects"] = Relationship(back_populates="folders")

    # Quan hệ đệ quy (folder cha và folder con)
    parent: Optional["Folders"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Folders.id"}
    )
    children: List["Folders"] = Relationship(back_populates="parent")

    # Quan hệ với Asset (1 folder có nhiều assets)
    assets: List["Assets"] = Relationship(back_populates="folders")
    
    # Quan hệ với Embeddings (1 folder có nhiều embeddings)
    embeddings: List["Embeddings"] = Relationship(back_populates="folders")