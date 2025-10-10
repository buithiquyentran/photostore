"""
Auto-Tagging Service - CLIP-based Image Tagging

Tự động đánh tags cho hình ảnh sử dụng CLIP model.
"""

import torch
import clip
import numpy as np
from PIL import Image
from sqlmodel import Session
from typing import List, Tuple

from dependencies.clip_service import get_clip_model
from db.crud_tag import get_or_create_tag, add_tag_to_asset, get_tags_for_asset
from models import Assets

# Load CLIP model (cached)
model, preprocess, device = get_clip_model()

# Predefined labels for auto-tagging
# EXPANDED: Thêm labels chi tiết cho clothing, colors, people attributes
DEFAULT_LABELS = [
    # People - General
    "person", "people", "human", "man", "woman", "boy", "girl",
    "child", "children", "baby", "adult", "teenager", "elderly",
    "male", "female", "couple", "group", "crowd",
    
    # People - Portraits & Poses
    "portrait", "selfie", "face", "smiling", "laughing",
    "looking at camera", "profile", "back view", "full body",
    "headshot", "closeup", "standing", "sitting", "walking",
    
    # Clothing - Upper Body
    "shirt", "t-shirt", "blouse", "sweater", "jacket", "coat",
    "hoodie", "tank top", "dress shirt", "polo shirt",
    "cardigan", "vest", "blazer",
    
    # Clothing - Lower Body & Full
    "pants", "jeans", "shorts", "skirt", "dress",
    "leggings", "trousers", "suit", "uniform",
    
    # Clothing - Accessories
    "hat", "cap", "glasses", "sunglasses", "scarf",
    "bag", "backpack", "watch", "jewelry", "necklace",
    
    # Colors - Common
    "white", "black", "red", "blue", "green", "yellow",
    "orange", "pink", "purple", "brown", "gray", "grey",
    
    # Colors - Clothing Specific
    "white shirt", "black shirt", "red dress", "blue jeans",
    "white dress", "black dress", "colorful clothing",
    
    # Combinations - People & Clothing
    "person wearing white", "person wearing black",
    "girl in dress", "woman in dress", "man in suit",
    "person in uniform", "casual wear", "formal wear",
    
    # Family & Relationships
    "family", "mother", "father", "parents", "siblings",
    "friends", "wedding", "bride", "groom",
    
    # Activities & Events
    "party", "celebration", "birthday", "graduation",
    "meeting", "presentation", "conference", "interview",
    "shopping", "eating", "drinking", "cooking",
    "reading", "writing", "working", "studying",
    
    # Nature & Outdoor
    "nature", "landscape", "mountain", "hill", "valley",
    "beach", "ocean", "sea", "lake", "river", "water",
    "forest", "tree", "trees", "flower", "flowers", "plant",
    "garden", "park", "field", "grass", "sky", "cloud", "clouds",
    "sunset", "sunrise", "night", "moon", "stars",
    "snow", "rain", "sunny", "cloudy",
    
    # Animals
    "cat", "dog", "bird", "animal", "pet", "horse",
    "cow", "pig", "chicken", "fish", "butterfly",
    
    # Food & Dining
    "food", "meal", "dish", "plate", "bowl",
    "restaurant", "cafe", "breakfast", "lunch", "dinner",
    "dessert", "cake", "bread", "fruit", "vegetable",
    "coffee", "tea", "drink", "beverage", "wine", "beer",
    
    # Urban & Architecture
    "city", "urban", "building", "buildings", "architecture",
    "street", "road", "bridge", "tower", "skyscraper",
    "house", "home", "apartment", "room", "indoor", "outdoor",
    "office", "kitchen", "bedroom", "living room", "bathroom",
    
    # Transportation
    "car", "cars", "vehicle", "bicycle", "bike", "motorcycle",
    "bus", "truck", "train", "airplane", "plane", "boat", "ship",
    
    # Objects - Electronics
    "phone", "smartphone", "computer", "laptop", "tablet",
    "camera", "television", "tv", "screen", "monitor",
    
    # Objects - Furniture & Home
    "furniture", "table", "chair", "sofa", "couch", "bed",
    "desk", "shelf", "cabinet", "door", "window",
    
    # Objects - Other
    "book", "books", "paper", "document", "pen", "pencil",
    "bottle", "glass", "cup", "mug", "plate", "bowl",
    
    # Art & Culture
    "art", "painting", "drawing", "sculpture", "artwork",
    "music", "instrument", "guitar", "piano",
    
    # Sports & Recreation
    "sport", "sports", "football", "soccer", "basketball",
    "tennis", "volleyball", "baseball", "swimming", "running",
    "gym", "fitness", "exercise", "yoga", "hiking", "cycling",
    
    # Places & Events
    "travel", "vacation", "trip", "holiday", "tourism",
    "festival", "concert", "show", "performance",
    "museum", "gallery", "theater", "cinema",
    "mall", "store", "shop", "market",
    "airport", "station", "hospital", "school", "university",
    
    # Weather & Season
    "summer", "winter", "spring", "autumn", "fall",
    "hot", "cold", "warm", "cool",
    
    # Style & Mood
    "beautiful", "pretty", "handsome", "cute", "elegant",
    "casual", "formal", "professional", "modern", "vintage",
    "colorful", "monochrome", "black and white",
    "bright", "dark", "light", "shadow",
    "happy", "sad", "serious", "fun", "romantic",
    
    # Photography Style
    "portrait photography", "landscape photography",
    "street photography", "fashion photography",
    "close up", "wide angle", "aerial view",
    
    # Work & Education
    "work", "working", "office work", "business",
    "meeting", "presentation", "training",
    "school", "classroom", "study", "studying",
    "teacher", "student", "learning",
]


def get_image_tags(
    image: Image.Image,
    labels: List[str] = None,
    threshold: float = 0.25,
    top_k: int = 5
) -> List[Tuple[str, float]]:
    """
    Tự động đánh tags cho hình ảnh sử dụng CLIP.
    
    Args:
        image: PIL Image object
        labels: List các labels để test (mặc định dùng DEFAULT_LABELS)
        threshold: Ngưỡng confidence (0-1), chỉ giữ tags có confidence >= threshold
        top_k: Số lượng tags tối đa trả về
    
    Returns:
        List of (tag_name, confidence_score) tuples, sorted by confidence
    """
    if labels is None:
        labels = DEFAULT_LABELS
    
    # Preprocess image
    image_tensor = preprocess(image).unsqueeze(0).to(device)
    
    # Tokenize labels
    text_tokens = clip.tokenize(labels).to(device)
    
    # Get features
    with torch.no_grad():
        image_features = model.encode_image(image_tensor)
        text_features = model.encode_text(text_tokens)
        
        # Normalize features
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        
        # Calculate similarity (cosine similarity) - FIXED: Bỏ softmax!
        # Softmax làm tổng = 1.0 → với 347 labels mỗi cái chỉ ~0.3% → Chỉ 1-2 tags!
        # Dùng cosine similarity trực tiếp (range: -1 to 1)
        similarity = (image_features @ text_features.T).cpu().numpy()[0]
    
    # Get tags with confidence >= threshold
    results = []
    for i, label in enumerate(labels):
        confidence = float(similarity[i])
        if confidence >= threshold:
            results.append((label, confidence))
    
    # Sort by confidence (descending) and take top_k
    results.sort(key=lambda x: x[1], reverse=True)
    results = results[:top_k]
    
    return results


def auto_tag_asset(
    session: Session,
    asset_id: int,
    image: Image.Image,
    labels: List[str] = None,
    threshold: float = 0.25,
    top_k: int = 5,
    overwrite: bool = False
) -> List[str]:
    """
    Tự động đánh tags cho asset và lưu vào database.
    
    Args:
        session: Database session
        asset_id: ID của asset
        image: PIL Image object
        labels: List các labels để test (optional)
        threshold: Ngưỡng confidence (0-1)
        top_k: Số lượng tags tối đa
        overwrite: Nếu True, xóa tất cả tags cũ trước khi thêm tags mới
    
    Returns:
        List of tag names đã được thêm
    """
    # Kiểm tra asset có tồn tại không
    asset = session.get(Assets, asset_id)
    if not asset:
        raise ValueError(f"Asset {asset_id} not found")
    
    # Get tags from image
    predicted_tags = get_image_tags(image, labels, threshold, top_k)
    
    if not predicted_tags:
        return []
    
    # Nếu overwrite, xóa tất cả tags cũ
    if overwrite:
        from db.crud_tag import remove_tag_from_asset, get_tags_for_asset
        existing_tags = get_tags_for_asset(session, asset_id)
        for tag in existing_tags:
            remove_tag_from_asset(session, tag.id, asset_id)
    
    # Add tags to database
    added_tags = []
    for tag_name, confidence in predicted_tags:
        # Get or create tag
        tag = get_or_create_tag(
            session, 
            tag_name,
            note=f"Auto-generated by CLIP (confidence: {confidence:.2f})"
        )
        
        # Link tag to asset
        add_tag_to_asset(session, tag.id, asset_id)
        
        added_tags.append(tag_name)
    
    return added_tags


def auto_tag_asset_by_id(
    session: Session,
    asset_id: int,
    labels: List[str] = None,
    threshold: float = 0.25,
    top_k: int = 5,
    overwrite: bool = False
) -> List[str]:
    """
    Tự động đánh tags cho asset từ asset_id (tự động load image từ file).
    
    Args:
        session: Database session
        asset_id: ID của asset
        labels: List các labels để test (optional)
        threshold: Ngưỡng confidence (0-1)
        top_k: Số lượng tags tối đa
        overwrite: Nếu True, xóa tất cả tags cũ trước khi thêm tags mới
    
    Returns:
        List of tag names đã được thêm
    """
    from pathlib import Path
    
    # Get asset from database
    asset = session.get(Assets, asset_id)
    if not asset:
        raise ValueError(f"Asset {asset_id} not found")
    
    # Load image từ file
    UPLOAD_DIR = Path("uploads")
    safe_path = asset.path.replace("\\", "/")
    file_path = (UPLOAD_DIR / safe_path).resolve()
    
    if not file_path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")
    
    # Open image
    image = Image.open(file_path).convert("RGB")
    
    # Auto tag
    return auto_tag_asset(session, asset_id, image, labels, threshold, top_k, overwrite)


def batch_auto_tag_assets(
    session: Session,
    asset_ids: List[int],
    labels: List[str] = None,
    threshold: float = 0.25,
    top_k: int = 5,
    overwrite: bool = False
) -> dict:
    """
    Tự động đánh tags cho nhiều assets cùng lúc.
    
    Args:
        session: Database session
        asset_ids: List of asset IDs
        labels: List các labels để test (optional)
        threshold: Ngưỡng confidence (0-1)
        top_k: Số lượng tags tối đa
        overwrite: Nếu True, xóa tất cả tags cũ trước khi thêm tags mới
    
    Returns:
        Dict with results: {asset_id: [tag_names]} và errors: {asset_id: error_message}
    """
    results = {}
    errors = {}
    
    for asset_id in asset_ids:
        try:
            tags = auto_tag_asset_by_id(
                session, 
                asset_id, 
                labels, 
                threshold, 
                top_k, 
                overwrite
            )
            results[asset_id] = tags
        except Exception as e:
            errors[asset_id] = str(e)
    
    return {
        "results": results,
        "errors": errors
    }


def search_similar_tags(query: str, labels: List[str] = None, top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Tìm các tags tương tự với query text.
    
    Args:
        query: Text query
        labels: List các labels để search (mặc định dùng DEFAULT_LABELS)
        top_k: Số lượng tags trả về
    
    Returns:
        List of (tag_name, similarity_score) tuples
    """
    if labels is None:
        labels = DEFAULT_LABELS
    
    # Tokenize
    query_tokens = clip.tokenize([query]).to(device)
    label_tokens = clip.tokenize(labels).to(device)
    
    with torch.no_grad():
        query_features = model.encode_text(query_tokens)
        label_features = model.encode_text(label_tokens)
        
        # Normalize
        query_features /= query_features.norm(dim=-1, keepdim=True)
        label_features /= label_features.norm(dim=-1, keepdim=True)
        
        # Calculate similarity
        similarity = (query_features @ label_features.T).cpu().numpy()[0]
    
    # Get top_k results
    results = [(labels[i], float(similarity[i])) for i in range(len(labels))]
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results[:top_k]

