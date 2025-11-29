<!--
Sync Impact Report:
Version: 0.0.0 → 1.0.0
Modifications:
  - Initial constitution creation for JSON Schema MCP Tool
  - Established 7 core principles for strongly-typed schema operations
  - Added Type Safety & Schema Enforcement section
  - Added Development Standards section
Templates Status:
  - ⚠ plan-template.md: Requires review for schema validation steps
  - ⚠ spec-template.md: Requires review for type safety requirements
  - ⚠ tasks-template.md: Requires review for schema testing tasks
Follow-up TODOs: None
-->

# JSON Schema MCP Tool Constitution

## Core Principles

### I. Schema-First Design (NON-NEGOTIABLE)
Every operation MUST be defined by a JSON Schema before implementation. All data structures, API inputs, and outputs are governed by explicit schemas. No untyped or loosely typed operations are permitted. Schemas MUST be:
- Valid JSON Schema Draft 2020-12 or later
- Self-documenting with title, description, and examples
- Versioned and tracked in source control
- Validated on every operation

**Rationale**: Type safety is the foundation of reliability. Schemas serve as contracts that prevent runtime errors and enable automatic validation.

### II. Type Safety Throughout the Stack
Strong typing MUST be enforced at every layer:
- **Schema Layer**: JSON Schema definitions with strict validation
- **Runtime Layer**: Type guards and validation at all boundaries
- **API Layer**: MCP protocol messages with typed parameters and results
- **Storage Layer**: Schema-validated persistence operations

TypeScript/static typing MUST be used for implementation. Any `any` type usage requires explicit justification and mitigation plan.

**Rationale**: Catching errors at compile-time and validation-time prevents data corruption and reduces debugging cycles.

### III. CRUD Operations as Typed Primitives
All CRUD operations MUST be implemented as strongly-typed, atomic primitives:
- **Create**: Schema-validated insertion with conflict detection
- **Read**: Type-safe queries with schema-conformant results
- **Update**: Validated mutations with schema version compatibility checks
- **Delete**: Safe removal with referential integrity validation

Each operation MUST return typed results including success/failure status and validation errors. No silent failures permitted.

**Rationale**: Predictable, well-defined operations enable reliable automation and integration.

### IV. Schema Validation at Every Boundary
Validation MUST occur at every system boundary:
- Input validation before any processing
- Output validation before any response
- Storage validation before persistence
- Retrieval validation after loading

Failed validation MUST:
- Halt the operation immediately
- Return detailed, actionable error messages
- Log the violation with full context
- Never partially apply changes

**Rationale**: Defense-in-depth prevents invalid data from propagating through the system.

### V. Test-First with Schema Coverage (NON-NEGOTIABLE)
TDD is mandatory with specific requirements:
- Write schemas FIRST, before any implementation
- Write tests for schema validation SECOND
- Ensure tests fail for invalid data and pass for valid data
- Achieve 100% schema coverage (every field tested)
- Test edge cases, boundaries, and error conditions
- User approval of schemas and tests required BEFORE implementation

**Rationale**: Schemas are the specification. Tests prove the implementation honors the specification.

### VI. MCP Protocol Compliance
All tool operations MUST conform to Model Context Protocol standards:
- Tools defined with JSON Schema for input parameters
- Results returned as typed JSON conforming to declared schemas
- Error handling follows MCP error response format
- Resource operations support standard MCP resource URIs
- Prompts and sampling requests properly typed

**Rationale**: Protocol compliance ensures interoperability with MCP clients and servers.

### VII. Composability and Modularity
Components MUST be designed for composition:
- Each module has a single, well-defined responsibility
- Schemas can reference other schemas via $ref
- Operations can be chained with type-safe pipelines
- Libraries are independently testable
- Clear interfaces between all components

**Rationale**: Modular design enables reuse, testing, and maintenance.

## Type Safety & Schema Enforcement

### Schema Definition Standards
All schemas MUST include:
- `$schema` field specifying JSON Schema version
- `$id` field with unique identifier
- `title` and `description` fields
- Type definitions for all properties
- Required vs optional field declarations
- Validation constraints (format, pattern, min/max, etc.)
- Examples demonstrating valid instances

### Validation Implementation
- Use established JSON Schema validators (ajv, jsonschema, etc.)
- Cache compiled validators for performance
- Provide detailed error messages with JSON pointers
- Support custom validation keywords when necessary
- Validate recursively for nested structures

### Type Generation
- Generate TypeScript types from schemas automatically
- Maintain bidirectional sync between schemas and types
- Use code generation tools (json-schema-to-typescript, etc.)
- Include generated types in version control
- Validate generation pipeline in CI/CD

## Development Standards

### Code Organization
```
/schemas       - JSON Schema definitions
/types         - Generated TypeScript types
/validators    - Schema validation utilities
/operations    - CRUD operation implementations
/mcp           - MCP protocol integration
/tests         - Test suites organized by operation
```

### Testing Requirements
- Unit tests for each CRUD operation
- Integration tests for operation chains
- Schema validation tests (positive and negative cases)
- Property-based testing for schema constraints
- Performance tests for large datasets
- MCP protocol conformance tests

### Documentation Requirements
- README with quick start guide
- API documentation generated from schemas
- Examples for each operation type
- Error handling guide
- Schema versioning and migration guide
- MCP tool registration examples

### Error Handling
All errors MUST:
- Use typed error classes/interfaces
- Include error codes for programmatic handling
- Provide human-readable messages
- Contain context (operation, input, validation failures)
- Follow MCP error response format when applicable
- Never expose internal implementation details

## Governance

### Constitutional Authority
This constitution supersedes all other development practices and guidelines. Any code, design, or practice that conflicts with these principles MUST be rejected or amended.

### Amendment Process
Constitution amendments require:
1. Documented rationale and impact analysis
2. Team review and approval
3. Version increment (MAJOR for breaking changes, MINOR for additions, PATCH for clarifications)
4. Migration plan for existing code
5. Update to all dependent templates and documentation

### Compliance Verification
- All code reviews MUST verify constitutional compliance
- CI/CD pipelines MUST enforce schema validation
- Pre-commit hooks SHOULD run type checking and validation
- Regular audits to identify compliance gaps
- Automated tools to detect violations where possible

### Versioning Policy
Version format: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes to schemas, APIs, or core principles
- MINOR: New schemas, operations, or capabilities
- PATCH: Bug fixes, performance improvements, clarifications

Schema versions follow the same semantic versioning rules and MUST be tracked independently.

### Complexity Justification
Any deviation from simplicity (complex validation logic, performance optimizations, etc.) MUST be:
- Documented with rationale
- Justified by measurable requirements
- Reviewed and approved
- Covered by comprehensive tests

**Version**: 1.0.0 | **Ratified**: 2025-11-29 | **Last Amended**: 2025-11-29
