"""
PhotoStore SDK for Python
==========================

A simple SDK to interact with PhotoStore API without worrying about HMAC authentication.

Usage:
    from photostore_sdk import PhotoStoreClient
    
    client = PhotoStoreClient(
        api_key="your_api_key",
        api_secret="your_api_secret",
        base_url="http://localhost:8000"
    )
    
    # Upload files
    result = client.upload_files(
        files=["image1.jpg", "image2.png"],
        folder_slug="photos",
        is_private=False
    )
    
    # Search by text
    results = client.search_text("sunset beach")
    
    # Search by image
    results = client.search_image("query_image.jpg")
    
    # Get asset info
    asset = client.get_asset(asset_id=123)
    
    # Delete asset
    client.delete_asset(asset_id=123)
"""

import hmac
import hashlib
import time
import requests
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import mimetypes


class PhotoStoreException(Exception):
    """Custom exception for PhotoStore SDK"""
    pass


class PhotoStoreClient:
    """
    Main client for interacting with PhotoStore API
    
    Args:
        api_key (str): Your PhotoStore API key
        api_secret (str): Your PhotoStore API secret
        base_url (str): Base URL of PhotoStore API (default: http://localhost:8000)
        timeout (int): Request timeout in seconds (default: 30)
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.api_endpoint = f"{self.base_url}/api/external"
    
    def _generate_signature(self) -> Dict[str, Any]:
        """Generate HMAC signature for authentication"""
        timestamp = int(time.time())
        message = f"{timestamp}:{self.api_key}"
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return {
            "signature": signature,
            "timestamp": timestamp
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        sig = self._generate_signature()
        return {
            "X-API-Key": self.api_key,
            "X-Signature": sig["signature"],
            "X-Timestamp": str(sig["timestamp"])
        }
    
    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise exceptions if needed"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            raise PhotoStoreException(f"API Error ({response.status_code}): {error_detail}")
        except requests.exceptions.RequestException as e:
            raise PhotoStoreException(f"Request failed: {str(e)}")
    
    def upload_files(
        self,
        files: List[Union[str, Path]],
        folder_slug: Optional[str] = None,
        is_private: bool = False
    ) -> Dict[str, Any]:
        """
        Upload one or multiple files to PhotoStore
        
        Args:
            files: List of file paths to upload
            folder_slug: Target folder slug (optional)
            is_private: Whether files should be private (default: False)
        
        Returns:
            Dict containing upload results
        
        Example:
            result = client.upload_files(
                files=["photo1.jpg", "photo2.png"],
                folder_slug="vacation",
                is_private=True
            )
        """
        # Prepare files - keep file handles open until after request
        files_to_upload = []
        file_handles = []
        
        try:
            for file_path in files:
                path = Path(file_path)
                if not path.exists():
                    raise PhotoStoreException(f"File not found: {file_path}")
                
                content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
                fh = open(path, "rb")
                file_handles.append(fh)
                files_to_upload.append(
                    ("files", (path.name, fh, content_type))
                )
            
            # Prepare form data
            data = {}
            if folder_slug:
                data["folder_slug"] = folder_slug
            if is_private:
                data["is_private"] = "true"
            else:
                data["is_private"] = "false"
            
            # Send request
            response = requests.post(
                f"{self.api_endpoint}/assets/upload",
                files=files_to_upload,
                data=data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
        finally:
            # Close all file handles
            for fh in file_handles:
                try:
                    fh.close()
                except:
                    pass
        
        return self._handle_response(response)
    
    def search_image(
        self,
        query_text: Optional[str] = None,
        image_path: Optional[Union[str, Path]] = None,
        k: int = 10,
        folder_id: Optional[int] = None,
        similarity_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Search assets by text query, image, or both (multimodal search)
        
        Args:
            query_text: Text search query (optional)
            image_path: Path to query image (optional)
            k: Maximum number of results (default: 10)
            folder_id: Optional folder ID to search within
            similarity_threshold: Minimum similarity 0-1 (default: 0.7 = 70%)
        
        Returns:
            Dict containing search results
        
        Example:
            # Text search only
            results = client.search(query_text="sunset beach", k=10)
            
            # Image search only
            results = client.search(image_path="query.jpg", k=10)
            
            # Multimodal search (text + image)
            results = client.search(
                query_text="red car",
                image_path="car.jpg",
                k=10
            )
        """
        if not query_text and not image_path:
            raise PhotoStoreException("Must provide at least query_text or image_path")
        
        # Prepare form data
        data = {
            "k": k,
            "similarity_threshold": similarity_threshold
        }
        
        if query_text:
            data["query_text"] = query_text
        
        if folder_id is not None:
            data["folder_id"] = folder_id
        
        # Prepare files if image is provided
        files = None
        file_handle = None
        
        try:
            if image_path:
                path = Path(image_path)
                if not path.exists():
                    raise PhotoStoreException(f"Image not found: {image_path}")
                
                content_type = mimetypes.guess_type(str(path))[0] or "image/jpeg"
                file_handle = open(path, "rb")
                files = [("file", (path.name, file_handle, content_type))]
            
            # Send request
            response = requests.post(
                f"{self.api_endpoint}/image",
                files=files,
                data=data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
        finally:
            # Close file handle if opened
            if file_handle:
                try:
                    file_handle.close()
                except:
                    pass
        
        return self._handle_response(response)

    def get_asset(self, asset_id: int) -> Dict[str, Any]:
        """
        Get asset information by ID
        
        Args:
            asset_id: Asset ID
        
        Returns:
            Dict containing asset details
        
        Example:
            asset = client.get_asset(123)
        """
        response = requests.get(
            f"{self.api_endpoint}/assets/{asset_id}",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        
        return self._handle_response(response)
    
    def delete_asset(self, asset_id: int, permanently: bool = False) -> Dict[str, Any]:
        """
        Delete an asset by ID
        
        Args:
            asset_id: Asset ID to delete
        
        Returns:
            Dict containing deletion result
        
        Example:
            result = client.delete_asset(123)
        """
        response = requests.delete(
            f"{self.api_endpoint}/assets/{asset_id}",
            params={"permanently": str(permanently).lower()},
            headers=self._get_headers(),
            timeout=self.timeout
        )
        
        return self._handle_response(response)
    
    def get_asset_url(
        self,
        file_url: str,
        save_to: Optional[Union[str, Path]] = None
    ) -> Union[bytes, None]:
        """
        Download asset file (for private assets)
        
        Args:
            file_url: Full file URL from PhotoStore
            save_to: Optional path to save file (if not provided, returns bytes)
        
        Returns:
            File bytes if save_to is None, otherwise None
        
        Example:
            # Download to memory
            data = client.get_asset_url("http://localhost:8000/uploads/...")
            
            # Download to file
            client.get_asset_url("http://localhost:8000/uploads/...", save_to="image.jpg")
        """
        response = requests.get(
            file_url,
            headers=self._get_headers(),
            timeout=self.timeout,
            stream=True
        )
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise PhotoStoreException(f"Failed to download asset: {str(e)}")
        
        if save_to:
            path = Path(save_to)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return None
        else:
            return response.content
    
    def list_assets(
        self,
        folder_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List assets in project/folder
        
        Args:
            folder_id: Optional folder ID to filter assets (if None, returns all project assets)
        
        Returns:
            List of assets
        
        Example:
            assets = client.list_assets(folder_id=5)
        """
        params = {}
        
        if folder_id is not None:
            params["folder_id"] = folder_id
        
        response = requests.get(
            f"{self.api_endpoint}/assets",
            params=params,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        
        return self._handle_response(response)
    
    def update_asset(
        self,
        asset_id: int,
        name: Optional[str] = None,
        is_private: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update asset metadata
        
        Args:
            asset_id: Asset ID to update
            name: New name for asset
            is_private: Update privacy status
            tags: Update tags
        
        Returns:
            Dict containing updated asset
        
        Example:
            result = client.update_asset(
                asset_id=123,
                name="new_name.jpg",
                is_private=True,
                tags=["updated", "photo"]
            )
        """
        data = {}
        
        if name is not None:
            data["name"] = name
        if is_private is not None:
            data["is_private"] = is_private
        if tags is not None:
            data["tags"] = tags
        
        response = requests.patch(
            f"{self.api_endpoint}/assets/{asset_id}",
            json=data,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        
        return self._handle_response(response)
    
    def get_thumbnail(
        self,
        asset_id: int,
        width: int = 300,
        height: int = 300,
        format: str = "webp",
        quality: int = 100,
        save_to: Optional[Union[str, Path]] = None,
        return_url: bool = False
    ) -> Union[bytes, str, None]:
        """
        Get or generate thumbnail for an asset
        
        Args:
            asset_id: Asset ID
            width: Thumbnail width (default: 300)
            height: Thumbnail height (default: 300)
            format: Image format - webp, jpg, png (default: webp)
            quality: Image quality 1-100 (default: 100)
            save_to: Optional path to save thumbnail (if not provided, returns bytes or URL)
            return_url: If True, returns thumbnail URL instead of downloading (default: False)
        
        Returns:
            - Thumbnail URL if return_url=True
            - Thumbnail bytes if return_url=False and save_to is None
            - None if save_to is provided (file saved to disk)
        
        Example:
            # Get thumbnail URL
            url = client.get_thumbnail(asset_id=123, width=500, height=500, return_url=True)
            # Returns: "http://localhost:8000/uploads/public-thumbnail/123_w=500&h=500&format=webp&q=100"
            
            # Download thumbnail bytes
            data = client.get_thumbnail(asset_id=123, width=300, height=300)
            
            # Save thumbnail to file
            client.get_thumbnail(asset_id=123, width=500, height=500, save_to="thumb.webp")
            
            # Get different formats
            jpg_data = client.get_thumbnail(asset_id=123, format="jpg", quality=90)
        """
        # Build thumbnail URL using the correct format
        thumbnail_url = f"{self.base_url}/uploads/public-thumbnail/{asset_id}_w={width}&h={height}&format={format}&q={quality}"
        
        # If only URL is requested, return it immediately
        if return_url:
            return thumbnail_url
        
        # Otherwise, download the thumbnail
        response = requests.get(
            thumbnail_url,
            headers=self._get_headers(),
            timeout=self.timeout,
            stream=True
        )
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            raise PhotoStoreException(f"Failed to get thumbnail: {error_detail}")
        
        # Download image bytes
        if save_to:
            path = Path(save_to)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return None
        else:
            return response.content


