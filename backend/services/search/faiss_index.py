# import faiss
             
# 1 FAISS index cho mỗi user
# USER_INDICES: dict[int, faiss.Index] = {}
# mapping theo user: faiss_id -> asset_id
# USER_FAISS_MAP: dict[int, dict[int, int]] = {}       # {user_id: {faiss_id: asset_id}}
# (tuỳ chọn) asset_id -> faiss_id để xoá/cập nhật nhanh
# USER_ASSET_MAP: dict[int, dict[int, int]] = {}       # {user_id: {asset_id: faiss_id}}
# DIM = 512  # dimension embedding
