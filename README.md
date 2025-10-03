# PhotoStore - Hệ thống Quản lý và Tìm kiếm Ảnh

Hệ thống quản lý ảnh với tính năng tìm kiếm thông minh sử dụng AI.

## ✨ Tính năng chính

### 🔍 Tìm kiếm thông minh
- Tìm kiếm bằng ảnh tương tự (AI Similarity Search)
- Tìm kiếm bằng text mô tả (Semantic Search)
- Tự động tạo embeddings cho ảnh upload

### 📂 Quản lý thư mục thông minh
- Tự động tạo URL-friendly slugs (ví dụ: "Thư mục của Bảo" → "thu-muc-cua-bao")
- Hỗ trợ tiếng Việt trong slugs
- Phân cấp thư mục: `thu-muc-cha/thu-muc-con/anh.jpg`

### 🔒 Bảo mật & Quyền truy cập
- **Keycloak Authentication**: Đăng nhập SSO cho users
- **Project-based Access Control**: Mỗi user có nhiều projects riêng biệt
- **External API**: API key & secret cho third-party integration
- **File Access Control**:
  + Public files: Truy cập trực tiếp qua URL
  + Private files: Yêu cầu token và kiểm tra ownership
- **HMAC Signature**: Bảo mật API calls với chữ ký số đơn giản

### 🚀 API Hiện đại
- RESTful API với GraphQL-style responses
- Swagger UI Documentation
- Automatic embedding generation

## 📁 Cấu trúc Project

```
photostore/
├── backend/              # FastAPI Backend + Docker setup
│   ├── api/             # API routes
│   ├── core/            # Core configuration
│   ├── db/              # Database models & CRUD
│   ├── models/          # SQLModel models
│   ├── services/        # Business logic
│   ├── docker-compose.yml    # Docker orchestration
│   └── README.md        # Backend documentation
│
└── frontend/            # Frontend (Next.js/React)
    └── ...
```

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
cp env.example .env
docker-compose up -d
```

Chi tiết xem: [backend/README.md](backend/README.md)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🛠️ Công nghệ

**Backend:**
- FastAPI (Python) - Web framework
- MySQL - Database
- SQLModel - ORM với type hints
- Keycloak - Authentication & Authorization
- CLIP - AI model cho image/text embeddings
- FAISS - Vector similarity search
- Docker - Containerization
- File Storage:
  + Local storage với URL-friendly paths
  + Access control middleware
  + Automatic file organization

**Frontend:**
- Next.js / React - UI framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Vite - Build tool

## 📚 Documentation

- [Backend Setup Guide](backend/README.md) - Hướng dẫn setup backend với Docker
- [API Documentation](http://localhost:8000/docs) - Swagger UI (sau khi chạy backend)
- [External API Guide](backend/EXTERNAL-API.md) - **API key authentication cho third-party**
- [Simple API Guide](backend/SIMPLE-API-GUIDE.md) - **Phiên bản đơn giản hóa của External API**
- [API Signature Generator](backend/README-API-SIGNATURE.md) - **Công cụ tạo signature cho API**
- [Image Search Guide](backend/README-EMBEDDINGS.md) - Hướng dẫn sử dụng AI Search
- [Upload Flow](backend/UPLOAD-FLOW.md) - Chi tiết về upload và auto-embedding
- [Folder Structure](backend/FOLDER-STRUCTURE.md) - Cấu trúc thư mục và file access control

## 📝 API Examples

### Upload & Truy cập file
```bash
# Upload file
POST /api/v1/users/assets/upload-images
Content-Type: multipart/form-data

files: [photo.jpg]
folder_slug: thu-muc-cha/thu-muc-con  # Hỗ trợ nested folders
project_slug: my-project  # Optional: Chỉ định project
is_private: false  # true = private, false = public

Response:
{
  "data": {
    "uploadFile": {
      "file": {
        "id": 123,
        "name": "photo.jpg",  # Original filename
        "system_name": "abc123.jpg",  # UUID filename
        "file_url": "http://localhost:8000/uploads/my-project/thu-muc-cha/thu-muc-con/abc123.jpg",
        "file_extension": "jpg",
        "file_type": "image/jpeg",
        "format": "image/jpeg",
        "file_size": 352525,
        "width": 800,
        "height": 600,
        "project_slug": "my-project",
        "folder_path": "my-project/thu-muc-cha/thu-muc-con",  # Full path với slugs
        "is_private": false,
        "created_at": 1759373976,
        "updated_at": 1759373976
      },
      "message": "File uploaded successfully",
      "result": true
    }
  }
}

# Truy cập file public (is_private = false)
GET /uploads/my-project/thu-muc-cha/thu-muc-con/abc123.jpg
# -> Truy cập trực tiếp, không cần token

# Truy cập file private (is_private = true)
GET /api/v1/uploads/my-project/thu-muc-cha/thu-muc-con/abc123.jpg
Authorization: Bearer YOUR_TOKEN
# -> Yêu cầu token và kiểm tra ownership
```

### Tìm kiếm ảnh
```bash
# Tìm bằng text (User API - cần Keycloak token)
POST /api/v1/search/text
Authorization: Bearer YOUR_TOKEN
query: "cat sitting on sofa"
k: 5

# Tìm bằng ảnh tương tự (User API - cần Keycloak token)
POST /api/v1/search/image
Authorization: Bearer YOUR_TOKEN
file: [upload ảnh]
k: 5
```

### External API (Third-party Integration)
```bash
# Lấy API credentials
GET /api/v1/projects/123/api-key
Authorization: Bearer YOUR_KEYCLOAK_TOKEN

Response:
{
  "api_key": "pk_xxx",
  "api_secret": "sk_xxx"
}

# Tạo folder (External API - Đơn giản hóa)
POST /api/v1/external/folders
X-API-Key: pk_xxx
X-Timestamp: 1696204800
X-Signature: hmac_sha256(timestamp:api_key, api_secret)
Content-Type: application/json

{
  "name": "thư mục của bảo",
  "parent_id": null
}

# Search bằng text (External API - Đơn giản hóa)
POST /api/v1/external/search/text
X-API-Key: pk_xxx
X-Timestamp: 1696204800
X-Signature: hmac_sha256(timestamp:api_key, api_secret)

query: cat sitting on sofa
k: 5
```

Chi tiết xem: [Simple API Guide](backend/SIMPLE-API-GUIDE.md)

## 🔐 Default Credentials

**Keycloak:**
- URL: http://localhost:8080
- Admin: `admin` / `admin`

**Adminer (Database UI):**
- URL: http://localhost:8081
- Server: `mysql`
- User: `photostore_user`
- Password: `photostore_pass`


