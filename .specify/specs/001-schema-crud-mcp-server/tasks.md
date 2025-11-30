# Task Decomposition: JSON Schema CRUD MCP Server
## Implementation Checklist

**Feature Branch**: `001-schema-crud-mcp-server`  
**Created**: 2025-11-29  
**Updated**: 2025-11-29 (Monorepo Structure)  
**Status**: Ready for Implementation

---

## Directory Structure Note

**This project uses a monorepo structure:**
- `apps/mcp_server/` - MCP interface application (thin adapters)
- `apps/rest_api/` - REST API application (thin adapters)
- `lib/json_schema_core/` - Shared core library (all business logic)
- `tests/lib/` - Core library unit tests
- `tests/apps/` - Application integration tests

**All business logic lives in `lib/json_schema_core/`** - the apps/ directories contain only thin protocol adapters.

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

## Phase 0: TDD Bootstrap - Core Library Foundation [Day 1, ~6 hours]

**Goal**: Build DocumentService core library incrementally with TRUE TDD - each task produces a test file + implementation file pair

**Philosophy - True TDD Cycle (Red-Green-Refactor):**
1. **RED**: Write a failing test for ONE specific behavior
2. **GREEN**: Write minimal code to make that ONE test pass
3. **REFACTOR**: Clean up code while keeping tests green
4. **COMMIT**: Commit the test + implementation together
5. **REPEAT**: Move to next behavior

**Why This Approach:**
- ✅ Each task is self-contained (test + impl)
- ✅ No overlap between tasks - clear dependencies
- ✅ Can commit after each task with passing tests
- ✅ Focus on DocumentService CORE LIBRARY first
- ✅ MCP and REST interfaces come later (they're just thin adapters)

---

### 0.0 CI/CD Setup - GitHub Actions for TDD [~30 minutes] ✅ COMPLETE

- [x] **P0.0.1** Create `.github/workflows/` directory
- [x] **P0.0.2** Create `ci.yml` GitHub Actions workflow  
- [x] **P0.0.3** Add test execution steps to workflow
- [x] **P0.0.4** Create dummy test to validate CI pipeline
- [x] **P0.0.5** Add coverage badge to README

**🎯 Critical**: This CI/CD pipeline will validate EVERY subsequent task. All future commits must keep tests green!

---

### 0.1 Project Structure + Domain Models [~45 minutes]

**Goal**: Set up Python project with core domain models needed for DocumentService

- [ ] **P0.1.1** Create monorepo directory structure
  - Create `lib/json_schema_core/` with `__init__.py`
  - Create `lib/json_schema_core/domain/` with `__init__.py`
  - Create `lib/json_schema_core/services/` with `__init__.py`
  - Create `lib/json_schema_core/storage/` with `__init__.py`
  - Create `lib/json_schema_core/utils/` with `__init__.py`
  - Create `tests/lib/` with `__init__.py`
  - Create `tests/lib/domain/` with `__init__.py`
  - Create `tests/fixtures/schemas/` (no __init__.py needed)
  - **Acceptance**: Directory structure exists, can import `lib.json_schema_core`
  - **Commit**: `"chore: create monorepo structure for core library"`

- [ ] **P0.1.2** Create `pyproject.toml` with dependencies
  - Project name: `json-schema-mcp-tool`, version: `0.1.0`
  - Python: `>=3.11`
  - Core deps: `jsonschema = "^4.20.0"`, `python-ulid = "^2.2.0"`, `pydantic = "^2.5.0"`
  - Dev deps: `pytest = "^8.0.0"`, `pytest-asyncio = "^0.23.0"`, `pytest-cov = "^4.1.0"`
  - **Acceptance**: Can run `pip install -e .` without errors
  - **Commit**: `"chore: add pyproject.toml with core dependencies"`

- [ ] **P0.1.3** Create `pytest.ini` configuration
  - Set `testpaths = tests`
  - Set `asyncio_mode = auto`
  - Set `pythonpath = lib` (so tests can import from lib.json_schema_core)
  - Set `addopts = --cov=lib --cov-report=term-missing --cov-report=xml --cov-report=html --junitxml=pytest-report.xml -v`
  - **Acceptance**: `pytest --version` works, pytest.ini is read
  - **Commit**: `"chore: configure pytest for monorepo structure"`

- [ ] **P0.1.4** Write test + impl: DocumentId value object
  - **TEST**: Create `tests/lib/domain/test_document_id.py`
    - Test: `test_document_id_from_ulid_string()` - Create from ULID string
    - Test: `test_document_id_generate()` - Generate new ULID
    - Test: `test_document_id_str_conversion()` - Convert to string
  - **IMPL**: Create `lib/json_schema_core/domain/document_id.py`
    - Class: `DocumentId` (wraps ULID string)
    - Method: `__init__(self, value: str)`
    - Method: `@classmethod def generate(cls) -> DocumentId`
    - Method: `__str__(self) -> str`
  - **Acceptance**: Tests pass, 100% coverage on DocumentId
  - **Commit**: `"feat(domain): add DocumentId value object with tests"`

- [ ] **P0.1.5** Write test + impl: Domain exceptions
  - **TEST**: Create `tests/lib/domain/test_errors.py`
    - Test: `test_path_not_found_error()` - Can raise and catch
    - Test: `test_version_conflict_error()` - Contains version info
    - Test: `test_validation_failed_error()` - Contains validation details
    - Test: `test_document_not_found_error()` - Contains doc_id
  - **IMPL**: Create `lib/json_schema_core/domain/errors.py`
    - Class: `PathNotFoundError(Exception)` - has `path: str`
    - Class: `VersionConflictError(Exception)` - has `expected: int, actual: int`
    - Class: `ValidationFailedError(Exception)` - has `errors: list`
    - Class: `DocumentNotFoundError(Exception)` - has `doc_id: str`
  - **Acceptance**: All tests pass
  - **Commit**: `"feat(domain): add domain exceptions with tests"`

- [ ] **P0.1.6** Write test + impl: DocumentMetadata value object
  - **TEST**: Create `tests/lib/domain/test_metadata.py`
    - Test: `test_metadata_creation()` - Create with all fields
    - Test: `test_metadata_from_dict()` - Deserialize from dict
    - Test: `test_metadata_to_dict()` - Serialize to dict
    - Test: `test_metadata_increment_version()` - Update version and timestamp
  - **IMPL**: Create `lib/json_schema_core/domain/metadata.py`
    - Class: `DocumentMetadata` (Pydantic model or dataclass)
    - Fields: `doc_id: str, version: int, created_at: datetime, updated_at: datetime`
    - Method: `increment_version(self) -> DocumentMetadata`
  - **Acceptance**: All tests pass
  - **Commit**: `"feat(domain): add DocumentMetadata with tests"`

- [ ] **P0.1.7** Copy test schema to fixtures
  - Copy `schemas/text.json` to `tests/fixtures/schemas/text.json`
  - Create `tests/fixtures/schemas/__init__.py` that exports path constant
  - **Acceptance**: Test can import schema path
  - **Commit**: `"test: add text.json schema to fixtures"`

**Remove tests/test_dummy.py** after P0.1.3 completes

---

### 0.2 Storage Layer - FileSystemStorage [~1.5 hours]

**Goal**: Build storage abstraction with tests BEFORE DocumentService needs it

- [ ] **P0.2.1** Write test + impl: StorageInterface (abstract base)
  - **TEST**: Create `tests/lib/storage/test_storage_interface.py`
    - Test: `test_cannot_instantiate_interface()` - ABC cannot be instantiated
  - **IMPL**: Create `lib/json_schema_core/storage/storage_interface.py`
    - Class: `StorageInterface(ABC)`
    - Abstract methods: `read_document()`, `write_document()`, `delete_document()`, `list_documents()`, `read_metadata()`, `write_metadata()`
  - **Acceptance**: Test passes
  - **Commit**: `"feat(storage): add StorageInterface ABC with tests"`

- [ ] **P0.2.2** Write test + impl: FileSystemStorage - write_document
  - **TEST**: Create `tests/lib/storage/test_file_storage.py`
    - Test: `test_write_document_creates_file(tmp_path)` - Write JSON document
    - Test: `test_write_document_atomic(tmp_path)` - Uses temp file + rename
  - **IMPL**: Create `lib/json_schema_core/storage/file_storage.py`
    - Class: `FileSystemStorage(StorageInterface)`
    - Method: `__init__(self, base_path: Path)`
    - Method: `write_document(self, doc_id: str, content: dict) -> None`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(storage): implement write_document with atomic writes"`

- [ ] **P0.2.3** Write test + impl: FileSystemStorage - read_document
  - **TEST**: Add to `tests/lib/storage/test_file_storage.py`
    - Test: `test_read_document_returns_content(tmp_path)` - Read written document
    - Test: `test_read_document_raises_not_found(tmp_path)` - Missing file raises error
  - **IMPL**: Update `lib/json_schema_core/storage/file_storage.py`
    - Method: `read_document(self, doc_id: str) -> dict`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(storage): implement read_document with error handling"`

- [ ] **P0.2.4** Write test + impl: FileSystemStorage - metadata operations
  - **TEST**: Add to `tests/lib/storage/test_file_storage.py`
    - Test: `test_write_metadata(tmp_path)` - Write metadata JSON
    - Test: `test_read_metadata(tmp_path)` - Read metadata JSON
    - Test: `test_read_metadata_missing_returns_none(tmp_path)` - No file = None
  - **IMPL**: Update `lib/json_schema_core/storage/file_storage.py`
    - Method: `write_metadata(self, doc_id: str, metadata: dict) -> None`
    - Method: `read_metadata(self, doc_id: str) -> dict | None`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(storage): add metadata read/write operations"`

- [ ] **P0.2.5** Write test + impl: FileSystemStorage - list_documents
  - **TEST**: Add to `tests/lib/storage/test_file_storage.py`
    - Test: `test_list_documents_empty(tmp_path)` - Empty storage returns []
    - Test: `test_list_documents_returns_doc_ids(tmp_path)` - Returns list of IDs
    - Test: `test_list_documents_pagination(tmp_path)` - Limit/offset work
  - **IMPL**: Update `lib/json_schema_core/storage/file_storage.py`
    - Method: `list_documents(self, limit: int = 100, offset: int = 0) -> list[str]`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(storage): implement list_documents with pagination"`

- [ ] **P0.2.6** Write test + impl: FileSystemStorage - delete_document
  - **TEST**: Add to `tests/lib/storage/test_file_storage.py`
    - Test: `test_delete_document_removes_file(tmp_path)` - File deleted
    - Test: `test_delete_document_removes_metadata(tmp_path)` - Metadata deleted
    - Test: `test_delete_document_missing_is_ok(tmp_path)` - Idempotent
  - **IMPL**: Update `lib/json_schema_core/storage/file_storage.py`
    - Method: `delete_document(self, doc_id: str) -> None`
  - **Acceptance**: Tests pass, FileSystemStorage complete
  - **Commit**: `"feat(storage): implement delete_document"`

---

### 0.3 Utility Layer - JSONPointer & ULID [~45 minutes]

**Goal**: Build utility functions needed by DocumentService

- [ ] **P0.3.1** Write test + impl: JSONPointer - parse and resolve
  - **TEST**: Create `tests/lib/utils/test_json_pointer.py`
    - Test: `test_parse_pointer()` - Parse "/title" into ["title"]
    - Test: `test_parse_nested_pointer()` - Parse "/sections/0/paragraphs/1"
    - Test: `test_resolve_pointer()` - Get value from document
    - Test: `test_resolve_pointer_not_found()` - Raises PathNotFoundError
  - **IMPL**: Create `lib/json_schema_core/utils/json_pointer.py`
    - Function: `parse_pointer(pointer: str) -> list[str]`
    - Function: `resolve_pointer(document: dict, pointer: str) -> Any`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(utils): add JSONPointer resolution with tests"`

- [ ] **P0.3.2** Write test + impl: JSONPointer - set and delete
  - **TEST**: Add to `tests/lib/utils/test_json_pointer.py`
    - Test: `test_set_pointer()` - Update value at pointer
    - Test: `test_set_pointer_creates_path()` - Create missing intermediate objects
    - Test: `test_delete_pointer()` - Remove value at pointer
  - **IMPL**: Update `lib/json_schema_core/utils/json_pointer.py`
    - Function: `set_pointer(document: dict, pointer: str, value: Any) -> dict`
    - Function: `delete_pointer(document: dict, pointer: str) -> dict`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(utils): add JSONPointer set/delete operations"`

---

### 0.4 Service Layer - ValidationService [~30 minutes]

**Goal**: Build ValidationService before DocumentService depends on it

- [ ] **P0.4.1** Write test + impl: ValidationService - validate document
  - **TEST**: Create `tests/lib/services/test_validation_service.py`
    - Test: `test_validate_valid_document()` - Returns True for valid doc
    - Test: `test_validate_invalid_document()` - Raises ValidationFailedError
    - Test: `test_validation_error_details()` - Error has validation details
  - **IMPL**: Create `lib/json_schema_core/services/validation_service.py`
    - Class: `ValidationService`
    - Method: `__init__(self, schema: dict)`
    - Method: `validate(self, document: dict) -> None` (raises on failure)
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): add ValidationService with tests"`

- [ ] **P0.4.2** Write test + impl: ValidationService - apply defaults
  - **TEST**: Add to `tests/lib/services/test_validation_service.py`
    - Test: `test_apply_defaults_adds_missing_fields()` - Adds default values
    - Test: `test_apply_defaults_keeps_provided_values()` - Doesn't override
  - **IMPL**: Update `lib/json_schema_core/services/validation_service.py`
    - Method: `apply_defaults(self, document: dict) -> dict`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): add apply_defaults to ValidationService"`

---

### 0.5 Service Layer - SchemaService [~20 minutes]

**Goal**: Build SchemaService to load schemas

- [ ] **P0.5.1** Write test + impl: SchemaService - load schema
  - **TEST**: Create `tests/lib/services/test_schema_service.py`
    - Test: `test_load_schema_from_file()` - Load text.json schema
    - Test: `test_load_schema_caches()` - Doesn't reload every time
    - Test: `test_load_schema_not_found()` - Raises error for missing schema
  - **IMPL**: Create `lib/json_schema_core/services/schema_service.py`
    - Class: `SchemaService`
    - Method: `__init__(self, schema_dir: Path)`
    - Method: `load_schema(self, schema_name: str) -> dict`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): add SchemaService with tests"`

**🎯 Phase 0 Complete When:**
- ✅ All domain models implemented with tests
- ✅ FileSystemStorage fully implemented with tests
- ✅ JSONPointer utilities implemented with tests
- ✅ ValidationService and SchemaService implemented with tests
- ✅ **All tests passing, 100% coverage**
- ✅ Can run `pytest tests/lib/` and see ALL GREEN
- ✅ Ready to build DocumentService in Phase 1 (it now has all dependencies)

---

## Phase 1: DocumentService Implementation [Day 2-3, ~8 hours]

**Goal**: Build DocumentService with ALL dependencies already implemented and tested in Phase 0

**Prerequisite**: Phase 0 complete - we have:
- ✅ Domain models (DocumentId, DocumentMetadata, errors)
- ✅ FileSystemStorage (full CRUD + metadata)
- ✅ JSONPointer utilities
- ✅ ValidationService (validate + apply_defaults)
- ✅ SchemaService (load schema)

**Approach**: Write test + implementation for each DocumentService method

---

### 1.1 DocumentService - create_document [~1.5 hours]

### 1.1 DocumentService - create_document [~1.5 hours]

- [ ] **P1.1.1** Write test: create_document with valid data
  - **TEST**: Create `tests/lib/services/test_document_service.py`
    - Test: `test_create_document_success()` - Creates doc, returns doc_id + version
    - Test: `test_create_document_generates_ulid()` - Doc ID is valid ULID
    - Test: `test_create_document_version_is_one()` - Initial version = 1
    - Test: `test_create_document_saves_to_storage()` - Calls storage.write_document()
  - **Acceptance**: Tests written and FAIL
  - **Commit**: `"test(services): add create_document tests (failing)"`

- [ ] **P1.1.2** Implement: DocumentService.create_document()
  - **IMPL**: Create `lib/json_schema_core/services/document_service.py`
    - Class: `DocumentService`
    - Method: `__init__(self, storage, validation_service, schema_service)`
    - Method: `async def create_document(self, schema_name: str, content: dict) -> tuple[str, int]`
      - Generate new DocumentId
      - Apply schema defaults via ValidationService
      - Validate document via ValidationService
      - Create DocumentMetadata (version=1)
      - Write document to storage
      - Write metadata to storage
      - Return (doc_id, version)
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): implement DocumentService.create_document()"`

---

### 1.2 DocumentService - read_node [~1.5 hours]

- [ ] **P1.2.1** Write test: read_node with various paths
  - **TEST**: Add to `tests/lib/services/test_document_service.py`
    - Test: `test_read_node_root()` - Read "/" returns full document
    - Test: `test_read_node_field()` - Read "/title" returns string
    - Test: `test_read_node_nested()` - Read "/sections/0/title" works
    - Test: `test_read_node_array_element()` - Read "/authors/1" works
    - Test: `test_read_node_not_found()` - Raises PathNotFoundError
    - Test: `test_read_node_returns_version()` - Returns correct version
  - **Acceptance**: Tests written and FAIL
  - **Commit**: `"test(services): add read_node tests (failing)"`

- [ ] **P1.2.2** Implement: DocumentService.read_node()
  - **IMPL**: Update `lib/json_schema_core/services/document_service.py`
    - Method: `async def read_node(self, doc_id: str, node_path: str) -> tuple[Any, int]`
      - Load document from storage (raise DocumentNotFoundError if missing)
      - Load metadata from storage
      - Use JSONPointer to resolve path
      - Return (value, version)
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): implement DocumentService.read_node()"`

---

### 1.3 DocumentService - update_node [~2 hours]

- [ ] **P1.3.1** Write test: update_node with validation and versioning
  - **TEST**: Add to `tests/lib/services/test_document_service.py`
    - Test: `test_update_node_success()` - Updates value, increments version
    - Test: `test_update_node_validates()` - Rejects invalid data
    - Test: `test_update_node_version_conflict()` - Raises VersionConflictError
    - Test: `test_update_node_updates_timestamp()` - Updates updated_at
    - Test: `test_update_node_path_not_found()` - Raises PathNotFoundError
  - **Acceptance**: Tests written and FAIL
  - **Commit**: `"test(services): add update_node tests (failing)"`

- [ ] **P1.3.2** Implement: DocumentService.update_node()
  - **IMPL**: Update `lib/json_schema_core/services/document_service.py`
    - Method: `async def update_node(self, doc_id: str, node_path: str, value: Any, expected_version: int) -> tuple[Any, int]`
      - Load document and metadata
      - Check version matches expected_version (raise VersionConflictError if not)
      - Use JSONPointer to update path
      - Validate updated document
      - Increment version in metadata
      - Write document and metadata
      - Return (value, new_version)
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): implement DocumentService.update_node()"`

---

### 1.4 DocumentService - create_node [~1.5 hours]

- [ ] **P1.4.1** Write test: create_node (add to array/object)
  - **TEST**: Add to `tests/lib/services/test_document_service.py`
    - Test: `test_create_node_append_to_array()` - Adds to "/sections"
    - Test: `test_create_node_validates()` - Rejects invalid data
    - Test: `test_create_node_increments_version()` - Version++
    - Test: `test_create_node_version_conflict()` - Checks version
  - **Acceptance**: Tests written and FAIL
  - **Commit**: `"test(services): add create_node tests (failing)"`

- [ ] **P1.4.2** Implement: DocumentService.create_node()
  - **IMPL**: Update `lib/json_schema_core/services/document_service.py`
    - Method: `async def create_node(self, doc_id: str, node_path: str, value: Any, expected_version: int) -> tuple[str, int]`
      - Load document and metadata
      - Check version
      - Use JSONPointer to insert value (append to array or add to object)
      - Validate updated document
      - Increment version
      - Write document and metadata
      - Return (created_path, new_version)
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): implement DocumentService.create_node()"`

---

### 1.5 DocumentService - delete_node [~1.5 hours]

- [ ] **P1.5.1** Write test: delete_node
  - **TEST**: Add to `tests/lib/services/test_document_service.py`
    - Test: `test_delete_node_from_array()` - Removes from array
    - Test: `test_delete_node_from_object()` - Removes field
    - Test: `test_delete_node_validates()` - Validates result
    - Test: `test_delete_node_increments_version()` - Version++
    - Test: `test_delete_node_not_found()` - Raises PathNotFoundError
  - **Acceptance**: Tests written and FAIL
  - **Commit**: `"test(services): add delete_node tests (failing)"`

- [ ] **P1.5.2** Implement: DocumentService.delete_node()
  - **IMPL**: Update `lib/json_schema_core/services/document_service.py`
    - Method: `async def delete_node(self, doc_id: str, node_path: str, expected_version: int) -> tuple[Any, int]`
      - Load document and metadata
      - Check version
      - Use JSONPointer to delete path
      - Validate updated document
      - Increment version
      - Write document and metadata
      - Return (deleted_value, new_version)
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): implement DocumentService.delete_node()"`

---

### 1.6 DocumentService - list_documents [~1 hour]

- [ ] **P1.6.1** Write test: list_documents with pagination
  - **TEST**: Add to `tests/lib/services/test_document_service.py`
    - Test: `test_list_documents_empty()` - Returns []
    - Test: `test_list_documents_returns_metadata()` - Returns metadata dicts
    - Test: `test_list_documents_pagination()` - Limit/offset work
    - Test: `test_list_documents_sorting()` - Sorted by created_at desc
  - **Acceptance**: Tests written and FAIL
  - **Commit**: `"test(services): add list_documents tests (failing)"`

- [ ] **P1.6.2** Implement: DocumentService.list_documents()
  - **IMPL**: Update `lib/json_schema_core/services/document_service.py`
    - Method: `async def list_documents(self, limit: int = 100, offset: int = 0) -> list[dict]`
      - Call storage.list_documents(limit, offset)
      - Load metadata for each doc_id
      - Convert to dict format
      - Return list of metadata dicts
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(services): implement DocumentService.list_documents()"`

**🎯 Phase 1 Complete When:**
- ✅ DocumentService fully implemented with ALL CRUD methods
- ✅ All tests passing for DocumentService
- ✅ 100% test coverage on DocumentService
- ✅ Can run `pytest tests/lib/services/test_document_service.py -v` - ALL GREEN
- ✅ Ready to build interface layers (MCP + REST) in Phase 2

---

## Phase 2: Development Tools & Configuration [Day 3-4, ~6 hours]

**Goal**: Add code quality tools and configuration management

---

### 2.1 Development Tools & Quality [~3 hours]

**Goal**: Add code quality tools and development workflow enhancements

**Note**: Basic project structure and pytest already set up in Phase 0

**Note**: Basic project structure and pytest already set up in Phase 0

- [ ] **P2.1.1** Add additional production dependencies to `pyproject.toml`
  - Add `mcp` package (Model Context Protocol SDK)
  - Add `fastapi` (REST API framework)
  - Add `uvicorn[standard]` (ASGI server)
  - Update existing dependencies if needed
  - **Acceptance**: All production dependencies listed
  - **Commit**: `"chore: add MCP and REST API dependencies"`

- [ ] **P2.1.2** Configure Ruff linter and formatter
  - Add Ruff to dev dependencies
  - Create `ruff.toml` config or add to `pyproject.toml`
  - Set line length to 100
  - Enable key rules (F, E, W, I, N)
  - **Acceptance**: `ruff check lib/ tests/` runs successfully
  - **Commit**: `"chore: configure Ruff linter"`

- [ ] **P2.1.3** Configure MyPy type checker
  - Add MyPy to dev dependencies
  - Add `[tool.mypy]` section to `pyproject.toml`
  - Enable strict mode
  - Set Python version to 3.11
  - **Acceptance**: `mypy lib/` runs successfully
  - **Commit**: `"chore: configure MyPy type checking"`

- [ ] **P2.1.4** Set up pre-commit hooks
  - Add `pre-commit` to dev dependencies
  - Create `.pre-commit-config.yaml`
  - Add hooks for Ruff, MyPy, pytest
  - **Acceptance**: `pre-commit run --all-files` works
  - **Commit**: `"chore: add pre-commit hooks"`

---

### 2.2 Configuration Management [~3 hours]

### 2.2 Configuration Management [~3 hours]

**Goal**: Implement flexible configuration system (FR-001a to FR-001f) in core library

- [ ] **P2.2.1** Write test + impl: ServerConfig with Pydantic
  - **TEST**: Create `tests/lib/test_config.py`
    - Test: `test_config_defaults()` - Can create with defaults
    - Test: `test_config_from_dict()` - Load from dict
    - Test: `test_config_validation()` - Validates types
  - **IMPL**: Create `lib/json_schema_core/config.py`
    - Class: `ServerConfig(BaseSettings)` from Pydantic
    - Fields: `schema_path: Path`, `storage_dir: Path`, `lock_timeout: int`, `server_name: str`
    - Defaults: schema_path="./schemas", storage_dir="./storage", lock_timeout=30, server_name="json-schema-server"
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(config): add ServerConfig with Pydantic validation"`

- [ ] **P2.2.2** Write test + impl: Configuration file loading
  - **TEST**: Add to `tests/lib/test_config.py`
    - Test: `test_load_from_json(tmp_path)` - Load from JSON file
    - Test: `test_load_from_missing_file()` - Handles missing file gracefully
  - **IMPL**: Update `lib/json_schema_core/config.py`
    - Method: `@classmethod def from_file(cls, path: Path) -> ServerConfig`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(config): add JSON file loading"`

- [ ] **P2.2.3** Write test + impl: Environment variable override
  - **TEST**: Add to `tests/lib/test_config.py`
    - Test: `test_env_var_override(monkeypatch)` - Env vars override defaults
    - Test: `test_env_var_prefix()` - Uses JSON_SCHEMA_ prefix
  - **IMPL**: Update `lib/json_schema_core/config.py`
    - Use Pydantic's `model_config` with `env_prefix="JSON_SCHEMA_"`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(config): add environment variable support"`

- [ ] **P2.2.4** Create config.example.json template
  - Create `config.example.json` in repository root
  - Include all configuration options with comments (JSON doesn't support comments, so use descriptive keys)
  - Provide sensible example values
  - **Acceptance**: Example file is valid JSON
  - **Commit**: `"docs: add config.example.json template"`

**🎯 Phase 2 Complete When:**
- ✅ Code quality tools configured (Ruff, MyPy, pre-commit)
- ✅ ServerConfig implemented with tests
- ✅ Configuration supports files + env vars + defaults
- ✅ All tests passing
- ✅ Ready to build interface layers

---

## Phase 3: MCP Interface Layer [Day 5-6, ~8 hours]

**Goal**: Build MCP server as thin adapter calling DocumentService

**Prerequisites**: Phase 1 complete - DocumentService fully implemented

---

### 3.1 MCP Server Setup [~2 hours]

- [ ] **P3.1.1** Create MCP server directory structure
  - Create `apps/mcp_server/` with `__init__.py`
  - Create `apps/mcp_server/tools/` with `__init__.py`
  - Create `tests/apps/mcp_server/` with `__init__.py`
  - **Acceptance**: Directory structure exists
  - **Commit**: `"chore: create MCP server directory structure"`

- [ ] **P3.1.2** Write test + impl: MCP server initialization
  - **TEST**: Create `tests/apps/mcp_server/test_server.py`
    - Test: `test_server_init()` - Can create server instance
    - Test: `test_server_has_config()` - Loads configuration
  - **IMPL**: Create `apps/mcp_server/server.py`
    - Class: `MCPServer`
    - Method: `__init__(self, config: ServerConfig)`
    - Initialize MCP server from SDK
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): initialize MCP server"`

- [ ] **P3.1.3** Write test + impl: Service dependency injection
  - **TEST**: Add to `tests/apps/mcp_server/test_server.py`
    - Test: `test_server_creates_services()` - Initializes DocumentService, etc.
  - **IMPL**: Update `apps/mcp_server/server.py`
    - Initialize FileSystemStorage
    - Initialize ValidationService, SchemaService
    - Initialize DocumentService with dependencies
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): add service dependency injection"`

---

### 3.2 MCP Tools - Document CRUD [~4 hours]

- [ ] **P3.2.1** Write test + impl: document_create tool
  - **TEST**: Create `tests/apps/mcp_server/test_document_tools.py`
    - Test: `test_document_create_success()` - Calls DocumentService.create_document()
    - Test: `test_document_create_validation_error()` - Returns error response
  - **IMPL**: Create `apps/mcp_server/tools/document_tools.py`
    - Function: `@mcp_tool async def document_create(schema_name: str, content: dict) -> dict`
    - Call: `document_service.create_document(schema_name, content)`
    - Return: `{"doc_id": str, "version": int}`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): implement document_create tool"`

- [ ] **P3.2.2** Write test + impl: document_read_node tool
  - **TEST**: Add to `tests/apps/mcp_server/test_document_tools.py`
    - Test: `test_document_read_node_success()` - Returns node content
    - Test: `test_document_read_node_not_found()` - Returns error
  - **IMPL**: Update `apps/mcp_server/tools/document_tools.py`
    - Function: `@mcp_tool async def document_read_node(doc_id: str, node_path: str) -> dict`
    - Call: `document_service.read_node(doc_id, node_path)`
    - Return: `{"content": Any, "version": int}`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): implement document_read_node tool"`

- [ ] **P3.2.3** Write test + impl: document_update_node tool
  - **TEST**: Add to `tests/apps/mcp_server/test_document_tools.py`
    - Test: `test_document_update_node_success()` - Updates and returns new version
    - Test: `test_document_update_node_version_conflict()` - Returns conflict error
  - **IMPL**: Update `apps/mcp_server/tools/document_tools.py`
    - Function: `@mcp_tool async def document_update_node(doc_id: str, node_path: str, value: Any, expected_version: int) -> dict`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): implement document_update_node tool"`

- [ ] **P3.2.4** Write test + impl: document_create_node tool
  - **TEST**: Add to `tests/apps/mcp_server/test_document_tools.py`
    - Test: `test_document_create_node_success()` - Creates and returns path
  - **IMPL**: Update `apps/mcp_server/tools/document_tools.py`
    - Function: `@mcp_tool async def document_create_node(...)`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): implement document_create_node tool"`

- [ ] **P3.2.5** Write test + impl: document_delete_node tool
  - **TEST**: Add to `tests/apps/mcp_server/test_document_tools.py`
  - **IMPL**: Update `apps/mcp_server/tools/document_tools.py`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): implement document_delete_node tool"`

- [ ] **P3.2.6** Write test + impl: document_list tool
  - **TEST**: Add to `tests/apps/mcp_server/test_document_tools.py`
  - **IMPL**: Update `apps/mcp_server/tools/document_tools.py`
  - **Acceptance**: Tests pass
  - **Commit**: `"feat(mcp): implement document_list tool"`

---

### 3.3 MCP Server Entry Point [~2 hours]

- [ ] **P3.3.1** Create __main__.py for MCP server
  - Create `apps/mcp_server/__main__.py`
  - Load configuration
  - Initialize server
  - Start MCP server (stdio transport)
  - **Acceptance**: Can run `python -m apps.mcp_server`
  - **Commit**: `"feat(mcp): add server entry point"`

- [ ] **P3.3.2** Create integration test for MCP server
  - **TEST**: Create `tests/apps/mcp_server/test_integration.py`
    - Test: `test_full_document_lifecycle()` - Create, read, update, delete via MCP tools
  - **Acceptance**: Integration test passes
  - **Commit**: `"test(mcp): add integration test"`

**🎯 Phase 3 Complete When:**
- ✅ MCP server fully functional
- ✅ All document CRUD tools implemented
- ✅ All tests passing
- ✅ Can run MCP server: `python -m apps.mcp_server`
- ✅ Ready to build REST API interface

---

## Phase 4: REST API Interface Layer [Day 7-8, ~8 hours]

**Goal**: Build REST API as thin adapter calling DocumentService (parallel to MCP)
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
  - **Acceptance**: `pytest tests/lib/test_json_pointer.py` passes with >95% coverage

---

## Phase 2: Storage Layer (Week 2)

### 2.1 Storage Interface & File Storage [~6 hours]

**Goal**: Abstract storage with file system implementation (FR-015 to FR-020)

- [ ] **P2.1.1** Create `lib/json_schema_core/storage/base.py` module
  - Define abstract `StorageAdapter` interface
  - Declare abstract methods: `save_document()`, `load_document()`, `delete_document()`, `list_documents()`, `document_exists()`
  - **Acceptance**: Interface class defined with proper signatures

- [ ] **P2.1.2** Create `lib/json_schema_core/storage/file_storage.py` module
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
  - **Acceptance**: `pytest tests/lib/test_file_storage.py` passes

---

### 2.2 ULID Generation [~2 hours]

**Goal**: Implement ULID generator for document IDs (FR-107 to FR-111)

- [ ] **P2.2.1** Create `lib/json_schema_core/utils/ulid_generator.py` module
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
  - **Acceptance**: `pytest tests/lib/test_ulid_generator.py` passes

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
  - **Acceptance**: `pytest tests/lib/test_file_storage.py` updated and passes

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
  - **Acceptance**: `pytest tests/lib/test_errors.py` passes

---

## Phase 3: Schema & Validation (Week 3)

### 3.1 Schema Loading & Resolution [~6 hours]

**Goal**: Load and resolve JSON Schema with $ref support (FR-001 to FR-007, FR-086 to FR-090)

- [ ] **P3.1.1** Create `lib/json_schema_core/services/schema_service.py` module
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
  - **Acceptance**: `pytest tests/lib/test_schema_service.py` passes

---

### 3.2 Validation Service [~5 hours]

**Goal**: Validate documents and nodes against schema (FR-058 to FR-064)

- [ ] **P3.2.1** Create `lib/json_schema_core/services/validation_service.py` module
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
  - **Acceptance**: `pytest tests/lib/test_validation_service.py` passes

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
  - Run: `pytest tests/lib/test_document_service.py -v`
  - All ~12 tests should now PASS (were failing in Phase 0)
  - Fix any remaining failures
  - **Acceptance**: ALL Phase 0 DocumentService tests are GREEN ✅

---

### 4.2 Lock Service [~4 hours]

**Goal**: Implement document-level locking (FR-082 to FR-082e)

- [ ] **P4.2.1** Create `lib/json_schema_core/services/lock_service.py` module
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
  - **Acceptance**: `pytest tests/lib/test_lock_service.py` passes

---

## Phase 5: Interface Layer (Week 5)

**CRITICAL**: Interface layer tasks create THIN ADAPTERS ONLY in `apps/` directories:
- `apps/mcp_server/tools/` - Parse MCP requests, call `lib/json_schema_core/services/`, format MCP responses
- `apps/rest_api/routes/` - Parse HTTP requests, call `lib/json_schema_core/services/`, format HTTP responses
- **NO business logic in these files** - all validation, storage, domain logic is in `lib/json_schema_core/`

### 5.1 MCP Tool Implementations [~8 hours]

**Goal**: Implement all 8 MCP tools as thin wrappers calling core library services (FR-065 to FR-069)

- [ ] **P5.1.1** Create `apps/mcp_server/tools/document_tools.py` module
  - Import MCP SDK and service dependencies from `lib/json_schema_core/`
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

- [ ] **P5.1.8** Create `apps/mcp_server/tools/schema_tools.py` module
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

- [ ] **P5.1.11** Create `apps/mcp_server/tools/tool_registry.py` module
  - Register all 8 tools with MCP server
  - Define tool metadata and handlers
  - **Acceptance**: All tools registered successfully

- [ ] **P5.1.12** Write integration tests for MCP tools
  - Test each tool end-to-end through MCP protocol
  - Test error handling and structured responses
  - Test tool discovery
  - **Acceptance**: `pytest tests/apps/mcp_server/test_mcp_tools.py` passes

---

### 5.2 Server Initialization [~3 hours]

**Goal**: Set up MCP server entry point

- [ ] **P5.2.1** Create `apps/mcp_server/server.py` module
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

- [ ] **P5.2.3** Create `apps/mcp_server/__main__.py` entry point
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

- [ ] **P5.3.1** Create `apps/rest_api/models.py` module
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

- [ ] **P5.3.4** Create `apps/rest_api/routes/documents.py` module
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

- [ ] **P5.3.11** Create `apps/rest_api/routes/schema.py` module
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

- [ ] **P5.3.14** Create `apps/rest_api/middleware.py` module
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
  - **Acceptance**: `pytest tests/apps/rest_api/test_routes.py` passes

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
3. ✅ **Monorepo architecture** - All business logic in `lib/json_schema_core/`, interfaces in `apps/`
4. ✅ **Zero code duplication** - Both MCP and REST call same service methods
5. ✅ Both interfaces use identical service methods from core library
6. ✅ Comprehensive error handling with structured errors
7. ✅ Clear separation of concerns (apps/ → lib/services/ → lib/storage/)

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
