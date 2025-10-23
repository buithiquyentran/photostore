from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Thumbnails(SQLModel, table=True):
    __tablename__ = "thumbnails"

    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="assets.id", nullable=False)

    # Size parameters
    width: int
    height: int
    quality: int = Field(default=80)
    format: str = Field(default="webp", max_length=10)

    # Generated file info
    file_url: str = Field(max_length=512)
    file_size: Optional[float] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = Field(default=0)

    # Relationship
    assets: Optional["Assets"] = Relationship(back_populates="thumbnails")

