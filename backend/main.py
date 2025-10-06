from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from api.main import api_router
from core.config import settings
from dependencies.auth_middleware import AuthMiddleware
from dependencies.api_key_middleware import verify_api_request
from dependencies.static_middleware import verify_static_access

from db.session import engine

# Import models để SQLModel biết
from models.users import Users, RefreshToken
from models.projects import Projects
from models.folders import Folders
from models.assets import Assets
from models.embeddings import Embeddings

def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins= ["*"] ,#settings.all_cors_origins, # "http://localhost:3000,http://localhost:5173"
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
required_roles = {
    "/api/v1/admin/*": ["admin"],             # chỉ role admin mới được vào
    "/api/v1/users/*": ["user", "admin"],     # user hoặc admin đều được
}

app.add_middleware(AuthMiddleware, required_roles=required_roles)
app.middleware("http")(verify_static_access)

# Add API key middleware
app.middleware("http")(verify_api_request)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Database connected successfully!"}

# Add static files middleware

@app.on_event("startup")
def startup_event():
    """Initialize database tables and uploads directory on startup"""
    print("🚀 Starting up PhotoStore...")
    
    # Create all tables if not exist
    SQLModel.metadata.create_all(engine)
    print("✅ Database tables initialized")
    
    # Create uploads directory if not exists
    from pathlib import Path
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    print(f"✅ Uploads directory initialized at {uploads_dir.absolute()}")
    
    # TODO: Load FAISS indices for active projects
    # from db.session import get_session
    # from services.search.embeddings_service import rebuild_project_embeddings
    # with next(get_session()) as session:
    #     # Rebuild indices for active projects
    #     pass
