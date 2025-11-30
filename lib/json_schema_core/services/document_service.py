"""
DocumentService - Core CRUD operations for documents
"""
from datetime import datetime
from typing import Any
from json_schema_core.storage.storage_interface import StorageInterface
from json_schema_core.services.schema_service import SchemaService
from json_schema_core.services.validation_service import ValidationService
from json_schema_core.domain.document_id import DocumentId
from json_schema_core.domain.metadata import DocumentMetadata
from json_schema_core.domain.errors import DocumentNotFoundError
from json_schema_core.utils.json_pointer import resolve_pointer


class DocumentService:
    """Service for document CRUD operations with schema validation"""
    
    def __init__(self, storage: StorageInterface, schema_service: SchemaService):
        """
        Initialize DocumentService with required dependencies
        
        Args:
            storage: Storage backend for documents and metadata
            schema_service: Service for loading and resolving schemas
        """
        self.storage = storage
        self.schema_service = schema_service
        self._schema_cache: dict[str, dict] = {}
    
    def create_document(self, schema_id: str, document: dict, doc_id: str | None = None) -> tuple[str, DocumentMetadata]:
        """
        Create a new document with validation and metadata
        
        Args:
            schema_id: The ID of the schema to validate against
            document: The document data to create
            doc_id: Optional custom document ID (must be valid ULID format)
            
        Returns:
            Tuple of (document_id, metadata)
            
        Raises:
            ValidationFailedError: If document fails schema validation
            DocumentNotFoundError: If schema not found
            ValueError: If custom doc_id is invalid or already exists
        """
        # Validate and process custom ID if provided
        if doc_id is not None:
            # Validate ID format (ULID should be 26 characters, uppercase alphanumeric)
            if not (len(doc_id) == 26 and doc_id.isalnum() and doc_id.isupper()):
                raise ValueError(f"Invalid document ID format: {doc_id}")
            
            # Check if document already exists
            try:
                self.storage.read_document(doc_id)
                # If we get here, document exists
                raise ValueError(f"Document with ID {doc_id} already exists")
            except Exception as e:
                # If DocumentNotFoundError, that's good - ID is available
                if "not found" not in str(e).lower():
                    # Some other error occurred
                    raise
        
        # Load schema (with caching)
        if schema_id not in self._schema_cache:
            schema = self.schema_service.load_schema(schema_id)
            self._schema_cache[schema_id] = schema
        else:
            schema = self._schema_cache[schema_id]
        
        # Create validation service for this schema
        validation_service = ValidationService(schema)
        
        # Apply default values from schema
        document_with_defaults = validation_service.apply_defaults(document)
        
        # Validate document against schema
        validation_service.validate(document_with_defaults)
        
        # Use custom ID or generate new one
        if doc_id is None:
            doc_id = str(DocumentId.generate())
        
        # Create metadata
        now = datetime.now()
        metadata = DocumentMetadata(
            doc_id=doc_id,
            version=1,
            created_at=now,
            updated_at=now
        )
        
        # Store document and metadata atomically
        self.storage.write_document(doc_id, document_with_defaults)
        self.storage.write_metadata(doc_id, metadata.model_dump(mode='json'))
        
        return doc_id, metadata
    
    def read_node(self, doc_id: str, node_path: str) -> tuple[Any, int]:
        """
        Read a document or a specific node within a document using JSONPointer
        
        Args:
            doc_id: The ID of the document to read
            node_path: JSONPointer path to the node (use "/" for root)
            
        Returns:
            Tuple of (node_value, version)
            
        Raises:
            DocumentNotFoundError: If document not found
            PathNotFoundError: If node_path doesn't exist in document
        """
        # Load document from storage
        try:
            document = self.storage.read_document(doc_id)
        except Exception as e:
            if "not found" in str(e).lower():
                raise DocumentNotFoundError(doc_id)
            raise
        
        # Load metadata to get version
        metadata_dict = self.storage.read_metadata(doc_id)
        if metadata_dict is None:
            raise DocumentNotFoundError(doc_id)
        
        version = metadata_dict["version"]
        
        # Resolve the path in the document
        if node_path == "/":
            # Root path - return full document
            return document, version
        else:
            # Use JSONPointer to resolve path
            value = resolve_pointer(document, node_path)
            return value, version
