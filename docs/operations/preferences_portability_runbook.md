# Preferences Portability Runbook

<!-- markdownlint-disable MD031 MD036 -->

_Status: Draft · Last Updated: 2025-11-12_

This runbook provides step-by-step guidance for operations engineers responsible for
executing and validating the preferences portability tooling in Richard's File
Utilities (RFU). The CLI resides at `scripts/tools/preferences_portability.py`
and supports both export and import workflows with optional AES encryption.

## 1. Prerequisites

- Active RFU virtual environment (`venv\Scripts\activate` on Windows).
- Access to the RFU data directory (`data/rfu_database.db`) and log output (`logs/rfu.log`).
- Optional: `pyAesCrypt` installed if encrypted exports or imports are required.
- Confirm telemetry logging by tailing `logs/rfu.log` and locating
  `RFU.PreferencePortability` entries.

## 2. Export Procedure

1. Identify the user namespace to export (`--user` argument). Defaults to the
   active OS account when not overridden elsewhere in the application.
2. Choose an export destination. If omitted, the CLI writes to the current
   working directory.
3. Run:
   ```powershell
   python -m scripts.tools.preferences_portability export `
       --user default `
       --dest "C:/temp/prefs-exports" `
       --category theming `
       --category favorites `
       --skip-encrypted
   ```
4. When `--encrypt` is supplied, the CLI prompts for a passphrase. Ensure the
   passphrase is stored securely according to security policy.
5. Validate completion:
   - CLI prints `Exported preferences to <path>`.
   - `logs/rfu.log` captures a structured entry with `operation="export"`,
     `entry_count`, `categories`, `encrypted`, and `destination` fields.

## 3. Import Procedure

1. Obtain the exported archive path.
2. Decide whether to remap the user namespace (`--target-user`) or reuse the
   original namespace.
3. Determine collision behavior:
   - Default: skip existing preferences.
   - `--allow-overwrite` to upsert conflicting keys.
4. Run:
   ```powershell
   python -m scripts.tools.preferences_portability import `
       "C:/temp/prefs-exports/default-2025-11-12.json" `
       --target-user staging_default `
       --allow-overwrite
   ```
5. For encrypted payloads, pass `--decrypt` and enter the passphrase when
   prompted.
6. Validate completion:
   - CLI prints `Imported {applied} entries (skipped {skipped}) for user {user_id}`.
   - `logs/rfu.log` records an import entry with `operation="import"`,
     `applied_count`, `skipped_count`, `categories`, `encrypted`, and `source`.

## 4. Telemetry Verification Checklist

- [ ] Confirm both export and import flows log `RFU.PreferencePortability`
      entries with user ID, counts, categories, encryption flag, and
      destination/source metadata.
- [ ] Ensure log timestamps match the execution window and no errors appear
      after the entries.
- [ ] Archive relevant log excerpts in the release evidence folder when
      completing RC-1 validation.

## 5. Common Issues & Remediations

| Symptom                                                     | Root Cause                                  | Resolution                                                                   |
| ----------------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------- |
| `pyAesCrypt not installed` error                            | AES dependency absent                       | Install `pyAesCrypt` or rerun without `--encrypt/--decrypt`.                 |
| `PreferencePortabilityError: destination is not writable`   | Insufficient permissions                    | Choose a writable path or adjust directory ACLs.                             |
| Import reports zero applied entries                         | Source archive empty or categories filtered | Inspect the export JSON and re-run without restrictive `--category` filters. |
| CLI exits with `ClickException` referencing schema mismatch | Export created against newer schema         | Upgrade RFU to match schema version, then retry.                             |

## 6. Post-Execution Validation

1. Run the CLI integration smoke test when feasible:
   ```powershell
   python -m pytest tests/integration/test_preferences_portability_cli.py -q
   ```
2. Spot-check the `user_preferences` table for new or updated rows:
   ```powershell
   python -c "from src.database.database_manager import DatabaseManager;\nprint(len(DatabaseManager().execute_query('SELECT * FROM user_preferences')))
   "
   ```
3. Record outcomes in the release evidence log alongside any archived exports.

## 7. Operations Approval

| Date       | Reviewer                       | Notes                                                                                                                                          |
| ---------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 2025-11-12 | Morgan Patel (Operations Lead) | Observed export/import dry run; confirmed telemetry entries and CLI smoke test pass (`tests/integration/test_preferences_portability_cli.py`). |
| 2025-11-13 | Morgan Patel (Operations Lead) | Dry-run using updated preference adapters (`--dry-run sync`) validated no JSON writes; confirmed audit log entries and zero DB mutations.      |

Store this runbook alongside the release tracker. Update the approval table on
subsequent reviews to preserve traceability.

## 8. Appendix B – Telemetry Dashboard Snapshot

Use the telemetry summary helper to generate a quick dashboard of daily
export/import activity directly from `logs/rfu.log`. The command now also
persists timestamped JSON/Markdown artifacts (plus `*_latest` pointers) under
`reports/telemetry/` for CI automation:

```powershell
python -m scripts.reporting.preferences_portability_summary `
   --log logs/rfu.log `
   --output-dir reports/telemetry
```

Latest snapshot (`reports/telemetry/preferences_portability_summary_latest.md`,
generated 2025-11-14 17:23:28 UTC):

| Date       | Export Runs | Export Entries | Import Runs | Import Entries | Import Applied | Import Skipped |
| ---------- | ----------- | -------------- | ----------- | -------------- | -------------- | -------------- |
| 2025-11-12 | 2           | 1              | 2           | 1              | 1              | 0              |
| 2025-11-13 | 3           | 6              | 1           | 0              | 0              | 0              |
| 2025-11-14 | 1           | 10,000         | 1           | 10,000         | 10,000         | 0              |

Archive the CLI output (or Grafana screenshot when available) alongside the
release evidence bundle for RC-3 and later reviews.
