# 🔍 PhotoStore Search Architecture

## Overview

Hệ thống tìm kiếm ảnh sử dụng **CLIP** (Contrastive Language-Image Pre-training) và **FAISS** (Facebook AI Similarity Search) để tìm kiếm ảnh bằng:
- **Ảnh tương tự** (Image similarity search)
- **Text query** (Semantic text-to-image search)

## Architecture Design

### 1. **Project-based FAISS Index**

Mỗi project có 1 FAISS index riêng biệt:

```
Project 1 → FAISS Index 1 → [vector_1, vector_2, ..., vector_n]
Project 2 → FAISS Index 2 → [vector_1, vector_2, ..., vector_m]
Project 3 → FAISS Index 3 → [vector_1, vector_2, ..., vector_k]
```

**Lợi ích:**
- ✅ Tìm kiếm nhanh hơn (search trong scope nhỏ)
- ✅ Isolation giữa các projects
- ✅ Dễ quản lý và maintain
- ✅ Scale tốt khi có nhiều projects

### 2. **Database Schema**

```sql
-- Bảng embeddings
embeddings:
  - id: int (PK)
  - asset_id: int (FK → assets.id)
  - project_id: int (FK → projects.id, INDEXED)
  - folder_id: int (FK → folders.id, INDEXED, NULLABLE)
  - embedding: text (JSON array of 512 floats)
  - created_at: datetime

-- Indexes
INDEX idx_project_id ON embeddings(project_id)
INDEX idx_folder_id ON embeddings(folder_id)
```

### 3. **FAISS Index Management**

**In-memory storage:**
```python
PROJECT_INDICES = {
    project_id: faiss.Index
}

PROJECT_FAISS_MAP = {
    project_id: {
        faiss_id: (asset_id, folder_id)
    }
}

PROJECT_ASSET_MAP = {
    project_id: {
        asset_id: faiss_id
    }
}
```

### 4. **CLIP Model**

- **Model:** `ViT-B/32`
- **Embedding dimension:** 512
- **Normalization:** L2 normalized vectors
- **Similarity:** Cosine similarity (Inner Product)

## Workflow

### 🔼 Upload Image Flow

```mermaid
graph LR
    A[Upload Image] --> B[Save to Storage]
    B --> C[Create Asset Record]
    C --> D[Extract CLIP Embedding]
    D --> E[Save to DB]
    E --> F[Add to FAISS Index]
```

**Code:**
```python
# 1. Upload image
asset_id = add_asset(session, ...)

# 2. Create embedding
embedding = create_embedding_for_asset(
    session=session,
    asset_id=asset_id,
    image_bytes=file_bytes
)

# Tự động:
# - Embed image với CLIP
# - Lưu vào DB (project_id, folder_id)
# - Add vào FAISS index của project
```

### 🔍 Search Flow

#### Search by Image:
```mermaid
graph LR
    A[Upload Query Image] --> B[Extract CLIP Embedding]
    B --> C[Search in Project FAISS]
    C --> D[Filter by Folder if needed]
    D --> E[Return Asset IDs]
    E --> F[Query DB for Details]
```

#### Search by Text:
```mermaid
graph LR
    A[Text Query] --> B[Extract CLIP Embedding]
    B --> C[Search in Project FAISS]
    C --> D[Filter by Folder if needed]
    D --> E[Return Asset IDs]
    E --> F[Query DB for Details]
```

**Code:**
```python
# Search by image
assets = search_by_image(
    session=session,
    project_id=1,
    image=pil_image,
    k=10,
    folder_id=5  # optional
)

# Search by text
assets = search_by_text(
    session=session,
    project_id=1,
    query_text="a cat on the sofa",
    k=10,
    folder_id=5  # optional
)
```

### 🗑️ Delete Image Flow

```mermaid
graph LR
    A[Delete Asset] --> B[Delete from DB]
    B --> C[Remove from FAISS Index]
```

**Code:**
```python
delete_embedding_for_asset(session, asset_id)

# Tự động:
# - Xóa record trong DB
# - Mark as deleted trong FAISS mapping
```

## API Endpoints

### 1. Search by Image
```http
POST /api/v1/search/image
Content-Type: multipart/form-data

file: <image_file>
project_id: 1
folder_id: 5  # optional
k: 10  # number of results
```

**Response:**
```json
{
  "status": 1,
  "data": [
    {
      "id": 123,
      "name": "photo.jpg",
      "path": "uploads/...",
      "width": 1920,
      "height": 1080,
      "folder_id": 5
    },
    ...
  ],
  "total": 10,
  "query_type": "image"
}
```

### 2. Search by Text
```http
POST /api/v1/search/text
Content-Type: application/x-www-form-urlencoded

query=a cat on the sofa
project_id=1
folder_id=5  # optional
k=10
```

**Response:**
```json
{
  "status": 1,
  "data": [...],
  "total": 10,
  "query": "a cat on the sofa",
  "query_type": "text"
}
```

### 3. Rebuild Index
```http
POST /api/v1/search/rebuild

project_id=1
```

**Use cases:**
- Sau khi restore database
- Khi FAISS index bị lỗi
- Sau migration

### 4. Get Stats
```http
GET /api/v1/search/stats/{project_id}
```

**Response:**
```json
{
  "project_id": 1,
  "total_vectors": 1523,
  "indexed": true,
  "dimension": 512
}
```

## Synchronization Mechanisms

### 1. **Auto-sync on Upload**

Khi upload ảnh, tự động tạo embedding:

```python
# Trong upload_assets endpoint
asset_id = add_asset(session, ...)
create_embedding_for_asset(session, asset_id, file_bytes)
```

### 2. **Auto-sync on Delete**

Khi xóa ảnh, tự động xóa embedding:

```python
# Trong delete_asset endpoint
delete_embedding_for_asset(session, asset_id)
```

### 3. **Manual Rebuild**

Rebuild toàn bộ index từ database:

```python
rebuild_project_embeddings(session, project_id)
```

## Performance Considerations

### 1. **FAISS Index Type**

Sử dụng `IndexFlatIP` (Inner Product):
- ✅ Exact search (100% accurate)
- ✅ Simple và reliable
- ⚠️ O(n) complexity
- ⚠️ Không scale cho >1M vectors

**Scale options:**
- `IndexIVFFlat`: Faster, approximate
- `IndexHNSWFlat`: Faster, high recall

### 2. **Caching**

- CLIP model được cache với `@lru_cache()`
- FAISS indices lưu trong memory
- No disk persistence (rebuild on restart)

### 3. **Optimization Tips**

**For Large Projects (>100K images):**
```python
# Sử dụng IVF index
nlist = 100  # số clusters
quantizer = faiss.IndexFlatIP(DIM)
index = faiss.IndexIVFFlat(quantizer, DIM, nlist)

# Train với sample data
index.train(sample_vectors)
```

## Folder Filtering

Tìm kiếm có thể filter theo folder:

```python
# Chỉ search trong folder cụ thể
assets = search_by_text(
    session=session,
    project_id=1,
    query_text="sunset",
    folder_id=5  # <-- Filter
)
```

**Implementation:**
- FAISS trả về nhiều kết quả (k * 10)
- Filter theo `folder_id` trong mapping
- Trả về đúng k kết quả cuối cùng

## Example Usage

### Complete Upload + Search Flow

```python
# 1. Upload images to project
from db.crud_asset import add_asset
from db.crud_embedding import create_embedding_for_asset

for file in files:
    # Save asset
    asset_id = add_asset(
        session=session,
        user_id=user_id,
        folder_id=folder_id,
        path=path,
        name=name,
        ...
    )
    
    # Create embedding (auto-sync to FAISS)
    create_embedding_for_asset(
        session=session,
        asset_id=asset_id,
        image_bytes=file_bytes
    )

# 2. Search by text
from services.search.embeddings_service import search_by_text

results = search_by_text(
    session=session,
    project_id=project_id,
    query_text="beautiful sunset on the beach",
    k=20
)

# 3. Search by similar image
from services.search.embeddings_service import search_by_image

results = search_by_image(
    session=session,
    project_id=project_id,
    image=query_image,
    k=20,
    folder_id=folder_id  # optional filter
)
```

## Troubleshooting

### Issue: Index empty after restart
**Solution:** FAISS indices are in-memory. Rebuild on startup:
```python
@app.on_event("startup")
def load_indices():
    for project in session.exec(select(Projects)).all():
        rebuild_project_embeddings(session, project.id)
```

### Issue: Search results không chính xác
**Solution:** 
1. Check CLIP model đã load đúng
2. Verify vectors đã được normalized
3. Rebuild index nếu cần

### Issue: Slow search
**Solution:**
1. Giảm k (số kết quả)
2. Sử dụng IVF index cho large datasets
3. Add hardware (GPU for CLIP)

## Future Improvements

- [ ] Persistent FAISS indices (save to disk)
- [ ] Background embedding generation
- [ ] Batch embedding creation
- [ ] GPU acceleration for CLIP
- [ ] Advanced FAISS indices (IVF, HNSW)
- [ ] Multi-modal search (image + text combined)
- [ ] Search result ranking/filtering
- [ ] Analytics và search logs

---

**Happy Searching! 🔍**
