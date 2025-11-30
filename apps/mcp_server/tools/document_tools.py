"""MCP tools for document operations."""

from typing import Any

from json_schema_core.domain.errors import (
    DocumentNotFoundError,
    PathNotFoundError,
    ValidationFailedError,
    VersionConflictError,
)

from apps.mcp_server.server import MCPServer


def document_create(server: MCPServer, schema_id: str) -> dict:
    """
    Create a new document with auto-generated ID.

    Args:
        server: MCPServer instance
        schema_id: Schema ID to validate against

    Returns:
        dict with doc_id and version

    Raises:
        ValidationFailedError: If document cannot be created
            (e.g., required fields without defaults)
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


def document_read_node(doc_id: str, node_path: str, server: MCPServer) -> dict:
    """
    Read a node from a document.

    Args:
        doc_id: Document ID
        node_path: JSON Pointer path to the node (e.g., "/", "/title", "/sections/0")
        server: MCPServer instance

    Returns:
        dict with content and version

    Raises:
        DocumentNotFoundError: If document doesn't exist
        PathNotFoundError: If path doesn't exist in document
    """
    try:
        # Call DocumentService to read node
        content, version = server.document_service.read_node(
            doc_id=doc_id, node_path=node_path
        )

        return {"content": content, "version": version}

    except DocumentNotFoundError as e:
        return {
            "error": "document-not-found",
            "message": str(e),
            "doc_id": doc_id,
        }
    except PathNotFoundError as e:
        return {
            "error": "path-not-found",
            "message": str(e),
            "path": node_path,
        }
    except Exception as e:
        return {"error": "read-failed", "message": str(e)}


def document_update_node(
    doc_id: str, node_path: str, value: Any, expected_version: int, server: MCPServer
) -> dict:
    """
    Update a node in a document.

    Args:
        doc_id: Document ID
        node_path: JSON Pointer path to the node to update
        value: New value for the node
        expected_version: Expected version for optimistic locking
        server: MCPServer instance

    Returns:
        dict with updated content and new version

    Raises:
        DocumentNotFoundError: If document doesn't exist
        PathNotFoundError: If path doesn't exist
        VersionConflictError: If version doesn't match
        ValidationFailedError: If update violates schema
    """
    try:
        # Call DocumentService to update node
        content, version = server.document_service.update_node(
            doc_id=doc_id,
            node_path=node_path,
            value=value,
            expected_version=expected_version,
        )

        return {"content": content, "version": version}

    except DocumentNotFoundError as e:
        return {
            "error": "document-not-found",
            "message": str(e),
            "doc_id": doc_id,
        }
    except PathNotFoundError as e:
        return {
            "error": "path-not-found",
            "message": str(e),
            "path": node_path,
        }
    except VersionConflictError as e:
        return {
            "error": "version-conflict",
            "message": str(e),
            "expected": expected_version,
            "actual": e.actual_version if hasattr(e, "actual_version") else None,
        }
    except ValidationFailedError as e:
        return {
            "error": "validation-failed",
            "message": str(e),
            "details": e.errors if hasattr(e, "errors") else [],
        }
    except Exception as e:
        return {"error": "update-failed", "message": str(e)}


def document_create_node(
    doc_id: str, node_path: str, value: Any, expected_version: int, server: MCPServer
) -> dict:
    """
    Create a new node in a document (typically in an array).

    Args:
        doc_id: Document ID
        node_path: JSON Pointer path to the array or object to add to
        value: Value to add
        expected_version: Expected version for optimistic locking
        server: MCPServer instance

    Returns:
        dict with created_path and new version

    Raises:
        DocumentNotFoundError: If document doesn't exist
        PathNotFoundError: If path doesn't exist
        VersionConflictError: If version doesn't match
        ValidationFailedError: If creation violates schema
    """
    try:
        # Call DocumentService to create node (uses parent_path parameter)
        created_value, version = server.document_service.create_node(
            doc_id=doc_id,
            parent_path=node_path,
            value=value,
            expected_version=expected_version,
        )

        # Read back the parent to determine the index where the value was added
        # For arrays, the new item is at the end
        parent_content, _ = server.document_service.read_node(doc_id=doc_id, node_path=node_path)

        if isinstance(parent_content, list):
            # Find the index (last item)
            index = len(parent_content) - 1
            created_path = f"{node_path}/{index}"
        else:
            # For dicts or other types, just return the parent path
            created_path = node_path

        return {"created_path": created_path, "version": version}

    except DocumentNotFoundError as e:
        return {
            "error": "document-not-found",
            "message": str(e),
            "doc_id": doc_id,
        }
    except PathNotFoundError as e:
        return {
            "error": "path-not-found",
            "message": str(e),
            "path": node_path,
        }
    except VersionConflictError as e:
        return {
            "error": "version-conflict",
            "message": str(e),
            "expected": expected_version,
            "actual": e.actual_version if hasattr(e, "actual_version") else None,
        }
    except ValidationFailedError as e:
        return {
            "error": "validation-failed",
            "message": str(e),
            "details": e.errors if hasattr(e, "errors") else [],
        }
    except Exception as e:
        return {"error": "create-node-failed", "message": str(e)}


def document_delete_node(
    doc_id: str, node_path: str, expected_version: int, server: MCPServer
) -> dict:
    """
    Delete a node from a document.

    Args:
        doc_id: Document ID
        node_path: JSON Pointer path to the node to delete
        expected_version: Expected version for optimistic locking
        server: MCPServer instance

    Returns:
        dict with deleted content and new version

    Raises:
        DocumentNotFoundError: If document doesn't exist
        PathNotFoundError: If path doesn't exist
        VersionConflictError: If version doesn't match
        ValidationFailedError: If deletion violates schema
    """
    try:
        # Call DocumentService to delete node
        deleted_value, version = server.document_service.delete_node(
            doc_id=doc_id,
            node_path=node_path,
            expected_version=expected_version,
        )

        return {"content": deleted_value, "version": version}

    except DocumentNotFoundError as e:
        return {
            "error": "document-not-found",
            "message": str(e),
            "doc_id": doc_id,
        }
    except PathNotFoundError as e:
        return {
            "error": "path-not-found",
            "message": str(e),
            "path": node_path,
        }
    except VersionConflictError as e:
        return {
            "error": "version-conflict",
            "message": str(e),
            "expected": expected_version,
            "actual": e.actual_version if hasattr(e, "actual_version") else None,
        }
    except ValidationFailedError as e:
        return {
            "error": "validation-failed",
            "message": str(e),
            "details": e.errors if hasattr(e, "errors") else [],
        }
    except Exception as e:
        return {"error": "delete-node-failed", "message": str(e)}


def document_list(limit: int = 100, offset: int = 0, server: MCPServer = None) -> dict:
    """
    List all documents with metadata.

    Args:
        limit: Maximum number of documents to return (default 100)
        offset: Number of documents to skip (default 0)
        server: MCPServer instance

    Returns:
        dict with list of document metadata

    Raises:
        None - always returns a valid response
    """
    try:
        # Call DocumentService to list documents
        documents = server.document_service.list_documents(limit=limit, offset=offset)

        return {"documents": documents}

    except Exception as e:
        return {"error": "list-failed", "message": str(e)}





