# from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
# from sqlmodel import Session, select
# from typing import List
# from PIL import Image
# import numpy as np
# import io, faiss, json
# from db.session import get_session
# from models import Assets, Embeddings
# router = APIRouter()
# router = APIRouter(prefix="/assets",  tags=["Assets"])
# from services.search.faiss_index import USER_INDICES, USER_FAISS_MAP, USER_ASSET_MAP,DIM
# from core.security import get_current_user
# from models import Folders, Projects
# from dependencies.clip_service import get_clip_model

# import torch
# import clip
# from PIL import Image

# # load model 1 lần khi start server
# # device = "cuda" if torch.cuda.is_available() else "cpu"
# # model, preprocess = clip.load("ViT-B/32", device=device)
# model, preprocess, device = get_clip_model()
# # DIM = 512  # với CLIP ViT-B/32 thì embedding_dim = 512

# def embed_image(image: Image.Image) -> np.ndarray:
#     """Trích embedding từ ảnh bằng CLIP."""
#     image_tensor = preprocess(image).unsqueeze(0).to(device)
#     with torch.no_grad():
#         image_features = model.encode_image(image_tensor)
#         image_features /= image_features.norm(dim=-1, keepdim=True)  # normalize
#     return image_features.cpu().numpy().astype("float32")  # shape (1, 512)
# def get_text_embedding(text: str):
#     text_token = clip.tokenize([text]).to(device)
#     with torch.no_grad():
#         text_features = model.encode_text(text_token)
#         # Chuẩn hóa về vector đơn vị (giống ảnh)
#         text_features = text_features / text_features.norm(dim=-1, keepdim=True)
#     return text_features.cpu().numpy().astype("float32")  # shape (1, 512)
    


# def add_embedding_to_faiss(user_id: int, asset_id: int, embedding: list[float]):
#     # ensure_user_index(None, user_id)  # đảm bảo có index, session=None vì không rebuild DB
#     idx = USER_INDICES[user_id]
#     mapping = USER_FAISS_MAP[user_id]
#     reverse_map = USER_ASSET_MAP[user_id]

#     vec = np.array(embedding, dtype="float32").reshape(1, -1)
#     faiss.normalize_L2(vec)

#     idx.add(vec)

#     # FAISS id mới nhất
#     faiss_id = idx.ntotal - 1
#     mapping[faiss_id] = asset_id
#     reverse_map[asset_id] = faiss_id


     
# def ensure_user_index(session, user_id: int):
#     if user_id in USER_INDICES:
#         return
#     # Query tất cả embeddings của user từ DB
#     rows = session.exec(
#         select(Embeddings.embedding, Embeddings.asset_id)
#         .join(Assets, Embeddings.asset_id == Assets.id)
#         .join(Folders, Assets.folder_id == Folders.id)
#         .join(Projects, Folders.project_id == Projects.id)
#         .where(Projects.user_id == user_id)
#     ).all()

#     idx = faiss.IndexFlatIP(DIM)
#     faiss_id_to_asset = {}
#     asset_to_faiss_id = {}

#     if rows:
#         vectors = []
#         for emb_json, asset_id in rows:
#             vec = json.loads(emb_json) if isinstance(emb_json, str) else emb_json
#             vectors.append(vec)

#         X = np.array(vectors, dtype="float32")
#         faiss.normalize_L2(X)
#         idx.add(X)

#         for i, (_, asset_id) in enumerate(rows):
#             faiss_id_to_asset[i] = asset_id
#             asset_to_faiss_id[asset_id] = i

#     USER_INDICES[user_id] = idx
#     USER_FAISS_MAP[user_id] = faiss_id_to_asset
#     USER_ASSET_MAP[user_id] = asset_to_faiss_id

# def search_user(session, user_id: int, query_vec: np.ndarray, k: int = 10):
#     # ensure_user_index(session, user_id)

#     idx = USER_INDICES[user_id]
#     mapping = USER_FAISS_MAP[user_id]

#     q = np.array(query_vec, dtype="float32").reshape(1, -1)
#     faiss.normalize_L2(q)

#     D, I = idx.search(q, k)
#     asset_ids = []
#     for fid in I[0]:
#         if fid == -1:
#             continue
#         if fid in mapping:
#             asset_ids.append(mapping[fid])
#     return asset_ids

# def search_by_embedding(session, user_id: int, query_vec: np.ndarray, k: int = 10):
#     # ensure_user_index(session, user_id)
#     idx = USER_INDICES[user_id]
#     mapping = USER_FAISS_MAP[user_id]

#     faiss.normalize_L2(query_vec)
#     D, I = idx.search(query_vec, k)

#     asset_ids = []
#     for fid in I[0]:
#         if fid == -1:
#             continue
#         if fid in mapping:
#             asset_ids.append(mapping[fid])

#     return asset_ids
