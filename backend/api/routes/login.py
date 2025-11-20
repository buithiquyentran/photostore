from fastapi import APIRouter, HTTPException, status
import requests
from pydantic import BaseModel
from typing import Dict, Any

from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ============================================
# Request/Response Models
# ============================================
class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str

# ============================================
# Authentication Endpoints
# ============================================

@router.post("/login")
def login_with_keycloak(credentials: LoginRequest):
    """
    Login user với Keycloak và trả về access_token + refresh_token
    """
    payload = {
        "client_id": settings.CLIENT_ID, # CLIENT_ID  = photostore_client
        "grant_type": "password",
        "username": credentials.username,
        "password": credentials.password,
    }

    try:
        resp = requests.post(
            f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token", # KEYCLOAK_URL  = http://photostore_keycloak:8080/realms/photostore_realm
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if resp.status_code != 200:
            error_detail = resp.json() if resp.headers.get("content-type") == "application/json" else resp.text
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Keycloak authentication failed: {error_detail}"
            )
        
        return resp.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to authentication service: {str(e)}"
        )

@router.post("/refresh")
def refresh_token(request: RefreshRequest):
    """
    Refresh access token sử dụng refresh_token
    """
    payload = {
        "client_id": settings.CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": request.refresh_token,
    }

    try:
        resp = requests.post(
            f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )

        if resp.status_code != 200:
            error_detail = resp.json() if resp.headers.get("content-type") == "application/json" else resp.text
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Token refresh failed: {error_detail}"
            )
        
        return resp.json()
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to authentication service: {str(e)}"
        )

@router.post("/logout")
def logout(request: RefreshRequest):
    """
    Logout user và invalidate refresh token
    """
    payload = {
        "client_id": settings.CLIENT_ID,
        "refresh_token": request.refresh_token,
    }

    try:
        resp = requests.post(
            f"{settings.KEYCLOAK_URL}/protocol/openid-connect/logout",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )

        if resp.status_code != 204:  # Keycloak trả về 204 No Content nếu thành công
            error_detail = resp.json() if resp.headers.get("content-type") == "application/json" else resp.text
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"Logout failed: {error_detail}"
            )

        return {"message": "Logged out successfully", "status": "success"}
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to authentication service: {str(e)}"
        )

# ============================================
# Admin Functions - User Registration
# ============================================

def get_admin_token() -> str:
    """
    Lấy admin access token từ Keycloak sử dụng client credentials grant
    Token này có quyền admin để tạo/quản lý users
    """
    payload = {
        "client_id": settings.ADMIN_CLIENT_ID,
        "client_secret": settings.ADMIN_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    
    try:
        resp = requests.post(
            f"{settings.KEYCLOAK_URL}/protocol/openid-connect/token",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if resp.status_code != 200:
            error_detail = resp.json() if resp.headers.get("content-type") == "application/json" else resp.text
            print(f"Failed to get admin token: {error_detail}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cannot obtain admin token: {error_detail}"
            )
        
        return resp.json()["access_token"]
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to authentication service: {str(e)}"
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_data: RegisterRequest):
    """
    Đăng ký user mới trong Keycloak
    Yêu cầu admin token để thực hiện
    """
    # Lấy admin token
    admin_token = get_admin_token()
    
    # Tạo payload user theo format của Keycloak Admin API
    user_payload = {
        "username": user_data.username,
        "email": user_data.email,
        "firstName": user_data.first_name or "",
        "lastName": user_data.last_name or "",
        "enabled": True,
        "emailVerified": True,
        "credentials": [
            {
                "type": "password",
                "value": user_data.password,
                "temporary": False
            }
        ],
    }
    
    # Extract base URL từ KEYCLOAK_URL (remove /realms/realm_name)
    # KEYCLOAK_URL format: http://keycloak:8080/realms/photostore_realm
    keycloak_base_url = settings.KEYCLOAK_URL.split("/realms/")[0]
    realm_name = settings.KEYCLOAK_URL.split("/realms/")[1] if "/realms/" in settings.KEYCLOAK_URL else "photostore_realm"
    
    try:
        resp = requests.post(
            f"{keycloak_base_url}/admin/realms/{realm_name}/users",
            json=user_payload,
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if resp.status_code == 201:
            return {
                "message": "User registered successfully",
                "status": 1,
                "username": user_data.username,
                "email": user_data.email
            }
        elif resp.status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists"
            )
        else:
            error_detail = resp.json() if resp.headers.get("content-type") == "application/json" else resp.text
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"User registration failed: {error_detail}"
            )
    
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Cannot connect to authentication service: {str(e)}"
        )
