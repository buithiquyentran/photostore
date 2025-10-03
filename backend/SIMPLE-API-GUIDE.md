# Hướng dẫn sử dụng External API (Phiên bản đơn giản)

Tài liệu này mô tả cách sử dụng External API với phương thức xác thực đơn giản hơn.

## Xác thực API

External API sử dụng phương thức xác thực dựa trên API key và signature để bảo vệ các endpoints. Phương thức này đã được đơn giản hóa để dễ sử dụng hơn.

### Headers cần thiết

Mỗi request cần có 3 headers:

```
X-API-Key: <API key của project>
X-Timestamp: <Unix timestamp>
X-Signature: <HMAC-SHA256 signature>
```

### Cách tạo signature

Signature được tạo bằng cách mã hóa một chuỗi message với API secret sử dụng thuật toán HMAC-SHA256:

```
message = "{timestamp}:{api_key}"
signature = HMAC-SHA256(message, api_secret)
```

### Ví dụ tạo signature bằng Python

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

### Lưu ý về timestamp

- Timestamp chỉ được sử dụng để tạo signature, không kiểm tra thời gian hết hạn
- Format là Unix timestamp (số giây kể từ 1/1/1970 UTC)
- Không cần lo lắng về múi giờ, chỉ cần đảm bảo timestamp là một số hợp lệ

## Endpoints

### Quản lý thư mục

```
# Tạo folder mới
POST /api/v1/external/folders
Content-Type: application/json
{
  "name": "Tên thư mục",
  "parent_id": null,  # Optional, ID của thư mục cha
  "description": "Mô tả"  # Optional
}

# Lấy danh sách folders
GET /api/v1/external/folders
GET /api/v1/external/folders?parent_id=123  # Lọc theo parent folder

# Xóa folder
DELETE /api/v1/external/folders/{folder_id}
```

### Quản lý assets

```
# Upload assets
POST /api/v1/external/assets/upload
Content-Type: multipart/form-data
files: [file1, file2, ...]
folder_id: 123  # Optional
is_private: false  # Optional, default false

# Lấy danh sách assets
GET /api/v1/external/assets
GET /api/v1/external/assets?folder_id=123  # Lọc theo folder

# Xóa asset
DELETE /api/v1/external/assets/{asset_id}
```

### Tìm kiếm

```
# Tìm kiếm bằng text
POST /api/v1/external/search/text
Content-Type: multipart/form-data
query: "cat sitting on sofa"
k: 10  # Số lượng kết quả, mặc định 10
folder_id: 123  # Optional, lọc theo folder

# Tìm kiếm bằng ảnh
POST /api/v1/external/search/image
Content-Type: multipart/form-data
file: [upload file ảnh]
k: 10  # Số lượng kết quả, mặc định 10
folder_id: 123  # Optional, lọc theo folder
```

## Client Example

Xem file `simple_client_example.py` để biết cách sử dụng API trong Python.

```python
from photostore_client import PhotoStoreClient

client = PhotoStoreClient(
    api_key="pk_xxx",
    api_secret="sk_xxx",
    base_url="http://localhost:8000"
)

# Tạo folder
folder = client.create_folder("Thư mục mới")

# Upload ảnh
result = client.upload_files(
    file_paths=["image1.jpg", "image2.png"],
    folder_id=folder["id"],
    is_private=False
)

# Tìm kiếm
search_results = client.search_by_text("cat on sofa", k=5)
```
