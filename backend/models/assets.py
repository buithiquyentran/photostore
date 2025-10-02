from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship # type: ignore


class Assets(SQLModel, table=True):
    __tablename__ = "assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    folder_id: int = Field(foreign_key="folders.id", nullable=True)
    project_id: int = Field(foreign_key="projects.id", nullable=False)  # Thêm project_id
    
    # File info
    name: str = Field(max_length=255, nullable=False, description="Original filename")
    system_name: str = Field(max_length=100, nullable=False, description="System generated filename (UUID)")
    file_extension: str = Field(max_length=20, nullable=False)
    file_type: str = Field(max_length=100, nullable=False, description="MIME type")
    format: str = Field(max_length=100, nullable=False, description="File format (e.g. image/jpeg)")
    file_size: int = Field(nullable=False, description="File size in bytes")
    
    # Image specific
    width: Optional[int] = Field(nullable=True, description="Image width in pixels")
    height: Optional[int] = Field(nullable=True, description="Image height in pixels")
    
    # Path info
    path: str = Field(max_length=500, nullable=False, description="Relative path using slugs")
    file_url: str = Field(max_length=1000, nullable=False, description="Full URL to access the file")
    folder_path: str = Field(max_length=500, nullable=False, description="Full folder path using slugs")
    
    # Flags
    is_image: bool = Field(default=True, description="True if file is an image")
    is_favorite: bool = Field(default=False, description="True if file is marked as favorite")
    is_deleted: bool = Field(default=False, description="True if file is soft deleted")
    is_private: bool = Field(default=False, description="True if file is private")
    
    # Timestamps as Unix timestamps
    created_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    updated_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))

    # Quan hệ với bảng folders (1 folder có nhiều assets)
    folders: Optional["Folders"] = Relationship(back_populates="assets")
    
    embeddings: List["Embeddings"] = Relationship(back_populates="assets")
