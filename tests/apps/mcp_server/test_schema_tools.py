"""Tests for MCP schema tools."""



def test_schema_get_node_root(mcp_server):
    """Test schema_get_node tool returns root schema."""
    from apps.mcp_server.tools.schema_tools import schema_get_node

    # Get the root schema
    result = schema_get_node(node_path="/", dereferenced=True, server=mcp_server)

    # Should return schema dict
    assert "schema" in result
    schema = result["schema"]

    # Should be a valid schema object
    assert "type" in schema
    assert schema["type"] == "object"
    assert "properties" in schema


def test_schema_get_node_nested(mcp_server):
    """Test schema_get_node can get nested field schema."""
    from apps.mcp_server.tools.schema_tools import schema_get_node

    # Get schema for a specific field (in JSON Schema, properties are under /properties/<field>)
    result = schema_get_node(node_path="/properties/title", dereferenced=True, server=mcp_server)

    # Should return schema for the title field
    assert "schema" in result
    schema = result["schema"]

    # Title should be a string with default
    assert "type" in schema
    assert schema["type"] == "string"


def test_schema_get_node_invalid_path(mcp_server):
    """Test schema_get_node returns error for invalid path."""
    from apps.mcp_server.tools.schema_tools import schema_get_node

    # Try to get schema for non-existent path
    result = schema_get_node(node_path="/nonexistent", dereferenced=True, server=mcp_server)

    # Should return error response
    assert "error" in result
    assert result["error"] == "path-not-found"


def test_schema_get_root_dereferenced(mcp_server):
    """Test schema_get_root tool returns dereferenced schema."""
    from apps.mcp_server.tools.schema_tools import schema_get_root

    # Get the root schema dereferenced
    result = schema_get_root(dereferenced=True, server=mcp_server)

    # Should return schema
    assert "schema" in result
    schema = result["schema"]

    # Should be fully dereferenced (no $ref)
    assert "type" in schema
    # Check that it doesn't have $ref at the root level
    assert "$ref" not in schema


def test_schema_get_root_raw(mcp_server):
    """Test schema_get_root can return raw schema with $refs."""
    from apps.mcp_server.tools.schema_tools import schema_get_root

    # Get the root schema raw (with $refs intact)
    result = schema_get_root(dereferenced=False, server=mcp_server)

    # Should return schema
    assert "schema" in result
    schema = result["schema"]

    # Should be a valid schema
    assert "type" in schema
