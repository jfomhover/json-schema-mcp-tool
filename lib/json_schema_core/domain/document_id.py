"""DocumentId value object - wraps ULID for document identification."""

from ulid import ULID


class DocumentId:
    """Value object representing a document identifier using ULID."""

    def __init__(self, value: str):
        """Create DocumentId from a ULID string.

        Args:
            value: ULID string (26 characters)
        """
        self._value = value

    @classmethod
    def generate(cls) -> "DocumentId":
        """Generate a new DocumentId with a fresh ULID.

        Returns:
            New DocumentId instance with generated ULID
        """
        return cls(str(ULID()))

    def __str__(self) -> str:
        """Convert DocumentId to string representation.

        Returns:
            ULID string
        """
        return self._value
