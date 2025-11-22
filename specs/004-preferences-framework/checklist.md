# Quality Checklist: Unified Preferences Framework

_Status: Draft · Generated 2025-11-12_

Use this checklist to confirm the requirements for the Unified Preferences
Framework are complete, clear, and consistent across specification artifacts.
Reference files:

- `.github/copilot-instructions.md`
- `specs/004-preferences-framework/spec.md`
- `specs/004-preferences-framework/preference_schema_design.md`
- `specs/004-preferences-framework/fleeting_notes_004-preferences-framework.md`
- `specs/004-preferences-framework/plan.md`

## Completeness

- [x] `spec.md` enumerates all preference categories (theming, favorites,
      directories, future namespaces) with typed contracts and migration
      coverage.
- [x] Portability requirements (export destination, payload structure, AES
      support) appear in both `spec.md` and the operational plan.
- [x] `preference_schema_design.md` documents every table, index, and trigger
      required for the current release scope.
- [x] Runbook, telemetry, and tooling tasks listed in `plan.md` cover the
      operational expectations highlighted in the fleeting notes.
- [x] Outstanding items in fleeting notes are mirrored as actionable tasks in
      `plan.md` or intentionally marked as closed.

## Clarity

- [x] Terminology for PreferenceManager, PreferencesStore, ConfigManager, and
      portability is used consistently across all documents.
- [x] Fallback behaviour (environment overrides, JSON read-only mode) is
      described in plain language with no conflicting statements.
- [x] Portability error handling states (DecryptionRequiredError,
      InvalidExportError, missing AES dependency) are explicitly named and
      explained.
- [x] Migration steps outline exact sequencing (backup JSON, map via schema,
      upsert via store, record migration key) without ambiguity.
- [x] Acceptance criteria for CLI integration (UI entry, smoke test, logging)
      are measurable and unambiguous in `plan.md`.

## Consistency

- [x] Schema default values (source, schema_version) match between
      `spec.md`, `preference_schema_design.md`, and existing code comments.
- [x] Fleeting notes "Clarifications" and `spec.md` agree that no unresolved
      constitution items remain.
- [x] `plan.md` phases map cleanly to work already recorded in fleeting notes
      (e.g., portability operationalization, JSON cleanup).
- [x] Optional dependency guidance for `pyAesCrypt` is consistent across spec,
      schema design, and plan documents.
- [x] Testing references (unit, integration, CLI smoke) reflect the current
      suite and future additions planned in `plan.md`.

## Validation Steps

- [x] Run targeted unit tests:
      `python -m pytest tests/unit/test_preferences_manager.py -q` and
      `python -m pytest tests/unit/preferences/test_portability.py -q` (last run 2025-11-12).
- [x] Execute CLI smoke test once implemented to ensure portability tooling
      works end-to-end (`pytest tests/integration/test_preferences_portability_cli.py -q`, 2025-11-12).
- [x] Review logging output for export/import operations to confirm telemetry
      fields match documented expectations (2025-11-12: observed
      `RFU.PreferencePortability` entries in `logs/rfu.log` capturing user_id,
      entry_count, categories, encrypted, destination/source).
- [x] Add structured logging in `src/core/preferences/portability.py` for export/import
      flows (user_id, entry_count, categories, encrypted flag) and re-run the
      telemetry review (completed 2025-11-12).
- [x] Reconcile plan milestones with project tracker or tasks.md before each
      release checkpoint (2025-11-12: see `specs/004-preferences-framework/project_tracker.md` for
      aligned checkpoints and action items).
- [x] Follow-up: implement telemetry logging before marking the above items complete
      (see new `RFU.PreferencePortability` entries dated 2025-11-12).
- [x] Complete Phase 0 schema snapshot and full-suite `pytest` baseline prior to
      closing RC-1 (2025-11-12: see `reports/preferences_schema_snapshot_2025-11-12.json`
      and `reports/pytest_full_run_2025-11-12.txt`; baseline notes legacy `AppLog`
      NameError in archived tests).
- [x] Summarize documentation diff audit findings for Phase 0 baseline
      traceability (2025-11-12: see Documentation Diff Audit in
      `specs/004-preferences-framework/project_tracker.md`).
- [x] Open remediation tracking for the legacy `AppLog` NameError surfaced by the
      global pytest baseline (2025-11-12: see
      `specs/004-preferences-framework/remediation_app_log_nameerror.md`).
- [x] Draft the portability runbook and capture operations approval before RC-1
      sign-off (2025-11-12: see `docs/operations/preferences_portability_runbook.md`
      and approval table logged in `project_tracker.md`).
