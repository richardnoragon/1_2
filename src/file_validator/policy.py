"""Policy evaluation logic for centralized file validation."""
from __future__ import annotations

from typing import Iterable, Set, Tuple

from .exceptions import InvalidModeError
from .heuristics import is_high_risk_executable
from .models import DetectionResult
from .utils import canonicalise_allowed_types

MATCH_ACTION = "accept"
WARN_ACTION = "warn"
REJECT_ACTION = "reject"


def _is_allowed(detection: DetectionResult, allowed: Set[str]) -> bool:
    detected = detection.detected_type.lower()
    canonical = (detection.canonical_extension or "").lstrip(".")
    return detected in allowed or (canonical and canonical in allowed)


def evaluate_policy(
    detection: DetectionResult,
    *,
    allowed_types: Iterable[str] | None,
    mode: str,
) -> Tuple[bool, str, str]:
    allowed_set = canonicalise_allowed_types(allowed_types)
    allowed_set = {item for item in allowed_set if item}

    is_allowed = _is_allowed(detection, allowed_set) or not allowed_set

    if mode not in {"reject", "warn", "auto"}:
        raise InvalidModeError(f"Unsupported validation mode: {mode}")

    if is_allowed:
        reason = "Detected type is within the allowed policy set"
        return True, MATCH_ACTION, reason

    # mismatch handling
    if mode == "reject":
        return False, REJECT_ACTION, "Mismatch rejected per policy"

    if mode == "warn":
        return False, WARN_ACTION, "Mismatch reported as warning"

    # auto mode
    assert mode == "auto"
    if is_high_risk_executable(detection.detected_type):
        return False, REJECT_ACTION, "High-risk mismatch escalated to reject"

    return False, WARN_ACTION, "Mismatch downgraded to warning"
