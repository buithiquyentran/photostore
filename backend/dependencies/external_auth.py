# dependencies/external_auth.py
from fastapi import Depends, HTTPException, Form
from sqlalchemy.orm import Session
from db.session import get_session
import time
from typing import Optional
from services.api_client.api_client_service import get_client_by_key
from services.api_client.signature import generate_signature

async def verify_external_request(
    api_key: Optional[str] = Form(None),
    timestamp: Optional[int] = Form(None),
    signature: Optional[str] = Form(None),
    session: Session = Depends(get_session),
):
    # Trường hợp public -> không cần verify
    if not api_key or not timestamp or not signature:
        return None

    client = get_client_by_key(api_key=api_key, session=session)
    if not client:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # check expired 5 phút
    now = int(time.time())
    if now - int(timestamp) > 3600: #60*5
        raise HTTPException(status_code=401, detail="Signature expired")

    # build lại params đúng như khi ký
    params = {"timestamp": str(timestamp)}
    expected = generate_signature(params, client.api_secret, add_timestamp=False)

    if expected["signature"] != signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    return client
