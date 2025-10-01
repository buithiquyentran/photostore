# 🎯 PhotoStore - Image Embeddings & Search Guide

## Tổng quan

Hệ thống tự động tạo **embeddings** (vector representations) cho mọi ảnh được upload, cho phép:
- 🔍 Tìm kiếm ảnh bằng ảnh tương tự
- 📝 Tìm kiếm ảnh bằng text mô tả (semantic search)
- 📁 Tìm kiếm trong phạm vi project hoặc folder cụ thể

## Cơ chế hoạt động

### 1. Upload Flow - Tự động tạo Embeddings

```
📤 User Upload Image
    ↓
💾 Lưu file vào storage
    ↓
📊 Tạo Asset record (database)
    ↓
🤖 TỰ ĐỘNG: Extract CLIP embedding (512-dim vector)
    ↓
💿 Lưu vào bảng embeddings (project_id, folder_id, vector)
    ↓
⚡ TỰ ĐỘNG: Add vào FAISS index của project
    ↓
✅ Sẵn sàng tìm kiếm!
```

### 2. Cấu trúc dữ liệu

**Bảng embeddings:**
```
id          : int (PK)
asset_id    : int (FK → assets.id)
project_id  : int (FK → projects.id) [INDEXED]
folder_id   : int (FK → folders.id) [INDEXED, NULLABLE]
embedding   : text (JSON array của 512 floats)
created_at  : datetime
```

**FAISS Index (In-memory):**
```python
PROJECT_INDICES = {
    1: faiss.Index,  # Project 1 có index riêng
    2: faiss.Index,  # Project 2 có index riêng
    ...
}
```

## API Endpoints

### Upload với Auto-Embedding

#### 1. Upload qua Web UI
```bash
POST /api/v1/users/assets/upload-images

# Form data
files: [file1.jpg, file2.jpg, ...]
folder_name: "my_photos"  # optional
is_private: false

# Response
{
  "status": 1,
  "data": [
    {
      "id": 123,
      "path": "1/10/my_photos/abc.jpg",
      ...
    }
  ]
}

# ✅ Embeddings tự động được tạo cho mỗi ảnh!
```

#### 2. Upload qua External API
```bash
POST /api/v1/external/assets/upload

# Headers
X-API-Key: your_api_key
X-Signature: generated_signature

# Form data
files: [file1.jpg, file2.jpg, ...]
folder_name: "uploads"  # optional

# ✅ Embeddings tự động được tạo!
```

### Search APIs

#### 1. Search bằng Image
```bash
POST /api/v1/search/image

# Form data
file: query_image.jpg
project_id: 1
folder_id: 5  # optional, để tìm trong folder cụ thể
k: 10         # số lượng kết quả

# Response
{
  "status": 1,
  "data": [
    {
      "id": 456,
      "name": "photo.jpg",
      "path": "...",
      "similarity": 0.95
    },
    ...
  ],
  "total": 10,
  "query_type": "image"
}
```

#### 2. Search bằng Text
```bash
POST /api/v1/search/text

# Form data
query: "a cat sitting on the sofa"
project_id: 1
folder_id: 5  # optional
k: 10

# Response
{
  "status": 1,
  "data": [...],
  "total": 10,
  "query": "a cat sitting on the sofa",
  "query_type": "text"
}
```

#### 3. Rebuild Index
```bash
POST /api/v1/search/rebuild

project_id: 1

# Response
{
  "status": 1,
  "message": "Project 1 index rebuilt successfully",
  "stats": {
    "total_vectors": 1523,
    "indexed": true,
    "dimension": 512
  }
}
```

#### 4. Get Search Stats
```bash
GET /api/v1/search/stats/1

# Response
{
  "project_id": 1,
  "total_vectors": 1523,
  "indexed": true,
  "dimension": 512
}
```

## Code Examples

### Backend - Auto Embedding Creation

```python
# backend/api/routes/user_assets.py

@router.post("/upload-images")
async def upload_assets(...):
    # Lưu asset
    asset_id = add_asset(
        session=session,
        user_id=user_id,
        folder_id=folder_id,
        path=path,
        ...
    )
    
    # 🔥 TỰ ĐỘNG tạo embedding
    if file.content_type.startswith("image/"):
        embedding = create_embedding_for_asset(
            session=session,
            asset_id=asset_id,
            image_bytes=file_bytes
        )
        # ✅ Đã lưu vào DB và FAISS
```

### Backend - Manual Embedding Creation

```python
from db.crud_embedding import create_embedding_for_asset

# Tạo embedding cho asset đã tồn tại
embedding = create_embedding_for_asset(
    session=session,
    asset_id=123,
    image_bytes=open("photo.jpg", "rb").read()
)
```

### Backend - Search

```python
from services.search.embeddings_service import search_by_text, search_by_image

# Search by text
results = search_by_text(
    session=session,
    project_id=1,
    query_text="sunset on the beach",
    k=20,
    folder_id=5  # optional
)

# Search by image
from PIL import Image
query_image = Image.open("query.jpg")

results = search_by_image(
    session=session,
    project_id=1,
    image=query_image,
    k=20,
    folder_id=5  # optional
)
```

### Frontend - Upload with Auto Embedding

```typescript
// Upload images - embeddings tự động được tạo
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);
formData.append('folder_name', 'vacation_photos');
formData.append('is_private', 'false');

const response = await fetch('/api/v1/users/assets/upload-images', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

// ✅ Embeddings đã được tạo tự động!
```

### Frontend - Search

```typescript
// Search by text
const searchByText = async (query: string, projectId: number) => {
  const formData = new FormData();
  formData.append('query', query);
  formData.append('project_id', projectId.toString());
  formData.append('k', '20');
  
  const response = await fetch('/api/v1/search/text', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};

// Search by image
const searchByImage = async (file: File, projectId: number) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('project_id', projectId.toString());
  formData.append('k', '20');
  
  const response = await fetch('/api/v1/search/image', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};
```

## Database Migration

Nếu bạn đã có database cũ, cần chạy migration:

```bash
# Chạy migration SQL
mysql -u photostore_user -p photostore < backend/migrations/add_project_folder_to_embeddings.sql
```

Hoặc dùng SQLModel để tạo bảng mới:

```python
from db.session import engine
from sqlmodel import SQLModel

# Tạo tất cả bảng (bao gồm embeddings mới)
SQLModel.metadata.create_all(engine)
```

## Performance Tips

### 1. Batch Upload

Upload nhiều ảnh cùng lúc để tối ưu:

```python
# ✅ GOOD: Upload batch
files = [file1, file2, file3, ...]
response = upload_assets(files=files)

# ❌ BAD: Upload từng file
for file in files:
    response = upload_assets(files=[file])
```

### 2. Background Processing

Với project lớn (>10K images), nên tạo embeddings trong background:

```python
from fastapi import BackgroundTasks

def create_embeddings_background(asset_ids: list[int]):
    for asset_id in asset_ids:
        create_embedding_for_asset(...)

@router.post("/upload-images")
async def upload_assets(..., background_tasks: BackgroundTasks):
    asset_ids = []
    for file in files:
        asset_id = add_asset(...)
        asset_ids.append(asset_id)
    
    # Tạo embeddings trong background
    background_tasks.add_task(create_embeddings_background, asset_ids)
```

### 3. Rebuild Strategy

- **On startup:** Load indices cho active projects
- **Periodic:** Rebuild indices mỗi ngày cho large projects
- **On-demand:** Rebuild khi cần (sau restore DB)

## Troubleshooting

### Embedding không được tạo?

**Check logs:**
```
✅ Created embedding for asset 123        # Success
⚠️ Failed to create embedding for asset 124  # Failed
```

**Debug:**
1. File có phải image không?
2. CLIP model đã load?
3. File bytes có valid?

```python
# Debug code
print(f"Content-Type: {file.content_type}")
print(f"File size: {len(file_bytes)}")

try:
    img = Image.open(io.BytesIO(file_bytes))
    print(f"Image: {img.size}, {img.mode}")
except Exception as e:
    print(f"Invalid image: {e}")
```

### Search không trả về kết quả?

**Check:**
```bash
# 1. Check project có embeddings?
GET /api/v1/search/stats/1

# 2. Rebuild nếu cần
POST /api/v1/search/rebuild
project_id=1
```

**Logs:**
```
[FAISS] Project 1 has no index        # Cần rebuild
[FAISS] Project 1 index is empty      # Chưa có embeddings
```

### Performance chậm?

**Optimize:**
1. Giảm `k` (số kết quả)
2. Sử dụng IVF index cho large datasets (>100K)
3. Cache CLIP model (đã có sẵn)
4. Use GPU nếu có

## Best Practices

### ✅ DO

- Upload images theo batch
- Set folder_name rõ ràng
- Rebuild indices định kỳ cho large projects
- Monitor embedding creation logs
- Use appropriate `k` value (10-50)

### ❌ DON'T

- Upload từng file một (slow)
- Ignore embedding creation errors
- Search với k > 100 (slow)
- Delete embeddings manually (dùng API)

## Architecture Summary

```
┌─────────────────────────────────────────────┐
│              UPLOAD FLOW                     │
├─────────────────────────────────────────────┤
│ Upload Image → Save File → Create Asset     │
│      ↓                                       │
│ Auto Create Embedding (CLIP)                │
│      ↓                                       │
│ Save to DB (project_id, folder_id)          │
│      ↓                                       │
│ Auto Add to FAISS (project-based index)     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              SEARCH FLOW                     │
├─────────────────────────────────────────────┤
│ Query (Image/Text) → Extract Embedding      │
│      ↓                                       │
│ Search in Project FAISS Index               │
│      ↓                                       │
│ Filter by Folder (optional)                 │
│      ↓                                       │
│ Return Sorted Results                       │
└─────────────────────────────────────────────┘
```

---

**Happy Searching! 🚀**

Xem thêm:
- [SEARCH-ARCHITECTURE.md](./SEARCH-ARCHITECTURE.md) - Chi tiết architecture
- [UPLOAD-FLOW.md](./UPLOAD-FLOW.md) - Chi tiết upload flow
