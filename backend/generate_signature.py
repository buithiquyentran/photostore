#!/usr/bin/env python3
"""
Generate API Signature for PhotoStore External API

Script này tạo signature và headers cần thiết để gọi External API.
Chạy script và copy headers để sử dụng trong Postman hoặc các công cụ test API khác.
"""

import hmac
import hashlib
import time
import json
import argparse
import sys
import os
from typing import Dict, Any, Optional

def generate_signature(api_key: str, api_secret: str, timestamp: Optional[int] = None) -> Dict[str, str]:
    """
    Tạo HMAC signature đơn giản cho API request
    
    Args:
        api_key: API key của project
        api_secret: API secret của project
        timestamp: Unix timestamp (nếu None sẽ dùng thời gian hiện tại)
    
    Returns:
        Dict chứa headers cần thiết
    """
    if timestamp is None:
        timestamp = int(time.time())
    
    timestamp_str = str(timestamp)
    
    # Format đơn giản: TIMESTAMP:API_KEY
    message = f"{timestamp_str}:{api_key}"
    
    # Tạo signature bằng HMAC-SHA256
    signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "X-API-Key": api_key,
        "X-Timestamp": timestamp_str,
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

def print_headers(headers: Dict[str, str], for_curl: bool = False) -> None:
    """
    In headers để copy vào Postman hoặc curl
    
    Args:
        headers: Dict chứa headers
        for_curl: Nếu True, in headers theo format curl
    """
    print("\n" + "=" * 60)
    print("API Headers")
    print("=" * 60)
    
    if for_curl:
        print("curl headers:")
        for key, value in headers.items():
            print(f"-H '{key}: {value}' \\")
    else:
        print("Postman headers:")
        for key, value in headers.items():
            print(f"{key}: {value}")
    
    print("=" * 60)

def save_to_file(headers: Dict[str, str], filename: str) -> None:
    """
    Lưu headers vào file
    
    Args:
        headers: Dict chứa headers
        filename: Tên file để lưu
    """
    with open(filename, 'w') as f:
        json.dump(headers, f, indent=2)
    
    print(f"\nHeaders saved to file: {filename}")

def main():
    # Default API credentials - thay đổi giá trị này để không phải nhập mỗi lần chạy
    DEFAULT_API_KEY = "pk_hm4xqCXfprlNVW6CqxB4KmBUIQGICTuoYK49xd08QS8"
    DEFAULT_API_SECRET = "sk_LcqHRVdTDpPVbKcw-ABSx5cKwJ_3VEEZFE8xH3kXYH4_iwg80V_W_5LvjEBkhzTL"
    
    parser = argparse.ArgumentParser(description='Generate API signature for PhotoStore External API')
    parser.add_argument('--key', '-k', help='API key')
    parser.add_argument('--secret', '-s', help='API secret')
    parser.add_argument('--timestamp', '-t', type=int, help='Custom timestamp (Unix time)')
    parser.add_argument('--curl', '-c', action='store_true', help='Output in curl format')
    parser.add_argument('--save', '-o', help='Save headers to file')
    
    args = parser.parse_args()
    
    # Sử dụng API key/secret từ command line hoặc giá trị mặc định
    api_key = args.key or DEFAULT_API_KEY
    api_secret = args.secret or DEFAULT_API_SECRET
    
    if not api_key or not api_secret:
        print("Error: API key and API secret cannot be empty")
        sys.exit(1)
    
    # Tạo headers
    headers = generate_signature(api_key, api_secret, args.timestamp)
    
    # In headers
    print_headers(headers, args.curl)
    
    # Lưu vào file nếu cần
    if args.save:
        save_to_file(headers, args.save)
    
    print("\nExpiration time: " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(headers["X-Timestamp"]) + 300)))

if __name__ == "__main__":
    main()
