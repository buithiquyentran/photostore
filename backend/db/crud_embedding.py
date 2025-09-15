# from sqlmodel import Session
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime
import io, faiss, json

from models import Embeddings
from PIL import Image
import io
import json
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
import torch

# from services.embeddings_service import index, faiss_id_to_asset, embed_image, rebuild_faiss
from services.search.embeddings_service import embed_image

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model = clip_model.to(device)

def embed_image(image: Image.Image) -> np.ndarray:
    inputs = clip_processor(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        emb = clip_model.get_image_features(**inputs)
    emb = emb / emb.norm(dim=-1, keepdim=True)  # chuẩn hoá vector
    return emb.cpu().numpy().astype("float32")

def embed_text(text: str) -> np.ndarray:
    inputs = clip_processor(text=[text], return_tensors="pt").to(device)
    with torch.no_grad():
        emb = clip_model.get_text_features(**inputs)
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy().astype("float32")

def add_to_faiss(asset_id: int, embedding: list[float]):
    global next_faiss_id, faiss_id_to_asset

    vec = np.array([embedding], dtype="float32")
    faiss.normalize_L2(vec)

    index.add(vec)  # add vào FAISS
    faiss_id_to_asset[next_faiss_id] = asset_id
    next_faiss_id += 1

    print(f"[FAISS] Added asset {asset_id}, current total {index.ntotal}")


def add_embedding(session: Session, asset_id: int, file_bytes: bytes):
    """
    Sinh vector embedding từ ảnh và lưu vào bảng Embeddings.
    """
    # chuyển bytes -> PIL image
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")

    # vector hóa CLIP 
    vector = embed_image(image)  # numpy (1,512)

    # lưu vào DB
    embedding = Embeddings(asset_id=asset_id, embedding=json.dumps(vector[0].tolist()))
    session.add(embedding)
    session.commit()
    session.refresh(embedding)

    return embedding, vector[0].tolist()
