"""MCP Server implementation for JSON Schema document management."""

from mcp.server import Server

from json_schema_core.services.document_service import DocumentService
from json_schema_core.services.schema_service import SchemaService


class MCPServer:
    """MCP Server for document operations."""

    def __init__(self, document_service: DocumentService, schema_service: SchemaService = None):
        """
        Initialize MCP server with services.

        Args:
            document_service: DocumentService instance for document operations
            schema_service: SchemaService instance for schema introspection (optional)
        """
        self.document_service = document_service
        self.schema_service = schema_service
        self.name = "json-schema-mcp-server"
        self.server = Server(self.name)

