import os
import json
from datetime import datetime

def ensure_dir(directory):
    """Ensure directory exists"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(data, filepath):
    """Save data to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(filepath):
    """Load data from JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

def format_size(size_bytes):
    """Format size in bytes to human readable"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f}{size_names[i]}"

def format_timestamp(timestamp):
    """Format timestamp to readable string"""
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")
