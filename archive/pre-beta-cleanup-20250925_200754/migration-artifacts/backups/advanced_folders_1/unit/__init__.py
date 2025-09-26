"""
Unit tests initialization for Advanced Folders.
"""

# Import all test modules to ensure they're discovered
from . import (test_error_handling, test_exceptions, test_models,
               test_repository, test_validation_framework)

__all__ = [
    "test_exceptions",
    "test_validation_framework",
    "test_models",
    "test_repository",
    "test_error_handling"
]