from fastapi import Depends, Request, HTTPException
from fastapi import Request, HTTPException
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

KEYCLOAK_URL = "http://localhost:8080/realms/photostore_realm"
ALGORITHM = "RS256"

# Load JWKS từ Keycloak
jwks = requests.get(f"{KEYCLOAK_URL}/protocol/openid-connect/certs").json()
def get_current_user(request: Request):
    if not hasattr(request.state, "user") or request.state.user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user



def get_key(token: str):
    """Chọn public key theo kid trong header JWT"""
    unverified_header = jwt.get_unverified_header(token)
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
        sub_id =  payload.get("sub")
        if (sub_id):
            db_user = session.exec(select(Users).where(Users.sub_id == sub_id)).first()
            return db_user
    except JWTError:
        return None
