"""Test fixtures for MCP server tests."""

import pytest
from pathlib import Path

from json_schema_core.config import ServerConfig
from json_schema_core.services.document_service import DocumentService
from json_schema_core.services.schema_service import SchemaService
from json_schema_core.services.validation_service import ValidationService
from json_schema_core.storage.file_storage import FileSystemStorage


@pytest.fixture
def config(tmp_path):
    """Return ServerConfig for tests."""
    schema_path = tmp_path / "schemas"
    storage_dir = tmp_path / "storage"
    schema_path.mkdir()
    storage_dir.mkdir()

    return ServerConfig(
        schema_path=schema_path,
        storage_dir=storage_dir,
        lock_timeout=30,
        server_name="test-mcp-server",
    )


@pytest.fixture
def sample_schema(config):
    """Create a sample schema file for testing."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}, "default": []},
        },
        "required": ["title"],
    }

    # Write schema to file
    schema_file = config.schema_path / "document.json"
    import json

    with open(schema_file, "w") as f:
        json.dump(schema, f)

    return "document"


@pytest.fixture
def document_service(config, sample_schema):
    """Return initialized DocumentService for tests."""
    storage = FileSystemStorage(config.storage_dir)
    
    # SchemaService needs schemas to be in storage
    # Copy schema to storage location
    import shutil
    schema_file = config.schema_path / f"{sample_schema}.json"
    storage_schema_file = config.storage_dir / f"{sample_schema}.json"
    shutil.copy(schema_file, storage_schema_file)
    
    schema_service = SchemaService(storage)

    service = DocumentService(storage, schema_service)

    return service


@pytest.fixture
def mcp_server(document_service):
    """Return MCP server instance for tests."""
    from apps.mcp_server.server import MCPServer

    return MCPServer(document_service)
