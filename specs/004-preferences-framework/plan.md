# Implementation Plan: Unified Preferences Framework

_Status: Draft · Last Updated: 2025-11-14_

This execution plan translates `specs/004-preferences-framework/spec.md`,
`preference_schema_design.md`, and the active items in
`fleeting_notes_004-preferences-framework.md` into concrete workstreams.
The motto "better many smaller detailed steps over larger vague ones" guides the
structure below.

## Guiding Objectives

1. Keep `src/database/database_manager.py` the canonical schema owner and ensure
   all preference access flows through `PreferencesStore`/`PreferenceManager`.
2. Finish operationalizing portability (export/import) with runbooks,
   automation, and telemetry to satisfy Constitution Principle VI expectations.
3. Eliminate residual JSON/legacy dependencies while maintaining documented
   fallbacks for business continuity.
4. Deliver comprehensive validation to prove typed persistence, migration, and
   portability behave as specified.

## Phase 0 – Baseline Verification

1. **Inventory Current State**
   - Fetch git status; snapshot existing modifications for traceability.
   - Re-run `pytest tests/unit/preferences/test_portability.py -q` and
     `pytest tests/unit/test_preferences_manager.py -q` to confirm local green
     baselines.
   - Attempt a full `pytest` run; capture the existing global suite failures
     cited in the fleeting notes and open a remediation task with logs attached.
   - Capture SQLite schema via
     `DatabaseManager().execute_query("PRAGMA table_info(user_preferences)")`
     to freeze the canonical reference.
2. **Documentation Sync Audit**
   - Diff `spec.md`, `preference_schema_design.md`, and
     `fleeting_notes_004-preferences-framework.md` against current plan to
     ensure terminology and contracts are aligned.
   - Log any deltas in the fleeting notes "Clarifications" section before
     advancing.

## Phase 1 – Portability Operationalization

1. **Runbook Authoring**
   - Draft `docs/operations/preferences_portability.md` covering:
     - Export usage examples with and without AES.
     - Import collision handling (skip vs overwrite).
     - Common failure remediation (missing `pyAesCrypt`, malformed payloads) and guidance when AES is unavailable.
   - Canonical operations reference is now `docs/operations/preferences_portability_runbook.md`, including the operations approval table dated 2025-11-12.
   - Peer review with operations SMEs; record approval in fleeting notes.

1. **CLI Integration**
   - Expose portability tooling via the RFU hub launcher:
     - Add a menu/button entry calling `self.launch_tool("Preference Portability", ...)` (follow tool discovery conventions).
     - Validate that launching opens a small wrapper window or terminal prompt per UX guidelines.
     - Acceptance criteria: UI entry visible in hub, manual launch completes without error, CLI smoke test passes, telemetry event recorded.
     - Documentation checkpoint: Phase 1 references must point to `docs/operations/preferences_portability_runbook.md` and preserve the 2025-11-12 approval table provenance.
1. **Automated Smoke Test**
   - Add `tests/integration/test_preferences_portability_cli.py` running the
     CLI via `subprocess.run` (no AES) to export/import sample data and assert
     exit code + JSON payload integrity.
   - Mark test with `@pytest.mark.cli` for selective execution.
1. **Telemetry/Logging Hooks**
   - Update `export_preferences`/`import_preferences` to emit structured log
     events (`logger = get_log_manager().get_logger("PreferencePortability")`).
   - Include fields: `user_id`, `entry_count`, `categories`, `encrypted` flag.
   - Document the new log format in the runbook appendix.

## Phase 2 – Adoption & Cleanup

1. **Remaining JSON Consumers**
   - Audit modules still writing via `ConfigManager.set_setting` for migrated
     keys; file targeted tasks to move them onto `PreferenceManager` (one task
     per module).
   - Update fleeting notes table with migration statuses.
2. **Explorer & Tooling Verification**
   - Confirm explorer services exclusively read from `PreferencesStore` by
     grepping for `PreferenceService` references; remove any remaining shims.
   - Add regression tests if new adapters exist.
3. **Operator Feedback Loop**
   - Schedule live dry-run of portability tooling with the operations team.
   - Collect feedback; open issues for usability gaps and track them in
     fleeting notes ("Follow-up emphasis" section).
   - 2025-11-13: Operations dry-run completed by Morgan Patel (Operations Lead)
     using `python -m scripts.tools.preferences_portability`; zero-entry payload
     validated and observations captured in the tracker and fleeting notes.
   - Follow-up (Owner: Morgan Patel · Due 2025-11-15): update
     `docs/operations/preferences_portability_runbook.md` with explicit
     `python -m` invocation guidance and a pre-flight dependency checklist
     covering virtual-environment activation and `pip install -r requirements.txt`.
   - Follow-up (Coordinator: Priya Shah · Due 2025-11-18): assign QA ownership
     for the PreferenceManager outage integration scenario so legacy fallback
     behaviour remains observable.

## Phase 3 – Quality & Release Readiness

1. **Expanded Test Coverage**
   - Introduce integration tests covering:
     - Concurrent exports while preferences mutate (simulate using threads).
     - Importing encrypted payloads (conditional skip when `pyAesCrypt` absent).
   - Ensure coverage reports (`pytest --cov=src`) include the portability
     module.
   - Status (2025-11-14): Concurrent export coverage implemented in
     `tests/integration/test_preferences_portability_concurrent.py`, encrypted
     import coverage added via
     `tests/integration/test_preferences_portability_encrypted.py`, and a
     coverage report generated for the maintained unit/core suite (see
     `reports/preferences_portability_cov/index.html`). Performance benchmarks
     and release notes remain outstanding; broaden coverage scope once legacy
     suites or expanded targets are re-enabled.
2. **Performance Profiling**
   - Benchmark export/import on large datasets (~10k preferences) to validate
     acceptable latency; record results in `reports/preferences_portability_perf.md`.
3. **Release Checklist**
   - Verify documentation references in `spec.md` are up-to-date.
   - Draft release notes summarizing portability, migration status, and known
     limitations (AES dependency, global test suite caveats).

## Phase 4 – Post-Launch Monitoring

1. **Telemetry Dashboard**
   - Create a simple reporting script (or Grafana panel) summarizing export /
     import frequency and failure counts from log data.
   - Status (2025-11-14): `scripts/reporting/preferences_portability_summary.py`
     ingests `logs/rfu.log`, writes timestamped JSON/Markdown snapshots to
     `reports/telemetry/`, and feeds the table now embedded in
     `docs/operations/preferences_portability_runbook.md` Appendix B; future
     iterations will evaluate Grafana parity once ops pipelines stabilize.
2. **Maintenance Cadence**
   - Add quarterly reminder to re-run CLI smoke test, validate dependency pins,
     and refresh ops runbook screenshots.
   - Status (2025-11-14): Program Mgmt calendar invite scheduled for the first
     business Monday of each quarter; cadence documented in
     `project_tracker.md` Phase 4 milestone evidence.
3. **Feedback Triage**
   - Keep fleeting notes updated with any new issues; once stabilized, graduate
     remaining tasks into `tasks.md` or product backlog.
   - Status (2025-11-14): "Feedback Triage Checklist" recorded in
     `fleeting_notes_004-preferences-framework.md` Section XV outlining the
     capture → assess → route → close loop workflow.

## Exit Criteria

- All portability documentation, telemetry, and automation items implemented
  and verified.
- No remaining modules write migrated preference keys through JSON.
- Tests (unit, integration, CLI smoke) pass consistently on CI.
- Fleeting notes "Clarifications" section remains empty for two consecutive
  reviews, indicating no open questions.

---

Prepared by: GitHub Copilot (GPT-5-Codex Preview) on 2025-11-12.
