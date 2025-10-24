from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status
import io
import os
from PIL import Image
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from sqlmodel import select
import io
import os
from fastapi import HTTPException, status
from pathlib import Path
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from PIL import Image

UPLOAD_DIR = Path("uploads")
from models import  Assets , Thumbnails

UPLOAD_THUMBNAILS = Path("uploads/thumbnails")

# Thumbnail schemas
class ThumbnailCreate(BaseModel):
    asset_id: int
    width: int
    height: int
    quality: int = 80
    format: str = "webp"
    file_url: str
    file_size: Optional[float] = None

# Thumbnail CRUD functions
def get_thumbnail(
    session: Session, 
    asset_id: int, 
    width: int, 
    height: int, 
    format: str = "webp",
    quality: int = 80
) -> Optional[Thumbnails]:
    """Get existing thumbnail or return None"""
    return session.query(Thumbnails).filter(
        Thumbnails.asset_id == asset_id,
        Thumbnails.width == width,
        Thumbnails.height == height,
        Thumbnails.format == format,
        Thumbnails.quality == quality
    ).first()

# def create_thumbnail(session: Session, thumbnail_data: ThumbnailCreate) -> Thumbnails:
#     """Create new thumbnail record in database"""
#     db_thumbnail =Thumbnails(**thumbnail_data.dict())
#     session.add(db_thumbnail)
#     session.commit()
#     session.refresh(db_thumbnail)
#     return db_thumbnail

def update_thumbnail_access(session: Session, thumbnail: Thumbnails):
    """Update last accessed time and access count"""
    thumbnail.last_accessed = datetime.utcnow()
    thumbnail.access_count += 1
    session.commit()

def resize_image(image_data: bytes, width: int, height: int, format: str = "webp", quality: int = 80) -> bytes:
    """Resize image using Pillow"""
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if saving as JPEG
        if format.lower() in ['jpg', 'jpeg'] and image.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Resize image maintaining aspect ratio
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        save_format = 'JPEG' if format.lower() in ['jpg', 'jpeg'] else format.upper()
        
        if save_format == 'JPEG':
            image.save(output, format=save_format, quality=quality, optimize=True)
        elif save_format == 'WEBP':
            image.save(output, format=save_format, quality=quality, optimize=True)
        else:
            image.save(output, format=save_format, optimize=True)
        
        return output.getvalue()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resize image: {str(e)}"
        )

def upload_thumbnail_to_local(
    thumbnail_data: bytes,
    asset_id: int,
    width: int,
    height: int,
    format: str = "webp"
) -> str:
    """
    Lưu thumbnail xuống local (uploads/thumbnails)
    và trả về URL có thể truy cập qua static /uploads route.
    """
    try:
        # Đảm bảo thư mục tồn tại
        os.makedirs(UPLOAD_THUMBNAILS, exist_ok=True)

        # Đặt tên file (nên dùng _ thay vì ? vì ? gây lỗi URL)
        thumbnail_filename = f"{asset_id}_{width}x{height}.{format.lower()}"
        save_path = UPLOAD_THUMBNAILS / thumbnail_filename

        # Ghi file từ bytes
        with open(save_path, "wb") as f:
            f.write(thumbnail_data)

        # Tạo URL public (tùy thuộc app.mount trong main.py)
        file_url = f"http://localhost:8000/uploads/thumbnail/{thumbnail_filename}"
        return file_url

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save thumbnail locally: {str(e)}"
        )


def get_or_create_thumbnail(
    session: Session,
    asset_id: int,
    width: int,
    height: int,
    format: str = "webp",
    quality: int = 80,
) -> Thumbnails:
    """
    Lấy thumbnail đã có hoặc tạo mới (lưu LOCAL)
    """

    # Step 1️⃣: Kiểm tra thumbnail đã tồn tại chưa
    statement = select(Thumbnails).where(
        (Thumbnails.asset_id == asset_id)
        & (Thumbnails.width == width)
        & (Thumbnails.height == height)
        & (Thumbnails.format == format)
        & (Thumbnails.quality == quality)
    )
    existing_thumbnail: Optional[Thumbnails] = session.exec(statement).first()

    if existing_thumbnail:
        existing_thumbnail.access_count += 1
        session.add(existing_thumbnail)
        session.commit()
        session.refresh(existing_thumbnail)
        return existing_thumbnail

    # Step 2️⃣: Lấy file gốc
    stmt_file = select(Assets).where(Assets.id == asset_id)
    original_file = session.exec(stmt_file).first()

    if not original_file:
        raise HTTPException(status_code=404, detail="Original file not found")

    # Step 3️⃣: Kiểm tra loại file
    if not original_file.file_type or not original_file.file_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")

    # Step 4️⃣: Đọc ảnh gốc từ local
    try:
        
        # uploads_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads"))
        relative_path = original_file.path
        local_path = os.path.join(UPLOAD_DIR, relative_path).replace("\\", "/")
        
        if not os.path.exists(local_path):
            raise HTTPException(status_code=404, detail="Original image not found in local storage")

        with open(local_path, "rb") as f:
            original_image_data = f.read()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read original image from local storage: {str(e)}"
        )

    # Step 5️⃣: Resize ảnh
    thumbnail_data = resize_image(original_image_data, width, height, format, quality)

    # Step 6️⃣: Lưu thumbnail xuống local
    thumbnail_url = upload_thumbnail_to_local(thumbnail_data, asset_id, width, height, format)
    
    filename = f"{asset_id}_{width}x{height}.{format.lower()}"
    # Step 7️⃣: Tạo record trong DB
    new_thumbnail = Thumbnails(
        asset_id=asset_id,
        width=width,
        height=height,
        quality=quality,
        format=format,
        filename= filename,
        file_url=thumbnail_url,
        file_size=len(thumbnail_data),
        access_count=1,
    )

    session.add(new_thumbnail)
    session.commit()
    session.refresh(new_thumbnail)

    return new_thumbnail
def generate_thumbnail_urls_for_file(asset_id: int, base_url: str = "http://localhost:8000/api/v1") -> list:
    """Generate thumbnail URLs for common sizes"""
    common_sizes = [
        (64, 64),   # Small thumbnail
        (300, 300),   # Medium thumbnail  
        (500, 500),   # Large thumbnail
        (800, 600),   # Landscape
    ]
    
    thumbnail_urls = []
    for width, height in common_sizes:
        thumbnail_url = f"{base_url}/thumbnail/{asset_id}?w={width}&h={height}"
        thumbnail_urls.append({
            "width": width,
            "height": height,
            "url": thumbnail_url
        })
    
    return thumbnail_urls 