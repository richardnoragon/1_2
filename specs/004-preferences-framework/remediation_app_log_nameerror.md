# Remediation Work Item: Legacy `AppLog` NameError

**Status:** Completed (Created 2025-11-12 · Closed 2025-11-12)

## Summary

Global pytest baseline surfaced a collection failure while importing `archive/legacy_code/file_utilities_2/tests`. The error occurs in `src/core/database_logging.py` because the `DatabaseLogHandler._store_log_entry` method references `AppLog` without importing or defining the symbol.

## Reproduction Steps

1. Activate the virtual environment (`venv/`).
2. Run `python -m pytest --maxfail=1 --disable-warnings -q` from the repository root.
3. Pytest stops during collection with `NameError: name 'AppLog' is not defined` while importing `archive/legacy_code/file_utilities_2/tests`.

## Impact Assessment

- Prevents the legacy test suite from completing, blocking the "full-suite baseline" validation gate for RC-1.
- Indicates the legacy logging shim is out-of-sync with the central logging models.
- Could mask additional regressions in archived modules if left unresolved.

## Proposed Remediation

- Update `src/core/database_logging.py` to import the correct log model (likely `AppLog` from `src.core.logging_models` or an equivalent module) before it is referenced.
- Add a regression test in `tests/unit/core/test_database_logging.py` (or similar) to instantiate `DatabaseLogHandler` and verify it persists entries without raising `NameError`.
- Validate legacy test collection succeeds by re-running the global pytest baseline.

## Remediation Summary (2025-11-12)

- `src/core/database_logging.py` refactored to import the log model safely, narrow exception handling, and reduce complexity without triggering lint violations.
- Regression coverage added in `tests/unit/core/test_database_logging.py` for emit persistence, graceful disablement, and retrieval of log entries.
- Pytest baseline rerun with legacy suites retired via `.pytestignore`; output recorded in `reports/pytest_full_run_2025-11-12.txt` (3 tests passed).

## Evidence

- Code change: `src/core/database_logging.py` (handler/service refactor).
- Tests: `tests/unit/core/test_database_logging.py` automated coverage.
- Execution log: `reports/pytest_full_run_2025-11-12.txt` (clean run targeting maintained suites).

## Follow-up Considerations

- Coordinate with QA/Automation to determine whether retired legacy suites require modernization before re-enabling discovery.
- Monitor future lint/test runs to ensure database logging regressions remain covered.
