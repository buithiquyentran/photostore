# dependencies/external_auth.py
from fastapi import Depends, HTTPException, Form
from sqlalchemy.orm import Session
from db.session import get_session
import time

from services.api_client.api_client_service import get_client_by_key
from services.api_client.signature import generate_signature

async def verify_external_request(
    api_key: str = Form(...),
    timestamp: int = Form(...),
    signature: str = Form(...),
    session: Session = Depends(get_session)
):
    client = get_client_by_key(api_key=api_key, session=session)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # check expired 5phut
    now = int(time.time())
    if now - int(timestamp) > 300:
        raise HTTPException(status_code=401, detail="Signature expired")

    # build lại params đúng như khi ký
    params = {"timestamp": str(timestamp)}
    expected = generate_signature(params, client.api_secret, add_timestamp=False)

    if expected["signature"] != signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    return client
