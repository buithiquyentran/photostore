import time, hashlib

def generate_signature(params: dict , api_secret: str, add_timestamp: bool = True):
    """
    Sinh signature từ params + api_secret
    - params: dict các tham số (vd: {"folder": "demo"})
    - api_secret: secret của client
    - add_timestamp: nếu True thì tự thêm timestamp vào params
    """
    # Thêm timestamp nếu chưa có
    if add_timestamp and "timestamp" not in params:
        params["timestamp"] = str(int(time.time()))

    # Sắp xếp params theo alphabet key
    sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params.items()))

    # Ghép với api_secret để ký
    to_sign = f"{sorted_params}{api_secret}"

    signature = hashlib.sha256(to_sign.encode()).hexdigest()

    return {
        "params": params,
        "signature": signature
    }
