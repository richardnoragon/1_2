"""Compatibility helpers bridging legacy validators to the centralized API."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Tuple

from .detector import detect_file_type, validate_file_type
from .models import DetectionResult, ValidationResult
from .utils import canonicalise_allowed_types

LegacyValidationOutcome = Tuple[bool, str, ValidationResult]


def legacy_detect(path: Path | str) -> dict[str, object]:
    """Return the legacy payload for a detection request."""

    detection = detect_file_type(path)
    return detection.to_dict()


def legacy_validate(
    path: Path | str,
    *,
    allowed_types: Optional[Iterable[str]] = None,
    mode: str = "reject",
    workflow: Optional[str] = None,
    emit_event: bool = True,
) -> LegacyValidationOutcome:
    """Replicate the legacy tuple response used by historical helpers."""

    canonical = canonicalise_allowed_types(allowed_types)
    validation = validate_file_type(
        path,
        allowed_types=canonical,
        mode=mode,
        workflow=workflow,
        emit_event=emit_event,
    )
    allowed = validation.action != "reject"
    return allowed, validation.reason, validation


def is_allowed(
    path: Path | str,
    *,
    allowed_types: Optional[Iterable[str]] = None,
    mode: str = "reject",
    workflow: Optional[str] = None,
) -> bool:
    """Return whether the validator accepts a file using legacy semantics."""

    allowed, _, _ = legacy_validate(
        path,
        allowed_types=allowed_types,
        mode=mode,
        workflow=workflow,
        emit_event=False,
    )
    return allowed


def validation_payload(validation: ValidationResult) -> dict[str, object]:
    """Return a serialisable payload mirroring the legacy dictionary output."""

    payload = validation.to_dict()
    payload.update(
        {
            "is_allowed": validation.action != "reject",
            "detected_type": validation.detection.detected_type,
            "confidence": validation.detection.confidence,
            "evidence": list(validation.detection.evidence),
        }
    )
    return payload


__all__ = [
    "LegacyValidationOutcome",
    "legacy_detect",
    "legacy_validate",
    "is_allowed",
    "validation_payload",
    "DetectionResult",
    "ValidationResult",
]
