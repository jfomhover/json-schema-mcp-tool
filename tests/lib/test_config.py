"""
Tests for ServerConfig - Configuration management
"""
import pytest
from pathlib import Path
from pydantic import ValidationError


# P2.1.1: Test ServerConfig with default values


def test_config_defaults():
    """Test that ServerConfig has sensible default values"""
    from json_schema_core.config import ServerConfig

    config = ServerConfig()

    assert config.schema_path == Path("./schemas")
    assert config.storage_dir == Path("./storage")
    assert config.lock_timeout == 30
    assert config.server_name == "json-schema-server"


# P2.1.3: Test ServerConfig validates field types


def test_config_validates_lock_timeout_type():
    """Test that ServerConfig validates lock_timeout is an integer"""
    from json_schema_core.config import ServerConfig

    with pytest.raises(ValidationError) as exc_info:
        ServerConfig(lock_timeout="not_an_int")

    # Verify the error is about the lock_timeout field
    assert "lock_timeout" in str(exc_info.value).lower()


def test_config_validates_path_types():
    """Test that ServerConfig validates paths are Path-compatible"""
    from json_schema_core.config import ServerConfig

    # Pydantic will coerce strings to Path, so test with truly invalid type
    with pytest.raises(ValidationError) as exc_info:
        ServerConfig(schema_path=123)

    assert "schema_path" in str(exc_info.value).lower()


# P2.1.4: Test ServerConfig from dict


def test_config_from_dict():
    """Test that ServerConfig can be initialized from a dict"""
    from json_schema_core.config import ServerConfig

    config_dict = {
        "schema_path": "./custom/schemas",
        "storage_dir": "./custom/storage",
        "lock_timeout": 60,
        "server_name": "custom-server",
    }

    config = ServerConfig(**config_dict)

    assert config.schema_path == Path("./custom/schemas")
    assert config.storage_dir == Path("./custom/storage")
    assert config.lock_timeout == 60
    assert config.server_name == "custom-server"
