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


def test_server_registers_tools(mcp_server):
    """Test that server registers MCP tools."""
    # For now, just check that the server has a list_tools method
    # We'll verify specific tools once they're implemented
    assert hasattr(mcp_server.server, "list_tools")
