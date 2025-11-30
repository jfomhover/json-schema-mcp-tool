"""JSON Pointer utilities for navigating JSON documents.

Implements RFC 6901 JSON Pointer specification.
"""

from typing import Any
from json_schema_core.domain.errors import PathNotFoundError


def parse_pointer(pointer: str) -> list[str]:
    """Parse a JSON Pointer into a list of path components.
    
    Args:
        pointer: JSON Pointer string (e.g., "/path/to/field")
        
    Returns:
        List of path components
        
    Examples:
        >>> parse_pointer("/title")
        ["title"]
        >>> parse_pointer("/sections/0/title")
        ["sections", "0", "title"]
        >>> parse_pointer("")
        []
    """
    if pointer == "":
        return []
    
    if not pointer.startswith("/"):
        raise ValueError(f"JSON Pointer must start with '/': {pointer}")
    
    # Remove leading slash and split
    parts = pointer[1:].split("/")
    
    # Unescape special characters per RFC 6901
    # ~1 represents / and ~0 represents ~
    unescaped = []
    for part in parts:
        part = part.replace("~1", "/")
        part = part.replace("~0", "~")
        unescaped.append(part)
    
    return unescaped


def resolve_pointer(document: dict, pointer: str) -> Any:
    """Resolve a JSON Pointer to get the value at that path.
    
    Args:
        document: JSON document to navigate
        pointer: JSON Pointer string
        
    Returns:
        Value at the pointer location
        
    Raises:
        PathNotFoundError: If the path doesn't exist, with detailed context
        
    Examples:
        >>> doc = {"title": "Test", "value": 42}
        >>> resolve_pointer(doc, "/title")
        "Test"
        >>> resolve_pointer(doc, "/value")
        42
    """
    parts = parse_pointer(pointer)
    
    # Root pointer returns whole document
    if not parts:
        return document
    
    current = document
    current_path = ""
    
    for i, part in enumerate(parts):
        current_path += f"/{part}"
        
        # Handle array indexing
        if isinstance(current, list):
            try:
                index = int(part)
                if index < 0 or index >= len(current):
                    raise PathNotFoundError(pointer)
                current = current[index]
            except (ValueError, IndexError):
                raise PathNotFoundError(pointer)
        
        # Handle dictionary access
        elif isinstance(current, dict):
            if part not in current:
                raise PathNotFoundError(pointer)
            current = current[part]
        
        # Can't navigate further into non-container types
        else:
            raise PathNotFoundError(pointer)
    
    return current
