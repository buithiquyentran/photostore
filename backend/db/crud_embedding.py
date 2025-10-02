"""
CRUD operations for Embeddings

Helper functions để tạo/xóa embeddings khi upload/delete assets
"""

from sqlmodel import Session
from PIL import Image
import io
from typing import Optional

from models import Embeddings, Assets, Folders
from services.search.embeddings_service import (
    embed_image,
    add_embedding_to_db,
    remove_embedding_from_db
)


def create_embedding_for_asset(
    session: Session,
    asset_id: int,
    image_bytes: bytes
) -> Optional[Embeddings]:
    """
    Tạo embedding cho asset từ image bytes.
    
    Tự động lấy project_id và folder_id từ asset.
    
    Args:
        session: Database session
        asset_id: ID của asset
        image_bytes: Bytes của ảnh
    
    Returns:
        Embeddings object hoặc None nếu không tạo được
    """
    # Lấy asset info
    asset = session.get(Assets, asset_id)
    if not asset:
        print(f"[CRUD] Asset {asset_id} not found")
        return None
    
    # Lấy folder để biết project_id
    folder = session.get(Folders, asset.folder_id) if asset.folder_id else None
    if not folder:
        print(f"[CRUD] Folder not found for asset {asset_id}")
        return None
    
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Tạo embedding vector
        embedding_vector = embed_image(image)
        
        # Lưu vào DB và FAISS
        embedding = add_embedding_to_db(
            session=session,
            asset_id=asset_id,
            project_id=folder.project_id,
            folder_id=asset.folder_id,
            embedding_vector=embedding_vector
        )
        
        return embedding
        
    except Exception as e:
        print(f"[CRUD] Error creating embedding for asset {asset_id}: {e}")
        return None


def delete_embedding_for_asset(session: Session, asset_id: int):
    """
    Xóa embedding của asset.
    
    Args:
        session: Database session
        asset_id: ID của asset
    """
    # Lấy asset info
    asset = session.get(Assets, asset_id)
    if not asset:
        return
    
    # Lấy folder để biết project_id
    folder = session.get(Folders, asset.folder_id) if asset.folder_id else None
    if not folder:
        return
    
    try:
        remove_embedding_from_db(session, asset_id, folder.project_id)
    except Exception as e:
        print(f"[CRUD] Error deleting embedding for asset {asset_id}: {e}")
