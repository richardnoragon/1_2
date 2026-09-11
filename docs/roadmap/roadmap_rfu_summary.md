# Richard's File Utilities (RFU) Enterprise Modernization Roadmap

## 1. Current State Assessment

### 1.1 Repository Footprint (2025-10-05)

- Top-level directories: `src/` (primary application), `tests/` (now with dedicated UI suite), `docs/` (expanded with roadmap materials), `scripts/`, `config/`, `core/`, `resources/`, `reports/`, `assets/`, `logs/`, `results/`, `rfu_reports/`, `RFU_Hub_Preferences_Security_Implementation_Plan/`, `archive/`, `backups/`, `src_backup/`, `emergency-backup-20250925_200754/`, plus operational metadata folders (`.benchmarks/`, `.roo/`, `.specify/`, `.vscode/`). Additional enterprise directories catalogued during automation (`data/`, `gui/`, `migrations/`, `specs/`, `venv/`) remain tracked in the change log for taxonomy alignment.
- Duplicate/legacy code locations: `src_backup/`, historical migration artifacts under `archive/` and `RFU_Hub_Preferences_Security_Implementation_Plan/`; root retains only the supported launchers (`main.py`, `rfu_explorer.py`) with obsolete `main.py.backup` removed.
- GUI entry points: `src/main.py` (canonical launcher), root-level `main.py` wrapper, `rfu_explorer.py`, standalone demos (`demo_pyvisualizer.py`, `simple_pyvisualizer_demo.py`).
- Configuration artifacts: `config/rfu_config.json`, `.env`, workspace analysis baselines in `reports/` and `results/`; transient caches (`.mypy_cache/`, `.pytest_cache/`) and stray root logs cleared to preserve enterprise readiness.

#### Section 1.1 Status Tracking (Updated 2025-10-08)

| Milestone                                          | Status   | Completed On         | Validation (Metric Snapshot)                                                                                                                                           | Risk (ID / Level)        | Dependencies (ID / Notes)                                        | Progress Notes                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------------- | -------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Top-level directory inventory baseline established | Complete | 2025-10-08T01:10:30Z | TC-1 (directory_count=26; variance=0) — [Validation (v1.0.0)](../enterprise_documentation/v1.0.0/validation_artifacts/section_1_1_validation_results_v1.0.0.md)        | RISK-SEC1-1-001 (Low)    | DEP-SEC1-1-001; CL-2025-10-08-001                                | Dashboard automation generated via [`generate_section_1_1_dashboard.py`](../../scripts/status_dashboard/generate_section_1_1_dashboard.py); audit hashes captured in [`section_1_1_document_audit_log.csv`](../../reports/audit_trail/section_1_1_document_audit_log.csv).                                                     |
| Legacy and duplicate locations confirmed           | Complete | 2025-10-08T01:11:05Z | TC-2 (legacy_directories=3; compliance=pass) — [Validation (v1.0.0)](../enterprise_documentation/v1.0.0/validation_artifacts/section_1_1_validation_results_v1.0.0.md) | RISK-SEC1-1-002 (Medium) | DEP-SEC1-1-001; CL-2025-10-08-002                                | Legacy verification notes stored in [`section_1_1_legacy_verification_notes_2025-10-08.md`](../../reports/validation/section_1_1_legacy_verification_notes_2025-10-08.md); traceability maintained via [`TRC-SEC1-1-001`](../enterprise_documentation/v1.0.0/traceability_matrices/section_1_1_traceability_matrix_v1.0.0.md). |
| GUI entry points catalogued                        | Complete | 2025-10-08T01:12:45Z | TC-3 (launch_success=true; avg_startup=2.7s) — [Validation (v1.0.0)](../enterprise_documentation/v1.0.0/validation_artifacts/section_1_1_validation_results_v1.0.0.md) | RISK-SEC1-1-003 (Medium) | DEP-SEC1-1-001; CL-2025-10-08-002; CL-2025-10-08-003             | Launch logs archived at [`section_1_1_gui_entry_point_launch_log_2025-10-08.txt`](../../reports/validation/section_1_1_gui_entry_point_launch_log_2025-10-08.txt); implementation guidance in [`IMP-SEC1-1-001`](../enterprise_documentation/v1.0.0/implementation_guides/section_1_1_execution_playbook_v1.0.0.md).           |
| Configuration artifacts audited                    | Complete | 2025-10-08T01:13:50Z | TC-4 (artifacts_verified=2; cache_issues=0) — [Validation (v1.0.0)](../enterprise_documentation/v1.0.0/validation_artifacts/section_1_1_validation_results_v1.0.0.md)  | RISK-SEC1-1-004 (Low)    | DEP-SEC1-1-001; CL-2025-10-08-002; SEC-VC-001 compliance mapping | Configuration checklist logged in [`section_1_1_configuration_audit_checklist_2025-10-08.csv`](../../reports/validation/section_1_1_configuration_audit_checklist_2025-10-08.csv); compliance summary tracked in [`CMP-SEC1-1-001`](../enterprise_documentation/v1.0.0/compliance/section_1_1_compliance_alignment_v1.0.0.md). |

### 1.2 Dependency Inventory

- Application dependencies tracked in `requirements.txt` (version 3.1.0-enterprise) covering PyQt5 GUI stack, encryption, PDF/media processing, monitoring, testing, and documentation toolchains.
- Development tooling defined in `setup.cfg` (linting, formatting, mypy), Python 3.10+ expected via `venv/`.
- Pending upgrades: monitor PyQt5 LTS, cryptography stack for FIPS regressions, ensure packages with OS markers tested per platform.
- Hardening baseline (Issue #80): duplicate `requests` entry removed; `pip-audit` and `cyclonedx-bom` added for vulnerability scanning and SBOM generation in CI quality gates; strict vulnerability fail policy enabled; default audit retention aligned to 12 months. The implementation is recorded in [`docs/security/ISSUE_80_SECURITY_AUDIT_AND_DEPENDENCY_HARDENING.md`](../security/ISSUE_80_SECURITY_AUDIT_AND_DEPENDENCY_HARDENING.md) and synchronized with the code in the core audit and config layers.
- Follow-up policy backlog for Issue #80:
	- Add a documented allowlist / ignore file for known transitive vulnerabilities, including ownership and expiration dates.
	- Expand file-operation audit metadata so more entry points emit richer actor, resource, and session context.
	- Publish SBOM artifacts alongside release assets and define the retention / distribution workflow for those reports.
- Startup-path optimization baseline (Issue #82): database initialization moved behind an on-demand getter, optional PDF widget loading is deferred until the PDF tools tab is created, and a lightweight cold-import benchmark documents the current startup path. The implementation is recorded in [`docs/performance/ISSUE_82_PERFORMANCE_AND_STARTUP_PATH_OPTIMIZATION.md`](../performance/ISSUE_82_PERFORMANCE_AND_STARTUP_PATH_OPTIMIZATION.md).
- Observability consolidation baseline (Issue #83): `ObservabilityService` now provides the shared structured event model for errors, warnings, info, and tool/file lifecycle events, while `ErrorHandler` routes diagnostics through the shared layer without changing user-facing dialogs. The implementation is recorded in [`docs/observability/ISSUE_83_ERROR_HANDLING_AND_OBSERVABILITY_CONSOLIDATION.md`](../observability/ISSUE_83_ERROR_HANDLING_AND_OBSERVABILITY_CONSOLIDATION.md).
- Test infrastructure and quality-gate baseline (Issue #84): `scripts/quality/run_quality_gates.py` now provides the canonical project-scoped gate runner with explicit coverage thresholds, optional smoke mode, and a headless-safe default execution pattern. The implementation is recorded in [`docs/testing/ISSUE_84_TEST_INFRASTRUCTURE_AND_QUALITY_GATES.md`](../testing/ISSUE_84_TEST_INFRASTRUCTURE_AND_QUALITY_GATES.md).
- Implementation roadmap umbrella (Issue #85): the recommended package rollout order is Architecture (#79) → Security (#80) → UI/UX (#81) → Performance (#82) → Observability (#83) → Testing (#84). The canonical roadmap note is [`docs/roadmap/ISSUE_85_IMPLEMENTATION_ROADMAP.md`](ISSUE_85_IMPLEMENTATION_ROADMAP.md).
- Project completion sync (2026-09-11): the items previously marked In Progress on project #2 for #79, #80, #81, #82, and #85 were completed and closed with their issue-linked documentation updated.
- Project completion sync (2026-09-11): the items moved to In Progress for #83 and #84 were completed and closed with their issue-linked documentation updated.

### 1.3 Technical Debt Summary

- Redundant code paths and archival directories remain (`src_backup/`, legacy automation scripts), yet active launch surface is now limited to vetted entry points.
- Documentation naming is improved by consolidating roadmap and fix guides under `docs/`, though broader snake_case adoption is still pending for older assets.
- Missing central dependency lock (no `poetry.lock`/`requirements-lock.txt`), limited CI/CD enforcement for quality gates, and remaining startup-path latency should continue to be monitored with the documented benchmark.
- Error/telemetry consolidation is now centralized, but shared observability regression coverage should remain part of the core validation set for future handler changes.
- Quality-gate enforcement is now centralized, but the repository should continue to track minimum coverage expectations and runner behavior through the documented issue #84 regression tests.
- The package rollout order is now explicitly documented, so any reprioritization should update the issue #85 roadmap note and the linked package docs together.
- Testing posture strengthened by relocating UI smoke tests into `tests/ui/`; comprehensive GUI and PDF engine coverage tracking still required.
- Log streams consolidated under `logs/`; rotation policy and SIEM forwarding backlog items remain open.

## 2. Enterprise Requirements Analysis

- **Scalability**: Modularize tools, enforce async/offloading for heavy file operations, containerization support, horizontal scaling via microservice-friendly APIs for non-GUI components.
- **Security**: Maintain ISO 27001/NERC CIP alignment, harden cryptography usage (central key management), enforce code signing, integrate secrets vault, comply with corporate RBAC.
- **Compliance**: Implement audit trails, policy-driven configuration with version control, maintain data residency controls, ensure dependency SBOM and vulnerability scanning.
- **Monitoring & Observability**: Centralize structured logging, introduce telemetry exporters (OpenTelemetry), health checks for services, SLA dashboards for operations.
- **Maintainability**: Enforce layered architecture (core engines vs GUI), ADR log in `docs/adr/`, dependency drift monitoring, automated documentation builds.

## 3. Phased Migration Strategy

| Phase                        | Timeline    | Milestones                                                      | Deliverables                                                        | Rollback Procedure                                                                    |
| ---------------------------- | ----------- | --------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 0. Mobilization              | Weeks 0-2   | Form modernization squad, confirm scope, baseline metrics       | Project charter, risk register, inventory baselines                 | Preserve current branch/tag `baseline-2025Q4`; restore environment snapshot           |
| 1. Foundation Hardening      | Weeks 3-8   | Dependency audit, environment standardization, config hardening | `env/` standards doc, dependency lock file, secrets policy          | Revert via `requirements.txt` tag `pre-hardening`; backup venv binaries               |
| 2. Architecture Refactor     | Weeks 9-18  | Introduce modular core/services split, consolidate entry points | Refactored `src/rfu/` structure, service interface specs            | Maintain feature flags; rollback through blue/green deployment of new module packages |
| 3. Platform Integration      | Weeks 19-28 | Implement observability, security controls, CI/CD pipelines     | CI workflows, monitoring dashboards, compliance reports             | Hot-standby infrastructure; failback to Phase 1 stable branch                         |
| 4. Enterprise Release        | Weeks 29-36 | Pilot deployment, user training, production certification       | Final release notes, signed binaries, training completion           | Controlled rollback plan with data snapshots and auto-redeploy of previous release    |
| 5. Optimization & Governance | Weeks 37-52 | Performance tuning, governance board activation                 | KPI reports, governance charter, backlog of continuous improvements | Rolling release with canary toggles; revert by disabling new optimizations            |

## 4. File System Restructuring Plan

- **Consolidate application code**: Move all runtime code to `src/rfu/` following domains (`core/`, `utilities/`, `interfaces/`, `plugins/`); migrate analytics modules (now located in `src/analytics/`) into `src/rfu/analysis/` to avoid duplication.
- **Archive segregation**: Relocate historical artifacts to `archive/legacy/` with metadata manifest; keep only non-deployable references.
- **Entry point normalization**: Retain `src/main.py` as canonical launcher; convert root `main.py` and `rfu_explorer.py` into thin wrappers or CLI scripts under `src/rfu/cli/`; retire legacy references to `src/rfu/main.py` once modernization gating completes.
- **Testing alignment**: Move root-level pytest files into `tests/ui/` or relevant domain folders; ensure tests mirror `src` structure (e.g., `tests/utilities/file_management/test_file_finder.py`).
- **Naming conventions**: Adopt lower_snake_case for files, PascalCase for classes, kebab-case for docs; create lint rule in `setup.cfg` to enforce.
- **Separation of concerns**: Distinguish GUI (PyQt) from engine logic; place business logic in `src/rfu/services/` callable by CLI, GUI, or API layers.
- **Documentation organization**: Centralize in `docs/` with subfolders `architecture/`, `operations/`, `compliance/`, `adr/`.
- **Asset management**: Move logs to `logs/` with rotation policy, results to `results/` (immutable), generated reports to `reports/`. Ensure `resources/` only hosts static assets consumed by code.

## 5. Quality Assurance Framework

- **Automated Testing**: Expand pytest suites (unit, integration, GUI via `pytest-qt`), enforce >95% coverage with `--cov`; add nightly performance benchmarks using `pytest-benchmark`.
- **Code Review Process**: Implement mandatory two-reviewer rule, security review checklist, static analysis gates (flake8, mypy) enforced in CI before merge.
- **Validation Checkpoints**: Pre-release smoke tests, regression test packs per tool category, user acceptance sign-off for critical GUI workflows.
- **Continuous Integration**: GitHub Actions pipeline (build/lint/test/security scan), nightly dependency scan (Dependabot with custom policies), artifact publishing to internal package registry.
- **Release Certification**: QA sign-off matrix documenting test results, coverage deltas, known issues, and rollback readiness.

## 6. Risk Mitigation Strategies

- **Data Integrity**: Implement transactional backups for configuration and SQLite assets, checksum validation for file operations, automated restore drills each quarter.
- **System Availability**: Introduce blue/green deployment for desktop release packaging, maintain offline installer with integrity checks, establish incident response runbook (RTO ≤ 2h, RPO ≤ 1h).
- **Stakeholder Impact**: Communication plan with release notes, change impact assessments, executive dashboard for modernization progress, dedicated support window after major releases.
- **Security Breach Preparedness**: Centralized logging to SIEM, quarterly penetration testing, run tabletop exercises for crypto key compromise.

## 7. Documentation & Knowledge Transfer

- **Standards**: Adopt Diátaxis framework (tutorials, how-to, reference, explanation) stored in `docs/`; auto-generate API docs via Sphinx + Read the Docs pipeline.
- **Knowledge Base**: Maintain Confluence/SharePoint space with decision logs, runbooks, onboarding checklists; schedule monthly documentation reviews.
- **Training**: Structured training modules for developers (architecture, security), operations (monitoring, deployment), and end-users (tool usage); record sessions for archive.
- **Onboarding Packets**: Provide environment setup scripts, sample datasets, troubleshooting guides; integrate with company LMS for tracking completion.

## 8. Success Metrics & Benchmarks

- **Engineering KPIs**: Code coverage ≥95%, mean PR review time ≤48h, static analysis issues resolved within sprint, build success rate ≥99%.
- **Operational Metrics**: Application startup time ≤3s, file operation throughput improved by 30%, crash-free sessions ≥99.5%, MTTR < 60m.
- **Security & Compliance**: Zero critical vulnerabilities outstanding >7 days, successful quarterly audits, full traceability of config changes.
- **Adoption**: User satisfaction ≥4.5/5, training completion rate ≥95%, support tickets reduced by 40% post-modernization.

## 9. Team Responsibilities & Resource Allocation

- **Program Sponsor**: VP Operations – executive oversight, budget approvals.
- **Modernization Lead**: Enterprise architect coordinating roadmap execution.
- **Core Engineering Squad** (6 FTE): Platform architect, lead developer, two feature engineers, QA engineer, DevSecOps engineer.
- **Security & Compliance** (2 FTE): Security analyst, compliance specialist.
- **Data & Analytics** (1 FTE): Performance benchmarking and reporting.
- **Documentation & Training** (1 FTE): Technical writer/instructional designer.
- **Stakeholder Committee**: Representatives from manufacturing operations, IT infrastructure, and security governance meeting bi-weekly.
- **Contractor Support**: Optional GUI/UX specialist and accessibility consultant engaged during Phase 2.

## 10. Long-Term Maintenance & Governance

- **Governance Board**: Establish RFU Steering Committee (meets monthly) to review KPIs, approve roadmap adjustments, and manage risk register.
- **Lifecycle Policies**: Semantic versioning, quarterly feature releases, monthly patch cadence, end-of-life policy for deprecated tools (12-month sunset).
- **Configuration Management**: Centralized config repository with change control board, automated drift detection, and encrypted secrets storage.
- **Continuous Improvement**: Quarterly retrospectives, backlog grooming for modernization follow-up, annual architecture review with external audit.
- **Support Model**: Tiered support (L1 helpdesk, L2 operations, L3 engineering). Maintain on-call schedule with escalation paths.
- **Sustainability**: Regular dependency updates with SBOM publication, energy-efficient profiling for compute-intensive tasks, alignment with corporate sustainability KPIs.
