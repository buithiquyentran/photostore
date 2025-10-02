from fastapi import Depends, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
import requests
import fnmatch
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional
from jose import JWTError
from sqlmodel import Session, select
from db.session import get_session
from models.users import Users
from core.config import settings

KEYCLOAK_URL = settings.KEYCLOAK_URL
ALGORITHM = "RS256"

# Lazy load JWKS - chỉ load khi cần
_jwks_cache = None

def get_jwks():
    """Lazy load và cache JWKS từ Keycloak"""
    global _jwks_cache
    if _jwks_cache is None:
        try:
            _jwks_cache = requests.get(f"{KEYCLOAK_URL}/protocol/openid-connect/certs", timeout=5).json()
        except Exception as e:
            print(f"Warning: Cannot load JWKS from Keycloak: {e}")
            raise HTTPException(status_code=503, detail="Authentication service unavailable")
    return _jwks_cache

def get_current_user(request: Request,  session: Session = Depends(get_session)):
    """
    Lấy current user từ token.
    Trả về Users object từ database.
    """
    if not hasattr(request.state, "user") or request.state.user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    sub = request.state.user.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token: missing sub")
    
    # Tìm user trong database
    current_user = session.exec(select(Users).where(Users.sub == sub)).first()
    
    if not current_user:
        # User chưa tồn tại trong database, tạo mới từ token info
        email = request.state.user.get("email")
        username = request.state.user.get("preferred_username") or email
        
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: missing email")
        
        current_user = Users(
            sub=sub,
            email=email,
            username=username,
            is_superuser=False
        )
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        print(f"✅ Created new user in DB: {current_user.email} (id: {current_user.id})")
    
    return current_user

def get_key(token: str):
    """Chọn public key theo kid trong header JWT"""
    unverified_header = jwt.get_unverified_header(token)
    jwks = get_jwks()  # Lazy load JWKS
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return key
    raise HTTPException(status_code=401, detail="Public key not found")

# ✅ Dependency: lấy token từ header nếu có
async def get_optional_token(request: Request) -> Optional[str]:
    auth: str = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(auth)
    print("scheme, param", scheme, param)
    if not auth or scheme.lower() != "bearer":
        return None
    return param

# ✅ Dependency: parse token thành user_id (có thể None)
async def get_optional_user(token: str | None = Depends(get_optional_token), session: Session = Depends(get_session)) -> Optional[Users]:
    """
    Parse token và trả về Users object từ database.
    Nếu user chưa tồn tại trong DB, tạo mới từ token info.
    """
    if not token:
        return None
    try:
        key = get_key(token)
        payload = jwt.decode(
            token,
            key,
            algorithms=[ALGORITHM],
            options={"verify_aud": False}
        )
        print("payload", payload)
        if not payload:
            return None
            
        sub = payload.get("sub")
        if not sub:
            return None
            
        # Tìm user trong database
        db_user = session.exec(select(Users).where(Users.sub == sub)).first()
        
        if not db_user:
            # User chưa tồn tại trong database, tạo mới từ token info
            email = payload.get("email")
            username = payload.get("preferred_username") or email
            
            if not email:
                return None
                
            db_user = Users(
                sub=sub,
                email=email,
                username=username,
                is_superuser=False
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            print(f"✅ Created new user in DB: {db_user.email} (id: {db_user.id})")
            
        return db_user
    except JWTError:
        return None
