# UI/UX Harmonization — Automated Compliance Tooling

**Path:** `docs/ui-ux-harmonization/AUTOMATED_TOOLING.md`  
**Authority:** Guide §1.3 / TASKS.md P1-D07  
**Status:** Active — April 2026  
**Baseline recorded:** April 2026

---

## Overview

Three automated checks enforce UI/UX Harmonization compliance. All three are implemented as standalone Python scripts under `scripts/compliance/` and are designed to run in CI without manual intervention.

| # | Check | Script | Phase active |
|---|---|---|---|
| 1 | Theming Compliance | `scripts/compliance/check_theming_compliance.py` | Phase 1 (baseline) → enforced from Phase 3 |
| 2 | Component Usage Validation | `scripts/compliance/check_component_usage.py` | Phase 1 (baseline) → enforced from Phase 3 |
| 3 | Accessibility Scan | `scripts/compliance/check_accessibility.py` | Phase 1 (baseline) → enforced from Phase 3 |

A combined runner executes all three in sequence:

```
scripts/compliance/run_compliance_checks.py
```

---

## Check 1 — Theming Compliance

### Purpose

Detects hard-coded hex color strings (e.g. `#2c3e50`, `#3498db`) remaining in Python source files. Per spec §4.1.2, all color values **MUST** resolve through `token(key)` calls against the `TOKENS` dict; no hex literals may appear in tool or widget source.

### Tooling selection rationale

Custom Python regex scanner. No third-party dependency required. Operates on `.py` files recursively under `src/`. Excludes `themes.py` and `styles.py` (the canonical TOKENS definition files).

### Invocation

```bash
# Report mode (Phase 1 — doesn't fail CI)
python scripts/compliance/check_theming_compliance.py --root .

# Strict mode (Phase 3 — fails CI on any violation)
python scripts/compliance/check_theming_compliance.py --root . --strict

# Write baseline JSON
python scripts/compliance/check_theming_compliance.py --root . --baseline results/compliance/theming_baseline.json
```

### Configuration

| Parameter | Value | Notes |
|---|---|---|
| Scan root | `src/` | All `.py` files scanned recursively |
| Excluded files | `themes.py`, `styles.py` | Canonical TOKENS definition — hex values are intentional |
| Excluded dirs | `__pycache__`, `.venv312`, `venv`, `.git`, `backups` | Build/env artifacts |
| Pattern | `#[0-9a-fA-F]{3}` or `#[0-9a-fA-F]{6}` | Word-boundary anchored |

### Phase 1 baseline (April 2026)

| Metric | Value |
|---|---|
| Total violations | **457** |
| Key sources | `src/core/constants.py`, `src/gui/safe_standard_window.py`, `src/tabbed_hub.py`, all tool files |
| Expected resolution | Phase 3 — TH-1 and TH-2 tasks per tool |

> Phase 3 CI gate: `--strict` flag passed; check exits 1 if any violations remain in that tool's migrated files.

---

## Check 2 — Component Usage Validation

### Purpose

Confirms that tool source files use Hub-provided shared components (`PrimaryButton`, `SecondaryButton`, `TextInput`, `Modal`, `ToastNotification`, `Breadcrumb`, `LoadingIndicator`) rather than bare Qt equivalents (`QPushButton`, `QLineEdit`, `QDialog`, `QProgressBar`), unless the deviation is documented in `DEVIATIONS.md`.

### Tooling selection rationale

Custom Python AST/regex scanner. No third-party dependency required. Scans `.py` files under `src/tools/` only (tool files, not the shared component library itself). Reports bare widget usage per-file.

In Phase 1, the check is report-only (`--phase 1`). In Phase 3, `--phase 3 --strict` enforces the requirement.

### Invocation

```bash
# Phase 1 — report only (does not fail CI)
python scripts/compliance/check_component_usage.py --root . --phase 1

# Phase 3 — enforce (fails CI on violations in migrated tools)
python scripts/compliance/check_component_usage.py --root . --phase 3 --strict

# Write baseline JSON
python scripts/compliance/check_component_usage.py --root . --baseline results/compliance/component_baseline.json
```

### Configuration

| Parameter | Value | Notes |
|---|---|---|
| Scan root | `src/tools/` | Tool files only — shared library is excluded |
| Detected widgets | `QPushButton`, `QLineEdit`, `QDialog`, `QProgressBar` | Direct Qt use that should migrate to shared components |
| Excluded dirs | `components/`, `core/guardian/`, `tests/` | Library and infrastructure — not tool code |
| Enforcement phase | `3` | `--phase 1` always exits 0 regardless of findings |

### Phase 1 baseline (April 2026)

| Metric | Value |
|---|---|
| Total violations | **887** |
| Files with violations | **69** |
| Most common widget | `QPushButton` (nearly all tool files) |
| Expected resolution | Phase 3 — CP-1 through CP-7 tasks per tool |

> Phase 3 CI gate: `--phase 3 --strict` flags passed after each tool's CP migration tasks are done.

---

## Check 3 — Accessibility Scan

### Purpose

Detects interactive Qt widgets (`QPushButton`, `QComboBox`, `QLineEdit`, `QCheckBox`, etc.) in source files that do **not** have a `setAccessibleName()` call within a ±20 line context window. All interactive controls **MUST** carry accessible labels per spec §6.1 and constitution §7(e).

### Tooling selection rationale

Custom Python regex/line-context scanner. No third-party accessibility framework required (GUI automation tools like `pyatspi`, `axe-core`, or `Accessibility Insights` require a running application and cannot be integrated into static CI). Static analysis catches the structural requirement (accessible name MUST be set in constructor/setup code) without running the UI.

> **Limitation:** This check cannot detect runtime accessibility issues (focus order, screen reader announcement quality, reduced motion compliance). Manual accessibility spot checks per Guide §4.2 remain required for Phase 4 verification.

### Invocation

```bash
# Report mode
python scripts/compliance/check_accessibility.py --root .

# Strict mode (fails CI on violations)
python scripts/compliance/check_accessibility.py --root . --strict

# Write baseline JSON
python scripts/compliance/check_accessibility.py --root . --baseline results/compliance/accessibility_baseline.json
```

### Configuration

| Parameter | Value | Notes |
|---|---|---|
| Scan root | `src/` | All `.py` files scanned recursively |
| Context window | ±20 lines | Looks within 20 lines after widget creation for `setAccessibleName()` |
| Detected widgets | `QPushButton`, `QToolButton`, `QCheckBox`, `QRadioButton`, `QComboBox`, `QSpinBox`, `QDoubleSpinBox`, `QLineEdit`, `QTextEdit`, `QPlainTextEdit`, `QListWidget`, `QTreeWidget`, `QTableWidget`, `QSlider`, `QTabWidget` | Interactive controls that require labels |
| Exempt widgets | Shared component classes (already call `setAccessibleName()` internally) | `PrimaryButton`, `TextInput`, etc. |
| Excluded dirs | `components/`, `tests/`, `__pycache__`, `venv` | Not tool code |

### Phase 1 baseline (April 2026)

| Metric | Value |
|---|---|
| Total violations | **981** |
| Files with violations | **73** |
| Expected resolution | Phase 3 — A11Y-1 and A11Y-2 tasks per tool |

> Phase 3 CI gate: `--strict` flag passed after each tool's A11Y migration tasks are done.

---

## Combined Runner

All three checks can be run together with the combined runner:

```bash
# Phase 1 — report only, writes baselines
python scripts/compliance/run_compliance_checks.py --root . --baseline-dir results/compliance --phase 1

# Phase 3 — strict enforcement
python scripts/compliance/run_compliance_checks.py --root . --phase 3 --strict
```

Output: `results/compliance/compliance_summary.json` (machine-readable combined result).

---

## CI Integration

Add to the CI pipeline as a step after unit tests. In Phase 1, run in report-only mode: 

```yaml
# Example CI step (GitHub Actions / equivalent)
- name: UI/UX Compliance Checks (Phase 1 — report only)
  run: |
    python scripts/compliance/run_compliance_checks.py \
      --root . \
      --baseline-dir results/compliance \
      --phase 1
  # No --strict in Phase 1; step never fails CI
```

In Phase 3, add `--strict` and `--phase 3` once the tool under migration has completed all TH/CP/A11Y tasks.

---

## Baseline Files

| File | Description |
|---|---|
| `results/compliance/theming_baseline.json` | April 2026 baseline — 457 theming violations |
| `results/compliance/component_baseline.json` | April 2026 baseline — 887 component violations across 69 files |
| `results/compliance/accessibility_baseline.json` | April 2026 baseline — 981 accessibility violations across 73 files |
| `results/compliance/compliance_summary.json` | Latest combined run summary |

---

## Limitations and Deferred Tooling

| Item | Status | Notes |
|---|---|---|
| Runtime accessibility testing (screen reader, focus order) | **Deferred to Phase 4** | Requires a running GUI; manual testing per Guide §4.2–§4.3 |
| Visual theming smoke test (light/dark render) | **Deferred to Phase 4** | Requires `QApplication`; constitution DW §11 requires manual visual verify |
| High-contrast mode testing | **Deferred to Phase 4** | Manual per Guide §4.3 |
| Colour-blind simulation | **Deferred to Phase 4** | Manual per spec §6.2.4 |
| `DEVIATIONS.md` cross-reference (ensure all bare widget uses are documented) | **Phase 3** | `check_component_usage.py` reports; human confirms or documents deviation |
