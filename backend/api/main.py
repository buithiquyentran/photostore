from fastapi import APIRouter

from api.routes import (
    assets, projects, folders, login, users, api_clients,
    external_assets, user_assets, search, static_files,
    external_api, tags
)
# , login, private, users, utils
from core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(projects.router)
api_router.include_router(folders.router)
api_router.include_router(assets.router)
api_router.include_router(user_assets.router)
api_router.include_router(users.router)
api_router.include_router(api_clients.router)
api_router.include_router(external_assets.router)
api_router.include_router(search.router)  # Search API
api_router.include_router(tags.router)  # Tags API
api_router.include_router(static_files.router)  # Static files with access control

# External API router (không qua api_router để có URL /api/external thay vì /api/v1/external)
external_api_router = external_api.router



