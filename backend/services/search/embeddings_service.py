"""
Embeddings Service - CLIP-based Image & Text Embeddings

Xử lý:
- Tạo embeddings từ ảnh
- Tạo embeddings từ text
- Lưu vào database
- Đồng bộ với FAISS index
"""

import torch
import clip
import numpy as np
from PIL import Image
from sqlmodel import Session, select
import json
from typing import Optional

from dependencies.clip_service import get_clip_model
from models import Embeddings, Assets, Folders
from services.search.faiss_index import (
    add_vector_to_project,
    remove_vector_from_project,
    rebuild_project_index,
    search_in_project
)

# Load CLIP model (cached)
model, preprocess, device = get_clip_model()


def embed_image(image: Image.Image) -> np.ndarray:
    """
    Tạo embedding vector từ ảnh sử dụng CLIP.
    
    Args:
        image: PIL Image object
    
    Returns:
        numpy array shape (512,) - normalized vector
    """
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        image_features = model.encode_image(image_tensor)
        # Normalize để dùng cosine similarity
        image_features /= image_features.norm(dim=-1, keepdim=True)
    
    return image_features.cpu().numpy().astype("float32").flatten()  # shape (512,)


def embed_text(text: str) -> np.ndarray:
    """
    Tạo embedding vector từ text sử dụng CLIP.
    
    Args:
        text: Text query (e.g., "a cat on the sofa")
    
    Returns:
        numpy array shape (512,) - normalized vector
    """
    text_token = clip.tokenize([text]).to(device)
    
    with torch.no_grad():
        text_features = model.encode_text(text_token)
        # Normalize để dùng cosine similarity
        text_features /= text_features.norm(dim=-1, keepdim=True)
    
    return text_features.cpu().numpy().astype("float32").flatten()  # shape (512,)


def add_embedding_to_db(
    session: Session,
    asset_id: int,
    project_id: int,
    folder_id: Optional[int],
    embedding_vector: np.ndarray
) -> Embeddings:
    """
    Lưu embedding vào database và đồng bộ với FAISS.
    
    Args:
        session: Database session
        asset_id: ID của asset
        project_id: ID của project
        folder_id: ID của folder (có thể None)
        embedding_vector: Vector embedding (512,)
    
    Returns:
        Embeddings object đã lưu
    """
    # Convert numpy array to JSON string
    embedding_json = json.dumps(embedding_vector.tolist())
    
    # Tạo embedding record
    embedding = Embeddings(
        asset_id=asset_id,
        project_id=project_id,
        folder_id=folder_id,
        embedding=embedding_json
    )
    
    session.add(embedding)
    session.commit()
    session.refresh(embedding)
    
    # Đồng bộ với FAISS index
    add_vector_to_project(
        project_id=project_id,
        asset_id=asset_id,
        folder_id=folder_id,
        embedding=embedding_vector
    )
    
    print(f"[Embeddings] Added embedding for asset {asset_id} in project {project_id}")
    
    return embedding


def remove_embedding_from_db(session: Session, asset_id: int, project_id: int):
    """
    Xóa embedding khỏi database và FAISS index.
    
    Args:
        session: Database session
        asset_id: ID của asset
        project_id: ID của project
    """
    # Xóa khỏi database
    embedding = session.exec(
        select(Embeddings).where(Embeddings.asset_id == asset_id)
    ).first()
    
    if embedding:
        session.delete(embedding)
        session.commit()
    
    # Xóa khỏi FAISS
    remove_vector_from_project(project_id, asset_id)
    
    print(f"[Embeddings] Removed embedding for asset {asset_id} from project {project_id}")


def rebuild_project_embeddings(session: Session, project_id: int):
    """
    Rebuild toàn bộ FAISS index cho project từ database.
    
    Args:
        session: Database session
        project_id: ID của project
    """
    print(f"[Embeddings] Rebuilding embeddings for project {project_id}")
    
    # Query tất cả embeddings của project
    embeddings = session.exec(
        select(Embeddings)
        .where(Embeddings.project_id == project_id)
    ).all()
    
    # Prepare data for FAISS
    embeddings_data = []
    for emb in embeddings:
        embedding_vec = json.loads(emb.embedding)
        embeddings_data.append((emb.asset_id, emb.folder_id, embedding_vec))
    
    # Rebuild FAISS index
    rebuild_project_index(project_id, embeddings_data)
    
    print(f"[Embeddings] Rebuilt {len(embeddings_data)} embeddings for project {project_id}")


def search_by_image(
    session: Session,
    project_id: Optional[int],
    image: Image.Image,
    k: int = 10,
    folder_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> list[Assets]:
    """
    Tìm kiếm assets tương tự bằng ảnh.
    
    Args:
        session: Database session
        project_id: ID của project (None = search tất cả projects của user)
        image: PIL Image object
        k: Số lượng kết quả
        folder_id: Filter theo folder (optional)
        user_id: ID của user (required nếu project_id=None)
    
    Returns:
        List of Assets objects
    """
    # Tạo embedding từ ảnh
    query_vector = embed_image(image)
    
    if project_id:
        # Search trong 1 project cụ thể
        asset_ids = search_in_project(project_id, query_vector, k, folder_id)
    else:
        # Search across all projects của user
        if not user_id:
            raise ValueError("user_id required when project_id is None")
        
        # Lấy tất cả projects của user
        from models.projects import Projects
        user_projects = session.exec(
            select(Projects).where(Projects.user_id == user_id)
        ).all()
        
        if not user_projects:
            return []
        
        # Search trong từng project và merge results
        all_results = []
        for proj in user_projects:
            proj_results = search_in_project(proj.id, query_vector, k, folder_id)
            all_results.extend(proj_results)
        
        # Sort by similarity và lấy top k
        asset_ids = all_results[:k]
    
    if not asset_ids:
        return []
    
    # Query assets from database
    assets = session.exec(
        select(Assets).where(Assets.id.in_(asset_ids))
    ).all()
    
    # Sắp xếp theo thứ tự tìm được
    asset_dict = {asset.id: asset for asset in assets}
    sorted_assets = [asset_dict[aid] for aid in asset_ids if aid in asset_dict]
    
    return sorted_assets


def search_by_text(
    session: Session,
    project_id: Optional[int],
    query_text: str,
    k: int = 10,
    folder_id: Optional[int] = None,
    user_id: Optional[int] = None
) -> list[Assets]:
    """
    Tìm kiếm assets bằng text query.
    
    Args:
        session: Database session
        project_id: ID của project (None = search tất cả projects của user)
        query_text: Text query (e.g., "a cat on the sofa")
        k: Số lượng kết quả
        folder_id: Filter theo folder (optional)
        user_id: ID của user (required nếu project_id=None)
    
    Returns:
        List of Assets objects
    """
    # Tạo embedding từ text
    query_vector = embed_text(query_text)
    
    if project_id:
        # Search trong 1 project cụ thể
        asset_ids = search_in_project(project_id, query_vector, k, folder_id)
    else:
        # Search across all projects của user
        if not user_id:
            raise ValueError("user_id required when project_id is None")
        
        # Lấy tất cả projects của user
        from models.projects import Projects
        user_projects = session.exec(
            select(Projects).where(Projects.user_id == user_id)
        ).all()
        
        if not user_projects:
            return []
        
        # Search trong từng project và merge results
        all_results = []
        for proj in user_projects:
            proj_results = search_in_project(proj.id, query_vector, k, folder_id)
            all_results.extend(proj_results)
        
        # Sort by similarity và lấy top k
        asset_ids = all_results[:k]
    
    if not asset_ids:
        return []
    
    # Query assets from database
    assets = session.exec(
        select(Assets).where(Assets.id.in_(asset_ids))
    ).all()
    
    # Sắp xếp theo thứ tự tìm được
    asset_dict = {asset.id: asset for asset in assets}
    sorted_assets = [asset_dict[aid] for aid in asset_ids if aid in asset_dict]
    
    return sorted_assets
