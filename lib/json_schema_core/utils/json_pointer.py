"""JSON Pointer utilities for navigating JSON documents.

Implements RFC 6901 JSON Pointer specification.
"""

import copy
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


def set_pointer(document: dict, pointer: str, value: Any) -> dict:
    """Set a value at a JSON Pointer location.
    
    Creates a new document with the value set. Does NOT modify the original.
    Does NOT auto-create intermediate paths - all parent paths must exist.
    
    Args:
        document: JSON document to modify
        pointer: JSON Pointer string
        value: Value to set
        
    Returns:
        New document with the value set
        
    Raises:
        PathNotFoundError: If the path doesn't exist (no auto-creation)
        
    Examples:
        >>> doc = {"title": "Test", "nested": {"field": "old"}}
        >>> set_pointer(doc, "/title", "New")
        {"title": "New", "nested": {"field": "old"}}
        >>> set_pointer(doc, "/nested/field", "new")
        {"title": "Test", "nested": {"field": "new"}}
    """
    parts = parse_pointer(pointer)
    
    if not parts:
        raise ValueError("Cannot set root pointer")
    
    # Deep copy to avoid modifying original
    result = copy.deepcopy(document)
    
    # Navigate to parent
    current = result
    for i, part in enumerate(parts[:-1]):
        if isinstance(current, list):
            try:
                index = int(part)
                if index < 0 or index >= len(current):
                    raise PathNotFoundError(pointer)
                current = current[index]
            except (ValueError, IndexError):
                raise PathNotFoundError(pointer)
        elif isinstance(current, dict):
            if part not in current:
                # NO auto-creation - path must exist
                raise PathNotFoundError(pointer)
            current = current[part]
        else:
            raise PathNotFoundError(pointer)
    
    # Set the final value
    final_part = parts[-1]
    if isinstance(current, list):
        try:
            index = int(final_part)
            if index < 0 or index >= len(current):
                raise PathNotFoundError(pointer)
            current[index] = value
        except (ValueError, IndexError):
            raise PathNotFoundError(pointer)
    elif isinstance(current, dict):
        # For set, we allow creating the final key
        current[final_part] = value
    else:
        raise PathNotFoundError(pointer)
    
    return result


def delete_pointer(document: dict, pointer: str) -> dict:
    """Delete a value at a JSON Pointer location.
    
    Creates a new document with the value deleted. Does NOT modify the original.
    
    Args:
        document: JSON document to modify
        pointer: JSON Pointer string
        
    Returns:
        New document with the value deleted
        
    Raises:
        PathNotFoundError: If the path doesn't exist
        
    Examples:
        >>> doc = {"title": "Test", "value": 42}
        >>> delete_pointer(doc, "/value")
        {"title": "Test"}
    """
    parts = parse_pointer(pointer)
    
    if not parts:
        raise ValueError("Cannot delete root pointer")
    
    # Deep copy to avoid modifying original
    result = copy.deepcopy(document)
    
    # Navigate to parent
    current = result
    for i, part in enumerate(parts[:-1]):
        if isinstance(current, list):
            try:
                index = int(part)
                if index < 0 or index >= len(current):
                    raise PathNotFoundError(pointer)
                current = current[index]
            except (ValueError, IndexError):
                raise PathNotFoundError(pointer)
        elif isinstance(current, dict):
            if part not in current:
                raise PathNotFoundError(pointer)
            current = current[part]
        else:
            raise PathNotFoundError(pointer)
    
    # Delete the final value
    final_part = parts[-1]
    if isinstance(current, list):
        try:
            index = int(final_part)
            if index < 0 or index >= len(current):
                raise PathNotFoundError(pointer)
            del current[index]
        except (ValueError, IndexError):
            raise PathNotFoundError(pointer)
    elif isinstance(current, dict):
        if final_part not in current:
            raise PathNotFoundError(pointer)
        del current[final_part]
    else:
        raise PathNotFoundError(pointer)
    
    return result
