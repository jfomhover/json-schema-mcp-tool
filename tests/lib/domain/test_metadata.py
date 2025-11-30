"""Tests for DocumentMetadata value object."""

from datetime import datetime
import pytest
from json_schema_core.domain.metadata import DocumentMetadata


def test_metadata_creation():
    """Test creating DocumentMetadata with all fields."""
    doc_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    version = 1
    created_at = datetime(2024, 1, 1, 12, 0, 0)
    updated_at = datetime(2024, 1, 1, 12, 0, 0)
    
    metadata = DocumentMetadata(
        doc_id=doc_id,
        version=version,
        created_at=created_at,
        updated_at=updated_at,
    )
    
    assert metadata.doc_id == doc_id
    assert metadata.version == version
    assert metadata.created_at == created_at
    assert metadata.updated_at == updated_at


def test_metadata_from_dict():
    """Test deserializing DocumentMetadata from dict."""
    data = {
        "doc_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "version": 2,
        "created_at": "2024-01-01T12:00:00",
        "updated_at": "2024-01-02T15:30:00",
    }
    
    metadata = DocumentMetadata.from_dict(data)
    
    assert metadata.doc_id == data["doc_id"]
    assert metadata.version == data["version"]
    assert isinstance(metadata.created_at, datetime)
    assert isinstance(metadata.updated_at, datetime)


def test_metadata_to_dict():
    """Test serializing DocumentMetadata to dict."""
    doc_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    version = 3
    created_at = datetime(2024, 1, 1, 12, 0, 0)
    updated_at = datetime(2024, 1, 2, 15, 30, 0)
    
    metadata = DocumentMetadata(
        doc_id=doc_id,
        version=version,
        created_at=created_at,
        updated_at=updated_at,
    )
    
    result = metadata.to_dict()
    
    assert result["doc_id"] == doc_id
    assert result["version"] == version
    assert isinstance(result["created_at"], str)
    assert isinstance(result["updated_at"], str)


def test_metadata_increment_version():
    """Test updating version and timestamp."""
    doc_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    created_at = datetime(2024, 1, 1, 12, 0, 0)
    updated_at = datetime(2024, 1, 1, 12, 0, 0)
    
    metadata = DocumentMetadata(
        doc_id=doc_id,
        version=1,
        created_at=created_at,
        updated_at=updated_at,
    )
    
    # Increment version
    new_metadata = metadata.increment_version()
    
    assert new_metadata.version == 2
    assert new_metadata.doc_id == doc_id
    assert new_metadata.created_at == created_at
    assert new_metadata.updated_at > updated_at  # Timestamp should be updated
    
    # Original should be unchanged
    assert metadata.version == 1
