# 🔧 Setup admin-cli Client - Hướng dẫn từng bước

## Bước 1: Tìm client admin-cli

1. Keycloak Admin Console: http://localhost:8080
2. Login: admin / admin
3. Chọn realm: **photostore_realm** (dropdown góc trái)
4. Menu bên trái → **Clients**
5. Trong danh sách, tìm client tên **"admin-cli"**
6. Click vào **admin-cli**

## Bước 2: Enable Client Authentication

Tab **"Settings"**:

Tìm và BẬT các options sau:

```
Client authentication: ON  ← Kéo switch sang ON
Service accounts roles: ON  ← Kéo switch sang ON

Standard flow: OFF (giữ nguyên)
Direct access grants: OFF (giữ nguyên)
Implicit flow: OFF (giữ nguyên)
```

→ Scroll xuống, click **"Save"**

## Bước 3: Assign Roles

Tab **"Service Account Roles"**:

1. Click button **"Assign role"**
2. Một modal popup hiện ra
3. Click dropdown **"Filter by clients"**
4. Chọn **"realm-management"** từ dropdown
5. Tích chọn các roles sau:
   - ✅ manage-users
   - ✅ view-users
   - ✅ query-users
6. Click button **"Assign"** (màu xanh)

## Bước 4: Lấy Client Secret

Tab **"Credentials"**:

1. Bạn sẽ thấy field **"Client secret"**
2. Click icon 👁️ (eye) để hiện secret
3. Click icon 📋 (copy) để copy
4. Secret sẽ có dạng: `abc123xyz-456def-789ghi...` (rất dài)

## Bước 5: Cập nhật .env

Mở file `backend/.env`:

```env
# Client cho user login (public)
CLIENT_ID=photostore_client
# hoặc CLIENT_ID=photostore_realm (nếu dùng cái có sẵn)

# Client cho admin operations (confidential)
ADMIN_CLIENT_ID=admin-cli
ADMIN_CLIENT_SECRET=<paste-secret-vừa-copy>
```

## Bước 6: Restart Backend

```bash
cd backend
docker-compose restart backend
```

## ✅ Verify

Check logs để đảm bảo không có lỗi:

```bash
docker-compose logs backend --tail=20
```

Nếu thấy "Application startup complete" là thành công!

---

## 🎯 Tóm tắt file .env cuối cùng:

```env
# Database
DATABASE_URL=mysql+pymysql://photostore_user:photostore_pass@mysql:3306/photostore

# Keycloak
KEYCLOAK_URL=http://keycloak:8080/realms/photostore_realm
CLIENT_ID=photostore_client
ADMIN_CLIENT_ID=admin-cli
ADMIN_CLIENT_SECRET=abc123...xyz789  ← Secret từ admin-cli

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## ❌ Lỗi thường gặp:

### "unauthorized_client"
**Nguyên nhân**: CLIENT_ID hoặc ADMIN_CLIENT_ID sai
**Fix**: Đảm bảo dùng tên CLIENT chứ không phải tên REALM

### "invalid_client_credentials"  
**Nguyên nhân**: ADMIN_CLIENT_SECRET sai hoặc admin-cli chưa enable Client authentication
**Fix**: Làm lại Bước 2 và Bước 4

### "insufficient_scope"
**Nguyên nhân**: admin-cli chưa có roles manage-users
**Fix**: Làm lại Bước 3
