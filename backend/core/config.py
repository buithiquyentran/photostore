from pydantic_settings import BaseSettings
from typing import List
class Settings(BaseSettings):
    DATABASE_URL: str
    PROJECT_NAME: str = "PhotoStore"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"          
    SECRET_KEY: str  = "supersecretkey"
    REFR_SECRET_KEY : str = "supersecretkeyrefresh"
    all_cors_origins: List[str] = ["http://localhost:5173","http://localhost:5174"]
    KEYCLOAK_URL: str 
    CLIENT_ID: str 
    ADMIN_CLIENT_ID: str 
    ADMIN_CLIENT_SECRET: str 
    class Config:   
        env_file = ".env"

settings = Settings()
