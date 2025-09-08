from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Embeddings(SQLModel, table=True):
    __tablename__ = "embeddings"
    id: Optional[int] = Field(default=None, primary_key=True)
    asset_id: int = Field(foreign_key="assets.id")
    embedding: str = Field(nullable=False)

    # Quan hệ với User (1 user có nhiều projects)
 
    assets: Optional["Assets"] = Relationship(back_populates="embeddings")
