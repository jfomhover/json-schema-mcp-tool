# 📋 JSON Schema MCP Tool

> **A powerful Model Context Protocol (MCP) server for managing JSON documents with schema validation**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0.0-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

## 🌟 Overview

**JSON Schema MCP Tool** is a production-ready Model Context Protocol server that provides comprehensive CRUD operations for JSON documents with built-in JSON Schema validation. It enables AI assistants like Claude to create, read, update, and manage structured documents with strict schema enforcement.

### ✨ Key Features

- 🔒 **Schema-First Design** - Every document is validated against a JSON Schema
- 🔄 **Optimistic Locking** - Version-based concurrency control prevents conflicts
- 🔍 **Schema Introspection** - Query and explore schema definitions at runtime

## 🏗️ Architecture

```
json-schema-mcp-tool/
├── apps/
│   └── mcp_server/          # MCP interface layer (thin adapter)
│       ├── server.py         # MCPServer implementation
│       └── tools/            # MCP tool definitions
│           ├── document_tools.py  # CRUD operations
│           └── schema_tools.py    # Schema introspection
├── lib/
│   └── json_schema_core/    # Core business logic (reusable)
│       ├── domain/           # Domain models and errors
│       ├── services/         # Business services
│       │   ├── document_service.py
│       │   ├── schema_service.py
│       │   └── validation_service.py
│       ├── storage/          # Storage abstraction
│       └── utils/            # JSON Pointer utilities
└── tests/                   # Comprehensive test suite
```

Future: `apps/rest_api/` - Thin REST adapter (same core library)

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (required)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jfomhover/json-schema-mcp-tool.git
   cd json-schema-mcp-tool
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install the package**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies** (optional)
   ```bash
   pip install -e ".[dev]"
   ```

5. **Verify installation**
   ```bash
   pytest tests/ -v
   ```

   You should see all tests passing ✅

## 🔧 Configuration for VS Code

### Option 1: Using Claude Dev Extension

1. **Install Claude Dev** extension in VS Code

2. **Open MCP Settings**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
   - Type "MCP: Edit Config"
   - Select the command to open your MCP configuration

3. **Add the server configuration**

   For **Windows** (PowerShell):
   ```json
   {
     "mcpServers": {
       "json-schema-tool": {
         "command": "powershell",
         "args": [
           "-ExecutionPolicy",
           "Bypass",
           "-Command",
           "& 'C:\\Users\\<YOUR_USERNAME>\\path\\to\\json-schema-mcp-tool\\.venv\\Scripts\\Activate.ps1'; python -m apps.mcp_server"
         ],
         "cwd": "C:\\Users\\<YOUR_USERNAME>\\path\\to\\json-schema-mcp-tool",
         "env": {}
       }
     }
   }
   ```

   For **macOS/Linux**:
   ```json
   {
     "mcpServers": {
       "json-schema-tool": {
         "command": "/absolute/path/to/json-schema-mcp-tool/.venv/bin/python",
         "args": ["-m", "apps.mcp_server"],
         "cwd": "/absolute/path/to/json-schema-mcp-tool",
         "env": {}
       }
     }
   }
   ```

4. **Reload VS Code**
   - Press `Ctrl+Shift+P` / `Cmd+Shift+P`
   - Type "Developer: Reload Window"

5. **Verify the connection**
   - Open a new chat with Claude
   - Ask: "Can you list the available MCP tools?"
   - You should see `document_create`, `document_read_node`, etc.

### Option 2: Using Claude Desktop App

1. **Locate your Claude config file**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add the server** (same configuration as above)

3. **Restart Claude Desktop**

## 📚 Available MCP Tools

### Document Operations

#### `document_create`
Creates a new document with auto-generated ID and applies schema defaults.

**Parameters**: None (empty document is created with defaults)  
**Returns**: `{"doc_id": "...", "version": 1}`

```python
# Example: Claude creates a document
> "Create a new document"
✓ Document created with ID: 01JFKX7G8H2M4K6QPBWNZ5VRTC
```

#### `document_read_node`
Reads a document or a specific node within it using JSON Pointer paths.

**Parameters**:
- `doc_id` (string): Document ID
- `node_path` (string): JSON Pointer path (e.g., "/", "/title", "/sections/0")

**Returns**: `{"content": {...}, "version": N}`

```python
# Example: Read entire document
> "Show me document 01JFKX7G8H2M4K6QPBWNZ5VRTC"

# Example: Read specific field
> "What's the title of document 01JFKX7G8H2M4K6QPBWNZ5VRTC?"
```

#### `document_update_node`
Updates a specific node in a document with optimistic locking.

**Parameters**:
- `doc_id` (string): Document ID
- `node_path` (string): JSON Pointer path
- `value` (any): New value
- `expected_version` (int): Current version for conflict detection

**Returns**: `{"content": {...}, "version": N+1}`

```python
# Example: Update the title
> "Change the title to 'My New Title' in document 01JFKX7G8H2M4K6QPBWNZ5VRTC"
```

#### `document_create_node`
Appends a new item to an array or adds a property to an object.

**Parameters**:
- `doc_id` (string): Document ID
- `node_path` (string): Path to parent array/object
- `value` (any): Value to add
- `expected_version` (int): Current version

**Returns**: `{"created_path": "...", "version": N+1}`

```python
# Example: Add a tag
> "Add tag 'python' to document 01JFKX7G8H2M4K6QPBWNZ5VRTC"
```

#### `document_delete_node`
Deletes a node from a document (validates the result).

**Parameters**:
- `doc_id` (string): Document ID
- `node_path` (string): Path to node to delete
- `expected_version` (int): Current version

**Returns**: `{"content": deleted_value, "version": N+1}`

#### `document_list`
Lists all documents with metadata and pagination.

**Parameters**:
- `limit` (int, default: 100): Max documents to return
- `offset` (int, default: 0): Number to skip

**Returns**: `{"documents": [{metadata}, ...]}`

### Schema Introspection

#### `schema_get_node`
Gets the schema definition for a specific path in the document schema.

**Parameters**:
- `node_path` (string): JSON Pointer path (e.g., "/properties/title")
- `dereferenced` (bool, default: true): Resolve $ref references

**Returns**: `{"schema": {...}}`

#### `schema_get_root`
Gets the complete root schema.

**Parameters**:
- `dereferenced` (bool, default: true): Resolve $ref references

**Returns**: `{"schema": {...}}`

## 🎯 Use Cases

### 1. Documentation Management
```
User: Create a new technical document
AI: [Uses document_create] → Returns doc_id
AI: Document created! Would you like to add a title?

User: Yes, set the title to "API Design Guide"
AI: [Uses document_update_node] → Updates /title
AI: Title updated! Current version: 2
```

### 2. Structured Data Collection
```
User: What fields are required for documents?
AI: [Uses schema_get_root] → Analyzes schema
AI: Required fields are: title, content
AI: Optional fields with defaults: tags (empty array), metadata
```

### 3. Version Control & Collaboration
```
User: Update the document, but make sure it hasn't changed
AI: [Uses document_read_node] → Gets current version
AI: [Uses document_update_node with expected_version] → Safe update
AI: ✓ Update successful! No conflicts detected.
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lib --cov=apps

# Run specific test file
pytest tests/apps/mcp_server/test_document_tools.py -v

# Run tests matching a pattern
pytest -k "test_document_create"
```

### Code Quality

```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Project Structure Guidelines

- ✅ **DO** put business logic in `lib/json_schema_core/`
- ✅ **DO** put protocol adapters in `apps/`
- ✅ **DO** write tests for every feature
- ❌ **DON'T** put business logic in `apps/` (keep it thin)
- ❌ **DON'T** skip version checks in updates (optimistic locking is critical)

## 🔐 Security Considerations

- **Schema Validation**: All documents are validated before storage
- **Path Safety**: JSON Pointers are validated to prevent traversal attacks
- **Version Control**: Optimistic locking prevents race conditions
- **Storage Isolation**: Documents are stored in a configurable directory
- **No External Network**: File-based storage, no external dependencies

## 🗺️ Roadmap

- [x] **Phase 0**: Core library foundation (DocumentService, SchemaService)
- [x] **Phase 1**: Complete CRUD operations with validation
- [x] **Phase 2**: Configuration and development tools
- [x] **Phase 4**: MCP interface layer (current)
- [ ] **Phase 3**: REST API interface (future)
- [ ] **Phase 5**: Advanced features (search, queries, webhooks)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [JSON Schema](https://json-schema.org/)
- Inspired by the need for structured data management in AI workflows

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/jfomhover/json-schema-mcp-tool/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jfomhover/json-schema-mcp-tool/discussions)

---

<div align="center">
  <strong>Made with ❤️ for AI-powered document management</strong>
  <br>
  <sub>Built with Test-Driven Development • Designed for the Model Context Protocol</sub>
</div>
