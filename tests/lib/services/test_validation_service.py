"""Tests for ValidationService."""

import pytest
from json_schema_core.services.validation_service import ValidationService
from json_schema_core.domain.errors import ValidationFailedError


def test_validate_valid_document():
    """Test that validate passes for a valid document."""
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "value": {"type": "number"}
        },
        "required": ["title"]
    }
    
    service = ValidationService(schema)
    document = {"title": "Test", "value": 42}
    
    # Should not raise any exception
    service.validate(document)


def test_validate_invalid_document():
    """Test that validate raises ValidationFailedError for invalid document."""
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "value": {"type": "number"}
        },
        "required": ["title"]
    }
    
    service = ValidationService(schema)
    
    # Missing required field
    document = {"value": 42}
    
    with pytest.raises(ValidationFailedError):
        service.validate(document)


def test_validation_error_details():
    """Test that ValidationFailedError contains validation details."""
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "value": {"type": "number"}
        },
        "required": ["title", "value"]
    }
    
    service = ValidationService(schema)
    
    # Multiple validation errors
    document = {"title": 123}  # Wrong type, missing required field
    
    with pytest.raises(ValidationFailedError) as exc_info:
        service.validate(document)
    
    error = exc_info.value
    # Should have a list of errors
    assert hasattr(error, 'errors')
    assert len(error.errors) > 0
    # Each error should have details
    assert isinstance(error.errors, list)


def test_validate_with_nested_schema():
    """Test validation with nested objects."""
    schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "nested": {
                "type": "object",
                "properties": {
                    "field": {"type": "string"}
                },
                "required": ["field"]
            }
        },
        "required": ["title", "nested"]
    }
    
    service = ValidationService(schema)
    
    # Valid nested document
    valid_doc = {
        "title": "Test",
        "nested": {"field": "value"}
    }
    service.validate(valid_doc)
    
    # Invalid - missing nested required field
    invalid_doc = {
        "title": "Test",
        "nested": {}
    }
    
    with pytest.raises(ValidationFailedError):
        service.validate(invalid_doc)
