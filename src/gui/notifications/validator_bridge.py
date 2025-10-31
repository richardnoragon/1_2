"""Bridge module translating validator results into GUI notifications."""
from __future__ import annotations

from typing import Any, Dict

from src.file_validator.models import ValidationResult


_LEVEL_BY_ACTION = {
    "reject": "critical",
    "warn": "warning",
    "accept": "info",
}


def _build_message(validation: ValidationResult) -> str:
    if validation.action == "reject":
        return "High-risk mismatch detected"
    if validation.action == "warn":
        return "File mismatch requires review"
    return "File validated successfully"


def _build_details(validation: ValidationResult) -> Dict[str, Any]:
    return {
        "action": validation.action,
        "reason": validation.reason,
        "detected_type": validation.detection.detected_type,
        "confidence": validation.detection.confidence,
        "allowed_types": sorted(validation.allowed_types),
    }


def dispatch_validator_alert(
    validation: ValidationResult,
    notifier,
    *,
    workflow: str,
) -> None:
    """Send the validator outcome to the GUI notification system."""
    level = _LEVEL_BY_ACTION.get(validation.action, "info")
    message = _build_message(validation)
    details = _build_details(validation)
    notifier.push(
        level=level,
        message=message,
        workflow=workflow,
        details=details,
    )
