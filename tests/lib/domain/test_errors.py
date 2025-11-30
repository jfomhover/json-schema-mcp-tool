"""Tests for domain exceptions."""

import pytest
from json_schema_core.domain.errors import (
    DocumentNotFoundError,
    PathNotFoundError,
    ValidationFailedError,
    VersionConflictError,
)


def test_path_not_found_error():
    """Test PathNotFoundError can be raised and caught."""
    path = "/nonexistent/path"

    with pytest.raises(PathNotFoundError) as exc_info:
        raise PathNotFoundError(path)

    error = exc_info.value
    assert error.path == path
    assert path in str(error)


def test_version_conflict_error():
    """Test VersionConflictError contains version information."""
    expected = 5
    actual = 3

    with pytest.raises(VersionConflictError) as exc_info:
        raise VersionConflictError(expected, actual)

    error = exc_info.value
    assert error.expected == expected
    assert error.actual == actual
    assert str(expected) in str(error)
    assert str(actual) in str(error)


def test_validation_failed_error():
    """Test ValidationFailedError contains validation details."""
    errors = [
        {"field": "name", "error": "Required field missing"},
        {"field": "age", "error": "Must be positive"},
    ]

    with pytest.raises(ValidationFailedError) as exc_info:
        raise ValidationFailedError(errors)

    error = exc_info.value
    assert error.errors == errors
    assert len(error.errors) == 2


def test_document_not_found_error():
    """Test DocumentNotFoundError contains document ID."""
    doc_id = "01ARZ3NDEKTSV4RRFFQ69G5FAV"

    with pytest.raises(DocumentNotFoundError) as exc_info:
        raise DocumentNotFoundError(doc_id)

    error = exc_info.value
    assert error.doc_id == doc_id
    assert doc_id in str(error)
