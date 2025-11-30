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
    content, version = mcp_server.document_service.read_node(
        schema_id=sample_schema, doc_id=doc_id, node_path="/"
    )
    assert version == 1
    # Document should have defaults applied
    assert "tags" in content
    assert content["tags"] == []
