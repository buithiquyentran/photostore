from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
import requests
import fnmatch

KEYCLOAK_URL = "http://localhost:8080/realms/photostore_realm"
ALGORITHM = "RS256"

# Load JWKS từ Keycloak
jwks = requests.get(f"{KEYCLOAK_URL}/protocol/openid-connect/certs").json()

def get_key(token: str):
    """Chọn public key theo kid trong header JWT"""
    unverified_header = jwt.get_unverified_header(token)
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return key
    raise HTTPException(status_code=401, detail="Public key not found")
def extract_user_roles(payload: dict) -> list:
    return payload.get("realm_access", {}).get("roles", [])

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, required_roles=None):
        super().__init__(app)
        self.required_roles = required_roles or []
        self.public_paths = [
           "/api/v1/auth/*",
            "/api/v1/openapi.json",
            "/docs",
            "/redoc",
        ]
   
    def _get_required_roles_for_path(self, path: str):
        """
        Trả về List roles yêu cầu cho path, hoặc None nếu không yêu cầu roles.
        Khi có nhiều pattern match, chọn pattern dài nhất (most specific).
        """
        matches = []
        print(path)
        for pat, roles in self.required_roles.items():
            print("pat, roles",pat, roles)  
            if fnmatch.fnmatch(path, pat):
                matches.append((pat, roles))
        if not matches:
            return None
        # chọn pattern dài nhất (specific)
        best = max(matches, key=lambda x: len(x[0]))
        return best[1]
    
    async def dispatch(self, request: Request, call_next):
        # Nếu path nằm trong danh sách public thì bỏ qua check
        import fnmatch

        if any(fnmatch.fnmatch(request.url.path, pat) for pat in self.public_paths):
            return await call_next(request)


        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")

        token = auth_header.split(" ")[1]

        try:
            key = get_key(token)
            payload = jwt.decode(
                token,
                key,
                algorithms=[ALGORITHM],
                options={"verify_aud": False}
            )

            path = request.url.path
            required = self._get_required_roles_for_path(path)
            print("required", required)
            if required:
                user_roles = extract_user_roles(payload)
                print("user_roles", user_roles)
                
                # if not any(r in user_roles for r izn required):
                #     raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
            request.state.user = payload

        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

        return await call_next(request)
