"""Tests for MCP server initialization."""

import pytest


def test_server_creation(document_service):
    """Test that MCP server can be created."""
    from apps.mcp_server.server import MCPServer

    server = MCPServer(document_service)

    assert server is not None
    assert hasattr(server, "name")
    assert server.name == "json-schema-mcp-server"
