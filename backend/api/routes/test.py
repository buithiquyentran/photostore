from fastapi import APIRouter

router = APIRouter(prefix="/test", tags=["Test"])
from fastapi import APIRouter, Query
import hmac, hashlib
import time

@router.get("/signature")
def get_signature(
    api_key: str = Query(...),
    api_secret: str = Query(...),
    
):
    """
    Sinh signature để test xác thực API.
    """
    timestamp = str(int(time.time()))
    message = f"{timestamp}:{api_key}"
    signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return {
        "api_key": api_key,
        "api_secret": api_secret,
        "timestamp": timestamp,
        "signature": signature
    }
