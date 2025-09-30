from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Users(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, nullable=False)
    email: str = Field(max_length=100, nullable=False, unique=True)
    sub: str = Field(max_length=255, nullable=False, unique=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Quan hệ với Project (1 user có nhiều projects)
    projects: List["Projects"] = Relationship(back_populates="users")
    refresh_token: List["RefreshToken"] = Relationship(back_populates="users")
class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_token"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token: str
    expires_at: datetime
    users: Optional["Users"] = Relationship(back_populates="refresh_token")

