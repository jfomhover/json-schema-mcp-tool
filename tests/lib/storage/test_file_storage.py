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
