# Preferences Framework Release Notes

_Status: Draft · Generated 2025-11-14_

## 1. Overview

Richard's File Utilities now routes preference writes/reads through the unified `PreferencesStore`/`PreferenceManager` stack with export/import tooling for user portability. This document captures the release-ready state, migration progress, validation evidence, known gaps, and telemetry checkpoints required for rollout.

## 2. Release Readiness Snapshot

| Area                      | Status                                                                                                                                                                                                                           | Evidence |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Preference migration      | ✅ JSON fallbacks disabled for migrated keys; explorer services and adapters persist via `PreferenceManager` only. Sweep recorded in `specs/004-preferences-framework/fleeting_notes_004-preferences-framework.md` (2025-11-13). |
| Portability tooling       | ✅ CLI export/import flows validated (operations dry-run on 2025-11-13; encrypted import test added 2025-11-14).                                                                                                                 |
| Concurrency & reliability | ✅ `tests/integration/test_preferences_portability_concurrent.py` exercises simultaneous exports during mutations using isolated SQLite state.                                                                                   |
| Encryption support        | ✅ `tests/integration/test_preferences_portability_encrypted.py` verifies AES exports/imports with conditional skip when `pyAesCrypt` absent.                                                                                    |
| Coverage                  | ✅ Maintained unit/core suites executed with coverage on 2025-11-14; HTML artifacts under `reports/preferences_portability_cov/`.                                                                                                |
| Performance               | ⚠️ Benchmark shows fast exports (0.433 s for 10k entries) but slow imports (44.714 s; ~224 entries/s). Follow-up captured to evaluate batching/transactions.                                                                     |
| Runbook / plan alignment  | ✅ Operations runbook updated 2025-11-12; plan/tracker cross-referenced after each dry-run; remaining UX screenshot appendix tracked elsewhere.                                                                                  |

## 3. Migration Progress Summary

- `ConfigManager.set_setting` writes to `general.theme`, `default_directory`, `recent_directories`, and `show_hidden` disabled in active modules; lingering references documented only in archived files.
- Explorer services (bookmarks, layout, recent directories) use dedicated adapters built atop `PreferenceManager`, ensuring a single authority for preference persistence.
- Preference bootstrap (`DatabaseManager`) migrates legacy audit tables and records migration keys; first-run backups stored in `config/rfu_config_backup_*.json`.
- Operations dry-run (2025-11-13) confirmed CLI export/import zero-entry success with action items reconciled across plan/tracker/fleeting notes.

## 4. Quality & Validation Evidence

- **Unit & Integration Tests**
  - `tests/unit/preferences/test_explorer_adapters.py`: confirms adapters write via `PreferenceManager`.
  - `tests/integration/test_preferences_portability_concurrent.py`: concurrent export safety.
  - `tests/integration/test_preferences_portability_encrypted.py`: AES passphrase path with skip guard when `pyAesCrypt` missing.
- **Coverage**
  - Command: `python -m pytest --cov=src --cov-report=html:reports/preferences_portability_cov --cov-report=term -v` (2025-11-14).
  - Result: Maintained unit/core suite green; HTML summary stored under `reports/preferences_portability_cov/index.html`.
- **Benchmark**
  - Command: `python -m scripts.perf.preferences_portability_benchmark` (10k entries, 50 categories).
  - Metrics: seed 2.843 s; export 0.433 s; import 44.714 s; export size 2.41 MiB.
  - Observation: Import path limited by per-row upserts and audit triggers; batching/transaction scope under evaluation.

## 5. Known Limitations & Risks

1. **Import Throughput** – Current import latency (~224 entries/s) may be insufficient for large tenant migrations. Performance investigation (Engineering Perf Team · Due 2025-12-05) in-flight.
2. **Optional Dependency Coverage** – Encrypted flows require `pyAesCrypt`. Operations must validate availability on target hosts (Morgan Patel · Due 2025-11-22).
3. **Telemetry Dashboard** – Aggregated reporting (Phase 4) not yet implemented; manual log review required for now.
4. **UX Evidence** – Hub launcher screenshot + walkthrough appendix pending (tracked in tasks/plan).

## 6. Telemetry & Monitoring Checkpoints

| Checkpoint                             | Owner          | Status      | Notes                                                                                                              |
| -------------------------------------- | -------------- | ----------- | ------------------------------------------------------------------------------------------------------------------ |
| CLI export/import telemetry log review | Operations     | Manual      | Inspect `logs/rfu.log` for `preferences_export_completed` / `preferences_import_completed` entries after each run. |
| Runbook cadence reminder               | Program Mgmt   | Pending     | Needs calendar entry + tracker note for quarterly CLI smoke test and screenshot refresh (Phase 4 task).            |
| Daily aggregation script               | Reporting Team | Not started | Future script (`scripts/reporting/preferences_portability_summary.py`) will emit per-day counts once implemented.  |
| Coverage drift monitoring              | QA Lead        | Pending     | Evaluate expanding pytest discovery beyond maintained suites once legacy tests are remediated (Due 2025-11-29).    |

## 7. Release Checklist

- [x] Document portability status and migration evidence.
- [x] Capture benchmark + coverage artifacts.
- [ ] Publish release notes to stakeholders (Release Mgmt) and collect sign-off.
- [ ] Attach telemetry dashboard output once Phase 4 monitoring work completes.

## 8. Contacts

- **Product / Operations**: Morgan Patel (Operations Lead)
- **Engineering**: Priya Shah (QA Coordinator), Engineering Perf Team (import optimization)
- **Documentation**: Release Management Guild
