from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import List, Union
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Project
    PROJECT_NAME: str = "PhotoStore"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"
    
    # Security
    SECRET_KEY: str = "supersecretkey"
    REFR_SECRET_KEY: str = "supersecretkeyrefresh"
    
    # CORS - Đọc từ CORS_ORIGINS và parse thành list
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Keycloak
    KEYCLOAK_URL: str
    CLIENT_ID: str
    ADMIN_CLIENT_ID: str
    ADMIN_CLIENT_SECRET: str
    
    @property
    def all_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS string to list"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',') if origin.strip()]
        return []
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }

settings = Settings()
