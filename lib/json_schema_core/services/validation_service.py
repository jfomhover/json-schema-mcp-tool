"""Validation service for JSON Schema validation."""

import copy

from jsonschema import ValidationError
from jsonschema import validate as jsonschema_validate

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
            if hasattr(e, "context") and e.context:
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

    def apply_defaults(self, document: dict) -> dict:
        """Apply default values from schema to document.

        Creates a new document with defaults applied. Does NOT modify original.

        Args:
            document: Document to apply defaults to

        Returns:
            New document with defaults applied
        """
        # Deep copy to avoid modifying original
        result = copy.deepcopy(document)

        # Apply defaults from schema
        self._apply_defaults_recursive(result, self.schema)

        return result

    def _apply_defaults_recursive(self, document: dict, schema: dict) -> None:
        """Recursively apply defaults from schema to document.

        Modifies document in place.

        Args:
            document: Document to apply defaults to
            schema: Schema containing default values
        """
        if not isinstance(schema, dict):
            return

        # Get properties and their defaults
        properties = schema.get("properties", {})

        for prop_name, prop_schema in properties.items():
            if "default" in prop_schema and prop_name not in document:
                # Apply default value
                document[prop_name] = copy.deepcopy(prop_schema["default"])
            elif prop_name in document and isinstance(prop_schema, dict):
                # Recursively apply defaults to nested objects
                if prop_schema.get("type") == "object" and isinstance(document[prop_name], dict):
                    self._apply_defaults_recursive(document[prop_name], prop_schema)
