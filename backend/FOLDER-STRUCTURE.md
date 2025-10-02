# 📂 Folder Structure Guide

## Tổng quan

Hệ thống sử dụng cấu trúc thư mục thông minh với:
- 🔄 Tự động tạo slugs từ tên thư mục
- 🌳 Hỗ trợ nested folders không giới hạn độ sâu
- 🔍 URL-friendly paths cho SEO

## Cấu trúc

```
projects/
├── my-project/                  # project.slug
│   ├── thu-muc-cha/            # folder.slug (parent)
│   │   └── thu-muc-con/        # folder.slug (child)
│   │       └── abc123.jpg      # Ảnh upload
│   └── default/                # Default folder (tự động tạo)
└── another-project/
    └── ...
```

## Slugs

### 1. Project Slugs
- Tự động tạo từ project name
- Unique trong phạm vi user
- Ví dụ: "My Project 2024" → "my-project-2024"

### 2. Folder Slugs
- Tự động tạo từ folder name
- Unique trong cùng level (parent)
- Hỗ trợ tiếng Việt
- Ví dụ: "Thư mục của Bảo" → "thu-muc-cua-bao"

## Upload API

### 1. Upload vào folder cụ thể
```bash
POST /api/v1/users/assets/upload-images
files: [photo.jpg]
folder_slug: thu-muc-cha/thu-muc-con
project_slug: my-project  # Optional
```

### 2. Upload vào root folder mới
```bash
POST /api/v1/users/assets/upload-images
files: [photo.jpg]
folder_slug: thu-muc-moi  # Tự động tạo nếu chưa có
```

### 3. Upload vào default folder
```bash
POST /api/v1/users/assets/upload-images
files: [photo.jpg]
# Không cần folder_slug, tự động dùng default folder
```

## Response Format

```json
{
  "data": {
    "uploadFile": {
      "file": {
        "file_url": "http://localhost:8000/uploads/my-project/thu-muc-cha/thu-muc-con/abc123.jpg",
        "project_slug": "my-project",
        "folder_path": "my-project/thu-muc-cha/thu-muc-con"
      }
    }
  }
}
```

## Lưu ý

1. **Tạo folder mới:**
   - Chỉ tự động tạo ở root level
   - Nested folders phải tạo từng cấp

2. **Default folder:**
   - Tự động tạo khi cần
   - Slug: "default"
   - Dùng khi không chỉ định folder

3. **Duplicate slugs:**
   - Tự động thêm suffix số
   - Ví dụ: "my-folder", "my-folder-1"

4. **Security:**
   - Validate project ownership
   - Validate parent folder tồn tại
   - Validate folder access rights
