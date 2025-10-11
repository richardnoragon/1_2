---
document_id: META-SEC1-1-001
version: 1.0.0
document_type: metadata_schema
created: 2025-10-08T02:10:00Z
last_reviewed: 2025-10-08T02:10:00Z
author: modernization_program_pm
status: approved
---

# Enterprise Documentation Metadata Schema (v1.0.0)

## Required Fields

- `document_id`: Unique identifier following `<TYPE>-<SECTION>-<SEQUENCE>` format.
- `version`: Semantic version string `major.minor.patch`.
- `document_type`: One of `requirements`, `technical_specification`, `implementation_guide`, `testing_protocol`, `validation_artifact`, `change_management_log`, `version_control_history`, `compliance_record`, `traceability_matrix`, `metadata_schema`.
- `created`: ISO 8601 timestamp of initial creation.
- `last_reviewed`: ISO 8601 timestamp of latest review.
- `author`: Role or individual responsible for content stewardship.
- `status`: `draft`, `in_review`, `approved`, or `active`.

## Optional Fields

- `related_milestones`: List of roadmap milestones aligned with the artifact.
- `references`: Relative path references to dependent artifacts.
- `regulations`: For compliance documents, list of applicable controls.
- `related_requirements`: For specifications and guides, references to requirement documents.
- `source_tests`: For validation artifacts, references to the executed test plans.

## Tagging Strategy

- Incorporate additional YAML fields prefixed with `tags_` (e.g., `tags_phase: phase_1_foundation`) to support downstream analytics without breaking compatibility.
- Ensure all metadata keys use lower_snake_case naming.

## Governance

- Metadata updates require review by Documentation & Training FTE.
- Audit trail recorded via `scripts/document_audit/document_audit_logger.py` with outputs stored under `reports/audit_trail/`.
