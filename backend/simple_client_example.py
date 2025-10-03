#!/usr/bin/env python3
"""
Simple API Client Example - Dễ dàng tích hợp vào project của bạn
"""

import hmac
import hashlib
import time
import requests
import json
from typing import Optional, Dict, Any, List

class PhotoStoreClient:
    """Client đơn giản để gọi External API"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
    
    def _generate_signature(self, timestamp: str) -> str:
        """Tạo HMAC signature đơn giản"""
        message = f"{timestamp}:{self.api_key}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(
        self, 
        method: str, 
        path: str, 
        json_data: Optional[Dict] = None,
        form_data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Gửi request với signature"""
        
        # Tạo timestamp và signature
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp)
        
        # Headers
        headers = {
            "X-API-Key": self.api_key,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        }
        
        # URL đầy đủ
        url = f"{self.base_url}{path}"
        
        # Gửi request
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=form_data, files=files)
            elif form_data:
                response = requests.post(url, headers=headers, data=form_data)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Parse response
        try:
            return response.json()
        except:
            return {"status": "error", "message": response.text}
    
    # ========================================
    # Folder Management
    # ========================================
    
    def create_folder(self, name: str, parent_id: Optional[int] = None, description: Optional[str] = None) -> Dict:
        """Tạo folder mới"""
        return self._make_request("POST", "/api/v1/external/folders", json_data={
            "name": name,
            "parent_id": parent_id,
            "description": description
        })
    
    def list_folders(self, parent_id: Optional[int] = None) -> List[Dict]:
        """Lấy danh sách folders"""
        path = "/api/v1/external/folders"
        if parent_id is not None:
            path += f"?parent_id={parent_id}"
        return self._make_request("GET", path)
    
    def delete_folder(self, folder_id: int) -> Dict:
        """Xóa folder"""
        return self._make_request("DELETE", f"/api/v1/external/folders/{folder_id}")
    
    # ========================================
    # Asset Management
    # ========================================
    
    def upload_files(self, file_paths: List[str], folder_id: Optional[int] = None, is_private: bool = False) -> List[Dict]:
        """Upload files"""
        files = [('files', open(fp, 'rb')) for fp in file_paths]
        form_data = {
            'folder_id': folder_id,
            'is_private': str(is_private).lower()
        }
        
        try:
            return self._make_request("POST", "/api/v1/external/assets/upload", form_data=form_data, files=files)
        finally:
            for _, f in files:
                f.close()
    
    def list_assets(self, folder_id: Optional[int] = None) -> List[Dict]:
        """Lấy danh sách assets"""
        path = "/api/v1/external/assets"
        if folder_id is not None:
            path += f"?folder_id={folder_id}"
        return self._make_request("GET", path)
    
    def delete_asset(self, asset_id: int) -> Dict:
        """Xóa asset"""
        return self._make_request("DELETE", f"/api/v1/external/assets/{asset_id}")
    
    # ========================================
    # Search
    # ========================================
    
    def search_by_text(self, query: str, folder_id: Optional[int] = None, k: int = 10) -> Dict:
        """Tìm kiếm bằng text"""
        return self._make_request("POST", "/api/v1/external/search/text", form_data={
            'query': query,
            'folder_id': folder_id,
            'k': k
        })
    
    def search_by_image(self, image_path: str, folder_id: Optional[int] = None, k: int = 10) -> Dict:
        """Tìm kiếm bằng hình ảnh"""
        with open(image_path, 'rb') as f:
            files = {'file': f}
            form_data = {
                'folder_id': folder_id,
                'k': k
            }
            return self._make_request("POST", "/api/v1/external/search/image", form_data=form_data, files=files)


# ========================================
# Ví dụ sử dụng
# ========================================

def example_usage():
    """Ví dụ sử dụng client"""
    
    # 1. Khởi tạo client
    client = PhotoStoreClient(
        api_key="pk_hm4xqCXfprlNVW6CqxB4KmBUIQGICTuoYK49xd08QS8",
        api_secret="sk_LcqHRVdTDpPVbKcw-ABSx5cKwJ_3VEEZFE8xH3kXYH4_iwg80V_W_5LvjEBkhzTL",
        base_url="http://localhost:8000"
    )
    
    print("=" * 60)
    print("PhotoStore External API Client - Examples")
    print("=" * 60)
    
    # 2. Tạo folder
    print("\n[1] Tao folder moi...")
    result = client.create_folder(
        name="Test Folder from Client",
        description="Folder created via simple client"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 3. List folders
    print("\n[2] Danh sach folders...")
    folders = client.list_folders()
    print(json.dumps(folders, indent=2, ensure_ascii=False))
    
    # 4. List assets
    print("\n[3] Danh sach assets...")
    assets = client.list_assets()
    print(json.dumps(assets, indent=2, ensure_ascii=False))
    
    # 5. Search by text
    print("\n[4] Tim kiem bang text...")
    search_results = client.search_by_text("cat", k=5)
    print(json.dumps(search_results, indent=2, ensure_ascii=False))
    
    # 6. Upload files (uncomment neu co file de test)
    # print("\n[5] Upload files...")
    # upload_result = client.upload_files(
    #     file_paths=["test1.jpg", "test2.png"],
    #     folder_id=1,
    #     is_private=False
    # )
    # print(json.dumps(upload_result, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("[OK] Done! Copy class PhotoStoreClient vao project cua ban de su dung")
    print("=" * 60)


if __name__ == "__main__":
    # Thay API credentials của bạn vào đây
    example_usage()

