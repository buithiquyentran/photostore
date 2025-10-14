"""
Tags API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from typing import List, Optional
from pydantic import BaseModel
from PIL import Image
import io

from db.session import get_session
from dependencies.dependencies import get_current_user
from db.crud_tag import (
    get_or_create_tag,
    add_tag_to_asset,
    get_tags_for_asset,
    remove_tag_from_asset,
    search_assets_by_tags,
    get_all_tags,
    update_tag,
    delete_tag
)
from services.tagging_service import (
    auto_tag_asset_by_id,
    get_image_tags,
    batch_auto_tag_assets,
    search_similar_tags
)
from models import Tags, Assets

router = APIRouter(prefix="/tags", tags=["Tags"])


# ===== Pydantic Models =====

class TagCreate(BaseModel):
    name: str
    note: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[int] = None
    note: Optional[str] = None


class TagResponse(BaseModel):
    id: int
    name: str
    status: int
    note: Optional[str]
    created_at: int
    updated_at: int


class AssetTagRequest(BaseModel):
    asset_id: int
    tag_names: List[str]


class AutoTagRequest(BaseModel):
    asset_id: int
    threshold: float = 0.25
    top_k: int = 5
    overwrite: bool = False
    custom_labels: Optional[List[str]] = None


class BatchAutoTagRequest(BaseModel):
    asset_ids: List[int]
    threshold: float = 0.25
    top_k: int = 5
    overwrite: bool = False
    custom_labels: Optional[List[str]] = None


class SearchByTagsRequest(BaseModel):
    tag_names: List[str]
    project_id: Optional[int] = None
    folder_id: Optional[int] = None
    match_all: bool = False


class SearchTextRequest(BaseModel):
    query: str
    project_id: Optional[int] = None
    folder_id: Optional[int] = None
    match_all: bool = False


# ===== Tag Management APIs =====

@router.get("/", response_model=List[TagResponse])
def list_tags(
    active_only: bool = True,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Lấy danh sách tất cả tags.
    """
    tags = get_all_tags(session, active_only=active_only)
    return tags


@router.post("/", response_model=TagResponse)
def create_tag(
    tag_data: TagCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tạo tag mới (hoặc lấy tag đã tồn tại).
    """
    tag = get_or_create_tag(session, tag_data.name, tag_data.note)
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag_info(
    tag_id: int,
    tag_data: TagUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Cập nhật thông tin tag.
    """
    tag = update_tag(
        session,
        tag_id,
        name=tag_data.name,
        status=tag_data.status,
        note=tag_data.note
    )
    
    if not tag:
        raise HTTPException(404, "Tag not found")
    
    return tag


@router.delete("/{tag_id}")
def delete_tag_by_id(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Xóa tag và tất cả liên kết của nó.
    """
    success = delete_tag(session, tag_id)
    
    if not success:
        raise HTTPException(404, "Tag not found")
    
    return {"message": "Tag deleted successfully"}


# ===== Asset Tagging APIs =====

@router.post("/asset/add")
def add_tags_to_asset(
    request: AssetTagRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Thêm tags cho asset (manual tagging).
    """
    # Kiểm tra asset có tồn tại và thuộc về user không
    asset = session.get(Assets, request.asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")
    
    # TODO: Check quyền sở hữu asset
    
    added_tags = []
    for tag_name in request.tag_names:
        tag = get_or_create_tag(session, tag_name)
        add_tag_to_asset(session, tag.id, request.asset_id)
        added_tags.append(tag.name)
    
    return {
        "asset_id": request.asset_id,
        "added_tags": added_tags
    }


@router.get("/asset/{asset_id}", response_model=List[TagResponse])
def get_asset_tags(
    asset_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Lấy tất cả tags của một asset.
    """
    # Kiểm tra asset có tồn tại không
    asset = session.get(Assets, asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")
    
    # TODO: Check quyền xem asset
    
    tags = get_tags_for_asset(session, asset_id)
    return tags


@router.delete("/asset/{asset_id}/tag/{tag_id}")
def remove_tag_from_asset_route(
    asset_id: int,
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Xóa tag khỏi asset.
    """
    # Kiểm tra asset có tồn tại không
    asset = session.get(Assets, asset_id)
    if not asset:
        raise HTTPException(404, "Asset not found")
    
    # TODO: Check quyền sửa asset
    
    success = remove_tag_from_asset(session, tag_id, asset_id)
    
    if not success:
        raise HTTPException(404, "Tag association not found")
    
    return {"message": "Tag removed from asset successfully"}


# ===== Auto-Tagging APIs =====

@router.post("/auto-tag")
def auto_tag_asset_route(
    request: AutoTagRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tự động đánh tags cho asset sử dụng CLIP.
    """
    try:
        tags = auto_tag_asset_by_id(
            session,
            request.asset_id,
            labels=request.custom_labels,
            threshold=request.threshold,
            top_k=request.top_k,
            overwrite=request.overwrite
        )
        
        return {
            "asset_id": request.asset_id,
            "tags": tags,
            "count": len(tags)
        }
    except ValueError as e:
        raise HTTPException(404, str(e))
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error during auto-tagging: {str(e)}")


@router.post("/auto-tag/batch")
def batch_auto_tag_route(
    request: BatchAutoTagRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tự động đánh tags cho nhiều assets cùng lúc.
    """
    result = batch_auto_tag_assets(
        session,
        request.asset_ids,
        labels=request.custom_labels,
        threshold=request.threshold,
        top_k=request.top_k,
        overwrite=request.overwrite
    )
    
    return result


@router.post("/auto-tag/upload")
async def auto_tag_upload_image(
    file: UploadFile = File(...),
    threshold: float = 0.25,
    top_k: int = 5,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload hình ảnh và lấy predicted tags (không lưu vào database).
    Dùng để preview tags trước khi upload asset.
    """
    try:
        # Đọc file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Get predicted tags
        predicted_tags = get_image_tags(image, threshold=threshold, top_k=top_k)
        
        return {
            "filename": file.filename,
            "predicted_tags": [
                {"name": name, "confidence": round(conf, 4)}
                for name, conf in predicted_tags
            ]
        }
    except Exception as e:
        raise HTTPException(500, f"Error processing image: {str(e)}")


# ===== Search APIs =====

@router.post("/search")
def search_by_tags(
    request: SearchByTagsRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tìm kiếm assets theo tags.
    """
    assets = search_assets_by_tags(
        session,
        request.tag_names,
        project_id=request.project_id,
        folder_id=request.folder_id,
        match_all=request.match_all
    )
    
    return {
        "query": request.tag_names,
        "match_all": request.match_all,
        "count": len(assets),
        "assets": assets
    }


@router.post("/search/text")
def search_by_text(
    request: SearchTextRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Tìm kiếm assets bằng text query.
    
    Workflow:
    1. Dùng CLIP để tìm các tags tương tự với query text
    2. Tìm assets có các tags đó
    """
    # Tìm tags tương tự với query
    similar_tags = search_similar_tags(request.query, top_k=10)
    
    if not similar_tags:
        return {
            "query": request.query,
            "similar_tags": [],
            "count": 0,
            "assets": []
        }
    
    # Lấy tag names (chỉ lấy những tags có similarity > 0.2)
    tag_names = [name for name, score in similar_tags if score > 0.2]
    
    if not tag_names:
        return {
            "query": request.query,
            "similar_tags": similar_tags,
            "count": 0,
            "assets": []
        }
    
    # Tìm assets theo tags
    assets = search_assets_by_tags(
        session,
        tag_names,
        project_id=request.project_id,
        folder_id=request.folder_id,
        match_all=request.match_all
    )
    
    return {
        "query": request.query,
        "similar_tags": [
            {"name": name, "similarity": round(score, 4)}
            for name, score in similar_tags
        ],
        "matched_tags": tag_names,
        "count": len(assets),
        "assets": assets
    }


@router.get("/search/suggest")
def suggest_tags(
    query: str,
    top_k: int = 5,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Gợi ý tags dựa trên query text.
    """
    similar_tags = search_similar_tags(query, top_k=top_k)
    
    return {
        "query": query,
        "suggestions": [
            {"name": name, "similarity": round(score, 4)}
            for name, score in similar_tags
        ]
    }

