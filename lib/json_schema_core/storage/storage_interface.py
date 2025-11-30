"""Storage interface for document persistence."""

from abc import ABC, abstractmethod


class StorageInterface(ABC):
    """Abstract base class for storage implementations."""
    
    @abstractmethod
    def read_document(self, doc_id: str) -> dict:
        """Read a document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document content as dictionary
            
        Raises:
            DocumentNotFoundError: If document doesn't exist
        """
        pass
    
    @abstractmethod
    def write_document(self, doc_id: str, content: dict) -> None:
        """Write a document.
        
        Args:
            doc_id: Document identifier
            content: Document content as dictionary
        """
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """Delete a document.
        
        Args:
            doc_id: Document identifier
        """
        pass
    
    @abstractmethod
    def list_documents(self, limit: int = 100, offset: int = 0) -> list[str]:
        """List document IDs with pagination.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of document IDs
        """
        pass
    
    @abstractmethod
    def read_metadata(self, doc_id: str) -> dict | None:
        """Read document metadata.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def write_metadata(self, doc_id: str, metadata: dict) -> None:
        """Write document metadata.
        
        Args:
            doc_id: Document identifier
            metadata: Metadata dictionary
        """
        pass
