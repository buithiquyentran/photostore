
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    PROJECT_NAME: str = "PhotoStore"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "local"           # local | staging | production
    SENTRY_DSN: str | None = None

    # CORS
    all_cors_origins: List[str] = []

    class Config:
        env_file = ".env"

settings = Settings()
