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
- MCP Python SDK (`mcp` package)
- jsonschema library (Draft 2020-12 support)
- ULID library for document IDs
- Structured logging with Python logging module

**Architecture Pattern**: Layered architecture with clear separation of concerns:
1. **MCP Layer**: Tool definitions and protocol handling
2. **Service Layer**: Business logic (document operations, validation)
3. **Storage Layer**: File system abstraction
4. **Domain Layer**: Core entities and value objects

---

## Project Structure

```
json-schema-mcp-tool/
├── src/
│   └── json_schema_mcp/
│       ├── __init__.py
│       ├── __main__.py                 # Entry point (python -m json_schema_mcp)
│       ├── server.py                   # MCP server initialization
│       ├── config.py                   # Configuration management
│       │
│       ├── mcp_tools/                  # MCP tool implementations
│       │   ├── __init__.py
│       │   ├── document_tools.py       # document_create, document_read_node, etc.
│       │   ├── schema_tools.py         # schema_get_node, schema_get_root
│       │   └── tool_registry.py        # Tool registration and metadata
│       │
│       ├── services/                   # Business logic layer
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
│   │   ├── overview.md                 # System architecture
│   │   ├── layers.md                   # Layer responsibilities
│   │   ├── data-flow.md                # Request flow diagrams
│   │   └── concurrency.md              # Locking and versioning
│   ├── api/
│   │   ├── mcp-tools.md                # MCP tool reference
│   │   ├── error-codes.md              # Complete error catalog
│   │   └── examples.md                 # Usage examples
│   ├── operations/
│   │   ├── configuration.md            # Server configuration
│   │   ├── deployment.md               # Running the server
│   │   └── troubleshooting.md          # Common issues
│   └── development/
│       ├── setup.md                    # Development environment
│       ├── testing.md                  # Test strategy
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
pydantic = "^2.5.0"               # Data validation and settings
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
    """Document entity with content and metadata"""
    doc_id: DocumentId
    content: dict[str, Any]
    version: int
    
    def to_json(self) -> str:
        """Serialize document content to JSON"""
        return json.dumps(self.content, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, doc_id: DocumentId, json_str: str, version: int) -> "Document":
        """Deserialize document from JSON"""
        content = json.loads(json_str)
        return cls(doc_id=doc_id, content=content, version=version)
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
        """Resolve pointer against document, returns value at path"""
        current = document
        for token in self.tokens:
            if isinstance(current, dict):
                if token not in current:
                    raise PathNotFoundError(self.path, token)
                current = current[token]
            elif isinstance(current, list):
                try:
                    index = int(token)
                    if index < 0:  # FR-024: Handle negative indices post-MVP
                        raise ValueError("Negative indices not supported in MVP")
                    current = current[index]
                except (ValueError, IndexError) as e:
                    raise PathNotFoundError(self.path, token) from e
            else:
                raise PathNotFoundError(self.path, token)
        return current
    
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
- Path not found errors
- Array append notation "/-"

**Deliverables:**
- ✅ RFC 6901 compliant implementation
- ✅ Comprehensive error messages
- ✅ 100% test coverage for path operations

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
```

**Tasks:**
- [ ] Implement `StorageAdapter` abstract interface
- [ ] Implement `FileSystemStorage` with atomic writes
- [ ] Implement write-then-rename strategy with fsync()
- [ ] Add startup cleanup for orphaned .tmp files
- [ ] Handle file system errors gracefully
- [ ] Add metadata file handling

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

### 5.2 Server Initialization

**Goal**: MCP server startup with configuration and service wiring.

**Implementation:**
```python
# src/json_schema_mcp/server.py
from mcp.server import Server
from .config import ServerConfig
from .services.schema_service import SchemaService
from .services.validation_service import ValidationService
from .services.document_service import DocumentService
from .services.lock_service import LockService
from .storage.file_storage import FileSystemStorage
from .mcp_tools import register_document_tools, register_schema_tools
import logging

async def create_server() -> Server:
    """Initialize MCP server with all dependencies"""
    
    # Load configuration (FR-001a to FR-001f)
    config = ServerConfig()
    
    # Setup logging (FR-001e)
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    # Initialize storage
    storage = FileSystemStorage(config.storage_dir)
    storage.cleanup_temp_files()  # FR-018d
    
    # Load and validate schema (FR-001 to FR-007)
    schema_service = SchemaService(config.schema_path)
    logger.info(f"Loaded schema from {config.schema_path}")
    
    # Initialize validation service
    validation_service = ValidationService(schema_service.validator)
    
    # Initialize lock service
    lock_service = LockService()
    
    # Initialize document service
    document_service = DocumentService(
        storage=storage,
        schema_service=schema_service,
        validation_service=validation_service,
        lock_service=lock_service
    )
    
    # Create MCP server
    server = Server("json-schema-crud-mcp-server")
    
    # Register tools
    register_document_tools(server, document_service)
    register_schema_tools(server, schema_service)
    
    logger.info("MCP server initialized successfully")
    return server

# src/json_schema_mcp/__main__.py
import asyncio
from .server import create_server

async def main():
    """Entry point for python -m json_schema_mcp"""
    server = await create_server()
    # Run MCP server (stdio transport)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

**Tasks:**
- [ ] Implement server initialization with dependency injection
- [ ] Configure logging from config (FR-001e)
- [ ] Add startup validation (schema load, storage writability)
- [ ] Implement MCP stdio transport
- [ ] Add graceful shutdown handling

**Test Cases:**
- Server starts successfully with valid config
- Server fails on invalid schema
- Server fails on non-writable storage directory
- Logging configured correctly

**Deliverables:**
- ✅ Runnable MCP server: `python -m json_schema_mcp`
- ✅ Complete dependency wiring
- ✅ Startup validation

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
│   ├── test_mcp_tools.py
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
- End-to-end: Complete workflows

**Tasks:**
- [ ] Write unit tests for all modules
- [ ] Write integration tests for atomic operations
- [ ] Write concurrency tests with multiple operations
- [ ] Write end-to-end MCP tool tests
- [ ] Create test fixtures (schemas, documents)
- [ ] Set up pytest with coverage reporting

**Deliverables:**
- ✅ Comprehensive test suite
- ✅ >90% code coverage
- ✅ All acceptance scenarios tested

---

### 6.2 Documentation (docs/ folder)

**Documentation Structure:**

```markdown
# docs/index.md
- Getting Started
- Quick Start Guide
- Architecture Overview
- API Reference
- Operations Guide

# docs/architecture/overview.md
- System Architecture Diagram
- Component Responsibilities
- Layer Interactions
- Data Flow

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

# docs/api/error-codes.md
- Complete Error Catalog
- Error Code → HTTP Status Mapping
- Remediation Guidance

# docs/operations/configuration.md
- Environment Variables
- Config File Format
- Configuration Precedence

# docs/operations/deployment.md
- Running the Server
- MCP Client Integration
- Production Considerations

# docs/development/setup.md
- Development Environment
- Running Tests
- Code Style Guide
```

**Tasks:**
- [ ] Write architecture documentation with diagrams
- [ ] Document all MCP tools with examples
- [ ] Create complete error code reference
- [ ] Write configuration guide
- [ ] Create deployment guide
- [ ] Write development setup guide
- [ ] Add usage examples for common scenarios

**Deliverables:**
- ✅ Comprehensive documentation in docs/
- ✅ Architecture diagrams
- ✅ API reference with examples
- ✅ Operations guides

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
- ✅ All user stories from spec have passing tests
- ✅ >90% code coverage
- ✅ All functional requirements (FR-001 to FR-116) implemented
- ✅ Complete documentation in docs/
- ✅ Server runs successfully: `python -m json_schema_mcp`
- ✅ Integration with MCP client (e.g., Claude Desktop) verified

**Quality Gates:**
- All tests passing
- MyPy type checking passes
- Black formatting applied
- Pylint score >8.0
- No critical security issues

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
