# PhotoStore - Hệ thống Quản lý và Tìm kiếm Ảnh

Hệ thống quản lý ảnh với tính năng tìm kiếm thông minh sử dụng AI.

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
- FastAPI (Python)
- MySQL
- Keycloak (Authentication)
- CLIP + FAISS (AI Image Search)

**Frontend:**
- Next.js / React
- TypeScript
- Tailwind CSS

## 📚 Documentation

- [Backend Setup Guide](backend/README.md) - Hướng dẫn setup backend với Docker
- [API Documentation](http://localhost:8000/docs) - Swagger UI (sau khi chạy backend)

## 🔐 Default Credentials

**Keycloak:**
- URL: http://localhost:8080
- Admin: `admin` / `admin`

**Adminer (Database UI):**
- URL: http://localhost:8081
- Server: `mysql`
- User: `photostore_user`
- Password: `photostore_pass`


