"""Custom exceptions for centralized file validation."""
from __future__ import annotations


class FileValidationError(Exception):
    """Base exception for validator failures."""


class UnsupportedFileError(FileValidationError):
    """Raised when validation cannot determine a file's type."""


class InvalidModeError(FileValidationError):
    """Raised when validation is invoked with an unknown mode."""
