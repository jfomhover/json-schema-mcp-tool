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

1. **Given** the server is initialized with a JSON schema, **When** agent calls document_create with no arguments, **Then** system generates a unique doc_id, creates a minimal valid document (empty object or schema defaults), and returns the doc_id
2. **Given** a schema with required fields, **When** agent creates a new document, **Then** system initializes those required fields with default values or null placeholders that pass minimal validation
3. **Given** a schema with default values specified, **When** agent creates a new document, **Then** system initializes the document with those schema-defined defaults
4. **Given** multiple sequential document_create calls, **When** agent creates documents, **Then** each returns a unique doc_id with no collisions
5. **Given** a newly created document, **When** agent queries its content at root path "/", **Then** system returns the minimal initialized structure that is schema-valid

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

1. **Given** a document exists, **When** user updates path "/metadata/title" with valid string, **Then** system validates against schema, persists change, and returns success with updated content
2. **Given** a document exists, **When** user updates with invalid data type (e.g., number where string expected), **Then** system rejects with detailed validation error
3. **Given** a required field in schema, **When** user attempts to update to null or undefined, **Then** system rejects with required field violation error
4. **Given** an update to nested path, **When** parent path doesn't exist, **Then** system either creates parent structure (if schema allows) or returns error
5. **Given** an array field, **When** user updates specific index, **Then** system validates array item against schema and persists change
6. **Given** update violates schema constraints (min/max length, pattern, format), **When** validation fails, **Then** system returns specific constraint violation details
7. **Given** concurrent updates to same document, **When** both updates conflict, **Then** system handles according to conflict resolution strategy (optimistic locking, last-write-wins)

---

### User Story 5 - Create New Content at Path (Priority: P3)

A user wants to add new content to an existing document at a specific path, such as appending a new chapter to a book or adding a new property.

**Why this priority**: This complements update operations by allowing additive changes. Less critical than update because update can sometimes achieve similar results, but important for array operations and optional fields.

**Independent Test**: Can be tested by creating base document, then using create operation to add new elements (array items, optional fields) and verifying schema validation and persistence.

**Acceptance Scenarios**:

1. **Given** a document with an array field, **When** user creates new item in array (e.g., "/content/chapters/-"), **Then** system validates new item against array item schema and appends to array
2. **Given** a path to optional property that doesn't exist, **When** user creates content at that path, **Then** system validates against schema and adds the property
3. **Given** a path that already exists, **When** user attempts to create, **Then** system returns conflict error
4. **Given** a create operation with invalid data, **When** validation fails, **Then** system returns detailed validation errors without modifying document
5. **Given** nested path where intermediary paths don't exist, **When** user creates, **Then** system either auto-creates intermediate structure or returns error based on schema additionalProperties settings

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

- What happens when a JSON path references an array element that is out of bounds?
  - System returns "index out of bounds" error with current array length
- How does system handle very large documents (>100MB) in memory?
  - System uses streaming validation for large documents and path-based access to avoid loading entire document into agent context
- What happens when an agent tries to read the root path of a very large document?
  - System returns the full document but warns that for large documents, agents should use specific paths; client applications should use the export mechanism (MCP resource URI)
- What happens when schema file is modified while server is running?
  - Server continues using the loaded schema in memory; schema changes require server restart
- What if users need to manage documents with different schemas?
  - They must run separate server instances, each initialized with a different schema
- How does system handle schema validation timeouts for complex schemas?
  - Configurable timeout with graceful error reporting; validation complexity limits documented
- What happens when JSON path contains special characters or escape sequences?
  - System uses RFC 6901 (JSON Pointer) standard encoding/decoding
- How are concurrent operations on the same document serialized?
  - Document-level locking with configurable timeout; operations queue or fail-fast based on configuration
- What happens if storage backend becomes unavailable during operation?
  - Operation fails with storage error; no partial writes; transaction rollback where supported
- How does system validate circular references in schemas?
  - Schema validation detects circular $ref chains; runtime validation handles recursive structures with depth limits
- How do client applications export complete documents after agent editing?
  - Client applications use MCP resource URIs (e.g., `schema://doc_id`) or direct file access when sharing storage layer with server
- What happens if the storage directory doesn't exist or lacks write permissions?
  - System initialization fails with clear error message; storage directory must be created and writable before server starts
- How does the storage abstraction layer ensure future cloud migration compatibility?
  - Storage interface defines all CRUD operations independently of implementation; local file storage is one implementation; future cloud NoSQL implementations will satisfy same interface
- What happens if server is started without a schema configuration?
  - Server fails to start with error message requiring schema file path in configuration

## Requirements *(mandatory)*

### Functional Requirements

#### Server Initialization & Schema Configuration

- **FR-001**: System MUST be initialized with a single JSON schema at server startup
- **FR-002**: System MUST load schema from file path specified in server configuration
- **FR-003**: System MUST validate the schema itself is valid JSON Schema Draft 2020-12 before accepting it
- **FR-004**: System MUST fail to start if schema file is missing, unreadable, or invalid
- **FR-005**: System MUST use the configured schema for ALL document operations within that server instance
- **FR-006**: System MUST NOT allow schema changes while server is running (require restart with new schema)
- **FR-007**: System MUST provide mechanism to query the currently configured schema URI and metadata

#### Document Lifecycle

- **FR-008**: System MUST support creating a new document instance with no input arguments, auto-generating a unique doc_id
- **FR-009**: System MUST initialize new documents with minimal valid content (empty object or schema defaults) that passes schema validation
- **FR-010**: System MUST auto-generate doc_ids that are unique, URL-safe strings with minimum 8 characters, maximum 256 characters
- **FR-011**: System MUST persist documents durably (survive server restart)
- **FR-012**: System MUST return the auto-generated doc_id immediately upon document creation
- **FR-013**: System MUST automatically apply the server's configured schema to all new documents (no per-document schema selection)
- **FR-014**: System MUST implement storage through an abstraction layer/interface to enable future migration from local to cloud storage

#### Storage Implementation (MVP)

- **FR-015**: System MUST use local file-based storage for MVP implementation
- **FR-016**: System MUST store each document as a separate JSON file in a structured directory
- **FR-017**: System MUST use auto-generated doc_id as filename (with .json extension), ensuring filesystem-safe characters
- **FR-018**: System MUST implement atomic file write operations to prevent corruption
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

- **FR-041**: System MUST validate update data against schema for target path before applying changes
- **FR-042**: System MUST support atomic updates (all-or-nothing - no partial updates on validation failure)
- **FR-043**: System MUST preserve document validity after updates (entire document validates against schema)
- **FR-044**: System MUST prevent updates that would violate required field constraints
- **FR-045**: System MUST prevent updates that would violate type constraints
- **FR-046**: System MUST support updating nested paths, including array elements
- **FR-047**: System MUST return both validation errors and updated content structure on successful update

#### Create Operations

- **FR-048**: System MUST support creating new content at paths that don't exist (if schema allows)
- **FR-049**: System MUST support appending to arrays using JSON Pointer append notation (`/-`)
- **FR-050**: System MUST validate created content against schema before persistence
- **FR-051**: System MUST reject create operations when path already exists (conflict)
- **FR-052**: System MUST support creating nested structures when parent paths allow additional properties

#### Delete Operations

- **FR-053**: System MUST support deleting content at optional paths
- **FR-054**: System MUST prevent deletion of required fields
- **FR-055**: System MUST validate remaining document structure after deletion
- **FR-056**: System MUST prevent deletions that would violate schema constraints (e.g., minItems)
- **FR-057**: System MUST support deleting array elements with automatic reindexing

#### Validation & Error Handling

- **FR-058**: System MUST use JSON Schema Draft 2020-12 or later for validation
- **FR-059**: System MUST provide detailed validation errors with JSON Pointer to specific failed constraint
- **FR-060**: System MUST return error messages including: error code, human-readable message, JSON path, schema constraint violated, and actual value provided
- **FR-061**: System MUST validate at every boundary: input validation, pre-persistence validation, post-retrieval validation
- **FR-062**: System MUST fail fast on validation errors (halt immediately, return detailed error)
- **FR-063**: System MUST log all validation failures with full context

#### MCP Protocol Integration

- **FR-064**: System MUST expose all operations as MCP tools with JSON Schema input definitions
- **FR-065**: System MUST return results conforming to MCP response format
- **FR-066**: System MUST map errors to MCP error response structure
- **FR-067**: System MUST support MCP resource URIs for document access (e.g., `schema://doc_id` for full document export)
- **FR-068**: Each MCP tool MUST declare its input schema including doc_id and path parameters
- **FR-069**: Each MCP tool MUST declare its output schema for type-safe responses

#### Type Safety

- **FR-070**: System MUST use TypeScript for implementation with strict type checking enabled
- **FR-071**: System MUST generate TypeScript types from JSON schemas for all data structures
- **FR-072**: System MUST validate TypeScript types match runtime JSON schema validation
- **FR-073**: System MUST prevent use of `any` type except where explicitly justified with mitigation
- **FR-074**: System MUST use type guards at all system boundaries

### Key Entities

- **Document**: A JSON data structure instance conforming to a specific JSON schema, identified by unique doc_id (string). Contains metadata (schema reference, creation time, last modified) and content (the actual JSON data tree). Stored as individual JSON file in MVP implementation.

- **Schema**: A JSON Schema definition (Draft 2020-12) describing valid structure, types, and constraints for documents. Referenced by URI, contains validation rules and structural definitions. Server is initialized with exactly one schema.

- **Path**: A JSON Pointer (RFC 6901) string identifying a specific location within a document's tree structure. Examples: `/`, `/metadata/title`, `/content/chapters/0/title`.

- **Operation**: A typed CRUD action (Create, Read, Update, Delete, GetSchema) with parameters including doc_id, path, and optional data payload. Returns typed result with success/error status.

- **ValidationError**: A structured error type containing: error code, human message, JSON pointer to violation location, constraint violated, expected value/type, actual value provided, and schema reference.

- **StorageAdapter**: An abstraction interface defining storage operations (save, load, delete, exists, list) independent of implementation. MVP uses file-based adapter; future adapters will support cloud NoSQL databases.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a schema-validated document and receive a unique identifier in under 500ms for documents up to 10MB
- **SC-002**: System rejects 100% of schema-invalid data with detailed error messages including JSON pointer to error location
- **SC-003**: Users can retrieve content at any path depth in under 100ms for documents up to 10MB
- **SC-004**: System maintains document validity - 100% of operations either complete successfully with valid result or fail completely with no partial changes
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
- Doc_ids are managed by users (system doesn't auto-generate unless requested)
- Local filesystem provides atomic write operations for MVP
- Network latency between MCP client and server is reasonable (<100ms)
- Configured JSON schema is valid per Draft 2020-12 specification
- Users understand JSON Pointer syntax or use tools that generate valid paths
- Concurrent operations on same document are relatively rare (optimistic locking acceptable)
- Agent operations focus on path-based incremental editing, not bulk document retrieval
- Client applications have mechanisms to handle complete document export separate from agent operations
- Local file system has sufficient storage capacity for document storage (MVP)
- File system permissions allow read/write operations in designated storage directory
- Schema changes are infrequent enough that server restarts are acceptable

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

### Dependencies

- JSON Schema validation library (e.g., AJV, Hyperjson, or similar) supporting Draft 2020-12
- JSON Pointer implementation (RFC 6901 compliant)
- MCP SDK/library for TypeScript
- Node.js filesystem APIs for local file-based storage (MVP)
- TypeScript compiler with strict mode
- JSON Schema to TypeScript type generator

### Constraints

- Must conform to all principles in project constitution (schema-first, type safety, validation at boundaries, etc.)
- Must use TypeScript with strict type checking
- Must validate all data against schemas at every boundary
- Must follow TDD approach (tests written and approved before implementation)
- Must use MCP protocol exclusively for external interface (no REST/GraphQL/other APIs)
- Must handle documents as complete units (no partial document loading except via path operations)
- Must support schemas up to reasonable complexity (depth limits, reference limits to prevent DoS)
- Performance target: sub-second response for documents up to 10MB
- Storage implementation must use abstraction layer to enable future migration to cloud NoSQL
- MVP uses local file-based storage; production may require cloud storage migration

## MCP Tools Specification

This section defines the MCP tools with semantically meaningful names that reflect the document-centric purpose and tree structure. All tools use consistent terminology: `document_*` for document operations, `schema_*` for schema introspection, and tree/node terminology for path-based operations.

### Tool: document_create

Creates a new empty document conforming to the server's configured schema and returns a unique doc_id. The document is initialized with minimal valid content (empty object or schema defaults). Agents then use other CRUD operations to populate the document tree incrementally.

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
      "description": "The minimal initial document tree structure (e.g., {} or schema defaults)"
    }
    "validationResult": {
      "type": "object",
      "properties": {
        "valid": { "type": "boolean" },
        "errors": { "type": "array" }
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
  "required": ["success", "node_content"],
  "properties": {
    "success": { "type": "boolean" },
    "node_content": {
      "description": "Content at the specified tree node, type varies based on schema"
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
  "required": ["doc_id", "node_path", "node_data"],
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
    "validationResult": {
      "type": "object",
      "properties": {
        "valid": { "type": "boolean" },
        "errors": { "type": "array" }
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
  "required": ["doc_id", "node_path", "node_data"],
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
    "validationResult": {
      "type": "object",
      "properties": {
        "valid": { "type": "boolean" },
        "errors": { "type": "array" }
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
  "required": ["success"],
  "properties": {
    "success": { "type": "boolean" },
    "deleted_node": {
      "description": "The node content that was deleted from the tree"
    },
    "validationResult": {
      "type": "object",
      "properties": {
        "valid": { "type": "boolean" },
        "errors": { "type": "array" }
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

These conventions ensure that tool names and parameters clearly communicate the system's purpose: managing complete documents with granular tree-based operations.

---

## Constitutional Compliance

This specification adheres to the project constitution:

- **Schema-First Design**: All operations defined by JSON schemas; MCP tool input/output schemas specified; Server initialized with single schema
- **Type Safety**: All data structures defined with strict types; TypeScript implementation required
- **CRUD Operations as Primitives**: Eight atomic operations defined with clear input/output contracts
- **Validation at Boundaries**: Explicit validation requirements at every operation boundary
- **Test-First**: Acceptance scenarios provided for every user story; ready for test implementation
- **MCP Protocol Compliance**: All operations exposed as MCP tools with proper schema definitions
- **Composability**: Each tool has single responsibility; operations can be chained

## Next Steps

1. Review this specification for completeness and clarity
2. Create quality checklist to validate spec meets all requirements
3. If approved, proceed to `/speckit.plan` to create technical implementation plan
4. Write tests based on acceptance scenarios before implementation
5. Generate TypeScript types from all JSON schemas
6. Implement MCP server following TDD approach
