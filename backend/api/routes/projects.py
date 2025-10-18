from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from db.session import get_session
from models.projects import Projects, generate_api_key, generate_api_secret
from dependencies.dependencies import get_current_user
from utils.slug import create_slug

router = APIRouter(tags=["Projects"])

class APIKeyResponse(BaseModel):
    api_key: str
    api_secret: str

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False

@router.get("/projects")
def get_projects(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Lấy danh sách projects của user"""
    try:
        projects = session.exec(
            select(Projects)
            .where((Projects.user_id == current_user.id))
        ).all()
        return {"status": "success", "data": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")

@router.post("/projects")
def create_project(
    project_data: ProjectCreateRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Tạo project mới"""
    try:
        project_slug = create_slug(project_data.name)
        
        # Kiểm tra trùng slug
        existing = session.exec(
            select(Projects)
            .where(
                Projects.user_id == current_user.id,
                Projects.slug == project_slug
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Project with this name already exists"
            )
        
        new_project = Projects(
            user_id=current_user.id,
            name=project_data.name,
            slug=project_slug,
            description=project_data.description,
            is_default=project_data.is_default,
            api_key=generate_api_key(),
            api_secret=generate_api_secret()
        )
        session.add(new_project)
        session.commit()
        session.refresh(new_project)
        return {"status": "success", "data": new_project}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm project: {e}")

@router.get("/projects/{project_id}/api-key", response_model=APIKeyResponse)
def get_project_api_key(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Lấy API key và secret key của project"""
    try:
        project = session.get(Projects, project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": "Project not found"
                }
            )
            
        if project.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "status": "error",
                    "message": "You don't have permission to access this project"
                }
            )
            
        return APIKeyResponse(
            api_key=project.api_key,
            api_secret=project.api_secret
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )

@router.post("/projects/{project_id}/regenerate-api-key", response_model=APIKeyResponse)
def regenerate_project_api_key(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Tạo lại API key và secret key mới cho project"""
    try:
        project = session.get(Projects, project_id)
        if not project:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": "Project not found"
                }
            )
            
        if project.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "status": "error",
                    "message": "You don't have permission to access this project"
                }
            )
            
        # Tạo key mới
        project.api_key = generate_api_key()
        project.api_secret = generate_api_secret()
        
        session.add(project)
        session.commit()
        session.refresh(project)
            
        return APIKeyResponse(
            api_key=project.api_key,
            api_secret=project.api_secret
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error"
            }
        )
