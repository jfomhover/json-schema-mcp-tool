"""Tests for DocumentId value object."""

import pytest
from json_schema_core.domain.document_id import DocumentId


def test_document_id_from_ulid_string():
    """Test creating DocumentId from a ULID string."""
    ulid_str = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    doc_id = DocumentId(ulid_str)
    assert str(doc_id) == ulid_str


def test_document_id_generate():
    """Test generating a new ULID."""
    doc_id = DocumentId.generate()
    assert doc_id is not None
    assert len(str(doc_id)) == 26  # ULID length
    
    # Generate another and verify they're different
    doc_id2 = DocumentId.generate()
    assert str(doc_id) != str(doc_id2)


def test_document_id_str_conversion():
    """Test converting DocumentId to string."""
    ulid_str = "01ARZ3NDEKTSV4RRFFQ69G5FAV"
    doc_id = DocumentId(ulid_str)
    
    # Should be able to convert to string
    result = str(doc_id)
    assert result == ulid_str
    assert isinstance(result, str)
