from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db.session import get_session
from models.users import Users  
from dependencies.dependencies import get_current_user
from db.crud_user import add_user_with_assets
router = APIRouter(prefix="/users/users", tags=["Users"])


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(Users, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    try:
        session.delete(user)
        session.commit()
        return {"status": "success", "message": "Xóa user thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa user: {e}")

@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

@router.post("/social-login")
async def social_login(user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    # user lấy ra từ token Keycloak (đã decode trong middleware)
    sub_id = user["sub"]
    email = user.get("email")
    username = user.get("name")

    db_user = session.exec(select(Users).where(Users.sub_id == sub_id)).first()

    if not db_user:
        new_user = await add_user_with_assets(session=session, email=email, username=username,  sub_id=sub_id)
        return {"msg": "User created", "user": new_user}
    
    return {"msg": "User exists", "user": db_user}

