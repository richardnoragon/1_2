# CI Enforcement Specification

**Constitution Reference**: §11  
**Version**: 1.37.0  
**Added**: 2026-04-24 (harmonization2 Phase 4)
**Updated**: 2026-04-24 (v1.37.0 — bumped to align with constitution v1.37.0 harmonization2 completion)

---

## Overview

This document is the canonical reference for Constitution §11 — CI Enforcement
Specification. It defines the mandatory CI rules, automated checks, failure
conditions, and reporting requirements that enforce the Tool Capability Matrix
(§12) and all associated constitutional sections.

CI is the **final authority** on whether a tool is allowed to merge.

---

## 1. CI Architecture

```
PR Submitted
    │
    ├─ Static Analysis Layer (§11.4)
    │   ├─ TH: Theming token scan
    │   ├─ DR: Dry-run path scan
    │   ├─ CP: Shared component scan
    │   ├─ A11Y: Accessibility scan
    │   ├─ ERR: Error handling scan
    │   ├─ STR: String token scan
    │   ├─ MEN: Menu architecture scan (§7)
    │   ├─ FNT: Font token scan
    │   ├─ LYT: Layout token scan
    │   └─ WRD: Wording / verb form scan
    │
    ├─ Schema Validation Layer (§11.5)
    │   ├─ Menu registry schema
    │   ├─ Telemetry schema
    │   ├─ Preference schema
    │   └─ Tool metadata schema
    │
    ├─ Runtime Test Layer (§11.6)
    │   ├─ INT: UI Interaction tests
    │   ├─ GRD: Guardian tests
    │   ├─ CE: Critical Engine tests (if classified)
    │   └─ PERF: Performance tests
    │
    ├─ Matrix Compliance Layer (§11.7)
    │   └─ Evaluates all 20 capability codes against §12
    │
    └─ Reporting Layer (§11.8)
        ├─ JSON machine-readable report
        ├─ Markdown human-readable summary
        └─ Hub dashboard update
```

---

## 2. Static Analysis Rule Definitions

### 2.1 TH — Theming

Violations detected:
- `#[0-9a-fA-F]{3,8}` (hex color literals)
- `rgb(` / `rgba(` outside theme token files
- `QFont(` with raw family string
- Missing `_on_theme_changed` method in QWidget subclasses

### 2.2 DR — Dry-Run

Violations detected:
- Methods matching `delete|remove|wipe|overwrite|anonymize` without
  `if.*dry_run` branching
- Missing `dry_run_toggle` wiring in tool `__init__`

### 2.3 CP — Shared Components

Violations detected:
- `QPushButton(` in tool code (use PrimaryButton / SecondaryButton)
- `QMessageBox.critical(` in tool code (use ModalError)
- `QDialog` subclasses implementing their own confirmation pattern

### 2.4 A11Y — Accessibility

Violations detected:
- `setAccessibleName("")` or missing `setAccessibleName`
- `setAccessibleDescription("")` or missing where required
- Color-as-sole-indicator patterns (stylesheet-only error state)
- Widget geometry < 44px in any dimension (logical pixels)

### 2.5 ERR — Error Handling

Violations detected:
- `str(e)` or `repr(e)` passed to any UI display function
- `except Exception:` without `logger.error` call
- Missing error code constant in exception raise/handle chain
- `QMessageBox.critical(` (must use ModalError)

### 2.6 STR — Strings

Violations detected:
- String literals in `setText(`, `setTitle(`, `setLabel(`, `setPlaceholderText(`
  that are not `ui_strings.*` references
- Hardcoded English strings in tool QAction labels

### 2.7 MEN — Menu Architecture

Violations detected:
- `menuBar().addMenu(` in tool code outside Hub Menu Registry
- `addAction(` on a QMenu object in tool code outside registry
- Menu registration under File, Edit, Window, or Help without exemption flag
- Missing accelerator in `register()` call

### 2.8 FNT — Font Tokens

Violations detected:
- `QFont("` with raw family name
- `setPointSize(` with integer literal outside font token module
- `setPixelSize(` with integer literal outside font token module

### 2.9 LYT — Layout

Violations detected:
- `setSpacing(` or `setContentsMargins(` with integer literals outside
  layout token module
- Missing safe-area margin class on top-level widget

### 2.10 WRD — Wording

Violations detected:
- Menu/button labels not starting with imperative verb (regex: `^[A-Z][a-z]+ing `)
- Ellipsis `…` on actions that do not open a dialog
- Button labels in SCREAMING_CASE or all-lowercase

---

## 3. Schema Validation Rules

### 3.1 Menu Registry Schema

```json
{
  "tool_id": "string (required)",
  "menu": "string (one of: Tools, Reports, View)",
  "label_token": "string (ui_strings key, required)",
  "accelerator": "string (Ctrl+X pattern, required)",
  "enabled_condition": "callable reference",
  "visible_condition": "callable reference",
  "callback": "callable reference (required)"
}
```

Validation failures:
- `menu` not in allowed set → FAIL
- `accelerator` absent or malformed → FAIL
- `label_token` not found in `ui_strings` → FAIL
- Duplicate `accelerator` under same parent → FAIL

### 3.2 Telemetry Schema

All events MUST conform to:
```json
{
  "event": "string (registered event name, required)",
  "tool": "string (tool_id, required)",
  "timestamp": "ISO8601 (auto-populated)",
  "session_id": "string (required)"
}
```

Additional required fields per event type as defined in the telemetry registry.

### 3.3 Preference Schema

```json
{
  "preference_category": "string (required)",
  "preference_key": "string (required)",
  "default_value": "any (required)",
  "value_type": "string (required)",
  "description": "string (required)",
  "schema_version": "integer (required)"
}
```

### 3.4 Tool Metadata Schema

```json
{
  "tool_id": "string (required)",
  "tool_name": "string (required)",
  "classification": "Standard | CE (required)",
  "capabilities": ["TH", "DR", ...],
  "owner": "string (required)",
  "version": "semver (required)"
}
```

---

## 4. Reporting Format

### 4.1 Machine-Readable JSON Report

```json
{
  "tool_id": "my_tool",
  "pr": "PR-1234",
  "timestamp": "2026-04-24T00:00:00Z",
  "overall": "FAIL",
  "capabilities": {
    "TH": { "status": "PASS" },
    "DR": { "status": "FAIL", "violations": [
      { "file": "src/utilities/...", "line": 42,
        "rule": "DR-01", "message": "Destructive method missing dry-run branch" }
    ]},
    "MEN": { "status": "PASS" }
  }
}
```

### 4.2 Human-Readable Markdown Summary

```markdown
## CI Compliance Report — my_tool — PR #1234

| Capability | Status | Violations |
|------------|--------|------------|
| TH | ✅ PASS | — |
| DR | ❌ FAIL | 1 violation |
| MEN | ✅ PASS | — |

### DR Violations
**src/utilities/my_tool/engine.py:42** — `DR-01`: Destructive method
`delete_files()` has no `if self.dry_run` branch.
**Fix**: Add dry-run path returning preview list without executing deletion.
```

---

## 5. Failure Conditions Summary

CI MUST fail if ANY of the following:
- Any §11.4 static analysis rule violation detected
- Any §11.5 schema validation failure
- Any §11.6 runtime test failure
- Any §11.7 matrix capability missing, Partial, or Unknown
- Any reserved name violated (§7.4.4)
- Any accelerator conflict
- Any raw string literal in UI code

CI MUST NOT permit overrides except by constitutional amendment.

---

## 6. Implementation Blueprint

### GitHub Actions Pipeline

```yaml
name: CI Compliance

on: [pull_request]

jobs:
  static-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run RFU Static Analysis
        run: python scripts/ci/static_analysis.py --rules TH,DR,CP,A11Y,ERR,STR,MEN,FNT,LYT,WRD

  schema-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate Schemas
        run: python scripts/ci/schema_validator.py

  runtime-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Runtime Test Suite
        run: python -m pytest tests/ci/ -m "INT or GRD or CE or PERF" -v

  matrix-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate Tool Capability Matrix
        run: python scripts/ci/matrix_validator.py --matrix docs/tool-capability-matrix.json

  report:
    needs: [static-analysis, schema-validation, runtime-tests, matrix-compliance]
    runs-on: ubuntu-latest
    steps:
      - name: Generate Compliance Report
        run: python scripts/ci/generate_report.py --output ci-report.json
      - uses: actions/upload-artifact@v4
        with:
          name: ci-compliance-report
          path: ci-report.json
```

---

## Cross-References

- Constitution §11 (normative)
- Constitution §12 Tool Capability Matrix
- Constitution §7 Menu Architecture & Nomenclature
- Constitution §10 UI Interaction Contract
- docs/tool-capability-matrix-template.md
- .specify/memory/checklist-ci-enforcement-compliance.md
