"""Curated magic numbers used by the centralized file validator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Sequence


@dataclass(frozen=True)
class SignatureRule:
    name: str
    magic: Sequence[bytes]
    canonical_extension: str


def _b(hex_string: str) -> bytes:
    return bytes.fromhex(hex_string)


SIGNATURES: Dict[str, SignatureRule] = {
    "pdf": SignatureRule(
        name="pdf",
        magic=[b"%PDF-"],
        canonical_extension=".pdf",
    ),
    "png": SignatureRule(
        name="png",
        magic=[_b("89504E470D0A1A0A")],
        canonical_extension=".png",
    ),
    "gif": SignatureRule(
        name="gif",
        magic=[b"GIF87a", b"GIF89a"],
        canonical_extension=".gif",
    ),
    "jpg": SignatureRule(
        name="jpg",
        magic=[_b("FFD8FF")],
        canonical_extension=".jpg",
    ),
    "zip": SignatureRule(
        name="zip",
        magic=[b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"],
        canonical_extension=".zip",
    ),
    "pe": SignatureRule(
        name="pe",
        magic=[b"MZ"],
        canonical_extension=".exe",
    ),
    "elf": SignatureRule(
        name="elf",
        magic=[b"\x7fELF"],
        canonical_extension="",
    ),
}


def iter_signatures() -> Iterable[SignatureRule]:
    return SIGNATURES.values()
