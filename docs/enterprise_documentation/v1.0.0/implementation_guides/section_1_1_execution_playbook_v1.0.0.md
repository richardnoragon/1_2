---
document_id: IMP-SEC1-1-001
version: 1.0.0
document_type: implementation_guide
created: 2025-10-08T00:45:00Z
last_reviewed: 2025-10-08T00:45:00Z
author: modernization_program_pm
status: approved
related_requirements:
  - docs/enterprise_documentation/v1.0.0/requirements/section_1_1_repository_footprint_requirements_v1.0.0.md
references:
  - scripts/status_dashboard/generate_section_1_1_dashboard.py
  - scripts/document_audit/document_audit_logger.py
---

# Section 1.1 Execution Playbook

## Step 1 – Directory Discovery

1. Activate the project virtual environment.
2. Run `python scripts/status_dashboard/generate_section_1_1_dashboard.py --refresh`.
3. Review the generated dashboard to confirm the directory inventory matches governance expectations.

## Step 2 – Legacy Location Verification

1. Execute the verification checklist in `docs/enterprise_documentation/v1.0.0/testing_protocols/section_1_1_validation_test_plan_v1.0.0.md`.
2. Capture any deviations in the change management log template.

## Step 3 – GUI Entry Point Review

1. Confirm launchers defined in `src/main.py`, `main.py`, and `rfu_explorer.py`.
2. Validate that each launcher delegates to the canonical PyQt5 entry point without deprecated imports.

## Step 4 – Configuration Artifact Audit

1. Inspect `config/rfu_config.json`, `.env`, and workspace analysis baselines.
2. Run `python scripts/document_audit/document_audit_logger.py --scope docs/enterprise_documentation/v1.0.0 --output reports/audit_trail/section_1_1_document_audit_log.csv`.
3. Archive the output under `docs/enterprise_documentation/v1.0.0/validation_artifacts/`.

## Step 5 – Status Update

1. Update `docs/roadmap/roadmap_rfu_summary.md` table with refreshed metrics, risks, and dependencies.
2. Attach validation references and traceability identifiers in the table notes column.
