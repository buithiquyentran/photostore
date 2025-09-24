from fastapi import Depends, Request, HTTPException

def get_current_user(request: Request):
    if not hasattr(request.state, "user") or request.state.user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user

