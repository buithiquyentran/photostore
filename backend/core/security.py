import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select
from uuid import uuid4
from models.users import Users, RefreshToken
# Import settings containing SECRET_KEY
from core.config import settings  # Ensure this path matches your project structure

# Cấu hình
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode.update({"type": "access"})  # Thêm type
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(session: Session, data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    to_encode.update({"type": "refresh"})  # Thêm type
    expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expires})

    token = jwt.encode(to_encode, settings.REFR_SECRET_KEY, algorithm=ALGORITHM)

    refresh = RefreshToken(
        user_id=data["id"],
        token=token,
        expires_at=expires
    )
    session.add(refresh)
    session.commit()
    session.refresh(refresh)
    return token

def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, settings.REFR_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None