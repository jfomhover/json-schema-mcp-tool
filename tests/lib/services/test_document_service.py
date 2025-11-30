"""
Tests for DocumentService - Document CRUD operations
"""
import pytest
from json_schema_core.services.document_service import DocumentService
from json_schema_core.services.schema_service import SchemaService
from json_schema_core.services.validation_service import ValidationService
from json_schema_core.storage.file_storage import FileSystemStorage
from json_schema_core.domain.errors import ValidationFailedError
from json_schema_core.domain.document_id import DocumentId
from json_schema_core.domain.metadata import DocumentMetadata
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime


# P1.0.1: Test Fixtures for DocumentService

@pytest.fixture
def temp_storage():
    """Create a temporary storage directory"""
    temp_dir = tempfile.mkdtemp()
    storage = FileSystemStorage(temp_dir)
    yield storage
    shutil.rmtree(temp_dir)


@pytest.fixture
def text_schema():
    """Load and return the text.json schema"""
    schema_path = Path(__file__).parent.parent.parent.parent / "schemas" / "text.json"
    with open(schema_path, "r") as f:
        return json.load(f)


@pytest.fixture
def validation_service(text_schema):
    """Create a ValidationService with text schema"""
    return ValidationService(text_schema)


@pytest.fixture
def schema_service(temp_storage):
    """Create a SchemaService with temporary storage"""
    return SchemaService(temp_storage)


@pytest.fixture
def document_service(temp_storage, schema_service):
    """Create a DocumentService with all dependencies"""
    return DocumentService(temp_storage, schema_service)


# P1.0.2: Sample Document Fixtures

@pytest.fixture
def valid_minimal_doc():
    """Minimal valid text document with required fields only"""
    return {
        "title": "Test",
        "authors": ["Author"],
        "sections": []
    }


@pytest.fixture
def valid_full_doc():
    """Complete valid text document with sections and paragraphs"""
    return {
        "title": "Complete Document",
        "authors": ["First Author", "Second Author"],
        "sections": [
            {
                "title": "Introduction",
                "paragraphs": [
                    "This is the first paragraph of the introduction.",
                    "This is the second paragraph with more details."
                ]
            },
            {
                "title": "Main Content",
                "paragraphs": [
                    "Here we discuss the main topic.",
                    "Additional information follows.",
                    "And even more content here."
                ]
            },
            {
                "title": "Conclusion",
                "paragraphs": [
                    "Final thoughts and summary."
                ]
            }
        ]
    }


@pytest.fixture
def invalid_doc_missing_title():
    """Invalid document - missing required 'title' field"""
    return {
        "authors": ["Author"],
        "sections": []
    }


@pytest.fixture
def invalid_doc_wrong_type():
    """Invalid document - wrong type for 'authors' field"""
    return {
        "title": "Test",
        "authors": "Single Author String",  # Should be array
        "sections": []
    }


@pytest.fixture
def sample_schema(temp_storage, text_schema):
    """Create and store the text.json schema"""
    schema_id = DocumentId.generate()
    temp_storage.write_document(str(schema_id), text_schema)
    return str(schema_id), text_schema


# P1.1.1: Basic Document Creation

def test_create_document_with_valid_data(document_service, sample_schema):
    """Test creating a document with valid data"""
    schema_id, _ = sample_schema
    document = {
        "title": "Test Document",
        "authors": ["John Doe"],
        "sections": [
            {
                "title": "Introduction",
                "paragraphs": ["This is a test paragraph."]
            }
        ]
    }
    
    doc_id, metadata = document_service.create_document(schema_id, document)
    
    # Check document ID is generated (ULID format)
    assert doc_id is not None
    assert len(doc_id) > 0
    
    # Check metadata
    assert isinstance(metadata, DocumentMetadata)
    assert metadata.doc_id == doc_id
    assert metadata.version == 1
    assert metadata.created_at is not None
    assert metadata.updated_at is not None
    assert isinstance(metadata.created_at, datetime)
    assert isinstance(metadata.updated_at, datetime)


def test_create_document_validation_failure(document_service, sample_schema):
    """Test that validation failure prevents document creation"""
    schema_id, _ = sample_schema
    invalid_document = {
        "title": "Test",
        "authors": [],  # Invalid: minItems is 1
        "sections": []
    }
    
    with pytest.raises(ValidationFailedError):
        document_service.create_document(schema_id, invalid_document)


def test_create_document_metadata_correct(document_service, sample_schema):
    """Test that metadata is created correctly"""
    schema_id, _ = sample_schema
    document = {
        "title": "Metadata Test",
        "authors": ["Jane Smith"],
        "sections": []
    }
    
    doc_id, metadata = document_service.create_document(schema_id, document)
    
    # Version should be 1 for new document
    assert metadata.version == 1
    
    # Timestamps should be set and close to current time
    assert metadata.created_at is not None
    assert metadata.updated_at is not None
    assert metadata.created_at <= metadata.updated_at


def test_create_document_id_is_ulid(document_service, sample_schema):
    """Test that document ID is in ULID format"""
    schema_id, _ = sample_schema
    document = {
        "title": "ULID Test",
        "authors": ["Test User"],
        "sections": []
    }
    
    doc_id, _ = document_service.create_document(schema_id, document)
    
    # ULID should be 26 characters
    assert len(doc_id) == 26
    # ULID should be uppercase alphanumeric
    assert doc_id.isalnum()
    assert doc_id.isupper()


def test_create_document_atomic_storage(document_service, sample_schema, temp_storage):
    """Test that document and metadata are stored atomically"""
    schema_id, _ = sample_schema
    document = {
        "title": "Atomic Test",
        "authors": ["Atomic Author"],
        "sections": []
    }
    
    doc_id, _ = document_service.create_document(schema_id, document)
    
    # Both document and metadata should be stored
    stored_doc = temp_storage.read_document(doc_id)
    stored_meta = temp_storage.read_metadata(doc_id)
    
    assert stored_doc is not None
    assert stored_meta is not None
    assert stored_doc["title"] == "Atomic Test"
    assert stored_meta["doc_id"] == doc_id
    assert stored_meta["version"] == 1


# P1.1.2: Document Creation with Custom ID

def test_create_document_with_custom_id(document_service, sample_schema, temp_storage):
    """Test creating a document with a custom ID"""
    schema_id, _ = sample_schema
    custom_id = str(DocumentId.generate())
    document = {
        "title": "Custom ID Test",
        "authors": ["Custom Author"],
        "sections": []
    }
    
    doc_id, metadata = document_service.create_document(schema_id, document, doc_id=custom_id)
    
    # Should use the custom ID
    assert doc_id == custom_id
    assert metadata.doc_id == custom_id
    
    # Document should be stored with custom ID
    stored_doc = temp_storage.read_document(custom_id)
    assert stored_doc["title"] == "Custom ID Test"


def test_create_document_custom_id_already_exists(document_service, sample_schema, temp_storage):
    """Test error when custom ID already exists"""
    schema_id, _ = sample_schema
    
    # Create first document
    custom_id = str(DocumentId.generate())
    document1 = {
        "title": "First Document",
        "authors": ["First Author"],
        "sections": []
    }
    document_service.create_document(schema_id, document1, doc_id=custom_id)
    
    # Try to create second document with same ID
    document2 = {
        "title": "Second Document",
        "authors": ["Second Author"],
        "sections": []
    }
    
    with pytest.raises(ValueError, match="already exists"):
        document_service.create_document(schema_id, document2, doc_id=custom_id)


def test_create_document_custom_id_must_be_valid(document_service, sample_schema):
    """Test that custom ID must be valid format"""
    schema_id, _ = sample_schema
    document = {
        "title": "Test",
        "authors": ["Test Author"],
        "sections": []
    }
    
    # Try with invalid ID (not ULID format)
    with pytest.raises(ValueError, match="Invalid document ID"):
        document_service.create_document(schema_id, document, doc_id="invalid-id-123")


# P1.2: Document Creation - Error Handling

def test_create_document_missing_required_field(document_service, sample_schema, invalid_doc_missing_title):
    """Test that missing required field causes validation error"""
    schema_id, _ = sample_schema
    
    # invalid_doc_missing_title is missing the required "title" field
    with pytest.raises(ValidationFailedError) as exc_info:
        document_service.create_document(schema_id, invalid_doc_missing_title)
    
    # Verify error contains details about missing field
    error = exc_info.value
    assert len(error.errors) > 0
    # Check if any error mentions "title" or "required"
    error_str = str(error.errors).lower()
    assert "title" in error_str or "required" in error_str


def test_create_document_wrong_type(document_service, sample_schema, invalid_doc_wrong_type):
    """Test that wrong field type causes validation error"""
    schema_id, _ = sample_schema
    
    # invalid_doc_wrong_type has "authors" as string instead of array
    with pytest.raises(ValidationFailedError) as exc_info:
        document_service.create_document(schema_id, invalid_doc_wrong_type)
    
    # Verify error contains details about type mismatch
    error = exc_info.value
    assert len(error.errors) > 0
    # Check if any error mentions "authors" or type-related keywords
    error_str = str(error.errors).lower()
    assert "authors" in error_str or "array" in error_str or "type" in error_str


def test_create_document_validates_after_defaults(document_service, temp_storage):
    """Test that validation occurs after applying defaults"""
    # Create a schema with a default that should pass validation
    schema_id = str(DocumentId.generate())
    schema = {
        "type": "object",
        "properties": {
            "count": {"type": "integer", "minimum": 10, "default": 15},
            "name": {"type": "string"}
        },
        "required": ["count", "name"]
    }
    temp_storage.write_document(schema_id, schema)
    
    # Document without "count" - should get default value of 15
    document = {
        "name": "Test"
    }
    
    doc_id, _ = document_service.create_document(schema_id, document)
    
    # Verify default was applied and document was stored
    stored_doc = temp_storage.read_document(doc_id)
    assert stored_doc["count"] == 15
    assert stored_doc["name"] == "Test"


def test_create_document_empty_required_array(document_service, sample_schema):
    """Test that empty array for required field with minItems fails validation"""
    schema_id, _ = sample_schema
    
    # text.json schema requires authors array to have minItems: 1
    document = {
        "title": "Test",
        "authors": [],  # Empty array violates minItems: 1
        "sections": []
    }
    
    with pytest.raises(ValidationFailedError) as exc_info:
        document_service.create_document(schema_id, document)
    
    # Verify error contains validation details
    error = exc_info.value
    assert len(error.errors) > 0
    # Check if any error mentions the validation issue
    error_str = str(error.errors).lower()
    assert "authors" in error_str or "minitems" in error_str or "too short" in error_str


# P1.3: Document Reading - read_node (Happy Path)

def test_read_node_root(document_service, sample_schema, valid_full_doc, temp_storage):
    """Test reading full document with root path '/'"""
    schema_id, _ = sample_schema
    
    # Create a document
    doc_id, metadata = document_service.create_document(schema_id, valid_full_doc)
    
    # Read root path
    content, version = document_service.read_node(doc_id, "/")
    
    # Should return full document
    assert content["title"] == valid_full_doc["title"]
    assert content["authors"] == valid_full_doc["authors"]
    assert len(content["sections"]) == len(valid_full_doc["sections"])
    assert version == 1


def test_read_node_simple_field(document_service, sample_schema, valid_full_doc):
    """Test reading a simple field using JSONPointer"""
    schema_id, _ = sample_schema
    
    # Create a document
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Read the title field
    title, version = document_service.read_node(doc_id, "/title")
    
    assert title == valid_full_doc["title"]
    assert version == 1


def test_read_node_nested_path(document_service, sample_schema, valid_full_doc):
    """Test reading nested paths with JSONPointer"""
    schema_id, _ = sample_schema
    
    # Create a document
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Read nested section title
    section_title, version = document_service.read_node(doc_id, "/sections/0/title")
    
    assert section_title == valid_full_doc["sections"][0]["title"]
    assert version == 1


def test_read_node_array_element(document_service, sample_schema, valid_full_doc):
    """Test reading array element using JSONPointer"""
    schema_id, _ = sample_schema
    
    # Create a document
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Read first author
    first_author, version = document_service.read_node(doc_id, "/authors/0")
    
    assert first_author == valid_full_doc["authors"][0]
    assert version == 1


def test_read_node_deep_nested(document_service, sample_schema, valid_full_doc):
    """Test reading deeply nested content"""
    schema_id, _ = sample_schema
    
    # Create a document
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Read first paragraph of first section
    paragraph, version = document_service.read_node(doc_id, "/sections/0/paragraphs/0")
    
    assert paragraph == valid_full_doc["sections"][0]["paragraphs"][0]
    assert version == 1


# P1.4: Document Reading - read_node (Error Handling)

def test_read_node_document_not_found(document_service):
    """Test that reading non-existent document raises error"""
    from json_schema_core.domain.errors import DocumentNotFoundError
    
    non_existent_id = str(DocumentId.generate())
    
    with pytest.raises(DocumentNotFoundError):
        document_service.read_node(non_existent_id, "/")


def test_read_node_path_not_found(document_service, sample_schema, valid_minimal_doc):
    """Test that reading non-existent path raises error"""
    from json_schema_core.domain.errors import PathNotFoundError
    
    schema_id, _ = sample_schema
    
    # Create a document
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Try to read non-existent field
    with pytest.raises(PathNotFoundError):
        document_service.read_node(doc_id, "/nonexistent")


def test_read_node_invalid_array_index(document_service, sample_schema, valid_minimal_doc):
    """Test that invalid array index raises error"""
    from json_schema_core.domain.errors import PathNotFoundError
    
    schema_id, _ = sample_schema
    
    # Create a minimal document (empty sections array)
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Try to read index that doesn't exist
    with pytest.raises(PathNotFoundError):
        document_service.read_node(doc_id, "/sections/99")


# P1.5: Document Updating - update_node (Happy Path)

def test_update_node_simple_field(document_service, sample_schema, valid_minimal_doc, temp_storage):
    """Test updating a simple field in a document"""
    schema_id, _ = sample_schema
    
    # Create document (version 1)
    doc_id, metadata = document_service.create_document(schema_id, valid_minimal_doc)
    assert metadata.version == 1
    
    # Update the title field
    new_value, new_version = document_service.update_node(
        doc_id, "/title", "Updated Title", expected_version=1
    )
    
    # Should return new value and incremented version
    assert new_value == "Updated Title"
    assert new_version == 2
    
    # Verify the change was persisted
    stored_title, version = document_service.read_node(doc_id, "/title")
    assert stored_title == "Updated Title"
    assert version == 2


def test_update_node_increments_version(document_service, sample_schema, valid_minimal_doc):
    """Test that update_node increments version correctly"""
    schema_id, _ = sample_schema
    
    # Create document (version 1)
    doc_id, metadata = document_service.create_document(schema_id, valid_minimal_doc)
    assert metadata.version == 1
    
    # First update (1 → 2)
    _, version = document_service.update_node(doc_id, "/title", "Title 2", expected_version=1)
    assert version == 2
    
    # Second update (2 → 3)
    _, version = document_service.update_node(doc_id, "/title", "Title 3", expected_version=2)
    assert version == 3
    
    # Third update (3 → 4)
    _, version = document_service.update_node(doc_id, "/title", "Title 4", expected_version=3)
    assert version == 4


def test_update_node_updates_timestamp(document_service, sample_schema, valid_minimal_doc, temp_storage):
    """Test that update_node updates the updated_at timestamp"""
    import time
    
    schema_id, _ = sample_schema
    
    # Create document
    doc_id, metadata = document_service.create_document(schema_id, valid_minimal_doc)
    created_at = metadata.created_at
    
    # Wait a bit to ensure timestamp difference
    time.sleep(0.1)
    
    # Update the document
    document_service.update_node(doc_id, "/title", "Updated Title", expected_version=1)
    
    # Read metadata and check timestamp
    metadata_dict = temp_storage.read_metadata(doc_id)
    updated_at = datetime.fromisoformat(metadata_dict["updated_at"])
    
    assert updated_at > created_at


def test_update_node_validates_result(document_service, sample_schema, valid_minimal_doc):
    """Test that update_node validates the updated document"""
    schema_id, _ = sample_schema
    
    # Create document
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Try to update title with wrong type (integer instead of string)
    with pytest.raises(ValidationFailedError):
        document_service.update_node(doc_id, "/title", 12345, expected_version=1)


def test_update_node_nested_field(document_service, sample_schema, valid_full_doc):
    """Test updating a nested field in a document"""
    schema_id, _ = sample_schema
    
    # Create document with nested content
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Update nested section title
    new_value, new_version = document_service.update_node(
        doc_id, "/sections/0/title", "Updated Section Title", expected_version=1
    )
    
    assert new_value == "Updated Section Title"
    assert new_version == 2
    
    # Verify the change
    section_title, _ = document_service.read_node(doc_id, "/sections/0/title")
    assert section_title == "Updated Section Title"


# P1.6: Document Updating - update_node (Optimistic Locking)

def test_update_node_version_conflict(document_service, sample_schema, valid_minimal_doc):
    """Test that update_node raises VersionConflictError on version mismatch"""
    from json_schema_core.domain.errors import VersionConflictError
    
    schema_id, _ = sample_schema
    
    # Create document (version 1)
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # First update succeeds (1 → 2)
    document_service.update_node(doc_id, "/title", "Title 2", expected_version=1)
    
    # Try to update with stale version (should fail)
    with pytest.raises(VersionConflictError) as exc_info:
        document_service.update_node(doc_id, "/title", "Title 3", expected_version=1)
    
    # Verify error details
    error = exc_info.value
    assert error.expected == 1
    assert error.actual == 2


def test_update_node_no_save_on_conflict(document_service, sample_schema, valid_minimal_doc, temp_storage):
    """Test that update_node doesn't save when version conflict occurs"""
    from json_schema_core.domain.errors import VersionConflictError
    
    schema_id, _ = sample_schema
    
    # Create document (version 1)
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Update to version 2
    document_service.update_node(doc_id, "/title", "Title 2", expected_version=1)
    
    # Try to update with stale version (should fail)
    try:
        document_service.update_node(doc_id, "/title", "Title 3", expected_version=1)
    except VersionConflictError:
        pass  # Expected
    
    # Verify document is still at version 2 with "Title 2"
    stored_doc = temp_storage.read_document(doc_id)
    metadata_dict = temp_storage.read_metadata(doc_id)
    
    assert stored_doc["title"] == "Title 2"
    assert metadata_dict["version"] == 2


# ============================================================================
# Phase 1.7: create_node Tests
# ============================================================================

def test_create_node_append_to_array(document_service, sample_schema, valid_minimal_doc):
    """Test appending an element to an array"""
    schema_id, _ = sample_schema
    
    # Create document with minimal authors array
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Append new author to array
    new_value, new_version = document_service.create_node(
        doc_id, "/authors", "New Author", expected_version=1
    )
    
    assert new_value == "New Author"
    assert new_version == 2
    
    # Verify the array was updated
    authors, _ = document_service.read_node(doc_id, "/authors")
    assert len(authors) == 2
    assert authors[-1] == "New Author"


def test_create_node_add_to_object(document_service, sample_schema, valid_full_doc):
    """Test adding a property to an object"""
    schema_id, _ = sample_schema
    
    # Create document
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Add new section to sections array
    new_section = {
        "title": "New Section",
        "paragraphs": ["New content"]
    }
    new_value, new_version = document_service.create_node(
        doc_id, "/sections", new_section, expected_version=1
    )
    
    assert new_value == new_section
    assert new_version == 2
    
    # Verify the section was added
    sections, _ = document_service.read_node(doc_id, "/sections")
    assert len(sections) == 4  # Original 3 + 1 new
    assert sections[-1]["title"] == "New Section"


def test_create_node_validates_result(document_service, sample_schema, valid_minimal_doc):
    """Test that create_node validates the resulting document"""
    from json_schema_core.domain.errors import ValidationFailedError
    
    schema_id, _ = sample_schema
    
    # Create document
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Try to add invalid section (missing required paragraphs field)
    invalid_section = {"title": "Bad Section"}  # Missing required 'paragraphs'
    
    with pytest.raises(ValidationFailedError):
        document_service.create_node(doc_id, "/sections", invalid_section, expected_version=1)


def test_create_node_version_conflict(document_service, sample_schema, valid_minimal_doc):
    """Test that create_node detects version conflicts"""
    from json_schema_core.domain.errors import VersionConflictError
    
    schema_id, _ = sample_schema
    
    # Create document (version 1)
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # First create succeeds (1 → 2)
    document_service.create_node(doc_id, "/authors", "Author 2", expected_version=1)
    
    # Second create with stale version should fail
    with pytest.raises(VersionConflictError) as exc_info:
        document_service.create_node(doc_id, "/authors", "Author 3", expected_version=1)
    
    assert exc_info.value.expected == 1
    assert exc_info.value.actual == 2


def test_create_node_invalid_parent_type(document_service, sample_schema, valid_minimal_doc):
    """Test that create_node fails if parent is not array or object"""
    schema_id, _ = sample_schema
    
    # Create document
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Try to create node under a string field (not valid)
    with pytest.raises(ValueError) as exc_info:
        document_service.create_node(doc_id, "/title", "something", expected_version=1)
    
    assert "array or object" in str(exc_info.value).lower()


# ============================================================================
# Phase 1.8: delete_node Tests
# ============================================================================

def test_delete_node_from_array(document_service, sample_schema, valid_full_doc):
    """Test deleting an element from an array"""
    schema_id, _ = sample_schema
    
    # Create document with multiple authors
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Delete second author (index 1)
    deleted_value, new_version = document_service.delete_node(
        doc_id, "/authors/1", expected_version=1
    )
    
    assert deleted_value == "Second Author"
    assert new_version == 2
    
    # Verify array was updated
    authors, _ = document_service.read_node(doc_id, "/authors")
    assert len(authors) == 1
    assert authors[0] == "First Author"


def test_delete_node_from_object(document_service, sample_schema, valid_full_doc):
    """Test deleting a property from an object"""
    schema_id, _ = sample_schema
    
    # Create document with sections
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # Delete first section
    deleted_value, new_version = document_service.delete_node(
        doc_id, "/sections/0", expected_version=1
    )
    
    assert deleted_value["title"] == "Introduction"
    assert new_version == 2
    
    # Verify section was removed
    sections, _ = document_service.read_node(doc_id, "/sections")
    assert len(sections) == 2  # Original 3 - 1
    assert sections[0]["title"] == "Main Content"


def test_delete_node_validates_result(document_service, sample_schema, valid_minimal_doc):
    """Test that delete_node validates the resulting document"""
    from json_schema_core.domain.errors import ValidationFailedError
    
    schema_id, _ = sample_schema
    
    # Create document with single author
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Try to delete the only author (would violate minItems: 1)
    with pytest.raises(ValidationFailedError):
        document_service.delete_node(doc_id, "/authors/0", expected_version=1)


def test_delete_node_version_conflict(document_service, sample_schema, valid_full_doc):
    """Test that delete_node detects version conflicts"""
    from json_schema_core.domain.errors import VersionConflictError
    
    schema_id, _ = sample_schema
    
    # Create document (version 1)
    doc_id, _ = document_service.create_document(schema_id, valid_full_doc)
    
    # First delete succeeds (1 → 2)
    document_service.delete_node(doc_id, "/authors/1", expected_version=1)
    
    # Second delete with stale version should fail
    with pytest.raises(VersionConflictError) as exc_info:
        document_service.delete_node(doc_id, "/authors/0", expected_version=1)
    
    assert exc_info.value.expected == 1
    assert exc_info.value.actual == 2


def test_delete_node_root_error(document_service, sample_schema, valid_minimal_doc):
    """Test that delete_node cannot delete root node"""
    schema_id, _ = sample_schema
    
    # Create document
    doc_id, _ = document_service.create_document(schema_id, valid_minimal_doc)
    
    # Try to delete root
    with pytest.raises(ValueError) as exc_info:
        document_service.delete_node(doc_id, "/", expected_version=1)
    
    assert "root" in str(exc_info.value).lower()


# ============================================================================
# Phase 1.9: list_documents Tests
# ============================================================================

def test_list_documents_empty(document_service):
    """Test that list_documents returns empty list when no documents exist"""
    # List documents in empty storage
    result = document_service.list_documents()
    
    assert result == []


def test_list_documents_returns_metadata(document_service, sample_schema, valid_minimal_doc):
    """Test that list_documents returns metadata for all documents"""
    schema_id, _ = sample_schema
    
    # Create 3 documents
    doc_ids = []
    for i in range(3):
        doc = valid_minimal_doc.copy()
        doc["title"] = f"Document {i+1}"
        doc_id, _ = document_service.create_document(schema_id, doc)
        doc_ids.append(doc_id)
    
    # List all documents
    result = document_service.list_documents()
    
    # Should return 3 metadata dicts
    assert len(result) == 3
    
    # Each should have required metadata fields
    for metadata in result:
        assert "doc_id" in metadata
        assert "version" in metadata
        assert "created_at" in metadata
        assert "updated_at" in metadata
        assert metadata["doc_id"] in doc_ids


def test_list_documents_pagination(document_service, sample_schema, valid_minimal_doc):
    """Test that list_documents supports pagination"""
    schema_id, _ = sample_schema
    
    # Create 5 documents
    doc_ids = []
    for i in range(5):
        doc = valid_minimal_doc.copy()
        doc["title"] = f"Document {i+1}"
        doc_id, _ = document_service.create_document(schema_id, doc)
        doc_ids.append(doc_id)
    
    # Get first 2 documents
    page1 = document_service.list_documents(limit=2, offset=0)
    assert len(page1) == 2
    
    # Get next 2 documents
    page2 = document_service.list_documents(limit=2, offset=2)
    assert len(page2) == 2
    
    # Get last 1 document
    page3 = document_service.list_documents(limit=2, offset=4)
    assert len(page3) == 1
    
    # Verify no overlap between pages
    page1_ids = {m["doc_id"] for m in page1}
    page2_ids = {m["doc_id"] for m in page2}
    page3_ids = {m["doc_id"] for m in page3}
    
    assert len(page1_ids & page2_ids) == 0
    assert len(page2_ids & page3_ids) == 0
    assert len(page1_ids & page3_ids) == 0
    
    # Verify all 5 documents are covered
    all_ids = page1_ids | page2_ids | page3_ids
    assert len(all_ids) == 5

