from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Text


class Embeddings(SQLModel, table=True):
    __tablename__ = "embeddings"
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="assets.id")
    project_id: int = Field(foreign_key="projects.id", index=True)  # Thêm project_id để tìm kiếm nhanh
    folder_id: Optional[int] = Field(default=None, foreign_key="folders.id", index=True)  # Thêm folder_id để filter
    embedding: str = Field(sa_type=Text, nullable=False)  # TEXT type để chứa vector lớn (512 floats ~11KB)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    assets: Optional["Assets"] = Relationship(back_populates="embeddings")
    projects: Optional["Projects"] = Relationship(back_populates="embeddings")
    folders: Optional["Folders"] = Relationship(back_populates="embeddings")
