"""
Slug generation utilities
"""
import re
import unicodedata


def create_slug(text: str) -> str:
    """
    Tạo slug từ text tiếng Việt.
    
    Args:
        text: Text cần chuyển thành slug
        
    Returns:
        Slug string (lowercase, hyphen-separated)
        
    Examples:
        "Thư mục của Bảo" -> "thu-muc-cua-bao"
        "My Photos 2024!" -> "my-photos-2024"
    """
    if not text:
        return ""
    
    # Chuyển về lowercase
    text = text.lower()
    
    # Chuyển đổi ký tự tiếng Việt
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
        'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd'
    }
    
    # Thay thế ký tự tiếng Việt
    for vn_char, en_char in vietnamese_map.items():
        text = text.replace(vn_char, en_char)
    
    # Normalize unicode (để xử lý các ký tự đặc biệt khác)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Chỉ giữ lại chữ cái, số và khoảng trắng
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    
    # Thay khoảng trắng bằng dấu gạch ngang
    text = re.sub(r'\s+', '-', text)
    
    # Loại bỏ dấu gạch ngang ở đầu/cuối
    text = text.strip('-')
    
    # Loại bỏ dấu gạch ngang liên tiếp
    text = re.sub(r'-+', '-', text)
    
    return text


def build_folder_path(session, folder_id: int) -> str:
    """
    Xây dựng đường dẫn folder từ slug.
    
    Args:
        session: Database session
        folder_id: ID của folder
        
    Returns:
        Folder path dạng "parent-slug/child-slug/grandchild-slug"
    """
    from models.folders import Folders
    from sqlmodel import select
    
    folder = session.get(Folders, folder_id)
    if not folder:
        return ""
    
    path_parts = []
    current_folder = folder
    
    # Traverse lên parent folders
    while current_folder:
        if current_folder.slug:
            path_parts.insert(0, current_folder.slug)
        elif current_folder.name:
            # Fallback nếu chưa có slug
            path_parts.insert(0, create_slug(current_folder.name))
        
        if current_folder.parent_id:
            current_folder = session.get(Folders, current_folder.parent_id)
        else:
            break
    
    return "/".join(path_parts)
