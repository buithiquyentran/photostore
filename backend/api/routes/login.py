from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy import text
from jose import jwt, JWTError
from PIL import Image
import io, os
from db.session import get_session
from core.security import create_access_token, decode_access_token, create_refresh_token, decode_refresh_token
from pydantic import BaseModel
from datetime import datetime
from models.users import Users, RefreshToken
from core.config import settings
from core.security import ALGORITHM 
router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
from core.security import get_current_user
from db.crud_embedding import add_embedding
import requests
from db.crud_asset import add_asset

SUPABASE_URL = settings.SUPABASE_URL
BUCKET_NAME_PUBLIC = "images" 

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    status: int = 0
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    username: str
    is_superuser: bool

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str
class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    try:
        result = session.exec(
            text("CALL login(:p_email, :p_password)").bindparams(
                p_email=data.email, p_password=data.password
            )
        )
        user = result.mappings().first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        payload = {"id": str(user["id"]), "email": user["email"]}

        # Tạo access và refresh token
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(session, payload)

        return {
            "status": 1,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "is_superuser": user["is_superuser"]
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    try:
        # Gọi procedure MySQL
        result = session.execute(
            text("CALL register(:p_email, :p_password, :p_name)")
            .bindparams(p_email=data.email, p_password=data.password, p_name=data.username)
        )
        print(result)
        user = result.mappings().first()
        if not user:
            raise HTTPException(status_code=401, detail="Register failed")

        user_id = user["user_id"]
        folder_id = user["folder_id"]

        # Các file mặc định trong bucket public
        default_assets = [
            "uploads/0.jpg",
            "uploads/1.jpg",
            "uploads/2.jpg",
            "uploads/3.jpg",
            "uploads/4.jpg",
            "uploads/5.jpg",
            "uploads/6.jpg",
            "uploads/7.jpg",
            "uploads/8.jpg",
            "uploads/9.jpg",
            "uploads/10.jpg",
            "uploads/11.jpg",
            "uploads/12.jpg",
            "uploads/13.jpg",
            "uploads/14.jpg",
            "uploads/15.jpg",
            "uploads/16.jpg",
            "uploads/17.jpg",
            "uploads/18.jpg",
            "uploads/19.jpg",
        ]

        for path in default_assets:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME_PUBLIC}/{path}"
            resp = requests.get(public_url)
            file_bytes = resp.content
            size = len(file_bytes)
            content_type = resp.headers.get("Content-Type")
             # lấy dimension nếu là ảnh
            width = height = None
            if content_type.startswith("image/"):
                try:
                    with Image.open(io.BytesIO(file_bytes)) as im:
                        width, height = im.size
                except Exception:
                    raise HTTPException(400, f"Ảnh {file_bytes.filename} không hợp lệ")
            asset_id = add_asset(
                session=session,
                user_id=user_id,
                folder_id=folder_id,
                url=public_url,
                name=path,
                format=content_type,
                width=width, height=height,
                file_size=size,
            )
            # thêm embedding 
            add_embedding(session=session, asset_id=asset_id, file_bytes=file_bytes)

        session.commit()

        # Tạo JWT
        payload = {"id": str(user_id), "email": user["email"]}
        access_token = create_access_token({"sub": str(user_id), "email": user["email"]})
        refresh_token = create_refresh_token(session, payload)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": user["email"],
            "username": user["username"],
            "is_superuser": user["is_superuser"],
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/me", response_model=Users)
def get_me(id=Depends(get_current_user), session: Session = Depends(get_session)):
    user = session.get(Users, id)
    return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_superuser": user.is_superuser
        }
   
@router.post("/refresh")
def refresh_token(data: RefreshRequest, session: Session = Depends(get_session)):
    try:
        payload = decode_refresh_token(data.refresh_token)
        print(payload)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid scope for token")

        user_data = {"id": payload.get("id"), "email": payload.get("email")}
        new_access_token = create_access_token(user_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
