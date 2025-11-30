"""
SchemaService - Schema loading and $ref resolution
"""
import copy
from typing import Set
from json_schema_core.storage.storage_interface import StorageInterface
from json_schema_core.domain.errors import DocumentNotFoundError, ValidationFailedError


class SchemaService:
    """Service for loading and resolving JSON schemas"""
    
    def __init__(self, storage: StorageInterface):
        """Initialize SchemaService with storage backend"""
        self.storage = storage
        self._cache: dict[str, dict] = {}
    
    def load_schema(self, schema_id: str) -> dict:
        """
        Load a schema from storage and resolve all $ref references
        
        Args:
            schema_id: The ID of the schema to load
            
        Returns:
            The fully resolved schema
            
        Raises:
            DocumentNotFoundError: If schema not found in storage
        """
        # Check cache first
        if schema_id in self._cache:
            return copy.deepcopy(self._cache[schema_id])
        
        # Load the base schema
        schema = self.storage.read_document(schema_id)
        
        # Resolve all $ref references
        resolved = self._resolve_refs(schema, schema_id, set())
        
        # Cache the resolved schema
        self._cache[schema_id] = resolved
        
        # Return a copy to prevent mutation
        return copy.deepcopy(resolved)
    
    def _resolve_refs(self, schema: dict, base_id: str, visited: Set[str]) -> dict:
        """
        Recursively resolve $ref references in a schema
        
        Args:
            schema: The schema (or sub-schema) to resolve
            base_id: The ID of the base schema (for resolving relative refs)
            visited: Set of schema IDs already visited (for circular detection)
            
        Returns:
            A copy of the schema with all $ref resolved
            
        Raises:
            ValidationFailedError: If circular reference detected
        """
        # Make a copy to avoid mutating the original
        result = copy.deepcopy(schema)
        
        # Check for circular reference
        if base_id in visited:
            raise ValidationFailedError([{
                "message": f"Circular reference detected: {base_id}",
                "path": "",
                "validator": "ref_resolution"
            }])
        
        visited_copy = visited.copy()
        visited_copy.add(base_id)
        
        # Process the schema recursively
        self._resolve_refs_recursive(result, base_id, visited_copy)
        
        return result
    
    def _resolve_refs_recursive(self, obj: any, base_id: str, visited: Set[str]) -> None:
        """
        Helper to recursively resolve $ref in-place
        
        Args:
            obj: Current object being processed (dict, list, or scalar)
            base_id: Base schema ID for resolving references
            visited: Set of visited schema IDs
        """
        if isinstance(obj, dict):
            # Check if this is a $ref
            if "$ref" in obj:
                ref = obj["$ref"]
                
                # Handle local references (start with #/)
                if ref.startswith("#/"):
                    # Local reference - resolve within base schema
                    path = ref[2:].split("/")
                    base_schema = self.storage.read_document(base_id)
                    resolved = self._navigate_path(base_schema, path)
                    
                    # Replace $ref with resolved content
                    obj.clear()
                    obj.update(copy.deepcopy(resolved))
                    
                    # Continue resolving in the resolved content
                    self._resolve_refs_recursive(obj, base_id, visited)
                else:
                    # Cross-schema reference - load the referenced schema
                    ref_id = ref
                    
                    if ref_id in visited:
                        raise ValidationFailedError([{
                            "message": f"Circular reference detected: {ref_id}",
                            "path": "",
                            "validator": "ref_resolution"
                        }])
                    
                    visited_copy = visited.copy()
                    visited_copy.add(ref_id)
                    
                    ref_schema = self.storage.read_document(ref_id)
                    
                    # Replace $ref with resolved content
                    obj.clear()
                    obj.update(copy.deepcopy(ref_schema))
                    
                    # Continue resolving in the resolved content
                    self._resolve_refs_recursive(obj, ref_id, visited_copy)
            else:
                # Recurse into dictionary values
                for value in obj.values():
                    self._resolve_refs_recursive(value, base_id, visited)
                    
        elif isinstance(obj, list):
            # Recurse into list items
            for item in obj:
                self._resolve_refs_recursive(item, base_id, visited)
    
    def _navigate_path(self, obj: any, path: list[str]) -> any:
        """
        Navigate a path in an object (for resolving #/path/to/value references)
        
        Args:
            obj: The object to navigate
            path: List of keys to traverse
            
        Returns:
            The value at the path
            
        Raises:
            ValidationFailedError: If path not found
        """
        current = obj
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                raise ValidationFailedError(f"Cannot resolve reference path: {'/'.join(path)}")
        return current
    
    def get_required_fields(self, schema: dict) -> list[str]:
        """
        Extract required field names from a schema
        
        Args:
            schema: The schema to inspect
            
        Returns:
            List of required field names (empty if none)
        """
        return schema.get("required", [])
    
    def get_default_values(self, schema: dict) -> dict:
        """
        Extract default values from schema properties
        
        Args:
            schema: The schema to inspect
            
        Returns:
            Dictionary mapping field names to their default values
        """
        defaults = {}
        properties = schema.get("properties", {})
        
        for field_name, field_schema in properties.items():
            if "default" in field_schema:
                defaults[field_name] = field_schema["default"]
        
        return defaults
    
    def get_schema_dependencies(self, schema_id: str) -> set[str]:
        """
        Find all schema dependencies (external $ref) for a schema
        
        Args:
            schema_id: The ID of the schema to analyze
            
        Returns:
            Set of schema IDs that this schema references (excludes local #/ refs)
        """
        schema = self.storage.read_document(schema_id)
        dependencies = set()
        
        self._collect_dependencies(schema, dependencies)
        
        return dependencies
    
    def _collect_dependencies(self, obj: any, dependencies: set[str]) -> None:
        """
        Recursively collect schema dependencies from $ref
        
        Args:
            obj: Object to scan for $ref
            dependencies: Set to collect dependency IDs into
        """
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                # Only collect external references (not local #/ refs)
                if not ref.startswith("#/"):
                    dependencies.add(ref)
            else:
                # Recurse into dictionary values
                for value in obj.values():
                    self._collect_dependencies(value, dependencies)
        elif isinstance(obj, list):
            # Recurse into list items
            for item in obj:
                self._collect_dependencies(item, dependencies)
    
    def clear_cache(self) -> None:
        """Clear all cached schemas"""
        self._cache.clear()
