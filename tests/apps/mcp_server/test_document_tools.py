"""Tests for MCP document tools."""

import pytest


def test_document_create_success(mcp_server, sample_schema):
    """Test document_create tool creates document with auto-generated ID."""
    from apps.mcp_server.tools.document_tools import document_create

    # Call the tool
    result = document_create(mcp_server, sample_schema)

    # Should return dict with doc_id and version
    assert "doc_id" in result
    assert "version" in result
    assert result["version"] == 1

    # doc_id should be valid ULID format (26 characters)
    assert len(result["doc_id"]) == 26
    assert result["doc_id"].isalnum()

    # Verify document was actually created
    doc_id = result["doc_id"]
    content, version = mcp_server.document_service.read_node(doc_id=doc_id, node_path="/")
    assert version == 1
    # Document should have defaults applied
    assert "tags" in content
    assert content["tags"] == []
    assert "title" in content
    assert content["title"] == "Untitled"


def test_document_create_required_field_error(mcp_server, config):
    """Test document_create returns error if required field has no default."""
    from apps.mcp_server.tools.document_tools import document_create
    import json
    # Write a schema with a required field and no default
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string", "default": ""},
        },
        "required": ["title", "content"],
    }
    schema_file = config.schema_path / "required_no_default.json"
    with open(schema_file, "w") as f:
        json.dump(schema, f)
    # Copy to storage for schema service
    import shutil
    shutil.copy(schema_file, config.storage_dir / "required_no_default.json")
    # Call the tool
    result = document_create(mcp_server, "required_no_default")
    assert "error" in result
    assert result["error"] == "validation-failed"
    assert "title" in str(result["details"]).lower() or "title" in str(result["message"]).lower()


def test_document_read_node_success(mcp_server, sample_schema):
    """Test document_read_node tool reads root node successfully."""
    from apps.mcp_server.tools.document_tools import document_create, document_read_node

    # Create a document first
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Read the root node
    result = document_read_node(doc_id=doc_id, node_path="/", server=mcp_server)

    # Should return content and version
    assert "content" in result
    assert "version" in result
    assert result["version"] == 1

    # Content should have defaults applied
    content = result["content"]
    assert "tags" in content
    assert content["tags"] == []
    assert "title" in content
    assert content["title"] == "Untitled"


def test_document_read_node_nested(mcp_server, sample_schema):
    """Test document_read_node can read nested paths."""
    from apps.mcp_server.tools.document_tools import document_create, document_read_node

    # Create a document first
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Read just the title field
    result = document_read_node(doc_id=doc_id, node_path="/title", server=mcp_server)
    assert "content" in result
    assert result["content"] == "Untitled"

    # Read the tags array
    result = document_read_node(doc_id=doc_id, node_path="/tags", server=mcp_server)
    assert "content" in result
    assert result["content"] == []


def test_document_read_node_not_found(mcp_server):
    """Test document_read_node returns error for non-existent document."""
    from apps.mcp_server.tools.document_tools import document_read_node

    # Try to read a non-existent document
    result = document_read_node(doc_id="nonexistent", node_path="/", server=mcp_server)

    # Should return error response
    assert "error" in result
    assert result["error"] == "document-not-found"
    assert result["doc_id"] == "nonexistent"


def test_document_read_node_invalid_path(mcp_server, sample_schema):
    """Test document_read_node returns error for invalid path."""
    from apps.mcp_server.tools.document_tools import document_create, document_read_node

    # Create a document first
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Try to read a non-existent path
    result = document_read_node(doc_id=doc_id, node_path="/nonexistent", server=mcp_server)

    # Should return error response
    assert "error" in result
    assert result["error"] == "path-not-found"
    assert result["path"] == "/nonexistent"


def test_document_update_node_success(mcp_server, sample_schema):
    """Test document_update_node tool updates a node successfully."""
    from apps.mcp_server.tools.document_tools import document_create, document_update_node, document_read_node

    # Create a document first
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Update the title
    result = document_update_node(
        doc_id=doc_id, node_path="/title", value="New Title", expected_version=1, server=mcp_server
    )

    # Should return updated content and new version
    assert "content" in result
    assert "version" in result
    assert result["version"] == 2

    # Verify the update by reading back
    read_result = document_read_node(doc_id=doc_id, node_path="/title", server=mcp_server)
    assert read_result["content"] == "New Title"
    assert read_result["version"] == 2


def test_document_update_node_version_conflict(mcp_server, sample_schema):
    """Test document_update_node returns error on version conflict."""
    from apps.mcp_server.tools.document_tools import document_create, document_update_node

    # Create a document
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Update once (version 1 -> 2)
    document_update_node(
        doc_id=doc_id, node_path="/title", value="First Update", expected_version=1, server=mcp_server
    )

    # Try to update with old version (should fail)
    result = document_update_node(
        doc_id=doc_id, node_path="/title", value="Second Update", expected_version=1, server=mcp_server
    )

    # Should return version conflict error
    assert "error" in result
    assert result["error"] == "version-conflict"
    assert result["expected"] == 1
    # actual version should be 2


def test_document_update_node_validation_error(mcp_server, sample_schema):
    """Test document_update_node returns error on validation failure."""
    from apps.mcp_server.tools.document_tools import document_create, document_update_node

    # Create a document
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Try to update with invalid value (e.g., wrong type)
    result = document_update_node(
        doc_id=doc_id, node_path="/title", value=12345, expected_version=1, server=mcp_server
    )

    # Should return validation error
    assert "error" in result
    assert result["error"] == "validation-failed"


def test_document_create_node_success(mcp_server, sample_schema):
    """Test document_create_node tool creates a new node in an array."""
    from apps.mcp_server.tools.document_tools import document_create, document_create_node, document_read_node

    # Create a document
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Create a new tag in the tags array
    new_tag = "python"
    result = document_create_node(
        doc_id=doc_id, node_path="/tags", value=new_tag, expected_version=1, server=mcp_server
    )

    # Should return created_path and new version
    assert "created_path" in result
    assert "version" in result
    assert result["version"] == 2
    assert result["created_path"] == "/tags/0"

    # Verify by reading back the tags array
    read_result = document_read_node(doc_id=doc_id, node_path="/tags", server=mcp_server)
    assert read_result["content"] == ["python"]


def test_document_create_node_validation_error(mcp_server, sample_schema):
    """Test document_create_node returns error on validation failure."""
    from apps.mcp_server.tools.document_tools import document_create, document_create_node

    # Create a document
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Try to create a node with invalid data (e.g., wrong type for tags array)
    result = document_create_node(
        doc_id=doc_id, node_path="/tags", value=12345, expected_version=1, server=mcp_server
    )

    # Should return validation error
    assert "error" in result
    assert result["error"] == "validation-failed"


def test_document_delete_node_success(mcp_server, sample_schema):
    """Test document_delete_node tool deletes a node successfully."""
    from apps.mcp_server.tools.document_tools import (
        document_create,
        document_create_node,
        document_delete_node,
        document_read_node,
    )

    # Create a document
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Add two tags
    document_create_node(doc_id=doc_id, node_path="/tags", value="python", expected_version=1, server=mcp_server)
    document_create_node(doc_id=doc_id, node_path="/tags", value="rust", expected_version=2, server=mcp_server)

    # Delete the first tag
    result = document_delete_node(doc_id=doc_id, node_path="/tags/0", expected_version=3, server=mcp_server)

    # Should return deleted content and new version
    assert "content" in result
    assert "version" in result
    assert result["content"] == "python"
    assert result["version"] == 4

    # Verify by reading back the tags array
    read_result = document_read_node(doc_id=doc_id, node_path="/tags", server=mcp_server)
    assert read_result["content"] == ["rust"]


def test_document_delete_node_validation_error(mcp_server, sample_schema):
    """Test document_delete_node returns error on validation failure."""
    from apps.mcp_server.tools.document_tools import document_create, document_delete_node

    # Create a document
    create_result = document_create(mcp_server, sample_schema)
    doc_id = create_result["doc_id"]

    # Try to delete a required field (should fail validation)
    result = document_delete_node(doc_id=doc_id, node_path="/title", expected_version=1, server=mcp_server)

    # Should return validation error
    assert "error" in result
    assert result["error"] == "validation-failed"


def test_document_list_empty(mcp_server):
    """Test document_list tool returns empty list when no documents exist."""
    from apps.mcp_server.tools.document_tools import document_list

    # Call document_list
    result = document_list(server=mcp_server)

    # Should return empty list
    assert "documents" in result
    assert result["documents"] == []


def test_document_list_returns_metadata(mcp_server, sample_schema):
    """Test document_list returns document metadata."""
    from apps.mcp_server.tools.document_tools import document_create, document_list

    # Create 3 documents
    doc_ids = []
    for _ in range(3):
        create_result = document_create(mcp_server, sample_schema)
        doc_ids.append(create_result["doc_id"])

    # List all documents
    result = document_list(server=mcp_server)

    # Should return 3 documents with metadata
    assert "documents" in result
    assert len(result["documents"]) == 3
    
    # Check that each has the required metadata fields
    for doc in result["documents"]:
        assert "doc_id" in doc
        assert "version" in doc
        assert "created_at" in doc
        assert "updated_at" in doc


def test_document_list_pagination(mcp_server, sample_schema):
    """Test document_list supports pagination."""
    from apps.mcp_server.tools.document_tools import document_create, document_list

    # Create 5 documents
    for _ in range(5):
        document_create(mcp_server, sample_schema)

    # Get first 2
    result1 = document_list(limit=2, offset=0, server=mcp_server)
    assert len(result1["documents"]) == 2

    # Get next 2
    result2 = document_list(limit=2, offset=2, server=mcp_server)
    assert len(result2["documents"]) == 2

    # Get last 1
    result3 = document_list(limit=2, offset=4, server=mcp_server)
    assert len(result3["documents"]) == 1







