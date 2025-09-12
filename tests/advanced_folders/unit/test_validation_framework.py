"""
Unit tests for Advanced Folders validation framework.

Tests the extensible validation system with custom validators,
composition capabilities, and detailed error reporting.
"""

from typing import Any

import pytest

from src.rfu.advanced_folders.validation.validator_framework import (
    EXISTING_DIRECTORY, EXISTING_FILE, EXISTING_PATH, REQUIRED, BaseValidator,
    PathValidator, RequiredValidator, ValidationError, ValidationFramework,
    ValidationResult, ValidationSeverity)


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_valid_result_creation(self):
        """Test creation of valid result."""
        result = ValidationResult(is_valid=True, field="test_field")
        
        assert result.is_valid is True
        assert result.field == "test_field"
        assert result.errors == []
        assert result.warnings == []
    
    def test_invalid_result_creation(self):
        """Test creation of invalid result."""
        errors = [
            ValidationError("Field is required", "REQUIRED"),
            ValidationError("Field too long", "LENGTH")
        ]
        
        result = ValidationResult(
            is_valid=False,
            field="test_field",
            errors=errors
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 2
        assert result.errors[0].message == "Field is required"
    
    def test_result_with_warnings(self):
        """Test result with warnings."""
        warnings = [
            ValidationError("Field might be too long", "LENGTH_WARNING")
        ]
        
        result = ValidationResult(
            is_valid=True,
            field="test_field",
            warnings=warnings
        )
        
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "LENGTH_WARNING"
    
    def test_add_error(self):
        """Test adding error to result."""
        result = ValidationResult(is_valid=True, field="test")
        result.add_error("New error", "NEW_ERROR")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].message == "New error"
    
    def test_add_warning(self):
        """Test adding warning to result."""
        result = ValidationResult(is_valid=True, field="test")
        result.add_warning("New warning", "NEW_WARNING")
        
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.warnings[0].message == "New warning"


class TestValidationError:
    """Test ValidationError class."""
    
    def test_error_creation(self):
        """Test basic error creation."""
        error = ValidationError("Test error", "TEST_CODE")
        
        assert error.message == "Test error"
        assert error.code == "TEST_CODE"
        assert error.context == {}
    
    def test_error_with_context(self):
        """Test error creation with context."""
        context = {"field": "email", "value": "invalid"}
        error = ValidationError("Invalid email", "EMAIL_INVALID", context)
        
        assert error.context == context
        assert error.context["field"] == "email"


class TestRequiredValidator:
    """Test RequiredValidator."""
    
    def test_valid_required_value(self):
        """Test validation of valid required value."""
        validator = RequiredValidator()
        result = validator.validate("test_value", "test_field")
        
        assert result.is_valid is True
        assert result.field == "test_field"
        assert len(result.errors) == 0
    
    def test_none_value_fails(self):
        """Test that None value fails validation."""
        validator = RequiredValidator()
        result = validator.validate(None, "test_field")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "required" in result.errors[0].message.lower()
    
    def test_empty_string_fails(self):
        """Test that empty string fails validation."""
        validator = RequiredValidator()
        result = validator.validate("", "test_field")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
    
    def test_whitespace_string_fails(self):
        """Test that whitespace-only string fails validation."""
        validator = RequiredValidator()
        result = validator.validate("   ", "test_field")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
    
    def test_empty_list_fails(self):
        """Test that empty list fails validation."""
        validator = RequiredValidator()
        result = validator.validate([], "test_field")
        
        assert result.is_valid is False
        assert len(result.errors) == 1
    
    def test_non_empty_list_passes(self):
        """Test that non-empty list passes validation."""
        validator = RequiredValidator()
        result = validator.validate([1, 2, 3], "test_field")
        
        assert result.is_valid is True


class TestLengthValidator:
    """Test LengthValidator."""
    
    def test_valid_length_string(self):
        """Test string with valid length."""
        validator = LengthValidator(min_length=3, max_length=10)
        result = validator.validate("hello", "test_field")
        
        assert result.is_valid is True
    
    def test_string_too_short(self):
        """Test string that's too short."""
        validator = LengthValidator(min_length=5)
        result = validator.validate("hi", "test_field")
        
        assert result.is_valid is False
        assert "minimum" in result.errors[0].message.lower()
    
    def test_string_too_long(self):
        """Test string that's too long."""
        validator = LengthValidator(max_length=5)
        result = validator.validate("this is too long", "test_field")
        
        assert result.is_valid is False
        assert "maximum" in result.errors[0].message.lower()
    
    def test_exact_length_validation(self):
        """Test exact length validation."""
        validator = LengthValidator(exact_length=5)
        
        # Valid exact length
        result = validator.validate("hello", "test_field")
        assert result.is_valid is True
        
        # Invalid lengths
        result = validator.validate("hi", "test_field")
        assert result.is_valid is False
        
        result = validator.validate("hello world", "test_field")
        assert result.is_valid is False
    
    def test_list_length_validation(self):
        """Test length validation on lists."""
        validator = LengthValidator(min_length=2, max_length=5)
        
        result = validator.validate([1, 2, 3], "test_field")
        assert result.is_valid is True
        
        result = validator.validate([1], "test_field")
        assert result.is_valid is False
        
        result = validator.validate([1, 2, 3, 4, 5, 6], "test_field")
        assert result.is_valid is False


class TestPathValidator:
    """Test PathValidator."""
    
    def test_valid_absolute_path(self):
        """Test valid absolute path."""
        validator = PathValidator(must_exist=False, must_be_absolute=True)
        result = validator.validate("/home/user/documents", "test_field")
        
        assert result.is_valid is True
    
    def test_valid_relative_path(self):
        """Test valid relative path."""
        validator = PathValidator(must_exist=False, must_be_absolute=False)
        result = validator.validate("documents/file.txt", "test_field")
        
        assert result.is_valid is True
    
    def test_invalid_path_characters(self):
        """Test path with invalid characters."""
        validator = PathValidator(must_exist=False)
        result = validator.validate("path/with\x00null/byte", "test_field")
        
        assert result.is_valid is False
        assert "invalid" in result.errors[0].message.lower()
    
    def test_must_be_absolute_validation(self):
        """Test must_be_absolute validation."""
        validator = PathValidator(must_be_absolute=True)
        
        # Relative path should fail
        result = validator.validate("relative/path", "test_field")
        assert result.is_valid is False
        assert "absolute" in result.errors[0].message.lower()
    
    def test_allowed_extensions_validation(self):
        """Test allowed extensions validation."""
        validator = PathValidator(allowed_extensions={".txt", ".pdf"})
        
        # Valid extension
        result = validator.validate("/path/file.txt", "test_field")
        assert result.is_valid is True
        
        # Invalid extension
        result = validator.validate("/path/file.exe", "test_field")
        assert result.is_valid is False
        assert "extension" in result.errors[0].message.lower()
    
    def test_blocked_paths_validation(self):
        """Test blocked paths validation."""
        validator = PathValidator(blocked_paths={"/system", "/windows"})
        
        # Blocked path should fail
        result = validator.validate("/system/file.txt", "test_field")
        assert result.is_valid is False
        assert "blocked" in result.errors[0].message.lower()


class TestRegexValidator:
    """Test RegexValidator."""
    
    def test_valid_regex_match(self):
        """Test valid regex match."""
        validator = RegexValidator(r"^[a-zA-Z0-9]+$", "alphanumeric only")
        result = validator.validate("hello123", "test_field")
        
        assert result.is_valid is True
    
    def test_invalid_regex_match(self):
        """Test invalid regex match."""
        validator = RegexValidator(r"^[a-zA-Z0-9]+$", "alphanumeric only")
        result = validator.validate("hello-world!", "test_field")
        
        assert result.is_valid is False
        assert "alphanumeric only" in result.errors[0].message
    
    def test_email_regex_validation(self):
        """Test email regex validation."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        validator = RegexValidator(email_pattern, "valid email format")
        
        # Valid emails
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@sub.domain.org"
        ]
        
        for email in valid_emails:
            result = validator.validate(email, "email")
            assert result.is_valid is True, f"Email {email} should be valid"
        
        # Invalid emails
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user space@domain.com"
        ]
        
        for email in invalid_emails:
            result = validator.validate(email, "email")
            assert result.is_valid is False, f"Email {email} should be invalid"


class TestRangeValidator:
    """Test RangeValidator."""
    
    def test_valid_number_range(self):
        """Test valid number in range."""
        validator = RangeValidator(min_value=1, max_value=10)
        result = validator.validate(5, "test_field")
        
        assert result.is_valid is True
    
    def test_number_below_minimum(self):
        """Test number below minimum."""
        validator = RangeValidator(min_value=5)
        result = validator.validate(3, "test_field")
        
        assert result.is_valid is False
        assert "minimum" in result.errors[0].message.lower()
    
    def test_number_above_maximum(self):
        """Test number above maximum."""
        validator = RangeValidator(max_value=10)
        result = validator.validate(15, "test_field")
        
        assert result.is_valid is False
        assert "maximum" in result.errors[0].message.lower()
    
    def test_boundary_values(self):
        """Test boundary values."""
        validator = RangeValidator(min_value=5, max_value=10)
        
        # Boundary values should be valid
        result = validator.validate(5, "test_field")
        assert result.is_valid is True
        
        result = validator.validate(10, "test_field")
        assert result.is_valid is True
        
        # Outside boundaries should be invalid
        result = validator.validate(4, "test_field")
        assert result.is_valid is False
        
        result = validator.validate(11, "test_field")
        assert result.is_valid is False


class TestTypeValidator:
    """Test TypeValidator."""
    
    def test_valid_type(self):
        """Test valid type validation."""
        validator = TypeValidator(str)
        result = validator.validate("hello", "test_field")
        
        assert result.is_valid is True
    
    def test_invalid_type(self):
        """Test invalid type validation."""
        validator = TypeValidator(str)
        result = validator.validate(123, "test_field")
        
        assert result.is_valid is False
        assert "type" in result.errors[0].message.lower()
    
    def test_multiple_allowed_types(self):
        """Test multiple allowed types."""
        validator = TypeValidator((str, int))
        
        # Both types should be valid
        result = validator.validate("hello", "test_field")
        assert result.is_valid is True
        
        result = validator.validate(123, "test_field")
        assert result.is_valid is True
        
        # Other types should be invalid
        result = validator.validate(12.34, "test_field")
        assert result.is_valid is False


class TestCompositeValidator:
    """Test CompositeValidator."""
    
    def test_all_validators_pass(self):
        """Test when all validators pass."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=3, max_length=10),
            RegexValidator(r"^[a-zA-Z]+$", "letters only")
        ]
        
        composite = CompositeValidator(validators)
        result = composite.validate("hello", "test_field")
        
        assert result.is_valid is True
    
    def test_one_validator_fails(self):
        """Test when one validator fails."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=10),  # This will fail
            RegexValidator(r"^[a-zA-Z]+$", "letters only")
        ]
        
        composite = CompositeValidator(validators)
        result = composite.validate("hello", "test_field")
        
        assert result.is_valid is False
        assert len(result.errors) >= 1
    
    def test_multiple_validators_fail(self):
        """Test when multiple validators fail."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=10),  # Will fail
            RegexValidator(r"^[0-9]+$", "numbers only")  # Will fail
        ]
        
        composite = CompositeValidator(validators)
        result = composite.validate("hello", "test_field")
        
        assert result.is_valid is False
        assert len(result.errors) >= 2


class TestValidationFramework:
    """Test ValidationFramework class."""
    
    def test_framework_creation(self):
        """Test framework creation."""
        framework = ValidationFramework()
        assert framework is not None
    
    def test_register_validator(self):
        """Test registering a validator."""
        framework = ValidationFramework()
        validator = RequiredValidator()
        
        framework.register_validator("test_field", validator)
        
        # Should not raise an exception
        assert True
    
    def test_validate_single_field(self):
        """Test validating a single field."""
        framework = ValidationFramework()
        framework.register_validator("name", RequiredValidator())
        
        data = {"name": "John Doe"}
        results = framework.validate(data)
        
        assert "name" in results
        assert results["name"].is_valid is True
    
    def test_validate_multiple_fields(self):
        """Test validating multiple fields."""
        framework = ValidationFramework()
        framework.register_validator("name", RequiredValidator())
        framework.register_validator("email", RegexValidator(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "valid email"
        ))
        
        data = {
            "name": "John Doe",
            "email": "john@example.com"
        }
        
        results = framework.validate(data)
        
        assert len(results) == 2
        assert results["name"].is_valid is True
        assert results["email"].is_valid is True
    
    def test_validate_with_errors(self):
        """Test validation with errors."""
        framework = ValidationFramework()
        framework.register_validator("name", RequiredValidator())
        framework.register_validator("age", RangeValidator(min_value=0, max_value=150))
        
        data = {
            "name": "",  # Invalid: empty
            "age": 200   # Invalid: too high
        }
        
        results = framework.validate(data)
        
        assert results["name"].is_valid is False
        assert results["age"].is_valid is False
    
    def test_validate_missing_field(self):
        """Test validation when field is missing from data."""
        framework = ValidationFramework()
        framework.register_validator("required_field", RequiredValidator())
        
        data = {}  # Missing required_field
        results = framework.validate(data)
        
        assert "required_field" in results
        assert results["required_field"].is_valid is False
    
    def test_is_valid_overall(self):
        """Test overall validation status."""
        framework = ValidationFramework()
        framework.register_validator("name", RequiredValidator())
        framework.register_validator("age", RangeValidator(min_value=0))
        
        # All valid
        valid_data = {"name": "John", "age": 25}
        results = framework.validate(valid_data)
        assert framework.is_valid(results) is True
        
        # One invalid
        invalid_data = {"name": "", "age": 25}
        results = framework.validate(invalid_data)
        assert framework.is_valid(results) is False
    
    def test_get_error_summary(self):
        """Test getting error summary."""
        framework = ValidationFramework()
        framework.register_validator("name", RequiredValidator())
        framework.register_validator("email", RegexValidator(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "valid email"
        ))
        
        data = {"name": "", "email": "invalid-email"}
        results = framework.validate(data)
        
        errors = framework.get_error_summary(results)
        
        assert len(errors) == 2
        assert any("name" in error for error in errors)
        assert any("email" in error for error in errors)


class TestValidationEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_validate_none_data(self):
        """Test validation with None data."""
        framework = ValidationFramework()
        framework.register_validator("test", RequiredValidator())
        
        results = framework.validate(None)
        assert "test" in results
        assert results["test"].is_valid is False
    
    def test_validate_empty_data(self):
        """Test validation with empty data."""
        framework = ValidationFramework()
        framework.register_validator("test", RequiredValidator())
        
        results = framework.validate({})
        assert "test" in results
        assert results["test"].is_valid is False
    
    def test_validator_exception_handling(self):
        """Test that validator exceptions are handled gracefully."""
        class FailingValidator(BaseValidator):
            def validate(self, value: Any, field: str) -> ValidationResult:
                raise ValueError("Validator failed")
        
        framework = ValidationFramework()
        framework.register_validator("test", FailingValidator())
        
        # Should not raise exception, but should return invalid result
        results = framework.validate({"test": "value"})
        assert results["test"].is_valid is False
        assert "error" in results["test"].errors[0].message.lower()


if __name__ == "__main__":
    pytest.main([__file__])