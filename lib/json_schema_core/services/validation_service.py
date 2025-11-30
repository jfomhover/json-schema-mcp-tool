"""Validation service for JSON Schema validation."""

from jsonschema import validate as jsonschema_validate, ValidationError
from json_schema_core.domain.errors import ValidationFailedError


class ValidationService:
    """Service for validating documents against JSON Schema."""
    
    def __init__(self, schema: dict):
        """Initialize with a JSON Schema.
        
        Args:
            schema: JSON Schema dictionary
        """
        self.schema = schema
    
    def validate(self, document: dict) -> None:
        """Validate a document against the schema.
        
        Args:
            document: Document to validate
            
        Raises:
            ValidationFailedError: If validation fails, with error details
        """
        try:
            jsonschema_validate(instance=document, schema=self.schema)
        except ValidationError as e:
            # Collect all validation errors
            errors = [self._format_error(e)]
            
            # Check if there are more errors in the context
            if hasattr(e, 'context') and e.context:
                for sub_error in e.context:
                    errors.append(self._format_error(sub_error))
            
            raise ValidationFailedError(errors)
    
    def _format_error(self, error: ValidationError) -> dict:
        """Format a validation error into a dictionary.
        
        Args:
            error: ValidationError from jsonschema
            
        Returns:
            Dictionary with error details
        """
        return {
            "message": error.message,
            "path": list(error.absolute_path),
            "validator": error.validator,
            "validator_value": error.validator_value,
        }
