from datetime import datetime
from typing import Optional
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

    access_control: bool = Field(default=True, description="true nếu file public")
    url: str = Field(max_length=255, nullable=False)

    created: datetime = Field(default_factory=datetime.utcnow)
    last_created: datetime = Field(default_factory=datetime.utcnow)

    # Quan hệ với bảng folders (1 folder có nhiều assets)
    folders: Optional["Folders"] = Relationship(back_populates="assets")
