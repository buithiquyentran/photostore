# PhotoStore Python SDK

Thư viện Python SDK để tương tác với PhotoStore API một cách dễ dàng, tự động xử lý HMAC authentication.

## Cài đặt

```bash
pip install requests
```

Sao chép file `photostore_sdk.py` vào project của bạn.

## Sử dụng cơ bản

```python
from photostore_sdk import PhotoStoreClient

# Khởi tạo client
client = PhotoStoreClient(
    api_key="pk_your_api_key",
    api_secret="sk_your_api_secret",
    base_url="http://localhost:8000"
)

# Upload files
result = client.upload_files(
    files=["photo1.jpg", "photo2.png"],
    folder_slug="vacation",
    is_private=False,
    tags=["beach", "summer"]
)
print(f"Uploaded {len(result['data'])} files")

# Tìm kiếm bằng text
results = client.search_text("sunset beach", limit=10)
for asset in results['data']:
    print(f"Found: {asset['name']}")

# Tìm kiếm bằng ảnh
similar = client.search_image("query_image.jpg", limit=5)

# Lấy thông tin asset
asset = client.get_asset(asset_id=123)

# Danh sách assets
assets = client.list_assets(
    folder_path="vacation/beach",
    is_private=False,
    limit=50
)

# Cập nhật asset
client.update_asset(
    asset_id=123,
    name="new_name.jpg",
    is_private=True,
    tags=["updated"]
)

# Xóa asset
client.delete_asset(asset_id=123)

# Download private asset
client.get_asset_url(
    file_url="http://localhost:8000/uploads/...",
    save_to="downloaded.jpg"
)
```

## API Reference

### PhotoStoreClient

#### `__init__(api_key, api_secret, base_url, timeout)`

Khởi tạo client với credentials.

#### `upload_files(files, folder_slug=None, project_slug=None, is_private=False, tags=None)`

Upload một hoặc nhiều files.

**Parameters:**

- `files`: List các đường dẫn file
- `folder_slug`: Slug của folder đích (optional)
- `project_slug`: Slug của project (optional)
- `is_private`: File có private không (default: False)
- `tags`: List các tags (optional)

**Returns:** Dict chứa kết quả upload

#### `search_text(query, limit=20, offset=0)`

Tìm kiếm assets bằng text.

**Parameters:**

- `query`: Từ khóa tìm kiếm
- `limit`: Số kết quả tối đa
- `offset`: Offset cho phân trang

**Returns:** Dict chứa kết quả tìm kiếm

#### `search_image(image_path, limit=20)`

Tìm kiếm ảnh tương tự.

**Parameters:**

- `image_path`: Đường dẫn ảnh query
- `limit`: Số kết quả tối đa

**Returns:** Dict chứa ảnh tương tự

#### `get_asset(asset_id)`

Lấy thông tin chi tiết của asset.

#### `delete_asset(asset_id)`

Xóa asset.

#### `list_assets(folder_path=None, is_private=None, is_deleted=False, limit=50, offset=0)`

Lấy danh sách assets với filters.

#### `update_asset(asset_id, name=None, is_private=None, tags=None)`

Cập nhật metadata của asset.

#### `get_asset_url(file_url, save_to=None)`

Download file (dành cho private assets).

## Xử lý lỗi

```python
from photostore_sdk import PhotoStoreClient, PhotoStoreException

try:
    result = client.upload_files(["image.jpg"])
except PhotoStoreException as e:
    print(f"Error: {e}")
```

## Ví dụ nâng cao

### Upload nhiều files với progress

```python
import os

files = ["photo1.jpg", "photo2.jpg", "photo3.jpg"]

for i, file in enumerate(files, 1):
    try:
        result = client.upload_files([file], is_private=False)
        print(f"[{i}/{len(files)}] Uploaded {file}")
    except Exception as e:
        print(f"[{i}/{len(files)}] Failed {file}: {e}")
```

### Tìm kiếm và download

```python
# Tìm kiếm
results = client.search_text("sunset")

# Download tất cả kết quả
for asset in results['data'][:5]:
    filename = f"download_{asset['id']}.jpg"
    client.get_asset_url(asset['file_url'], save_to=filename)
    print(f"Downloaded: {filename}")
```

### Batch update

```python
# Lấy tất cả assets trong folder
assets = client.list_assets(folder_path="vacation")

# Thêm tag cho tất cả
for asset in assets['data']:
    client.update_asset(
        asset_id=asset['id'],
        tags=asset.get('tags', []) + ['vacation2024']
    )
```

## License

MIT
