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
