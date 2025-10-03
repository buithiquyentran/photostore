# Hướng dẫn sử dụng API Signature Generator

Script `generate_signature.py` giúp tạo signature và headers cần thiết để gọi External API của PhotoStore.

## Cách sử dụng

### 1. Chạy với API key và secret mặc định

```bash
python generate_signature.py
```

API key và secret mặc định được cấu hình trong file `generate_signature.py`. Bạn có thể thay đổi giá trị này để không phải nhập mỗi lần chạy.

### 2. Chạy với API key và secret từ command line

```bash
python generate_signature.py -k YOUR_API_KEY -s YOUR_API_SECRET
```

### 3. Xuất headers dạng curl

```bash
python generate_signature.py -c
```

### 4. Lưu headers vào file

```bash
python generate_signature.py -o headers.json
```

### 5. Sử dụng timestamp tùy chỉnh

```bash
python generate_signature.py -t 1696204800
```

## Tham số

| Tham số | Mô tả |
|---------|-------|
| `-k`, `--key` | API key |
| `-s`, `--secret` | API secret |
| `-t`, `--timestamp` | Unix timestamp tùy chỉnh |
| `-c`, `--curl` | Xuất headers dạng curl |
| `-o`, `--save` | Lưu headers vào file |
| `-h`, `--help` | Hiển thị trợ giúp |

## Ví dụ kết quả

```
============================================================
API Headers (Copy & Paste)
============================================================
Postman headers:
X-API-Key: pk_xxx
X-Timestamp: 1696204800
X-Signature: abc123def456
Content-Type: application/json
============================================================

Expiration time: 2025-10-03 09:51:40
```

## Cấu hình thời gian hết hạn

Thời gian hết hạn của signature được cấu hình trong file `.env` thông qua biến `API_KEY_EXPIRY_SECONDS`:

```
# API Key Settings
# Set to 0 to disable expiry check (không kiểm tra thời gian hết hạn)
API_KEY_EXPIRY_SECONDS=300
```

- Nếu `API_KEY_EXPIRY_SECONDS > 0`: Kiểm tra timestamp phải nằm trong khoảng ±N giây so với thời gian hiện tại
- Nếu `API_KEY_EXPIRY_SECONDS = 0`: Không kiểm tra thời gian hết hạn, chỉ kiểm tra format

## Sử dụng trong code

```python
import hmac
import hashlib
import time

def generate_signature(api_key, api_secret):
    timestamp = str(int(time.time()))
    message = f"{timestamp}:{api_key}"
    signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "X-API-Key": api_key,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/json"
    }
```
