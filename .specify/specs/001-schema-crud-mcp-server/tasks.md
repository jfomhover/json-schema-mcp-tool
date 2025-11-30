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

## Phase 1: DocumentService Implementation [Day 2-3, ~10 hours]

**Goal**: Build DocumentService with ALL dependencies already implemented and tested in Phase 0

**Prerequisite**: Phase 0 complete - we have:
- ✅ Domain models (DocumentId, DocumentMetadata, errors)
- ✅ FileSystemStorage (full CRUD + metadata)
- ✅ JSONPointer utilities
- ✅ ValidationService (validate + apply_defaults)
- ✅ SchemaService (load schema)

**Approach**: True TDD - write ONE test, make it pass, refactor, commit

---

### 1.0 Test Infrastructure Setup [~30 minutes]

**Goal**: Set up test fixtures and helpers before writing DocumentService tests

- [ ] **P1.0.1** Create test fixtures for DocumentService
  - **TEST**: Create `tests/lib/services/test_document_service.py`
    - Setup pytest imports and test class structure
    - Fixture: `test_schema()` - Returns text.json schema dict
    - Fixture: `storage(tmp_path)` - Returns FileSystemStorage instance
    - Fixture: `validation_service(test_schema)` - Returns ValidationService
    - Fixture: `schema_service(tmp_path, test_schema)` - Returns SchemaService
    - Fixture: `document_service(storage, validation_service, schema_service)` - Returns DocumentService instance
  - **Acceptance**: Fixtures defined, can be imported
  - **Commit**: `"test(services): add DocumentService test fixtures"`

- [ ] **P1.0.2** Create sample document fixtures
  - **TEST**: Add to `tests/lib/services/test_document_service.py`
    - Fixture: `valid_minimal_doc()` - Returns `{"title": "Test", "authors": ["Author"], "sections": []}`
    - Fixture: `valid_full_doc()` - Returns complete doc with sections and paragraphs
    - Fixture: `invalid_doc_missing_title()` - Missing required field
    - Fixture: `invalid_doc_wrong_type()` - Wrong type for field
  - **Acceptance**: Sample data fixtures available
  - **Commit**: `"test(services): add sample document fixtures"`

---

### 1.1 DocumentService - create_document (Happy Path) [~1 hour]

- [ ] **P1.1.1** Test: create_document returns doc_id and version
  - **TEST**: Add to `tests/lib/services/test_document_service.py`
    - Test: `test_create_document_returns_doc_id_and_version(document_service, valid_minimal_doc)`
      - Call `create_document("text", valid_minimal_doc)`
      - Assert returns tuple of (str, int)
      - Assert version == 1
  - **Acceptance**: Test written and FAILS
  - **Commit**: `"test(services): add create_document return value test (failing)"`

- [ ] **P1.1.2** Implement: DocumentService class and create_document skeleton
  - **IMPL**: Create `lib/json_schema_core/services/document_service.py`
    - Class: `DocumentService`
    - Method: `__init__(self, storage: StorageInterface, validation_service: ValidationService, schema_service: SchemaService)`
    - Method: `async def create_document(self, schema_name: str, content: dict) -> tuple[str, int]`
      - Minimal implementation: return ("placeholder", 1)
  - **Acceptance**: Test PASSES with placeholder
  - **Commit**: `"feat(services): add DocumentService skeleton with create_document stub"`

- [ ] **P1.1.3** Test: create_document generates valid ULID
  - **TEST**: Add test
    - Test: `test_create_document_generates_valid_ulid(document_service, valid_minimal_doc)`
      - Call create_document
      - Assert doc_id matches ULID format (26 chars, uppercase alphanumeric)
      - Assert doc_id is unique on repeated calls
  - **Acceptance**: Test FAILS (placeholder doesn't generate ULID)
  - **Commit**: `"test(services): add ULID generation test (failing)"`

- [ ] **P1.1.4** Implement: Generate ULID for document ID
  - **IMPL**: Update `create_document()`
    - Generate new DocumentId using `DocumentId.generate()`
    - Return (str(doc_id), 1)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): generate ULID for new documents"`

- [ ] **P1.1.5** Test: create_document applies schema defaults
  - **TEST**: Add test
    - Test: `test_create_document_applies_defaults(document_service)`
      - Call create_document with minimal doc (no sections field)
      - Read document back from storage
      - Assert document has `sections: []` default applied
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add schema defaults test (failing)"`

- [ ] **P1.1.6** Implement: Apply schema defaults before saving
  - **IMPL**: Update `create_document()`
    - Call `validation_service.apply_defaults(content)`
    - Use returned document with defaults
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): apply schema defaults in create_document"`

- [ ] **P1.1.7** Test: create_document saves to storage
  - **TEST**: Add test
    - Test: `test_create_document_saves_to_storage(document_service, valid_minimal_doc, storage)`
      - Call create_document
      - Read document directly from storage using doc_id
      - Assert document content matches (with defaults applied)
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add storage persistence test (failing)"`

- [ ] **P1.1.8** Implement: Write document to storage
  - **IMPL**: Update `create_document()`
    - Call `storage.write_document(doc_id, document_with_defaults)`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): persist document to storage"`

- [ ] **P1.1.9** Test: create_document saves metadata
  - **TEST**: Add test
    - Test: `test_create_document_saves_metadata(document_service, valid_minimal_doc, storage)`
      - Call create_document
      - Read metadata from storage
      - Assert metadata has doc_id, version=1, created_at, updated_at
      - Assert created_at == updated_at for new document
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add metadata persistence test (failing)"`

- [ ] **P1.1.10** Implement: Create and save metadata
  - **IMPL**: Update `create_document()`
    - Create DocumentMetadata with version=1, current timestamps
    - Call `storage.write_metadata(doc_id, metadata.to_dict())`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): persist document metadata"`

---

### 1.2 DocumentService - create_document (Error Handling) [~1 hour]

- [ ] **P1.2.1** Test: create_document validates against schema
  - **TEST**: Add test
    - Test: `test_create_document_validates_schema(document_service, invalid_doc_missing_title)`
      - Call create_document with invalid doc
      - Assert raises ValidationFailedError
      - Assert error contains validation details
  - **Acceptance**: Test FAILS (no validation yet)
  - **Commit**: `"test(services): add validation test (failing)"`

- [ ] **P1.2.2** Implement: Validate document before saving
  - **IMPL**: Update `create_document()`
    - Call `validation_service.validate(document_with_defaults)` before storage
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): validate documents in create_document"`

- [ ] **P1.2.3** Test: create_document handles validation with wrong types
  - **TEST**: Add test
    - Test: `test_create_document_rejects_wrong_types(document_service, invalid_doc_wrong_type)`
      - Call create_document with doc where title is int instead of string
      - Assert raises ValidationFailedError
      - Assert error message mentions type mismatch
  - **Acceptance**: Test PASSES (validation already implemented)
  - **Commit**: `"test(services): add type validation test"`

---

### 1.3 DocumentService - read_node (Happy Path) [~1.5 hours]

- [ ] **P1.3.1** Test: read_node reads root path
  - **TEST**: Add test
    - Test: `test_read_node_root(document_service, valid_full_doc)`
      - Create a document
      - Call read_node(doc_id, "/")
      - Assert returns full document content and version
  - **Acceptance**: Test FAILS (method not implemented)
  - **Commit**: `"test(services): add read_node root test (failing)"`

- [ ] **P1.3.2** Implement: read_node method skeleton
  - **IMPL**: Add to `document_service.py`
    - Method: `async def read_node(self, doc_id: str, node_path: str) -> tuple[Any, int]`
      - Load document from storage
      - Load metadata from storage
      - Return (document, metadata["version"])
  - **Acceptance**: Test PASSES for root path
  - **Commit**: `"feat(services): implement read_node for root path"`

- [ ] **P1.3.3** Test: read_node reads simple field
  - **TEST**: Add test
    - Test: `test_read_node_simple_field(document_service, valid_full_doc)`
      - Create document
      - Call read_node(doc_id, "/title")
      - Assert returns just the title string and version
  - **Acceptance**: Test FAILS (no JSONPointer resolution)
  - **Commit**: `"test(services): add read_node field test (failing)"`

- [ ] **P1.3.4** Implement: Use JSONPointer to resolve path
  - **IMPL**: Update `read_node()`
    - Use `resolve_pointer(document, node_path)` from utils
    - Return (resolved_value, version)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): add JSONPointer resolution in read_node"`

- [ ] **P1.3.5** Test: read_node reads nested paths
  - **TEST**: Add test
    - Test: `test_read_node_nested(document_service, valid_full_doc)`
      - Call read_node(doc_id, "/sections/0/title")
      - Assert returns section title
    - Test: `test_read_node_array_element(document_service, valid_full_doc)`
      - Call read_node(doc_id, "/authors/0")
      - Assert returns first author
  - **Acceptance**: Tests PASS (JSONPointer handles this)
  - **Commit**: `"test(services): add nested path read tests"`

---

### 1.4 DocumentService - read_node (Error Handling) [~30 minutes]

- [ ] **P1.4.1** Test: read_node raises error for missing document
  - **TEST**: Add test
    - Test: `test_read_node_document_not_found(document_service)`
      - Call read_node with non-existent doc_id
      - Assert raises DocumentNotFoundError
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add document not found test (failing)"`

- [ ] **P1.4.2** Implement: Check document exists
  - **IMPL**: Update `read_node()`
    - Wrap storage.read_document() in try/except
    - Raise DocumentNotFoundError if file not found
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): handle missing documents in read_node"`

- [ ] **P1.4.3** Test: read_node raises error for invalid path
  - **TEST**: Add test
    - Test: `test_read_node_path_not_found(document_service, valid_minimal_doc)`
      - Create document
      - Call read_node(doc_id, "/nonexistent")
      - Assert raises PathNotFoundError
  - **Acceptance**: Test PASSES (JSONPointer already raises this)
  - **Commit**: `"test(services): add invalid path test"`

---

### 1.5 DocumentService - update_node (Happy Path) [~1.5 hours]

- [ ] **P1.5.1** Test: update_node updates simple field
  - **TEST**: Add test
    - Test: `test_update_node_simple_field(document_service, valid_minimal_doc)`
      - Create document (version 1)
      - Call update_node(doc_id, "/title", "New Title", expected_version=1)
      - Assert returns ("New Title", 2)
      - Assert reading /title returns "New Title"
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add update_node test (failing)"`

- [ ] **P1.5.2** Implement: update_node skeleton
  - **IMPL**: Add to `document_service.py`
    - Method: `async def update_node(self, doc_id: str, node_path: str, value: Any, expected_version: int) -> tuple[Any, int]`
      - Load document and metadata
      - Use `set_pointer(document, node_path, value)` from utils
      - Increment version
      - Write document and metadata
      - Return (value, new_version)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): implement update_node basic functionality"`

- [ ] **P1.5.3** Test: update_node increments version
  - **TEST**: Add test
    - Test: `test_update_node_increments_version(document_service, valid_minimal_doc)`
      - Create document (version 1)
      - Update a field
      - Assert metadata.version == 2
      - Update again
      - Assert metadata.version == 3
  - **Acceptance**: Test PASSES (already implemented)
  - **Commit**: `"test(services): verify version increment on update"`

- [ ] **P1.5.4** Test: update_node updates timestamp
  - **TEST**: Add test
    - Test: `test_update_node_updates_timestamp(document_service, valid_minimal_doc)`
      - Create document, note created_at
      - Sleep 0.1 seconds
      - Update field
      - Assert updated_at > created_at
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add timestamp update test (failing)"`

- [ ] **P1.5.5** Implement: Update updated_at timestamp
  - **IMPL**: Update `update_node()`
    - Call `metadata.increment_version()` which updates timestamp
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): update timestamp on node updates"`

- [ ] **P1.5.6** Test: update_node validates result
  - **TEST**: Add test
    - Test: `test_update_node_validates(document_service, valid_minimal_doc)`
      - Create document
      - Try to update /title with integer value
      - Assert raises ValidationFailedError
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add update validation test (failing)"`

- [ ] **P1.5.7** Implement: Validate after update
  - **IMPL**: Update `update_node()`
    - Call `validation_service.validate(updated_document)` before saving
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): validate document after update"`

---

### 1.6 DocumentService - update_node (Optimistic Locking) [~1 hour]

- [ ] **P1.6.1** Test: update_node checks version
  - **TEST**: Add test
    - Test: `test_update_node_version_conflict(document_service, valid_minimal_doc)`
      - Create document (version 1)
      - Update successfully with expected_version=1 (now version 2)
      - Try to update again with expected_version=1
      - Assert raises VersionConflictError
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add version conflict test (failing)"`

- [ ] **P1.6.2** Implement: Version checking
  - **IMPL**: Update `update_node()`
    - Check `metadata["version"] == expected_version`
    - Raise VersionConflictError if mismatch
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): implement optimistic locking in update_node"`

- [ ] **P1.6.3** Test: update_node doesn't save on version conflict
  - **TEST**: Add test
    - Test: `test_update_node_no_save_on_conflict(document_service, valid_minimal_doc, storage)`
      - Create document (version 1)
      - Update to version 2
      - Try update with expected_version=1 (should fail)
      - Read document from storage
      - Assert version is still 2, content unchanged
  - **Acceptance**: Test PASSES (exception prevents save)
  - **Commit**: `"test(services): verify no save on version conflict"`

---

### 1.7 DocumentService - create_node [~1.5 hours]

- [ ] **P1.7.1** Test: create_node appends to array
  - **TEST**: Add test
    - Test: `test_create_node_append_to_array(document_service, valid_minimal_doc)`
      - Create document with empty sections
      - Call create_node(doc_id, "/sections", section_data, expected_version=1)
      - Assert returns (created_path, 2) where created_path = "/sections/0"
      - Assert sections array has 1 element
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add create_node test (failing)"`

- [ ] **P1.7.2** Implement: create_node method
  - **IMPL**: Add to `document_service.py`
    - Method: `async def create_node(self, doc_id: str, node_path: str, value: Any, expected_version: int) -> tuple[str, int]`
      - Load document and metadata
      - Check version
      - Resolve parent path
      - If parent is array: append value
      - If parent is object: add new key (derive from value or counter)
      - Validate updated document
      - Increment version
      - Write document and metadata
      - Return (created_path, new_version)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): implement create_node for arrays"`

- [ ] **P1.7.3** Test: create_node validates new node
  - **TEST**: Add test
    - Test: `test_create_node_validates(document_service, valid_minimal_doc)`
      - Try to create node with invalid data
      - Assert raises ValidationFailedError
  - **Acceptance**: Test PASSES (validation already implemented)
  - **Commit**: `"test(services): verify validation in create_node"`

- [ ] **P1.7.4** Test: create_node checks version
  - **TEST**: Add test
    - Test: `test_create_node_version_conflict(document_service, valid_minimal_doc)`
      - Create document, update it (version 2)
      - Try create_node with expected_version=1
      - Assert raises VersionConflictError
  - **Acceptance**: Test PASSES (version check already implemented)
  - **Commit**: `"test(services): verify version check in create_node"`

---

### 1.8 DocumentService - delete_node [~1.5 hours]

- [ ] **P1.8.1** Test: delete_node removes from array
  - **TEST**: Add test
    - Test: `test_delete_node_from_array(document_service, valid_full_doc)`
      - Create document with 2 sections
      - Call delete_node(doc_id, "/sections/1", expected_version=1)
      - Assert returns (deleted_section, 2)
      - Assert sections array has 1 element
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add delete_node test (failing)"`

- [ ] **P1.8.2** Implement: delete_node method
  - **IMPL**: Add to `document_service.py`
    - Method: `async def delete_node(self, doc_id: str, node_path: str, expected_version: int) -> tuple[Any, int]`
      - Load document and metadata
      - Check version
      - Resolve value at path (to return)
      - Use `delete_pointer(document, node_path)` from utils
      - Validate updated document
      - Increment version
      - Write document and metadata
      - Return (deleted_value, new_version)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): implement delete_node"`

- [ ] **P1.8.3** Test: delete_node validates result
  - **TEST**: Add test
    - Test: `test_delete_node_validates_result(document_service, valid_minimal_doc)`
      - Try to delete required field (e.g., /title)
      - Assert raises ValidationFailedError
  - **Acceptance**: Test PASSES (validation already implemented)
  - **Commit**: `"test(services): verify validation in delete_node"`

- [ ] **P1.8.4** Test: delete_node handles missing path
  - **TEST**: Add test
    - Test: `test_delete_node_path_not_found(document_service, valid_minimal_doc)`
      - Try to delete non-existent path
      - Assert raises PathNotFoundError
  - **Acceptance**: Test PASSES (JSONPointer raises this)
  - **Commit**: `"test(services): verify error on delete missing path"`

---

### 1.9 DocumentService - list_documents [~1 hour]

- [ ] **P1.9.1** Test: list_documents returns empty list
  - **TEST**: Add test
    - Test: `test_list_documents_empty(document_service)`
      - Call list_documents()
      - Assert returns []
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(services): add list_documents test (failing)"`

- [ ] **P1.9.2** Implement: list_documents method
  - **IMPL**: Add to `document_service.py`
    - Method: `async def list_documents(self, limit: int = 100, offset: int = 0) -> list[dict]`
      - Call `storage.list_documents(limit, offset)`
      - For each doc_id: load metadata
      - Convert metadata to dict
      - Return list of metadata dicts
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(services): implement list_documents"`

- [ ] **P1.9.3** Test: list_documents returns metadata
  - **TEST**: Add test
    - Test: `test_list_documents_returns_metadata(document_service, valid_minimal_doc)`
      - Create 3 documents
      - Call list_documents()
      - Assert returns list of 3 dicts
      - Assert each has doc_id, version, created_at, updated_at
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(services): verify list_documents metadata"`

- [ ] **P1.9.4** Test: list_documents pagination
  - **TEST**: Add test
    - Test: `test_list_documents_pagination(document_service, valid_minimal_doc)`
      - Create 5 documents
      - Call list_documents(limit=2, offset=0) - returns first 2
      - Call list_documents(limit=2, offset=2) - returns next 2
      - Call list_documents(limit=2, offset=4) - returns last 1
  - **Acceptance**: Test PASSES (storage handles pagination)
  - **Commit**: `"test(services): verify list_documents pagination"`

---

### 1.10 DocumentService - Integration Tests [~30 minutes]

- [ ] **P1.10.1** Integration test: Full document lifecycle
  - **TEST**: Add test
    - Test: `test_full_document_lifecycle(document_service, valid_full_doc)`
      - Create document
      - Read root and verify content
      - Update a field
      - Read updated field
      - Create a new section
      - Delete a section
      - List documents
      - Verify final state
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(services): add full lifecycle integration test"`

- [ ] **P1.10.2** Integration test: Concurrent updates
  - **TEST**: Add test
    - Test: `test_concurrent_updates_version_conflict(document_service, valid_minimal_doc)`
      - Create document (version 1)
      - Simulate two concurrent updates both reading version 1
      - First update succeeds (version 2)
      - Second update fails with VersionConflictError
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(services): verify optimistic locking prevents conflicts"`

**🎯 Phase 1 Complete When:**
- ✅ DocumentService fully implemented with ALL CRUD methods
- ✅ All unit tests passing (40+ tests)
- ✅ Integration tests passing
- ✅ 100% test coverage on DocumentService
- ✅ Can run `pytest tests/lib/services/test_document_service.py -v` - ALL GREEN
- ✅ Each method tested for: happy path, error handling, edge cases
- ✅ Optimistic locking verified
- ✅ Ready to build interface layers (MCP + REST) in Phase 2

---

## Phase 2: Configuration Management & Development Tools [Day 3-4, ~8 hours]

**Goal**: Complete configuration system and add code quality tools

**Prerequisites**: Phase 1 complete - DocumentService fully implemented

---

### 2.0 Add Interface Dependencies [~15 minutes]

- [ ] **P2.0.1** Add MCP and REST API dependencies
  - **IMPL**: Update `pyproject.toml`
    - Add `mcp = "^1.0.0"` (Model Context Protocol SDK)
    - Add `fastapi = "^0.104.0"` (REST API framework)
    - Add `uvicorn[standard] = "^0.24.0"` (ASGI server)
  - **Acceptance**: Dependencies listed
  - **Commit**: `"chore: add MCP and REST API dependencies"`

---

### 2.1 Configuration Management - Core [~3 hours]

**Goal**: Build configuration system with TDD

- [ ] **P2.1.1** Test: ServerConfig with default values
  - **TEST**: Create `tests/lib/test_config.py`
    - Test: `test_config_defaults()`
      - Create `ServerConfig()` without args
      - Assert schema_path == Path("./schemas")
      - Assert storage_dir == Path("./storage")
      - Assert lock_timeout == 30
      - Assert server_name == "json-schema-server"
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add ServerConfig defaults test (failing)"`

- [ ] **P2.1.2** Implement: ServerConfig class
  - **IMPL**: Create `lib/json_schema_core/config.py`
    - Import: `from pydantic_settings import BaseSettings`
    - Class: `ServerConfig(BaseSettings)`
    - Fields: `schema_path: Path`, `storage_dir: Path`, `lock_timeout: int`, `server_name: str`
    - Set defaults in field definitions
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): add ServerConfig with default values"`

- [ ] **P2.1.3** Test: ServerConfig validates field types
  - **TEST**: Add test
    - Test: `test_config_validates_types()`
      - Try to create ServerConfig with lock_timeout="not_an_int"
      - Assert raises ValidationError
    - Test: `test_config_validates_paths()`
      - Try to create with schema_path=123
      - Assert raises ValidationError
  - **Acceptance**: Test PASSES (Pydantic handles this)
  - **Commit**: `"test(config): verify type validation"`

- [ ] **P2.1.4** Test: ServerConfig from dict
  - **TEST**: Add test
    - Test: `test_config_from_dict()`
      - Create dict with config values
      - Create ServerConfig(**config_dict)
      - Assert all fields match dict values
  - **Acceptance**: Test PASSES (Pydantic handles this)
  - **Commit**: `"test(config): verify dict initialization"`

---

### 2.2 Configuration Management - File Loading [~1.5 hours]

- [ ] **P2.2.1** Test: Load config from JSON file
  - **TEST**: Add test
    - Test: `test_load_from_json_file(tmp_path)`
      - Create temp JSON file with config
      - Call ServerConfig.from_file(json_path)
      - Assert config loaded correctly
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add JSON file loading test (failing)"`

- [ ] **P2.2.2** Implement: from_file class method
  - **IMPL**: Update `config.py`
    - Method: `@classmethod def from_file(cls, path: Path) -> "ServerConfig"`
      - Read JSON file
      - Parse JSON
      - Return cls(**json_data)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): implement JSON file loading"`

- [ ] **P2.2.3** Test: Handle missing config file gracefully
  - **TEST**: Add test
    - Test: `test_load_from_missing_file_uses_defaults(tmp_path)`
      - Call from_file with non-existent path
      - Assert returns config with defaults (doesn't crash)
    - Test: `test_load_from_missing_file_logs_warning(tmp_path, caplog)`
      - Verify warning logged
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add missing file handling test (failing)"`

- [ ] **P2.2.4** Implement: Handle missing file
  - **IMPL**: Update `from_file()`
    - Wrap in try/except FileNotFoundError
    - Log warning if file missing
    - Return cls() with defaults
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): handle missing config file gracefully"`

- [ ] **P2.2.5** Test: Handle invalid JSON
  - **TEST**: Add test
    - Test: `test_load_from_invalid_json_raises_error(tmp_path)`
      - Create file with invalid JSON
      - Assert raises ConfigurationError (custom exception)
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add invalid JSON test (failing)"`

- [ ] **P2.2.6** Implement: Handle invalid JSON
  - **IMPL**: Update `from_file()`
    - Create custom ConfigurationError in errors.py
    - Catch json.JSONDecodeError
    - Raise ConfigurationError with helpful message
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): handle invalid JSON with clear error"`

---

### 2.3 Configuration Management - Environment Variables [~1.5 hours]

- [ ] **P2.3.1** Test: Environment variables override defaults
  - **TEST**: Add test
    - Test: `test_env_var_overrides_default(monkeypatch)`
      - Set env var JSON_SCHEMA_STORAGE_DIR="/custom/path"
      - Create ServerConfig()
      - Assert storage_dir == Path("/custom/path")
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add env var override test (failing)"`

- [ ] **P2.3.2** Implement: Environment variable support
  - **IMPL**: Update `ServerConfig`
    - Add `model_config = {"env_prefix": "JSON_SCHEMA_"}`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): add environment variable support"`

- [ ] **P2.3.3** Test: Env vars override file values
  - **TEST**: Add test
    - Test: `test_env_var_overrides_file(tmp_path, monkeypatch)`
      - Create config file with storage_dir="/file/path"
      - Set env var JSON_SCHEMA_STORAGE_DIR="/env/path"
      - Load from file
      - Assert storage_dir == Path("/env/path")
  - **Acceptance**: Test PASSES (Pydantic precedence)
  - **Commit**: `"test(config): verify env var precedence over file"`

- [ ] **P2.3.4** Test: All config fields support env vars
  - **TEST**: Add test
    - Test: `test_all_fields_have_env_vars(monkeypatch)`
      - Set all env vars (JSON_SCHEMA_SCHEMA_PATH, etc.)
      - Create ServerConfig()
      - Assert all fields match env values
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(config): verify all fields support env vars"`

---

### 2.4 Configuration Management - Validation [~1 hour]

- [ ] **P2.4.1** Test: Validate schema_path exists
  - **TEST**: Add test
    - Test: `test_validate_schema_path_exists(tmp_path)`
      - Create config with non-existent schema_path
      - Call validate() method
      - Assert raises ConfigurationError
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add schema_path validation test (failing)"`

- [ ] **P2.4.2** Implement: Validate schema_path
  - **IMPL**: Add to `ServerConfig`
    - Method: `def validate(self) -> None`
      - Check schema_path.exists()
      - Raise ConfigurationError if not
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): validate schema_path exists"`

- [ ] **P2.4.3** Test: Create storage_dir if missing
  - **TEST**: Add test
    - Test: `test_validate_creates_storage_dir(tmp_path)`
      - Create config with non-existent storage_dir
      - Call validate()
      - Assert storage_dir created
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add storage_dir creation test (failing)"`

- [ ] **P2.4.4** Implement: Create storage_dir
  - **IMPL**: Update `validate()`
    - Create storage_dir if it doesn't exist
    - Use storage_dir.mkdir(parents=True, exist_ok=True)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): auto-create storage_dir if missing"`

- [ ] **P2.4.5** Test: Validate lock_timeout is positive
  - **TEST**: Add test
    - Test: `test_validate_lock_timeout_positive()`
      - Create config with lock_timeout=0
      - Assert raises ConfigurationError
      - Create config with lock_timeout=-5
      - Assert raises ConfigurationError
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(config): add lock_timeout validation test (failing)"`

- [ ] **P2.4.6** Implement: Validate lock_timeout
  - **IMPL**: Update `validate()`
    - Check lock_timeout > 0
    - Raise ConfigurationError if not
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(config): validate lock_timeout is positive"`

---

### 2.5 Configuration Management - Documentation [~30 minutes]

- [ ] **P2.5.1** Create config.example.json template
  - **IMPL**: Create `config.example.json` in repo root
    - Include all fields with example values
    - Add inline documentation (as values or separate README)
  - **Acceptance**: File exists and is valid JSON
  - **Commit**: `"docs: add config.example.json template"`

- [ ] **P2.5.2** Test: Example config is valid
  - **TEST**: Add test
    - Test: `test_example_config_is_valid()`
      - Load config.example.json
      - Create ServerConfig from it
      - Assert no errors
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(config): verify example config is valid"`

---

### 2.6 Development Tools - Linting & Formatting [~1 hour]

- [ ] **P2.6.1** Configure Ruff linter and formatter
  - **IMPL**: Update `pyproject.toml`
    - Add `ruff` to dev dependencies
    - Add `[tool.ruff]` section
    - Set line-length = 100
    - Enable rules: F (pyflakes), E/W (pycodestyle), I (isort), N (pep8-naming)
    - Add `[tool.ruff.format]` section
  - **Acceptance**: Can run `ruff check lib/ tests/`
  - **Commit**: `"chore: configure Ruff linter and formatter"`

- [ ] **P2.6.2** Run Ruff and fix issues
  - **IMPL**: Run `ruff check --fix lib/ tests/`
    - Fix any issues found
    - Run `ruff format lib/ tests/`
  - **Acceptance**: `ruff check lib/ tests/` returns clean
  - **Commit**: `"style: apply Ruff formatting to codebase"`

---

### 2.7 Development Tools - Type Checking [~30 minutes]

- [ ] **P2.7.1** Configure MyPy type checker
  - **IMPL**: Update `pyproject.toml`
    - Add `mypy` to dev dependencies
    - Add `[tool.mypy]` section
    - Set python_version = "3.11"
    - Enable strict mode
    - Set warn_return_any = true
  - **Acceptance**: Can run `mypy lib/`
  - **Commit**: `"chore: configure MyPy type checker"`

- [ ] **P2.7.2** Fix type issues
  - **IMPL**: Run `mypy lib/` and fix issues
    - Add missing type hints
    - Fix type mismatches
  - **Acceptance**: `mypy lib/` returns clean
  - **Commit**: `"style: fix type hints for MyPy compliance"`

---

### 2.8 Development Tools - Pre-commit Hooks [~30 minutes]

- [ ] **P2.8.1** Configure pre-commit hooks
  - **IMPL**: 
    - Add `pre-commit` to dev dependencies
    - Create `.pre-commit-config.yaml`
    - Add hooks: ruff (check + format), mypy, pytest-check
  - **Acceptance**: File created
  - **Commit**: `"chore: configure pre-commit hooks"`

- [ ] **P2.8.2** Install and test pre-commit
  - **IMPL**: Run `pre-commit install`
    - Run `pre-commit run --all-files`
    - Fix any issues
  - **Acceptance**: All hooks pass
  - **Commit**: `"chore: install pre-commit hooks"`

**🎯 Phase 2 Complete When:**
- ✅ ServerConfig fully implemented with tests (15+ tests)
- ✅ Configuration supports: defaults, files, env vars
- ✅ Configuration validation implemented
- ✅ Ruff, MyPy, pre-commit configured
- ✅ All tests passing
- ✅ Code quality tools enforcing standards
- ✅ Ready to build REST API interface

---

## Phase 3: REST API Interface Layer [Day 5-7, ~12 hours]

**Goal**: Build REST API as thin adapter calling DocumentService

**Prerequisites**: 
- Phase 1: DocumentService fully implemented
- Phase 2: ServerConfig available

**Architecture**: FastAPI application with thin routes that delegate to DocumentService

---

### 3.0 REST API Project Setup [~30 minutes]

- [ ] **P3.0.1** Create REST API directory structure
  - **IMPL**:
    - Create `apps/rest_api/` with `__init__.py`
    - Create `apps/rest_api/routes/` with `__init__.py`
    - Create `tests/apps/rest_api/` with `__init__.py`
  - **Acceptance**: Directory structure exists
  - **Commit**: `"chore: create REST API directory structure"`

- [ ] **P3.0.2** Create test fixtures for REST API
  - **TEST**: Create `tests/apps/rest_api/conftest.py`
    - Fixture: `config()` - Returns ServerConfig for tests
    - Fixture: `document_service(config)` - Returns initialized DocumentService
    - Fixture: `app(document_service)` - Returns FastAPI app instance
    - Fixture: `client(app)` - Returns TestClient
  - **Acceptance**: Fixtures defined
  - **Commit**: `"test(rest): add REST API test fixtures"`

---

### 3.1 FastAPI Application Setup [~1.5 hours]

- [ ] **P3.1.1** Test: Create FastAPI application
  - **TEST**: Create `tests/apps/rest_api/test_app.py`
    - Test: `test_app_creation()`
      - Create app instance
      - Assert isinstance(app, FastAPI)
      - Assert app.title == "JSON Schema CRUD API"
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add app creation test (failing)"`

- [ ] **P3.1.2** Implement: FastAPI application
  - **IMPL**: Create `apps/rest_api/app.py`
    - Create FastAPI instance
    - Set title, description, version
    - Function: `create_app(config: ServerConfig) -> FastAPI`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): create FastAPI application"`

- [ ] **P3.1.3** Test: App has dependency injection for services
  - **TEST**: Add test
    - Test: `test_app_has_service_dependency(app)`
      - Check app state has document_service
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add service dependency test (failing)"`

- [ ] **P3.1.4** Implement: Service dependency injection
  - **IMPL**: Update `app.py`
    - Initialize FileSystemStorage, ValidationService, SchemaService
    - Initialize DocumentService
    - Store in app.state
    - Create dependency function: `get_document_service()`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add service dependency injection"`

- [ ] **P3.1.5** Test: App has CORS middleware
  - **TEST**: Add test
    - Test: `test_app_has_cors_middleware(client)`
      - Make OPTIONS request
      - Check CORS headers present
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add CORS middleware test (failing)"`

- [ ] **P3.1.6** Implement: CORS middleware
  - **IMPL**: Update `app.py`
    - Add CORSMiddleware
    - Allow origins: ["*"] (configurable)
    - Allow methods: ["*"]
    - Allow headers: ["*"]
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add CORS middleware"`

---

### 3.2 Pydantic Models for API [~1 hour]

- [ ] **P3.2.1** Test: Request/response models defined
  - **TEST**: Create `tests/apps/rest_api/test_models.py`
    - Test: `test_create_document_request_model()`
      - Create CreateDocumentRequest with schema_name and content
      - Validate required fields
    - Test: `test_create_document_response_model()`
      - Create CreateDocumentResponse with doc_id and version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add API models test (failing)"`

- [ ] **P3.2.2** Implement: Request/response models
  - **IMPL**: Create `apps/rest_api/models.py`
    - Class: `CreateDocumentRequest(BaseModel)` - schema_name, content
    - Class: `CreateDocumentResponse(BaseModel)` - doc_id, version
    - Class: `ReadNodeResponse(BaseModel)` - content, version
    - Class: `UpdateNodeRequest(BaseModel)` - value, expected_version
    - Class: `UpdateNodeResponse(BaseModel)` - content, version
    - Class: `DocumentMetadataResponse(BaseModel)` - doc_id, version, created_at, updated_at
    - Class: `ErrorResponse(BaseModel)` - error, message, details
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add Pydantic request/response models"`

---

### 3.3 Health Check Endpoint [~30 minutes]

- [ ] **P3.3.1** Test: Health check endpoint
  - **TEST**: Create `tests/apps/rest_api/test_health.py`
    - Test: `test_health_check_returns_200(client)`
      - GET /health
      - Assert status_code == 200
      - Assert response.json() == {"status": "healthy"}
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add health check test (failing)"`

- [ ] **P3.3.2** Implement: Health check route
  - **IMPL**: Create `apps/rest_api/routes/health.py`
    - Router: `router = APIRouter()`
    - Endpoint: `@router.get("/health")`
    - Return: `{"status": "healthy"}`
  - **IMPL**: Update `app.py`
    - Import and include health router
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add health check endpoint"`

---

### 3.4 Document CRUD Endpoints - CREATE [~2 hours]

- [ ] **P3.4.1** Test: POST /documents creates document
  - **TEST**: Create `tests/apps/rest_api/test_documents.py`
    - Test: `test_create_document_success(client)`
      - POST /documents with valid data
      - Assert status_code == 201
      - Assert response has doc_id and version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add create document test (failing)"`

- [ ] **P3.4.2** Implement: POST /documents endpoint
  - **IMPL**: Create `apps/rest_api/routes/documents.py`
    - Router: `router = APIRouter(prefix="/documents", tags=["documents"])`
    - Endpoint: `@router.post("/", status_code=201, response_model=CreateDocumentResponse)`
    - Call: `document_service.create_document()`
    - Return: CreateDocumentResponse
  - **IMPL**: Update `app.py` to include documents router
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add POST /documents endpoint"`

- [ ] **P3.4.3** Test: POST /documents validation error returns 400
  - **TEST**: Add test
    - Test: `test_create_document_validation_error(client)`
      - POST /documents with invalid data
      - Assert status_code == 400
      - Assert response has error details
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add validation error test (failing)"`

- [ ] **P3.4.4** Implement: Exception handler for validation errors
  - **IMPL**: Create `apps/rest_api/middleware.py`
    - Exception handler: `@app.exception_handler(ValidationFailedError)`
    - Return HTTPException(400, detail=...)
  - **IMPL**: Update `app.py` to register exception handler
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add validation error exception handler"`

---

### 3.5 Document CRUD Endpoints - READ [~1.5 hours]

- [ ] **P3.5.1** Test: GET /documents/{doc_id}/nodes reads root
  - **TEST**: Add test
    - Test: `test_read_document_root(client, document_service)`
      - Create document via service
      - GET /documents/{doc_id}/nodes?path=/
      - Assert status_code == 200
      - Assert response has content and version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add read document test (failing)"`

- [ ] **P3.5.2** Implement: GET /documents/{doc_id}/nodes endpoint
  - **IMPL**: Update `routes/documents.py`
    - Endpoint: `@router.get("/{doc_id}/nodes", response_model=ReadNodeResponse)`
    - Query param: `path: str = Query(default="/")`
    - Call: `document_service.read_node(doc_id, path)`
    - Return: ReadNodeResponse
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add GET /documents/{doc_id}/nodes endpoint"`

- [ ] **P3.5.3** Test: GET with nested path
  - **TEST**: Add test
    - Test: `test_read_nested_node(client, document_service)`
      - Create document
      - GET /documents/{doc_id}/nodes?path=/title
      - Assert returns just title value
  - **Acceptance**: Test PASSES (already implemented)
  - **Commit**: `"test(rest): verify nested path reading"`

- [ ] **P3.5.4** Test: GET document not found returns 404
  - **TEST**: Add test
    - Test: `test_read_document_not_found(client)`
      - GET /documents/nonexistent/nodes
      - Assert status_code == 404
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add document not found test (failing)"`

- [ ] **P3.5.5** Implement: Exception handler for DocumentNotFoundError
  - **IMPL**: Update `middleware.py`
    - Exception handler: `@app.exception_handler(DocumentNotFoundError)`
    - Return HTTPException(404, detail=...)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add not found exception handler"`

---

### 3.6 Document CRUD Endpoints - UPDATE [~2 hours]

- [ ] **P3.6.1** Test: PUT /documents/{doc_id}/nodes updates node
  - **TEST**: Add test
    - Test: `test_update_node_success(client, document_service)`
      - Create document (version 1)
      - PUT /documents/{doc_id}/nodes?path=/title with body
      - Assert status_code == 200
      - Assert version == 2
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add update node test (failing)"`

- [ ] **P3.6.2** Implement: PUT /documents/{doc_id}/nodes endpoint
  - **IMPL**: Update `routes/documents.py`
    - Endpoint: `@router.put("/{doc_id}/nodes", response_model=UpdateNodeResponse)`
    - Query param: `path: str`
    - Body: `request: UpdateNodeRequest`
    - Call: `document_service.update_node(doc_id, path, request.value, request.expected_version)`
    - Return: UpdateNodeResponse
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add PUT /documents/{doc_id}/nodes endpoint"`

- [ ] **P3.6.3** Test: PUT with version conflict returns 409
  - **TEST**: Add test
    - Test: `test_update_node_version_conflict(client, document_service)`
      - Create and update document (version 2)
      - PUT with expected_version=1
      - Assert status_code == 409
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add version conflict test (failing)"`

- [ ] **P3.6.4** Implement: Exception handler for VersionConflictError
  - **IMPL**: Update `middleware.py`
    - Exception handler: `@app.exception_handler(VersionConflictError)`
    - Return HTTPException(409, detail=...)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add version conflict exception handler"`

- [ ] **P3.6.5** Test: PUT with invalid path returns 404
  - **TEST**: Add test
    - Test: `test_update_node_path_not_found(client, document_service)`
      - PUT /documents/{doc_id}/nodes?path=/nonexistent
      - Assert status_code == 404
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add path not found test (failing)"`

- [ ] **P3.6.6** Implement: Exception handler for PathNotFoundError
  - **IMPL**: Update `middleware.py`
    - Exception handler: `@app.exception_handler(PathNotFoundError)`
    - Return HTTPException(404, detail=...)
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add path not found exception handler"`

---

### 3.7 Document CRUD Endpoints - CREATE NODE [~1.5 hours]

- [ ] **P3.7.1** Test: POST /documents/{doc_id}/nodes creates node
  - **TEST**: Add test
    - Test: `test_create_node_success(client, document_service)`
      - Create document
      - POST /documents/{doc_id}/nodes?path=/sections with body
      - Assert status_code == 201
      - Assert returns created_path and version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add create node test (failing)"`

- [ ] **P3.7.2** Implement: POST /documents/{doc_id}/nodes endpoint
  - **IMPL**: Update `routes/documents.py`
    - Endpoint: `@router.post("/{doc_id}/nodes", status_code=201)`
    - Query param: `path: str`
    - Body: `request: UpdateNodeRequest` (reuse model)
    - Call: `document_service.create_node()`
    - Return: `{"created_path": str, "version": int}`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add POST /documents/{doc_id}/nodes endpoint"`

- [ ] **P3.7.3** Test: POST validates new node
  - **TEST**: Add test
    - Test: `test_create_node_validation_error(client, document_service)`
      - POST with invalid node data
      - Assert status_code == 400
  - **Acceptance**: Test PASSES (exception handler already exists)
  - **Commit**: `"test(rest): verify create node validation"`

---

### 3.8 Document CRUD Endpoints - DELETE [~1 hour]

- [ ] **P3.8.1** Test: DELETE /documents/{doc_id}/nodes deletes node
  - **TEST**: Add test
    - Test: `test_delete_node_success(client, document_service)`
      - Create document with sections
      - DELETE /documents/{doc_id}/nodes?path=/sections/0&expected_version=1
      - Assert status_code == 200
      - Assert returns deleted content and version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add delete node test (failing)"`

- [ ] **P3.8.2** Implement: DELETE /documents/{doc_id}/nodes endpoint
  - **IMPL**: Update `routes/documents.py`
    - Endpoint: `@router.delete("/{doc_id}/nodes")`
    - Query params: `path: str`, `expected_version: int`
    - Call: `document_service.delete_node()`
    - Return: `{"content": Any, "version": int}`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add DELETE /documents/{doc_id}/nodes endpoint"`

- [ ] **P3.8.3** Test: DELETE validates result
  - **TEST**: Add test
    - Test: `test_delete_node_validation_error(client, document_service)`
      - Try to delete required field
      - Assert status_code == 400
  - **Acceptance**: Test PASSES (exception handler exists)
  - **Commit**: `"test(rest): verify delete node validation"`

---

### 3.9 Document List Endpoint [~1 hour]

- [ ] **P3.9.1** Test: GET /documents lists documents
  - **TEST**: Add test
    - Test: `test_list_documents_empty(client)`
      - GET /documents
      - Assert status_code == 200
      - Assert returns []
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(rest): add list documents test (failing)"`

- [ ] **P3.9.2** Implement: GET /documents endpoint
  - **IMPL**: Update `routes/documents.py`
    - Endpoint: `@router.get("/", response_model=list[DocumentMetadataResponse])`
    - Query params: `limit: int = 100`, `offset: int = 0`
    - Call: `document_service.list_documents(limit, offset)`
    - Return: list of DocumentMetadataResponse
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(rest): add GET /documents endpoint"`

- [ ] **P3.9.3** Test: GET /documents returns metadata
  - **TEST**: Add test
    - Test: `test_list_documents_returns_metadata(client, document_service)`
      - Create 3 documents
      - GET /documents
      - Assert returns 3 items with metadata
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(rest): verify list documents metadata"`

- [ ] **P3.9.4** Test: GET /documents pagination
  - **TEST**: Add test
    - Test: `test_list_documents_pagination(client, document_service)`
      - Create 5 documents
      - GET /documents?limit=2&offset=0
      - Assert returns 2 items
      - GET /documents?limit=2&offset=2
      - Assert returns next 2 items
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(rest): verify list documents pagination"`

---

### 3.10 REST API Entry Point [~1 hour]

- [ ] **P3.10.1** Create __main__.py for REST API
  - **IMPL**: Create `apps/rest_api/__main__.py`
    - Load configuration
    - Create app
    - Run with uvicorn
  - **Acceptance**: Can run `python -m apps.rest_api`
  - **Commit**: `"feat(rest): add server entry point"`

- [ ] **P3.10.2** Test: Can start server programmatically
  - **TEST**: Create `tests/apps/rest_api/test_server.py`
    - Test: `test_server_starts()`
      - Import and create app
      - Assert app is FastAPI instance
      - Assert has all routes registered
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(rest): verify server startup"`

---

### 3.11 REST API Integration Tests [~1 hour]

- [ ] **P3.11.1** Integration test: Full document lifecycle via REST
  - **TEST**: Create `tests/apps/rest_api/test_integration.py`
    - Test: `test_full_document_lifecycle_rest(client)`
      - POST /documents - create
      - GET /documents/{doc_id}/nodes - read
      - PUT /documents/{doc_id}/nodes - update
      - POST /documents/{doc_id}/nodes - create node
      - DELETE /documents/{doc_id}/nodes - delete node
      - GET /documents - list
      - Verify final state
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(rest): add full lifecycle integration test"`

- [ ] **P3.11.2** Integration test: Error handling
  - **TEST**: Add test
    - Test: `test_error_handling_integration(client)`
      - Test 404 for missing document
      - Test 400 for validation error
      - Test 409 for version conflict
      - Test 404 for invalid path
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(rest): add error handling integration test"`

**🎯 Phase 3 Complete When:**
- ✅ REST API fully functional
- ✅ All CRUD endpoints implemented (CREATE, READ, UPDATE, DELETE, LIST)
- ✅ All exception handlers implemented
- ✅ All tests passing (30+ tests)
- ✅ Integration tests passing
- ✅ Can run REST API: `python -m apps.rest_api`
- ✅ API documented with OpenAPI/Swagger
- ✅ Ready to build MCP interface

---

## Phase 4: MCP Interface Layer [Day 8-10, ~10 hours]

**Goal**: Build MCP server as thin adapter calling DocumentService (parallel to REST API)

**Prerequisites**: 
- Phase 1: DocumentService fully implemented
- Phase 2: ServerConfig available

**Architecture**: MCP tools that delegate to DocumentService (zero duplication with REST API)

---

### 4.0 MCP Server Project Setup [~30 minutes]

- [ ] **P4.0.1** Create MCP server directory structure
  - **IMPL**:
    - Create `apps/mcp_server/` with `__init__.py`
    - Create `apps/mcp_server/tools/` with `__init__.py`
    - Create `tests/apps/mcp_server/` with `__init__.py`
  - **Acceptance**: Directory structure exists
  - **Commit**: `"chore: create MCP server directory structure"`

- [ ] **P4.0.2** Create test fixtures for MCP server
  - **TEST**: Create `tests/apps/mcp_server/conftest.py`
    - Fixture: `config()` - Returns ServerConfig for tests
    - Fixture: `document_service(config)` - Returns initialized DocumentService
    - Fixture: `mcp_server(document_service)` - Returns MCP server instance
  - **Acceptance**: Fixtures defined
  - **Commit**: `"test(mcp): add MCP server test fixtures"`

---

### 4.1 MCP Server Initialization [~2 hours]

- [ ] **P4.1.1** Test: Create MCP server
  - **TEST**: Create `tests/apps/mcp_server/test_server.py`
    - Test: `test_server_creation(config)`
      - Create server instance
      - Assert server initialized
      - Assert has name
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add server creation test (failing)"`

- [ ] **P4.1.2** Implement: MCP server class
  - **IMPL**: Create `apps/mcp_server/server.py`
    - Import `from mcp.server import Server`
    - Class: `MCPServer`
    - Method: `__init__(self, config: ServerConfig)`
    - Create MCP Server instance
    - Store config and server
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): create MCP server class"`

- [ ] **P4.1.3** Test: Server has service dependencies
  - **TEST**: Add test
    - Test: `test_server_has_services(mcp_server)`
      - Assert server has document_service
      - Assert service is DocumentService instance
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add service dependency test (failing)"`

- [ ] **P4.1.4** Implement: Service dependency injection
  - **IMPL**: Update `server.py`
    - Initialize FileSystemStorage
    - Initialize ValidationService, SchemaService
    - Initialize DocumentService with dependencies
    - Store document_service in server
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): add service dependency injection"`

- [ ] **P4.1.5** Test: Server registers tools
  - **TEST**: Add test
    - Test: `test_server_registers_tools(mcp_server)`
      - Assert server has tools registered
      - Check for expected tool names
  - **Acceptance**: Test FAILS (no tools yet)
  - **Commit**: `"test(mcp): add tool registration test (failing)"`

- [ ] **P4.1.6** Implement: Tool registration framework
  - **IMPL**: Update `server.py`
    - Method: `register_tools(self)`
    - Use MCP SDK to register tool handlers
    - Prepare for tool implementations
  - **Acceptance**: Test PASSES (empty list OK for now)
  - **Commit**: `"feat(mcp): add tool registration framework"`

---

### 4.2 MCP Tools - CREATE Document [~1.5 hours]

- [ ] **P4.2.1** Test: document_create tool
  - **TEST**: Create `tests/apps/mcp_server/test_document_tools.py`
    - Test: `test_document_create_success(mcp_server, document_service)`
      - Call tool: document_create(schema_name="text", content={...})
      - Assert returns dict with doc_id and version
      - Verify document created via document_service
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add document_create test (failing)"`

- [ ] **P4.2.2** Implement: document_create tool
  - **IMPL**: Create `apps/mcp_server/tools/document_tools.py`
    - Function: `async def document_create(schema_name: str, content: dict, server: MCPServer) -> dict`
      - Call: `server.document_service.create_document(schema_name, content)`
      - Catch exceptions and convert to MCP error format
      - Return: `{"doc_id": str(doc_id), "version": version}`
  - **IMPL**: Update `server.py` to register tool
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): implement document_create tool"`

- [ ] **P4.2.3** Test: document_create validation error
  - **TEST**: Add test
    - Test: `test_document_create_validation_error(mcp_server)`
      - Call with invalid content
      - Assert returns error response (not exception)
      - Assert error has details
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add validation error test (failing)"`

- [ ] **P4.2.4** Implement: Error handling for document_create
  - **IMPL**: Update `document_create()`
    - Wrap in try/except for ValidationFailedError
    - Return error dict: `{"error": "ValidationError", "message": ..., "details": ...}`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): add error handling to document_create"`

---

### 4.3 MCP Tools - READ Node [~1.5 hours]

- [ ] **P4.3.1** Test: document_read_node tool
  - **TEST**: Add test
    - Test: `test_document_read_node_success(mcp_server, document_service)`
      - Create document
      - Call tool: document_read_node(doc_id, node_path="/")
      - Assert returns content and version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add document_read_node test (failing)"`

- [ ] **P4.3.2** Implement: document_read_node tool
  - **IMPL**: Update `document_tools.py`
    - Function: `async def document_read_node(doc_id: str, node_path: str, server: MCPServer) -> dict`
      - Call: `server.document_service.read_node(doc_id, node_path)`
      - Return: `{"content": content, "version": version}`
  - **IMPL**: Register tool in server
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): implement document_read_node tool"`

- [ ] **P4.3.3** Test: document_read_node with nested path
  - **TEST**: Add test
    - Test: `test_document_read_node_nested(mcp_server, document_service)`
      - Create document with nested data
      - Read /title, /authors/0, /sections/0/title
      - Assert returns correct values
  - **Acceptance**: Test PASSES (already implemented)
  - **Commit**: `"test(mcp): verify nested path reading"`

- [ ] **P4.3.4** Test: document_read_node error handling
  - **TEST**: Add test
    - Test: `test_document_read_node_not_found(mcp_server)`
      - Call with non-existent doc_id
      - Assert returns error response
    - Test: `test_document_read_node_invalid_path(mcp_server, document_service)`
      - Create document, read invalid path
      - Assert returns error response
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add read_node error tests (failing)"`

- [ ] **P4.3.5** Implement: Error handling for document_read_node
  - **IMPL**: Update `document_read_node()`
    - Catch DocumentNotFoundError, PathNotFoundError
    - Return appropriate error responses
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): add error handling to document_read_node"`

---

### 4.4 MCP Tools - UPDATE Node [~2 hours]

- [ ] **P4.4.1** Test: document_update_node tool
  - **TEST**: Add test
    - Test: `test_document_update_node_success(mcp_server, document_service)`
      - Create document
      - Call tool: document_update_node(doc_id, "/title", "New Title", expected_version=1)
      - Assert returns updated content and new version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add document_update_node test (failing)"`

- [ ] **P4.4.2** Implement: document_update_node tool
  - **IMPL**: Update `document_tools.py`
    - Function: `async def document_update_node(doc_id: str, node_path: str, value: Any, expected_version: int, server: MCPServer) -> dict`
      - Call: `server.document_service.update_node(...)`
      - Return: `{"content": content, "version": version}`
  - **IMPL**: Register tool in server
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): implement document_update_node tool"`

- [ ] **P4.4.3** Test: document_update_node version conflict
  - **TEST**: Add test
    - Test: `test_document_update_node_version_conflict(mcp_server, document_service)`
      - Create and update document (version 2)
      - Try to update with expected_version=1
      - Assert returns version conflict error
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add version conflict test (failing)"`

- [ ] **P4.4.4** Implement: Version conflict error handling
  - **IMPL**: Update `document_update_node()`
    - Catch VersionConflictError
    - Return error: `{"error": "VersionConflict", "message": ..., "expected": ..., "actual": ...}`
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): add version conflict handling"`

- [ ] **P4.4.5** Test: document_update_node validation error
  - **TEST**: Add test
    - Test: `test_document_update_node_validation_error(mcp_server, document_service)`
      - Try to update with invalid value
      - Assert returns validation error
  - **Acceptance**: Test PASSES (error handling already exists)
  - **Commit**: `"test(mcp): verify update validation"`

---

### 4.5 MCP Tools - CREATE Node [~1.5 hours]

- [ ] **P4.5.1** Test: document_create_node tool
  - **TEST**: Add test
    - Test: `test_document_create_node_success(mcp_server, document_service)`
      - Create document with empty sections
      - Call tool: document_create_node(doc_id, "/sections", section_data, expected_version=1)
      - Assert returns created_path and new version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add document_create_node test (failing)"`

- [ ] **P4.5.2** Implement: document_create_node tool
  - **IMPL**: Update `document_tools.py`
    - Function: `async def document_create_node(doc_id: str, node_path: str, value: Any, expected_version: int, server: MCPServer) -> dict`
      - Call: `server.document_service.create_node(...)`
      - Return: `{"created_path": path, "version": version}`
  - **IMPL**: Register tool
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): implement document_create_node tool"`

- [ ] **P4.5.3** Test: document_create_node error handling
  - **TEST**: Add test
    - Test: `test_document_create_node_validation_error(mcp_server, document_service)`
      - Try to create with invalid data
      - Assert returns validation error
  - **Acceptance**: Test PASSES (error handling exists)
  - **Commit**: `"test(mcp): verify create_node validation"`

---

### 4.6 MCP Tools - DELETE Node [~1 hour]

- [ ] **P4.6.1** Test: document_delete_node tool
  - **TEST**: Add test
    - Test: `test_document_delete_node_success(mcp_server, document_service)`
      - Create document with sections
      - Call tool: document_delete_node(doc_id, "/sections/0", expected_version=1)
      - Assert returns deleted content and new version
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add document_delete_node test (failing)"`

- [ ] **P4.6.2** Implement: document_delete_node tool
  - **IMPL**: Update `document_tools.py`
    - Function: `async def document_delete_node(doc_id: str, node_path: str, expected_version: int, server: MCPServer) -> dict`
      - Call: `server.document_service.delete_node(...)`
      - Return: `{"content": deleted_value, "version": version}`
  - **IMPL**: Register tool
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): implement document_delete_node tool"`

- [ ] **P4.6.3** Test: document_delete_node error handling
  - **TEST**: Add test
    - Test: `test_document_delete_node_validation_error(mcp_server, document_service)`
      - Try to delete required field
      - Assert returns validation error
  - **Acceptance**: Test PASSES (error handling exists)
  - **Commit**: `"test(mcp): verify delete_node validation"`

---

### 4.7 MCP Tools - LIST Documents [~1 hour]

- [ ] **P4.7.1** Test: document_list tool
  - **TEST**: Add test
    - Test: `test_document_list_empty(mcp_server)`
      - Call tool: document_list()
      - Assert returns empty list
  - **Acceptance**: Test FAILS
  - **Commit**: `"test(mcp): add document_list test (failing)"`

- [ ] **P4.7.2** Implement: document_list tool
  - **IMPL**: Update `document_tools.py`
    - Function: `async def document_list(limit: int = 100, offset: int = 0, server: MCPServer) -> dict`
      - Call: `server.document_service.list_documents(limit, offset)`
      - Return: `{"documents": [...metadata dicts...]}`
  - **IMPL**: Register tool
  - **Acceptance**: Test PASSES
  - **Commit**: `"feat(mcp): implement document_list tool"`

- [ ] **P4.7.3** Test: document_list returns metadata
  - **TEST**: Add test
    - Test: `test_document_list_returns_metadata(mcp_server, document_service)`
      - Create 3 documents
      - Call document_list()
      - Assert returns 3 items with metadata
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(mcp): verify document_list metadata"`

- [ ] **P4.7.4** Test: document_list pagination
  - **TEST**: Add test
    - Test: `test_document_list_pagination(mcp_server, document_service)`
      - Create 5 documents
      - Call document_list(limit=2, offset=0)
      - Assert returns 2 items
      - Call document_list(limit=2, offset=2)
      - Assert returns next 2
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(mcp): verify document_list pagination"`

---

### 4.8 MCP Server Entry Point [~1 hour]

- [ ] **P4.8.1** Create __main__.py for MCP server
  - **IMPL**: Create `apps/mcp_server/__main__.py`
    - Load configuration (from file or env vars)
    - Initialize MCPServer with config
    - Set up stdio transport
    - Start server
  - **Acceptance**: Can import and run module
  - **Commit**: `"feat(mcp): add server entry point"`

- [ ] **P4.8.2** Test: Can start server programmatically
  - **TEST**: Create `tests/apps/mcp_server/test_main.py`
    - Test: `test_server_starts()`
      - Import main module
      - Create server
      - Assert server initialized
      - Assert has all tools registered
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(mcp): verify server startup"`

---

### 4.9 MCP Tool Descriptions & Schema [~1 hour]

- [ ] **P4.9.1** Add tool descriptions
  - **IMPL**: Update `document_tools.py`
    - Add docstrings to all tool functions
    - Include parameter descriptions
    - Include return value descriptions
    - Add usage examples in docstrings
  - **Acceptance**: All tools documented
  - **Commit**: `"docs(mcp): add tool descriptions"`

- [ ] **P4.9.2** Add input schemas for tools
  - **IMPL**: Update tool registrations
    - Define input schemas using MCP SDK
    - Specify required vs optional parameters
    - Add type information
    - Add validation constraints
  - **Acceptance**: Tools have complete schemas
  - **Commit**: `"feat(mcp): add tool input schemas"`

- [ ] **P4.9.3** Test: Tool schemas are valid
  - **TEST**: Add test
    - Test: `test_tool_schemas_valid(mcp_server)`
      - Inspect registered tools
      - Assert all have schemas
      - Assert schemas are valid
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(mcp): verify tool schemas"`

---

### 4.10 MCP Integration Tests [~1 hour]

- [ ] **P4.10.1** Integration test: Full document lifecycle via MCP
  - **TEST**: Create `tests/apps/mcp_server/test_integration.py`
    - Test: `test_full_document_lifecycle_mcp(mcp_server)`
      - document_create - create
      - document_read_node - read root
      - document_update_node - update field
      - document_read_node - verify update
      - document_create_node - add section
      - document_delete_node - remove section
      - document_list - list all
      - Verify final state
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(mcp): add full lifecycle integration test"`

- [ ] **P4.10.2** Integration test: Error handling across tools
  - **TEST**: Add test
    - Test: `test_error_handling_integration_mcp(mcp_server)`
      - Test DocumentNotFoundError
      - Test ValidationFailedError
      - Test VersionConflictError
      - Test PathNotFoundError
      - Assert all return proper error responses
  - **Acceptance**: Test PASSES
  - **Commit**: `"test(mcp): add error handling integration test"`

---

### 4.11 MCP vs REST Comparison Test [~30 minutes]

- [ ] **P4.11.1** Test: MCP and REST produce identical results
  - **TEST**: Create `tests/integration/test_mcp_rest_parity.py`
    - Test: `test_mcp_rest_create_parity(mcp_server, rest_client)`
      - Create same document via MCP and REST
      - Assert both succeed
      - Assert versions match
    - Test: `test_mcp_rest_read_parity(...)`
      - Create document
      - Read via MCP and REST
      - Assert results identical
    - Test: `test_mcp_rest_update_parity(...)`
      - Update via both interfaces
      - Verify same final state
  - **Acceptance**: Test PASSES - proves zero duplication
  - **Commit**: `"test(integration): verify MCP/REST parity"`

**🎯 Phase 4 Complete When:**
- ✅ MCP server fully functional
- ✅ All document CRUD tools implemented (6 tools)
- ✅ All tools have descriptions and schemas
- ✅ All tests passing (25+ tests)
- ✅ Integration tests passing
- ✅ Error handling consistent with REST API
- ✅ Can run MCP server: `python -m apps.mcp_server`
- ✅ MCP and REST produce identical results (zero duplication verified)
- ✅ Project complete: Dual interface (MCP + REST) sharing DocumentService

---

## 🎉 Project Complete!

All phases restructured with micro-step TDD approach:
- **Phase 0**: Core library foundation (50+ tasks)
- **Phase 1**: DocumentService implementation (50 tasks)
- **Phase 2**: Configuration management & dev tools (30+ tasks)
- **Phase 3**: REST API interface layer (50+ tasks)
- **Phase 4**: MCP interface layer (40+ tasks)

**Total**: ~220 granular tasks, each taking ~10 minutes
**Pattern**: Test (FAIL) → Implement → Test (PASS) → Commit
**Result**: Clean git history with atomic, reversible changes

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
