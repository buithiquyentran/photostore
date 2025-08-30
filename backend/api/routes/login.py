from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy import text
from jose import jwt, JWTError
from db.session import get_session
from core.security import create_access_token, decode_access_token, create_refresh_token
from pydantic import BaseModel
from datetime import datetime
from models.users import Users, RefreshToken
from core.config import settings
from core.security import ALGORITHM 
router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
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
    """
    Gọi procedure MySQL để register, nếu thành công thì trả về JWT token
    """
    try:
        # Gọi stored procedure
        result = session.exec(
            text("CALL register(:p_email, :p_password, :p_name)").bindparams(p_email=data.email, p_password=data.password, p_name=data.username)
        )

        user = result.mappings().first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
         # COMMIT transaction để ghi dữ liệu
        session.commit()
        # Tạo JWT
        token = create_access_token({"sub": str(user["id"]), "email": user["email"]})

        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "is_superuser": user["is_superuser"]
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=Users)
def get_me(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = decode_access_token(token)
    print(payload)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    id = payload.get("id")
    user = session.get(Users, id)
    return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_superuser": user.is_superuser
        }
   
@router.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("scope") != "refresh_token":
            raise HTTPException(status_code=401, detail="Invalid scope for token")

        user_data = {"id": payload.get("id"), "email": payload.get("email")}
        new_access_token = create_refresh_token(user_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
