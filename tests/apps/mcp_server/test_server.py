"""Tests for MCP server initialization."""

import pytest


def test_server_creation(document_service):
    """Test that MCP server can be created."""
    from apps.mcp_server.server import MCPServer

    server = MCPServer(document_service)

    assert server is not None
    assert hasattr(server, "name")
    assert server.name == "json-schema-mcp-server"


def test_server_has_services(mcp_server):
    """Test that server has document service dependency."""
    from json_schema_core.services.document_service import DocumentService

    assert hasattr(mcp_server, "document_service")
    assert isinstance(mcp_server.document_service, DocumentService)
