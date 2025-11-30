"""DocumentMetadata value object."""

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for a document including versioning information."""

    doc_id: str = Field(..., description="Document identifier (ULID)")
    version: int = Field(..., description="Document version for optimistic locking", ge=1)
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentMetadata":
        """Create DocumentMetadata from a dictionary.

        Args:
            data: Dictionary with metadata fields

        Returns:
            DocumentMetadata instance
        """
        # Convert string timestamps to datetime if needed
        created_at = data["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            doc_id=data["doc_id"],
            version=data["version"],
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict:
        """Convert DocumentMetadata to a dictionary.

        Returns:
            Dictionary with metadata fields and ISO format timestamps
        """
        return {
            "doc_id": self.doc_id,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def increment_version(self) -> "DocumentMetadata":
        """Create a new metadata instance with incremented version and updated timestamp.

        Returns:
            New DocumentMetadata with version+1 and current timestamp
        """
        return DocumentMetadata(
            doc_id=self.doc_id,
            version=self.version + 1,
            created_at=self.created_at,
            updated_at=datetime.now(),
        )
