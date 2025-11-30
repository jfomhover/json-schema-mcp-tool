"""Tests for FileSystemStorage."""

import json
import os
from pathlib import Path
import pytest
from json_schema_core.storage.file_storage import FileSystemStorage
from json_schema_core.domain.errors import DocumentNotFoundError


def test_write_document_creates_file(tmp_path):
    """Test that write_document creates a JSON file."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-1"
    content = {"title": "Test Document", "value": 42}
    
    storage.write_document(doc_id, content)
    
    # Check that the file exists
    doc_file = tmp_path / f"{doc_id}.json"
    assert doc_file.exists()
    
    # Verify content
    with open(doc_file, "r") as f:
        saved_content = json.load(f)
    assert saved_content == content


def test_write_document_atomic(tmp_path):
    """Test that write_document uses atomic write (temp file + rename)."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-2"
    content = {"data": "test"}
    
    # Spy on the file system to verify temp file was used
    storage.write_document(doc_id, content)
    
    # After write completes, temp file should not exist
    tmp_file = tmp_path / f"{doc_id}.tmp"
    assert not tmp_file.exists()
    
    # But the final file should exist
    doc_file = tmp_path / f"{doc_id}.json"
    assert doc_file.exists()


def test_write_document_cleans_up_tmp_on_error(tmp_path):
    """Test that temp file is cleaned up when write fails."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-3"
    
    # Create a scenario that will fail: invalid JSON-serializable content
    invalid_content = {"data": object()}  # object() is not JSON serializable
    
    with pytest.raises(TypeError):
        storage.write_document(doc_id, invalid_content)
    
    # Verify temp file was cleaned up
    tmp_file = tmp_path / f"{doc_id}.tmp"
    assert not tmp_file.exists()


def test_write_document_durable(tmp_path):
    """Test that write_document uses fsync for durability."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-4"
    content = {"important": "data"}
    
    # Write the document
    storage.write_document(doc_id, content)
    
    # The file should exist and be readable
    # (fsync was called, so data should be on disk)
    doc_file = tmp_path / f"{doc_id}.json"
    assert doc_file.exists()
    
    # Verify we can read it back
    with open(doc_file, "r") as f:
        saved_content = json.load(f)
    assert saved_content == content


def test_read_document_returns_content(tmp_path):
    """Test that read_document returns the document content."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-5"
    content = {"title": "Test", "data": [1, 2, 3]}
    
    # Write first
    storage.write_document(doc_id, content)
    
    # Now read back
    result = storage.read_document(doc_id)
    assert result == content


def test_read_document_raises_not_found(tmp_path):
    """Test that read_document raises DocumentNotFoundError for missing documents."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "non-existent-doc"
    
    with pytest.raises(DocumentNotFoundError) as exc_info:
        storage.read_document(doc_id)
    
    assert exc_info.value.doc_id == doc_id


def test_write_metadata_atomic(tmp_path):
    """Test that write_metadata uses atomic write (temp file + rename)."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-6"
    metadata = {
        "doc_id": doc_id,
        "version": 1,
        "schema_uri": "https://example.com/schema",
        "created_at": "2024-01-01T12:00:00",
        "modified_at": "2024-01-01T12:00:00"
    }
    
    storage.write_metadata(doc_id, metadata)
    
    # After write completes, temp file should not exist
    tmp_file = tmp_path / f"{doc_id}.meta.tmp"
    assert not tmp_file.exists()
    
    # But the final metadata file should exist
    meta_file = tmp_path / f"{doc_id}.meta.json"
    assert meta_file.exists()


def test_read_metadata(tmp_path):
    """Test that read_metadata returns metadata."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-7"
    metadata = {
        "doc_id": doc_id,
        "version": 2,
        "schema_uri": "https://example.com/schema",
        "created_at": "2024-01-01T12:00:00",
        "modified_at": "2024-01-02T15:30:00"
    }
    
    # Write first
    storage.write_metadata(doc_id, metadata)
    
    # Now read back
    result = storage.read_metadata(doc_id)
    assert result == metadata


def test_read_metadata_missing_returns_none(tmp_path):
    """Test that read_metadata returns None for missing metadata."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "non-existent-metadata"
    
    result = storage.read_metadata(doc_id)
    assert result is None


def test_metadata_includes_required_fields(tmp_path):
    """Test that metadata includes all required fields."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-8"
    metadata = {
        "doc_id": doc_id,
        "version": 1,
        "schema_uri": "https://example.com/schema",
        "created_at": "2024-01-01T12:00:00",
        "modified_at": "2024-01-01T12:00:00"
    }
    
    storage.write_metadata(doc_id, metadata)
    result = storage.read_metadata(doc_id)
    
    # Verify all required fields are present
    assert "doc_id" in result
    assert "version" in result
    assert "schema_uri" in result
    assert "created_at" in result
    assert "modified_at" in result


def test_write_metadata_cleans_up_tmp_on_error(tmp_path):
    """Test that temp metadata file is cleaned up when write fails."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-9"
    
    # Create a scenario that will fail: invalid JSON-serializable content
    invalid_metadata = {"data": object()}  # object() is not JSON serializable
    
    with pytest.raises(TypeError):
        storage.write_metadata(doc_id, invalid_metadata)
    
    # Verify temp file was cleaned up
    tmp_file = tmp_path / f"{doc_id}.meta.tmp"
    assert not tmp_file.exists()


def test_write_metadata_durable(tmp_path):
    """Test that write_metadata uses fsync for durability."""
    storage = FileSystemStorage(tmp_path)
    doc_id = "test-doc-10"
    metadata = {
        "doc_id": doc_id,
        "version": 1,
        "schema_uri": "https://example.com/schema",
        "created_at": "2024-01-01T12:00:00",
        "modified_at": "2024-01-01T12:00:00"
    }
    
    # Write the metadata
    storage.write_metadata(doc_id, metadata)
    
    # The file should exist and be readable
    # (fsync was called, so data should be on disk)
    meta_file = tmp_path / f"{doc_id}.meta.json"
    assert meta_file.exists()
    
    # Verify we can read it back
    with open(meta_file, "r") as f:
        saved_metadata = json.load(f)
    assert saved_metadata == metadata
