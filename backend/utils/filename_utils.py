"""
Utilities for handling filenames
"""
import os
from typing import Tuple

def truncate_filename(filename: str, max_length: int = 255) -> str:
    """
    Truncate filename if it's longer than max_length while preserving extension.
    Example: 
        very_long_filename.jpg (max_length=20) -> very_long_f...jpg
    """
    if not filename:
        return filename
        
    # Get name and extension
    name, ext = os.path.splitext(filename)
    
    # Calculate max name length
    # -3 for '...' and rest for extension
    max_name_length = max_length - len(ext) - 3
    
    if len(name) > max_name_length:
        # Truncate name and add '...'
        name = name[:max_name_length] + '...'
    
    return name + ext

def split_filename(filename: str) -> Tuple[str, str]:
    """
    Split filename into name and extension.
    Returns (name, extension)
    """
    # Handle empty/None filename
    if not filename:
        return "", ""
        
    # Split into name and extension
    name, ext = os.path.splitext(filename)
    
    # Remove dot from extension and convert to lowercase
    ext = ext.lstrip('.').lower()
    
    return name, ext

def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename.
    """
    if not filename:
        return filename
        
    # Get name and extension
    name, ext = os.path.splitext(filename)
    
    # Remove/replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
        
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    
    return name + ext if ext else name
