"""Core detection and validation pipeline for centralized file validator."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

from .heuristics import (
    detect_pdf_by_token,
    inspect_zip_container,
    is_probably_text,
)
from .models import DetectionResult, ValidationResult
from .policy import evaluate_policy
from .signatures import iter_signatures
from .telemetry import emit_validation_event
from .utils import (
    canonicalise_allowed_types,
    guess_mime_type,
    normalise_extension,
    read_header,
)

_CANONICAL_EXTENSIONS = {
    "pdf": ".pdf",
    "png": ".png",
    "gif": ".gif",
    "jpg": ".jpg",
    "zip": ".zip",
    "docx": ".docx",
    "pptx": ".pptx",
    "xlsx": ".xlsx",
    "epub": ".epub",
    "pe": ".exe",
    "elf": "",
    "text": ".txt",
}


def _match_signature(header: bytes) -> Optional[DetectionResult]:
    for rule in iter_signatures():
        for magic in rule.magic:
            if header.startswith(magic):
                evidence = f"magic: {magic.hex().upper()}"
                return DetectionResult(
                    detected_type=rule.name,
                    confidence="high",
                    evidence=[evidence],
                    canonical_extension=rule.canonical_extension,
                )
    return None


def _refine_zip_detection(
    path: Path, detection: DetectionResult
) -> DetectionResult:
    refined_type, container_evidence = inspect_zip_container(path)
    if not refined_type:
        return detection
    canonical_extension = _CANONICAL_EXTENSIONS.get(
        refined_type,
        detection.canonical_extension,
    )
    evidence = list(detection.evidence) + [container_evidence]
    confidence = "high" if refined_type != "zip" else detection.confidence
    return DetectionResult(
        detected_type=refined_type,
        confidence=confidence,
        evidence=evidence,
        canonical_extension=canonical_extension,
    )


def _fallback_detection(path: Path, header: bytes) -> DetectionResult:
    evidence: List[str] = []
    if detect_pdf_by_token(header):
        evidence.append("heuristic: %PDF token")
        detected_type = "pdf"
        confidence = "medium"
        canonical_extension = ".pdf"
    elif is_probably_text(header):
        evidence.append("heuristic: text ascii ratio")
        detected_type = "text"
        confidence = "medium"
        canonical_extension = ".txt"
    else:
        mime = guess_mime_type(path)
        detected_type = mime or "unknown"
        canonical_extension = normalise_extension(path) if mime else ""
        evidence.append("fallback: mimetypes")
        confidence = "low"

    return DetectionResult(
        detected_type=detected_type,
        confidence=confidence,
        evidence=evidence,
        canonical_extension=canonical_extension,
    )


def detect_file_type(path: Path | str) -> DetectionResult:
    file_path = Path(path)
    header = read_header(file_path)

    detection = _match_signature(header)
    if detection:
        if detection.detected_type == "zip":
            detection = _refine_zip_detection(file_path, detection)
        return detection

    return _fallback_detection(file_path, header)


def validate_file_type(
    path: Path | str,
    *,
    allowed_types: Iterable[str] | None = None,
    mode: str = "reject",
    workflow: Optional[str] = None,
    emit_event: bool = True,
) -> ValidationResult:
    file_path = Path(path)
    detection = detect_file_type(file_path)

    allowed_set = canonicalise_allowed_types(allowed_types)
    is_match, action, reason = evaluate_policy(
        detection,
        allowed_types=allowed_set,
        mode=mode,
    )

    result = ValidationResult.from_detection(
        detection,
        is_match=is_match,
        action=action,
        reason=reason,
        requested_mode=mode,
        allowed_types=allowed_set,
    )

    if emit_event:
        emit_validation_event(result, workflow=workflow)

    return result
