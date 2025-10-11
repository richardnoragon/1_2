---
title: "Section 1.1 Repository Footprint Specification"
document_type: "specification"
status: "approved"
last_updated: 2025-10-07
author: "Core Engineering Squad"
approved_by: "Enterprise Architecture Board"
related_documents:
  - ../requirements/section_1_1_repository_footprint_requirements.md
  - ../../roadmap/roadmap_rfu_summary.md#11-repository-footprint-2025-10-05
  - ../implementation_guides/section_1_1_repository_footprint_implementation.md
---

<!-- markdownlint-disable MD025 -->

# Section 1.1 Repository Footprint Specification

This specification translates Section 1.1 directives into measurable inventory baselines and verification criteria.

## Top-Level Directory Inventory

| Directory                                           | Expected Role                                                         | Verification Status | Notes                                              |
| --------------------------------------------------- | --------------------------------------------------------------------- | ------------------- | -------------------------------------------------- |
| `src/`                                              | Primary application codebase with PyQt5 modules.                      | Verified 2025-10-07 | Align with modular refactor plan in Roadmap §3.    |
| `tests/`                                            | Automated test suites including `ui/`.                                | Verified 2025-10-07 | Coverage expansion tracked in QA framework.        |
| `docs/`                                             | Centralized documentation including roadmap and enterprise framework. | Verified 2025-10-07 | New enterprise framework established.              |
| `scripts/`                                          | Automation, maintenance, and reporting scripts.                       | Verified 2025-10-07 | `status_reporting/` added for automation.          |
| `config/`                                           | Configuration assets (`rfu_config.json`, policy files).               | Verified 2025-10-07 | Ensure ConfigManager alignment.                    |
| `core/`                                             | Core system components (legacy staging).                              | Verified 2025-10-07 | Subject to consolidation in Phase 2.               |
| `resources/`                                        | Static resources consumed by application.                             | Verified 2025-10-07 | Monitor for binary assets.                         |
| `reports/`                                          | Generated reports and compliance outputs.                             | Verified 2025-10-07 | Status reports now stored under `status_reports/`. |
| `assets/`                                           | Images and UI assets.                                                 | Verified 2025-10-07 | Ensure proper licensing tags.                      |
| `logs/`                                             | Runtime logs and diagnostics.                                         | Verified 2025-10-07 | Rotation policy pending.                           |
| `results/`                                          | Immutable execution results and baselines.                            | Verified 2025-10-07 | Houses cleanup summaries.                          |
| `rfu_reports/`                                      | Legacy RFU reporting artifacts.                                       | Verified 2025-10-07 | Candidate for consolidation.                       |
| `RFU_Hub_Preferences_Security_Implementation_Plan/` | Historical security implementation plan artifacts.                    | Verified 2025-10-07 | Archive review scheduled.                          |
| `archive/`                                          | Historical migration artifacts.                                       | Verified 2025-10-07 | Maintain manifest per migration governance.        |
| `backups/`                                          | Backup snapshots and recovery assets.                                 | Verified 2025-10-07 | Validate currency each quarter.                    |
| `src_backup/`                                       | Legacy code snapshot retained for rollback.                           | Verified 2025-10-07 | Flagged as duplicate location.                     |
| `emergency-backup-20250925_200754/`                 | Emergency backup snapshot.                                            | Verified 2025-10-07 | Confirm retention policy.                          |
| `.benchmarks/`                                      | Benchmark outputs.                                                    | Verified 2025-10-07 | Clean per performance schedule.                    |
| `.roo/`                                             | Tooling metadata.                                                     | Verified 2025-10-07 | Exclude from packaging.                            |
| `.specify/`                                         | Tooling metadata.                                                     | Verified 2025-10-07 | Exclude from packaging.                            |
| `.vscode/`                                          | Editor settings.                                                      | Verified 2025-10-07 | Align with workspace conventions.                  |

### Additional Observations (Delta from Roadmap)

| Directory     | Status  | Action                                                          |
| ------------- | ------- | --------------------------------------------------------------- |
| `data/`       | Present | Evaluate whether to add to roadmap baseline.                    |
| `gui/`        | Present | Contains GUI prototypes; assess consolidation into `src/rfu/`.  |
| `migrations/` | Present | Confirm alignment with database strategy.                       |
| `specs/`      | Present | Legacy specification folder; migrate into enterprise framework. |
| `venv/`       | Present | Development virtual environment.                                |

## Duplicate and Legacy Code Locations

| Location                                            | Description                             | Validation Result           | Notes                                                     |
| --------------------------------------------------- | --------------------------------------- | --------------------------- | --------------------------------------------------------- |
| `src_backup/`                                       | Legacy snapshot for rollback.           | Verified 2025-10-07         | Schedule audit to remove deprecated modules post Phase 2. |
| `archive/`                                          | Historical migration artifacts.         | Verified 2025-10-07         | Ensure manifest alignment with change log.                |
| `RFU_Hub_Preferences_Security_Implementation_Plan/` | Migration assets and backups.           | Verified 2025-10-07         | Tag for long-term archival.                               |
| Root `main.py.backup`                               | Should be absent per roadmap directive. | Confirmed Absent 2025-10-07 | No remediation required.                                  |

## GUI Entry Points

| Artifact                           | Path                          | Validation Result           | Notes                                                                                                             |
| ---------------------------------- | ----------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Primary GUI launcher               | `src/main.py`                 | Verified 2025-10-07         | Canonical entry point observed during validation.                                                                 |
| Retired roadmap launcher reference | `src/rfu/main.py`             | Confirmed absent 2025-10-07 | Roadmap corrected to align with canonical launcher (`CL-2025-10-07-003`); continue monitoring for reintroduction. |
| Root wrapper                       | `main.py`                     | Verified 2025-10-07         | Wraps canonical launcher.                                                                                         |
| Explorer launcher                  | `rfu_explorer.py`             | Verified 2025-10-07         | Maintained for legacy workflows.                                                                                  |
| Demo visualizer                    | `demo_pyvisualizer.py`        | Verified 2025-10-07         | For training/testing.                                                                                             |
| Simple visualizer                  | `simple_pyvisualizer_demo.py` | Verified 2025-10-07         | Remains accessible for QA demos.                                                                                  |

## Configuration Artifacts

| Artifact            | Path                             | Validation Result   | Notes                          |
| ------------------- | -------------------------------- | ------------------- | ------------------------------ |
| Core config         | `config/rfu_config.json`         | Verified 2025-10-07 | Managed through ConfigManager. |
| Environment file    | `.env`                           | Verified 2025-10-07 | Ensure secrets rotation.       |
| Workspace baselines | `reports/`                       | Verified 2025-10-07 | Houses analysis baselines.     |
| Execution baselines | `results/`                       | Verified 2025-10-07 | Contains cleanup summaries.    |
| Transient caches    | `.mypy_cache/`, `.pytest_cache/` | Verified 2025-10-07 | Cleared during CI cycles.      |

## Acceptance Criteria

- Automated verification passes with zero failures and produces auditable JSON output.
- Deviations (additional directories) recorded in change log with planned follow-up.
- Specification updates trigger regeneration of traceability matrix under `../version_control/section_1_1_repository_footprint_traceability.md`.
