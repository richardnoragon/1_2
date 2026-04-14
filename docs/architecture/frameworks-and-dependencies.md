# RFU — Frameworks & Dependencies Inventory

**Version**: 1.0.0
**Date**: 2026-03-11
**Spec**: [specs/007-ui-harmonization](../../specs/007-ui-harmonization/spec.md)
**Maintained by**: update this file in the same PR as any version or role change (FR-014).

---

## How to Use This Document

- **Framework** — a library that dictates the overall structure of the application (GUI toolkit, test runner).  
- **Dependency** — a library that performs a well-scoped task and is consumed by one or more modules.  
- **Version policy**: all versions are pinned with `==` in `requirements.txt`.  No ranges.  
- **When adding a new dependency**: see [packaging-style.md](packaging-style.md) §Adding a New Dependency.

---

## 1. GUI Framework

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `PyQt5` | 5.15.11 | Primary GUI toolkit — all windows, widgets, dialogs | LTS branch; wide platform support (Windows, macOS, Linux); stable Python 3.12 bindings |
| `PyQt5-Qt5` | 5.15.2 | Qt5 binary runtime shipped with PyQt5 wheels | Required by PyQt5 installer; version must stay in sync with PyQt5 |
| `PyQt5-sip` | 12.17.0 | SIP binding layer between Python and Qt C++ | Required by PyQt5; pinned separately to avoid ABI breakage |

**Minimum acceptable**: PyQt5 ≥ 5.15.9 (earlier 5.15.x releases lack several `QFont` fixes used by `FontPickerDialog`).

---

## 2. Identity & Security

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `cryptography` | 44.0.2 | Secret handling, token signing, envelope encryption for sensitive preferences | Gold-standard Python cryptography library; actively maintained by PyCA |
| `argon2-cffi` | 23.1.0 | Argon2id password hashing (Constitution §VII) | OWASP-recommended KDF; memory-hard against GPU attacks |
| `argon2-cffi-bindings` | 21.2.0 | Native C bindings for argon2-cffi | Required by argon2-cffi; must stay version-matched |
| `cffi` | 1.17.1 | C foreign-function interface, used by argon2 and cryptography | Transitive; pinned to prevent ABI mismatches |
| `pyOpenSSL` | 25.0.0 | SSL/TLS support for enterprise network tools | Wraps OpenSSL for secure socket operations |
| `pycryptodomex` | 3.22.0 | Additional cipher algorithms (AES-GCM, RSA, etc.) | Supplemental to `cryptography`; used by encryption tool |
| `pyAesCrypt` | 6.1.1 | AES file-level encryption/decryption | Used directly by Encrypt/Decrypt tool for `.aes` format |

---

## 3. Testing

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `pytest` | 8.3.5 | Primary test runner | Ecosystem standard; extensive plugin support |
| `pytest-qt` | 4.4.0 | PyQt5 widget testing and offscreen rendering | Provides `qtbot`, offscreen platform for CI |
| `pytest-cov` | 6.1.0 | Code coverage measurement and reporting | Enforces ≥ 85% gate (Constitution §III) |
| `pytest-html` | 4.1.1 | HTML test report generation | Human-readable CI artifacts |
| `pytest-mock` | 3.14.0 | Mock/patch helpers | Enables unit testing without live QApplication |
| `pytest-asyncio` | 0.26.0 | Async test support | For async IO helpers in network tools |
| `pytest-benchmark` | 4.0.0 | Performance benchmarking | Validates UAP apply ≤ 50ms, theme propagation ≤ 500ms |
| `pytest-timeout` | 2.3.1 | Per-test execution timeout | Prevents hanging GUI tests in CI |
| `pytest-xdist` | 3.6.0 | Parallel test execution | Reduces CI wall-clock time |
| `pytest-randomly` | 3.16.0 | Random test-order execution | Detects order-dependent failures |
| `pytest-order` | 1.2.1 | Explicit ordering for identity contract gate | Ensures auth setup runs before auth tests |
| `pytest-dependency` | 0.6.0 | Express test prerequisites | Skips dependent tests when prerequisite fails |
| `pytest-json-report` | 1.5.0 | JSON output for programmatic result parsing | Used by CI pipeline |
| `pytest-metadata` | 3.1.1 | Attach metadata to test sessions | Records Python/PyQt5 versions in reports |
| `pytest-sugar` | 1.0.0 | Enhanced console output (progress bar) | Developer experience |
| `factory-boy` | 3.3.1 | Test data factories for model objects | Reduces boilerplate in fixture setup |
| `Faker` | 33.1.0 | Synthetic test data generation | Realistic file paths, names, sizes |
| `PyVirtualDisplay` | 3.0 | Virtual display for headless GUI testing | Fallback when offscreen platform is unavailable |

---

## 4. Document & Data Processing

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `pandas` | 2.2.3 | Tabular data analysis (catalog, metadata export) | Industry standard; required by Catalog and Size Analyzer tools |
| `numpy` | 2.2.4 | Numerical computing; array operations | Dependency of pandas and opencv |
| `openpyxl` | 3.1.5 | Read/write `.xlsx` files | Used by catalog export and data analysis tools |
| `python-docx` | 1.1.2 | Read/write `.docx` Word documents | Used by document processing tools |
| `lxml` | 5.3.1 | Fast XML/HTML parsing | Dependency of python-docx and direct use in metadata tools |
| `beautifulsoup4` | 4.12.3 | HTML parsing and scraping | Used by help system and web-based tool outputs |
| `PyYAML` | 6.0.2 | YAML parsing for authentication contracts | Authentication contract files use YAML format |
| `types-PyYAML` | 6.0.12.20240917 | Type stubs for PyYAML | MyPy static analysis |

---

## 5. PDF Tools

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `PyMuPDF` | 1.25.4 | Primary PDF rendering and manipulation engine | Fastest Python PDF library; supports text extraction, rendering, merging |
| `PyPDF2` | 3.0.1 | Legacy PDF read/write operations | Retained for compatibility with existing tool code |
| `PyPDF4` | 1.27.0 | Extended PDF support (forms, annotations) | Used by PDF form-fill tool |
| `pikepdf` | 9.5.2 | Advanced PDF operations (encryption, repair, optimization) | Built on libqpdf; handles malformed PDFs |

---

## 6. File & Archive Operations

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `Pillow` | 11.1.0 | Image reading, writing, thumbnail generation, EXIF | Swiss-army-knife image library |
| `piexif` | 1.1.3 | EXIF metadata read/write | Lightweight complement to Pillow for EXIF editing |
| `opencv-python-headless` | 4.11.0.86 | Computer vision operations (headless — no GUI) | Used by image analysis tools; headless avoids Qt conflict |
| `mutagen` | 1.47.0 | Audio file metadata (MP3, FLAC, OGG, M4A) | Used by media file catalog tool |
| `py7zr` | 1.0.0 | 7-Zip archive creation and extraction | Used by Compression tool |
| `pyzstd` | 0.16.2 | Zstandard compression | High-ratio compression for backup archives |
| `multivolumefile` | 0.2.3 | Multi-volume archive support | Required by py7zr for spanning volumes |
| `Brotli` | 1.1.0 | Brotli compression algorithm | Web-content-compatible compression |
| `inflate64` | 1.0.1 | Enhanced ZIP decompression (Deflate64) | Required for some Windows-generated ZIP archives |
| `python-magic` | 0.4.27 | File type detection via magic bytes | Used by File Validator (content-based detection) |
| `python-magic-bin` | 0.4.14 | libmagic binary for Linux | Platform-conditional (`sys_platform=="linux"`) |
| `Send2Trash` | 1.8.3 | Cross-platform safe file deletion (to OS trash) | Used by tools that need reversible delete |
| `chardet` | 5.2.0 | Character encoding auto-detection | Required for text files with unknown encoding |
| `fuzzywuzzy` | 0.18.0 | Fuzzy string matching for duplicate detection | Used by Duplicate Finder |
| `python-Levenshtein` | 0.26.0 | Fast Levenshtein distance computation | Speeds up fuzzywuzzy operations |

---

## 7. System & Network

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `psutil` | 7.0.0 | Cross-platform system and process info | Used by System Diagnostics and Process Monitor tools |
| `watchdog` | 6.0.0 | File system event monitoring | Used by Sync & Backup for live change detection |
| `requests` | 2.32.3 | HTTP client | Used by network tools and update-check logic |
| `urllib3` | 2.2.3 | URL handling layer for requests | Pinned separately; requests depends on it |
| `paramiko` | 3.5.0 | SSH client (SFTP, remote file transfer) | Used by File Transfer tool |
| `netifaces` | 0.11.0 | Network interface enumeration | Platform-conditional (`sys_platform != "win32"`) |
| `pywin32` | 308 | Windows API access (shell, registry, COM) | Windows-conditional; used by system and security tools |
| `wmi` | 1.5.1 | Windows Management Instrumentation | Windows-conditional; used by system diagnostics |
| `pyobjc-framework-Cocoa` | 10.3.1 | macOS AppKit / Cocoa integration | macOS-conditional; used for native macOS UI features |

---

## 8. Code Quality & Tooling

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `black` | 25.1.0 | Opinionated code formatter | Ensures consistent style; enforced by pre-commit |
| `isort` | 5.13.2 | Import sorting | Keeps imports ordered; black-compatible mode |
| `flake8` | 7.2.0 | PEP 8 linting | Catches style violations and simple bugs |
| `mypy` | 1.15.0 | Static type checking | Prevents type-related runtime errors |
| `pre-commit` | 4.0.1 | Git pre-commit hook runner | Runs black, isort, flake8 before every commit |
| `memory-profiler` | 0.61.0 | Memory usage profiling | Used during performance-sensitive development |
| `line-profiler` | 4.2.0 | Line-by-line profiling | Used for targeted performance investigation |

---

## 9. CLI & Utilities

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `fire` | 0.7.0 | CLI interface from Python functions | Used by maintenance and audit scripts |
| `click` | 8.1.8 | Command-line interface framework | Used by scripts requiring rich CLI (progress, prompts) |
| `termcolor` | 2.5.0 | Colored terminal output | Used by CLI scripts for readable output |
| `colorama` | 0.4.6 | Cross-platform ANSI color support | Required for `termcolor` to work on Windows |

---

## 10. Documentation

| Package | Pinned Version | Role | Rationale |
|---|---|---|---|
| `sphinx` | 8.1.3 | API documentation generation | Generates HTML/PDF docs from docstrings |
| `sphinx-rtd-theme` | 3.0.2 | Read-the-Docs Sphinx theme | Enterprise-grade documentation appearance |

---

## 11. Type Stubs

| Package | Pinned Version | Role |
|---|---|---|
| `types-PyYAML` | 6.0.12.20240917 | MyPy stubs for PyYAML |
| `types-requests` | 2.32.0.20241016 | MyPy stubs for requests |

---

## Version Change Procedure

1. Update the pinned version in `requirements.txt`.
2. Update the row in this document (version + rationale note if the role changed).
3. Run `python scripts/check_dependencies.py` to confirm the new version is installed.
4. Run the full test suite (`python -m pytest tests/ -v`) in the affected virtual environment.
5. Include this document update in the same PR as the code change.

---

## Minimum Acceptable Versions (quick reference)

| Package | Minimum | Notes |
|---|---|---|
| `PyQt5` | 5.15.9 | `QFont` fixes required by FontPickerDialog |
| `cryptography` | 42.0.0 | API changes before 42 break envelope encryption |
| `argon2-cffi` | 21.3.0 | Argon2id algorithm stability |
| `pytest` | 8.0.0 | `pytest-order` plugin compatibility |
| `pytest-qt` | 4.4.0 | Offscreen platform required for CI |
| `PyMuPDF` | 1.24.0 | Python 3.12 wheel availability |
| `pikepdf` | 9.0.0 | QPDF 11 backend required |
