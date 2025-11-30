"""
Tests for SchemaService - Schema loading and $ref resolution
"""
import pytest
from json_schema_core.services.schema_service import SchemaService
from json_schema_core.storage.file_storage import FileSystemStorage
from json_schema_core.domain.errors import DocumentNotFoundError, ValidationFailedError
from json_schema_core.domain.document_id import DocumentId
from pathlib import Path
import tempfile
import shutil
import json


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory"""
    temp_dir = tempfile.mkdtemp()
    storage = FileSystemStorage(temp_dir)
    yield storage
    shutil.rmtree(temp_dir)


@pytest.fixture
def schema_service(temp_storage):
    """Create a SchemaService with temporary storage"""
    return SchemaService(temp_storage)


# P0.5.1: Load Schema with Basic $ref Resolution

def test_load_schema_without_ref(schema_service, temp_storage):
    """Test loading a simple schema without $ref"""
    schema_id = DocumentId.generate()
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required": ["name"]
    }
    
    # Store the schema
    temp_storage.write_document(str(schema_id), schema)
    
    # Load it back
    loaded = schema_service.load_schema(str(schema_id))
    
    assert loaded == schema
    assert loaded["type"] == "object"
    assert "name" in loaded["properties"]


def test_load_schema_not_found(schema_service):
    """Test loading non-existent schema raises DocumentNotFoundError"""
    with pytest.raises(DocumentNotFoundError):
        schema_service.load_schema("nonexistent-id")


def test_resolve_local_ref(schema_service, temp_storage):
    """Test resolving $ref within the same schema"""
    schema_id = DocumentId.generate()
    schema = {
        "type": "object",
        "definitions": {
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"}
                }
            }
        },
        "properties": {
            "home": {"$ref": "#/definitions/address"},
            "work": {"$ref": "#/definitions/address"}
        }
    }
    
    temp_storage.write_document(str(schema_id), schema)
    loaded = schema_service.load_schema(str(schema_id))
    
    # Check that $ref was resolved
    assert loaded["properties"]["home"]["type"] == "object"
    assert "street" in loaded["properties"]["home"]["properties"]
    assert loaded["properties"]["work"]["type"] == "object"
    assert "city" in loaded["properties"]["work"]["properties"]


def test_resolve_cross_schema_ref(schema_service, temp_storage):
    """Test resolving $ref across multiple schemas"""
    # Create address schema
    address_id = DocumentId.generate()
    address_schema = {
        "type": "object",
        "properties": {
            "street": {"type": "string"},
            "city": {"type": "string"}
        }
    }
    temp_storage.write_document(str(address_id), address_schema)
    
    # Create person schema that references address
    person_id = DocumentId.generate()
    person_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "address": {"$ref": f"{address_id}"}
        }
    }
    temp_storage.write_document(str(person_id), person_schema)
    
    # Load person schema - should resolve address reference
    loaded = schema_service.load_schema(str(person_id))
    
    assert loaded["properties"]["address"]["type"] == "object"
    assert "street" in loaded["properties"]["address"]["properties"]
    assert "city" in loaded["properties"]["address"]["properties"]


# P0.5.2: Circular Reference Detection

def test_circular_ref_detection_direct(schema_service, temp_storage):
    """Test detecting direct circular reference (A -> A)"""
    schema_id = DocumentId.generate()
    schema = {
        "type": "object",
        "properties": {
            "self": {"$ref": f"{schema_id}"}
        }
    }
    temp_storage.write_document(str(schema_id), schema)
    
    with pytest.raises(ValidationFailedError) as exc_info:
        schema_service.load_schema(str(schema_id))
    
    # Check that the error message mentions circular reference
    assert len(exc_info.value.errors) == 1
    assert "Circular reference detected" in exc_info.value.errors[0]["message"]


def test_circular_ref_detection_indirect(schema_service, temp_storage):
    """Test detecting indirect circular reference (A -> B -> A)"""
    schema_a_id = DocumentId.generate()
    schema_b_id = DocumentId.generate()
    
    # Schema B references A
    schema_b = {
        "type": "object",
        "properties": {
            "back_to_a": {"$ref": f"{schema_a_id}"}
        }
    }
    temp_storage.write_document(str(schema_b_id), schema_b)
    
    # Schema A references B
    schema_a = {
        "type": "object",
        "properties": {
            "to_b": {"$ref": f"{schema_b_id}"}
        }
    }
    temp_storage.write_document(str(schema_a_id), schema_a)
    
    with pytest.raises(ValidationFailedError) as exc_info:
        schema_service.load_schema(str(schema_a_id))
    
    assert len(exc_info.value.errors) == 1
    assert "Circular reference detected" in exc_info.value.errors[0]["message"]


def test_circular_ref_detection_deep(schema_service, temp_storage):
    """Test detecting deep circular reference (A -> B -> C -> A)"""
    schema_a_id = DocumentId.generate()
    schema_b_id = DocumentId.generate()
    schema_c_id = DocumentId.generate()
    
    # Create C -> A
    schema_c = {
        "type": "object",
        "properties": {
            "back_to_a": {"$ref": f"{schema_a_id}"}
        }
    }
    temp_storage.write_document(str(schema_c_id), schema_c)
    
    # Create B -> C
    schema_b = {
        "type": "object",
        "properties": {
            "to_c": {"$ref": f"{schema_c_id}"}
        }
    }
    temp_storage.write_document(str(schema_b_id), schema_b)
    
    # Create A -> B
    schema_a = {
        "type": "object",
        "properties": {
            "to_b": {"$ref": f"{schema_b_id}"}
        }
    }
    temp_storage.write_document(str(schema_a_id), schema_a)
    
    with pytest.raises(ValidationFailedError) as exc_info:
        schema_service.load_schema(str(schema_a_id))
    
    assert len(exc_info.value.errors) == 1
    assert "Circular reference detected" in exc_info.value.errors[0]["message"]
