"""
Configuration management for JSON Schema MCP Tool
"""
from pathlib import Path

from pydantic_settings import BaseSettings


class ServerConfig(BaseSettings):
    """Server configuration with sensible defaults"""

    schema_path: Path = Path("./schemas")
    storage_dir: Path = Path("./storage")
    lock_timeout: int = 30
    server_name: str = "json-schema-server"
