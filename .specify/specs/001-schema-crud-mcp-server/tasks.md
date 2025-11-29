# Task Decomposition: JSON Schema CRUD MCP Server
## Implementation Checklist

**Feature Branch**: `001-schema-crud-mcp-server`  
**Created**: 2025-11-29  
**Status**: Ready for Implementation

---

## Task Overview

**Total Phases**: 8 (includes Phase 0: TDD Bootstrap)  
**Estimated Duration**: 6-7 weeks  
**Task Categories**: Setup, Infrastructure, Services, Interfaces, Testing, Documentation, Polish

**Development Approach**: Test-Driven Development (TDD)
- Write tests FIRST
- Run tests (expecting failures)
- Implement code to make tests pass
- Refactor while keeping tests green

---

## Phase 0: TDD Bootstrap - Document Service Tests First [Day 1, ~5.5 hours]

**Goal**: Set up CI/CD pipeline and write DocumentService unit tests BEFORE implementation

**Philosophy**: We write the tests first to:
1. Define the API contract before coding
2. Ensure our design is testable
3. Have failing tests that guide implementation
4. Verify our understanding of the spec requirements
5. **Automate validation** - GitHub Actions runs tests on every commit

### 0.0 CI/CD Setup - GitHub Actions for TDD [~30 minutes]

**Goal**: Establish automated testing pipeline FIRST, before any code

- [ ] **P0.0.1** Create `.github/workflows/` directory
  - Create directory structure: `.github/workflows/`
  - **Acceptance**: Directory exists

- [ ] **P0.0.2** Create `ci.yml` GitHub Actions workflow
  - Create `.github/workflows/ci.yml`
  - Configure trigger: `on: [push, pull_request]`
  - Set up Python 3.11 environment
  - **Acceptance**: Workflow file exists

- [ ] **P0.0.3** Add test execution steps to workflow
  - Step: Install dependencies (`pip install -e .[dev]` or `poetry install`)
  - Step: Run pytest with coverage (`pytest --cov=src --cov-report=term --cov-report=xml`)
  - Step: Upload coverage to Codecov (optional but recommended)
  - **Acceptance**: Workflow runs tests and generates coverage

- [ ] **P0.0.4** Create dummy test to validate CI pipeline
  - Create `tests/test_dummy.py` with one passing test: `def test_dummy(): assert True`
  - Commit and push to trigger GitHub Action
  - Verify workflow runs successfully (green check)
  - **Acceptance**: GitHub Action runs, shows 100% coverage for dummy test

- [ ] **P0.0.5** Add coverage badge to README (optional)
  - Add Codecov or coverage badge markdown to README.md
  - **Acceptance**: Badge shows in repository

**🎯 Critical**: This CI/CD pipeline will validate EVERY subsequent task. All future commits must keep tests green!

---

### 0.1 Minimal Project Setup [~1.5 hours]

- [ ] **P0.1.1** Create basic Python package structure
  - Create `src/json_schema_mcp/` directory
  - Create `src/json_schema_mcp/services/` directory
  - Create `src/json_schema_mcp/domain/` directory
  - Create `tests/unit/` directory
  - Create `tests/fixtures/schemas/` directory
  - Create minimal `__init__.py` files in each package
  - **Acceptance**: Directory structure exists

- [ ] **P0.1.2** Create `pyproject.toml` with minimal configuration
  - Set project name: `json-schema-mcp-tool`
  - Set version: `0.1.0`
  - Set Python version requirement: `>=3.11`
  - Add build system: `setuptools` or `poetry`
  - Add optional dependencies group: `[dev]` with test dependencies
  - **Acceptance**: pyproject.toml exists with metadata

- [ ] **P0.1.3** Add test dependencies to `pyproject.toml`
  - Add `pytest = "^8.0.0"`
  - Add `pytest-asyncio = "^0.23.0"`
  - Add `pytest-cov = "^4.1.0"` (for coverage)
  - **Acceptance**: Test dependencies listed

- [ ] **P0.1.4** Add core dependencies to `pyproject.toml`
  - Add `jsonschema = "^4.20.0"` (JSON Schema validation)
  - Add `python-ulid = "^2.2.0"` (ULID generation)
  - Add `pydantic = "^2.5.0"` (data validation)
  - **Acceptance**: Core dependencies listed

- [ ] **P0.1.5** Create `pytest.ini` configuration
  - Set test paths: `testpaths = tests`
  - Set asyncio mode: `asyncio_mode = auto`
  - Set Python paths: `pythonpath = src`
  - Add markers for unit/integration tests
  - Add coverage configuration: `addopts = --cov=src --cov-report=term-missing`
  - **Acceptance**: pytest.ini exists

- [ ] **P0.1.6** Install dependencies and verify pytest works
  - Run: `pip install -e .[dev]` or `poetry install`
  - Verify: `pytest --version` works
  - Remove `tests/test_dummy.py` (was only for CI validation)
  - Verify: `pytest tests/` runs (no tests yet, but should not error)
  - **Acceptance**: Can run pytest command, CI still green

- [ ] **P0.1.7** Copy test schema to fixtures
  - Copy `schemas/text.json` to `tests/fixtures/schemas/text.json`
  - **Acceptance**: Test schema file available at `tests/fixtures/schemas/text.json`

- [ ] **P0.1.8** Create sample test data file
  - Create `tests/fixtures/sample_text_documents.py` with example text documents
  - Include valid minimal document: `{"title": "Test", "authors": ["Author"], "sections": []}`
  - Include valid complete document with sections containing paragraphs
  - Include invalid documents (missing title, missing authors, wrong types)
  - Export as module-level constants or functions
  - **Acceptance**: Sample data can be imported: `from tests.fixtures.sample_text_documents import VALID_MINIMAL_DOCUMENT`

### 0.2 DocumentService Test Scaffolding [~1.5 hours]

- [ ] **P0.2.1** Create `tests/unit/test_document_service.py` with test class structure
  - Import pytest and required types
  - Create `TestDocumentService` class
  - Create pytest fixtures for mocked dependencies
  - **Acceptance**: Test file structure exists

- [ ] **P0.2.2** Write test fixtures for DocumentService dependencies
  - Fixture: `mock_storage` (in-memory dict-based storage adapter)
  - Fixture: `mock_validation_service` (returns valid by default)
  - Fixture: `mock_schema_service` (loads text.json schema)
  - Fixture: `mock_lock_service` (no-op lock)
  - Fixture: `document_service` (instantiate with mock dependencies)
  - **Acceptance**: Fixtures defined and importable

- [ ] **P0.2.3** Write test: `test_create_document_returns_doc_id_and_version`
  - Test that `create_document()` returns tuple of (DocumentId, int)
  - Assert version is 1 for new document
  - Assert document ID is valid ULID format
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.4** Write test: `test_create_document_applies_defaults_from_schema`
  - Test that created document has `sections: []` even if not provided
  - Test that required fields `title` and `authors` must have defaults or raise error
  - Load text.json schema and verify default values applied
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.5** Write test: `test_read_node_returns_content_and_version`
  - Create a document with sample data
  - Test reading root node "/" returns full document
  - Test reading nested node "/title" returns string
  - Test reading array node "/authors/0" returns first author
  - Assert version returned matches document version
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.6** Write test: `test_read_node_raises_error_for_invalid_path`
  - Test that reading non-existent path "/invalid" raises PathNotFoundError
  - Test that reading "/authors/99" raises PathNotFoundError
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.7** Write test: `test_update_node_increments_version`
  - Create document
  - Update a node (e.g., change title)
  - Assert version incremented from 1 to 2
  - Assert node value updated
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.8** Write test: `test_update_node_validates_against_schema`
  - Create document
  - Try to update "/title" with invalid type (e.g., number instead of string)
  - Assert ValidationFailedError raised
  - Assert version NOT incremented
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.9** Write test: `test_update_node_enforces_optimistic_locking`
  - Create document (version 1)
  - Update with correct version (version=1) - should succeed
  - Try to update again with stale version (version=1) - should fail
  - Assert VersionConflictError raised
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.10** Write test: `test_create_node_adds_new_section`
  - Create document with empty sections
  - Create new node at "/sections/0" with section data
  - Assert sections array now has 1 element
  - Assert version incremented
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.11** Write test: `test_delete_node_removes_section`
  - Create document with 2 sections
  - Delete node at "/sections/1"
  - Assert sections array now has 1 element
  - Assert version incremented
  - **Acceptance**: Test written, will FAIL (method not implemented)

- [ ] **P0.2.12** Write test: `test_list_documents_returns_metadata`
  - Create 3 documents
  - Call list_documents(limit=10, offset=0)
  - Assert returns list of 3 metadata dicts
  - Assert each has doc_id, version, created_at, updated_at
  - **Acceptance**: Test written, will FAIL (method not implemented)

### 0.3 DocumentService Interface Stub [~30 minutes]

- [ ] **P0.3.1** Create `src/json_schema_mcp/services/document_service.py` with class skeleton
  - Create `DocumentService` class
  - Add `__init__(self, storage, validation_service, schema_service, lock_service)`
  - Add method stubs with type hints (no implementation, just `pass` or `raise NotImplementedError`)
  - **Acceptance**: File exists, imports without error

- [ ] **P0.3.2** Add method stub: `async def create_document(self) -> tuple[DocumentId, int]`
  - Add docstring describing what it should do
  - Body: `raise NotImplementedError("To be implemented in Phase 4")`
  - **Acceptance**: Method signature defined

- [ ] **P0.3.3** Add method stubs for all CRUD operations
  - `async def read_node(self, doc_id: DocumentId, node_path: str) -> tuple[Any, int]`
  - `async def update_node(self, doc_id: DocumentId, node_path: str, node_data: Any, expected_version: int) -> tuple[Any, int]`
  - `async def create_node(self, doc_id: DocumentId, node_path: str, node_data: Any, expected_version: int) -> tuple[str, int]`
  - `async def delete_node(self, doc_id: DocumentId, node_path: str, expected_version: int) -> tuple[Any, int]`
  - `async def list_documents(self, limit: int = 100, offset: int = 0) -> list[dict]`
  - All with `raise NotImplementedError()` bodies
  - **Acceptance**: All method signatures defined with type hints

### 0.4 Run Tests (Expecting Failures) [~30 minutes]

- [ ] **P0.4.1** Create stub domain models (minimal to make tests run)
  - Create `src/json_schema_mcp/domain/models.py`
  - Add minimal `DocumentId` class (just wraps string for now)
  - Add minimal `ValidationError` class
  - Add minimal `DocumentMetadata` class
  - **Acceptance**: Tests can import domain models

- [ ] **P0.4.2** Create stub error classes (minimal to make tests run)
  - Create `src/json_schema_mcp/domain/errors.py`
  - Define: `PathNotFoundError`, `VersionConflictError`, `ValidationFailedError`
  - Each just inherits from Exception for now
  - **Acceptance**: Tests can import error classes

- [ ] **P0.4.3** Run pytest locally and verify all tests FAIL
  - Execute: `pytest tests/unit/test_document_service.py -v`
  - Verify each test fails with NotImplementedError or similar
  - Document the test output
  - **Acceptance**: ALL TESTS FAIL locally (expected!) - we have a clear todo list

- [ ] **P0.4.4** Commit the failing tests and verify CI
  - Commit message: "feat: Add DocumentService TDD tests (all failing by design)"
  - Push to feature branch
  - Verify GitHub Action runs and shows failing tests (expected)
  - Check coverage report is generated
  - **Acceptance**: CI runs, tests fail as expected, coverage report available

- [ ] **P0.4.5** Create `tests/fixtures/sample_text_documents.py` with example data
  - Define valid minimal document: `{"title": "Test", "authors": ["Author"], "sections": []}`
  - Define valid full document with sections and paragraphs
  - Define invalid documents (missing title, missing authors, wrong types)
  - Export as constants or fixtures
  - **Acceptance**: Sample data available for tests

**🎯 Phase 0 Complete When:**
- ✅ **GitHub Actions CI/CD pipeline running on every commit**
- ✅ All DocumentService unit tests written and failing
- ✅ DocumentService interface fully defined with type hints
- ✅ Test fixtures and sample data ready
- ✅ Clear TODO list of what needs implementation (the tests!)
- ✅ Can run `pytest` and see ~12 failing tests
- ✅ **CI pipeline validates every subsequent commit**
- ✅ Ready to proceed with "real" implementation phases

---

## Phase 1: Foundation & Core Infrastructure (Week 1)

### 1.1 Development Tools & Quality [~3 hours]

**Goal**: Add code quality tools and development workflow enhancements

**Note**: Basic project structure and pytest already set up in Phase 0

- [ ] **P1.1.1** Add additional production dependencies to `pyproject.toml`
  - Add `mcp` package (Model Context Protocol SDK)
  - Add `fastapi` (REST API framework)
  - Add `uvicorn` (ASGI server)
  - Update existing dependencies if needed
  - **Acceptance**: All production dependencies listed

- [ ] **P1.1.2** Configure Black code formatter
  - Add Black to dev dependencies
  - Create `.black` or `pyproject.toml` config section
  - Set line length to 100
  - **Acceptance**: `black src/ tests/` runs successfully

- [ ] **P1.1.3** Configure Pylint/Flake8 linter
  - Add linter to dev dependencies
  - Create `.pylintrc` or `.flake8` config
  - Configure max line length and ignored rules
  - **Acceptance**: `pylint src/` runs without setup errors

- [ ] **P1.1.4** Configure MyPy type checker
  - Add MyPy to dev dependencies
  - Create `mypy.ini` or `pyproject.toml` config
  - Enable strict mode
  - **Acceptance**: `mypy src/` runs successfully

- [ ] **P1.1.5** Create virtual environment management script
  - Create `scripts/setup_env.sh` (Linux/Mac) or `scripts/setup_env.ps1` (Windows)
  - Include venv creation and dependency installation
  - **Acceptance**: Script creates working environment

- [ ] **P1.1.6** Set up pre-commit hooks
  - Create `.pre-commit-config.yaml`
  - Add hooks for Black, Flake8, MyPy
  - **Acceptance**: `pre-commit run --all-files` works

---

### 1.2 Configuration Management [~3 hours]

**Goal**: Implement flexible configuration system (FR-001a to FR-001f)

- [ ] **P1.2.1** Create `src/json_schema_mcp/config.py` module
  - Define module structure
  - Import required dependencies (Pydantic, pathlib, os)
  - **Acceptance**: Module imports successfully

- [ ] **P1.2.2** Implement `ServerConfig` class with Pydantic BaseSettings
  - Define fields: `schema_path`, `storage_dir`, `lock_timeout`, `server_name`
  - Add type annotations for all fields
  - Set default values
  - **Acceptance**: Can instantiate `ServerConfig()` with defaults

- [ ] **P1.2.3** Add configuration file loading (JSON format)
  - Implement `load_from_file(path: Path)` class method
  - Parse JSON configuration file
  - Handle file not found gracefully
  - **Acceptance**: Loads valid config.json successfully

- [ ] **P1.2.4** Implement configuration precedence: env vars → config file → defaults
  - Check environment variables first (e.g., `JSON_SCHEMA_PATH`)
  - Fall back to config file values
  - Use defaults if neither present
  - **Acceptance**: Environment variables override config file

- [ ] **P1.2.5** Add configuration validation
  - Validate `schema_path` exists and is readable
  - Validate `storage_dir` is writable (create if needed)
  - Validate `lock_timeout` is positive integer
  - **Acceptance**: Raises clear error for invalid config

- [ ] **P1.2.6** Create `config.example.json` template
  - Include all configuration options with comments
  - Provide sensible example values
  - Add to repository root
  - **Acceptance**: Example file loads without errors

- [ ] **P1.2.7** Write unit tests for config module
  - Test default values
  - Test file loading
  - Test environment variable override
  - Test validation errors
  - **Acceptance**: `pytest tests/unit/test_config.py` passes

---

### 1.3 Domain Models - Full Implementation [~3.5 hours]

**Goal**: Complete domain entities and value objects (FR-010, FR-107-111)

**Note**: Basic stubs created in Phase 0.4; now we implement them fully

- [ ] **P1.3.1** Implement full `DocumentId` value object (enhance Phase 0 stub)
  - Add ULID string validation (reject invalid format)
  - Add `__str__()` and `__repr__()` methods
  - Add equality comparison and hashing
  - Validate ULID format on construction
  - **Acceptance**: Rejects invalid ULID strings, passes validation tests

- [ ] **P1.3.2** Implement `Document` entity class
  - Fields: `doc_id: DocumentId`, `content: dict`, `version: int`
  - Add `to_dict()` serialization method
  - Add `from_dict()` deserialization class method
  - **Acceptance**: Can serialize/deserialize document

- [ ] **P1.3.3** Implement full `DocumentMetadata` entity class (enhance Phase 0 stub)
  - Fields: `doc_id: DocumentId`, `version: int`, `created_at: datetime`, `updated_at: datetime`
  - Add `to_dict()` serialization with ISO 8601 timestamps
  - Add `from_dict()` deserialization class method
  - **Acceptance**: Metadata serializes to JSON-compatible dict

- [ ] **P1.3.4** Implement full `ValidationError` domain model (enhance Phase 0 stub)
  - Fields: `path: str`, `message: str`, `schema_path: str`
  - Add `to_dict()` for API responses
  - **Acceptance**: Can represent validation errors properly

- [ ] **P1.3.5** Create `ValidationReport` domain model
  - Fields: `valid: bool`, `errors: list[ValidationError]`
  - Add `to_dict()` serialization
  - Add convenience methods (`is_valid()`, `error_count()`)
  - **Acceptance**: Can collect multiple validation errors

- [ ] **P1.3.6** Write unit tests for domain models
  - Test DocumentId validation (enhance Phase 0 tests)
  - Test Document serialization
  - Test Metadata serialization with dates
  - Test ValidationReport functionality
  - **Acceptance**: `pytest tests/unit/test_models.py` passes

---

### 1.4 JSON Pointer Implementation [~5 hours]

**Goal**: RFC 6901 compliant JSON Pointer operations (FR-021 to FR-025)

- [ ] **P1.4.1** Create `src/json_schema_mcp/utils/json_pointer.py` module
  - Set up module structure
  - Import dependencies (typing, json)
  - **Acceptance**: Module imports successfully

- [ ] **P1.4.2** Implement `JSONPointer` value object class
  - Parse pointer string (e.g., "/foo/bar/0")
  - Store as list of tokens
  - Validate RFC 6901 format
  - **Acceptance**: Parses valid pointers correctly

- [ ] **P1.4.3** Implement pointer escaping/unescaping (~ and /)
  - `~0` decodes to `~`
  - `~1` decodes to `/`
  - Handle encoding when creating pointers
  - **Acceptance**: Correctly handles special characters

- [ ] **P1.4.4** Implement `get(document: dict, pointer: str) -> Any`
  - Navigate document following pointer tokens
  - Handle array indices (integer tokens)
  - Raise error if path doesn't exist
  - **Acceptance**: Retrieves nested values correctly

- [ ] **P1.4.5** Implement `set(document: dict, pointer: str, value: Any) -> dict`
  - Navigate to parent location
  - Set value at final token
  - Create intermediate objects/arrays if needed
  - Return modified document (immutable approach or copy)
  - **Acceptance**: Sets nested values correctly

- [ ] **P1.4.6** Implement `delete(document: dict, pointer: str) -> dict`
  - Navigate to parent location
  - Remove key (dict) or index (array)
  - Raise error if path doesn't exist
  - **Acceptance**: Deletes nested values correctly

- [ ] **P1.4.7** Implement `exists(document: dict, pointer: str) -> bool`
  - Check if pointer resolves to existing value
  - Return False instead of raising error
  - **Acceptance**: Correctly identifies existing paths

- [ ] **P1.4.8** Write unit tests for JSON Pointer
  - Test pointer parsing
  - Test escaping/unescaping
  - Test get/set/delete on nested objects
  - Test array operations
  - Test error conditions (invalid path, invalid pointer format)
  - **Acceptance**: `pytest tests/unit/test_json_pointer.py` passes with >95% coverage

---

## Phase 2: Storage Layer (Week 2)

### 2.1 Storage Interface & File Storage [~6 hours]

**Goal**: Abstract storage with file system implementation (FR-015 to FR-020)

- [ ] **P2.1.1** Create `src/json_schema_mcp/storage/base.py` module
  - Define abstract `StorageAdapter` interface
  - Declare abstract methods: `save_document()`, `load_document()`, `delete_document()`, `list_documents()`, `document_exists()`
  - **Acceptance**: Interface class defined with proper signatures

- [ ] **P2.1.2** Create `src/json_schema_mcp/storage/file_storage.py` module
  - Set up `FileSystemStorage` class implementing `StorageAdapter`
  - Initialize with storage directory path
  - **Acceptance**: Class instantiates with directory path

- [ ] **P2.1.3** Implement `save_document(doc_id: DocumentId, content: dict) -> None`
  - Generate filename: `{doc_id}.json`
  - Create parent directories if needed
  - Write JSON atomically (write to temp, then rename)
  - Handle write errors
  - **Acceptance**: Saves document to filesystem

- [ ] **P2.1.4** Implement `load_document(doc_id: DocumentId) -> dict`
  - Read JSON file from `{doc_id}.json`
  - Parse JSON content
  - Raise `DocumentNotFoundError` if file doesn't exist
  - **Acceptance**: Loads existing document correctly

- [ ] **P2.1.5** Implement `delete_document(doc_id: DocumentId) -> None`
  - Delete `{doc_id}.json` file
  - Raise `DocumentNotFoundError` if file doesn't exist
  - **Acceptance**: Deletes document from filesystem

- [ ] **P2.1.6** Implement `list_documents(limit: int, offset: int) -> list[DocumentId]`
  - List all `.json` files in storage directory
  - Parse filenames to extract DocumentIds
  - Apply pagination (offset and limit)
  - **Acceptance**: Returns paginated list of doc IDs

- [ ] **P2.1.7** Implement `document_exists(doc_id: DocumentId) -> bool`
  - Check if `{doc_id}.json` file exists
  - **Acceptance**: Returns correct boolean

- [ ] **P2.1.8** Write unit tests for file storage
  - Test save/load/delete operations
  - Test list with pagination
  - Test document_exists
  - Test error conditions (missing files, write failures)
  - Use temporary directory for tests
  - **Acceptance**: `pytest tests/unit/test_file_storage.py` passes

---

### 2.2 ULID Generation [~2 hours]

**Goal**: Implement ULID generator for document IDs (FR-107 to FR-111)

- [ ] **P2.2.1** Create `src/json_schema_mcp/utils/ulid_generator.py` module
  - Import `ulid` library
  - **Acceptance**: Module imports successfully

- [ ] **P2.2.2** Implement `generate_ulid() -> str` function
  - Use `ulid.create()` or equivalent
  - Return as lowercase string
  - Ensure monotonicity within same millisecond
  - **Acceptance**: Generates valid ULID strings

- [ ] **P2.2.3** Implement `is_valid_ulid(value: str) -> bool` validator
  - Check format: 26 characters, Crockford Base32
  - Validate timestamp and randomness components
  - **Acceptance**: Validates ULID format correctly

- [ ] **P2.2.4** Write unit tests for ULID generation
  - Test ULID format validity
  - Test uniqueness (generate 1000, check no duplicates)
  - Test monotonicity (same millisecond ordering)
  - Test is_valid_ulid with valid/invalid inputs
  - **Acceptance**: `pytest tests/unit/test_ulid_generator.py` passes

---

### 2.3 Metadata File Storage [~4 hours]

**Goal**: Store document metadata separately (FR-016a to FR-016d)

- [ ] **P2.3.1** Extend `FileSystemStorage` with metadata methods
  - Add methods to storage interface and implementation
  - **Acceptance**: Methods defined with signatures

- [ ] **P2.3.2** Implement `save_metadata(doc_id: DocumentId, metadata: DocumentMetadata) -> None`
  - Generate filename: `{doc_id}.meta.json`
  - Serialize metadata to JSON
  - Write atomically
  - **Acceptance**: Saves metadata file alongside document

- [ ] **P2.3.3** Implement `load_metadata(doc_id: DocumentId) -> DocumentMetadata`
  - Read `{doc_id}.meta.json`
  - Parse and deserialize to DocumentMetadata
  - Raise error if metadata file missing
  - **Acceptance**: Loads metadata correctly

- [ ] **P2.3.4** Implement `delete_metadata(doc_id: DocumentId) -> None`
  - Delete `{doc_id}.meta.json` file
  - No error if file doesn't exist (idempotent)
  - **Acceptance**: Deletes metadata file

- [ ] **P2.3.5** Update `delete_document()` to delete both files
  - Delete both `{doc_id}.json` and `{doc_id}.meta.json`
  - Handle partial deletion gracefully
  - **Acceptance**: Both files deleted together

- [ ] **P2.3.6** Write unit tests for metadata storage
  - Test save/load metadata
  - Test metadata survives document updates
  - Test coordinated deletion
  - **Acceptance**: `pytest tests/unit/test_file_storage.py` updated and passes

---

### 2.4 Error Code System - Full Implementation [~2.5 hours]

**Goal**: Implement structured error codes (FR-095 to FR-099)

**Note**: Basic error stubs created in Phase 0.4; now we implement them fully

- [ ] **P2.4.1** Define all error code constants (enhance Phase 0 stub)
  - `DOCUMENT_NOT_FOUND = "document-not-found"`
  - `PATH_NOT_FOUND = "path-not-found"`
  - `VERSION_CONFLICT = "version-conflict"`
  - `LOCK_TIMEOUT = "lock-timeout"`
  - `LOCK_HELD = "lock-held"`
  - `VALIDATION_FAILED = "validation-failed"`
  - `REQUIRED_FIELD_WITHOUT_DEFAULT = "required-field-without-default"`
  - `SCHEMA_LOAD_FAILED = "schema-load-failed"`
  - `SCHEMA_RESOLUTION_FAILED = "schema-resolution-failed"`
  - `STORAGE_WRITE_FAILED = "storage-write-failed"`
  - `STORAGE_READ_FAILED = "storage-read-failed"`
  - Add remaining 11 error codes
  - **Acceptance**: All 22 error codes defined (FR-099)

- [ ] **P2.4.2** Implement `DocumentError` base exception class
  - Fields: `code: str`, `message: str`, `details: dict`
  - Add `to_dict()` for structured responses
  - **Acceptance**: Base exception class defined

- [ ] **P2.4.3** Implement all specific exception subclasses (enhance Phase 0 stubs)
  - Complete `DocumentNotFoundError(code="document-not-found")`
  - Complete `PathNotFoundError(code="path-not-found")`
  - Complete `VersionConflictError(code="version-conflict")`
  - Add `LockTimeoutError(code="lock-timeout")`
  - Add `LockHeldError(code="lock-held")`
  - Complete `ValidationFailedError(code="validation-failed")`
  - Add `SchemaLoadError(code="schema-load-failed")`
  - Add `SchemaResolutionError(code="schema-resolution-failed")`
  - Add `StorageError(code="storage-*")`
  - Add all remaining exception types
  - **Acceptance**: Can raise and catch specific errors with proper codes

- [ ] **P2.4.4** Write unit tests for error system
  - Test exception creation with details
  - Test to_dict() serialization
  - Test error code format (kebab-case)
  - Test inheritance hierarchy
  - **Acceptance**: `pytest tests/unit/test_errors.py` passes

---

## Phase 3: Schema & Validation (Week 3)

### 3.1 Schema Loading & Resolution [~6 hours]

**Goal**: Load and resolve JSON Schema with $ref support (FR-001 to FR-007, FR-086 to FR-090)

- [ ] **P3.1.1** Create `src/json_schema_mcp/services/schema_service.py` module
  - Set up `SchemaService` class
  - Initialize with schema file path
  - **Acceptance**: Service instantiates successfully

- [ ] **P3.1.2** Implement schema loading from file
  - Read JSON Schema file from configured path
  - Parse JSON content
  - Validate basic structure ($schema, type, properties)
  - Raise `SchemaLoadError` on failure
  - **Acceptance**: Loads valid schema file

- [ ] **P3.1.3** Implement $ref resolution using jsonschema library
  - Use `jsonschema.RefResolver` or `jsonschema.validators.Draft202012Validator`
  - Resolve internal references (`#/$defs/...`)
  - Cache resolved schema
  - **Acceptance**: Resolves $ref pointers correctly

- [ ] **P3.1.4** Implement `get_root_schema(dereferenced: bool = True) -> dict`
  - Return full schema (FR-086)
  - If `dereferenced=True`, return fully resolved schema
  - If `dereferenced=False`, return raw schema with $ref
  - **Acceptance**: Returns schema in both forms

- [ ] **P3.1.5** Implement `get_node_schema(node_path: str, dereferenced: bool = True) -> dict`
  - Navigate schema to path (e.g., "/properties/title")
  - Return schema fragment at that path
  - Optionally dereference $ref in result
  - Raise error if path doesn't exist in schema
  - **Acceptance**: Returns schema for specific paths

- [ ] **P3.1.6** Add schema caching
  - Cache both raw and dereferenced schemas
  - Invalidate cache if schema file changes
  - **Acceptance**: Repeated calls use cached schema

- [ ] **P3.1.7** Write unit tests for schema service
  - Test schema loading
  - Test $ref resolution
  - Test get_root_schema with/without dereferencing
  - Test get_node_schema for various paths
  - Test error handling (missing schema, invalid $ref)
  - Use `schemas/text.json` as test fixture
  - **Acceptance**: `pytest tests/unit/test_schema_service.py` passes

---

### 3.2 Validation Service [~5 hours]

**Goal**: Validate documents and nodes against schema (FR-058 to FR-064)

- [ ] **P3.2.1** Create `src/json_schema_mcp/services/validation_service.py` module
  - Set up `ValidationService` class
  - Initialize with `SchemaService` dependency
  - **Acceptance**: Service instantiates with schema service

- [ ] **P3.2.2** Implement `validate_document(content: dict) -> ValidationReport`
  - Get root schema from schema service
  - Validate full document using jsonschema
  - Collect all validation errors
  - Return ValidationReport with errors
  - **Acceptance**: Validates complete documents

- [ ] **P3.2.3** Implement `validate_node(node_path: str, value: Any) -> ValidationReport`
  - Get node schema from schema service
  - Validate value against node schema
  - Collect validation errors
  - Return ValidationReport
  - **Acceptance**: Validates individual nodes

- [ ] **P3.2.4** Convert jsonschema errors to ValidationError domain objects
  - Map jsonschema.ValidationError to our ValidationError
  - Extract path, message, schema_path
  - Format error messages clearly
  - **Acceptance**: Error conversion works correctly

- [ ] **P3.2.5** Implement required field validation with defaults
  - Check required fields defined in schema
  - If field missing but has default, apply default
  - If field missing without default, raise error (FR-063)
  - **Acceptance**: Handles required fields correctly

- [ ] **P3.2.6** Write unit tests for validation service
  - Test valid document passes validation
  - Test invalid document fails with errors
  - Test node validation
  - Test required field handling with/without defaults
  - Test error message formatting
  - Use `schemas/text.json` as test fixture
  - **Acceptance**: `pytest tests/unit/test_validation_service.py` passes

---

## Phase 4: Document Operations (Week 4)

### 4.1 Document Service - Core CRUD Implementation [~7 hours]

**Goal**: Implement document CRUD operations to make Phase 0 tests pass (FR-008 to FR-014, FR-041 to FR-057)

**Note**: Service skeleton and method stubs created in Phase 0.3; now we implement them

- [ ] **P4.1.1** Implement `create_document() -> tuple[DocumentId, int]` (FR-008, FR-009)
  - Generate new ULID document ID
  - Get root schema with defaults from SchemaService
  - Create initial content by applying all default values
  - Validate initial content with ValidationService
  - Raise error if validation fails without defaults (FR-063)
  - Save document with version 1 using StorageAdapter
  - Save metadata (created_at, updated_at, version)
  - Return (doc_id, version)
  - **Acceptance**: Phase 0 tests for create_document PASS

- [ ] **P4.1.2** Implement `read_node(doc_id: DocumentId, node_path: str) -> tuple[Any, int]` (FR-041, FR-042)
  - Load document from storage
  - Get value at node_path using JSON Pointer
  - Load metadata for version
  - Raise `PathNotFoundError` if path doesn't exist
  - Return (node_content, version)
  - **Acceptance**: Phase 0 tests for read_node PASS

- [ ] **P4.1.3** Implement `update_node(doc_id: DocumentId, node_path: str, node_data: Any, expected_version: int) -> tuple[Any, int]` (FR-047, FR-048)
  - Acquire lock on document
  - Load document and metadata
  - Check version matches expected_version (optimistic locking)
  - Raise `VersionConflictError` if versions don't match
  - Update value at node_path using JSON Pointer
  - Validate updated document with ValidationService
  - Increment version
  - Save document and updated metadata
  - Release lock
  - Return (updated_node, new_version)
  - **Acceptance**: Phase 0 tests for update_node PASS (validation, version conflicts)

- [ ] **P4.1.4** Implement `create_node(doc_id: DocumentId, node_path: str, node_data: Any, expected_version: int) -> tuple[str, int]` (FR-052, FR-053)
  - Acquire lock on document
  - Load document and metadata
  - Check version matches expected_version
  - Check node_path doesn't already exist
  - Insert node_data at node_path (may create intermediate objects/arrays)
  - Validate updated document
  - Increment version
  - Save document and metadata
  - Release lock
  - Return (created_node_path, new_version)
  - **Acceptance**: Phase 0 tests for create_node PASS

- [ ] **P4.1.5** Implement `delete_node(doc_id: DocumentId, node_path: str, expected_version: int) -> tuple[Any, int]` (FR-054, FR-055)
  - Acquire lock on document
  - Load document and metadata
  - Check version matches expected_version
  - Check node_path exists
  - Store deleted value
  - Delete node at node_path using JSON Pointer
  - Validate updated document
  - Increment version
  - Save document and metadata
  - Release lock
  - Return (deleted_node, new_version)
  - **Acceptance**: Phase 0 tests for delete_node PASS

- [ ] **P4.1.6** Implement `list_documents(limit: int = 100, offset: int = 0) -> list[dict]` (FR-011, FR-012)
  - Call storage.list_documents(limit, offset)
  - For each doc_id, load metadata
  - Return list of metadata dicts
  - **Acceptance**: Phase 0 tests for list_documents PASS

- [ ] **P4.1.7** Verify all Phase 0 DocumentService tests now pass
  - Run: `pytest tests/unit/test_document_service.py -v`
  - All ~12 tests should now PASS (were failing in Phase 0)
  - Fix any remaining failures
  - **Acceptance**: ALL Phase 0 DocumentService tests are GREEN ✅

---

### 4.2 Lock Service [~4 hours]

**Goal**: Implement document-level locking (FR-082 to FR-082e)

- [ ] **P4.2.1** Create `src/json_schema_mcp/services/lock_service.py` module
  - Set up `LockService` class
  - Initialize with lock timeout configuration
  - Create in-memory lock registry (dict)
  - **Acceptance**: Service instantiates successfully

- [ ] **P4.2.2** Implement `acquire_lock(doc_id: DocumentId, timeout: float) -> None`
  - Check if document already locked
  - If locked, wait up to timeout seconds
  - If timeout exceeded, raise `LockTimeoutError`
  - If available, acquire lock (store timestamp and holder)
  - **Acceptance**: Acquires locks successfully

- [ ] **P4.2.3** Implement `release_lock(doc_id: DocumentId) -> None`
  - Remove lock from registry
  - Idempotent (no error if not locked)
  - **Acceptance**: Releases locks successfully

- [ ] **P4.2.4** Implement `is_locked(doc_id: DocumentId) -> bool`
  - Check if document has active lock
  - **Acceptance**: Returns correct lock status

- [ ] **P4.2.5** Implement automatic lock expiration
  - Store lock acquisition timestamp
  - Check lock age on acquire attempt
  - Auto-release expired locks (configurable expiration)
  - **Acceptance**: Expired locks released automatically

- [ ] **P4.2.6** Add lock context manager
  - Implement `__enter__` and `__exit__`
  - Ensure lock released even if exception occurs
  - **Acceptance**: Can use `with lock_service.lock(doc_id): ...`

- [ ] **P4.2.7** Write unit tests for lock service
  - Test acquire/release
  - Test timeout behavior
  - Test concurrent lock attempts
  - Test lock expiration
  - Test context manager
  - **Acceptance**: `pytest tests/unit/test_lock_service.py` passes

---

## Phase 5: Interface Layer (Week 5)

### 5.1 MCP Tool Implementations [~8 hours]

**Goal**: Implement all 8 MCP tools calling service layer (FR-065 to FR-069)

- [ ] **P5.1.1** Create `src/json_schema_mcp/mcp_tools/document_tools.py` module
  - Import MCP SDK and service dependencies
  - **Acceptance**: Module imports successfully

- [ ] **P5.1.2** Implement `document_create` tool (FR-065)
  - Define tool metadata (name, description, input schema)
  - Input: empty object `{}`
  - Call `document_service.create_document()`
  - Format response: `{success, doc_id, document_uri, schema_uri, initial_tree, version, validation_report}`
  - Handle errors and return structured error response
  - **Acceptance**: Tool creates document via MCP

- [ ] **P5.1.3** Implement `document_read_node` tool (FR-066)
  - Define tool metadata
  - Input: `{doc_id: string, node_path: string}`
  - Call `document_service.read_node(doc_id, node_path)`
  - Format response: `{success, node_content, version, node_type}`
  - Handle `PathNotFoundError` and `DocumentNotFoundError`
  - **Acceptance**: Tool reads nodes via MCP

- [ ] **P5.1.4** Implement `document_update_node` tool (FR-067)
  - Define tool metadata
  - Input: `{doc_id: string, node_path: string, node_data: any, version: integer}`
  - Call `document_service.update_node(...)`
  - Format response: `{success, updated_node, version, validation_report}`
  - Handle version conflicts and validation errors
  - **Acceptance**: Tool updates nodes via MCP

- [ ] **P5.1.5** Implement `document_create_node` tool (FR-068)
  - Define tool metadata
  - Input: `{doc_id: string, node_path: string, node_data: any, version: integer}`
  - Call `document_service.create_node(...)`
  - Format response: `{success, created_node_path, created_node, version, validation_report}`
  - Handle errors appropriately
  - **Acceptance**: Tool creates nodes via MCP

- [ ] **P5.1.6** Implement `document_delete_node` tool (FR-069)
  - Define tool metadata
  - Input: `{doc_id: string, node_path: string, version: integer}`
  - Call `document_service.delete_node(...)`
  - Format response: `{success, deleted_node, version, validation_report}`
  - Handle errors appropriately
  - **Acceptance**: Tool deletes nodes via MCP

- [ ] **P5.1.7** Implement `document_list` tool
  - Define tool metadata
  - Input: `{limit?: integer, offset?: integer}`
  - Call `document_service.list_documents(limit, offset)`
  - Format response: `{success, schema_uri, documents: array, total_documents, has_more}`
  - **Acceptance**: Tool lists documents via MCP

- [ ] **P5.1.8** Create `src/json_schema_mcp/mcp_tools/schema_tools.py` module
  - Import dependencies
  - **Acceptance**: Module imports successfully

- [ ] **P5.1.9** Implement `schema_get_node` tool
  - Define tool metadata
  - Input: `{node_path: string, dereferenced?: boolean}`
  - Call `schema_service.get_node_schema(node_path, dereferenced)`
  - Format response: `{success, node_schema}`
  - **Acceptance**: Tool returns node schema via MCP

- [ ] **P5.1.10** Implement `schema_get_root` tool
  - Define tool metadata
  - Input: `{dereferenced?: boolean}`
  - Call `schema_service.get_root_schema(dereferenced)`
  - Format response: `{success, schema_uri, root_schema, schema_version}`
  - **Acceptance**: Tool returns root schema via MCP

- [ ] **P5.1.11** Create `src/json_schema_mcp/mcp_tools/tool_registry.py` module
  - Register all 8 tools with MCP server
  - Define tool metadata and handlers
  - **Acceptance**: All tools registered successfully

- [ ] **P5.1.12** Write integration tests for MCP tools
  - Test each tool end-to-end through MCP protocol
  - Test error handling and structured responses
  - Test tool discovery
  - **Acceptance**: `pytest tests/integration/test_mcp_tools.py` passes

---

### 5.2 Server Initialization [~3 hours]

**Goal**: Set up MCP server entry point

- [ ] **P5.2.1** Create `src/json_schema_mcp/server.py` module
  - Set up MCP server initialization
  - Load configuration
  - Initialize all services
  - Register tools
  - **Acceptance**: Server module defined

- [ ] **P5.2.2** Implement server factory function
  - `create_server(config: ServerConfig) -> MCPServer`
  - Initialize service layer
  - Register all MCP tools
  - Set up error handling
  - **Acceptance**: Server instantiates correctly

- [ ] **P5.2.3** Create `src/json_schema_mcp/__main__.py` entry point
  - Parse command-line arguments
  - Load configuration
  - Create and start MCP server
  - Handle shutdown signals
  - **Acceptance**: Can run `python -m json_schema_mcp`

- [ ] **P5.2.4** Add MCP resource definitions (optional)
  - Define document resources (FR-070 to FR-072)
  - Add resource handlers
  - **Acceptance**: Resources exposed via MCP (if implemented)

- [ ] **P5.2.5** Write integration tests for server initialization
  - Test server starts successfully
  - Test configuration loading
  - Test graceful shutdown
  - **Acceptance**: `pytest tests/integration/test_server.py` passes

---

### 5.3 REST API Implementation [~8 hours]

**Goal**: Implement dual interface with REST API alongside MCP

- [ ] **P5.3.1** Create `src/json_schema_mcp/rest_api/models.py` module
  - Define Pydantic request/response models
  - Models match MCP tool schemas
  - **Acceptance**: Models defined with validation

- [ ] **P5.3.2** Define REST request models
  - `NodeUpdateRequest(node_data: Any, version: int)`
  - `NodeCreateRequest(node_data: Any, version: int)`
  - `NodeDeleteRequest(version: int)`
  - **Acceptance**: Request models validate input

- [ ] **P5.3.3** Define REST response models
  - `DocumentCreateResponse(doc_id: str, version: int, initial_tree: dict, validation_report: dict)`
  - `NodeReadResponse(node_path: str, node_content: Any, version: int, node_type: str)`
  - `NodeUpdateResponse(updated_node: Any, version: int, validation_report: dict)`
  - `SchemaNodeResponse(node_path: str, node_schema: dict)`
  - `SchemaResponse(root_schema: dict, schema_uri: str)`
  - `ErrorResponse(error: str, code: str, details: dict)`
  - **Acceptance**: Response models serialize correctly

- [ ] **P5.3.4** Create `src/json_schema_mcp/rest_api/routes/documents.py` module
  - Set up FastAPI router for document operations
  - **Acceptance**: Router defined

- [ ] **P5.3.5** Implement `POST /documents` endpoint (create_document)
  - No request body required
  - Call `document_service.create_document()`
  - Return 201 Created with DocumentCreateResponse
  - **Acceptance**: REST endpoint creates document

- [ ] **P5.3.6** Implement `GET /documents/{doc_id}` endpoint (read_node)
  - Query param: `node_path` (default: "/" for root)
  - Call `document_service.read_node(doc_id, node_path)`
  - Return 200 OK with NodeReadResponse
  - Return 404 if document/node not found
  - **Acceptance**: REST endpoint reads nodes

- [ ] **P5.3.7** Implement `PUT /documents/{doc_id}` endpoint (update_node)
  - Query params: `node_path`, `version`
  - Request body: `NodeUpdateRequest`
  - Call `document_service.update_node(...)`
  - Return 200 OK with NodeUpdateResponse
  - Return 409 Conflict on version mismatch
  - **Acceptance**: REST endpoint updates nodes

- [ ] **P5.3.8** Implement `POST /documents/{doc_id}/nodes` endpoint (create_node)
  - Query params: `node_path`, `version`
  - Request body: `NodeCreateRequest`
  - Call `document_service.create_node(...)`
  - Return 201 Created
  - **Acceptance**: REST endpoint creates nodes

- [ ] **P5.3.9** Implement `DELETE /documents/{doc_id}/nodes` endpoint (delete_node)
  - Query params: `node_path`, `version`
  - Call `document_service.delete_node(...)`
  - Return 200 OK with deleted node
  - **Acceptance**: REST endpoint deletes nodes

- [ ] **P5.3.10** Implement `GET /documents` endpoint (list_documents)
  - Query params: `limit` (default 100), `offset` (default 0)
  - Call `document_service.list_documents(limit, offset)`
  - Return 200 OK with paginated list
  - **Acceptance**: REST endpoint lists documents

- [ ] **P5.3.11** Create `src/json_schema_mcp/rest_api/routes/schema.py` module
  - Set up router for schema operations
  - **Acceptance**: Router defined

- [ ] **P5.3.12** Implement `GET /schema` endpoint (get_root_schema)
  - Query param: `dereferenced` (default true)
  - Call `schema_service.get_root_schema(dereferenced)`
  - Return 200 OK with SchemaResponse
  - **Acceptance**: REST endpoint returns root schema

- [ ] **P5.3.13** Implement `GET /schema/node` endpoint (get_node_schema)
  - Query params: `node_path`, `dereferenced` (default true)
  - Call `schema_service.get_node_schema(node_path, dereferenced)`
  - Return 200 OK with SchemaNodeResponse
  - **Acceptance**: REST endpoint returns node schema

- [ ] **P5.3.14** Create `src/json_schema_mcp/rest_api/middleware.py` module
  - Implement error handling middleware
  - Convert domain exceptions to HTTP responses
  - Add CORS middleware
  - **Acceptance**: Middleware handles errors correctly

- [ ] **P5.3.15** Create `src/json_schema_mcp/api_server.py` module
  - Set up FastAPI app factory
  - Register routers
  - Add middleware
  - Configure CORS, logging
  - **Acceptance**: REST API server runs

- [ ] **P5.3.16** Add health check endpoint `GET /health`
  - Return server status and version
  - **Acceptance**: Health check responds

- [ ] **P5.3.17** Write integration tests for REST API
  - Test all endpoints end-to-end
  - Test error responses and status codes
  - Verify responses match MCP tool outputs (same service calls)
  - **Acceptance**: `pytest tests/integration/test_rest_api.py` passes

---

## Phase 6: Testing & Documentation (Week 6)

### 6.1 Comprehensive Test Suite [~10 hours]

**Goal**: Achieve >90% code coverage with comprehensive tests

- [ ] **P6.1.1** Set up test fixtures and utilities
  - Create `tests/fixtures/` with schemas and documents
  - Copy `schemas/text.json` to test fixtures
  - Create example valid and invalid documents
  - **Acceptance**: Test fixtures available

- [ ] **P6.1.2** Complete unit test coverage for all modules
  - Ensure all domain/models tested
  - Ensure all utils tested
  - Ensure all services tested with mocks
  - **Acceptance**: Unit test coverage >90%

- [ ] **P6.1.3** Write integration tests for service layer
  - Test DocumentService with real storage and validation
  - Test error propagation
  - Test transaction-like behavior (lock acquire/release)
  - **Acceptance**: Integration tests pass

- [ ] **P6.1.4** Write end-to-end tests for MCP interface
  - Test complete workflows through MCP tools
  - Test multi-step operations (create, update, read, delete)
  - Test error scenarios
  - **Acceptance**: E2E MCP tests pass

- [ ] **P6.1.5** Write end-to-end tests for REST interface
  - Test complete workflows through REST API
  - Test multi-step operations via HTTP
  - Test error responses and status codes
  - **Acceptance**: E2E REST tests pass

- [ ] **P6.1.6** Write interface parity tests
  - Verify MCP and REST produce identical results for same service calls
  - Test that both interfaces handle errors identically
  - **Acceptance**: Parity tests confirm zero duplication

- [ ] **P6.1.7** Write concurrency tests
  - Test concurrent document access with locking
  - Test version conflict handling
  - Test race conditions
  - **Acceptance**: Concurrency tests pass

- [ ] **P6.1.8** Write atomic operation tests
  - Test transaction-like behavior of updates
  - Test rollback on validation failure
  - **Acceptance**: Atomic operation tests pass

- [ ] **P6.1.9** Set up code coverage reporting
  - Configure pytest-cov
  - Generate HTML coverage reports
  - Set minimum coverage threshold (90%)
  - **Acceptance**: Coverage reports generated

- [ ] **P6.1.10** Run full test suite and fix failing tests
  - Execute all tests
  - Debug and fix failures
  - Ensure CI-ready
  - **Acceptance**: All tests pass

---

### 6.2 Documentation [~6 hours]

**Goal**: Create comprehensive user and developer documentation

- [ ] **P6.2.1** Create `docs/architecture.md`
  - Document layered architecture
  - Explain zero-duplication pattern
  - Show data flow diagrams
  - Explain service layer as single source of truth
  - **Acceptance**: Architecture clearly documented

- [ ] **P6.2.2** Create `docs/api_reference.md`
  - Document all 8 MCP tools with examples
  - Document all REST endpoints with curl examples
  - Include request/response schemas
  - **Acceptance**: Complete API reference

- [ ] **P6.2.3** Create `docs/getting_started.md`
  - Installation instructions
  - Configuration guide
  - Quick start examples (both MCP and REST)
  - **Acceptance**: Users can get started

- [ ] **P6.2.4** Create `docs/configuration.md`
  - Document all configuration options
  - Explain precedence rules
  - Provide examples
  - **Acceptance**: Configuration fully documented

- [ ] **P6.2.5** Create `docs/error_handling.md`
  - List all error codes
  - Explain error response format
  - Provide examples
  - **Acceptance**: Error handling documented

- [ ] **P6.2.6** Create `docs/json_pointer_guide.md`
  - Explain JSON Pointer syntax
  - Provide examples
  - Document edge cases
  - **Acceptance**: JSON Pointer usage clear

- [ ] **P6.2.7** Create `docs/development.md`
  - Development setup
  - Running tests
  - Code style guidelines
  - Contributing guidelines
  - **Acceptance**: Developers can contribute

- [ ] **P6.2.8** Update README.md
  - Add project overview
  - Add feature highlights (dual interface: MCP + REST)
  - Add quick start
  - Link to detailed docs
  - **Acceptance**: README is informative

- [ ] **P6.2.9** Add inline code documentation
  - Add docstrings to all public functions
  - Add type hints everywhere
  - Add usage examples in docstrings
  - **Acceptance**: Code is self-documenting

- [ ] **P6.2.10** Generate API documentation with Sphinx or MkDocs
  - Set up documentation generator
  - Configure auto-generation from docstrings
  - Build HTML docs
  - **Acceptance**: API docs generated

---

## Phase 7: Polish & Release Prep (Final Week)

### 7.1 Error Handling & Logging [~3 hours]

**Goal**: Production-ready error handling and observability

- [ ] **P7.1.1** Implement structured logging throughout codebase
  - Add logging statements in services
  - Log all operations (create, read, update, delete)
  - Log errors with context
  - **Acceptance**: Comprehensive logging in place

- [ ] **P7.1.2** Configure log levels and formatting
  - Set up JSON structured logging
  - Configure log levels per module
  - Add request IDs for tracing (REST API)
  - **Acceptance**: Logs are machine-readable

- [ ] **P7.1.3** Add error monitoring hooks
  - Add error notification capability
  - Log stack traces for exceptions
  - **Acceptance**: Errors are traceable

---

### 7.2 Configuration & Deployment [~3 hours]

**Goal**: Production deployment readiness

- [ ] **P7.2.1** Create Docker configuration
  - Write `Dockerfile` for MCP server
  - Write `Dockerfile` for REST API server
  - Create `docker-compose.yml` for local development
  - **Acceptance**: Server runs in Docker

- [ ] **P7.2.2** Create deployment scripts
  - Add startup scripts for both interfaces
  - Add health check scripts
  - **Acceptance**: Easy deployment

- [ ] **P7.2.3** Document deployment options
  - Document Docker deployment
  - Document standalone deployment
  - Document environment variables
  - **Acceptance**: Deployment documented

---

### 7.3 Final Testing [~4 hours]

**Goal**: Ensure production readiness

- [ ] **P7.3.1** Perform manual testing
  - Test all MCP tools manually
  - Test all REST endpoints manually with Postman/curl
  - Test error scenarios
  - **Acceptance**: Manual tests pass

- [ ] **P7.3.2** Run performance tests
  - Test with large documents
  - Test concurrent operations
  - Test lock contention scenarios
  - **Acceptance**: Performance acceptable

- [ ] **P7.3.3** Run security audit
  - Check input validation
  - Check file path traversal protection
  - Check for injection vulnerabilities
  - **Acceptance**: No security issues

- [ ] **P7.3.4** Final integration test
  - Run complete test suite
  - Verify all tests pass
  - Check coverage thresholds
  - **Acceptance**: All tests pass, coverage >90%

- [ ] **P7.3.5** Create release checklist
  - Version tagging
  - Changelog update
  - Documentation review
  - **Acceptance**: Ready for release

---

## Summary Statistics

**Total Tasks**: 170+
**Estimated Hours**: 79-99 hours (2 months part-time or 2 weeks full-time)
**Phases**: 8 (includes Phase 0: TDD Bootstrap with CI/CD)
**Key Deliverables**:
- Fully functional MCP server with 8 tools
- Fully functional REST API with equivalent endpoints
- Shared service layer (zero duplication)
- Comprehensive test suite (>90% coverage)
- Complete documentation
- Production-ready deployment configuration

**Critical Success Factors**:
1. ✅ **CI/CD FIRST** - GitHub Actions pipeline validates every commit
2. ✅ **Test-driven development** - Write failing tests FIRST (Phase 0)
3. ✅ Zero code duplication (all logic in service layer)
4. ✅ Both interfaces use identical service methods
5. ✅ Comprehensive error handling with structured errors
6. ✅ Clear separation of concerns (interface → service → storage)
7. ✅ Complete documentation for users and developers

**TDD Workflow with CI/CD**:
1. **Phase 0.0**: Set up GitHub Actions (CI runs on every push)
2. **Phase 0.1-0.4**: Write DocumentService tests first (all failing, CI shows failures)
3. **Phases 1-4**: Implement foundation to make tests pass (CI turns green incrementally)
4. **Phase 5**: Add interface layers (MCP + REST, CI validates both)
5. **Phases 6-7**: Complete testing and polish (CI maintains quality)

**Next Steps**:
1. Review and approve this task breakdown
2. Set up project board with these tasks
3. **BEGIN PHASE 0.0**: Set up GitHub Actions CI/CD FIRST!
4. **PHASE 0.1-0.4**: Write DocumentService tests FIRST (expect failures!)
5. Use failing tests to guide implementation in subsequent phases
6. Watch CI turn from red → green as features are completed
7. Maintain interface parity throughout development
8. Never commit code that breaks tests (keep CI green)

**Phase 0 Deliverable** (Day 1):
- ✅ **GitHub Actions workflow running tests + coverage on every commit**
- ✅ ~12 failing DocumentService unit tests
- ✅ DocumentService interface stub (all methods raise NotImplementedError)
- ✅ Sample text.json test data
- ✅ Clear roadmap of what needs implementation
- ✅ **CI pipeline ready to validate all future work**
