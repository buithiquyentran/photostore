from fastapi import APIRouter

from api.routes import (
    projects, folders, login, users, 
    user_assets, search, static_files,
    external_api
)
# , login, private, users, utils
from core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(projects.router)
api_router.include_router(folders.router)
api_router.include_router(user_assets.router)
api_router.include_router(users.router)
api_router.include_router(search.router)  # Search API
api_router.include_router(static_files.router)  # Static files with access control
api_router.include_router(external_api.router)  # External API with API key authentication



