# dependencies/clip_service.py
import torch
import clip
from functools import lru_cache

DIM = 512  # embedding_dim của CLIP ViT-B/32

@lru_cache()
def get_clip_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Loading CLIP model...")  # Debug: chỉ in khi lần đầu gọi
    model, preprocess = clip.load("ViT-B/32", device=device)
    return model, preprocess, device
