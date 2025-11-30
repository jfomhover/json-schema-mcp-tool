"""Dummy test to validate CI/CD pipeline setup.

This test will be removed in Phase 0.1.6 after the project structure is set up.
Its sole purpose is to ensure GitHub Actions workflow runs successfully.
"""


def test_dummy():
    """Dummy test that always passes to validate CI pipeline."""
    assert True, "CI/CD pipeline is working!"


def test_python_version():
    """Verify Python version is 3.11+."""
    import sys
    
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version_info}"
