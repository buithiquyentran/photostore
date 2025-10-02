from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import secrets


def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"pk_{secrets.token_urlsafe(32)}"


def generate_api_secret() -> str:
    """Generate a secure random API secret"""
    return f"sk_{secrets.token_urlsafe(48)}"


class Projects(SQLModel, table=True):
    __tablename__ = "projects"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str = Field(max_length=100, nullable=False)
    slug: str = Field(max_length=150, nullable=False, index=True)  # URL-friendly version of name
    description: Optional[str] = Field(default=None)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    api_key: str = Field(default_factory=generate_api_key)  # Auto-generate
    api_secret: str = Field(default_factory=generate_api_secret)  # Auto-generate
    # Quan hệ với User (1 user có nhiều projects)
    users: Optional["Users"] = Relationship(back_populates="projects")

    # Quan hệ với Folder (1 project có nhiều folders)
    folders: List["Folders"] = Relationship(back_populates="projects")
    
    # Quan hệ với Embeddings (1 project có nhiều embeddings)
    embeddings: List["Embeddings"] = Relationship(back_populates="projects")
    