from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship  # type: ignore


class Tags(SQLModel, table=True):
    """
    Bảng lưu trữ các tags.
    """
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False, unique=True, index=True, description="Tag name")
    status: int = Field(default=1, description="1=active, 0=inactive")
    note: Optional[str] = Field(default=None, description="Note about this tag")
    
    # Timestamps as Unix timestamps
    created_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    updated_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    
    # Relationship
    tag_details: List["TagsDetail"] = Relationship(back_populates="tag")


class TagsDetail(SQLModel, table=True):
    """
    Bảng liên kết giữa tags và các đối tượng khác (assets, folders, projects, etc.)
    """
    __tablename__ = "tags_detail"

    id: Optional[int] = Field(default=None, primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", nullable=False)
    source_type: str = Field(max_length=50, nullable=False, description="Type: assets, folders, projects, etc.")
    source_id: int = Field(nullable=False, description="ID of the source object")
    
    # Timestamps as Unix timestamps
    created_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    updated_at: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    
    # Relationship
    tag: Optional["Tags"] = Relationship(back_populates="tag_details")
