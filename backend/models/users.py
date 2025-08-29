from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Users(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, nullable=False)
    email: str = Field(max_length=100, nullable=False, unique=True)
    password_hash: str = Field(max_length=255, nullable=False)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Quan hệ với Project (1 user có nhiều projects)
    projects: List["Projects"] = Relationship(back_populates="users")


