from fastapi import APIRouter

from api.routes import assets,projects,login
# , login, private, users, utils
from core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
# api_router.include_router(users.router)
# api_router.include_router(utils.router)
api_router.include_router(assets.router)
api_router.include_router(projects.router)

