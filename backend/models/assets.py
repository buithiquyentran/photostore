from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship # type: ignore


class Assets(SQLModel, table=True):
    __tablename__ = "assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    folder_id: int = Field(foreign_key="folders.id", nullable=True)
    name: str = Field(max_length=100, nullable=False)
    is_image: Optional[bool] = Field(default=True)
    format: Optional[str] = Field(max_length=100, nullable=True)
    width: int = Field(nullable=False)
    height: int = Field(nullable=False)
    file_size: int = Field(nullable=False, description="Kích thước file (byte)")
    is_favorite: bool = Field(default=False, description="true nếu file được đánh dấu yêu thích")
    is_deleted: bool = Field(default=False, description="true nếu file đã bị xóa")
    is_private: bool = Field(default=False, description="false nếu file public")
    path: str = Field(max_length=255, nullable=False)

    created: datetime = Field(default_factory=datetime.utcnow)
    last_created: datetime = Field(default_factory=datetime.utcnow)

    # Quan hệ với bảng folders (1 folder có nhiều assets)
    folders: Optional["Folders"] = Relationship(back_populates="assets")
    
    embeddings: List["Embeddings"] = Relationship(back_populates="assets")
