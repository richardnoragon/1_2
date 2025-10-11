---
document_id: TST-SEC1-1-001
version: 1.0.0
document_type: testing_protocol
created: 2025-10-08T01:00:00Z
last_reviewed: 2025-10-08T01:00:00Z
author: modernization_program_pm
status: approved
related_requirements:
  - docs/enterprise_documentation/v1.0.0/requirements/section_1_1_repository_footprint_requirements_v1.0.0.md
references:
  - docs/enterprise_documentation/v1.0.0/validation_artifacts/section_1_1_validation_results_v1.0.0.md
---

# Section 1.1 Validation Test Plan

## Test Suite Overview

- **Objective**: Validate repository footprint assessment outcomes defined in Section 1.1 of the roadmap.
- **Scope**: Top-level directory audit, legacy location confirmation, GUI entry point validation, configuration artifact inspection.

## Test Cases

### TC-1 Directory Inventory Completeness

- **Procedure**:
  1. Run repository directory listing via `python scripts/status_dashboard/generate_section_1_1_dashboard.py --inventory-only`.
  2. Compare output against `docs/roadmap/roadmap_rfu_summary.md` Section 1.1 listing.
- **Expected Result**: 100% match with roadmap enumerations.
- **Metrics Captured**: Directory count, variance count (expected 0).

### TC-2 Legacy Footprint Confirmation

- **Procedure**:
  1. Inspect directories `src_backup/`, `archive/`, and `RFU_Hub_Preferences_Security_Implementation_Plan/`.
  2. Confirm absence of `main.py.backup`.
- **Expected Result**: Legacy directories segregated, no deprecated launcher.
- **Metrics Captured**: Legacy directories count, compliance flag (pass/fail).

### TC-3 GUI Entry Point Verification

- **Procedure**:
  1. Execute launchers `python src/main.py`, `python main.py`, `python rfu_explorer.py`.
  2. Confirm they invoke the canonical PyQt5 hub without import errors.
- **Expected Result**: Launch success with consistent splash screen.
- **Metrics Captured**: Launch success (boolean), execution time (s).

### TC-4 Configuration Artifact Audit

- **Procedure**:
  1. Verify presence and readability of `config/rfu_config.json` and `.env`.
  2. Ensure caches such as `.mypy_cache` and `.pytest_cache` are absent or scheduled for cleanup.
- **Expected Result**: Configuration artifacts present; cache hygiene plan documented.
- **Metrics Captured**: Artifacts verified (count), outstanding cache issues (count).

## Exit Criteria

- All test cases executed with `status = pass`.
- Validation artifacts archived with SHA-256 hash recorded in audit log.
