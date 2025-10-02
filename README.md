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

### 🔒 Bảo mật
- Keycloak Authentication
- Project-based Access Control
- API Key & Secret cho external access

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

**Frontend:**
- Next.js / React - UI framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Vite - Build tool

## 📚 Documentation

- [Backend Setup Guide](backend/README.md) - Hướng dẫn setup backend với Docker
- [API Documentation](http://localhost:8000/docs) - Swagger UI (sau khi chạy backend)
- [Image Search Guide](backend/README-EMBEDDINGS.md) - Hướng dẫn sử dụng AI Search
- [Upload Flow](backend/UPLOAD-FLOW.md) - Chi tiết về upload và auto-embedding

## 📝 API Examples

### Upload ảnh (GraphQL-style response)
```bash
POST /api/v1/users/assets/upload-images
Content-Type: multipart/form-data

files: [photo.jpg]
folder_slug: thu-muc-cha/thu-muc-con  # Hỗ trợ nested folders
project_slug: my-project  # Optional: Chỉ định project
is_private: false

Response:
{
  "data": {
    "uploadFile": {
      "file": {
        "id": 123,
        "name": "photo.jpg",
        "file_url": "http://localhost:8000/uploads/my-project/thu-muc-cha/thu-muc-con/abc123.jpg",
        "file_extension": "jpg",
        "file_type": "image/jpeg",
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
  },
  "extensions": {
    "cost": {
      "requestedQueryCost": 0,
      "maximumAvailable": 50000
    }
  }
}
```

### Tìm kiếm ảnh
```bash
# Tìm bằng text
POST /api/v1/search/text
query: "cat sitting on sofa"
k: 5

# Tìm bằng ảnh tương tự
POST /api/v1/search/image
file: [upload ảnh]
k: 5
```

## 🔐 Default Credentials

**Keycloak:**
- URL: http://localhost:8080
- Admin: `admin` / `admin`

**Adminer (Database UI):**
- URL: http://localhost:8081
- Server: `mysql`
- User: `photostore_user`
- Password: `photostore_pass`


