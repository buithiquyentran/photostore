"""
FAISS Index Management - Project-based Architecture

Mỗi project có 1 FAISS index riêng:
- PROJECT_INDICES: {project_id: faiss.Index}
- PROJECT_FAISS_MAP: {project_id: {faiss_id: (asset_id, folder_id)}}
- PROJECT_ASSET_MAP: {project_id: {asset_id: faiss_id}}
"""

import faiss
import numpy as np
import os
import pickle
from typing import Dict, Tuple, Optional

# Dimension của CLIP ViT-B/32
DIM = 512

# Thư mục lưu trữ FAISS index trên ổ cứng
FAISS_INDEX_DIR = "faiss_indices"

# Lưu trữ FAISS index theo project_id (trong RAM)
PROJECT_INDICES: Dict[int, faiss.Index] = {}

# Mapping: project_id -> {faiss_id: (asset_id, folder_id)}
PROJECT_FAISS_MAP: Dict[int, Dict[int, Tuple[int, Optional[int]]]] = {}

# Reverse mapping: project_id -> {asset_id: faiss_id} (để xóa/update nhanh)
PROJECT_ASSET_MAP: Dict[int, Dict[int, int]] = {}

# Tạo thư mục lưu trữ nếu chưa có
os.makedirs(FAISS_INDEX_DIR, exist_ok=True)


def save_project_index_to_disk(project_id: int):
    """
    Lưu FAISS index của project xuống ổ cứng.
    """
    if project_id not in PROJECT_INDICES:
        return
    
    try:
        # Lưu FAISS index
        index_path = os.path.join(FAISS_INDEX_DIR, f"project_{project_id}.index")
        faiss.write_index(PROJECT_INDICES[project_id], index_path)
        
        # Lưu mapping
        mapping_path = os.path.join(FAISS_INDEX_DIR, f"project_{project_id}_mapping.pkl")
        with open(mapping_path, 'wb') as f:
            pickle.dump({
                'faiss_map': PROJECT_FAISS_MAP[project_id],
                'asset_map': PROJECT_ASSET_MAP[project_id]
            }, f)
        
    except Exception as e:
        print(f"[FAISS] Error saving index for project {project_id}: {e}")


def load_project_index_from_disk(project_id: int) -> bool:
    """
    Tải FAISS index của project từ ổ cứng.
    
    Returns:
        True nếu tải thành công, False nếu không
    """
    try:
        index_path = os.path.join(FAISS_INDEX_DIR, f"project_{project_id}.index")
        mapping_path = os.path.join(FAISS_INDEX_DIR, f"project_{project_id}_mapping.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(mapping_path):
            return False
        
        # Tải FAISS index
        idx = faiss.read_index(index_path)
        PROJECT_INDICES[project_id] = idx
        
        # Tải mapping
        with open(mapping_path, 'rb') as f:
            data = pickle.load(f)
            PROJECT_FAISS_MAP[project_id] = data['faiss_map']
            PROJECT_ASSET_MAP[project_id] = data['asset_map']
        
        return True
        
    except Exception as e:
        print(f"[FAISS] Error loading index for project {project_id}: {e}")
        return False


def get_or_create_project_index(project_id: int) -> faiss.Index:
    """
    Lấy hoặc tạo FAISS index cho project.
    Sử dụng IndexFlatIP (Inner Product) vì CLIP vectors đã được normalized.
    Tự động tải từ ổ cứng nếu có.
    """
    if project_id not in PROJECT_INDICES:
        # Thử tải từ ổ cứng trước
        if not load_project_index_from_disk(project_id):
            # Nếu không tải được, tạo mới
            idx = faiss.IndexFlatIP(DIM)  # Inner Product cho cosine similarity
            PROJECT_INDICES[project_id] = idx
            PROJECT_FAISS_MAP[project_id] = {}
            PROJECT_ASSET_MAP[project_id] = {}
    
    return PROJECT_INDICES[project_id]


def add_vector_to_project(
    project_id: int,
    asset_id: int,
    folder_id: Optional[int],
    embedding: np.ndarray
):
    """
    Thêm vector vào FAISS index của project.
    
    Args:
        project_id: ID của project
        asset_id: ID của asset
        folder_id: ID của folder (có thể None)
        embedding: Vector embedding (shape: 512)
    """
    idx = get_or_create_project_index(project_id)
    
    # Chuẩn hóa vector (nếu chưa)
    vec = np.array(embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(vec)
    
    # Thêm vào FAISS
    idx.add(vec)
    
    # Lấy faiss_id mới (index cuối cùng)
    faiss_id = idx.ntotal - 1
    
    # Lưu mapping
    PROJECT_FAISS_MAP[project_id][faiss_id] = (asset_id, folder_id)
    PROJECT_ASSET_MAP[project_id][asset_id] = faiss_id
    
    # Tự động lưu xuống ổ cứng
    save_project_index_to_disk(project_id)


def remove_vector_from_project(project_id: int, asset_id: int):
    """
    Xóa vector khỏi FAISS index.
    
    Note: FAISS không hỗ trợ xóa trực tiếp, cần rebuild index.
    Đánh dấu asset_id trong mapping để bỏ qua khi search.
    """
    if project_id not in PROJECT_ASSET_MAP:
        return
    
    if asset_id in PROJECT_ASSET_MAP[project_id]:
        faiss_id = PROJECT_ASSET_MAP[project_id][asset_id]
        
        # Xóa khỏi mapping (đánh dấu đã xóa)
        del PROJECT_FAISS_MAP[project_id][faiss_id]
        del PROJECT_ASSET_MAP[project_id][asset_id]
        
        # Tự động lưu xuống ổ cứng
        save_project_index_to_disk(project_id)


def search_in_project(
    project_id: int,
    query_vector: np.ndarray,
    k: int = 10,
    folder_id: Optional[int] = None,
    search_type: str = "image",
    similarity_threshold: float = 0.7  # Ngưỡng similarity (0.7 = 70% giống nhau),
    ) -> list[int]:
    """
    Tìm kiếm trong project bằng vector query.
    
    Args:
        project_id: ID của project
        query_vector: Vector query (shape: 512)
        k: Số lượng kết quả trả về
        folder_id: Nếu có, chỉ tìm trong folder này
        similarity_threshold: Ngưỡng similarity (0-1), chỉ trả về kết quả có similarity >= threshold
    
    Returns:
        List asset_ids tìm được
    """
    if project_id not in PROJECT_INDICES:
        return []
    
    idx = PROJECT_INDICES[project_id]
    mapping = PROJECT_FAISS_MAP[project_id]
    
    if idx.ntotal == 0:
        return []
    
    # Chuẩn hóa query vector
    q = np.array(query_vector, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(q)
    
    # Tìm kiếm (lấy nhiều hơn k để filter theo folder)
    search_k = k * 10 if folder_id else k
    
    D, I = idx.search(q, min(search_k, idx.ntotal))
    
    # Lấy asset_ids
    asset_ids = []
    for i, fid in enumerate(I[0]):
        if fid == -1:  # FAISS trả về -1 nếu không đủ kết quả
            continue
        
        if fid not in mapping:  # Vector đã bị xóa
            continue
        
        # Tính similarity từ distance (FAISS trả về inner product)
        # Vì vectors đã được chuẩn hóa, inner product chính là cosine similarity
        similarity = float(D[0][i])
        if search_type == "text":
            # Điều chỉnh threshold cho text search (thường thấp hơn)
            similarity_threshold= 0.2
        # Chỉ lấy kết quả có similarity >= threshold
        if similarity < similarity_threshold:
            continue
        
        asset_id, f_id = mapping[fid]
        
        # Filter theo folder nếu có
        if folder_id and f_id != folder_id:
            continue
        
        asset_ids.append(asset_id)
        
        if len(asset_ids) >= k:
            break
    
    return asset_ids


def rebuild_project_index(project_id: int, embeddings_data: list[Tuple[int, Optional[int], list[float]]]):
    """
    Rebuild toàn bộ FAISS index cho project từ database.
    
    Args:
        project_id: ID của project
        embeddings_data: List of (asset_id, folder_id, embedding_vector)
    """
    
    # Tạo index mới
    idx = faiss.IndexFlatIP(DIM)
    faiss_map = {}
    asset_map = {}
    
    if embeddings_data:
        vectors = []
        for asset_id, folder_id, embedding in embeddings_data:
            vec = np.array(embedding, dtype="float32")
            vectors.append(vec)
        
        # Convert to numpy array và normalize
        X = np.array(vectors, dtype="float32")
        faiss.normalize_L2(X)
        
        # Add vào index
        idx.add(X)
        
        # Tạo mapping
        for i, (asset_id, folder_id, _) in enumerate(embeddings_data):
            faiss_map[i] = (asset_id, folder_id)
            asset_map[asset_id] = i
    
    # Cập nhật global state
    PROJECT_INDICES[project_id] = idx
    PROJECT_FAISS_MAP[project_id] = faiss_map
    PROJECT_ASSET_MAP[project_id] = asset_map
    
    # Tự động lưu xuống ổ cứng
    save_project_index_to_disk(project_id)


def get_project_stats(project_id: int) -> dict:
    """Lấy thống kê về FAISS index của project."""
    if project_id not in PROJECT_INDICES:
        return {"total_vectors": 0, "indexed": False}
    
    idx = PROJECT_INDICES[project_id]
    return {
        "total_vectors": idx.ntotal,
        "indexed": True,
        "dimension": DIM
    }


def load_all_indices_from_disk():
    """
    Tải tất cả FAISS index từ ổ cứng khi khởi động server.
    """
    if not os.path.exists(FAISS_INDEX_DIR):
        return
    
    loaded_count = 0
    for filename in os.listdir(FAISS_INDEX_DIR):
        if filename.startswith("project_") and filename.endswith(".index"):
            # Extract project_id from filename
            try:
                project_id = int(filename.replace("project_", "").replace(".index", ""))
                if load_project_index_from_disk(project_id):
                    loaded_count += 1
            except ValueError:
                continue
    
    print(f"[FAISS] Loaded {loaded_count} indices from disk")
