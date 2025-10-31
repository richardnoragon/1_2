"""Data models for the centralized file validator."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence, Set


ConfidenceLevel = str
ActionType = str


@dataclass(frozen=True)
class DetectionResult:
    """Represents the outcome of inspecting a file's true content type."""

    detected_type: str
    confidence: ConfidenceLevel
    evidence: Sequence[str] = field(default_factory=list)
    canonical_extension: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "detected_type": self.detected_type,
            "confidence": self.confidence,
            "evidence": list(self.evidence),
            "canonical_extension": self.canonical_extension,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Represents the policy decision produced by the validator."""

    is_match: bool
    action: ActionType
    reason: str
    detection: DetectionResult
    requested_mode: str
    allowed_types: Set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "is_match": self.is_match,
            "action": self.action,
            "reason": self.reason,
            "requested_mode": self.requested_mode,
            "allowed_types": sorted(self.allowed_types),
            "detection": self.detection.to_dict(),
        }
        return payload

    @classmethod
    def from_detection(
        cls,
        detection: DetectionResult,
        *,
        is_match: bool,
        action: str,
        reason: str,
        requested_mode: str,
        allowed_types: Iterable[str] | None = None,
    ) -> "ValidationResult":
        return cls(
            is_match=is_match,
            action=action,
            reason=reason,
            detection=detection,
            requested_mode=requested_mode,
            allowed_types=set(allowed_types or ()),
        )
