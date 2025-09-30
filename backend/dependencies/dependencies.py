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
    if not hasattr(request.state, "user") or request.state.user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sub = request.state.user["sub"]
    current_user = session.exec(select(Users).where(Users.sub == sub)).first()
    if current_user:
        return current_user
    else:
        return request.state.user

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
def get_optional_user(token: str | None = Depends(get_optional_token),  session: Session = Depends(get_session)) -> Optional[int]:
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
        sub =  payload.get("sub")
        if (sub):
            db_user = session.exec(select(Users).where(Users.sub == sub)).first()
            return db_user
    except JWTError:
        return None
