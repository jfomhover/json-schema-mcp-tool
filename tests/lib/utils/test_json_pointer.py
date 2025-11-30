"""Tests for JSONPointer utilities."""

import pytest
from json_schema_core.domain.errors import PathNotFoundError
from json_schema_core.utils.json_pointer import (
    delete_pointer,
    parse_pointer,
    resolve_pointer,
    set_pointer,
)


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
    document = {"title": "Test Document", "value": 42, "nested": {"field": "data"}}

    result = resolve_pointer(document, "/title")
    assert result == "Test Document"

    result = resolve_pointer(document, "/value")
    assert result == 42

    result = resolve_pointer(document, "/nested/field")
    assert result == "data"


def test_resolve_pointer_array():
    """Test resolving a pointer with array index."""
    document = {"items": ["first", "second", "third"]}

    result = resolve_pointer(document, "/items/0")
    assert result == "first"

    result = resolve_pointer(document, "/items/2")
    assert result == "third"


def test_resolve_pointer_complex():
    """Test resolving complex nested pointer."""
    document = {
        "sections": [
            {"title": "Section 1", "paragraphs": ["para1", "para2"]},
            {"title": "Section 2", "paragraphs": ["para3", "para4"]},
        ]
    }

    result = resolve_pointer(document, "/sections/0/title")
    assert result == "Section 1"

    result = resolve_pointer(document, "/sections/1/paragraphs/1")
    assert result == "para4"


def test_resolve_pointer_not_found():
    """Test that resolve_pointer raises detailed error for missing paths."""
    document = {"a": {"b": "value"}}

    # Try to access /a/b/c when /a/b is a string, not an object
    with pytest.raises(PathNotFoundError) as exc_info:
        resolve_pointer(document, "/a/b/c")

    error = exc_info.value
    assert error.path == "/a/b/c"
    # The error message should provide guidance
    assert "path" in str(error).lower()


def test_resolve_pointer_missing_intermediate():
    """Test error when intermediate path doesn't exist."""
    document = {"a": {"x": "value"}}

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


def test_set_pointer():
    """Test setting a value at a pointer location."""
    document = {"title": "Test", "nested": {"field": "old value"}}

    # Set simple field
    result = set_pointer(document, "/title", "New Title")
    assert result["title"] == "New Title"
    # Original should be unchanged (immutable)
    assert document["title"] == "Test"

    # Set nested field
    result = set_pointer(document, "/nested/field", "new value")
    assert result["nested"]["field"] == "new value"
    assert document["nested"]["field"] == "old value"


def test_set_pointer_array():
    """Test setting a value in an array."""
    document = {"items": ["first", "second", "third"]}

    result = set_pointer(document, "/items/1", "UPDATED")
    assert result["items"][1] == "UPDATED"
    assert result["items"][0] == "first"
    # Original unchanged
    assert document["items"][1] == "second"


def test_set_pointer_fails_missing_intermediate():
    """Test that set_pointer does NOT auto-create intermediate paths."""
    document = {"a": {"x": "value"}}

    # Try to set /a/b/c when /a/b doesn't exist
    # This should fail - no auto-creation
    with pytest.raises(PathNotFoundError) as exc_info:
        set_pointer(document, "/a/b/c", "value")

    error = exc_info.value
    assert error.path == "/a/b/c"
    assert "does not exist" in str(error).lower() or "not found" in str(error).lower()


def test_set_pointer_missing_parent():
    """Test that you can set a new key in an existing dict."""
    document = {"a": {"x": "value"}}

    # /a/b doesn't exist, but /a does, so we can set /a/b
    result = set_pointer(document, "/a/b", "new value")
    assert result["a"]["b"] == "new value"
    assert result["a"]["x"] == "value"
    # Original unchanged
    assert "b" not in document["a"]


def test_delete_pointer():
    """Test deleting a value at a pointer location."""
    document = {"title": "Test", "value": 42, "nested": {"field": "data", "other": "keep"}}

    # Delete simple field
    result = delete_pointer(document, "/value")
    assert "value" not in result
    assert result["title"] == "Test"
    # Original unchanged
    assert "value" in document

    # Delete nested field
    result = delete_pointer(document, "/nested/field")
    assert "field" not in result["nested"]
    assert result["nested"]["other"] == "keep"
    assert "field" in document["nested"]


def test_delete_pointer_array():
    """Test deleting an array element."""
    document = {"items": ["first", "second", "third"]}

    result = delete_pointer(document, "/items/1")
    assert result["items"] == ["first", "third"]
    # Original unchanged
    assert document["items"] == ["first", "second", "third"]


def test_delete_pointer_not_found():
    """Test that deleting non-existent path raises error."""
    document = {"a": {"b": "value"}}

    # Try to delete non-existent path
    with pytest.raises(PathNotFoundError) as exc_info:
        delete_pointer(document, "/a/b/c")

    error = exc_info.value
    assert error.path == "/a/b/c"


def test_delete_pointer_missing_field():
    """Test deleting a field that doesn't exist."""
    document = {"a": {"x": "value"}}

    with pytest.raises(PathNotFoundError):
        delete_pointer(document, "/a/missing")


def test_parse_pointer_invalid():
    """Test that pointer must start with /."""
    with pytest.raises(ValueError, match="must start with"):
        parse_pointer("invalid")


def test_set_pointer_root_error():
    """Test that cannot set root pointer."""
    document = {"a": "value"}

    with pytest.raises(ValueError, match="root"):
        set_pointer(document, "", {"new": "doc"})


def test_delete_pointer_root_error():
    """Test that cannot delete root pointer."""
    document = {"a": "value"}

    with pytest.raises(ValueError, match="root"):
        delete_pointer(document, "")
