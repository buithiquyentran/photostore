from fastapi import APIRouter, Depends, HTTPException,status
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
import requests
from pydantic import BaseModel

from core.config import settings



router = APIRouter(prefix="/auth", tags=["Authentication"])
class LoginRequest(BaseModel):
    username: str
    password: str
class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
def login_with_keycloak(data: LoginRequest):
    data = {
        "client_id": settings.CLIENT_ID,
        "grant_type": "password",
        "username": data.username,
        "password": data.password,
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token", data=data, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    tokens = resp.json()
    return tokens

@router.post("/refresh")
def refresh_token(payload: RefreshRequest):
    data = {
        "client_id": settings.CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": payload.refresh_token,  # ✅ phải để key là string
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(
        f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token",
        data=data,
        headers=headers,
    )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())
    return resp.json()

@router.post("/logout")
def logout(data: RefreshRequest):
    payload = {
        "client_id": settings.CLIENT_ID,
        "refresh_token": data.refresh_token,
    }

    # Nếu client là confidential thì cần thêm client_secret
    # data["client_secret"] = CLIENT_SECRET

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(f"{settings.KEYCLOAK_URL}/protocol/openid-connect/logout", data=payload, headers=headers)

    if resp.status_code != 204:  # Keycloak trả về 204 No Content nếu OK
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return {"status": "1"}


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str

# Hàm lấy admin token
def get_admin_token():
    data = {
        "client_id": settings.ADMIN_CLIENT_ID,
        "client_secret": settings.ADMIN_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    resp = requests.post(
        f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print(resp)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())
    return resp.json()["access_token"]

# API đăng ký
@router.post("/register")
def register_user(data: RegisterRequest):
    token = get_admin_token()
    payload = {
        "username": data.username,
        "email": data.email,
        "firstName": data.first_name or "",
        "lastName": data.last_name or "",
        "enabled": True,
        "credentials": [
            {"type": "password", "value": data.password, "temporary": False}
        ],
    }
    
    resp = requests.post(
        f"http://localhost:8080/admin/realms/photostore_realm/users",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )

    if resp.status_code not in [200, 201]:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())

    return {"msg": "User registered successfully", "status": 200}
