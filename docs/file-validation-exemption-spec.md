# File Validation Exemption — "Written by RFU Itself" Boundary Specification

**Constitutional authority**: §IX.X.1–§IX.X.7  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.29.0)  
**Last updated**: 2026-04-05  

---

## 1. Purpose

§IX (File Validation & Content Integrity) exempts "internal temporary files
written and subsequently read back by RFU itself" from per-`open()` content
validation. This specification formally defines the **boundary** of that
exemption, closing the ambiguity that existed for cross-tool IPC, plugin-
written files, cross-session files, and shared temporary directories.

The core security principle: **the exemption is the narrowest safe definition**.
Any broader interpretation creates a privilege escalation or supply-chain
attack vector.

**See also**:  
- [.specify/memory/checklist-file-validation-exemption-compliance.md](../.specify/memory/checklist-file-validation-exemption-compliance.md) — reviewer checklist  
- [.specify/memory/constitution.md](../.specify/memory/constitution.md) — §IX, §IX.X  
- [.specify/memory/constitution_clairification_uiux_harmonny_r8.md](../.specify/memory/constitution_clairification_uiux_harmonny_r8.md) — round-8 Q16 answer  

---

## 2. The Exemption — Precise Scope (§IX.X.2)

A file qualifies for the validation exemption if and only if ALL four
conditions are simultaneously true:

| Condition | Requirement |
|-----------|-------------|
| **Same process** | Written by the same OS process (identical PID) |
| **Same tool instance** | Written by the same tool instance object in that process |
| **Same session** | Written during the same application session (same session UUID) |
| **No external exposure** | Not passed to any other component, plugin, IPC channel, or shared directory |

If **any single condition** is not met, the file MUST be validated before
being opened.

---

## 3. Boundaries That Invalidate the Exemption (§IX.X.3)

The following crossing events strip the exemption unconditionally:

| Boundary Crossed | Example |
|-----------------|---------|
| **Process boundary** | Tool A (PID 1001) writes, Tool B (PID 1002) reads |
| **Tool boundary** | Tool A writes a temp file, passes path to Tool B in same process |
| **Plugin boundary** | A ComponentGuardian-registered plugin writes a temp file |
| **Session boundary** | Session 1 writes; session 2 reads (e.g., resume/cache) |
| **IPC boundary** | Path passed via socket, pipe, shared memory, or message queue |
| **Shared temp directory** | File written to `%TEMP%` or `/tmp` accessible by other processes |
| **Background/scheduled task** | File handed off to a background worker or scheduled job |

### 3.1 Why Session-Wide Trust Is Unsafe

Session-wide trust would allow:
- Multiple tools running in the same session to skip validation between them
- Plugins to write unchecked files readable by the core pipeline
- Shared temp directories to act as an unvalidated injection surface

Therefore: **only same-process, same-instance trust is permitted**.

### 3.2 Why Plugins Never Qualify

Even when a plugin is registered with `ComponentGuardian`:
- It is third-party code and may be compromised
- It runs with potentially different privileges
- It may be poorly written or malicious
- ComponentGuardian registration is not a code-signing or integrity guarantee

Plugin-written files MUST ALWAYS be validated. There are no exceptions.

---

## 4. Exemption Guard Pattern (§IX.X.6)

### 4.1 Design Requirements

The exemption MUST be implemented via a single, tightly scoped helper
function backed by an **in-process, in-memory registry**:

- Registry lives in memory only — never written to disk
- Registry is keyed by `(absolute_path, process_id, session_id)`
- Registry is cleared on process exit (memory-only means this is automatic)
- The helper MUST NOT be importable from plugin code
- The helper MUST NOT be callable from cross-tool or IPC layers

### 4.2 Reference Implementation (Python)

```python
"""
file_validation_gate.py
Central entry point for all file-read operations in RFU.

This module enforces §IX validation requirements and the §IX.X exemption.
MUST NOT be imported by plugin code or cross-tool IPC layers.
"""

import os
import uuid
from pathlib import Path
from typing import IO

# --- Session identity (process-local, cleared on exit) ---

_SESSION_ID: str = str(uuid.uuid4())
_PROCESS_ID: int = os.getpid()

# --- In-memory registry (process-local, never persisted) ---
# Key: (absolute_path_str, process_id, session_id)

_internal_temp_registry: set[tuple[str, int, str]] = set()


def register_internal_temp(path: Path) -> None:
    """
    Register a file as written by this process/instance/session.
    MUST be called immediately after writing the file and only by core
    RFU tool code — never by plugins or cross-tool code.
    """
    _internal_temp_registry.add(
        (str(path.resolve()), _PROCESS_ID, _SESSION_ID)
    )


def _is_same_instance_internal_temp(path: Path) -> bool:
    """
    Returns True only if the file was registered by this exact
    process + session. Does NOT cross-check plugins or other tools.
    """
    key = (str(path.resolve()), _PROCESS_ID, _SESSION_ID)
    return key in _internal_temp_registry


def write_internal_temp(path: Path, data: bytes) -> None:
    """
    Write a temp file and register it for the same-instance exemption.
    Use this instead of path.write_bytes() when the file will be read
    back by this same instance without crossing any boundary.
    """
    path.write_bytes(data)
    register_internal_temp(path)


def open_validated(path: Path, mode: str = "rb") -> IO:
    """
    Central file-open entry point. Applies full validation unless the
    file qualifies for the same-instance exemption (§IX.X.2).

    All RFU code MUST use this function instead of open() or
    Path.open() directly.
    """
    if _is_same_instance_internal_temp(path):
        # Exemption: same process, same session, registered by this instance.
        # No validation required per §IX (Content-Based Detection bullet).
        return path.open(mode)

    # All other cases: validate before opening.
    _validate_file(path)
    return path.open(mode)


def _validate_file(path: Path) -> None:
    """
    Full validation pipeline per §IX:
    - Magic-byte / signature check
    - Heuristic content detection
    - Policy enforcement (allow/deny list)
    Raises ValidationError on failure.
    """
    # Implementation delegates to file_validator module.
    from file_validator import validate  # noqa: PLC0415
    validate(path)
```

### 4.3 Key Properties of the Implementation

| Property | How it is enforced |
|----------|--------------------|
| Same-process | `_PROCESS_ID = os.getpid()` — cannot match across processes |
| Same-session | `_SESSION_ID = uuid4()` — new UUID per process start |
| In-memory only | `_internal_temp_registry` is a Python `set` — not persisted |
| Plugin isolation | Module-level guard: plugins MUST NOT import this module directly |
| Cross-tool isolation | `open_validated()` is the only entry point; cross-tool callers will not have registered the file |

### 4.4 What Happens at Each Boundary

| Scenario | Registry contains the key? | Result |
|----------|---------------------------|--------|
| Same tool writes, same tool reads (same PID, same session) | ✅ Yes | Exemption granted — no validation |
| Tool A writes, Tool B reads (same PID) | ❌ No (Tool B never registered) | Full validation |
| Tool writes in session 1, reads in session 2 | ❌ No (different session UUID) | Full validation |
| Plugin writes, core reads | ❌ No (plugin MUST NOT call `register_internal_temp`) | Full validation |
| File written to shared temp, read by different process | ❌ No (different PID) | Full validation |
| Background task reads file written by foreground tool | ❌ No (different boundary) | Full validation |

---

## 5. CI Tests

### T1 — Same-instance exemption granted

```python
def test_same_instance_exemption(tmp_path):
    """Same-process, same-session write + read must not trigger validation."""
    test_file = tmp_path / "internal.tmp"
    write_internal_temp(test_file, b"data")

    with mock.patch("file_validation_gate._validate_file") as mock_validate:
        open_validated(test_file)
        mock_validate.assert_not_called()
```

### T2 — Cross-tool read triggers validation

```python
def test_cross_tool_read_validates(tmp_path):
    """A file written by Tool A but NOT registered must be validated."""
    test_file = tmp_path / "cross_tool.tmp"
    test_file.write_bytes(b"data")  # written without register_internal_temp

    with mock.patch("file_validation_gate._validate_file") as mock_validate:
        open_validated(test_file)
        mock_validate.assert_called_once_with(test_file)
```

### T3 — Plugin output triggers validation

```python
def test_plugin_output_validates(tmp_path, plugin_fixture):
    """File written by a plugin must be validated, never exempt."""
    plugin_file = plugin_fixture.write_output(tmp_path / "plugin_out.tmp")

    with mock.patch("file_validation_gate._validate_file") as mock_validate:
        open_validated(plugin_file)
        mock_validate.assert_called_once()
```

### T4 — Cross-session read triggers validation

```python
def test_cross_session_read_validates(tmp_path, monkeypatch):
    """File registered in a previous session must not be exempt in a new session."""
    test_file = tmp_path / "cached.tmp"
    write_internal_temp(test_file, b"session1 data")

    # Simulate new session by resetting session ID and registry
    monkeypatch.setattr("file_validation_gate._SESSION_ID", str(uuid.uuid4()))
    monkeypatch.setattr("file_validation_gate._internal_temp_registry", set())

    with mock.patch("file_validation_gate._validate_file") as mock_validate:
        open_validated(test_file)
        mock_validate.assert_called_once_with(test_file)
```

### T5 — Shared temp directory does not grant exemption to different process

```python
def test_shared_temp_dir_validates(tmp_path):
    """
    A file in a shared temp dir written by a different process
    must always be validated.
    """
    import subprocess, sys
    test_file = tmp_path / "shared.tmp"

    # Write the file from a subprocess (different PID, different session)
    subprocess.run(
        [sys.executable, "-c",
         f"from pathlib import Path; Path('{test_file}').write_bytes(b'x')"],
        check=True,
    )

    with mock.patch("file_validation_gate._validate_file") as mock_validate:
        open_validated(test_file)
        mock_validate.assert_called_once_with(test_file)
```

---

## 6. Migration Steps

### Step 1 — Introduce `file_validation_gate.py`

Add the reference implementation above as `src/utilities/security/file_validation_gate.py`
(or equivalent path in the project structure).

### Step 2 — Audit all `open()` / `Path.open()` calls

Find every direct `open()` or `Path.open()` call in the RFU codebase and
replace with `open_validated()`. Use the audit query:

```bash
grep -rn "\.open(" src/ --include="*.py" | grep -v "file_validation_gate"
grep -rn "\bopen(" src/ --include="*.py" | grep -v "file_validation_gate"
```

Any call that is NOT going through `open_validated()` is a potential
validation bypass.

### Step 3 — Replace direct `write_bytes` + `open` pairs with `write_internal_temp`

Where a tool writes a temp file and reads it back in the same context,
replace:

```python
# Before
tmp.write_bytes(data)
# ... later ...
with tmp.open("rb") as f:
    content = f.read()
```

with:

```python
# After
write_internal_temp(tmp, data)
# ... later ...
with open_validated(tmp, "rb") as f:
    content = f.read()
```

---

## 7. Cross-References

| Reference | Location |
|-----------|----------|
| Constitutional authority | §IX.X.1–§IX.X.7 |
| File validation base requirement | §IX Content-Based Detection bullet (constitution §IX) |
| ComponentGuardian (plugin registry) | docs/component-guardian-spec.md |
| §VIII Path Sanitization | §VIII (constitution) — external process path sanitization |
| Reviewer checklist | .specify/memory/checklist-file-validation-exemption-compliance.md |
| Round-8 Q16 answer | .specify/memory/constitution_clairification_uiux_harmonny_r8.md §Q16 |
| File validator telemetry rules | §IX Telemetry bullet (constitution §IX) |
