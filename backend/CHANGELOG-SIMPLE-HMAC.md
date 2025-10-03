# Changelog: Đơn giản hóa HMAC Signature

## Thay đổi

1. **Đơn giản hóa signature format**:
   - **Trước đây**: `METHOD:PATH:TIMESTAMP:API_KEY`
   - **Hiện tại**: `TIMESTAMP:API_KEY`

2. **Bỏ kiểm tra thời gian hết hạn**:
   - **Trước đây**: Kiểm tra timestamp phải trong khoảng ±5 phút so với thời gian hiện tại
   - **Hiện tại**: Chỉ kiểm tra timestamp có phải là số hợp lệ, không kiểm tra thời gian

3. **Tài liệu mới**:
   - Thêm `SIMPLE-API-GUIDE.md` mô tả phương thức xác thực đơn giản hơn
   - Cập nhật README.md để thêm liên kết đến tài liệu mới

## Lý do thay đổi

1. **Đơn giản hóa cho client**:
   - Giảm phức tạp khi tạo signature
   - Dễ dàng triển khai trên nhiều nền tảng

2. **Tránh vấn đề múi giờ**:
   - Loại bỏ lỗi do chênh lệch múi giờ giữa client và server
   - Không cần đồng bộ thời gian chính xác

3. **Vẫn đảm bảo bảo mật**:
   - API key và API secret vẫn được kiểm tra
   - Signature vẫn được tạo bằng HMAC-SHA256

## Cách sử dụng

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
        "X-Signature": signature
    }
```

## Lưu ý

- Timestamp vẫn được yêu cầu để tạo signature, nhưng không dùng để kiểm tra thời gian hết hạn
- Format signature đơn giản hơn giúp dễ dàng debug và triển khai
- Xem `simple_client_example.py` để biết cách sử dụng API trong Python
