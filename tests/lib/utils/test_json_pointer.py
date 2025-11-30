"""Tests for JSONPointer utilities."""

import pytest
from json_schema_core.utils.json_pointer import parse_pointer, resolve_pointer
from json_schema_core.domain.errors import PathNotFoundError


def test_parse_pointer():
    """Test parsing a simple JSON Pointer."""
    result = parse_pointer("/title")
    assert result == ["title"]


def test_parse_nested_pointer():
    """Test parsing a nested JSON Pointer."""
    result = parse_pointer("/sections/0/paragraphs/1")
    assert result == ["sections", "0", "paragraphs", "1"]


def test_parse_root_pointer():
    """Test parsing root pointer."""
    result = parse_pointer("")
    assert result == []


def test_parse_pointer_with_special_chars():
    """Test parsing pointer with escaped characters."""
    # ~0 represents ~ and ~1 represents /
    result = parse_pointer("/field~0name")
    assert result == ["field~name"]
    
    result = parse_pointer("/field~1name")
    assert result == ["field/name"]


def test_resolve_pointer():
    """Test resolving a pointer to get a value."""
    document = {
        "title": "Test Document",
        "value": 42,
        "nested": {
            "field": "data"
        }
    }
    
    result = resolve_pointer(document, "/title")
    assert result == "Test Document"
    
    result = resolve_pointer(document, "/value")
    assert result == 42
    
    result = resolve_pointer(document, "/nested/field")
    assert result == "data"


def test_resolve_pointer_array():
    """Test resolving a pointer with array index."""
    document = {
        "items": ["first", "second", "third"]
    }
    
    result = resolve_pointer(document, "/items/0")
    assert result == "first"
    
    result = resolve_pointer(document, "/items/2")
    assert result == "third"


def test_resolve_pointer_complex():
    """Test resolving complex nested pointer."""
    document = {
        "sections": [
            {
                "title": "Section 1",
                "paragraphs": ["para1", "para2"]
            },
            {
                "title": "Section 2",
                "paragraphs": ["para3", "para4"]
            }
        ]
    }
    
    result = resolve_pointer(document, "/sections/0/title")
    assert result == "Section 1"
    
    result = resolve_pointer(document, "/sections/1/paragraphs/1")
    assert result == "para4"


def test_resolve_pointer_not_found():
    """Test that resolve_pointer raises detailed error for missing paths."""
    document = {
        "a": {
            "b": "value"
        }
    }
    
    # Try to access /a/b/c when /a/b is a string, not an object
    with pytest.raises(PathNotFoundError) as exc_info:
        resolve_pointer(document, "/a/b/c")
    
    error = exc_info.value
    assert error.path == "/a/b/c"
    # The error message should provide guidance
    assert "path" in str(error).lower()


def test_resolve_pointer_missing_intermediate():
    """Test error when intermediate path doesn't exist."""
    document = {
        "a": {
            "x": "value"
        }
    }
    
    # /a exists, but /a/b doesn't
    with pytest.raises(PathNotFoundError) as exc_info:
        resolve_pointer(document, "/a/b/c")
    
    error = exc_info.value
    assert error.path == "/a/b/c"


def test_resolve_root_pointer():
    """Test resolving root pointer returns whole document."""
    document = {"title": "Test", "value": 42}
    
    result = resolve_pointer(document, "")
    assert result == document
