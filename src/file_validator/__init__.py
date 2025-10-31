"""Public API surface for the centralized file validator."""
from __future__ import annotations

from .detector import detect_file_type, validate_file_type
from .models import DetectionResult, ValidationResult

__all__ = [
    "detect_file_type",
    "validate_file_type",
    "DetectionResult",
    "ValidationResult",
]
