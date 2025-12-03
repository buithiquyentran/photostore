"""
Example usage of PhotoStore SDK
"""

from photostore_sdk import PhotoStoreClient, PhotoStoreException

# Initialize client
client = PhotoStoreClient(
    api_key="pk_qfYvKNeFcYPVkxrcxl3av6JXx7Nrnak3g5sl8tSEHhc",
    api_secret="sk_4wjxHPtf4Swac_WSmfdp7DPkHQB-I1NPw_yArBZHRffFCuArurYHKOhpn8tJPYJF",
    base_url="http://localhost:8000"
)

def example_upload():
    """Example: Upload files"""
    print("=== Upload Files ===")
    try:
        result = client.upload_files(
            files=["test_image1.jpg", "test_image2.png"],
            folder_slug="home1",
            is_private=False,
            tags=["example", "test"]
        )
        print(f"✅ Uploaded successfully!")
        print(f"Result: {result}")
    except PhotoStoreException as e:
        print(f"❌ Upload failed: {e}")


def example_search_text():
    """Example: Search by text"""
    print("\n=== Search by Text ===")
    try:
        results = client.search_text("beach sunset", limit=5)
        print(f"✅ Found {len(results.get('data', []))} results")
        for asset in results.get('data', [])[:3]:
            print(f"  - {asset.get('name')} (ID: {asset.get('id')})")
    except PhotoStoreException as e:
        print(f"❌ Search failed: {e}")


def example_search_image():
    """Example: Search by image"""
    print("\n=== Search by Image ===")
    try:
        results = client.search_image("query_image.jpg", limit=5)
        print(f"✅ Found {len(results.get('data', []))} similar images")
        for asset in results.get('data', [])[:3]:
            print(f"  - {asset.get('name')} (Similarity: {asset.get('similarity', 0):.2f})")
    except PhotoStoreException as e:
        print(f"❌ Image search failed: {e}")


def example_get_asset():
    """Example: Get asset info"""
    print("\n=== Get Asset Info ===")
    try:
        asset = client.get_asset(asset_id=1)
        print(f"✅ Asset found:")
        print(f"  Name: {asset.get('name')}")
        print(f"  Size: {asset.get('file_size')} bytes")
        print(f"  Private: {asset.get('is_private')}")
    except PhotoStoreException as e:
        print(f"❌ Get asset failed: {e}")


def example_list_assets():
    """Example: List assets"""
    print("\n=== List Assets ===")
    try:
        assets = client.list_assets(
            folder_path="home1",
            is_private=False,
            limit=10
        )
        print(f"✅ Found {len(assets.get('data', []))} assets")
        for asset in assets.get('data', [])[:5]:
            print(f"  - {asset.get('name')} (ID: {asset.get('id')})")
    except PhotoStoreException as e:
        print(f"❌ List assets failed: {e}")


def example_update_asset():
    """Example: Update asset"""
    print("\n=== Update Asset ===")
    try:
        result = client.update_asset(
            asset_id=1,
            name="updated_name.jpg",
            is_private=True,
            tags=["updated", "example"]
        )
        print(f"✅ Asset updated successfully!")
        print(f"Result: {result}")
    except PhotoStoreException as e:
        print(f"❌ Update failed: {e}")


def example_download_asset():
    """Example: Download private asset"""
    print("\n=== Download Asset ===")
    try:
        file_url = "http://localhost:8000/uploads/5/project1/home1/example.jpg"
        client.get_asset_url(file_url, save_to="downloaded_image.jpg")
        print(f"✅ Downloaded to: downloaded_image.jpg")
    except PhotoStoreException as e:
        print(f"❌ Download failed: {e}")


def example_delete_asset():
    """Example: Delete asset"""
    print("\n=== Delete Asset ===")
    try:
        result = client.delete_asset(asset_id=999)
        print(f"✅ Asset deleted successfully!")
    except PhotoStoreException as e:
        print(f"❌ Delete failed: {e}")


if __name__ == "__main__":
    print("PhotoStore SDK Examples\n")
    
    # Run examples (comment out what you don't need)
    example_upload()
    example_search_text()
    # example_search_image()
    # example_get_asset()
    example_list_assets()
    # example_update_asset()
    # example_download_asset()
    # example_delete_asset()
    
    print("\n✨ Done!")
