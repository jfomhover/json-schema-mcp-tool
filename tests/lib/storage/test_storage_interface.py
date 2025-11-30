"""Tests for StorageInterface ABC."""

import pytest
from json_schema_core.storage.storage_interface import StorageInterface


def test_cannot_instantiate_interface():
    """Test that StorageInterface cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        StorageInterface()
