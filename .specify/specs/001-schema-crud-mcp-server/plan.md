# Technical Implementation Plan: JSON Schema CRUD MCP Server

**Feature Branch**: `001-schema-crud-mcp-server`  
**Created**: 2025-11-29  
**Status**: Planning  
**Implementation Language**: Python 3.11+  
**Target**: Model Context Protocol (MCP) Server

---

## Executive Summary

This plan outlines the implementation of a Python-based MCP server that provides document-centric CRUD operations on JSON documents validated against a JSON Schema. The server will be implemented in the `src/` directory with comprehensive documentation in `docs/`.

**Key Technologies:**
- Python 3.11+ (async/await, type hints)
- **Dual Interfaces**: MCP Python SDK (`mcp` package) + FastAPI REST framework
- jsonschema library (Draft 2020-12 support)
- ULID library for document IDs
- Pydantic for data validation and API models
- Uvicorn ASGI server for REST API
- Structured logging with Python logging module

**Architecture Pattern**: Layered architecture with clear separation of concerns:
1. **Interface Layer**: MCP tools + REST endpoints (dual entry points)
2. **Service Layer**: Business logic (document operations, validation) - shared by both interfaces
3. **Storage Layer**: File system abstraction
4. **Domain Layer**: Core entities and value objects

---

## Project Structure

```
json-schema-mcp-tool/
├── src/
│   └── json_schema_mcp/
│       ├── __init__.py
│       ├── __main__.py                 # Entry point for MCP: python -m json_schema_mcp
│       ├── server.py                   # MCP server initialization
│       ├── api_server.py               # REST API server initialization (FastAPI app)
│       ├── config.py                   # Configuration management
│       │
│       ├── mcp_tools/                  # MCP tool implementations
│       │   ├── __init__.py
│       │   ├── document_tools.py       # document_create, document_read_node, etc.
│       │   ├── schema_tools.py         # schema_get_node, schema_get_root
│       │   └── tool_registry.py        # Tool registration and metadata
│       │
│       ├── rest_api/                   # REST API implementations
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── documents.py        # Document CRUD endpoints
│       │   │   ├── schema.py           # Schema introspection endpoints
│       │   │   └── health.py           # Health check endpoint
│       │   ├── models.py               # Pydantic request/response models
│       │   └── middleware.py           # CORS, error handling middleware
│       │
│       ├── services/                   # Business logic layer (SHARED by both interfaces)
│       │   ├── __init__.py
│       │   ├── document_service.py     # Document CRUD operations
│       │   ├── validation_service.py   # JSON Schema validation
│       │   ├── schema_service.py       # Schema loading and introspection
│       │   └── lock_service.py         # Document-level locking
│       │
│       ├── storage/                    # Storage abstraction layer
│       │   ├── __init__.py
│       │   ├── storage_interface.py    # Abstract base class
│       │   ├── file_storage.py         # Local file system implementation
│       │   └── metadata.py             # Metadata file handling
│       │
│       ├── domain/                     # Domain models and value objects
│       │   ├── __init__.py
│       │   ├── document.py             # Document entity
│       │   ├── metadata.py             # DocumentMetadata entity
│       │   ├── path.py                 # JSONPointer value object
│       │   └── errors.py               # Domain exceptions
│       │
│       └── utils/                      # Shared utilities
│           ├── __init__.py
│           ├── json_pointer.py         # RFC 6901 implementation
│           ├── ulid_generator.py       # ULID generation
│           └── atomic_write.py         # Write-then-rename helpers
│
├── docs/                               # Comprehensive documentation
│   ├── index.md                        # Documentation home
│   ├── architecture/
│   │   ├── overview.md                 # System architecture (dual interfaces)
│   │   ├── layers.md                   # Layer responsibilities
│   │   ├── data-flow.md                # Request flow diagrams (MCP + REST)
│   │   └── concurrency.md              # Locking and versioning
│   ├── api/
│   │   ├── mcp-tools.md                # MCP tool reference
│   │   ├── rest-endpoints.md           # REST API reference
│   │   ├── error-codes.md              # Complete error catalog
│   │   └── examples.md                 # Usage examples (both interfaces)
│   ├── operations/
│   │   ├── configuration.md            # Server configuration
│   │   ├── deployment.md               # Running the servers (MCP + REST)
│   │   └── troubleshooting.md          # Common issues
│   └── development/
│       ├── setup.md                    # Development environment
│       ├── testing.md                  # Test strategy (both interfaces)
│       └── contributing.md             # Contribution guidelines
│
├── tests/                              # Test suite (TDD approach)
│   ├── unit/
│   │   ├── test_document_service.py
│   │   ├── test_validation_service.py
│   │   ├── test_file_storage.py
│   │   └── test_json_pointer.py
│   ├── integration/
│   │   ├── test_mcp_tools.py
│   │   ├── test_rest_api.py            # REST endpoint tests
│   │   └── test_atomic_operations.py
│   └── fixtures/
│       ├── schemas/                    # Test JSON schemas
│       └── documents/                  # Test documents
│
├── pyproject.toml                      # Python project config (Poetry/pip)
├── requirements.txt                    # Production dependencies
├── requirements-dev.txt                # Development dependencies
└── config.example.json                 # Example configuration file
```

---

## Phase 1: Foundation & Core Infrastructure (Week 1)

### 1.1 Project Setup

**Goal**: Establish Python project structure with dependencies and tooling.

**Tasks:**
- [ ] Create Python package structure under `src/json_schema_mcp/`
- [ ] Set up `pyproject.toml` with Poetry or setup.py
- [ ] Configure development tools:
  - [ ] Black (code formatting)
  - [ ] Pylint/Flake8 (linting)
  - [ ] MyPy (type checking)
  - [ ] Pytest (testing)
- [ ] Create virtual environment management script
- [ ] Set up pre-commit hooks

**Dependencies to Install:**
```toml
[tool.poetry.dependencies]
python = "^3.11"
mcp = "^1.0.0"                    # MCP Python SDK
jsonschema = "^4.20.0"            # JSON Schema validation (Draft 2020-12)
python-ulid = "^2.0.0"            # ULID generation
pydantic = "^2.5.0"               # Data validation, settings, and API models
fastapi = "^0.109.0"              # REST API framework (NEW)
uvicorn = "^0.27.0"               # ASGI server for FastAPI (NEW)
python-multipart = "^0.0.6"       # FastAPI form data support (NEW)
```

**Deliverables:**
- ✅ Working virtual environment
- ✅ All dependencies installed
- ✅ Project importable: `python -m json_schema_mcp --version`

---

### 1.2 Configuration Management (FR-001a to FR-001f)

**Goal**: Implement configuration loading with environment variables and config file support.

**Implementation:**
```python
# src/json_schema_mcp/config.py
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Literal

class ServerConfig(BaseSettings):
    """Server configuration with precedence: env vars > config file > defaults"""
    
    # Required
    schema_path: Path
    
    # Optional with defaults
    storage_dir: Path = Path("./data")
    log_level: Literal["debug", "info", "warn", "error"] = "info"
    
    # Internal
    config_file: Path = Path("./config.json")
    
    class Config:
        env_prefix = ""  # No prefix, direct env var names
        env_file_encoding = "utf-8"
        case_sensitive = False
```

**Tasks:**
- [ ] Implement `ServerConfig` with Pydantic BaseSettings
- [ ] Add config file loading (JSON format)
- [ ] Implement precedence: env vars → config file → defaults
- [ ] Add config validation (schema_path exists, storage_dir writable)
- [ ] Create `config.example.json` template

**Test Cases:**
- Load from environment variables only
- Load from config file only
- Environment variables override config file
- Validation fails for missing schema_path
- Validation fails for non-writable storage_dir

**Deliverables:**
- ✅ `config.py` module with full type hints
- ✅ Config validation with clear error messages
- ✅ Example config file

---

### 1.3 Domain Models (FR-010, FR-107-111)

**Goal**: Create core domain entities with proper encapsulation.

**Implementation:**
```python
# src/json_schema_mcp/domain/document.py
from dataclasses import dataclass
from typing import Any
import json

@dataclass(frozen=True)
class DocumentId:
    """ULID-based document identifier (value object)"""
    value: str
    
    def __post_init__(self):
        if len(self.value) != 26:
            raise ValueError("doc_id must be 26 characters (ULID format)")
    
    def __str__(self) -> str:
        return self.value

@dataclass
class Document:
    """
    Document entity with content only.
    
    IMPORTANT: Version is NOT stored here - it lives in DocumentMetadata 
    in separate .meta.json file (FR-016d). Document entity only contains
    the actual JSON content that gets validated against schema.
    """
    doc_id: DocumentId
    content: dict[str, Any]
    
    def to_json(self) -> str:
        """Serialize document content to JSON (no version in output)"""
        return json.dumps(self.content, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, doc_id: DocumentId, json_str: str) -> "Document":
        """Deserialize document from JSON (version comes from separate metadata file)"""
        content = json.loads(json_str)
        return cls(doc_id=doc_id, content=content)
```

```python
# src/json_schema_mcp/domain/metadata.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

@dataclass
class DocumentMetadata:
    """Document metadata stored in separate .meta.json file (FR-016a to FR-016d)"""
    doc_id: str
    version: int
    schema_uri: str
    created_at: datetime
    modified_at: datetime
    content_size_bytes: int
    
    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "version": self.version,
            "schema_uri": self.schema_uri,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "content_size_bytes": self.content_size_bytes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DocumentMetadata":
        return cls(
            doc_id=data["doc_id"],
            version=data["version"],
            schema_uri=data["schema_uri"],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            content_size_bytes=data["content_size_bytes"]
        )
```

**Tasks:**
- [ ] Create `DocumentId` value object with ULID validation
- [ ] Create `Document` entity with serialization
- [ ] Create `DocumentMetadata` entity with dict conversion
- [ ] Create `JSONPointer` value object (RFC 6901)
- [ ] Define domain exceptions hierarchy

**Test Cases:**
- DocumentId validation (length, format)
- Document JSON serialization/deserialization
- Metadata datetime handling
- JSONPointer path validation

**Deliverables:**
- ✅ Complete domain model with type hints
- ✅ Immutable value objects where appropriate
- ✅ Domain exceptions with clear messages

---

### 1.4 JSON Pointer Implementation (FR-021 to FR-025)

**Goal**: RFC 6901 compliant JSON Pointer implementation.

**Implementation:**
```python
# src/json_schema_mcp/utils/json_pointer.py
from typing import Any

class JSONPointer:
    """RFC 6901 JSON Pointer implementation"""
    
    def __init__(self, path: str):
        if not path.startswith("/"):
            raise ValueError("JSON Pointer must start with '/'")
        self.path = path
        self.tokens = self._parse_tokens(path)
    
    def _parse_tokens(self, path: str) -> list[str]:
        """Parse path into tokens, handling escaping"""
        if path == "/":
            return []
        tokens = path[1:].split("/")
        # Unescape ~1 to / and ~0 to ~
        return [t.replace("~1", "/").replace("~0", "~") for t in tokens]
    
    def resolve(self, document: dict) -> Any:
        """
        Resolve pointer against document, returns value at path.
        Raises PathNotFoundError with deepest ancestor if path doesn't exist (FR-092, FR-093).
        """
        current = document
        current_path = ""
        
        for i, token in enumerate(self.tokens):
            parent = current
            parent_path = current_path
            current_path = "/" + "/".join(self.tokens[:i+1])
            
            if isinstance(current, dict):
                if token not in current:
                    # Path not found - include deepest existing ancestor (FR-093)
                    raise PathNotFoundError(
                        path=self.path,
                        deepest_ancestor=parent_path if parent_path else "/"
                    )
                current = current[token]
            elif isinstance(current, list):
                try:
                    index = int(token)
                    if index < 0:  # FR-024: Handle negative indices post-MVP
                        raise ValueError("Negative indices not supported in MVP")
                    current = current[index]
                except (ValueError, IndexError) as e:
                    # Path not found in array
                    raise PathNotFoundError(
                        path=self.path,
                        deepest_ancestor=parent_path if parent_path else "/"
                    ) from e
            else:
                # Trying to traverse into primitive value (string, number, etc.)
                raise PathNotFoundError(
                    path=self.path,
                    deepest_ancestor=parent_path if parent_path else "/"
                )
        
        return current
    
    def find_deepest_ancestor(self, document: dict) -> str:
        """
        Find the deepest existing path in document (FR-093).
        Used for error messages to guide users on which path to create first.
        Returns: JSON Pointer to deepest existing ancestor.
        """
        if not self.tokens:
            return "/"
        
        current = document
        deepest = "/"
        
        for i, token in enumerate(self.tokens):
            if isinstance(current, dict):
                if token not in current:
                    return deepest
                current = current[token]
                deepest = "/" + "/".join(self.tokens[:i+1])
            elif isinstance(current, list):
                try:
                    index = int(token)
                    if index < 0 or index >= len(current):
                        return deepest
                    current = current[index]
                    deepest = "/" + "/".join(self.tokens[:i+1])
                except (ValueError, IndexError):
                    return deepest
            else:
                # Hit a primitive - can't go deeper
                return deepest
        
        return deepest
    
    def set_value(self, document: dict, value: Any) -> dict:
        """Set value at pointer path in document (returns modified copy)"""
        # Implementation for update operations
        pass
    
    def append_to_array(self, document: dict, value: Any) -> dict:
        """Append value to array at pointer path (/-  notation)"""
        # Implementation for array append
        pass
```

**Tasks:**
- [ ] Implement token parsing with escaping (~0, ~1)
- [ ] Implement `resolve()` for reading values
- [ ] Implement `set_value()` for updates
- [ ] Implement `append_to_array()` for /- notation
- [ ] Add path validation and error handling
- [ ] Document negative index behavior (not supported in MVP)

**Test Cases:**
- Root path "/"
- Simple paths "/metadata/title"
- Array indexing "/chapters/0/title"
- Escaping ~0 and ~1
- Path not found errors with deepest ancestor tracking (FR-093)
- Array append notation "/-"
- Intermediate path missing - error includes ancestor and guidance
- find_deepest_ancestor() returns correct path for various scenarios

**Deliverables:**
- ✅ RFC 6901 compliant implementation
- ✅ Comprehensive error messages with ancestor tracking
- ✅ 100% test coverage for path operations
- ✅ Explicit guidance for missing intermediate paths (FR-094)

---

## Phase 2: Storage Layer (Week 2)

### 2.1 Storage Interface & File Storage (FR-015 to FR-020)

**Goal**: Implement storage abstraction with local file system backend.

**Implementation:**
```python
# src/json_schema_mcp/storage/storage_interface.py
from abc import ABC, abstractmethod
from typing import Optional
from ..domain.document import Document, DocumentId
from ..domain.metadata import DocumentMetadata

class StorageAdapter(ABC):
    """Abstract storage interface for future extensibility (FR-020)"""
    
    @abstractmethod
    async def save(self, document: Document, metadata: DocumentMetadata) -> None:
        """Save document and metadata atomically"""
        pass
    
    @abstractmethod
    async def load(self, doc_id: DocumentId) -> tuple[Document, DocumentMetadata]:
        """Load document and metadata"""
        pass
    
    @abstractmethod
    async def exists(self, doc_id: DocumentId) -> bool:
        """Check if document exists"""
        pass
    
    @abstractmethod
    async def delete(self, doc_id: DocumentId) -> None:
        """Delete document and metadata"""
        pass
    
    @abstractmethod
    async def list_all(self) -> list[DocumentMetadata]:
        """List all document metadata"""
        pass
```

```python
# src/json_schema_mcp/storage/file_storage.py
from pathlib import Path
import json
import os
from .storage_interface import StorageAdapter

class FileSystemStorage(StorageAdapter):
    """Local file system storage implementation (FR-015 to FR-020)"""
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Create storage directory if missing (FR-104)"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(self.storage_dir, os.W_OK):
            raise PermissionError(f"Storage directory not writable: {self.storage_dir}")
    
    async def save(self, document: Document, metadata: DocumentMetadata) -> None:
        """
        Atomic save using write-then-rename strategy (FR-018 to FR-018d)
        1. Write to .tmp files
        2. fsync() both files
        3. Atomic rename to .json files
        """
        doc_id_str = str(document.doc_id)
        
        # Paths
        content_path = self.storage_dir / f"{doc_id_str}.json"
        content_tmp = self.storage_dir / f"{doc_id_str}.tmp"
        meta_path = self.storage_dir / f"{doc_id_str}.meta.json"
        meta_tmp = self.storage_dir / f"{doc_id_str}.meta.tmp"
        
        try:
            # Write content to temp file
            with open(content_tmp, "w", encoding="utf-8") as f:
                f.write(document.to_json())
                f.flush()
                os.fsync(f.fileno())  # FR-018b
            
            # Write metadata to temp file
            with open(meta_tmp, "w", encoding="utf-8") as f:
                json.dump(metadata.to_dict(), f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # FR-018b
            
            # Atomic rename (FR-018c)
            os.replace(content_tmp, content_path)  # Atomic on POSIX/Windows
            os.replace(meta_tmp, meta_path)
            
        except Exception as e:
            # Cleanup temp files on error
            content_tmp.unlink(missing_ok=True)
            meta_tmp.unlink(missing_ok=True)
            raise StorageError(f"Failed to save document {doc_id_str}") from e
    
    async def load(self, doc_id: DocumentId) -> tuple[Document, DocumentMetadata]:
        """Load document and metadata from disk"""
        doc_id_str = str(doc_id)
        content_path = self.storage_dir / f"{doc_id_str}.json"
        meta_path = self.storage_dir / f"{doc_id_str}.meta.json"
        
        # Check both files exist
        if not content_path.exists():
            raise DocumentNotFoundError(doc_id_str)
        if not meta_path.exists():
            raise MetadataNotFoundError(doc_id_str)
        
        # Load content
        with open(content_path, "r", encoding="utf-8") as f:
            content_json = f.read()
        
        # Load metadata
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata_dict = json.load(f)
        
        metadata = DocumentMetadata.from_dict(metadata_dict)
        document = Document.from_json(doc_id, content_json, metadata.version)
        
        return document, metadata
    
    def cleanup_temp_files(self) -> None:
        """Cleanup orphaned .tmp files on startup (FR-018d)"""
        for tmp_file in self.storage_dir.glob("*.tmp"):
            tmp_file.unlink()
        for tmp_file in self.storage_dir.glob("*.meta.tmp"):
            tmp_file.unlink()
```

**Tasks:**
- [ ] Implement `StorageAdapter` abstract interface
- [ ] Implement `FileSystemStorage` with atomic writes
- [ ] Implement write-then-rename strategy with fsync()
- [ ] Add startup cleanup for orphaned .tmp files
- [ ] Handle file system errors gracefully
- [ ] Add metadata file handling (see Phase 2.3)

**Test Cases:**
- Save and load document successfully
- Atomic rename on write failure
- Cleanup temp files on startup
- Handle missing content/metadata files
- File system permission errors
- Concurrent write attempts (next phase)

**Deliverables:**
- ✅ Storage abstraction ready for cloud migration
- ✅ Atomic file operations
- ✅ Comprehensive error handling

---

### 2.3 Metadata File Storage (FR-016a to FR-016d)

**Goal**: Implement separate metadata file storage for version tracking and document metadata.

**Context**: The spec requires TWO files per document:
- `{doc_id}.json` - Document content (without version)
- `{doc_id}.meta.json` - Metadata including version counter

This separation is critical because:
1. Version counter must persist across operations (FR-075a, FR-076)
2. Version stored in metadata only, NOT in document content (FR-016d)
3. Metadata can be queried without parsing large document content
4. Clean separation of concerns (content vs. system metadata)

**Implementation:**
```python
# src/json_schema_mcp/storage/metadata.py
from pathlib import Path
from datetime import datetime
import json
import os
from ..domain.metadata import DocumentMetadata

class MetadataFileHandler:
    """Handles .meta.json file operations (FR-016a to FR-016d)"""
    
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
    
    def save_metadata(self, metadata: DocumentMetadata) -> None:
        """
        Save metadata to .meta.json file atomically (FR-016c).
        Uses write-then-rename strategy: write to .meta.tmp, fsync, rename.
        """
        doc_id_str = metadata.doc_id
        meta_path = self.storage_dir / f"{doc_id_str}.meta.json"
        meta_tmp = self.storage_dir / f"{doc_id_str}.meta.tmp"
        
        try:
            # Write to temp file
            with open(meta_tmp, "w", encoding="utf-8") as f:
                json.dump(metadata.to_dict(), f, indent=2)
                f.flush()
                os.fsync(f.fileno())  # FR-016c: Ensure durability
            
            # Atomic rename (FR-016c)
            os.replace(meta_tmp, meta_path)
            
        except Exception as e:
            meta_tmp.unlink(missing_ok=True)
            raise MetadataWriteError(f"Failed to save metadata for {doc_id_str}") from e
    
    def load_metadata(self, doc_id: str) -> DocumentMetadata:
        """
        Load metadata from .meta.json file (FR-016b).
        Raises MetadataNotFoundError if file doesn't exist.
        """
        meta_path = self.storage_dir / f"{doc_id}.meta.json"
        
        if not meta_path.exists():
            raise MetadataNotFoundError(f"Metadata file not found: {doc_id}")
        
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return DocumentMetadata.from_dict(data)
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise MetadataCorruptedError(f"Corrupted metadata file: {doc_id}") from e
    
    def delete_metadata(self, doc_id: str) -> None:
        """Delete metadata file"""
        meta_path = self.storage_dir / f"{doc_id}.meta.json"
        meta_path.unlink(missing_ok=True)
    
    def exists(self, doc_id: str) -> bool:
        """Check if metadata file exists"""
        meta_path = self.storage_dir / f"{doc_id}.meta.json"
        return meta_path.exists()
    
    def verify_consistency(self, doc_id: str) -> tuple[bool, bool]:
        """
        Verify both content and metadata files exist (edge case handling).
        Returns: (content_exists, metadata_exists)
        Used for startup verification and corruption detection.
        """
        content_path = self.storage_dir / f"{doc_id}.json"
        meta_path = self.storage_dir / f"{doc_id}.meta.json"
        return (content_path.exists(), meta_path.exists())
```

**Updated FileSystemStorage.save():**
```python
async def save(self, document: Document, metadata: DocumentMetadata) -> None:
    """
    Atomic save using write-then-rename strategy (FR-018 to FR-018d).
    Saves BOTH files: {doc_id}.json (content) AND {doc_id}.meta.json (metadata).
    """
    doc_id_str = str(document.doc_id)
    
    # Paths
    content_path = self.storage_dir / f"{doc_id_str}.json"
    content_tmp = self.storage_dir / f"{doc_id_str}.tmp"
    
    try:
        # Write content to temp file
        with open(content_tmp, "w", encoding="utf-8") as f:
            f.write(document.to_json())  # Document.to_json() does NOT include version
            f.flush()
            os.fsync(f.fileno())  # FR-018b
        
        # Write metadata to separate file (FR-016a)
        self.metadata_handler.save_metadata(metadata)  # Uses its own .meta.tmp → .meta.json
        
        # Atomic rename content file (FR-018c)
        os.replace(content_tmp, content_path)
        
    except Exception as e:
        # Cleanup temp files on error
        content_tmp.unlink(missing_ok=True)
        # Metadata handler cleans up its own .meta.tmp
        raise StorageError(f"Failed to save document {doc_id_str}") from e
```

**Updated FileSystemStorage.load():**
```python
async def load(self, doc_id: DocumentId) -> tuple[Document, DocumentMetadata]:
    """
    Load document and metadata from BOTH files (FR-016a).
    Returns tuple of (Document, DocumentMetadata).
    """
    doc_id_str = str(doc_id)
    content_path = self.storage_dir / f"{doc_id_str}.json"
    
    # Check both files exist (edge case handling)
    content_exists, meta_exists = self.metadata_handler.verify_consistency(doc_id_str)
    
    if not content_exists:
        if meta_exists:
            # Orphaned metadata file - corruption scenario
            raise DocumentCorruptedError(
                f"Content file missing but metadata exists: {doc_id_str}"
            )
        else:
            raise DocumentNotFoundError(doc_id_str)
    
    if not meta_exists:
        # Content exists but metadata missing - corruption scenario
        raise MetadataNotFoundError(
            f"Metadata file missing for document: {doc_id_str}. "
            f"Document may be corrupted. Consider regenerating metadata."
        )
    
    # Load content
    with open(content_path, "r", encoding="utf-8") as f:
        content_json = f.read()
    
    # Load metadata
    metadata = self.metadata_handler.load_metadata(doc_id_str)
    
    # Create Document entity (no version attribute - version is in metadata)
    document = Document.from_json(doc_id, content_json)
    
    return document, metadata
```

**Startup Verification:**
```python
def verify_storage_integrity(self) -> list[str]:
    """
    Verify storage integrity on startup (edge case handling).
    Returns list of corrupted document IDs that need attention.
    """
    corrupted = []
    
    # Find all .json files
    for content_file in self.storage_dir.glob("*.json"):
        doc_id = content_file.stem
        content_exists, meta_exists = self.metadata_handler.verify_consistency(doc_id)
        
        if content_exists and not meta_exists:
            corrupted.append(f"{doc_id}: missing metadata file")
        elif meta_exists and not content_exists:
            corrupted.append(f"{doc_id}: missing content file")
    
    return corrupted
```

**Tasks:**
- [ ] Implement `MetadataFileHandler` class with atomic writes
- [ ] Update `FileSystemStorage.save()` to write both files
- [ ] Update `FileSystemStorage.load()` to read both files with consistency checks
- [ ] Add `verify_storage_integrity()` startup check
- [ ] Handle edge cases: missing content, missing metadata, both missing
- [ ] Add metadata file cleanup in `cleanup_temp_files()`

**Test Cases:**
- Save document and metadata atomically - both files created
- Load document and metadata - both files read correctly
- Missing content file with existing metadata - raise DocumentCorruptedError
- Missing metadata file with existing content - raise MetadataNotFoundError
- Both files missing - raise DocumentNotFoundError
- Corrupted metadata JSON - raise MetadataCorruptedError
- Startup verification detects orphaned files
- Version increments correctly stored in metadata file only

**Deliverables:**
- ✅ Two-file storage system fully implemented
- ✅ Version counter persisted in .meta.json only
- ✅ Edge case handling for file corruption
- ✅ Startup integrity verification

---

### 2.4 Error Code System (FR-095 to FR-099)

**Goal**: Implement complete error code taxonomy before services need to throw errors.

**Context**: The spec defines 22 exhaustive error codes with categories, remediation, and causes. Services (Phase 3-4) will need to throw these errors, so we need the error system early.

**Implementation:**
```python
# src/json_schema_mcp/domain/errors.py
from enum import Enum
from typing import Optional, Any
from dataclasses import dataclass, field

class ErrorCategory(Enum):
    """HTTP-style error categories (FR-096)"""
    CLIENT_ERROR = "4xx"
    SERVER_ERROR = "5xx"

class ErrorCode(Enum):
    """
    Exhaustive enumeration of ALL error codes (FR-095).
    Each code has: identifier, category, description.
    """
    # Client Errors (4xx)
    INVALID_DOC_ID = ("invalid-doc-id", ErrorCategory.CLIENT_ERROR, "doc_id format is invalid")
    DOCUMENT_NOT_FOUND = ("document-not-found", ErrorCategory.CLIENT_ERROR, "Document doesn't exist")
    PATH_NOT_FOUND = ("path-not-found", ErrorCategory.CLIENT_ERROR, "JSON Pointer path doesn't exist")
    PATH_INVALID = ("path-invalid", ErrorCategory.CLIENT_ERROR, "JSON Pointer syntax malformed")
    CONFLICT = ("conflict", ErrorCategory.CLIENT_ERROR, "Resource already exists")
    VERSION_CONFLICT = ("version-conflict", ErrorCategory.CLIENT_ERROR, "Document version mismatch")
    LOCK_TIMEOUT = ("lock-timeout", ErrorCategory.CLIENT_ERROR, "Failed to acquire lock")
    
    # Validation Errors (422 category)
    REQUIRED_FIELD_WITHOUT_DEFAULT = ("required-field-without-default", ErrorCategory.CLIENT_ERROR, "Required field has no default")
    TYPE_MISMATCH = ("type-mismatch", ErrorCategory.CLIENT_ERROR, "Value type doesn't match schema")
    REQUIRED_MISSING = ("required-missing", ErrorCategory.CLIENT_ERROR, "Required field missing")
    MIN_LENGTH = ("min-length", ErrorCategory.CLIENT_ERROR, "String too short")
    MAX_LENGTH = ("max-length", ErrorCategory.CLIENT_ERROR, "String too long")
    PATTERN_FAILED = ("pattern-failed", ErrorCategory.CLIENT_ERROR, "Pattern mismatch")
    ENUM_MISMATCH = ("enum-mismatch", ErrorCategory.CLIENT_ERROR, "Value not in enum")
    MIN_ITEMS = ("min-items", ErrorCategory.CLIENT_ERROR, "Array too small")
    MAX_ITEMS = ("max-items", ErrorCategory.CLIENT_ERROR, "Array too large")
    MINIMUM = ("minimum", ErrorCategory.CLIENT_ERROR, "Number too small")
    MAXIMUM = ("maximum", ErrorCategory.CLIENT_ERROR, "Number too large")
    FORMAT_INVALID = ("format-invalid", ErrorCategory.CLIENT_ERROR, "Format constraint violated")
    ADDITIONAL_PROPERTIES_FORBIDDEN = ("additional-properties-forbidden", ErrorCategory.CLIENT_ERROR, "Extra properties not allowed")
    
    # Server Errors (5xx)
    SCHEMA_LOAD_FAILED = ("schema-load-failed", ErrorCategory.SERVER_ERROR, "Failed to load schema")
    SCHEMA_RESOLUTION_FAILED = ("schema-resolution-failed", ErrorCategory.SERVER_ERROR, "Failed to resolve $ref")
    STORAGE_READ_FAILED = ("storage-read-failed", ErrorCategory.SERVER_ERROR, "Storage read error")
    STORAGE_WRITE_FAILED = ("storage-write-failed", ErrorCategory.SERVER_ERROR, "Storage write error")
    INTERNAL_ERROR = ("internal-error", ErrorCategory.SERVER_ERROR, "Internal server error")
    
    def __init__(self, code: str, category: ErrorCategory, description: str):
        self.code = code
        self.category = category
        self.description = description

@dataclass
class ValidationErrorDetail:
    """Individual validation error with full context (FR-060, FR-062)"""
    code: str
    message: str
    path: str
    constraint: str
    expected: Any = None
    actual: Any = None

@dataclass
class ValidationReport:
    """Complete validation report with ALL errors (FR-059, FR-060)"""
    valid: bool
    error_count: int
    errors: list[ValidationErrorDetail] = field(default_factory=list)

# Domain Exceptions (all 22 error codes)
class DomainException(Exception):
    """Base exception for all domain errors"""
    def __init__(self, message: str, error_code: ErrorCode, details: dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}

class DocumentNotFoundError(DomainException):
    def __init__(self, doc_id: str):
        super().__init__(
            f"Document not found: {doc_id}",
            ErrorCode.DOCUMENT_NOT_FOUND,
            {"doc_id": doc_id}
        )

class PathNotFoundError(DomainException):
    """Path doesn't exist (FR-092, FR-093)"""
    def __init__(self, path: str, deepest_ancestor: str = None):
        details = {"path": path}
        if deepest_ancestor:
            details["deepest_ancestor"] = deepest_ancestor
        
        message = f"Path not found: {path}"
        if deepest_ancestor:
            message += f". Deepest existing ancestor: {deepest_ancestor}"
        
        super().__init__(message, ErrorCode.PATH_NOT_FOUND, details)

class VersionConflictError(DomainException):
    def __init__(self, doc_id: str, expected_version: int, actual_version: int):
        super().__init__(
            f"Version conflict: expected {expected_version}, actual {actual_version}",
            ErrorCode.VERSION_CONFLICT,
            {"doc_id": doc_id, "expected_version": expected_version, "actual_version": actual_version}
        )

# ... (all other 19 exception classes)

class ErrorFormatter:
    """Converts domain exceptions to structured MCP error responses (FR-067, FR-096)"""
    
    REMEDIATIONS = {
        ErrorCode.DOCUMENT_NOT_FOUND: "Verify doc_id is correct; use document_list to see available documents",
        ErrorCode.PATH_NOT_FOUND: "Use document_read_node on parent path to verify structure; create missing paths explicitly",
        ErrorCode.VERSION_CONFLICT: "Re-read document to get current version and content; reapply changes; retry with new version",
        # ... (all 22 remediations)
    }
    
    @classmethod
    def format_exception(cls, exc: DomainException) -> dict:
        """Convert domain exception to MCP error response"""
        return {
            "error": {
                "code": exc.error_code.code,
                "category": exc.error_code.category.value,
                "message": str(exc),
                "details": exc.details,
                "remediation": cls.REMEDIATIONS.get(exc.error_code, "Contact support")
            }
        }
```

**Tasks:**
- [ ] Implement `ErrorCode` enum with all 22 codes
- [ ] Implement all 22 domain exception classes
- [ ] Implement `ErrorFormatter` with remediation messages
- [ ] Implement `ValidationReport` and `ValidationErrorDetail`
- [ ] Add all remediation guidance messages (FR-096)

**Test Cases:**
- All 22 error codes defined and documented
- ErrorFormatter converts exceptions to MCP format
- Remediation messages are actionable
- ValidationReport collects multiple errors
- Error stability (FR-097) - codes don't change meaning

**Deliverables:**
- ✅ Complete error code taxonomy (22 codes)
- ✅ Domain exception hierarchy
- ✅ Error formatter with remediation
- ✅ Ready for services to use in Phase 3-4

---

### 2.2 ULID Generation (FR-107 to FR-111)

**Goal**: ULID-based document ID generation.

**Implementation:**
```python
# src/json_schema_mcp/utils/ulid_generator.py
from ulid import ULID
from ..domain.document import DocumentId

class ULIDGenerator:
    """ULID generator for document IDs (FR-107 to FR-111)"""
    
    @staticmethod
    def generate() -> DocumentId:
        """
        Generate new ULID-based document ID.
        Format: 26-character case-insensitive, timestamp-ordered, 128-bit random.
        Example: 01JDEX3M8K2N9WPQR5STV6XY7Z
        """
        ulid_str = str(ULID())
        return DocumentId(value=ulid_str)
    
    @staticmethod
    def from_string(ulid_str: str) -> DocumentId:
        """Parse ULID string into DocumentId with validation"""
        # Validates ULID format
        ULID.from_str(ulid_str)  # Raises if invalid
        return DocumentId(value=ulid_str)
```

**Tasks:**
- [ ] Implement ULID generation using python-ulid library
- [ ] Add ULID validation
- [ ] Document ULID format and benefits

**Test Cases:**
- Generate unique IDs (no collisions in 10k iterations)
- ULID format validation (26 chars)
- Timestamp ordering (later ULIDs sort after earlier)
- Invalid ULID rejection

**Deliverables:**
- ✅ ULID generator with validation
- ✅ Integration with DocumentId value object

---

## Phase 3: Schema & Validation (Week 3)

### 3.1 Schema Loading & Resolution (FR-001 to FR-007, FR-086 to FR-090)

**Goal**: Load JSON Schema with $ref resolution.

**Implementation:**
```python
# src/json_schema_mcp/services/schema_service.py
from jsonschema import Draft202012Validator, RefResolver
from jsonschema.exceptions import SchemaError
import json
from pathlib import Path

class SchemaService:
    """JSON Schema loading and introspection (FR-086 to FR-090)"""
    
    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        self.schema_uri = schema_path.as_uri()
        self.schema = self._load_and_validate_schema()
        self.validator = Draft202012Validator(self.schema)
        self.resolved_schema = self._resolve_refs()
    
    def _load_and_validate_schema(self) -> dict:
        """Load schema file and validate it's valid JSON Schema (FR-003)"""
        if not self.schema_path.exists():
            raise SchemaLoadError(f"Schema file not found: {self.schema_path}")
        
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            raise SchemaLoadError(f"Invalid JSON in schema file: {e}")
        
        # Validate schema itself
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as e:
            raise SchemaLoadError(f"Invalid JSON Schema: {e}")
        
        return schema
    
    def _resolve_refs(self) -> dict:
        """
        Recursively resolve all $ref references (FR-086, FR-087).
        Merge default values from referenced schemas.
        Detect circular references (FR-090).
        """
        # Use jsonschema RefResolver to dereference all $refs
        resolver = RefResolver.from_schema(self.schema)
        resolved = self._deep_resolve(self.schema, resolver, visited=set())
        return resolved
    
    def _deep_resolve(self, schema_part: dict, resolver: RefResolver, visited: set) -> dict:
        """Recursively resolve $ref with cycle detection"""
        # Implementation with cycle detection
        pass
    
    def get_schema_for_path(self, json_pointer: str) -> dict:
        """Get schema definition for specific path (FR-036 to FR-040)"""
        # Navigate schema following JSON Pointer path
        # Return dereferenced schema for that location
        pass
    
    def get_defaults(self) -> dict:
        """Extract all default values from resolved schema (FR-088, FR-089)"""
        return self._collect_defaults(self.resolved_schema)
    
    def _collect_defaults(self, schema: dict, current_path: list = None) -> dict:
        """Recursively collect default values from schema tree"""
        defaults = {}
        if "default" in schema:
            defaults = schema["default"]
        
        if "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                prop_defaults = self._collect_defaults(prop_schema, current_path + [prop] if current_path else [prop])
                if prop_defaults:
                    defaults[prop] = prop_defaults
        
        return defaults
```

**Tasks:**
- [ ] Implement schema loading with validation
- [ ] Implement $ref resolution with cycle detection
- [ ] Extract default values from resolved schema
- [ ] Implement schema introspection for paths
- [ ] Handle circular reference errors

**Test Cases:**
- Load valid schema successfully
- Detect invalid JSON Schema
- Resolve $ref references
- Detect circular $refs
- Extract defaults from nested schema
- Get schema for specific JSON Pointer path

**Deliverables:**
- ✅ Schema service with full $ref support
- ✅ Default value extraction
- ✅ Path-based schema introspection

---

### 3.2 Validation Service (FR-058 to FR-064)

**Goal**: Comprehensive JSON Schema validation with detailed error reporting.

**Implementation:**
```python
# src/json_schema_mcp/services/validation_service.py
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from typing import Any
from ..domain.errors import ValidationReport, ValidationErrorDetail

class ValidationService:
    """JSON Schema validation service (FR-058 to FR-064)"""
    
    def __init__(self, validator: Draft202012Validator):
        self.validator = validator
    
    def validate(self, document: dict[str, Any]) -> ValidationReport:
        """
        Perform COMPLETE validation, return ALL errors (FR-059).
        Returns structured validation report with all errors (FR-060).
        """
        errors = []
        
        # Iterate ALL validation errors (not fail-fast)
        for error in self.validator.iter_errors(document):
            error_detail = self._create_error_detail(error)
            errors.append(error_detail)
        
        return ValidationReport(
            valid=len(errors) == 0,
            error_count=len(errors),
            errors=errors
        )
    
    def _create_error_detail(self, error: ValidationError) -> ValidationErrorDetail:
        """Convert jsonschema ValidationError to structured format (FR-060, FR-062)"""
        # Map error to our error code taxonomy
        error_code = self._map_error_code(error)
        
        # Build JSON Pointer path
        path = "/" + "/".join(str(p) for p in error.absolute_path)
        
        # Create actionable message
        message = self._create_actionable_message(error)
        
        return ValidationErrorDetail(
            code=error_code,
            message=message,
            path=path,
            constraint=error.validator,
            expected=error.validator_value,
            actual=error.instance
        )
    
    def _map_error_code(self, error: ValidationError) -> str:
        """Map jsonschema error to our error code taxonomy"""
        validator_name = error.validator
        
        mapping = {
            "type": "type-mismatch",
            "required": "required-missing",
            "minLength": "min-length",
            "maxLength": "max-length",
            "pattern": "pattern-failed",
            "enum": "enum-mismatch",
            "minItems": "min-items",
            "maxItems": "max-items",
            "minimum": "minimum",
            "maximum": "maximum",
            "format": "format-invalid",
            "additionalProperties": "additional-properties-forbidden"
        }
        
        return mapping.get(validator_name, "validation-failed")
    
    def _create_actionable_message(self, error: ValidationError) -> str:
        """Create human-readable actionable error message (FR-062)"""
        # Build detailed message with remediation guidance
        pass
```

**Tasks:**
- [ ] Implement comprehensive validation (iter_errors, not fail-fast)
- [ ] Map jsonschema errors to our error code taxonomy
- [ ] Create actionable error messages with remediation
- [ ] Build structured ValidationReport
- [ ] Add logging for all validation failures (FR-063)

**Test Cases:**
- Validation passes for valid document
- Collect all errors (not just first)
- Error codes match specification
- Error messages are actionable
- JSON Pointer paths are accurate

**Deliverables:**
- ✅ ValidationService with comprehensive error reporting
- ✅ Structured validation reports
- ✅ Actionable error messages

---

## Phase 4: Document Operations (Week 4)

### 4.1 Document Service - Core CRUD (FR-008 to FR-014, FR-041 to FR-057)

**Goal**: Implement copy-on-write document operations.

**Implementation:**
```python
# src/json_schema_mcp/services/document_service.py
import copy
from datetime import datetime
from ..domain.document import Document, DocumentId
from ..domain.metadata import DocumentMetadata
from ..utils.ulid_generator import ULIDGenerator
from .validation_service import ValidationService
from .schema_service import SchemaService
from ..storage.storage_interface import StorageAdapter

class DocumentService:
    """Document CRUD operations with copy-on-write semantics"""
    
    def __init__(
        self,
        storage: StorageAdapter,
        schema_service: SchemaService,
        validation_service: ValidationService,
        lock_service: "LockService"
    ):
        self.storage = storage
        self.schema_service = schema_service
        self.validation_service = validation_service
        self.lock_service = lock_service
    
    async def create_document(self) -> tuple[DocumentId, int]:
        """
        Create new document with schema defaults (FR-008, FR-009).
        Returns (doc_id, version=1) (FR-075a).
        """
        # Generate ULID doc_id
        doc_id = ULIDGenerator.generate()
        
        # Get defaults from schema
        defaults = self.schema_service.get_defaults()
        
        # Check for required fields without defaults (FR-009a)
        self._check_required_fields_have_defaults()
        
        # Create document with version=1
        document = Document(
            doc_id=doc_id,
            content=defaults,
            version=1
        )
        
        # Validate initialized document (FR-009c)
        validation_report = self.validation_service.validate(document.content)
        if not validation_report.valid:
            raise DocumentCreationError("Cannot create document: validation failed", validation_report)
        
        # Create metadata
        now = datetime.utcnow()
        metadata = DocumentMetadata(
            doc_id=str(doc_id),
            version=1,
            schema_uri=self.schema_service.schema_uri,
            created_at=now,
            modified_at=now,
            content_size_bytes=len(document.to_json())
        )
        
        # Save atomically
        await self.storage.save(document, metadata)
        
        return doc_id, 1
    
    async def read_node(self, doc_id: DocumentId, path: str) -> tuple[Any, int]:
        """
        Read content at path (FR-026 to FR-031).
        Returns (content, version) for optimistic locking (FR-077).
        """
        # Load document
        document, metadata = await self.storage.load(doc_id)
        
        # Resolve path
        json_pointer = JSONPointer(path)
        content = json_pointer.resolve(document.content)
        
        return content, metadata.version
    
    async def update_node(
        self,
        doc_id: DocumentId,
        path: str,
        value: Any,
        expected_version: int
    ) -> tuple[Any, int]:
        """
        Update node using copy-on-write (FR-041 to FR-047).
        Requires version for optimistic locking (FR-078, FR-079).
        Returns (updated_content, new_version).
        """
        # Acquire document lock (FR-082b)
        async with self.lock_service.acquire_lock(doc_id, timeout=10.0):
            # Load current document
            document, metadata = await self.storage.load(doc_id)
            
            # Check version (FR-079, FR-080)
            if metadata.version != expected_version:
                raise VersionConflictError(
                    doc_id=str(doc_id),
                    expected_version=expected_version,
                    actual_version=metadata.version
                )
            
            # CLONE: Deep copy document (FR-041a)
            cloned_content = copy.deepcopy(document.content)
            
            # MODIFY: Apply change to clone (FR-041b)
            json_pointer = JSONPointer(path)
            modified_content = json_pointer.set_value(cloned_content, value)
            
            # VALIDATE: Validate entire cloned document (FR-041c)
            validation_report = self.validation_service.validate(modified_content)
            if not validation_report.valid:
                # Discard clone, return errors (FR-041f)
                raise ValidationFailedError("Update validation failed", validation_report)
            
            # PERSIST: Save if valid (FR-041d)
            new_version = metadata.version + 1  # FR-076
            updated_doc = Document(
                doc_id=doc_id,
                content=modified_content,
                version=new_version
            )
            
            updated_metadata = DocumentMetadata(
                doc_id=str(doc_id),
                version=new_version,
                schema_uri=metadata.schema_uri,
                created_at=metadata.created_at,
                modified_at=datetime.utcnow(),
                content_size_bytes=len(updated_doc.to_json())
            )
            
            await self.storage.save(updated_doc, updated_metadata)
            
            # Update in-memory state after successful persistence (FR-041e)
            return json_pointer.resolve(modified_content), new_version
    
    # Similar implementations for create_node, delete_node...
```

**Tasks:**
- [ ] Implement `create_document` with defaults and validation
- [ ] Implement `read_node` with path resolution
- [ ] Implement `update_node` with copy-on-write
- [ ] Implement `create_node` for array append and new properties
- [ ] Implement `delete_node` with validation
- [ ] Add version conflict detection
- [ ] Integrate with lock service

**Test Cases:**
- Create document with defaults
- Fail creation if required fields lack defaults
- Read node at various paths
- Update node successfully
- Version conflict on concurrent update
- Validation failure discards clone
- Delete required field fails

**Deliverables:**
- ✅ Complete DocumentService with CRUD operations
- ✅ Copy-on-write semantics working
- ✅ Version conflict detection

---

### 4.2 Lock Service (FR-082 to FR-082e)

**Goal**: Document-level locking with timeout.

**Implementation:**
```python
# src/json_schema_mcp/services/lock_service.py
import asyncio
from contextlib import asynccontextmanager
from typing import Dict
from ..domain.document import DocumentId

class LockService:
    """Document-level locking with timeout (FR-082 to FR-082e)"""
    
    def __init__(self):
        # In-memory lock map keyed by doc_id (FR-082a)
        self._locks: Dict[str, asyncio.Lock] = {}
        self._lock_creation_lock = asyncio.Lock()
    
    async def _get_or_create_lock(self, doc_id: DocumentId) -> asyncio.Lock:
        """Get existing lock or create new one for doc_id"""
        doc_id_str = str(doc_id)
        
        async with self._lock_creation_lock:
            if doc_id_str not in self._locks:
                self._locks[doc_id_str] = asyncio.Lock()
            return self._locks[doc_id_str]
    
    @asynccontextmanager
    async def acquire_lock(self, doc_id: DocumentId, timeout: float = 10.0):
        """
        Acquire exclusive lock on document (FR-082b).
        Raises LockTimeoutError if cannot acquire within timeout (FR-082d).
        Automatically releases lock on exit (FR-082c).
        """
        lock = await self._get_or_create_lock(doc_id)
        
        try:
            # Attempt to acquire with timeout
            await asyncio.wait_for(lock.acquire(), timeout=timeout)
            yield
        except asyncio.TimeoutError:
            raise LockTimeoutError(f"Failed to acquire lock for {doc_id} within {timeout}s")
        finally:
            # Always release lock (FR-082c)
            if lock.locked():
                lock.release()
    
    def cleanup_all_locks(self):
        """Release all locks on server restart (FR-082e)"""
        self._locks.clear()
```

**Tasks:**
- [ ] Implement lock acquisition with timeout
- [ ] Use context manager for automatic release
- [ ] Add lock cleanup on server restart
- [ ] Handle lock timeout errors

**Test Cases:**
- Acquire and release lock successfully
- Timeout after 10 seconds
- Concurrent operations serialize
- Lock cleanup on restart

**Deliverables:**
- ✅ LockService with timeout handling
- ✅ Context manager for safe lock release
- ✅ Cleanup mechanism

---

## Phase 5: MCP Integration (Week 5)

### 5.1 MCP Tool Implementations (FR-065 to FR-069)

**Goal**: Implement all 8 MCP tools with JSON Schema definitions.

**Implementation:**
```python
# src/json_schema_mcp/mcp_tools/document_tools.py
from mcp.server import Server
from mcp.types import Tool, TextContent
from ..services.document_service import DocumentService

def register_document_tools(server: Server, document_service: DocumentService):
    """Register document CRUD tools with MCP server"""
    
    @server.call_tool()
    async def document_create(arguments: dict) -> list[TextContent]:
        """
        Creates a new empty document conforming to the server's configured schema.
        Returns unique doc_id and initial version.
        """
        try:
            doc_id, version = await document_service.create_document()
            
            result = {
                "success": True,
                "doc_id": str(doc_id),
                "version": version,
                "initial_tree": {},  # TODO: Add actual defaults
                "validation_report": {
                    "valid": True,
                    "error_count": 0,
                    "errors": []
                }
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": {
                        "code": type(e).__name__,
                        "message": str(e)
                    }
                }, indent=2)
            )]
    
    @server.call_tool()
    async def document_read_node(arguments: dict) -> list[TextContent]:
        """Retrieves content at a specified node (path) within the document tree."""
        doc_id = arguments["doc_id"]
        path = arguments["node_path"]
        
        try:
            content, version = await document_service.read_node(
                DocumentId(doc_id), path
            )
            
            result = {
                "success": True,
                "node_content": content,
                "version": version,
                "node_type": type(content).__name__
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            # Error handling...
            pass
    
    # Similar implementations for other tools...
    
    # Register tool metadata
    server.list_tools.append(Tool(
        name="document_create",
        description="Creates a new empty document conforming to the server's configured schema",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ))
    
    server.list_tools.append(Tool(
        name="document_read_node",
        description="Retrieves content at a specified node (path) within the document tree",
        inputSchema={
            "type": "object",
            "required": ["doc_id", "node_path"],
            "properties": {
                "doc_id": {"type": "string"},
                "node_path": {"type": "string", "pattern": "^/"}
            }
        }
    ))
```

**Tasks:**
- [ ] Implement all 8 MCP tools with proper signatures
- [ ] Define JSON Schema for tool inputs (FR-065, FR-068)
- [ ] Define JSON Schema for tool outputs (FR-069)
- [ ] Map domain exceptions to MCP error responses (FR-067)
- [ ] Add comprehensive error handling
- [ ] Include validation reports in responses

**Test Cases:**
- Each tool with valid inputs
- Each tool with invalid inputs
- Error responses match specification
- JSON Schema validation for inputs/outputs

**Deliverables:**
- ✅ 8 MCP tools fully implemented
- ✅ Complete JSON Schema definitions
- ✅ Structured error responses

---

### 5.2 Server Initialization & MCP Resources

**Goal**: MCP server startup with configuration, service wiring, and resource URI support for document export.

**Context**: User Story 8 requires document export via MCP resource URIs (e.g., `schema://doc_id`). This enables client applications to retrieve complete documents independently of agent-driven path operations (FR-032, FR-068).

**Implementation:**
```python
# src/json_schema_mcp/server.py
from mcp.server import Server
from mcp.types import Resource, ResourceContents
from .config import ServerConfig
from .services.schema_service import SchemaService
from .services.validation_service import ValidationService
from .services.document_service import DocumentService
from .services.lock_service import LockService
from .storage.file_storage import FileSystemStorage
from .mcp_tools import register_document_tools, register_schema_tools
import logging
import json

async def create_server() -> Server:
    """Initialize MCP server with all dependencies"""
    
    # ===== PHASE 1: Configuration Loading (FR-001a to FR-001f) =====
    config = ServerConfig()
    
    # ===== PHASE 2: Logging Setup (FR-001e) =====
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting JSON Schema CRUD MCP Server")
    
    # ===== PHASE 3: Storage Initialization =====
    logger.info(f"Initializing storage at {config.storage_dir}")
    storage = FileSystemStorage(config.storage_dir)
    
    # Startup cleanup (FR-018d)
    storage.cleanup_temp_files()
    logger.info("Cleaned up orphaned temporary files")
    
    # Verify storage integrity (edge case handling)
    corrupted = storage.verify_storage_integrity()
    if corrupted:
        logger.warning(f"Found {len(corrupted)} corrupted documents: {corrupted}")
    
    # ===== PHASE 4: Schema Loading & Validation (FR-001 to FR-007, FR-086-090) =====
    logger.info(f"Loading schema from {config.schema_path}")
    try:
        schema_service = SchemaService(config.schema_path)
        logger.info(f"Schema loaded successfully: {schema_service.schema_uri}")
        logger.info(f"Schema has {len(schema_service.get_defaults())} default values")
    except Exception as e:
        logger.error(f"Failed to load schema: {e}")
        raise SchemaLoadError(f"Schema load failed: {e}") from e
    
    # ===== PHASE 5: Service Initialization =====
    validation_service = ValidationService(schema_service.validator)
    lock_service = LockService()
    lock_service.cleanup_all_locks()  # FR-082e: Clean locks on startup
    
    document_service = DocumentService(
        storage=storage,
        schema_service=schema_service,
        validation_service=validation_service,
        lock_service=lock_service
    )
    
    logger.info("All services initialized successfully")
    
    # ===== PHASE 6: MCP Server Creation =====
    server = Server("json-schema-crud-mcp-server")
    
    # ===== PHASE 7: Register MCP Tools =====
    register_document_tools(server, document_service)
    register_schema_tools(server, schema_service)
    logger.info("MCP tools registered successfully")
    
    # ===== PHASE 8: Register MCP Resource Provider (FR-032, FR-068) =====
    # This enables schema://doc_id URIs for complete document export (User Story 8)
    
    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List all available document resources"""
        try:
            documents = await storage.list_all()
            return [
                Resource(
                    uri=f"schema://{doc.doc_id}",
                    name=f"Document {doc.doc_id}",
                    description=f"Complete document (created: {doc.created_at})",
                    mimeType="application/json"
                )
                for doc in documents
            ]
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []
    
    @server.read_resource()
    async def read_resource(uri: str) -> ResourceContents:
        """
        Read complete document via resource URI (FR-032, FR-033, FR-034).
        URI format: schema://doc_id
        Returns complete validated document for client applications.
        """
        # Parse URI
        if not uri.startswith("schema://"):
            raise ValueError(f"Invalid resource URI: {uri}. Expected schema://doc_id")
        
        doc_id_str = uri[len("schema://"):]
        
        try:
            # Load complete document
            doc_id = DocumentId(doc_id_str)
            document, metadata = await storage.load(doc_id)
            
            # Validate entire document before export (FR-034)
            validation_report = validation_service.validate(document.content)
            if not validation_report.valid:
                logger.error(f"Document {doc_id_str} failed validation on export")
                raise ValidationFailedError(
                    f"Document validation failed with {validation_report.error_count} errors",
                    validation_report
                )
            
            # Return complete document with metadata
            response = {
                "doc_id": doc_id_str,
                "content": document.content,
                "metadata": {
                    "version": metadata.version,
                    "schema_uri": metadata.schema_uri,
                    "created_at": metadata.created_at.isoformat(),
                    "modified_at": metadata.modified_at.isoformat(),
                    "content_size_bytes": metadata.content_size_bytes
                }
            }
            
            return ResourceContents(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(response, indent=2, ensure_ascii=False)
            )
        
        except DocumentNotFoundError:
            raise ValueError(f"Document not found: {doc_id_str}")
        except Exception as e:
            logger.error(f"Failed to read resource {uri}: {e}")
            raise
    
    logger.info("MCP resource provider registered for schema:// URIs")
    
    # ===== PHASE 9: Startup Validation Summary =====
    logger.info("=" * 60)
    logger.info("Server initialization complete!")
    logger.info(f"Schema: {schema_service.schema_uri}")
    logger.info(f"Storage: {config.storage_dir}")
    logger.info(f"Log level: {config.log_level}")
    logger.info(f"MCP tools: 8 registered")
    logger.info(f"Resource URIs: schema://doc_id enabled for document export")
    logger.info("=" * 60)
    
    return server

# src/json_schema_mcp/__main__.py
import asyncio
from .server import create_server

async def main():
    """Entry point for python -m json_schema_mcp"""
    try:
        server = await create_server()
        # Run MCP server (stdio transport)
        await server.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

**Tasks:**
- [ ] Implement server initialization with 9-phase startup sequence
- [ ] Configure logging from config (FR-001e)
- [ ] Add comprehensive startup validation with checkpoints
- [ ] Implement MCP resource provider for `schema://doc_id` URIs (FR-032, FR-068)
- [ ] Add resource listing for all documents
- [ ] Validate documents on export (FR-034)
- [ ] Implement MCP stdio transport
- [ ] Add graceful shutdown handling
- [ ] Add startup logging with summary

**Test Cases:**
- Server starts successfully with valid config
- Server fails fast on invalid schema (FR-003)
- Server fails on non-writable storage directory (FR-105)
- Logging configured correctly at specified level
- Resource URI `schema://doc_id` returns complete document (User Story 8)
- Resource export validates document before returning (FR-034)
- Resource listing returns all documents
- Corrupted documents logged but don't block startup

**Deliverables:**
- ✅ Runnable MCP server: `python -m json_schema_mcp`
- ✅ Complete dependency wiring with explicit phases
- ✅ Comprehensive startup validation (9 phases)
- ✅ MCP resource URIs for document export (User Story 8)
- ✅ Detailed startup logging

---

### 5.3 REST API Implementation

**Goal**: Implement FastAPI REST endpoints with identical functionality to MCP tools, enabling independent API usage.

**Context**: The server must provide BOTH MCP (for agent integration) and REST API (for traditional HTTP clients) interfaces. Both interfaces share the same business logic layer and provide identical functionality (FR-065, FR-070).

**Implementation:**

```python
# src/json_schema_mcp/api_server.py
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import ServerConfig
from .services.document_service import DocumentService
from .services.schema_service import SchemaService
from .rest_api.routes import documents, schema, health
from .rest_api.middleware import error_handler_middleware
import logging
import uvicorn

def create_app(
    document_service: DocumentService,
    schema_service: SchemaService,
    config: ServerConfig
) -> FastAPI:
    """Create FastAPI application with all routes and middleware"""
    
    app = FastAPI(
        title="JSON Schema CRUD API",
        version="1.0.0",
        description="REST API for schema-validated document storage (dual interface with MCP)",
        docs_url="/docs",           # Swagger UI
        redoc_url="/redoc",         # ReDoc alternative
        openapi_url="/openapi.json" # OpenAPI 3.1 specification
    )
    
    # CORS middleware (FR-070i)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Error handling middleware
    app.middleware("http")(error_handler_middleware)
    
    # Dependency injection: make services available to routes
    app.state.document_service = document_service
    app.state.schema_service = schema_service
    
    # Register route modules
    app.include_router(health.router)
    app.include_router(documents.router)
    app.include_router(schema.router)
    
    return app

async def run_rest_server(port: int = 8080):
    """Run REST API server"""
    # Initialize all services (same as MCP server)
    config = ServerConfig()
    storage = FileSystemStorage(config.storage_dir)
    schema_service = SchemaService(config.schema_path)
    validation_service = ValidationService(schema_service.validator)
    lock_service = LockService()
    document_service = DocumentService(storage, schema_service, validation_service, lock_service)
    
    # Create FastAPI app
    app = create_app(document_service, schema_service, config)
    
    # Run with Uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


# src/json_schema_mcp/rest_api/models.py
from pydantic import BaseModel, Field
from typing import Any, Optional, List

class DocumentCreateRequest(BaseModel):
    """Request body for POST /documents (FR-070a)"""
    document_id: str = Field(..., description="ULID identifier for new document")
    content: dict[str, Any] = Field(..., description="Initial JSON content")

class DocumentCreateResponse(BaseModel):
    """Response for successful document creation"""
    document_id: str
    version: int
    message: str = "Document created successfully"

class NodeReadResponse(BaseModel):
    """Response for GET /documents/{doc_id} (FR-070b)"""
    document_id: str
    path: str
    content: Any
    version: int

class NodeUpdateRequest(BaseModel):
    """Request body for PUT/POST/DELETE on nodes (FR-070c, FR-070d, FR-070e)"""
    value: Optional[Any] = Field(None, description="New value for the node")

class NodeUpdateResponse(BaseModel):
    """Response for successful node operations"""
    document_id: str
    path: str
    version: int
    message: str

class DocumentListResponse(BaseModel):
    """Response for GET /documents (FR-070f)"""
    documents: List[str] = Field(..., description="List of document IDs")
    count: int

class SchemaResponse(BaseModel):
    """Response for GET /schema (FR-070g)"""
    schema_uri: str
    schema: dict[str, Any]

class SchemaNodeResponse(BaseModel):
    """Response for GET /schema/node (FR-070h)"""
    path: str
    node_schema: dict[str, Any]

class ErrorResponse(BaseModel):
    """Standard error response format (FR-069b)"""
    error_code: str
    message: str
    details: Optional[dict[str, Any]] = None


# src/json_schema_mcp/rest_api/routes/documents.py
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from typing import Optional
from ..models import *
from ...domain.errors import *
import logging

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

def get_document_service(request: Request):
    """Dependency: Get DocumentService from app state"""
    return request.app.state.document_service

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DocumentCreateResponse)
async def create_document(
    req: DocumentCreateRequest,
    service = Depends(get_document_service)
) -> DocumentCreateResponse:
    """
    Create a new schema-validated document (FR-070a).
    Maps to document_create MCP tool.
    """
    try:
        result = await service.create_document(req.document_id, req.content)
        return DocumentCreateResponse(
            document_id=req.document_id,
            version=result["version"],
            message="Document created successfully"
        )
    except ValidationFailedError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": e.error_code, "message": str(e), "details": e.details}
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": e.error_code, "message": str(e)}
        )

@router.get("/{doc_id}", response_model=NodeReadResponse)
async def read_node(
    doc_id: str,
    path: str = Query("/", description="JSON Pointer path"),
    service = Depends(get_document_service)
) -> NodeReadResponse:
    """
    Read a document or node at a specific JSON Pointer path (FR-070b).
    Maps to document_read_node MCP tool.
    """
    try:
        content, version = await service.read_node(doc_id, path)
        return NodeReadResponse(
            document_id=doc_id,
            path=path,
            content=content,
            version=version
        )
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": e.error_code, "message": str(e)}
        )
    except PathNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": e.error_code, "message": str(e)}
        )

@router.put("/{doc_id}", response_model=NodeUpdateResponse)
async def update_node(
    doc_id: str,
    path: str = Query(..., description="JSON Pointer path"),
    req: NodeUpdateRequest = None,
    service = Depends(get_document_service)
) -> NodeUpdateResponse:
    """
    Update a node at a specific JSON Pointer path (FR-070c).
    Maps to document_update_node MCP tool.
    """
    try:
        version = await service.update_node(doc_id, path, req.value)
        return NodeUpdateResponse(
            document_id=doc_id,
            path=path,
            version=version,
            message="Node updated successfully"
        )
    except (DocumentNotFoundError, PathNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": e.error_code, "message": str(e)}
        )
    except ValidationFailedError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_code": e.error_code, "message": str(e), "details": e.details}
        )
    except ConcurrencyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": e.error_code, "message": str(e)}
        )

@router.post("/{doc_id}/nodes", status_code=status.HTTP_201_CREATED, response_model=NodeUpdateResponse)
async def insert_node(
    doc_id: str,
    path: str = Query(..., description="JSON Pointer path"),
    req: NodeUpdateRequest = None,
    service = Depends(get_document_service)
) -> NodeUpdateResponse:
    """
    Insert a new node at a specific JSON Pointer path (FR-070d).
    Maps to document_insert_node MCP tool.
    """
    try:
        version = await service.insert_node(doc_id, path, req.value)
        return NodeUpdateResponse(
            document_id=doc_id,
            path=path,
            version=version,
            message="Node inserted successfully"
        )
    except Exception as e:
        # Similar error handling as update_node
        raise

@router.delete("/{doc_id}/nodes", response_model=NodeUpdateResponse)
async def delete_node(
    doc_id: str,
    path: str = Query(..., description="JSON Pointer path"),
    service = Depends(get_document_service)
) -> NodeUpdateResponse:
    """
    Delete a node at a specific JSON Pointer path (FR-070e).
    Maps to document_delete_node MCP tool.
    """
    try:
        version = await service.delete_node(doc_id, path)
        return NodeUpdateResponse(
            document_id=doc_id,
            path=path,
            version=version,
            message="Node deleted successfully"
        )
    except Exception as e:
        # Similar error handling
        raise

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    service = Depends(get_document_service)
) -> DocumentListResponse:
    """
    List all document IDs (FR-070f).
    Maps to document_list MCP tool.
    """
    try:
        doc_ids = await service.list_documents()
        return DocumentListResponse(documents=doc_ids, count=len(doc_ids))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "STORAGE_LIST_FAILED", "message": str(e)}
        )


# src/json_schema_mcp/rest_api/routes/schema.py
from fastapi import APIRouter, Depends, Query, Request
from ..models import SchemaResponse, SchemaNodeResponse

router = APIRouter(prefix="/schema", tags=["schema"])

def get_schema_service(request: Request):
    return request.app.state.schema_service

@router.get("/", response_model=SchemaResponse)
async def get_root_schema(service = Depends(get_schema_service)) -> SchemaResponse:
    """
    Get the full JSON Schema (FR-070g).
    Maps to schema_get_root MCP tool.
    """
    schema = service.get_schema()
    return SchemaResponse(schema_uri=service.schema_uri, schema=schema)

@router.get("/node", response_model=SchemaNodeResponse)
async def get_node_schema(
    path: str = Query(..., description="JSON Pointer path"),
    service = Depends(get_schema_service)
) -> SchemaNodeResponse:
    """
    Get schema for a specific node (FR-070h).
    Maps to schema_get_node MCP tool.
    """
    node_schema = service.get_node_schema(path)
    return SchemaNodeResponse(path=path, node_schema=node_schema)


# src/json_schema_mcp/rest_api/routes/health.py
from fastapi import APIRouter
from typing import Dict

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "interface": "REST"
    }


# src/json_schema_mcp/rest_api/middleware.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from ..domain.errors import *
import logging

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    """
    Map domain exceptions to HTTP status codes (FR-069b).
    
    Error code mappings:
    - 404: DOC_NOT_FOUND, PATH_NOT_FOUND
    - 408: LOCK_TIMEOUT
    - 409: VERSION_CONFLICT, LOCK_HELD, LOCK_RELEASED
    - 422: VALIDATION_FAILED, SCHEMA_INVALID, PATH_INVALID
    - 500: STORAGE_*, CONFIG_*, SCHEMA_LOAD_FAILED
    """
    try:
        return await call_next(request)
    except DocumentNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error_code": e.error_code, "message": str(e)}
        )
    except PathNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error_code": e.error_code, "message": str(e)}
        )
    except LockTimeoutError as e:
        return JSONResponse(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            content={"error_code": e.error_code, "message": str(e)}
        )
    except (VersionConflictError, LockAlreadyHeldError) as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error_code": e.error_code, "message": str(e)}
        )
    except (ValidationFailedError, SchemaInvalidError, PathInvalidError) as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error_code": e.error_code,
                "message": str(e),
                "details": getattr(e, "details", None)
            }
        )
    except (StorageError, ConfigurationError, SchemaLoadError) as e:
        logger.error(f"Internal error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": e.error_code, "message": str(e)}
        )
    except Exception as e:
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )


# src/json_schema_mcp/__main__.py (UPDATED for dual entry points)
import asyncio
import argparse
import sys
from .server import create_server
from .api_server import run_rest_server

async def main():
    """Entry point supporting both MCP and REST interfaces"""
    parser = argparse.ArgumentParser(description="JSON Schema CRUD Server")
    parser.add_argument(
        "--mode",
        choices=["mcp", "rest"],
        default="mcp",
        help="Server mode: 'mcp' for stdio transport (agents), 'rest' for HTTP API"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for REST API (default: 8080)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "mcp":
            # Run MCP server via stdio (for agent integration)
            server = await create_server()
            await server.run()
        elif args.mode == "rest":
            # Run REST API server (for HTTP clients)
            await run_rest_server(port=args.port)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

**Tasks:**
- [ ] Create `api_server.py` with FastAPI app initialization
- [ ] Implement all 8 REST endpoints (POST /documents, GET /documents/{doc_id}, PUT /documents/{doc_id}, POST /documents/{doc_id}/nodes, DELETE /documents/{doc_id}/nodes, GET /documents, GET /schema, GET /schema/node)
- [ ] Create Pydantic models for all request/response bodies (FR-070a-h)
- [ ] Implement error handling middleware mapping 22 error codes to HTTP status codes (FR-069b)
- [ ] Configure CORS middleware (FR-070i)
- [ ] Update `__main__.py` to support `--mode` argument (mcp vs rest)
- [ ] Configure OpenAPI/Swagger UI at /docs (FR-070b)
- [ ] Configure ReDoc at /redoc
- [ ] Add health check endpoint at /health
- [ ] Ensure both interfaces share same service layer (DRY)
- [ ] Test all endpoints with Swagger UI
- [ ] Verify identical functionality between MCP tools and REST endpoints

**Test Cases:**
- All 8 REST endpoints work correctly
- Pydantic validation rejects invalid requests
- Error codes map to correct HTTP status codes (200, 201, 400, 404, 408, 409, 422, 500)
- CORS headers present in responses
- Swagger UI accessible and functional
- OpenAPI spec validates against OpenAPI 3.1
- REST API independently usable without MCP client
- Both interfaces provide identical functionality
- Service layer shared correctly (no code duplication)

**Deliverables:**
- ✅ Runnable REST API server: `python -m json_schema_mcp --mode rest`
- ✅ All 8 REST endpoints implemented and tested
- ✅ Swagger UI at http://localhost:8080/docs
- ✅ OpenAPI 3.1 specification at /openapi.json
- ✅ CORS configured for browser clients
- ✅ Dual entry point: MCP (stdio) + REST (HTTP)
- ✅ Shared business logic layer (no duplication)

---

## Phase 6: Testing & Documentation (Week 6)

### 6.1 Test Suite (TDD Approach)

**Test Structure:**
```
tests/
├── unit/
│   ├── test_config.py
│   ├── test_document.py
│   ├── test_json_pointer.py
│   ├── test_ulid_generator.py
│   ├── test_schema_service.py
│   ├── test_validation_service.py
│   ├── test_document_service.py
│   ├── test_lock_service.py
│   └── test_file_storage.py
├── integration/
│   ├── test_atomic_operations.py
│   ├── test_concurrency.py
│   ├── test_mcp_tools.py          # MCP interface tests
│   ├── test_rest_api.py            # REST interface tests
│   └── test_end_to_end.py
└── fixtures/
    ├── schemas/
    │   ├── book.schema.json
    │   └── invalid.schema.json
    └── documents/
        └── book-example.json
```

**Test Coverage Goals:**
- Unit tests: >90% coverage
- Integration tests: All user stories from spec
- End-to-end: Complete workflows through BOTH interfaces (MCP + REST)
- Interface parity: Verify MCP tools and REST endpoints provide identical results

**REST API Test Examples:**
```python
# tests/integration/test_rest_api.py
from fastapi.testclient import TestClient
from src.json_schema_mcp.api_server import create_app
import pytest

@pytest.fixture
def client(document_service, schema_service, config):
    """Create test client"""
    app = create_app(document_service, schema_service, config)
    return TestClient(app)

def test_create_document_rest(client):
    """Test POST /documents"""
    response = client.post("/documents", json={
        "document_id": "01HQ7X...",
        "content": {"title": "Test Book"}
    })
    assert response.status_code == 201
    assert response.json()["version"] == 1

def test_read_node_rest(client):
    """Test GET /documents/{doc_id}?path=/title"""
    response = client.get("/documents/01HQ7X...?path=/title")
    assert response.status_code == 200
    assert response.json()["content"] == "Test Book"

def test_validation_error_rest(client):
    """Test that validation errors return 422"""
    response = client.post("/documents", json={
        "document_id": "01HQ7X...",
        "content": {"invalid": "field"}
    })
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_FAILED"

def test_swagger_ui_accessible(client):
    """Test that Swagger UI is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_spec(client):
    """Test that OpenAPI spec is valid"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert spec["openapi"].startswith("3.")
    assert len(spec["paths"]) >= 8  # All endpoints present

def test_cors_headers(client):
    """Test CORS headers present"""
    response = client.options("/documents")
    assert "access-control-allow-origin" in response.headers

def test_mcp_rest_parity(client, mcp_server):
    """Test that MCP and REST provide identical results"""
    doc_id = "01HQ7X..."
    content = {"title": "Parity Test"}
    
    # Create via REST
    rest_response = client.post("/documents", json={"document_id": doc_id, "content": content})
    rest_version = rest_response.json()["version"]
    
    # Read via MCP
    mcp_result = await mcp_server.call_tool("document_read_node", {"doc_id": doc_id, "node_path": "/"})
    mcp_content = mcp_result["node_content"]
    
    # Results should match
    assert mcp_content == content
```

**Tasks:**
- [ ] Write unit tests for all modules
- [ ] Write integration tests for atomic operations
- [ ] Write concurrency tests with multiple operations
- [ ] Write end-to-end MCP tool tests
- [ ] Write end-to-end REST API tests (NEW)
- [ ] Test interface parity (MCP vs REST) (NEW)
- [ ] Test Swagger UI accessibility (NEW)
- [ ] Test OpenAPI spec validity (NEW)
- [ ] Test CORS functionality (NEW)
- [ ] Test error code → HTTP status mapping (NEW)
- [ ] Create test fixtures (schemas, documents)
- [ ] Set up pytest with coverage reporting
- [ ] Use FastAPI TestClient for REST tests (NEW)

**Deliverables:**
- ✅ Comprehensive test suite
- ✅ >90% code coverage
- ✅ All acceptance scenarios tested
- ✅ Both MCP and REST interfaces tested
- ✅ Interface parity validated

---

### 6.2 Documentation (docs/ folder)

**Documentation Structure:**

```markdown
# docs/index.md
- Getting Started
- Quick Start Guide (both MCP and REST)
- Architecture Overview (dual interface)
- API Reference (MCP + REST)
- Operations Guide

# docs/architecture/overview.md
- System Architecture Diagram (showing both interfaces)
- Component Responsibilities
- Layer Interactions (shared service layer)
- Data Flow (MCP vs REST)
- Dual Interface Design Pattern

# docs/architecture/concurrency.md
- Optimistic Locking Explained
- Lock Acquisition Flow
- Version Conflict Handling

# docs/api/mcp-tools.md
- document_create
- document_read_node
- document_update_node
- document_create_node
- document_delete_node
- document_list
- schema_get_node
- schema_get_root

# docs/api/rest-endpoints.md (NEW)
- POST /documents - Create document
- GET /documents/{doc_id} - Read node
- PUT /documents/{doc_id} - Update node
- POST /documents/{doc_id}/nodes - Insert node
- DELETE /documents/{doc_id}/nodes - Delete node
- GET /documents - List documents
- GET /schema - Get root schema
- GET /schema/node - Get node schema
- Interactive examples with curl and Swagger UI

# docs/api/error-codes.md
- Complete Error Catalog (22 codes)
- Error Code → HTTP Status Mapping
- Remediation Guidance

# docs/operations/configuration.md
- Environment Variables
- Config File Format
- Configuration Precedence
- CORS Configuration (NEW)
- Port Configuration (NEW)

# docs/operations/deployment.md
- Running the MCP Server (stdio)
- Running the REST API Server (HTTP)
- Running Both Simultaneously (NEW)
- MCP Client Integration
- REST Client Examples (curl, Postman, Python requests) (NEW)
- Swagger UI Usage (NEW)
- Production Considerations

# docs/development/setup.md
- Development Environment
- Running Tests (both interfaces)
- Code Style Guide
- Testing with Swagger UI (NEW)
```

**Tasks:**
- [ ] Write architecture documentation with diagrams (including dual interface pattern)
- [ ] Document all MCP tools with examples
- [ ] Document all REST endpoints with curl examples (NEW)
- [ ] Create interactive Swagger UI guide (NEW)
- [ ] Create complete error code reference with HTTP status mapping
- [ ] Write configuration guide (including CORS, port settings)
- [ ] Create deployment guide for both interfaces (NEW)
- [ ] Write development setup guide
- [ ] Add usage examples for common scenarios (MCP + REST)
- [ ] Document interface parity guarantees (NEW)

**Deliverables:**
- ✅ Comprehensive documentation in docs/
- ✅ Architecture diagrams showing dual interface
- ✅ API reference with examples (MCP + REST)
- ✅ Operations guides for both interfaces
- ✅ Swagger UI usage guide

---

## Phase 7: Polish & Release Prep

### 7.1 Error Handling & Logging

**Tasks:**
- [ ] Implement complete error code taxonomy (FR-095 to FR-099)
- [ ] Add structured logging with context
- [ ] Create error response formatter
- [ ] Add request/response logging
- [ ] Implement health check endpoint

### 7.2 Configuration & Deployment

**Tasks:**
- [ ] Create example config files
- [ ] Write deployment documentation
- [ ] Add environment variable documentation
- [ ] Create Docker support (optional)
- [ ] Add systemd service file example

### 7.3 Final Testing

**Tasks:**
- [ ] Run full test suite
- [ ] Manual testing with MCP clients
- [ ] Performance testing (10MB documents)
- [ ] Concurrency testing (100 operations)
- [ ] Memory profiling

---

## Success Metrics

**Implementation Complete When:**
- ✅ All 8 MCP tools implemented and tested
- ✅ All 8 REST endpoints implemented and tested (NEW)
- ✅ Interface parity validated (MCP and REST provide identical functionality) (NEW)
- ✅ All user stories from spec have passing tests
- ✅ >90% code coverage
- ✅ All functional requirements (FR-001 to FR-117) implemented (UPDATED from FR-116)
- ✅ Complete documentation in docs/ (including REST API docs)
- ✅ MCP server runs successfully: `python -m json_schema_mcp --mode mcp` (UPDATED)
- ✅ REST API server runs successfully: `python -m json_schema_mcp --mode rest` (NEW)
- ✅ Swagger UI accessible at http://localhost:8080/docs (NEW)
- ✅ OpenAPI spec validates against OpenAPI 3.1 (NEW)
- ✅ Integration with MCP client (e.g., Claude Desktop) verified
- ✅ REST API independently usable without MCP client (NEW)
- ✅ CORS working for browser-based clients (NEW)

**Quality Gates:**
- All tests passing (both MCP and REST interfaces)
- MyPy type checking passes
- Black formatting applied
- Pylint score >8.0
- No critical security issues
- Swagger UI fully functional (NEW)
- HTTP status codes map correctly to error codes (NEW)

---

## Risk Mitigation

**Technical Risks:**
1. **JSON Schema $ref resolution complexity** → Mitigation: Use jsonschema library's built-in resolver, comprehensive testing
2. **File system atomicity edge cases** → Mitigation: Thorough testing on Windows/Linux, use os.replace for atomic rename
3. **Async I/O performance** → Mitigation: Profile early, optimize hot paths, consider aiofiles if needed

**Schedule Risks:**
1. **MCP SDK learning curve** → Mitigation: Study MCP examples, start with simple tool implementations
2. **Complex validation logic** → Mitigation: Leverage jsonschema library, focus on error mapping

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Set up development environment** (Python 3.11, dependencies)
3. **Create project structure** as defined above
4. **Begin Phase 1: Foundation** with configuration and domain models
5. **Follow TDD approach**: Write tests first, then implementation

---

## Appendix: Key Design Decisions

**Why Python over TypeScript (spec was TypeScript)?**
- User explicitly requested Python implementation
- Python has excellent JSON Schema support (jsonschema library)
- Python MCP SDK available
- Simpler async I/O with asyncio
- Strong typing via type hints + MyPy

**Why separate .meta.json files?**
- Clean separation of concerns
- Version not mixed with user content
- Easy to query metadata without parsing content
- Follows specification requirement (FR-016a)

**Why no in-memory cache for MVP?**
- User explicitly requested no caching
- Simpler implementation
- File I/O sufficient for MVP scale
- Can add caching in post-MVP phase

**Why file system storage over database?**
- Specification requirement for MVP
- Simpler deployment (no DB dependency)
- Easy backup/restore (copy files)
- Storage abstraction enables future migration

---

This plan provides a comprehensive roadmap for implementing the JSON Schema CRUD MCP Server in Python. Follow the phases sequentially, maintain test coverage, and refer to the specification for detailed requirements.
