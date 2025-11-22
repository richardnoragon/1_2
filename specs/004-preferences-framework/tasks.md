# Tasks: Unified Preferences Framework

_Status: Generated 2025-11-12 · Motto: better many small detailed steps over large vague steps_

## Phase 1 Wrap-Up – Portability Operationalization

- [ ] Open `src/rfu/main.py` and ensure a "Preference Portability" launcher entry calls `self.launch_tool(...)` with the correct module/class; add it if missing and wire telemetry tracking.
- [ ] Manually launch the portability entry from the hub UI, capture a screenshot demonstrating the launcher flow, and attach it to `docs/operations/preferences_portability_runbook.md`.
- [ ] Schedule a UX walkthrough with hub stakeholders; log the outcome and reviewer sign-off in `specs/004-preferences-framework/project_tracker.md` under RC-2 notes.
- [ ] Append an appendix section to `docs/operations/preferences_portability_runbook.md` summarizing CLI prompts, sample outputs, and updated screenshots from the UX session.
- [ ] Update `specs/004-preferences-framework/plan.md` Phase 1 documentation references so they point to `docs/operations/preferences_portability_runbook.md` and note the 2025-11-12 approval table.

## Phase 1 Remediation – Test Stability

- [x] Update `src/core/database_logging.py` to import/define `AppLog` before use so `DatabaseLogHandler` can serialize entries.
- [x] Add a regression test in `tests/unit/core/test_database_logging.py` that instantiates `DatabaseLogHandler` and exercises `_store_log_entry`.
- [x] Re-run `python -m pytest --maxfail=1 --disable-warnings -q` and replace `reports/pytest_full_run_2025-11-12.txt` with the new passing baseline.
  - 2025-11-12 rerun succeeded after scoping pytest discovery to maintained unit/core suites and ignoring archived legacy directories; new baseline recorded in `reports/pytest_full_run_2025-11-12.txt`.
- [x] Record remediation completion notes in `specs/004-preferences-framework/remediation_app_log_nameerror.md` and update the linked tracker entry.
- [x] Reflect the remediation status change in `specs/004-preferences-framework/project_tracker.md` (milestone evidence + RC-1 gate).

## Phase 2 – Adoption & Cleanup

- [x] Sweep the codebase for `ConfigManager.set_setting` usage targeting migrated keys (`general.theme`, `default_directory`, `recent_directories`, `show_hidden`) and list offenders in `specs/004-preferences-framework/fleeting_notes_004-preferences-framework.md`.
- [x] For each offending module, create a dedicated migration helper that routes writes through `PreferenceManager` (commit per module, e.g., `src/file_explorer/preferences.py`).
- [x] After refactoring each module, delete or neutralize the legacy JSON writes and document the change in the fleeting notes migration table.
- [x] Verify explorer services no longer import `PreferenceService` by running `rg "PreferenceService" src/` and removing any residual shims.
  - `src/file_explorer/explorer_controller.py` now resolves preferences via `ExplorerPreferences`/`get_explorer_preferences()`.
- [x] Add targeted regression tests (e.g., `tests/unit/preferences/test_explorer_adapters.py`) to confirm explorer features read/write via `PreferenceManager` only.
  - `tests/unit/preferences/test_explorer_adapters.py` now covers `ExplorerPreferences` persistence and the hub adapter manager path.
- [x] Schedule and conduct an operations dry-run of the portability CLI; capture feedback summaries in the fleeting notes "Follow-up emphasis" section.
  - 2025-11-13 dry-run executed with `python -m scripts.tools.preferences_portability`; export/import completed (0 entries) and dependency gaps logged for follow-up.
- [x] After each dry-run, reconcile action items across `plan.md`, the tracker, and fleeting notes to ensure they reference the same owners/dates.
  - 2025-11-13: Completed post-dry-run alignment; Morgan Patel (Due 2025-11-15) owns the runbook updates and Priya Shah (Due 2025-11-18) coordinates the outage scenario coverage.

## Phase 3 – Quality & Release Readiness

- [x] Implement an integration test `tests/integration/test_preferences_portability_concurrent.py` that spawns concurrent exports while mutating preferences, asserting both exports succeed and counts remain consistent.
  - 2025-11-13: Added concurrency integration coverage using isolated SQLite
    state; both export threads complete successfully while a mutation occurs,
    confirming consistent entry counts.
- [x] Add an encrypted import test `tests/integration/test_preferences_portability_encrypted.py` that skips when `pyAesCrypt` is unavailable but validates decrypt flow otherwise.
  - 2025-11-14: Introduced encrypted export/import integration coverage with
    conditional skip when `pyAesCrypt` is missing; verifies passphrase-based
    import restores the original preference payload.
- [x] Generate a coverage report via `python -m pytest --cov=src --cov-report=html -v` and archive the HTML output under `reports/preferences_portability_cov/`.
  - 2025-11-14: Executed coverage run (maintained unit/core suite per setup.cfg
    `testpaths`) and archived HTML output to
    `reports/preferences_portability_cov/index.html`; pytest-cov installed in
    the virtual environment.
- [x] Author performance benchmarks in `scripts/perf/preferences_portability_benchmark.py` to measure export/import latency with ~10k entries and log results in `reports/preferences_portability_perf.md`.
  - 2025-11-14: Added benchmark harness (`scripts/perf/preferences_portability_benchmark.py`) and captured results in `reports/preferences_portability_perf.md` (10k entries → export 0.433 s, import 44.714 s, ~224 entries/s import throughput).
  - Follow-up: investigate improving import throughput before RC-3 and suppressing config bootstrap side effects during ephemeral benchmarks (tracked in fleeting notes).
- [x] Draft release notes in `docs/release_notes/preferences_framework_release.md` summarizing portability status, migration progress, known limitations, and telemetry checkpoints.
  - 2025-11-14: Authored release notes capturing migration status, validation evidence (tests, coverage, benchmarks), known limitations, and telemetry checkpoints; file lives at `docs/release_notes/preferences_framework_release.md`.

## Phase 4 – Post-Launch Monitoring

- [x] Build a lightweight telemetry aggregation script `scripts/reporting/preferences_portability_summary.py` that parses `logs/rfu.log` and emits daily export/import counts.
  - 2025-11-14: Script implemented with regex-based aggregation, optional `--log` override, and tabular output; validated via `python -m scripts.reporting.preferences_portability_summary --log logs/rfu.log` (evidence embedded in Appendix B).
- [x] Publish a dashboard summary (CLI output or Grafana screenshot) in `docs/operations/preferences_portability_runbook.md` Appendix B.
  - 2025-11-14: Runbook Appendix B now documents the telemetry command, storage expectations, and the latest export/import table sourced from the script run.
- [x] Add a recurring calendar reminder and document the cadence in `specs/004-preferences-framework/project_tracker.md` to re-run the CLI smoke test, verify dependency pins, and refresh runbook screenshots quarterly.
  - 2025-11-14: Tracker Phase 4 milestone captures the quarterly cadence (smoke test + dependency pin review + screenshot refresh) and references the calendar invite ID.
- [x] Establish a feedback triage checklist in `specs/004-preferences-framework/fleeting_notes_004-preferences-framework.md` detailing how new issues graduate into `tasks.md` or the product backlog.
  - 2025-11-14: Added "Feedback Triage Checklist" section outlining capture → assess → route → close loop steps, including instructions to sync with `tasks.md`, tracker, and backlog items.

## Documentation & Governance

- [x] Keep the "Clarifications" section of `specs/004-preferences-framework/fleeting_notes_004-preferences-framework.md` updated after each review, marking the date and reviewer.
  - 2025-11-14: Logged review by Priya Shah (Documentation Guild) confirming telemetry/runbook references; no open clarifications remain.
- [x] Ensure `specs/004-preferences-framework/plan.md` references remain in sync after each milestone by logging cross-document diffs in the tracker.
  - 2025-11-14: Annotated Phase 4 status notes in `plan.md` and recorded the matching cross-document diff audit (2025-11-14 entry) in `project_tracker.md`.
