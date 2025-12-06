# Image Editor - Google Photos Style

## ✅ Đã cài đặt:

### **Tính năng:**

- 🎨 **Crop** - Xén ảnh với aspect ratio (Free, 1:1, 4:3, 16:9)
- 🔄 **Rotate** - Xoay ảnh (góc tự do 0-360° hoặc ±90°)
- 🔀 **Flip** - Lật ảnh ngang/dọc
- 🔍 **Zoom** - Zoom in/out (100%-300%)
- 💾 **Save** - Lưu ảnh đã chỉnh sửa và thay thế ảnh cũ

### **Components:**

- `ImageEditor.tsx` - Component chỉnh sửa ảnh
- `ViewerPage.tsx` - Tích hợp nút Edit và xử lý save

### **Libraries:**

- `react-easy-crop` - Professional crop component

## 📖 Cách sử dụng:

### 1. **Mở ảnh trong ViewerPage**

- Click vào bất kỳ ảnh nào trong gallery
- ViewerPage sẽ hiển thị ảnh fullscreen

### 2. **Bắt đầu chỉnh sửa**

- Click nút **Edit** (icon bút chì) ở toolbar phía trên
- Image Editor sẽ mở ra

### 3. **Crop (Xén ảnh)**

- Tab **Crop**
- Chọn tỷ lệ: Free, 1:1, 4:3, 16:9
- Kéo/thu phóng vùng crop
- Điều chỉnh zoom với slider

### 4. **Rotate (Xoay ảnh)**

- Tab **Rotate**
- Click **-90°** hoặc **+90°** để xoay nhanh
- Hoặc kéo slider để xoay tự do (0-360°)
- **Flip H** - Lật ngang
- **Flip V** - Lật dọc

### 5. **Lưu thay đổi**

- Click **Save** ở góc trên bên phải
- Ảnh sẽ được:
  - Upload lên server
  - Thay thế ảnh cũ (ảnh cũ bị soft delete)
  - Tự động chuyển sang ảnh mới

### 6. **Hủy chỉnh sửa**

- Click **Cancel** để thoát mà không lưu

## 🎨 UI/UX Design:

### **Layout tương tự Google Photos:**

```
┌─────────────────────────────────────────────┐
│ [Cancel]       Edit Image          [Save]   │ ← Header
├─────────────────────────────────────────────┤
│                                             │
│                                             │
│           [Cropped Area]                    │ ← Crop Preview
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│   [Crop]   [Rotate]   [Adjust]             │ ← Tabs
├─────────────────────────────────────────────┤
│  Free  1:1  4:3  16:9                       │ ← Controls
│  [Zoom Slider] 150%                         │
└─────────────────────────────────────────────┘
```

### **Color Scheme:**

- Background: Black (#000)
- Overlay: Black/80% opacity
- Active button: Blue (#2563eb)
- Hover: White/10% opacity
- Text: White

## 🔧 Technical Details:

### **Crop Algorithm:**

```typescript
1. User adjusts crop area
2. Calculate pixel coordinates
3. Apply rotation transformation
4. Apply flip transformation
5. Extract cropped region
6. Convert to Blob (JPEG format)
7. Upload to server
```

### **Image Processing:**

- Canvas API for manipulation
- Matrix transformations for rotation
- Scale transformations for flip
- Image data extraction for crop

### **Upload Flow:**

```
Edit → Crop/Rotate → Save Click
  ↓
Convert to Blob (JPEG)
  ↓
Create FormData
  ↓
Upload to /api/v1/assets/upload-images
  ↓
Delete old image (soft delete)
  ↓
Navigate to new image path
```

## 🚀 Future Enhancements:

### **Adjust Tab (Coming soon):**

- Brightness adjustment
- Contrast adjustment
- Saturation adjustment
- Filters (B&W, Sepia, Vintage, etc.)
- Sharpness
- Blur

### **Advanced Features:**

- Undo/Redo stack
- Compare before/after
- Preset templates
- Batch editing
- Export quality settings

## 🎯 Keyboard Shortcuts:

- `Enter` - Save
- `Esc` - Cancel
- `R` - Rotate 90° clockwise
- `Shift + R` - Rotate 90° counter-clockwise
- `H` - Flip horizontal
- `V` - Flip vertical
- `+` - Zoom in
- `-` - Zoom out

## 📝 Notes:

1. **Image Format:** Edited images are saved as JPEG
2. **Quality:** Default quality is optimized for web
3. **Original Preservation:** Old image is soft-deleted, not permanently removed
4. **Folder:** Edited image is saved to the same folder as original
5. **Privacy:** Edited image inherits privacy setting from original

## 🐛 Troubleshooting:

### **Edit button not working:**

- Make sure image is fully loaded
- Check browser console for errors

### **Save fails:**

- Check network connection
- Verify user has upload permissions
- Check server logs

### **Image quality loss:**

- Adjust JPEG quality in `getCroppedImg()` function
- Change from JPEG to PNG for lossless (increases file size)
