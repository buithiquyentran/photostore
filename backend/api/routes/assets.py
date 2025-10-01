from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,Request,BackgroundTasks
from sqlmodel import Session, select, func
from fastapi import UploadFile, File, Form
from typing import List
from PIL import Image
import io, os
from uuid import uuid4
from datetime import datetime, timedelta
import io, faiss, json
import torch
import clip
import numpy as np
from pathlib import Path
from typing import Optional
from fastapi.responses import JSONResponse, FileResponse
from db.session import get_session
from models import  Projects, Folders, Assets , Users, Embeddings
from dependencies.dependencies import get_optional_user
from dependencies.external_auth import verify_external_request

from db.crud_asset import add_asset
# from db.crud_embedding import add_embedding
# from db.crud_embedding import embed_image
from db.crud_folder import get_or_create_folder

# from services.embeddings_service import index, faiss_id_to_asset, embed_image, rebuild_faiss,add_embedding_to_faiss, ensure_user_index,search_user
# from services.search.embeddings_service import  embed_image,add_embedding_to_faiss, search_user,ensure_user_index, get_text_embedding, search_by_embedding

router = APIRouter(prefix="/assets",  tags=["Assets"])
BUCKET_NAME = "photostore"
BUCKET_NAME_PUBLIC = "images" 
UPLOAD_DIR = Path("uploads")

@router.get("/{name}")
def get_asset(name: str, session: Session = Depends(get_session), current_user: dict = Depends(get_optional_user)):
    asset = session.exec(select(Assets).where(Assets.name == name)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    user  = session.exec(select(Users)
            .join(Projects, Users.id == Projects.user_id)
            .join(Folders, Projects.id == Folders.project_id)
            .join(Assets, Folders.id == Assets.folder_id)
            .where(Assets.id == asset.id)
        ).first()
    if not user:
        raise HTTPException(404, "Owner not found")
    # fix path separator
    safe_path = asset.path.replace("\\", "/")
    file_path = (UPLOAD_DIR / safe_path).resolve()
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    # Check quyền
    if asset.is_private:
        if current_user is None:
            raise HTTPException(401, "Unauthorized")
        try:
            current_user_id = int(current_user.id)   # 👈 convert sang int
        except ValueError:
            raise HTTPException(401, "Invalid user id in token")

        if current_user_id != user.id:
            raise HTTPException(401, "Unauthorized")

    return FileResponse(file_path)

@router.post("/{name}")
def get_asset(name: str, session: Session = Depends(get_session), client=Depends(verify_external_request)):
    asset = session.exec(select(Assets).where(Assets.name == name)).first()
    if not asset:
        raise HTTPException(404, "Asset not found")
    project = session.exec(select(Projects)
            .join(Folders, Projects.id == Folders.project_id)
            .join(Assets, Folders.id == Assets.folder_id)
            .where(Assets.id == asset.id)
        ).first()
    if not project:
        raise HTTPException(404, "Owner not found")
    # fix path separator
    safe_path = asset.path.replace("\\", "/")
    file_path = (UPLOAD_DIR / safe_path).resolve()
    if not file_path.exists():
        raise HTTPException(404, "File not found")
    # Check quyền
    if asset.is_private:
        if client is None:
            raise HTTPException(401, "Unauthorized")
        try:
            current_client_id = int(client.id)   # 👈 convert sang int
        except ValueError:
            raise HTTPException(401, "Invalid user id in token")

        if current_client_id != project.id:
            raise HTTPException(401, "Unauthorized")

    return FileResponse(file_path)

