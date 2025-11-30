"""MCP tools for schema introspection operations."""

from json_schema_core.domain.errors import PathNotFoundError
from json_schema_core.utils.json_pointer import resolve_pointer

from apps.mcp_server.server import MCPServer


def schema_get_node(node_path: str, dereferenced: bool = True, server: MCPServer = None) -> dict:
    """
    Get the schema for a specific node path.

    Args:
        node_path: JSON Pointer path to the node (e.g., "/", "/title", "/properties/name")
        dereferenced: Whether to resolve $ref references (default True)
        server: MCPServer instance

    Returns:
        dict with schema definition

    Raises:
        PathNotFoundError: If path doesn't exist in schema
    """
    try:
        # Get the full schema
        # Note: We're using 'document' as the default schema ID for now
        # In a full implementation, this would be configurable
        schema = server.schema_service.load_schema("document")

        # Navigate to the requested path
        if node_path == "/":
            result_schema = schema
        else:
            result_schema = resolve_pointer(schema, node_path)

        return {"schema": result_schema}

    except PathNotFoundError as e:
        return {
            "error": "path-not-found",
            "message": str(e),
            "path": node_path,
        }
    except Exception as e:
        return {"error": "schema-get-node-failed", "message": str(e)}


def schema_get_root(dereferenced: bool = True, server: MCPServer = None) -> dict:
    """
    Get the root schema.

    Args:
        dereferenced: Whether to resolve $ref references (default True)
        server: MCPServer instance

    Returns:
        dict with root schema definition

    Raises:
        None - always returns a valid response
    """
    try:
        # Load the full schema
        # Note: We're using 'document' as the default schema ID for now
        schema = server.schema_service.load_schema("document")

        return {"schema": schema}

    except Exception as e:
        return {"error": "schema-get-root-failed", "message": str(e)}

