# PhotoStore Frontend - Local Development Setup

## 🚀 Cách chạy Frontend (Local Development)

### 1. Cài đặt dependencies

```bash
cd frontend
npm install
```

### 2. Cấu hình môi trường

File `.env.local` đã được tạo sẵn với cấu hình mặc định:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=/api/v1

# Keycloak Configuration  
VITE_KEYCLOAK_URL=http://localhost:8080/
VITE_KEYCLOAK_REALM=photostore_realm
VITE_KEYCLOAK_CLIENT_ID=photostore-client

# App Configuration
VITE_APP_TITLE=PhotoStore
```

**Lưu ý:** File `.env.local` được dùng cho development và đã được gitignore tự động.

### 3. Đảm bảo Backend đang chạy

Trước khi chạy frontend, đảm bảo backend đã chạy:

```bash
# Từ thư mục gốc, chạy backend với docker
cd backend
docker-compose up -d
```

Backend sẽ chạy trên các ports:
- **Backend API:** http://localhost:8000
- **Keycloak:** http://localhost:8080
- **Adminer:** http://localhost:8081
- **MySQL:** localhost:3306

### 4. Chạy Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:5173**

## 🔧 Cấu hình trong code

Hiện tại các cấu hình Keycloak được hardcode trong `src/keycloak.ts`. Nếu muốn sử dụng biến môi trường, cần cập nhật file này.

### Cập nhật keycloak.ts (Optional)

Để sử dụng biến môi trường, sửa file `src/keycloak.ts`:

```typescript
import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL || "http://localhost:8080/",
  realm: import.meta.env.VITE_KEYCLOAK_REALM || "photostore_realm",
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || "photostore-client",
});

export default keycloak;
```

## 🔐 Thiết lập Keycloak

### 1. Truy cập Keycloak Admin Console

URL: http://localhost:8080
- **Username:** admin
- **Password:** admin

### 2. Tạo Realm mới

- Click dropdown góc trên bên trái (có text "master")
- Click **"Create Realm"**
- **Realm name:** `photostore_realm`
- Click **"Create"**

### 3. Tạo Client cho Frontend

- Vào **Clients** > **"Create client"**
- **Client ID:** `photostore-client`
- **Client type:** OpenID Connect
- Click **"Next"**

**Capability config:**
- ✅ **Client authentication:** OFF
- ✅ **Authorization:** OFF
- ✅ **Standard flow:** ON
- ✅ **Direct access grants:** ON
- Click **"Next"**

**Login settings:**
- **Valid redirect URIs:** 
  - `http://localhost:5173/*`
  - `http://localhost:3000/*`
- **Valid post logout redirect URIs:**
  - `http://localhost:5173/*`
  - `http://localhost:3000/*`
- **Web origins:** 
  - `http://localhost:5173`
  - `http://localhost:3000`
  - `http://localhost:8000`
- Click **"Save"**

### 4. Tạo Admin Client cho Backend

- Vào **Clients** > **"Create client"**
- **Client ID:** `photostore-admin`
- Click **"Next"**

**Capability config:**
- ✅ **Client authentication:** ON
- ✅ **Service accounts roles:** ON
- Click **"Next"**, rồi **"Save"**

**Lấy Client Secret:**
- Vào tab **"Credentials"**
- Copy **"Client secret"** và cập nhật vào `backend/.env`:
  ```
  ADMIN_CLIENT_SECRET=<your-client-secret>
  ```

### 5. Tạo User Test

- Vào **Users** > **"Create new user"**
- Điền thông tin:
  - **Username:** testuser
  - **Email:** test@example.com
  - **First name:** Test
  - **Last name:** User
  - ✅ **Email verified:** ON
  - ✅ **Enabled:** ON
- Click **"Create"**

**Set password:**
- Vào tab **"Credentials"**
- Click **"Set password"**
- **Password:** 123456 (hoặc password bạn muốn)
- **Password confirmation:** 123456
- ❌ **Temporary:** OFF
- Click **"Save"**

## 🧪 Test Login

1. Mở frontend: http://localhost:5173
2. Click vào **"Login"**
3. Đăng nhập với:
   - **Username:** testuser
   - **Password:** 123456

## 📝 Scripts NPM

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 🔍 Troubleshooting

### Lỗi CORS
Nếu gặp lỗi CORS, kiểm tra:
1. Backend `backend/core/config.py` có allow CORS cho `http://localhost:5173`
2. Keycloak client có đúng Web Origins

### Lỗi Keycloak connection
1. Kiểm tra Keycloak đang chạy: `docker ps | grep keycloak`
2. Truy cập http://localhost:8080 để xác nhận
3. Xem logs: `docker logs photostore_keycloak`

### Lỗi "Account is not fully set up"
1. Vào Keycloak Admin Console
2. Tìm user trong **Users**
3. Kiểm tra:
   - ✅ **Enabled:** ON
   - ✅ **Email verified:** ON
4. Vào tab **"Required actions"** và xóa hết các actions
5. Vào tab **"Credentials"** và đặt lại password với **Temporary:** OFF

### Backend không kết nối database
```bash
# Kiểm tra MySQL
docker ps | grep mysql

# Xem logs MySQL
docker logs photostore_mysql

# Restart backend
cd backend
docker-compose restart backend
```

## 📁 Cấu trúc dự án

```
photostore/
├── backend/              # FastAPI backend (Docker)
│   ├── docker-compose.yml
│   └── .env
├── frontend/             # React frontend (Local)
│   ├── .env.local
│   ├── src/
│   └── package.json
└── docker-compose.yml    # Full stack (optional)
```
