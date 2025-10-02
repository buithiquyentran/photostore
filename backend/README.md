# 🚀 PhotoStore Backend - Docker Setup

Backend API cho hệ thống PhotoStore với FastAPI, MySQL, Keycloak và tìm kiếm ảnh bằng AI.

## 📦 Các thành phần

- **Backend (FastAPI)**: API server với AI-powered image search
- **MySQL 8.0**: Database chính
- **Adminer**: Web UI quản lý database
- **Keycloak**: Identity và Access Management

## 🏃 Quick Start

### 1. Chuẩn bị file `.env`

```bash
cd backend
cp env.example .env
# Chỉnh sửa .env nếu cần (mặc định đã OK cho local)
```

### 2. Khởi động tất cả services

```bash
docker-compose up -d
```

### 3. Kiểm tra services đã chạy

```bash
docker-compose ps
```

## 📍 Endpoints

| Service | URL | Mô tả |
|---------|-----|-------|
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Adminer | http://localhost:8081 | Database management |
| Keycloak | http://localhost:8080 | IAM console |

## 🔐 Cấu hình Keycloak

### 1. Truy cập Keycloak Admin

- URL: http://localhost:8080
- Username: `admin`
- Password: `admin`

### 2. Tạo Realm

1. Click dropdown "master" → "Create Realm"
2. Realm name: `photostore_realm`
3. Click "Create"

### 3. Tạo Client

1. Vào "Clients" → "Create client"
2. **Client ID**: `photostore_client`
3. **Client authentication**: ON
4. **Valid redirect URIs**: `http://localhost:3000/*`
5. **Web origins**: `http://localhost:3000`
6. Save

### 4. Lấy Client Secret

1. Vào Client `photostore_client` → Tab "Credentials"
2. Copy **Client secret**
3. Cập nhật vào file `.env`:
   ```env
   ADMIN_CLIENT_SECRET=<client-secret-vừa-copy>
   ```
4. Restart backend: `docker-compose restart backend`

### 5. Tạo Client Roles

1. Vào Client `photostore_client` → Tab "Roles"
2. Tạo 2 roles: `admin` và `user`

### 6. Tạo Test User

1. Vào "Users" → "Create new user"
2. **Username**: `testuser`
3. **Email**: `test@example.com`
4. **Email verified**: ON
5. Tab "Credentials" → Set password: `Test@123`
6. **Temporary**: OFF
7. Tab "Role mapping" → Assign roles: `admin`, `user`

## 🗄️ Quản lý Database

### Truy cập Adminer

- URL: http://localhost:8081
- **System**: MySQL
- **Server**: `mysql`
- **Username**: `photostore_user`
- **Password**: `photostore_pass`
- **Database**: `photostore`

### Kết nối trực tiếp MySQL

```bash
docker-compose exec mysql mysql -u photostore_user -p photostore
# Password: photostore_pass
```

## 🔧 Các lệnh hữu ích

```bash
# Khởi động services
docker-compose up -d

# Xem logs
docker-compose logs -f
docker-compose logs -f backend

# Dừng services
docker-compose down

# Dừng và xóa data
docker-compose down -v

# Restart một service
docker-compose restart backend

# Rebuild và start lại
docker-compose up -d --build

# Vào shell container
docker-compose exec backend bash

# Xem trạng thái
docker-compose ps
```

## 🐛 Troubleshooting

### Port đã được sử dụng

```bash
# Kiểm tra port đang dùng
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # macOS/Linux

# Đổi port trong docker-compose.yml
ports:
  - "8001:8000"  # host:container
```

### Backend không connect được MySQL

```bash
# Kiểm tra MySQL đã ready
docker-compose exec mysql mysqladmin ping -h localhost

# Xem logs MySQL
docker-compose logs mysql

# Restart backend
docker-compose restart backend
```

### Keycloak không khởi động

```bash
# Xem logs
docker-compose logs keycloak

# Keycloak cần 30-60s để khởi động
# Kiểm tra MySQL đã chạy trước
docker-compose ps mysql
```

## 📊 Database Schema

Tables chính:
- `users` - Người dùng
- `projects` - Dự án
- `folders` - Thư mục
- `assets` - Ảnh và metadata
- `embeddings` - Vector embeddings cho AI search
- `refresh_token` - Authentication tokens

## 🤖 AI Features

- **CLIP Model**: Encode ảnh và text thành vectors
- **FAISS Index**: Tìm kiếm similarity nhanh
- **Semantic Search**: Tìm ảnh bằng ngôn ngữ tự nhiên

Ví dụ: "a cat on sofa", "sunset beach", "people playing football"

## 📚 Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL databases in Python
- **PyTorch + CLIP** - AI/ML for image search
- **FAISS** - Vector similarity search
- **MySQL 8.0** - Database
- **Keycloak** - Authentication & Authorization

## 🔒 Security Notes

1. Đổi passwords trong `.env` khi deploy production
2. Không commit file `.env` vào git
3. Sử dụng HTTPS trong production
4. Thường xuyên update Docker images

## 📝 Environment Variables

Xem file `env.example` để biết các biến cần thiết:

- `DATABASE_URL`: MySQL connection string
- `SECRET_KEY`: JWT secret key
- `KEYCLOAK_URL`: Keycloak realm URL
- `CLIENT_ID`: Keycloak client ID
- Và nhiều hơn nữa...

---

**Happy Coding! 🎉**
