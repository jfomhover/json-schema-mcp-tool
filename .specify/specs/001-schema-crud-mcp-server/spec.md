# Feature Specification: JSON Schema CRUD MCP Server

**Feature Branch**: `001-schema-crud-mcp-server`  
**Created**: 2025-11-29  
**Status**: Draft  
**Input**: User description: "This code implements an MCP server to do CRUD operations on a large json file following a given json schema. The MCP server has tools to create a root entry with an identifier, then all CRUD operations on that entry will have this identifier as first argument. The CRUD operations have a path to a given json tree section. There should be an operation to return the schema of that specific section in the json path, an operation to return the current content, an operation to update the content, an operation to create, and an operation to delete."

## Clarifications

### Session 2025-11-29

- Q: How should clients retrieve the complete, final JSON document after making incremental CRUD operations? → A: Dual-mode retrieval - MCP tools remain focused on path-based operations for agent-driven editing. Separate mechanism (MCP resource URI or client-side direct access) provided for client applications to retrieve complete documents when needed for saving/display/processing.
- Q: What storage mechanism should the system use for persisting JSON documents? → A: Local file-based storage for MVP with abstraction layer for extensibility. Use JSON files in directory structure initially, but implement storage interface that can support future migration to cloud NoSQL (MongoDB, DynamoDB, Firestore, etc.).
- Q: Should the system support multiple different schemas or use a single predetermined schema? → A: Single-schema-per-server-instance architecture. The MCP server is initialized with ONE specific JSON schema at startup, and ALL documents managed by that server instance MUST conform to that schema. This is a specialized tool for managing a specific document type, not a generic NoSQL database. Different schemas require separate server instances.
- Q: What should the parameter name be for document identifiers? → A: Use `doc_id` consistently throughout to make it clear these are document identifiers, not generic identifiers.
- Q: What is the primary purpose and scope of the CRUD operations? → A: The purpose is to manage **complete documents** (e.g., books, articles). The MCP server provides **granular path-based CRUD operations** on sections/subsections of the JSON tree, enabling agents to make surgical edits (update a chapter title, add a footnote, delete a paragraph) without replacing entire documents. This is NOT a generic JSON editor - it's a document-centric system with path-based editing capabilities that maintains whole-document validity.
- Q: How should document creation work - should doc_id be provided by the caller or auto-generated? → A: **Auto-generated approach**: `document_create` takes NO arguments and returns a system-generated unique doc_id. This enables agents to create documents on-demand and then populate them incrementally using CRUD operations. The system initializes a minimal valid document structure (empty object or schema defaults) that the agent builds upon.
- Q: How should validation errors be reported? → A: **Comprehensive error reporting**: System MUST return ALL validation errors in a single report, not fail on first error. Each error includes: machine-readable code, human-readable actionable message, JSON Pointer to exact location, violated constraint, expected value, and actual value. This enables agents to fix all issues in one pass rather than trial-and-error iteration.
- Q: How should document initialization handle required fields without defaults? → A: **Strict initialization**: If the schema has required fields without default values, `document_create` MUST fail with a clear error. The system will ONLY populate fields that have explicit `default` values defined in the JSON Schema. No implicit defaults (empty strings, zeros, etc.) are allowed. This ensures every created document is immediately valid and prevents ambiguity about what "minimal valid" means.
- Q: When should validation occur during update/create/delete operations? → A: **Validation-before-modification**: System MUST validate BEFORE modifying any state. Process: (1) Clone current document, (2) Apply modification to clone, (3) Validate ENTIRE cloned document tree, (4) If valid: persist atomically and update in-memory state, (5) If invalid: discard clone, return all errors, no state change. This ensures true atomicity - operations either fully succeed or fully fail with no partial modifications.
- Q: How should concurrent operations on the same document be handled? → A: **Optimistic locking with version/etag**: Each document has a version identifier that increments on every write. Read operations return current version. Write operations (update/create/delete) require version parameter and fail if document version has changed since read. Read operations never block writes. Lock acquisition timeout hardcoded at 10 seconds. This prevents lost updates while allowing high concurrency.
- Q: What is the initial version value for newly created documents? → A: **Version starts at 1**: When `document_create` creates a new document, it is initialized with `version: 1`. All subsequent write operations (update/create_node/delete_node) increment the version counter. This means version 0 never exists - the first readable version is always 1.
- Q: How should schema default values with $ref resolution work? → A: **Recursive $ref resolution for defaults**: System MUST recursively resolve ALL $ref references during schema loading and merge default values from referenced schemas. When initializing documents, defaults are collected from the entire resolved schema tree. If a $ref target has defaults, they apply. This ensures consistent initialization regardless of schema composition patterns.
- Q: What should happen when path operations target non-existent intermediate paths? → A: **Fail with detailed path error**: System MUST NOT auto-create intermediate paths. Operations on paths like `/a/b/c` when `/a/b` doesn't exist MUST fail with error code `path-not-found` including: the requested path, the deepest existing ancestor path, and guidance on which path to create first. This prevents unintended structure creation and keeps document evolution explicit and intentional.
- Q: Should error codes be enumerated as a closed set? → A: **Exhaustive error code enumeration**: System MUST define a complete, versioned list of ALL possible error codes as part of the API contract. Each code must have: machine-readable identifier, HTTP-style category (4xx client error, 5xx server error), description, typical causes, and remediation guidance. This enables robust error handling in client code without string parsing.
- Q: What should the storage directory structure be? → A: **Flat directory with doc_id as filename**: All documents stored in a single configured directory as `{doc_id}.json` files (e.g., `./data/01JDEX3M8K2N9WPQR5STV6XY7Z.json`). Temporary files use `.tmp` suffix during writes. Flat structure simplifies implementation, avoids nested directory limits, and enables easy backup/sync. Future optimization can introduce sharding subdirectories (e.g., first 2 chars of doc_id) if needed for >10k documents.
- Q: What doc_id generation algorithm should be used? → A: **ULID (Universally Unique Lexicographically Sortable Identifier)**: Use ULID format for auto-generated doc_id values. Benefits: 26-character case-insensitive encoding, timestamp-ordered (sortable), 128-bit random component (collision-resistant), filesystem-safe (no special chars), more human-friendly than UUIDs. Standard ULID libraries available in all languages. Example: `01JDEX3M8K2N9WPQR5STV6XY7Z`.
- Q: What are the transaction boundaries for file system operations? → A: **Document-level atomic boundaries**: Each document operation (create/update/delete) is an atomic transaction bounded by a single document. Write operations use: (1) Clone document in-memory, (2) Apply modification to clone, (3) Validate entire clone, (4) Write to `{doc_id}.tmp` file, (5) fsync() to ensure durable storage, (6) Atomic rename to `{doc_id}.json`. No cross-document transactions. Consistency guaranteed at individual document level only.

## Overview

This specification defines an MCP (Model Context Protocol) server that provides **document-centric CRUD operations** for managing complete JSON documents conforming to a specific JSON Schema. The server enables agents and applications to perform surgical, path-based edits on document sections (chapters, paragraphs, metadata) while maintaining whole-document validity and schema compliance.

**Purpose**: Manage complete, structured documents (books, articles, configuration files) that follow a predetermined schema.

**Mechanism**: Provide granular MCP tools for CRUD operations at any path within the document tree, enabling incremental editing without replacing entire documents.

**Scope**: This is a specialized document management tool, NOT a generic JSON editor or NoSQL database. Each server instance is configured with a single schema and manages documents of that type exclusively.

## User Scenarios & Testing *(mandatory)*

### User Story 0 - Server Initialization with Schema (Priority: P1)

A user wants to start the MCP server with a specific JSON schema that defines the structure for all documents that will be managed by this server instance.

**Why this priority**: This is the prerequisite for all other operations - the server must know what schema to enforce. This establishes the single-schema architecture that differentiates this from a generic NoSQL database.

**Independent Test**: Can be fully tested by starting server with a schema file path, verifying server initializes successfully, and confirming the schema is loaded and ready for document validation.

**Acceptance Scenarios**:

1. **Given** a valid JSON schema file path in server configuration, **When** server starts, **Then** system loads and validates the schema, making it available for all document operations
2. **Given** an invalid schema file path, **When** server attempts to start, **Then** system fails with clear error message indicating schema not found
3. **Given** a malformed JSON schema file, **When** server attempts to start, **Then** system fails with validation error detailing schema problems
4. **Given** server is running with a schema, **When** queried for schema information, **Then** system returns the configured schema URI and metadata
5. **Given** no schema specified in configuration, **When** server attempts to start, **Then** system fails with error requiring schema configuration

---

### User Story 1 - Create Empty Document (Priority: P1)

An agent wants to create a new document instance (e.g., a book) that will be populated incrementally. The system returns a unique document ID and initializes a minimal valid document structure that the agent can then build upon using CRUD operations.

**Why this priority**: This is the foundational operation - without the ability to create a document, no other operations are possible. This represents the core MVP that enables document instantiation. The no-arguments approach allows agents to create documents on-demand and build them incrementally.

**Independent Test**: Can be fully tested by calling document_create with no arguments, verifying it returns a unique document ID and a minimal valid document structure. Delivers the ability to instantiate new documents.

**Acceptance Scenarios**:

1. **Given** the server is initialized with a JSON schema, **When** agent calls document_create with no arguments, **Then** system generates a unique doc_id, creates a document with all schema-defined defaults, and returns the doc_id
2. **Given** a schema with required fields that have default values, **When** agent creates a new document, **Then** system initializes those required fields with the schema-defined defaults
3. **Given** a schema with required fields without default values, **When** agent attempts to create a new document, **Then** system MUST fail with error "Cannot create document: schema has required fields without defaults" and list the missing required fields
4. **Given** multiple sequential document_create calls, **When** agent creates documents, **Then** each returns a unique doc_id with no collisions
5. **Given** a newly created document, **When** agent queries its content at root path "/", **Then** system returns the initialized structure with all schema defaults applied, passing full schema validation

---

### User Story 2 - Read Document Content by Path (Priority: P1)

A user wants to retrieve specific content from a document using JSON path notation, getting only the relevant subset of data rather than the entire document. This is optimized for agent-driven incremental editing operations.

**Why this priority**: Reading is equally fundamental as writing. Users need to inspect document state before making changes. This enables efficient access to large documents by retrieving only needed sections for agent processing.

**Independent Test**: Can be tested independently by creating a document, then reading different paths (root, nested objects, arrays, specific elements) and verifying returned content matches the path location and conforms to schema.

**Acceptance Scenarios**:

1. **Given** a document exists with nested structure, **When** agent reads path "/metadata/author", **Then** system returns only the author field value with type validation
2. **Given** a document with array content, **When** agent reads path "/content/chapters/0", **Then** system returns first chapter object
3. **Given** a document with doc_id "book-123" exists, **When** agent reads path "/" (root), **Then** system returns entire document content (note: for large documents, agents should use specific paths; client applications should use separate export mechanism)
4. **Given** a non-existent doc_id, **When** user attempts to read any path, **Then** system returns "document not found" error
5. **Given** an invalid JSON path, **When** user attempts to read, **Then** system returns "invalid path" error with guidance
6. **Given** a path that doesn't exist in the document, **When** user reads that path, **Then** system returns "path not found" error with nearest valid parent path

---

### User Story 3 - Get Schema for Specific Path (Priority: P2)

A user wants to understand what data structure and validation rules apply to a specific location in the document tree before creating or updating content there.

**Why this priority**: This enables self-service and reduces errors by letting users discover valid data shapes before attempting operations. Critical for API clients and UI generation.

**Independent Test**: Can be tested by querying schema for various paths and verifying returned schema matches the definition for that location, including resolved $ref references.

**Acceptance Scenarios**:

1. **Given** a document with known schema, **When** user requests schema for path "/metadata", **Then** system returns the metadata object schema definition with all constraints
2. **Given** a schema with $ref references, **When** user requests schema for a path containing a reference, **Then** system returns fully resolved schema (dereferenced)
3. **Given** a path pointing to an array item, **When** user requests schema, **Then** system returns the item schema from array definition
4. **Given** a path with polymorphic types (oneOf/anyOf), **When** user requests schema, **Then** system returns all possible schemas for that location
5. **Given** an invalid path, **When** user requests schema, **Then** system returns error indicating path is not valid for this schema

---

### User Story 4 - Update Document Content at Path (Priority: P2)

A user wants to modify specific content within a document at a given path, with automatic validation against the schema for that location.

**Why this priority**: Update is the most common operation after initial creation. This enables incremental document editing without replacing entire documents.

**Independent Test**: Can be tested by creating a document, updating specific paths with valid/invalid data, and verifying changes are persisted correctly and validation errors are returned appropriately.

**Acceptance Scenarios**:

1. **Given** a document exists with version 5, **When** user reads document (getting version 5), then updates path "/metadata/title" with valid string and version 5, **Then** system validates version matches, clones document, applies change to clone, validates entire clone, persists atomically, increments version to 6, and returns success with new version
2. **Given** a document exists, **When** user updates with invalid data causing validation failure, **Then** system discards clone without persisting, original document unchanged, returns comprehensive validation report with ALL errors
3. **Given** a required field in schema, **When** user attempts to update to null, **Then** system validates clone, detects required field violation, discards clone, returns complete validation report
4. **Given** an update to nested path like "/a/b/c", **When** intermediate path "/a/b" doesn't exist, **Then** system returns error code `path-not-found` with deepest existing ancestor path and guidance, no state change
5. **Given** an array field, **When** user updates specific index, **Then** system applies to clone, validates entire cloned tree, persists atomically if valid
6. **Given** update violates multiple schema constraints, **When** validation of cloned document fails, **Then** system discards clone and returns ALL constraint violations in single report enabling batch fixes
7. **Given** document at version 5, **When** user attempts update with version 3 (stale), **Then** system detects version conflict, rejects operation with error code `version-conflict`, returns current version 5 for client to retry
8. **Given** concurrent updates to same document, **When** first update succeeds incrementing version, **Then** second update with old version fails with `version-conflict`, client must re-read and retry

---

### User Story 5 - Create New Content at Path (Priority: P3)

A user wants to add new content to an existing document at a specific path, such as appending a new chapter to a book or adding a new property.

**Why this priority**: This complements update operations by allowing additive changes. Less critical than update because update can sometimes achieve similar results, but important for array operations and optional fields.

**Independent Test**: Can be tested by creating base document, then using create operation to add new elements (array items, optional fields) and verifying schema validation and persistence.

**Acceptance Scenarios**:

1. **Given** a document with an array field, **When** user creates new item in array (e.g., "/content/chapters/-"), **Then** system validates new item against array item schema and appends to array, returning ALL validation errors if any exist
2. **Given** a path to optional property that doesn't exist, **When** user creates content at that path, **Then** system validates against schema and adds the property, providing comprehensive error report if validation fails
3. **Given** a path that already exists, **When** user attempts to create, **Then** system returns error code `conflict` with clear explanation
4. **Given** a create operation with multiple invalid fields, **When** validation fails, **Then** system returns complete validation report with ALL errors without modifying document
5. **Given** nested path like "/a/b/c" where intermediate paths "/a/b" don't exist, **When** user attempts create, **Then** system returns error code `path-not-found` with deepest existing ancestor and guidance on which path to create first (explicit path creation required)

---

### User Story 6 - Delete Content at Path (Priority: P3)

A user wants to remove specific content from a document at a given path, such as deleting a chapter or removing an optional field.

**Why this priority**: Deletion is necessary for complete CRUD functionality but less frequently used than read/update. Important for cleanup and content management workflows.

**Independent Test**: Can be tested by creating document with content, deleting at various paths, and verifying content is removed while maintaining document validity against schema.

**Acceptance Scenarios**:

1. **Given** a document with optional field, **When** user deletes that path, **Then** system removes field and validates remaining document against schema
2. **Given** a required field in schema, **When** user attempts to delete, **Then** system rejects with required field violation error
3. **Given** an array element, **When** user deletes by index, **Then** system removes element, reindexes array, and validates
4. **Given** a path that doesn't exist, **When** user attempts to delete, **Then** system returns "path not found" error
5. **Given** deletion would violate schema constraints (e.g., minItems on array), **When** attempted, **Then** system rejects with constraint violation error
6. **Given** successful deletion, **When** referential integrity checks exist, **Then** system validates no orphaned references remain

---

### User Story 7 - List All Documents (Priority: P3)

A user wants to see all documents managed by the server, with their identifiers and basic metadata.

**Why this priority**: Discovery capability - enables users to know what documents exist. Lower priority because individual document operations can work with known identifiers.

**Independent Test**: Can be tested by creating multiple documents and verifying list operation returns all identifiers with summary information.

**Acceptance Scenarios**:

1. **Given** multiple documents exist in system, **When** user lists all documents, **Then** system returns array of document identifiers with schema type and creation timestamp
2. **Given** no documents exist, **When** user lists documents, **Then** system returns empty array
3. **Given** large number of documents, **When** user lists with pagination parameters, **Then** system returns paginated results

---

### User Story 8 - Export Complete Document (Priority: P2)

A client application wants to retrieve the complete JSON document for purposes such as saving to disk, displaying in UI, or further processing outside the agent context.

**Why this priority**: Essential for client applications to persist or display final results after agent-driven editing. Separated from agent operations to avoid overwhelming agent context with large documents.

**Independent Test**: Can be tested by creating and editing a document via path operations, then using the export mechanism to retrieve the complete document and verifying it matches all applied changes and validates against schema.

**Acceptance Scenarios**:

1. **Given** a document exists after multiple edit operations, **When** client application requests export via MCP resource URI (e.g., `schema://doc-id`), **Then** system returns complete validated document
2. **Given** a large document (>1MB), **When** client exports, **Then** system efficiently retrieves without loading into agent context
3. **Given** document export request, **When** document is successfully retrieved, **Then** system validates entire document against schema before returning
4. **Given** client application has direct storage access, **When** client reads document file directly, **Then** document structure matches MCP-managed state

---

### Edge Cases

- **What happens when a schema has required fields without default values?**
  - `document_create` fails immediately with error code `required-field-without-default`, listing all required fields that lack defaults. System enforces strict initialization - only explicit defaults are used.

- **What happens if validation fails after applying a modification?**
  - The cloned document is discarded, original document remains unchanged in memory and on disk, and comprehensive validation report with ALL errors is returned to caller. Zero partial modifications occur.

- **What happens if file write succeeds but rename fails?**
  - Operation fails, temporary `.tmp` file remains on disk (cleaned up on next server start), original document file unchanged, in-memory state unchanged. Operation can be safely retried.

- **What happens during concurrent updates to the same document?**
  - System uses optimistic locking with version counters. First operation with correct version succeeds and increments version. Second operation with stale version fails with `version-conflict` error. Client must re-read document (getting new version) and retry. 10-second document lock timeout applies.

- **What happens when document version doesn't match in write operation?**
  - System immediately rejects operation with error code `version-conflict`, returning expected version and current version. No modification occurs. Client must re-read document to get current state and version, then retry operation.

- **What happens when a JSON path references an array element that is out of bounds?**
  - System returns error code `path-not-found` with current array length and guidance.

- **How does system handle schema with $ref references and default values?**
  - System recursively resolves ALL $ref references during schema loading at startup. Default values from referenced schemas are merged into resolved tree. Document initialization uses defaults from entire resolved schema regardless of $ref composition.

- **What happens when path operation targets non-existent intermediate path (e.g., `/a/b/c` when `/a/b` doesn't exist)?**
  - System fails with error code `path-not-found`, including: requested path, deepest existing ancestor path, and explicit guidance on which path to create first. NO auto-creation of intermediate paths - document structure evolution must be intentional.

- **How are error codes versioned and documented?**
  - Error codes are exhaustive enumeration in API contract. Each code includes: kebab-case identifier, HTTP category (4xx/5xx), description, causes, remediation. Error codes are stable across minor versions. New codes may be added; existing codes never change meaning.

- **What storage directory structure is used?**
  - Flat directory structure: all documents stored as `{doc_id}.json` in single configured directory (e.g., `./data/01JDEX3M8K2N9WPQR5STV6XY7Z.json`). Temporary files use `.tmp` suffix. Simple, efficient for MVP, can add sharding subdirectories for >10k documents.

- **What format are auto-generated doc_id values?**
  - ULID (Universally Unique Lexicographically Sortable Identifier): 26-character case-insensitive string, timestamp-ordered, 128-bit random, filesystem-safe. Example: `01JDEX3M8K2N9WPQR5STV6XY7Z`. Standard library used for generation.

- **What are transaction boundaries for operations?**
  - Document-level atomic transactions only. Each document operation is isolated atomic unit. NO cross-document transactions. Write workflow: clone → modify → validate → write `.tmp` → fsync() → atomic rename to `.json`. Consistency guaranteed at individual document level.

- **How does system handle very large documents (>100MB) in memory?**
  - System uses streaming validation for large documents and path-based access to avoid loading entire document into agent context.

- **What happens when an agent tries to read the root path of a very large document?**
  - System returns the full document but for large documents, agents should use specific paths; client applications should use the export mechanism (MCP resource URI).

- **What happens when schema file is modified while server is running?**
  - Server continues using the loaded schema in memory; schema changes require server restart.

- **What if users need to manage documents with different schemas?**
  - They must run separate server instances, each initialized with a different schema (single-schema-per-server architecture).

- **What happens when JSON path contains special characters or escape sequences?**
  - System uses RFC 6901 (JSON Pointer) standard encoding/decoding.

- **What happens if storage backend becomes unavailable during operation?**
  - Operation fails with error code `storage-write-failed` or `storage-read-failed`; no partial writes; transaction rollback.

- **How does system validate circular references in schemas?**
  - Schema loading fails with error code `schema-resolution-failed` if circular $ref chains detected; runtime validation handles recursive structures with depth limits.

- **How do client applications export complete documents after agent editing?**
  - Client applications use MCP resource URIs (e.g., `schema://doc_id`) or direct file access when sharing storage layer with server.

- **What happens if the storage directory doesn't exist or lacks write permissions?**
  - System initialization fails with clear error message; storage directory created automatically if missing, but parent must exist and be writable.

- **What happens if document content file exists but metadata file is missing?**
  - System treats document as corrupted and logs error. Document is not accessible until metadata is restored or document is recreated. On startup, system can optionally regenerate metadata from content file (with version reset to 1).

- **What happens if metadata file exists but content file is missing?**
  - System treats document as corrupted. `document_read_node` returns `document-not-found` error. Orphaned metadata files can be cleaned up during startup verification.

- **How does the storage abstraction layer ensure future cloud migration compatibility?**
  - Storage interface defines all CRUD operations independently of implementation; local file storage is one implementation; future cloud NoSQL implementations will satisfy same interface.

- **What happens if server is started without a schema configuration?**
  - Server fails to start with error code `schema-load-failed` requiring schema file path in configuration.

- **What happens if schema has circular $ref references?**
  - Schema loading at startup fails with error code `schema-resolution-failed` detailing the circular reference chain.

- **Do read operations block write operations or vice versa?**
  - NO. Read operations never block writes. Reads return current version. Optimistic locking handles conflicts. Document-level locks only serialize writes to same document.

## Requirements *(mandatory)*

### Atomic Operation Workflow

All mutating operations (update, create, delete) follow this mandatory workflow to ensure atomicity:

```
1. CLONE: Deep clone current document state from memory
2. MODIFY: Apply requested modification to cloned document
3. VALIDATE: Run full JSON Schema validation against entire cloned document tree
4. DECISION:
   a. If validation PASSES:
      - Write cloned document to {doc_id}.tmp file
      - Call fsync() to flush to disk
      - Atomically rename {doc_id}.tmp to {doc_id}.json
      - Update in-memory state to cloned document
      - Return success with validation report (valid=true)
   b. If validation FAILS:
      - Discard cloned document immediately
      - Original document remains unchanged (memory + disk)
      - Return comprehensive validation report with ALL errors
      - No state change, operation fully rolled back
```

**Key Guarantees:**
- Original document never modified until validation passes
- Validation sees complete document state, not partial modifications
- File system operations are atomic (write-then-rename)
- Failed operations leave zero trace
- Concurrent operations serialized per document (see concurrency requirements)

### Functional Requirements

#### Server Initialization & Schema Configuration

- **FR-001**: System MUST be initialized with a single JSON schema at server startup
- **FR-001a**: System MUST support configuration via environment variables OR JSON configuration file
- **FR-001b**: System MUST read configuration parameters in order of precedence: (1) environment variables, (2) config file, (3) built-in defaults
- **FR-001c**: Configuration MUST include required parameter: `SCHEMA_PATH` or `schema_path` (absolute or relative path to JSON Schema file)
- **FR-001d**: Configuration MUST include optional parameter: `STORAGE_DIR` or `storage_dir` (default: `./data`)
- **FR-001e**: Configuration MUST include optional parameter: `LOG_LEVEL` or `log_level` (default: `info`, allowed: `debug|info|warn|error`)
- **FR-001f**: Configuration file location specified by environment variable `CONFIG_FILE` (default: `./config.json`)
- **FR-002**: System MUST load schema from file path specified in server configuration
- **FR-003**: System MUST validate the schema itself is valid JSON Schema Draft 2020-12 before accepting it
- **FR-004**: System MUST fail to start if schema file is missing, unreadable, or invalid
- **FR-005**: System MUST use the configured schema for ALL document operations within that server instance
- **FR-006**: System MUST NOT allow schema changes while server is running (require restart with new schema)
- **FR-007**: System MUST provide mechanism to query the currently configured schema URI and metadata

#### Document Lifecycle

- **FR-008**: System MUST support creating a new document instance with no input arguments, auto-generating a unique doc_id
- **FR-009**: System MUST initialize new documents ONLY with fields that have explicit `default` values defined in the JSON Schema
- **FR-009a**: System MUST fail document creation if schema contains required fields without default values, returning clear error listing all missing required fields
- **FR-009b**: System MUST recursively apply default values from nested schemas and resolved $ref definitions
- **FR-009c**: System MUST validate the initialized document against the full schema before persisting (it must pass 100% validation)
- **FR-010**: System MUST auto-generate doc_ids that are unique, URL-safe strings with minimum 8 characters, maximum 256 characters
- **FR-011**: System MUST persist documents durably (survive server restart)
- **FR-012**: System MUST return the auto-generated doc_id immediately upon document creation
- **FR-013**: System MUST automatically apply the server's configured schema to all new documents (no per-document schema selection)
- **FR-014**: System MUST implement storage through an abstraction layer/interface to enable future migration from local to cloud storage

#### Storage Implementation (MVP)

- **FR-015**: System MUST use local file-based storage for MVP implementation
- **FR-016**: System MUST store each document as a separate JSON file in a structured directory
- **FR-016a**: System MUST store document metadata in separate companion file `{doc_id}.meta.json` alongside content file `{doc_id}.json`
- **FR-016b**: Metadata file MUST contain: `doc_id` (string), `version` (integer), `schema_uri` (string), `created_at` (ISO 8601 timestamp), `modified_at` (ISO 8601 timestamp), `content_size_bytes` (integer)
- **FR-016c**: System MUST update metadata file atomically using same write-then-rename strategy as content files (`{doc_id}.meta.tmp` → `{doc_id}.meta.json`)
- **FR-016d**: System MUST keep version counter in metadata file only (NOT embedded in document content)
- **FR-017**: System MUST use auto-generated doc_id as filename (with .json extension), ensuring filesystem-safe characters
- **FR-018**: System MUST implement atomic file write operations using write-then-rename strategy
- **FR-018a**: System MUST write validated document to temporary file `{doc_id}.tmp`
- **FR-018b**: System MUST call fsync() on temporary file to ensure data is flushed to disk
- **FR-018c**: System MUST atomically rename `{doc_id}.tmp` to `{doc_id}.json` (atomic at OS level)
- **FR-018d**: System MUST cleanup any orphaned `.tmp` files on server startup (crash recovery)
- **FR-019**: System MUST support efficient file-based lookups by doc_id
- **FR-020**: Storage interface MUST be designed to support future NoSQL backends (MongoDB, DynamoDB, Firestore, CouchDB, etc.) without changes to business logic

#### JSON Path Operations

- **FR-021**: System MUST support JSON Pointer (RFC 6901) syntax for all path operations
- **FR-022**: System MUST validate JSON paths before executing operations
- **FR-023**: System MUST provide clear error messages for invalid paths including suggestions for nearest valid path
- **FR-024**: System MUST handle array indexing including negative indices (from end) and append notation (`-`)
- **FR-025**: System MUST support root path `/` to reference entire document

#### Read Operations

- **FR-026**: System MUST retrieve content at specified path, returning only that subtree
- **FR-027**: System MUST return content in JSON format matching schema definition for that path
- **FR-028**: System MUST validate returned content against schema before responding
- **FR-029**: System MUST return typed error for non-existent doc_ids
- **FR-030**: System MUST return typed error for non-existent paths within existing documents
- **FR-031**: System MUST optimize read operations for agent use by returning manageable content sizes at specific paths

#### Document Export & Retrieval

- **FR-032**: System MUST provide MCP resource URI access (e.g., `schema://doc-id`) for client applications to retrieve complete documents
- **FR-033**: System MUST support exporting complete validated documents independent of MCP tool operations
- **FR-034**: System MUST validate entire document against schema before export
- **FR-035**: System MUST support client-side direct file access when client and server share storage layer

#### Schema Introspection

- **FR-036**: System MUST return JSON schema definition for any valid path in document structure
- **FR-037**: System MUST resolve all `$ref` references when returning schema (fully dereferenced)
- **FR-038**: System MUST handle polymorphic schemas (oneOf, anyOf, allOf) by returning complete type information
- **FR-039**: System MUST return schema for array items when path points to array element
- **FR-040**: System MUST include all validation constraints in returned schema (pattern, format, min/max, required fields, etc.)

#### Update Operations

- **FR-041**: System MUST use copy-on-write semantics for all update operations
- **FR-041a**: System MUST create deep clone of current document state before applying modifications
- **FR-041b**: System MUST apply modification to cloned document only
- **FR-041c**: System MUST validate ENTIRE cloned document tree against schema
- **FR-041d**: System MUST persist cloned document atomically (write-then-rename) if validation passes
- **FR-041e**: System MUST update in-memory state to cloned document only after successful persistence
- **FR-041f**: System MUST discard clone and return validation errors if validation fails, leaving original document unchanged
- **FR-042**: System MUST guarantee atomic updates (all-or-nothing - no partial updates on validation failure)
- **FR-043**: System MUST preserve document validity after updates (entire document validates against schema)
- **FR-044**: System MUST prevent updates that would violate required field constraints
- **FR-045**: System MUST prevent updates that would violate type constraints
- **FR-046**: System MUST support updating nested paths, including array elements
- **FR-047**: System MUST return validation report on successful update confirming document validity

#### Create Operations

- **FR-048**: System MUST use copy-on-write semantics for create operations (same process as updates)
- **FR-048a**: System MUST clone current document, apply create operation to clone, validate entire cloned tree, then persist if valid
- **FR-049**: System MUST support appending to arrays using JSON Pointer append notation (`/-`)
- **FR-050**: System MUST validate entire cloned document against schema before persistence (not just created node)
- **FR-051**: System MUST reject create operations when path already exists in cloned document (conflict)
- **FR-052**: System MUST support creating nested structures when parent paths allow additional properties

#### Delete Operations

- **FR-053**: System MUST use copy-on-write semantics for delete operations (same process as updates)
- **FR-053a**: System MUST clone current document, apply delete operation to clone, validate entire remaining tree, then persist if valid
- **FR-054**: System MUST prevent deletion of required fields (detected during validation of cloned document)
- **FR-055**: System MUST validate remaining document structure after deletion in clone before persisting
- **FR-056**: System MUST prevent deletions that would violate schema constraints like minItems (detected during validation)
- **FR-057**: System MUST support deleting array elements with automatic reindexing in cloned document

#### Validation & Error Handling

- **FR-058**: System MUST use JSON Schema Draft 2020-12 or later for validation
- **FR-059**: System MUST perform COMPLETE validation and return ALL errors in a single validation report (not fail-fast on first error)
- **FR-060**: System MUST return comprehensive validation reports including: array of ALL validation errors, each with error code, human-readable message, JSON Pointer to exact location, schema constraint violated, actual value provided, and expected constraint
- **FR-061**: System MUST validate at every boundary: input validation, pre-persistence validation, post-retrieval validation
- **FR-062**: System MUST provide actionable error messages that clearly explain what needs to be fixed and how
- **FR-063**: System MUST log all validation failures with full context for debugging
- **FR-064**: System MUST return validation errors in a structured format that enables programmatic processing and batch fixes

#### Concurrency Control

- **FR-076**: System MUST implement optimistic locking using document version identifiers (integer counter or etag)
- **FR-076a**: System MUST initialize new documents with version counter starting at 1 (version 0 never exists)
- **FR-077**: System MUST increment document version on every successful write operation (update, create node, delete node)
- **FR-078**: System MUST return current document version in all read operations (document_read_node output)
- **FR-079**: System MUST require version parameter in all write operation inputs (document_update_node, document_create_node, document_delete_node)
- **FR-080**: System MUST validate version parameter matches current document version before applying write operation
- **FR-081**: System MUST fail write operations with error code `version-conflict` if document version has changed since client's read
- **FR-082**: Read operations (document_read_node, schema_get_node) MUST NOT block or be blocked by write operations
- **FR-083**: System MUST use document-level lock timeout of 10 seconds (hardcoded, not configurable)
- **FR-083a**: System MUST implement document locks using in-memory mutex/lock map keyed by doc_id
- **FR-083b**: Write operations MUST acquire exclusive lock on doc_id before cloning document (blocking operation with timeout)
- **FR-083c**: System MUST release lock immediately after successful write (after atomic rename) or on operation failure
- **FR-083d**: System MUST fail write operation with error code `lock-timeout` if lock cannot be acquired within 10 seconds
- **FR-083e**: System MUST implement lock cleanup on abnormal termination (e.g., process crash) by releasing all locks on server restart
- **FR-084**: System MUST serialize write operations to the same document (only one write at a time per document)
- **FR-085**: System MUST allow concurrent read operations on the same document
- **FR-086**: System MUST allow concurrent operations on different documents without interference

#### Schema Resolution & Defaults

- **FR-087**: System MUST recursively resolve ALL $ref references during schema loading at server startup
- **FR-088**: System MUST merge default values from referenced schemas into the resolved schema tree
- **FR-089**: When initializing documents, system MUST collect defaults from the entire resolved schema tree (including $ref targets)
- **FR-090**: System MUST apply defaults consistently regardless of whether schema uses inline definitions or $ref composition
- **FR-091**: System MUST fail with clear error if $ref resolution encounters circular references or unresolvable references

#### Path Operations & Validation

- **FR-092**: System MUST NOT auto-create intermediate paths for nested operations
- **FR-093**: When path operation targets non-existent intermediate path (e.g., `/a/b/c` when `/a/b` doesn't exist), system MUST fail with error code `path-not-found`
- **FR-094**: Path error responses MUST include: requested path, deepest existing ancestor path, and guidance on which path to create first
- **FR-095**: System MUST require explicit path creation to make document evolution intentional and prevent accidental structure creation

#### Error Code Specification

- **FR-096**: System MUST define exhaustive enumeration of ALL possible error codes as versioned API contract
- **FR-097**: Each error code MUST include: machine-readable identifier (kebab-case string), HTTP-style category (4xx client/5xx server), description, typical causes, and remediation guidance
- **FR-098**: System MUST maintain error code stability across minor versions (no breaking changes to existing codes)
- **FR-099**: System MUST document all error codes in API specification with examples
- **FR-100**: New error codes MAY be added in minor versions; existing codes MUST NOT change meaning

#### Storage Directory Structure

- **FR-101**: System MUST use flat directory structure with all documents in single configured directory
- **FR-102**: System MUST store documents with filename pattern `{doc_id}.json` (e.g., `01JDEX3M8K2N9WPQR5STV6XY7Z.json`)
- **FR-103**: System MUST use `.tmp` suffix for temporary files during write operations (e.g., `{doc_id}.tmp`)
- **FR-104**: System MUST configure storage directory path at server startup (e.g., `./data/` or absolute path)
- **FR-105**: System MUST create storage directory if it doesn't exist at startup
- **FR-106**: System MUST validate storage directory is writable at startup and fail fast if not
- **FR-107**: Future optimization MAY introduce sharding subdirectories (e.g., first 2 chars of doc_id) when document count exceeds 10,000

#### Document ID Generation

- **FR-108**: System MUST use ULID (Universally Unique Lexicographically Sortable Identifier) format for auto-generated doc_id values
- **FR-109**: Generated doc_ids MUST be: 26-character case-insensitive encoding, timestamp-ordered (sortable by creation time), 128-bit random component for collision resistance
- **FR-110**: Generated doc_ids MUST be filesystem-safe (no special characters requiring escaping)
- **FR-111**: System MUST use standard ULID library for generation (not custom implementation)
- **FR-112**: Example valid doc_id: `01JDEX3M8K2N9WPQR5STV6XY7Z`

#### Transaction Boundaries

- **FR-113**: System MUST implement document-level atomic transactions (each document operation is an atomic unit)
- **FR-114**: System MUST NOT support cross-document transactions (no multi-document atomicity)
- **FR-115**: Write transaction workflow MUST follow: (1) Clone document in-memory, (2) Apply modification to clone, (3) Validate entire clone, (4) Write to `{doc_id}.tmp`, (5) fsync() for durability, (6) Atomic rename to `{doc_id}.json`
- **FR-116**: System MUST guarantee consistency at individual document level only
- **FR-117**: System MUST ensure each document operation either fully succeeds or fully fails (no partial modifications visible)

#### Dual Interface Architecture

- **FR-065**: System MUST provide TWO entry points: (1) MCP protocol server for agent/AI integrations, (2) OpenAPI REST API for traditional HTTP clients
- **FR-065a**: Both interfaces MUST expose identical functionality (all 8 operations available through both protocols)
- **FR-065b**: MCP server MUST run on stdio transport for agent integration
- **FR-065c**: REST API MUST run on HTTP with configurable port (default 8080)
- **FR-065d**: System MUST support running both interfaces simultaneously OR independently based on configuration

#### MCP Protocol Integration

- **FR-066**: System MUST expose all operations as MCP tools with JSON Schema input definitions
- **FR-067**: System MUST return results conforming to MCP response format
- **FR-068**: System MUST map errors to MCP error response structure with full validation reports
- **FR-069**: System MUST support MCP resource URIs for document access (e.g., `schema://doc_id` for full document export)
- **FR-069a**: Each MCP tool MUST declare its input schema including doc_id and path parameters
- **FR-069b**: Each MCP tool MUST declare its output schema for type-safe responses

#### REST API Integration

- **FR-070a**: System MUST provide OpenAPI 3.1 specification describing all REST endpoints
- **FR-070b**: System MUST serve Swagger UI at `/docs` endpoint for interactive API exploration
- **FR-070c**: System MUST serve ReDoc documentation at `/redoc` endpoint
- **FR-070d**: System MUST provide OpenAPI spec JSON at `/openapi.json` endpoint
- **FR-070e**: REST endpoints MUST map 1:1 to MCP tools with equivalent functionality
- **FR-070f**: REST API MUST use standard HTTP methods: POST for writes (create/update/delete), GET for reads
- **FR-070g**: REST API MUST return JSON responses with same structure as MCP tool outputs
- **FR-070h**: REST API MUST use standard HTTP status codes: 200 OK, 201 Created, 400 Bad Request, 404 Not Found, 409 Conflict, 422 Validation Error, 500 Internal Server Error
- **FR-070i**: REST API MUST support CORS for browser-based clients (configurable origins)

#### Type Safety

- **FR-071**: System MUST use Python 3.11+ for implementation with type hints and MyPy strict type checking enabled
- **FR-072**: System MUST define types (dataclasses, TypedDicts, Pydantic models) for all data structures from JSON schemas
- **FR-073**: System MUST validate Python types match runtime JSON schema validation
- **FR-074**: System MUST prevent use of `Any` type except where explicitly justified with mitigation
- **FR-075**: System MUST use type narrowing and isinstance() checks at all system boundaries

### Key Entities

- **Configuration**: Server configuration parameters loaded at startup from environment variables or JSON config file. Required: `schema_path` (path to JSON Schema file). Optional: `storage_dir` (document storage directory, default `./data`), `log_level` (logging verbosity, default `info`). Precedence order: environment variables override config file, config file overrides built-in defaults.

- **Document**: A JSON data structure instance conforming to a specific JSON schema, identified by unique doc_id (ULID format, 26 characters). Physical storage consists of TWO files: `{doc_id}.json` (content) and `{doc_id}.meta.json` (metadata including version counter, timestamps, schema reference). Version counter is stored in metadata file only, not in document content. Both files written atomically using write-then-rename strategy.

- **Schema**: A JSON Schema definition (Draft 2020-12) describing valid structure, types, and constraints for documents. Referenced by URI, contains validation rules, structural definitions, and default values. Server is initialized with exactly one schema at startup. All $ref references are recursively resolved during schema loading.

- **Path**: A JSON Pointer (RFC 6901) string identifying a specific location within a document's tree structure. Examples: `/`, `/metadata/title`, `/content/chapters/0/title`. Intermediate paths must exist; system does not auto-create missing paths.

- **Operation**: A typed CRUD action (Create, Read, Update, Delete, GetSchema) with parameters including doc_id, path, optional version (for writes), and optional data payload. Returns typed result with success/error status. Write operations are document-level atomic transactions.

- **ValidationError**: A structured error type containing: error code (kebab-case string), HTTP-style category (4xx/5xx), human message, JSON pointer to violation location, constraint violated, expected value/type, actual value provided, schema reference, and remediation guidance.

- **StorageAdapter**: An abstraction interface defining storage operations (save, load, delete, exists, list) independent of implementation. MVP uses file-based adapter with flat directory structure; future adapters will support cloud NoSQL databases.

- **Version**: Integer counter starting at 1 for newly created documents, incremented on every write operation. Used for optimistic locking - reads return current version, writes require matching version parameter. Prevents lost updates in concurrent scenarios. Version 0 never exists.

- **doc_id**: ULID (Universally Unique Lexicographically Sortable Identifier) - 26-character case-insensitive string, timestamp-ordered, filesystem-safe. Example: `01JDEX3M8K2N9WPQR5STV6XY7Z`. Auto-generated by document_create.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a schema-validated document and receive a unique identifier in under 500ms for documents up to 10MB
- **SC-002**: System rejects 100% of schema-invalid data with detailed error messages including JSON pointer to error location
- **SC-003**: Users can retrieve content at any path depth in under 100ms for documents up to 10MB
- **SC-004**: System maintains document validity - 100% of operations either complete successfully with valid result or fail completely with no partial changes (verified by: clone-validate-persist workflow, operations never leave documents in invalid state)
- **SC-004a**: Failed operations leave zero trace - original document unchanged in memory and on disk, no temporary state visible to other operations
- **SC-005**: Schema introspection returns fully resolved schema for any valid path in under 50ms
- **SC-006**: System handles 100 concurrent operations on different documents without performance degradation
- **SC-007**: Validation error messages enable users to fix issues without consulting external documentation (measured by: error message includes all necessary context - path, constraint, expected vs actual)
- **SC-008**: System validates against all schema constraints including: type, required fields, patterns, formats, min/max, enum, oneOf/anyOf/allOf
- **SC-009**: Zero data loss - all successfully completed operations persist across server restarts (verified by stopping/starting server and validating document integrity)
- **SC-010**: MCP protocol conformance verified by successful integration with standard MCP clients (Claude Desktop, Cline, etc.)
- **SC-011**: Client applications can export complete documents via MCP resource URIs independently of agent-driven path operations
- **SC-012**: Storage abstraction layer enables swapping file-based storage for cloud NoSQL without changing business logic (verified by interface compliance tests)

### Assumptions

- Server is initialized with a single, valid JSON schema before accepting any document operations
- All documents managed by a server instance conform to the same schema (single-schema architecture)
- Users requiring multiple schemas will run multiple server instances
- Doc_ids are auto-generated using ULID format by document_create (not provided by users)
- Local filesystem provides atomic rename operations for MVP write-then-rename strategy
- Network latency between MCP client and server is reasonable (<100ms)
- Configured JSON schema is valid per Draft 2020-12 specification
- Schema $ref references can be resolved (no circular references or broken URIs)
- Users understand JSON Pointer syntax or use tools that generate valid paths
- Users understand that intermediate paths must exist (no auto-creation)
- Concurrent operations on same document are relatively rare (optimistic locking acceptable)
- Agent operations focus on path-based incremental editing, not bulk document retrieval
- Client applications have mechanisms to handle complete document export separate from agent operations
- Local file system has sufficient storage capacity for document storage (MVP)
- File system permissions allow read/write operations in designated storage directory
- Storage directory can handle flat structure efficiently (up to ~10k documents before sharding needed)
- Schema changes are infrequent enough that server restarts are acceptable
- MVP performance acceptable without in-memory caching (documents read from disk on every operation)
- System is single-instance deployment (no distributed coordination required for MVP)

### Out of Scope

- Multi-schema support within single server instance (single-schema-per-instance design)
- Dynamic schema switching or runtime schema updates (requires server restart)
- Schema version migration tools (documents tied to schema version at server startup)
- Visual schema editor or JSON path builder UI
- Advanced query capabilities (filtering, searching across documents)
- Real-time collaborative editing with operational transforms
- Document versioning and history tracking
- Authentication and authorization (assumes trusted environment or external auth layer)
- Multi-document transactions (each operation is single-document scoped)
- Backup and restore utilities
- Schema registry or catalog management
- Custom validation keyword implementation
- Cloud storage implementation (deferred to post-MVP; abstraction layer prepared)
- Distributed locking or consensus mechanisms
- Replication or high-availability clustering
- Storage optimization (compression, deduplication)

### Post-MVP Enhancements

These features are deferred to future iterations after MVP validation. They represent optimizations and capabilities that can be added incrementally without breaking MVP functionality.

#### Performance & Scalability

- **In-memory document cache**: LRU cache for frequently accessed documents to reduce disk I/O. Considerations: cache size limits, eviction policy, memory pressure handling, cache coherency with file system. MVP reads from disk on every operation for simplicity.

- **Document metadata indexing**: In-memory index of document metadata (created_at, modified_at, doc_id) for fast `document_list` queries. MVP performs directory scan on every list operation. Post-MVP can maintain sorted index for efficient pagination and filtering.

- **Structural sharing for deep clone**: Instead of full document cloning, use immutable data structures with structural sharing to reduce memory footprint for large documents. MVP uses simple deep clone. Trade-off: complexity vs memory efficiency.

- **Validation timeout and limits**: Circuit breaker for validation operations to prevent DoS with pathological schemas. Add configurable timeout (e.g., 30s), max schema depth (e.g., 1000 levels), max document depth. MVP assumes well-behaved schemas.

#### Operations & Observability

- **Structured logging**: JSON-formatted logs with correlation IDs, request tracing, performance metrics. MVP uses simple console logging. Post-MVP needs log aggregation, rotation, filtering.

- **Health checks and metrics**: HTTP endpoints for liveness/readiness probes, Prometheus metrics for operation latency, error rates, document counts. Critical for production deployment.

- **Crash recovery algorithm**: Sophisticated startup recovery that compares `.tmp` file timestamps with `.json` files to recover interrupted writes. MVP simply deletes all `.tmp` files on startup (conservative but safe).

- **fsync() retry logic**: Exponential backoff retry on fsync failures, platform-specific error handling (Windows FlushFileBuffers vs POSIX fsync). MVP fails immediately on fsync error.

#### API & Features

- **Negative array indices**: Support Python-style negative indexing (`-1` = last element) as JSON Pointer extension. MVP strictly follows RFC 6901 (no negative indices).

- **MCP resource URI verification**: Validate `schema://doc_id` format against official MCP protocol specification for resource URIs. MVP uses assumed format.

- **JSON Schema format validators**: Document exhaustive list of supported `format` validators (email, uri, date-time, uuid, ipv4, ipv6, hostname, etc.) or reference validator library docs. MVP uses AJV defaults.

- **schema_get_node simplification**: Consider removing `doc_id` parameter from `schema_get_node` tool since schema is server-level (all docs share same schema). Requires API redesign discussion.

- **Batch operations**: Support for multi-document operations, bulk imports, batch validation. Improves efficiency for large-scale data migrations.

#### Advanced Features

- **Query and filtering**: JSONPath or GraphQL-style queries across multiple documents. Requires indexing infrastructure.

- **Document size limits**: Explicit max document size constraint (e.g., 50MB) with clear error messages. Prevents OOM crashes with pathological documents.

- **Real-time subscriptions**: WebSocket-based document change notifications for real-time collaboration. Significant architectural addition.

### Dependencies

- JSON Schema validation library supporting Draft 2020-12 (e.g., `jsonschema` for Python)
- JSON Pointer implementation (RFC 6901 compliant) - built into `jsonschema` library
- MCP Python SDK (`mcp` package)
- FastAPI framework for REST API implementation
- Uvicorn ASGI server for serving REST API
- ULID generator library for Python (e.g., `python-ulid` package)
- Python 3.11+ with async/await support
- Pydantic for configuration and data validation
- MyPy for static type checking

### Constraints

- Must conform to all principles in project constitution (schema-first, type safety, validation at boundaries, etc.)
- Must use Python 3.11+ with MyPy strict type checking
- Must validate all data against schemas at every boundary
- Must follow TDD approach (tests written and approved before implementation)
- Must provide BOTH MCP and REST interfaces with identical functionality
- Must handle documents as complete units (no partial document loading except via path operations)
- Must support schemas up to reasonable complexity (depth limits, reference limits to prevent DoS)
- Performance target: sub-second response for documents up to 10MB
- Storage implementation must use abstraction layer to enable future migration to cloud NoSQL
- MVP uses local file-based storage; production may require cloud storage migration
- REST API must be independently usable without MCP client (Swagger UI for testing)

## MCP Tools Specification

This section defines the MCP tools with semantically meaningful names that reflect the document-centric purpose and tree structure. All tools use consistent terminology: `document_*` for document operations, `schema_*` for schema introspection, and tree/node terminology for path-based operations.

### Tool: document_create

Creates a new empty document conforming to the server's configured schema and returns a unique doc_id. The document is initialized ONLY with fields that have explicit `default` values in the schema. If the schema has required fields without defaults, the operation fails with a clear error. Agents then use other CRUD operations to populate the document tree incrementally.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {}
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success", "doc_id"],
  "properties": {
    "success": { "type": "boolean" },
    "doc_id": { 
      "type": "string",
      "description": "Auto-generated unique document identifier"
    },
    "document_uri": { 
      "type": "string", 
      "format": "uri",
      "description": "URI to access the complete document"
    },
    "schema_uri": { 
      "type": "string", 
      "format": "uri",
      "description": "URI of the schema this document conforms to (server's configured schema)"
    },
    "initial_tree": {
      "type": "object",
      "description": "The document tree structure initialized with schema defaults only"
    },
    "version": {
      "type": "integer",
      "description": "Document version number, starts at 1, increments on every write operation"
    },
    "validation_report": {
      "type": "object",
      "required": ["valid"],
      "properties": {
        "valid": { "type": "boolean" },
        "error_count": { "type": "integer", "description": "Total number of validation errors" },
        "errors": { 
          "type": "array",
          "description": "Complete list of ALL validation errors. On creation failure, includes 'required-field-without-default' errors",
          "items": {
            "type": "object",
            "required": ["code", "message", "path"],
            "properties": {
              "code": { "type": "string", "description": "Machine-readable error code (e.g., 'required-field-without-default', 'type-mismatch')" },
              "message": { "type": "string", "description": "Human-readable error message explaining what's wrong and how to fix it" },
              "path": { "type": "string", "description": "JSON Pointer to the exact location of the error" },
              "constraint": { "type": "string", "description": "The schema constraint that was violated (e.g., 'required', 'type', 'minLength')" },
              "expected": { "description": "The expected value or format according to schema" },
              "actual": { "description": "The actual value provided that failed validation" }
            }
          }
        }
      }
    }
  }
}
```

---

### Tool: document_read_node

Retrieves content at a specified node (path) within the document tree.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["doc_id", "node_path"],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "Document identifier"
    },
    "node_path": {
      "type": "string",
      "pattern": "^/",
      "description": "JSON Pointer path to the node in the document tree (RFC 6901)"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success", "node_content", "version"],
  "properties": {
    "success": { "type": "boolean" },
    "node_content": {
      "description": "Content at the specified tree node, type varies based on schema"
    },
    "version": {
      "type": "integer",
      "description": "Current document version, use this in subsequent write operations for optimistic locking"
    },
    "node_type": {
      "type": "string",
      "enum": ["object", "array", "string", "number", "boolean", "null"],
      "description": "JSON type of the node"
    }
    }
  }
}
```

---

### Tool: schema_get_node

Returns JSON Schema definition for a specified node (path) within the document tree structure.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["doc_id", "node_path"],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "Document identifier"
    },
    "node_path": {
      "type": "string",
      "pattern": "^/",
      "description": "JSON Pointer path to the node in the document tree (RFC 6901)"
    },
    "dereferenced": {
      "type": "boolean",
      "default": true,
      "description": "Whether to resolve $ref references"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success", "node_schema"],
  "properties": {
    "success": { "type": "boolean" },
    "node_schema": {
      "type": "object",
      "description": "JSON Schema definition for the node at this path"
    },
    "node_exists": {
      "type": "boolean",
      "description": "Whether the node path exists in current document"
    }
  }
}
```

---

### Tool: document_update_node

Updates content at a specified node (path) in the document tree with validation.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["doc_id", "node_path", "node_data", "version"],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "Document identifier"
    },
    "node_path": {
      "type": "string",
      "pattern": "^/",
      "description": "JSON Pointer path to the node in the document tree (RFC 6901)"
    },
    "node_data": {
      "description": "New data for the node, must conform to schema for that location"
    },
    "version": {
      "type": "integer",
      "description": "Expected document version from previous read, operation fails if version has changed (optimistic locking)"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success"],
  "properties": {
    "success": { "type": "boolean" },
    "updated_node": {
      "description": "The updated content at the node"
    },
    "version": {
      "type": "integer",
      "description": "New document version after successful update (incremented from input version)"
    },
    "validation_report": {
      "type": "object",
      "required": ["valid"],
      "properties": {
        "valid": { "type": "boolean" },
        "error_count": { "type": "integer" },
        "errors": { 
          "type": "array",
          "description": "Complete list of ALL validation errors",
          "items": {
            "type": "object",
            "required": ["code", "message", "path"],
            "properties": {
              "code": { "type": "string" },
              "message": { "type": "string" },
              "path": { "type": "string" },
              "constraint": { "type": "string" },
              "expected": {},
              "actual": {}
            }
          }
        }
      }
    }
  }
}
```

---

### Tool: document_create_node

Creates new content at a specified node (path) in the document tree.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["doc_id", "node_path", "node_data", "version"],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "Document identifier"
    },
    "node_path": {
      "type": "string",
      "pattern": "^/",
      "description": "JSON Pointer path to the node in the document tree (RFC 6901), use /- for array append"
    },
    "node_data": {
      "description": "New data to create at the node, must conform to schema"
    },
    "version": {
      "type": "integer",
      "description": "Expected document version from previous read, operation fails if version has changed (optimistic locking)"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success"],
  "properties": {
    "success": { "type": "boolean" },
    "created_node_path": {
      "type": "string",
      "description": "Actual path where the node was created in the tree"
    },
    "created_node": {
      "description": "The created node content"
    },
    "version": {
      "type": "integer",
      "description": "New document version after successful create operation (incremented from input version)"
    },
    "validation_report": {
      "type": "object",
      "required": ["valid"],
      "properties": {
        "valid": { "type": "boolean" },
        "error_count": { "type": "integer" },
        "errors": { 
          "type": "array",
          "description": "Complete list of ALL validation errors",
          "items": {
            "type": "object",
            "required": ["code", "message", "path"],
            "properties": {
              "code": { "type": "string" },
              "message": { "type": "string" },
              "path": { "type": "string" },
              "constraint": { "type": "string" },
              "expected": {},
              "actual": {}
            }
          }
        }
      }
    }
  }
}
```

---

### Tool: document_delete_node

Deletes content at a specified node (path) in the document tree.

**Input Schema**:
```json
{
  "type": "object",
  "required": ["doc_id", "node_path", "version"],
  "properties": {
    "doc_id": {
      "type": "string",
      "description": "Document identifier"
    },
    "node_path": {
      "type": "string",
      "pattern": "^/",
      "description": "JSON Pointer path to the node in the document tree (RFC 6901)"
    },
    "version": {
      "type": "integer",
      "description": "Expected document version from previous read, operation fails if version has changed (optimistic locking)"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success"],
  "properties": {
    "success": { "type": "boolean" },
    "deleted_node": {
      "description": "The node content that was deleted from the tree"
    },
    "version": {
      "type": "integer",
      "description": "New document version after successful delete operation (incremented from input version)"
    },
    "validation_report": {
      "type": "object",
      "required": ["valid"],
      "properties": {
        "valid": { "type": "boolean" },
        "error_count": { "type": "integer" },
        "errors": { 
          "type": "array",
          "description": "Complete list of ALL validation errors (e.g., if deletion violates schema)",
          "items": {
            "type": "object",
            "required": ["code", "message", "path"],
            "properties": {
              "code": { "type": "string" },
              "message": { "type": "string" },
              "path": { "type": "string" },
              "constraint": { "type": "string" },
              "expected": {},
              "actual": {}
            }
          }
        }
      }
    }
  }
}
```

---

### Tool: document_list

Lists all documents managed by this server instance.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 1000,
      "default": 100
    },
    "offset": {
      "type": "integer",
      "minimum": 0,
      "default": 0
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success", "documents", "schema_uri"],
  "properties": {
    "success": { "type": "boolean" },
    "schema_uri": { 
      "type": "string",
      "description": "The schema URI configured for this server instance - all documents conform to this schema"
    },
    "documents": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "doc_id": { "type": "string" },
          "created_at": { "type": "string", "format": "date-time" },
          "modified_at": { "type": "string", "format": "date-time" },
          "tree_size_bytes": { 
            "type": "integer",
            "description": "Size of the document tree in bytes"
          }
        }
      }
    },
    "total_documents": { "type": "integer" },
    "has_more": { "type": "boolean" }
  }
}
```

---

### Tool: schema_get_root

Returns the root JSON Schema configured for this server instance (the schema that all documents conform to).

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "dereferenced": {
      "type": "boolean",
      "default": true,
      "description": "Whether to resolve $ref references"
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "required": ["success", "root_schema", "schema_uri"],
  "properties": {
    "success": { "type": "boolean" },
    "schema_uri": { 
      "type": "string",
      "format": "uri",
      "description": "URI of the configured root schema"
    },
    "root_schema": {
      "type": "object",
      "description": "The complete JSON Schema definition for the document tree root"
    },
    "schema_version": {
      "type": "string",
      "description": "Schema version information if available"
    }
  }
}
```

---

### Semantic Naming Conventions

The MCP tools use semantically meaningful names that reflect the document-centric purpose and tree structure:

**Tool Naming Patterns:**
- `document_*` - Operations on complete documents or document-level actions
- `schema_*` - Schema introspection operations

**Parameter Naming Conventions:**
- `doc_id` - Document identifier (consistent across all tools)
- `node_path` - JSON Pointer path to a specific node in the document tree
- `node_data` - Data for a tree node
- `document_tree` - The complete document structure
- `*_node` - Operations or values related to tree nodes
- `*_uri` - Resource URIs for documents and schemas
- `tree_size_bytes` - Size metrics use tree terminology

**Semantic Keywords:**
- **Document** - Emphasizes complete, managed documents (books, articles, etc.)
- **Tree/Node** - Reflects the hierarchical JSON structure
- **Path** - Indicates traversal through the tree structure
- **Schema** - Highlights schema-driven validation and type safety
- **Root** - Indicates the top-level schema or document structure

**Validation Error Reporting:**
- `validation_report` - Complete validation result with all errors
- `error_count` - Total number of validation errors found
- `code` - Machine-readable error code (e.g., 'type-mismatch', 'required-missing', 'required-field-without-default')
- `message` - Human-readable actionable error message
- `constraint` - The specific schema constraint violated
- `expected` - What the schema requires
- `actual` - What was provided

**Standard Error Codes:**

The system defines an exhaustive, versioned enumeration of ALL possible error codes. Each code includes machine-readable identifier, category, description, typical causes, and remediation.

**Client Errors (4xx category):**

- **`invalid-doc-id`** (400) - doc_id format is invalid or malformed
  - Causes: doc_id contains invalid characters, wrong length, or doesn't match ULID format
  - Remediation: Use only doc_id values returned by document_create; verify doc_id format matches ULID specification

- **`document-not-found`** (404) - Specified doc_id doesn't exist in storage
  - Causes: doc_id never created, or document was deleted
  - Remediation: Verify doc_id is correct; use document_list to see available documents; create new document with document_create

- **`path-not-found`** (404) - JSON Pointer path doesn't exist in document structure
  - Causes: Path references non-existent property or array index; intermediate paths missing
  - Remediation: Use document_read_node on parent path to verify structure; create missing intermediate paths explicitly; check for typos in path

- **`path-invalid`** (400) - JSON Pointer syntax is malformed
  - Causes: Path doesn't start with `/`; contains unescaped special characters; invalid array index
  - Remediation: Follow RFC 6901 JSON Pointer syntax; use `/` for root; escape `~` and `/` characters; use numeric array indices

- **`conflict`** (409) - Resource already exists at target path
  - Causes: Attempting document_create_node on path that already has content
  - Remediation: Use document_update_node to modify existing content; use document_read_node to check if path exists; delete existing content first if replacement intended

- **`version-conflict`** (409) - Document version has changed since read (optimistic locking conflict)
  - Causes: Another operation modified document between your read and write operations
  - Remediation: Re-read document with document_read_node to get current version and content; reapply your changes; retry write with new version

- **`lock-timeout`** (408) - Failed to acquire document lock within 10 seconds
  - Causes: Another write operation is taking too long; deadlock condition; system overload
  - Remediation: Retry operation after brief delay; check for long-running operations; investigate system performance

**Validation Errors (422 category):**

- **`required-field-without-default`** (422) - Schema has required field with no default value (document_create only)
  - Causes: JSON Schema defines required fields but doesn't provide default values for them
  - Remediation: Add default values to schema for all required fields; or change fields to optional; or provide initial values via document_update_node after creation

- **`type-mismatch`** (422) - Value type doesn't match schema type constraint
  - Causes: Providing string where number expected; object where array expected; etc.
  - Remediation: Check schema with schema_get_node; convert value to expected type; verify data structure matches schema definition

- **`required-missing`** (422) - Required field is missing from provided data
  - Causes: Update/create operation omits field marked as required in schema
  - Remediation: Include all required fields in operation; check schema with schema_get_node for required fields list; provide values for all required fields

- **`min-length`** / **`max-length`** (422) - String length constraint violated
  - Causes: String too short (below minLength) or too long (above maxLength)
  - Remediation: Check schema constraints; adjust string length to meet requirements; verify minLength/maxLength values in schema

- **`pattern-failed`** (422) - String doesn't match required regex pattern
  - Causes: String format incorrect according to schema pattern constraint
  - Remediation: Check schema pattern with schema_get_node; format string to match regex; verify pattern requirements

- **`enum-mismatch`** (422) - Value not in allowed enum values list
  - Causes: Provided value not one of the enumerated options in schema
  - Remediation: Check schema enum with schema_get_node; use exact value from enum list (case-sensitive); verify spelling

- **`min-items`** / **`max-items`** (422) - Array size constraint violated
  - Causes: Array has too few items (below minItems) or too many items (above maxItems)
  - Remediation: Check schema array constraints; adjust array size to meet requirements

- **`minimum`** / **`maximum`** (422) - Numeric value constraint violated
  - Causes: Number below minimum or above maximum allowed value
  - Remediation: Check schema numeric constraints; adjust value to valid range

- **`format-invalid`** (422) - String doesn't match required format (email, uri, date-time, etc.)
  - Causes: String format incorrect according to schema format specification
  - Remediation: Check schema format with schema_get_node; format string according to specification (ISO 8601 for dates, RFC 5321 for email, etc.)

- **`additional-properties-forbidden`** (422) - Object contains properties not defined in schema when additionalProperties: false
  - Causes: Providing extra fields not in schema when schema forbids additional properties
  - Remediation: Remove extra properties; check schema with schema_get_node for allowed properties; verify property names match schema exactly

**Server Errors (5xx category):**

- **`schema-load-failed`** (500) - Failed to load or parse JSON schema at server startup
  - Causes: Schema file not found; schema file contains invalid JSON; schema violates JSON Schema meta-schema
  - Remediation: Verify schema file path in configuration; validate schema file is well-formed JSON; validate schema against JSON Schema Draft 2020-12 meta-schema

- **`schema-resolution-failed`** (500) - Failed to resolve $ref references in schema
  - Causes: Circular $ref references; unresolvable $ref URIs; missing referenced schema definitions
  - Remediation: Check for circular references in schema; verify all $ref URIs resolve correctly; ensure referenced schemas are accessible

- **`storage-read-failed`** (500) - Failed to read document from storage
  - Causes: File system permissions; disk I/O error; corrupted document file
  - Remediation: Check file system permissions; verify disk health; check storage directory is readable; restore from backup if corrupted

- **`storage-write-failed`** (500) - Failed to write document to storage
  - Causes: Disk full; file system permissions; disk I/O error
  - Remediation: Check disk space; verify write permissions on storage directory; check disk health

- **`internal-error`** (500) - Unexpected internal server error
  - Causes: Unhandled exception; programming bug; system resource exhaustion
  - Remediation: Check server logs for details; report bug with reproduction steps; restart server if transient issue

**Error Response Format:**

All errors return structured format:
```json
{
  "error": {
    "code": "version-conflict",
    "category": "409",
    "message": "Document version has changed since read",
    "details": {
      "doc_id": "01JDEX3M8K2N9WPQR5STV6XY7Z",
      "expected_version": 5,
      "actual_version": 7,
      "path": "/metadata/title"
    },
    "remediation": "Re-read document to get current version, then retry operation"
  }
}
```

For validation errors with multiple violations, `details.violations` contains array of all errors:
```json
{
  "error": {
    "code": "validation-failed",
    "category": "422",
    "message": "Document validation failed with 3 errors",
    "details": {
      "violations": [
        {
          "code": "type-mismatch",
          "message": "Expected number, got string",
          "path": "/metadata/pageCount",
          "expected": "number",
          "actual": "string",
          "value": "not a number"
        },
        {
          "code": "required-missing",
          "message": "Required field 'author' is missing",
          "path": "/metadata",
          "required_fields": ["author"]
        },
        {
          "code": "pattern-failed",
          "message": "String doesn't match required pattern",
          "path": "/metadata/isbn",
          "pattern": "^[0-9]{13}$",
          "value": "invalid-isbn"
        }
      ]
    }
  }
}
```

These conventions ensure that tool names and parameters clearly communicate the system's purpose: managing complete documents with granular tree-based operations and comprehensive validation feedback.

---

## REST API Endpoints

The REST API provides HTTP/JSON access to all document operations with identical functionality to MCP tools. All endpoints are documented in OpenAPI 3.1 specification served at `/openapi.json`, with interactive documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Base URL

```
http://localhost:8080/api/v1
```

### Endpoint Summary

| Method | Endpoint | Description | MCP Tool Equivalent |
|--------|----------|-------------|---------------------|
| POST | `/documents` | Create new document | `document_create` |
| GET | `/documents/{doc_id}` | Read document node | `document_read_node` |
| PUT | `/documents/{doc_id}` | Update document node | `document_update_node` |
| POST | `/documents/{doc_id}/nodes` | Create node | `document_create_node` |
| DELETE | `/documents/{doc_id}/nodes` | Delete node | `document_delete_node` |
| GET | `/documents` | List all documents | `document_list` |
| GET | `/schema` | Get root schema | `schema_get_root` |
| GET | `/schema/node` | Get schema for path | `schema_get_node` |

### POST /documents - Create Document

Creates a new document with schema defaults.

**Request:**
```json
{}  // No body required
```

**Response (201 Created):**
```json
{
  "success": true,
  "doc_id": "01JDEX3M8K2N9WPQR5STV6XY7Z",
  "version": 1,
  "document_uri": "http://localhost:8080/api/v1/documents/01JDEX3M8K2N9WPQR5STV6XY7Z",
  "schema_uri": "file:///path/to/schema.json",
  "initial_tree": { /* schema defaults */ },
  "validation_report": { "valid": true, "error_count": 0, "errors": [] }
}
```

---

### GET /documents/{doc_id} - Read Document Node

Retrieves content at specified path.

**Query Parameters:**
- `path` (required): JSON Pointer path (e.g., `/metadata/title`)

**Response (200 OK):**
```json
{
  "success": true,
  "node_content": "My Book Title",
  "version": 5,
  "node_type": "string"
}
```

**Error Response (404 Not Found):**
```json
{
  "error": {
    "code": "path-not-found",
    "category": "404",
    "message": "Path not found: /metadata/nonexistent",
    "details": {
      "path": "/metadata/nonexistent",
      "deepest_ancestor": "/metadata"
    },
    "remediation": "Use GET /documents/{doc_id}?path=/metadata to verify structure"
  }
}
```

---

### PUT /documents/{doc_id} - Update Document Node

Updates content at specified path with validation.

**Query Parameters:**
- `path` (required): JSON Pointer path

**Request Body:**
```json
{
  "node_data": "Updated Title",
  "version": 5
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "updated_node": "Updated Title",
  "version": 6,
  "validation_report": { "valid": true, "error_count": 0, "errors": [] }
}
```

**Error Response (409 Conflict - Version Conflict):**
```json
{
  "error": {
    "code": "version-conflict",
    "category": "409",
    "message": "Document version has changed since read",
    "details": {
      "doc_id": "01JDEX3M8K2N9WPQR5STV6XY7Z",
      "expected_version": 5,
      "actual_version": 7
    },
    "remediation": "Re-read document to get current version, then retry operation"
  }
}
```

**Error Response (422 Unprocessable Entity - Validation Failed):**
```json
{
  "error": {
    "code": "validation-failed",
    "category": "422",
    "message": "Document validation failed with 2 errors",
    "details": {
      "violations": [
        {
          "code": "type-mismatch",
          "message": "Expected string, got number",
          "path": "/metadata/title",
          "constraint": "type",
          "expected": "string",
          "actual": 123
        }
      ]
    },
    "remediation": "Fix all validation errors listed in violations array"
  }
}
```

---

### POST /documents/{doc_id}/nodes - Create Node

Creates new content at specified path.

**Query Parameters:**
- `path` (required): JSON Pointer path (use `/-` for array append)

**Request Body:**
```json
{
  "node_data": { "title": "New Chapter", "content": "..." },
  "version": 5
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "created_node_path": "/chapters/3",
  "created_node": { "title": "New Chapter", "content": "..." },
  "version": 6,
  "validation_report": { "valid": true, "error_count": 0, "errors": [] }
}
```

---

### DELETE /documents/{doc_id}/nodes - Delete Node

Deletes content at specified path.

**Query Parameters:**
- `path` (required): JSON Pointer path

**Request Body:**
```json
{
  "version": 5
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "deleted_node": { "title": "Deleted Chapter", "content": "..." },
  "version": 6,
  "validation_report": { "valid": true, "error_count": 0, "errors": [] }
}
```

---

### GET /documents - List Documents

Lists all documents with pagination.

**Query Parameters:**
- `limit` (optional, default=100): Maximum results
- `offset` (optional, default=0): Offset for pagination

**Response (200 OK):**
```json
{
  "success": true,
  "schema_uri": "file:///path/to/schema.json",
  "documents": [
    {
      "doc_id": "01JDEX3M8K2N9WPQR5STV6XY7Z",
      "created_at": "2025-11-29T10:00:00Z",
      "modified_at": "2025-11-29T11:30:00Z",
      "tree_size_bytes": 45623
    }
  ],
  "total_documents": 42,
  "has_more": true
}
```

---

### GET /schema - Get Root Schema

Returns the server's configured root schema.

**Query Parameters:**
- `dereferenced` (optional, default=true): Whether to resolve $ref

**Response (200 OK):**
```json
{
  "success": true,
  "schema_uri": "file:///path/to/schema.json",
  "root_schema": { /* JSON Schema */ },
  "schema_version": "1.0.0"
}
```

---

### GET /schema/node - Get Schema for Path

Returns schema definition for specific path.

**Query Parameters:**
- `doc_id` (required): Document identifier
- `path` (required): JSON Pointer path
- `dereferenced` (optional, default=true): Whether to resolve $ref

**Response (200 OK):**
```json
{
  "success": true,
  "node_schema": {
    "type": "string",
    "minLength": 1,
    "maxLength": 200
  },
  "node_exists": true
}
```

---

### Health & Documentation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (returns `{"status": "healthy"}`) |
| GET | `/docs` | Swagger UI interactive documentation |
| GET | `/redoc` | ReDoc API documentation |
| GET | `/openapi.json` | OpenAPI 3.1 specification |

---

### HTTP Status Code Mapping

| Status | Usage |
|--------|-------|
| 200 OK | Successful read/update/delete |
| 201 Created | Successful document/node creation |
| 400 Bad Request | Invalid request format, invalid JSON Pointer |
| 404 Not Found | Document not found, path not found |
| 408 Request Timeout | Lock acquisition timeout |
| 409 Conflict | Version conflict, resource already exists |
| 422 Unprocessable Entity | Validation failed |
| 500 Internal Server Error | Server errors (schema load, storage failure) |

---

### CORS Configuration

REST API supports CORS for browser-based clients:

```python
# Configurable via environment variables
CORS_ORIGINS=["http://localhost:3000", "https://app.example.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET", "POST", "PUT", "DELETE"]
CORS_ALLOW_HEADERS=["*"]
```

---

## Constitutional Compliance

This specification adheres to the project constitution:

- **Schema-First Design**: All operations defined by JSON schemas; MCP tool and REST endpoint schemas specified; Server initialized with single schema
- **Type Safety**: All data structures defined with strict types; Python implementation required with type hints
- **CRUD Operations as Primitives**: Eight atomic operations defined with clear input/output contracts, accessible via both MCP and REST
- **Validation at Boundaries**: Explicit validation requirements at every operation boundary (both interfaces)
- **Test-First**: Acceptance scenarios provided for every user story; ready for test implementation
- **Dual Protocol Compliance**: All operations exposed as MCP tools AND REST endpoints with identical functionality
- **Composability**: Each tool/endpoint has single responsibility; operations can be chained

## Next Steps

1. Review this specification for completeness and clarity
2. Create quality checklist to validate spec meets all requirements
3. If approved, proceed to implementation planning for dual-interface architecture
4. Write tests based on acceptance scenarios before implementation (test both MCP and REST interfaces)
5. Generate Pydantic models from all JSON schemas for type safety across both interfaces
6. Implement MCP server and REST API following TDD approach with shared business logic layer
