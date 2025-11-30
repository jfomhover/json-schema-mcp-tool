"""
Tests for ServerConfig - Configuration management
"""
import pytest
from pathlib import Path


# P2.1.1: Test ServerConfig with default values


def test_config_defaults():
    """Test that ServerConfig has sensible default values"""
    from json_schema_core.config import ServerConfig

    config = ServerConfig()

    assert config.schema_path == Path("./schemas")
    assert config.storage_dir == Path("./storage")
    assert config.lock_timeout == 30
    assert config.server_name == "json-schema-server"
