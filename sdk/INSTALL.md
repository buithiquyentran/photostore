# PhotoStore SDK - Installation & Usage Guide

## Installation Methods

### Method 1: Install from source (Recommended for development)

```bash
cd photostore/sdk
pip install -e .
```

This installs the package in "editable" mode, so changes to the source code are immediately available.

### Method 2: Install from source (Production)

```bash
cd photostore/sdk
pip install .
```

### Method 3: Direct file import

Simply copy `python/photostore_sdk.py` to your project and import:

```python
from photostore_sdk import PhotoStoreClient
```

## Usage

### Initialize Client

```python
from photostore_sdk import PhotoStoreClient

client = PhotoStoreClient(
    api_key="pk_your_api_key",
    api_secret="sk_your_api_secret",
    base_url="http://localhost:8000"
)
```

### Upload Files

```python
# Upload single file
result = client.upload_files(
    files=["photo.jpg"],
    folder_slug="vacation",
    is_private=False
)

# Upload multiple files
result = client.upload_files(
    files=["photo1.jpg", "photo2.jpg", "photo3.jpg"],
    folder_slug="family",
    is_private=True
)
```

### Search

```python
# Search by text
results = client.search_text("sunset beach", k=10)

# Search by image
similar = client.search_image("query.jpg", k=5)
```

### Thumbnails

```python
# Get thumbnail URL
url = client.get_thumbnail(
    asset_id=123,
    width=500,
    height=500,
    format="webp",
    quality=90,
    return_url=True
)

# Download thumbnail
thumb_data = client.get_thumbnail(
    asset_id=123,
    width=300,
    height=300
)

# Save thumbnail to file
client.get_thumbnail(
    asset_id=123,
    width=800,
    height=600,
    save_to="thumbnail.jpg"
)
```

### Asset Management

```python
# List assets
assets = client.list_assets(folder_id=5)

# Get asset info
asset = client.get_asset(asset_id=123)

# Update asset
client.update_asset(
    asset_id=123,
    name="new_name.jpg",
    is_private=True
)

# Delete asset (soft delete)
client.delete_asset(asset_id=123)
```

## Uninstallation

```bash
pip uninstall photostore-sdk
```

## Requirements

- Python >= 3.8
- requests >= 2.25.0

## Development

Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format code:

```bash
black python/
```

## Support

For issues and questions, please visit:
https://github.com/buithiquyentran/photostore/issues
