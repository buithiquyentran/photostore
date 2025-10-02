# 🚀 PhotoStore - Bắt đầu Test Ngay!

## ✅ Backend đã sẵn sàng!

Database đã được tạo tự động với tất cả bảng:
- ✅ users
- ✅ projects  
- ✅ folders
- ✅ assets
- ✅ embeddings (có project_id, folder_id)

## 🎯 Test trong 3 bước

### Bước 1: Chuẩn bị ảnh test

```powershell
# Tạo folder
mkdir test_images

# Copy 3-5 ảnh vào folder test_images\
# Ví dụ: cat.jpg, dog.jpg, beach.jpg, sunset.jpg
```

### Bước 2: Mở Swagger UI

http://localhost:8000/docs

### Bước 3: Test theo thứ tự

#### 1. Register User
`POST /api/v1/auth/register`
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "first_name": "Test",
  "last_name": "User"
}
```

#### 2. Login
`POST /api/v1/auth/login`
```
username: testuser
password: 123456
```

➡️ **Copy `access_token`**

#### 3. Authorize
- Click nút **"Authorize"** ở góc trên
- Paste token vào
- Click "Authorize"

#### 4. Create Project (Tạo Project đầu tiên)
`POST /api/v1/projects`
```json
{
  "name": "My Photos",
  "description": "Test project for image search",
  "is_default": true
}
```

✅ Lưu `id` của project (ví dụ: `1`)

#### 5. Create Folder (Tùy chọn - hoặc dùng folder_name khi upload)
`POST /api/v1/users/folders/create`
```json
{
  "project_id": 1,
  "name": "vacation_photos",
  "parent_id": null
}
```

✅ Lưu `id` của folder (ví dụ: `1`)

**Lưu ý:** Bạn có thể bỏ qua bước này và dùng `folder_name` khi upload, hệ thống sẽ tự tạo folder.

#### 6. Upload Images
`POST /api/v1/users/assets/upload-images`
- files: [chọn 3-5 ảnh từ test_images]
- folder_name: test_photos
- is_private: false

Click **"Execute"**

✅ Check response có `"status": 1`

#### 7. Check Logs (Optional)
```powershell
docker-compose logs backend | Select-String "embedding"
```

Phải thấy:
```
✅ Created embedding for asset 1
[FAISS] Added asset 1 to project 1, total vectors: 1
✅ Created embedding for asset 2
[FAISS] Added asset 2 to project 1, total vectors: 2
```

#### 8. Check Search Stats
`GET /api/v1/search/stats/1`

Response:
```json
{
  "project_id": 1,
  "total_vectors": 5,
  "indexed": true,
  "dimension": 512
}
```

#### 9. Search by Text
`POST /api/v1/search/text`
- query: cat
- project_id: 1
- k: 5

Click **"Execute"**

✅ Response trả về danh sách ảnh liên quan đến "cat"!

#### 10. Search by Image
`POST /api/v1/search/image`
- file: [chọn 1 ảnh từ test_images]
- project_id: 1
- k: 5

Click **"Execute"**

✅ Response trả về các ảnh tương tự!

---

## 🎉 Xong!

Bạn vừa test thành công:
- ✅ Upload tự động tạo embeddings
- ✅ Search by text (AI semantic search)
- ✅ Search by image (similarity search)
- ✅ Project-based isolation
- ✅ FAISS vector search

---

## 📊 Check Database

Xem embeddings trong database:

```powershell
docker-compose exec mysql mysql -u photostore_user -pphotostore_pass photostore
```

```sql
SELECT 
    e.id,
    e.asset_id,
    e.project_id,
    e.folder_id,
    a.name,
    LENGTH(e.embedding) as vector_size,
    e.created_at
FROM embeddings e
JOIN assets a ON e.asset_id = a.id;
```

---

## 🐛 Troubleshooting

### Không thấy embeddings được tạo?

```powershell
# Check logs
docker-compose logs backend --tail 50

# Restart backend
docker-compose restart backend
```

### Search không trả về kết quả?

```
# Rebuild index qua Swagger UI
POST /api/v1/search/rebuild
project_id: 1
```

### Lỗi khác?

Check logs:
```powershell
docker-compose logs backend | Select-String -Pattern "error|Error|ERROR"
```

---

## 📚 Tài liệu chi tiết

- **`backend/TEST-GUIDE.md`** - Hướng dẫn test đầy đủ
- **`QUICK-TEST.md`** - Test nhanh 5 phút
- **`backend/SEARCH-ARCHITECTURE.md`** - Chi tiết architecture
- **`backend/README-EMBEDDINGS.md`** - Hướng dẫn sử dụng

---

## 🎯 URLs quan trọng

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Adminer (DB UI):** http://localhost:8081
  - Server: mysql
  - User: photostore_user
  - Password: photostore_pass
  - Database: photostore
- **Keycloak:** http://localhost:8080
  - Admin: admin / admin

---

**Happy Testing! 🎉**
