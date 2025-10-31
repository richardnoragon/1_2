"""Telemetry helpers for centralized file validator."""
from __future__ import annotations

from typing import Optional

from src.log_manager import get_log_manager

from .models import ValidationResult


def emit_validation_event(
    validation: ValidationResult,
    *,
    workflow: Optional[str] = None,
) -> None:
    """Emit a structured telemetry record for a validation result."""
    logger = get_log_manager().get_logger("file_validator.telemetry")
    payload = {
        "workflow": workflow or "unknown",
        "action": validation.action,
        "is_match": validation.is_match,
        "reason": validation.reason,
        "detected_type": validation.detection.detected_type,
        "confidence": validation.detection.confidence,
        "allowed_types": sorted(validation.allowed_types),
        "evidence": list(validation.detection.evidence),
    }
    logger.info(
        "file_validator.validation",
        extra={"validation": payload},
    )
