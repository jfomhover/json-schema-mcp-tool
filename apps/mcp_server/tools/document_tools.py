"""MCP tools for document operations."""

from apps.mcp_server.server import MCPServer
from json_schema_core.domain.errors import ValidationFailedError


def document_create(server: MCPServer, schema_id: str) -> dict:
    """
    Create a new document with auto-generated ID.

    Args:
        server: MCPServer instance
        schema_id: Schema ID to validate against

    Returns:
        dict with doc_id and version

    Raises:
        ValidationFailedError: If document cannot be created (e.g., required fields without defaults)
    """
    try:
        # Create empty document - defaults will be applied by DocumentService
        empty_doc = {}

        # Call DocumentService to create document
        doc_id, metadata = server.document_service.create_document(
            schema_id=schema_id, document=empty_doc
        )

        return {"doc_id": str(doc_id), "version": metadata.version}

    except ValidationFailedError as e:
        # Return error response
        return {
            "error": "validation-failed",
            "message": str(e),
            "details": e.errors if hasattr(e, "errors") else [],
        }
    except Exception as e:
        # Catch any other errors
        return {"error": "creation-failed", "message": str(e)}
