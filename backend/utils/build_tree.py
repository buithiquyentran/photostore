from typing import Any, List, Dict
from datetime import datetime

def _get_attr(item: Any, key: str):
    """Trả về giá trị của key cho dict hoặc object. Không raise lỗi nếu không tồn tại."""
    if item is None:
        return None
    if isinstance(item, dict):
        return item.get(key)
    # Pydantic/SQLModel: .dict() tồn tại -> ưu tiên dùng .dict()
    if hasattr(item, "dict") and callable(getattr(item, "dict")):
        try:
            return item.dict().get(key)
        except Exception:
            pass
    # Thử getattr
    try:
        return getattr(item, key)
    except Exception:
        pass
    # Thử __getitem__ (nếu object hỗ trợ)
    try:
        return item[key]
    except Exception:
        return None

def build_tree(folders: List[Any]) -> List[Dict]:
    """
    Nhận list of folder (dict hoặc object) và trả về list root nodes dạng dict
    mỗi node có key 'children' (list).
    """
    lookup: Dict[int, Dict] = {}

    # 1) Tạo node dict và map theo id
    for f in folders:
        fid = _get_attr(f, "id")
        if fid is None:
            # skip nếu object không có id
            continue

        created_at = _get_attr(f, "created_at")
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()

        lookup[fid] = {
            "id": fid,
            "name": _get_attr(f, "name"),
            "parent_id": _get_attr(f, "parent_id"),
            "project_id": _get_attr(f, "project_id"),
            "slug": _get_attr(f, "slug"),
            "created_at": created_at,
            "is_default": _get_attr(f, "is_default"),
            "children": []
        }

    # 2) Gắn children vào parent (nếu parent không có trong lookup -> coi là root / orphan)
    roots: List[Dict] = []
    for f in folders:
        fid = _get_attr(f, "id")
        if fid is None:
            continue
        node = lookup.get(fid)
        if not node:
            continue
        parent_id = node.get("parent_id")
        if parent_id is None or parent_id not in lookup:
            roots.append(node)
        else:
            lookup[parent_id]["children"].append(node)

    return roots
