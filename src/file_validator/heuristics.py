"""Secondary heuristics for file detection."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import zipfile


_TEXT_BYTES = set(range(32, 127)) | {9, 10, 13}


def is_probably_text(header: bytes, threshold: float = 0.9) -> bool:
    if not header:
        return False
    printable = sum(1 for byte in header if byte in _TEXT_BYTES)
    return (printable / len(header)) >= threshold


def detect_pdf_by_token(header: bytes) -> bool:
    return b"%PDF-" in header[:512]


def inspect_zip_container(path: Path) -> Tuple[Optional[str], Optional[str]]:
    if not zipfile.is_zipfile(path):
        return None, None
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
    except Exception:
        return None, None

    lowered = [name.lower() for name in names]
    if any(name.startswith("word/") for name in lowered):
        return "docx", "container: word/"
    if any(name.startswith("ppt/") for name in lowered):
        return "pptx", "container: ppt/"
    if any(name.startswith("xl/") for name in lowered):
        return "xlsx", "container: xl/"
    if "mimetype" in lowered and "meta-inf/container.xml" in lowered:
        return "epub", "container: epub"
    return "zip", "container: zip"


EXECUTABLE_TYPES = {"pe", "elf"}


def is_high_risk_executable(detected_type: str) -> bool:
    return detected_type in EXECUTABLE_TYPES
