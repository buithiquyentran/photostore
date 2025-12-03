"""
PhotoStore Python SDK - Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "python" / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="photostore_sdk",
    version="1.0.0",
    author="PhotoStore",
    author_email="support@photostore.com",
    description="Python SDK for PhotoStore API with automatic HMAC authentication",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/buithiquyentran/photostore",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    keywords="photostore sdk api image storage hmac authentication",
    project_urls={
        "Source": "https://github.com/buithiquyentran/photostore",
        "Documentation": "https://github.com/buithiquyentran/photostore/blob/main/sdk/python/README.md",
    },
)
