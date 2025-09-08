import faiss

DIM = 512  # số chiều embedding
index = faiss.IndexFlatIP(DIM)   # dùng cosine similarity (normalize trước)
faiss_id_to_asset: dict[int, int] = {}
next_faiss_id = 0               
