from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from sqlalchemy import text
from db.session import get_session
from core.security import create_access_token, decode_access_token
from pydantic import BaseModel

from models.users import Users
router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    status: int = 0
    access_token: str
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
    """
    Gọi procedure MySQL để login, nếu thành công thì trả về JWT token
    """
    try:
        # Gọi stored procedure
        result = session.exec(
            text("CALL login(:p_email, :p_password)").bindparams(p_email=data.email, p_password=data.password)
        )

        user = result.mappings().first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Tạo JWT
        token = create_access_token({"sub": str(user["id"]), "email": user["email"]})

        return {
            "status": 1,
            "access_token": token,
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

    id = payload.get("sub")
    user = session.get(Users, id)
    return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_superuser": user.is_superuser
        }
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")