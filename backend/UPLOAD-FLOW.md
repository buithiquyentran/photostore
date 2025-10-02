# 📤 Upload Flow - Tự động tạo Embeddings

## Tổng quan

Khi người dùng upload ảnh (qua Web UI hoặc API), hệ thống tự động:

1. ✅ Lưu file vào storage
2. ✅ Tạo record trong bảng `assets`
3. ✅ **TỰ ĐỘNG** tạo embedding vector (CLIP)
4. ✅ Lưu vào bảng `embeddings` với `project_id` và `folder_id`
5. ✅ **TỰ ĐỘNG** đồng bộ vào FAISS index của project

## Flow chi tiết

### 1. Upload qua Web UI

**Endpoint:** `POST /api/v1/users/assets/upload-images`

```
User Upload File
    ↓
Xác định Project (theo project_slug hoặc default)
    ↓
Xác định/Tạo Folder (theo folder_slug path hoặc default)
    ↓
Lưu file vào: uploads/{project_slug}/{folder_path}/{filename}
    ↓
Tạo Asset record trong DB
    ↓
🔥 TỰ ĐỘNG: Nếu là IMAGE → Tạo Embedding
    ├─ Extract CLIP vector (512 dims)
    ├─ Lưu vào bảng embeddings (project_id, folder_id, embedding)
    └─ Add vào FAISS index của project
    ↓
Trả về response
```

**Code:**
```python
# backend/api/routes/user_assets.py

@router.post("/upload-images")
async def upload_assets(...):
    # 1. Lưu asset
    asset_id = add_asset(
        session=session,
        user_id=current_user.id,
        folder_id=folder_id,
        path=object_path,
        ...
    )
    
    # 2. 🔥 TỰ ĐỘNG TẠO EMBEDDING cho ảnh
    if file.content_type.startswith("image/"):
        embedding = create_embedding_for_asset(
            session=session,
            asset_id=asset_id,
            image_bytes=file_bytes
        )
        # ✅ Đã lưu vào DB và FAISS
```

### 2. Upload qua External API

**Endpoint:** `POST /api/v1/external/assets/upload`

```
External Client (API Key + Signature)
    ↓
Xác thực API Key và Signature
    ↓
Lấy Project từ API Client
    ↓
Xác định/Tạo Folder
    ↓
Lưu file vào: uploads/{user_id}/{project_id}/{folder_name}/{filename}
    ↓
Tạo Asset record trong DB
    ↓
🔥 TỰ ĐỘNG: Nếu là IMAGE → Tạo Embedding
    ├─ Extract CLIP vector (512 dims)
    ├─ Lưu vào bảng embeddings (project_id, folder_id, embedding)
    └─ Add vào FAISS index của project
    ↓
Trả về response
```

**Code:**
```python
# backend/api/routes/external_assets.py

@router.post("/upload")
async def upload_asset_external(...):
    # 1. Lưu asset
    asset_id = add_asset(
        session=session,
        user_id=client.user_id,
        folder_id=folder_id,
        url=object_path,
        ...
    )
    
    # 2. 🔥 TỰ ĐỘNG TẠO EMBEDDING cho ảnh
    if file.content_type.startswith("image/"):
        embedding = create_embedding_for_asset(
            session=session,
            asset_id=asset_id,
            image_bytes=file_bytes
        )
        # ✅ Đã lưu vào DB và FAISS
```

## Cơ chế tự động

### `create_embedding_for_asset()` 

File: `backend/db/crud_embedding.py`

```python
def create_embedding_for_asset(
    session: Session,
    asset_id: int,
    image_bytes: bytes
) -> Optional[Embeddings]:
    """
    Tự động:
    1. Lấy asset info (để biết folder_id)
    2. Lấy folder info (để biết project_id)
    3. Convert bytes → PIL Image
    4. Extract CLIP embedding vector (512 dims)
    5. Lưu vào DB: embeddings(asset_id, project_id, folder_id, embedding)
    6. Đồng bộ vào FAISS: PROJECT_INDICES[project_id]
    """
    # Lấy asset → folder → project
    asset = session.get(Assets, asset_id)
    folder = session.get(Folders, asset.folder_id)
    project_id = folder.project_id
    
    # Tạo embedding
    image = Image.open(io.BytesIO(image_bytes))
    embedding_vector = embed_image(image)  # CLIP
    
    # Lưu vào DB + FAISS
    embedding = add_embedding_to_db(
        session=session,
        asset_id=asset_id,
        project_id=project_id,
        folder_id=asset.folder_id,
        embedding_vector=embedding_vector
    )
    
    return embedding
```

## Database Schema

### Bảng `embeddings`

```sql
CREATE TABLE embeddings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    asset_id INT NOT NULL,                    -- FK → assets.id
    project_id INT NOT NULL,                  -- FK → projects.id (INDEX)
    folder_id INT,                            -- FK → folders.id (INDEX, NULLABLE)
    embedding TEXT NOT NULL,                  -- JSON array [512 floats]
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_project_id (project_id),        -- Tìm kiếm theo project nhanh
    INDEX idx_folder_id (folder_id),          -- Filter theo folder nhanh
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL
);
```

### Ví dụ record:

```json
{
  "id": 123,
  "asset_id": 456,
  "project_id": 1,
  "folder_id": 5,
  "embedding": "[0.123, -0.456, 0.789, ..., 0.234]",  // 512 floats
  "created_at": "2024-01-15 10:30:00"
}
```

## Lưu ý quan trọng

### ✅ Chỉ tạo embedding cho IMAGE

```python
if file.content_type.startswith("image/"):
    create_embedding_for_asset(...)
```

Video files KHÔNG tạo embedding (vì CLIP chỉ hỗ trợ ảnh).

### ✅ Error Handling

Nếu embedding creation FAILED:
- ❌ KHÔNG block upload
- ✅ Upload vẫn thành công
- ⚠️ Log warning
- 🔄 Có thể rebuild sau bằng API

```python
try:
    embedding = create_embedding_for_asset(...)
    if embedding:
        print("✅ Created embedding")
    else:
        print("⚠️ Failed to create embedding")
except Exception as e:
    # Không raise error, chỉ log
    print(f"⚠️ Embedding failed: {e}")
    # Upload vẫn OK!
```

### ✅ Tự động đồng bộ FAISS

Khi tạo embedding, tự động add vào FAISS:

```python
def add_embedding_to_db(...):
    # Lưu DB
    embedding = Embeddings(...)
    session.add(embedding)
    session.commit()
    
    # 🔥 Tự động add vào FAISS
    add_vector_to_project(
        project_id=project_id,
        asset_id=asset_id,
        folder_id=folder_id,
        embedding=embedding_vector
    )
```

## Folder Structure

```
uploads/
├── {user_id}/
│   ├── {project_id}/
│   │   ├── {folder_name}/
│   │   │   ├── abc123.jpg      ← File storage
│   │   │   ├── def456.png
│   │   │   └── ...
```

**Ví dụ:**
```
uploads/
├── 1/                    # user_id = 1
│   ├── 10/               # project_id = 10
│   │   ├── photos/       # folder_name = "photos"
│   │   │   ├── a1b2c3.jpg
│   │   │   └── d4e5f6.png
│   │   ├── screenshots/  # folder_name = "screenshots"
│   │   │   └── g7h8i9.png
```

## Testing

### Test Upload Flow

```bash
# 1. Upload ảnh
curl -X POST "http://localhost:8000/api/v1/users/assets/upload-images" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "folder_name=my_photos" \
  -F "is_private=false"

# Response:
{
  "status": 1,
  "data": [
    {
      "id": 123,
      "path": "1/10/my_photos/abc123.jpg",
      ...
    }
  ]
}

# 2. Kiểm tra embedding đã được tạo
# Check logs:
# ✅ Created embedding for asset 123

# 3. Test search ngay
curl -X POST "http://localhost:8000/api/v1/search/text" \
  -d "query=sunset" \
  -d "project_id=10" \
  -d "k=10"
```

### Kiểm tra trong Database

```sql
-- Kiểm tra embedding đã được tạo
SELECT 
    e.id,
    e.asset_id,
    e.project_id,
    e.folder_id,
    a.name,
    LENGTH(e.embedding) as embedding_length
FROM embeddings e
JOIN assets a ON e.asset_id = a.id
WHERE e.project_id = 10;
```

## Troubleshooting

### Issue: Embedding không được tạo

**Check:**
1. File có phải là IMAGE không? (`content_type.startswith("image/")`)
2. CLIP model đã load? Check logs khi startup
3. File bytes có valid? Try open với PIL

**Debug:**
```python
# Thêm logging
print(f"File type: {file.content_type}")
print(f"File size: {len(file_bytes)}")

try:
    img = Image.open(io.BytesIO(file_bytes))
    print(f"Image size: {img.size}")
except Exception as e:
    print(f"Invalid image: {e}")
```

### Issue: FAISS index empty

**Solution:** Rebuild index
```bash
curl -X POST "http://localhost:8000/api/v1/search/rebuild" \
  -d "project_id=10"
```

### Issue: Search không trả về kết quả

**Check:**
1. Project có embeddings? `GET /api/v1/search/stats/{project_id}`
2. FAISS index đã được load?
3. Folder_id filter đúng không?

---

**Summary:** Mỗi khi upload ảnh → Tự động tạo embedding → Tự động lưu vào DB + FAISS → Sẵn sàng search! 🚀
