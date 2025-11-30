"""File system storage implementation."""

import json
import os
from pathlib import Path
from json_schema_core.storage.storage_interface import StorageInterface
from json_schema_core.domain.errors import DocumentNotFoundError


class FileSystemStorage(StorageInterface):
    """File system based storage implementation with atomic writes and durability."""
    
    def __init__(self, base_path: Path):
        """Initialize file system storage.
        
        Args:
            base_path: Base directory for storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def write_document(self, doc_id: str, content: dict) -> None:
        """Write a document with atomic operation and durability guarantee.
        
        Uses temp file + rename pattern for atomicity.
        Calls fsync to ensure data reaches disk.
        
        Args:
            doc_id: Document identifier
            content: Document content as dictionary
        """
        doc_file = self.base_path / f"{doc_id}.json"
        tmp_file = self.base_path / f"{doc_id}.tmp"
        
        try:
            # Write to temp file
            with open(tmp_file, "w") as f:
                json.dump(content, f, indent=2)
                f.flush()
                # Ensure data reaches disk before rename
                os.fsync(f.fileno())
            
            # Atomic rename (on POSIX systems)
            tmp_file.rename(doc_file)
            
        except Exception:
            # Clean up temp file on any error
            if tmp_file.exists():
                tmp_file.unlink()
            raise
    
    def read_document(self, doc_id: str) -> dict:
        """Read a document by ID.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Document content as dictionary
            
        Raises:
            DocumentNotFoundError: If document doesn't exist
        """
        doc_file = self.base_path / f"{doc_id}.json"
        
        if not doc_file.exists():
            raise DocumentNotFoundError(doc_id)
        
        with open(doc_file, "r") as f:
            return json.load(f)
    
    def delete_document(self, doc_id: str) -> None:
        """Delete a document.
        
        Args:
            doc_id: Document identifier
        """
        raise NotImplementedError("delete_document not yet implemented")
    
    def list_documents(self, limit: int = 100, offset: int = 0) -> list[str]:
        """List document IDs with pagination.
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of document IDs
        """
        raise NotImplementedError("list_documents not yet implemented")
    
    def read_metadata(self, doc_id: str) -> dict | None:
        """Read document metadata.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        meta_file = self.base_path / f"{doc_id}.meta.json"
        
        if not meta_file.exists():
            return None
        
        with open(meta_file, "r") as f:
            return json.load(f)
    
    def write_metadata(self, doc_id: str, metadata: dict) -> None:
        """Write document metadata with atomic operation and durability guarantee.
        
        Uses temp file + rename pattern for atomicity.
        Calls fsync to ensure data reaches disk.
        
        Args:
            doc_id: Document identifier
            metadata: Metadata dictionary
        """
        meta_file = self.base_path / f"{doc_id}.meta.json"
        tmp_file = self.base_path / f"{doc_id}.meta.tmp"
        
        try:
            # Write to temp file
            with open(tmp_file, "w") as f:
                json.dump(metadata, f, indent=2)
                f.flush()
                # Ensure data reaches disk before rename
                os.fsync(f.fileno())
            
            # Atomic rename (on POSIX systems)
            tmp_file.rename(meta_file)
            
        except Exception:
            # Clean up temp file on any error
            if tmp_file.exists():
                tmp_file.unlink()
            raise
