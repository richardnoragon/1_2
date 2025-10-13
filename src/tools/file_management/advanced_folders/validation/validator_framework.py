"""
Advanced validation framework for folder configurations and search parameters.

This module provides a comprehensive, extensible validation system designed for
enterprise-grade applications. It supports custom validators, composite validation
rules, and detailed error reporting with context preservation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ValidationSeverity(Enum):
    """Severity levels for validation messages."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationError:
    """Individual validation error."""

    message: str
    code: str
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize default context."""
        if self.context is None:
            self.context = {}


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    is_valid: bool
    field: str = ""
    errors: Optional[List[ValidationError]] = None
    warnings: Optional[List[ValidationError]] = None

    def __post_init__(self):
        """Initialize default lists."""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    def add_error(
        self, message: str, code: str, context: Optional[Dict[str, Any]] = None
    ):
        """Add an error to the result."""
        if self.errors is None:
            self.errors = []
        self.errors.append(ValidationError(message, code, context))
        self.is_valid = False

    def add_warning(
        self, message: str, code: str, context: Optional[Dict[str, Any]] = None
    ):
        """Add a warning to the result."""
        if self.warnings is None:
            self.warnings = []
        self.warnings.append(ValidationError(message, code, context))


class BaseValidator(ABC):
    """Abstract base class for all validators."""

    def __init__(self, name: str, message: Optional[str] = None):
        """
        Initialize validator.

        Args:
            name: Validator name for identification
            message: Custom error message template
        """
        self.name = name
        self.message = message or "Validation failed"

    @abstractmethod
    def validate(
        self, value: Any, field_name: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a value.

        Args:
            value: Value to validate
            field_name: Name of the field being validated

        Returns:
            ValidationResult with validation outcome
        """
        pass

    def __call__(
        self, value: Any, field_name: Optional[str] = None
    ) -> ValidationResult:
        """Allow validator to be called as a function."""
        return self.validate(value, field_name)


class RequiredValidator(BaseValidator):
    """Validator for required fields."""

    def __init__(self, message: Optional[str] = None):
        super().__init__("required", message or "This field is required")

    def validate(
        self, value: Any, field_name: Optional[str] = None
    ) -> ValidationResult:
        """Check if value is provided and not empty."""
        is_valid = value is not None and (
            not isinstance(value, str) or bool(value.strip())
        )

        result = ValidationResult(is_valid=is_valid, field=field_name or "")
        if not is_valid:
            result.add_error(
                self.message,
                "REQUIRED_FIELD_MISSING",
                {"field": field_name, "value": value},
            )

        return result


class PathValidator(BaseValidator):
    """Validator for file system paths."""

    def __init__(
        self,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_directory: bool = False,
        message: Optional[str] = None,
    ):
        """
        Initialize path validator.

        Args:
            must_exist: Whether path must exist
            must_be_file: Whether path must be a file
            must_be_directory: Whether path must be a directory
            message: Custom error message
        """
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_directory = must_be_directory

        super().__init__("path", message or "Invalid path")

    def validate(
        self, value: Any, field_name: Optional[str] = None
    ) -> ValidationResult:
        """Validate file system path."""
        result = ValidationResult(is_valid=True, field=field_name or "")

        if not isinstance(value, (str, Path)):
            result.add_error(
                "Value must be a string or Path object",
                "INVALID_TYPE",
                {
                    "field": field_name,
                    "value": value,
                    "expected_type": "str or Path",
                },
            )
            return result

        try:
            path = Path(value)

            if self.must_exist and not path.exists():
                result.add_error(
                    f"Path does not exist: {path}",
                    "PATH_NOT_EXISTS",
                    {"field": field_name, "path": str(path)},
                )

            if self.must_be_file and path.exists() and not path.is_file():
                result.add_error(
                    f"Path is not a file: {path}",
                    "PATH_NOT_FILE",
                    {"field": field_name, "path": str(path)},
                )

            if self.must_be_directory and path.exists() and not path.is_dir():
                result.add_error(
                    f"Path is not a directory: {path}",
                    "PATH_NOT_DIRECTORY",
                    {"field": field_name, "path": str(path)},
                )

        except (OSError, ValueError) as e:
            result.add_error(
                f"Invalid path format: {e}",
                "INVALID_PATH_FORMAT",
                {"field": field_name, "value": value, "error": str(e)},
            )

        return result


# Common validator instances for reuse
REQUIRED = RequiredValidator()
EXISTING_PATH = PathValidator(must_exist=True)
EXISTING_FILE = PathValidator(must_exist=True, must_be_file=True)
EXISTING_DIRECTORY = PathValidator(must_exist=True, must_be_directory=True)


def validate_data_structure(
    data: Dict[str, Any], validators: Dict[str, BaseValidator]
) -> Dict[str, ValidationResult]:
    """
    Validate an entire data structure.

    Args:
        data: Dictionary of data to validate
        validators: Dictionary mapping field names to validators

    Returns:
        Dictionary mapping field names to validation results
    """
    results = {}

    for field_name, validator in validators.items():
        value = data.get(field_name)
        results[field_name] = validator.validate(value, field_name)

    return results


def has_validation_errors(results: Dict[str, ValidationResult]) -> bool:
    """
    Check if any validation results contain errors.

    Args:
        results: Dictionary of validation results

    Returns:
        True if any results contain errors
    """
    return any(not result.is_valid for result in results.values())


def get_all_errors(
    results: Dict[str, ValidationResult],
) -> List[ValidationError]:
    """
    Get all errors from validation results.

    Args:
        results: Dictionary of validation results

    Returns:
        List of all validation errors
    """
    errors = []
    for result in results.values():
        if result.errors:
            errors.extend(result.errors)
    return errors


class ValidationFramework:
    """Main validation framework orchestrator."""

    def __init__(self):
        """Initialize validation framework."""
        self.validators = {}

    def add_validator(self, field_name: str, validator: BaseValidator):
        """Add a validator for a specific field."""
        self.validators[field_name] = validator

    def validate(self, data: Dict[str, Any]) -> Dict[str, ValidationResult]:
        """Validate data using registered validators."""
        return validate_data_structure(data, self.validators)

    def is_valid(self, data: Dict[str, Any]) -> bool:
        """Check if data is valid."""
        results = self.validate(data)
        return not has_validation_errors(results)
