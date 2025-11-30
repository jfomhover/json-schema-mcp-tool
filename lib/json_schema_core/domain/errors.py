"""Domain-level exceptions."""


class PathNotFoundError(Exception):
    """Raised when a file system path is not found."""
    
    def __init__(self, path: str):
        """Initialize with the path that was not found.
        
        Args:
            path: The file system path that was not found
        """
        self.path = path
        super().__init__(f"Path not found: {path}")


class VersionConflictError(Exception):
    """Raised when optimistic locking detects a version conflict."""
    
    def __init__(self, expected: int, actual: int):
        """Initialize with version conflict details.
        
        Args:
            expected: The version that was expected
            actual: The actual version found
        """
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Version conflict: expected {expected}, but found {actual}"
        )


class ValidationFailedError(Exception):
    """Raised when JSON Schema validation fails."""
    
    def __init__(self, errors: list):
        """Initialize with validation error details.
        
        Args:
            errors: List of validation error details
        """
        self.errors = errors
        super().__init__(f"Validation failed with {len(errors)} error(s)")


class DocumentNotFoundError(Exception):
    """Raised when a document is not found in storage."""
    
    def __init__(self, doc_id: str):
        """Initialize with the document ID that was not found.
        
        Args:
            doc_id: The document identifier that was not found
        """
        self.doc_id = doc_id
        super().__init__(f"Document not found: {doc_id}")
