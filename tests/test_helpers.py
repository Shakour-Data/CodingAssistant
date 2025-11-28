import pytest
import os
import json
import tempfile
from datetime import datetime
from app.utils.helpers import ensure_dir, save_json, load_json, format_size, format_timestamp

def test_ensure_dir():
    """Test ensure_dir function"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, 'test_subdir')
        assert not os.path.exists(test_dir)

        ensure_dir(test_dir)
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)

def test_save_json():
    """Test save_json function"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        test_file = f.name

    try:
        test_data = {'key': 'value', 'number': 42, 'list': [1, 2, 3]}
        save_json(test_data, test_file)

        # Verify file was created and contains correct data
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_load_json():
    """Test load_json function"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        test_file = f.name

    try:
        test_data = {'test': 'data', 'array': [4, 5, 6]}
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        loaded_data = load_json(test_file)
        assert loaded_data == test_data
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)

def test_load_json_nonexistent():
    """Test load_json with nonexistent file"""
    result = load_json('/nonexistent/file.json')
    assert result is None

def test_format_size():
    """Test format_size function"""
    assert format_size(0) == "0B"
    assert format_size(512) == "512.00B"
    assert format_size(1024) == "1.00KB"
    assert format_size(1536) == "1.50KB"
    assert format_size(1048576) == "1.00MB"
    assert format_size(1073741824) == "1.00GB"
    assert format_size(1099511627776) == "1.00TB"

def test_format_timestamp():
    """Test format_timestamp function"""
    # Test with datetime object
    dt = datetime(2023, 12, 25, 15, 30, 45)
    result = format_timestamp(dt)
    assert result == "2023-12-25 15:30:45"

    # Test with ISO string
    iso_string = "2023-12-25T15:30:45"
    result = format_timestamp(iso_string)
    assert result == "2023-12-25 15:30:45"
