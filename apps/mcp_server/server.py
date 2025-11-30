"""MCP Server implementation for JSON Schema document management."""

from mcp.server import Server

from json_schema_core.services.document_service import DocumentService


class MCPServer:
    """MCP Server for document operations."""

    def __init__(self, document_service: DocumentService):
        """
        Initialize MCP server with document service.

        Args:
            document_service: DocumentService instance for document operations
        """
        self.document_service = document_service
        self.name = "json-schema-mcp-server"
        self.server = Server(self.name)
