from fastapi import Request, HTTPException
from jose.exceptions import JWTError, ExpiredSignatureError
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
import requests
import fnmatch
from core.config import settings

# Sử dụng KEYCLOAK_URL từ environment variables
KEYCLOAK_URL = settings.KEYCLOAK_URL
ALGORITHM = "RS256"
CLIENT_ID = settings.CLIENT_ID

# Lazy load JWKS - chỉ load khi cần để tránh crash khi Keycloak chưa sẵn sàng
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

def get_key(token: str):
    """Chọn public key theo kid trong header JWT"""
    unverified_header = jwt.get_unverified_header(token)
    jwks = get_jwks()  # Lazy load JWKS
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return key
    raise HTTPException(status_code=401, detail="Public key not found")
# def extract_user_roles(payload: dict) -> list:
#     return payload.get("realm_access", {}).get("roles", [])
def has_client_role(payload: dict, required_roles: str) -> bool:
    client_roles = payload.get("resource_access", {}).get(CLIENT_ID, {}).get("roles", [])
    print("client_roles", client_roles)
    print("required_roles", required_roles)
    return any(r in client_roles for r in required_roles)

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, required_roles=None):
        super().__init__(app)
        self.required_roles = required_roles or {}
        self.public_paths = [
           "/api/v1/auth/*",
           "/api/external/*",  # External API with API key auth
           "/api/v1/openapi.json",
           "/docs",
           "/redoc",
           "/favicon.ico",
           "/api/v1/test/*",  # Test
           
        ]

    def _get_required_roles_for_path(self, path: str):
        matches = []
        for pat, roles in self.required_roles.items():
            if fnmatch.fnmatch(path, pat):
                matches.append((pat, roles))
        if not matches:
            return None
        best = max(matches, key=lambda x: len(x[0]))
        return best[1]

    async def dispatch(self, request: Request, call_next):
        # Allow OPTIONS requests for CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # bypass public
        if any(fnmatch.fnmatch(request.url.path, pat) for pat in self.public_paths):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing token"})

        token = auth_header.split(" ", 1)[1]
        try:
            key = get_key(token)
            payload = jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})

            required = self._get_required_roles_for_path(request.url.path)
            # if required and not has_client_role(payload, required):
            #     return JSONResponse(status_code=403, content={"detail": "Forbidden: insufficient role"})

            request.state.user = payload

        except ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Token expired"})
        except JWTError as e:
            return JSONResponse(status_code=401, content={"detail": f"Invalid token: {str(e)}"})
        except HTTPException:
            # nếu có HTTPException khác đâu đó, cho nó đi qua
            raise
        except Exception as e:
            # lỗi không liên quan token -> cho FastAPI xử lý (500)
            raise

        return await call_next(request)