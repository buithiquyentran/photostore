"""
Middleware để xác thực API key và secret key
"""
from fastapi import Request, HTTPException, Depends
from sqlmodel import Session, select
from db.session import engine, get_session
from models.projects import Projects
import hmac
import hashlib
import time

def verify_api_key(request: Request, session: Session = Depends(get_session)) -> Projects:
    """
    Xác thực API key và secret key.
    Trả về project nếu hợp lệ.
    """
    if request.method == "OPTIONS":
        return None  # Bỏ qua preflight
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Missing API key"
            }
        )

    # Tìm project với API key này
    project = session.exec(
        select(Projects)
        .where(Projects.api_key == api_key)
    ).first()

    if not project:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Invalid API key"
            }
        )

    # Verify signature
    timestamp = request.headers.get("X-Timestamp")
    signature = request.headers.get("X-Signature")

    if not timestamp or not signature:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Missing timestamp or signature"
            }
        )

    # Kiểm tra timestamp format (không kiểm tra thời gian để tránh lệch múi giờ)
    try:
        # Chỉ kiểm tra timestamp có phải là số hợp lệ
        ts = int(timestamp)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Invalid timestamp format"
            }
        )
     # check expired 5 phút
    now = int(time.time())
    if now - int(timestamp) > 3600: #60*5
        raise HTTPException(status_code=401, detail={
                "status": "error",
                "message": "Signature expired"
            })

    # Tạo signature để so sánh
    # Format đơn giản: TIMESTAMP:API_KEY
    message = f"{timestamp}:{api_key}"
    expected_signature = hmac.new(
        project.api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    # Debug logs (uncomment khi cần debug)
    # print(f"[DEBUG] Signature verification:")
    # print(f"  Timestamp: {timestamp}")
    # print(f"  API Key: {api_key}")
    # print(f"  API Secret: {project.api_secret[:20]}...")
    # print(f"  Message: {message}")
    # print(f"  Expected: {expected_signature}")
    # print(f"  Received: {signature}")
    # print(f"  Match: {hmac.compare_digest(signature, expected_signature)}")

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=401,
            detail={
                "status": "error",
                "message": "Invalid signature"
            }
        )

    return project

async def verify_api_request(request: Request, call_next):
    """
    Middleware để xác thực API requests.
    Chỉ áp dụng cho các routes bắt đầu bằng /api/v1/external
    """
    if not request.url.path.startswith("/api/v1/external"):
        return await call_next(request)

    try:
        with Session(engine) as session:
            project = verify_api_key(request, session)
            # Lưu project vào request state để route handlers có thể sử dụng
            request.state.project = project
            return await call_next(request)
    except HTTPException as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=e.status_code,
            content=e.detail
        )
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error"
            }
        )
