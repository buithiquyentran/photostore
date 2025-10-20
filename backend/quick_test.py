#!/usr/bin/env python3
"""
Quick Test Script for PhotoStore External API

Script này tạo signature và thực hiện một số API calls cơ bản để kiểm tra.
"""

import requests
import hmac
import hashlib
import time
import json
import os
from typing import Dict, Any, Optional, List

class PhotoStoreAPITester:
    """
    Lớp để test PhotoStore External API
    """
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timestamp = str(int(time.time()))
        self.headers = self._generate_headers()
    
    def _generate_headers(self) -> Dict[str, str]:
        """Tạo headers với signature"""
        message = f"{self.timestamp}:{self.api_key}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return {
            "X-API-Key": self.api_key,
            "X-Timestamp": self.timestamp,
            "X-Signature": signature,
            "Content-Type": "application/json"
        }
    
    def _print_request(self, method: str, url: str, data: Any = None):
        """In thông tin request"""
        print(f"\n{'=' * 60}")
        print(f"REQUEST: {method} {url}")
        print(f"HEADERS:")
        for key, value in self.headers.items():
            print(f"  {key}: {value}")
        
        if data:
            print(f"DATA:")
            print(json.dumps(data, indent=2))
        
        print(f"{'=' * 60}")
    
    def _print_response(self, response):
        """In thông tin response"""
        print(f"\n{'=' * 60}")
        print(f"RESPONSE: {response.status_code}")
        print(f"{'=' * 60}")
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
    
    def list_folders(self):
        """Test API lấy danh sách folders"""
        url = f"{self.base_url}/api/v1/external/folders"
        
        self._print_request("GET", url)
        response = requests.get(url, headers=self.headers)
        self._print_response(response)
        
        return response
    
    def create_folder(self, name: str, parent_id: Optional[int] = None):
        """Test API tạo folder mới"""
        url = f"{self.base_url}/api/v1/external/folders"
        data = {
            "name": name,
            "parent_id": parent_id,
            "description": f"Test folder created at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        self._print_request("POST", url, data)
        response = requests.post(url, headers=self.headers, json=data)
        self._print_response(response)
        
        return response
    
    def list_assets(self, folder_id: Optional[int] = None):
        """Test API lấy danh sách assets"""
        url = f"{self.base_url}/api/v1/external/assets"
        if folder_id:
            url += f"?folder_id={folder_id}"
        
        self._print_request("GET", url)
        response = requests.get(url, headers=self.headers)
        self._print_response(response)
        
        return response
    
    def search_text(self, query: str, k: int = 5):
        """Test API tìm kiếm bằng text"""
        url = f"{self.base_url}/api/v1/external/search/text"
        
        # Cần thay đổi headers cho form-data
        headers = self.headers.copy()
        del headers["Content-Type"]
        
        form_data = {
            "query": query,
            "k": k
        }
        
        self._print_request("POST", url, form_data)
        response = requests.post(url, headers=headers, data=form_data)
        self._print_response(response)
        
        return response

def main():
    # Lấy API key và secret từ môi trường hoặc nhập từ bàn phím
    api_key = os.environ.get("API_KEY")
    api_secret = os.environ.get("API_SECRET")
    
    if not api_key:
        api_key = input("Nhập API key: ").strip()
    
    if not api_secret:
        api_secret = input("Nhập API secret: ").strip()
    
    # Khởi tạo tester
    tester = PhotoStoreAPITester(api_key, api_secret)
    
    # Menu
    while True:
        print("\n" + "=" * 60)
        print("PHOTOSTORE API TESTER")
        print("=" * 60)
        print("1. Lấy danh sách folders")
        print("2. Tạo folder mới")
        print("3. Lấy danh sách assets")
        print("4. Tìm kiếm bằng text")
        print("0. Thoát")
        
        choice = input("\nChọn chức năng (0-4): ")
        
        if choice == "1":
            tester.list_folders()
        elif choice == "2":
            name = input("Tên folder: ")
            parent_id_str = input("ID của folder cha (để trống nếu là root): ")
            parent_id = int(parent_id_str) if parent_id_str else None
            tester.create_folder(name, parent_id)
        elif choice == "3":
            folder_id_str = input("ID của folder (để trống để lấy tất cả): ")
            folder_id = int(folder_id_str) if folder_id_str else None
            tester.list_assets(folder_id)
        elif choice == "4":
            query = input("Nhập từ khóa tìm kiếm: ")
            k_str = input("Số lượng kết quả (mặc định 5): ")
            k = int(k_str) if k_str else 5
            tester.search_text(query, k)
        elif choice == "0":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
