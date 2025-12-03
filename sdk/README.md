# PhotoStore SDK

Python SDK for PhotoStore API - Simplify image storage and management with automatic HMAC authentication.

## Features

- 🔐 **Automatic HMAC Authentication** - No need to manually handle signatures
- 📤 **Easy File Upload** - Upload single or multiple files with one function call
- 🔍 **Powerful Search** - Search by text or image similarity using CLIP embeddings
- 🖼️ **Thumbnail Generation** - Get optimized thumbnails with custom sizes and formats
- 📁 **Asset Management** - Complete CRUD operations for your assets
- 🎯 **Type Hints** - Full type annotations for better IDE support

## Installation

### From Source

```bash
cd photostore/sdk
pip install -e .
```

### Direct Import

Copy the `python/photostore_sdk.py` file to your project and import it:

```python
from photostore_sdk import PhotoStoreClient
```

## Quick Start

```python
from photostore_sdk import PhotoStoreClient

# Initialize client
client = PhotoStoreClient(
    api_key="pk_your_api_key",
    api_secret="sk_your_api_secret",
    base_url="http://localhost:8000"
)

# Upload a file
result = client.upload_files(
    files=["photo.jpg"],
    folder_slug="vacation",
    is_private=False
)

# Search by text
results = client.search_text("sunset beach", k=10)

# Get thumbnail
thumbnail = client.get_thumbnail(
    asset_id=123,
    width=500,
    height=500,
    format="webp"
)
```

## Documentation

Full documentation available in [`python/README.md`](python/README.md)

## Requirements

- Python >= 3.8
- requests >= 2.25.0

## License

MIT License - see [LICENSE](LICENSE) file for details
