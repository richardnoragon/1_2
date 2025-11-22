# Spec: Unified User Preferences Framework

Status: Baseline Update · Owner: Core Platform · Created: 2025-11-01

## Summary

Introduce a unified, database-backed Preference Framework that provides:

- Universal theming across tools (active theme + named profiles)
- Favorites management (paths and tools) with stable keys
- Directory preferences (default root, recents, show-hidden)
- Typed, namespaced, and migration-ready storage

The framework is exposed via `PreferenceManager` on top of the existing
`PreferencesStore` (DB CRUD). It aligns with Constitution v1.1.0 “VI. User
Preference Management & Personalization”.

## Goals

- Strong separation of concerns: modules depend on a high-level API, not DB
- Backward compatible with JSON ConfigManager; safe incremental adoption
- Extensible categories and keys without cross-module coupling
- Typed persistence with upsert semantics and clear namespacing

## Architecture

Layers:

- Storage: SQLite `user_preferences` (existing) managed by `DatabaseManager`
- Store: `PreferencesStore` (typed CRUD, batch set, list categories)
- Manager: `PreferenceManager` (user-scoped, category-specific helpers)

Key categories:

- theming: `theme`, `profile:<name>` (dict)
- favorites: `path:<hash>`, `tool:<name>` (dict records)
- directories: `default_root` (str), `recent` (list[str]), `show_hidden` (bool)

## Repository Survey (2025-11-03)

| Surface             | Files                                                                                                                            | Notes                                                                                                                                                       |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Config baselines    | `src/config/config_manager.py`, `src/config_manager.py`, `src/rfu/config_manager.py`, `config/rfu_config.json`                   | JSON defaults still define theme, recent directories, and validator profiles; RFU `ConfigManager` wraps these for validator workflows.                      |
| Database managers   | `src/database/database_manager.py`, `src/file_explorer/database/schema.py`                                                       | Canonical manager resides in `src/database/database_manager.py`; explorer schema now delegates to PreferenceManager and no longer provisions its own table. |
| Preference APIs     | `src/core/preferences/store.py`, `src/core/preferences/manager.py`                                                               | Store enforces typed CRUD; manager augments theming, favorites, directories; both depend on the canonical `DatabaseManager`.                                |
| Portability tooling | `src/core/preferences/portability.py`, `scripts/tools/preferences_portability.py`                                                | Module + CLI export typed snapshots to `backups/preferences/<user>` with optional AES encryption and rehydrate via `PreferencesStore`.                      |
| Config migration    | `src/config/schema_map.py`, `src/database/migrations/json_to_preferences.py`                                                     | `schema_map.map_config_to_preferences` converts JSON payloads into category/key dictionaries consumed by the migration helper.                              |
| GUI integration     | `src/gui/themes.py`, `src/tabbed_hub.py`, `src/file_explorer/features/hub_interface_toggle.py`, `src/rfu/preferences_adapter.py` | GUI bootstrap sets theme via `PreferenceManager`; tabbed hub toggle persists interface mode via `HubPreferencesAdapter` with legacy fallback support.       |
| Tests & fixtures    | `tests/unit/test_preferences_manager.py`                                                                                         | Covers CRUD roundtrips, theming profiles, favorites, directory prefs.                                                                                       |
| Docs & notes        | `specs/004-preferences-framework/spec.md`, `specs/004-preferences-framework/fleeting_notes_004-preferences-framework.md`         | Spec and fleeting notes track architecture decisions and open items.                                                                                        |

Highlighted gaps:

- Explorer schema now provisions only pane/history/bookmark data; explorer preferences resolve exclusively through the unified store.
- JSON defaults continue to carry theme and directory state; migration shims must backfill into the DB layer.

## Contracts

- User identity resolution: applications may pass an explicit `user_id` when
  constructing `PreferenceManager`. When omitted, the manager resolves the
  active ID via the `RFU_USER_ID` environment variable, then the operating
  system account (`getpass.getuser()`), and finally the fallback literal
  `"default"`. Multi-session or profile-aware tools should set `RFU_USER_ID`
  per session or supply the `user_id` argument directly.

## Migration & Compatibility

- Uses existing `user_preferences` table; no schema change required
- Compatible with `EnhancedConfigManager` and file-backed `ConfigManager`
- Module independence: each feature owns its category/keys; no shared coupling
- Encryption-ready: `is_encrypted` flag retained for future envelope crypto

### JSON ConfigManager → Preferences Store Migration

1. **Snapshot legacy payload**: Fetch the current `ConfigManager` state via its
   `get_all_settings()` helper (or equivalent) while holding any required file
   locks. Persist a JSON backup alongside timestamped metadata in
   `config/backups/` before mutating data.
2. **Normalize into preference categories**: Use
   `schema_map.map_config_to_preferences()` to translate the JSON structure into
   a `{category: {key: value}}` dictionary. Categories currently include
   `theming` (active theme, saved profiles) and `directories` (default root,
   recents, show_hidden). Module-specific entries can extend the helper by
   adding namespaced keys.
3. **Write through `PreferencesStore`**: Iterate categories and upsert via
   `PreferencesStore.set_category`, which enforces value typing before writing
   to the database. Tag every write with `source='config-migration'` to support
   audit forensics.
4. **Record migration key**: After a successful upsert, call
   `pref/2025-11-11/config-bootstrap` so the bootstrap logic remains idempotent.
5. **Retire migrated JSON fields**: Remove or blank the migrated entries from
   `config/rfu_config.json`. The ConfigManager layer should now treat the
6. **Explorer legacy bridge (retired)**: The beta cut removes the explorer
   `user_preferences` table entirely. Earlier alpha builds may still contain a
   legacy `data/file_explorer.db`; once the ConfigManager bootstrap runs, all
   explorer state lives in the canonical store and the legacy table is no

### Post-Migration Fallback Contract

- **Source of truth**: After `pref/2025-11-11/config-bootstrap` records as
  applied, the SQLite preference store is authoritative for every category
  migrated from JSON (`theming`, `directories`, and any future namespaces
- **JSON scrub**: The migration step that retires JSON fields erases
  `general.theme`, `default_directory`, `recent_directories`, and
  `show_hidden` (plus any additional mapped keys). Config backups remain
  runtime drift.
- **Read-only fallback**: `ConfigManager` stays available for modules that
  have not yet adopted `PreferenceManager`, but those callers must treat the

## Portability & Export/Import

- Location: `export_preferences` writes timestamped JSON snapshots into
  `backups/preferences/<user_id>/preferences_<timestamp>.json` (appending
  `.json.aes` when encryption is requested). The helper creates the directory
  automatically when absent.
- Format: The export payload includes `version`, `exported_at` (UTC ISO 8601),
  `user_id`, `entry_count`, and an ordered `entries` array. Each entry records
  `category`, `key`, `value`, `value_type`, `is_encrypted`, `source`, and
  `schema_version`. Values are emitted as native JSON types; the helper
  performs the same deserialization the store uses for reads.
- CLI workflow: `scripts/tools/preferences_portability.py` exposes
  `export`/`import` commands. `--encrypt` prompts for an AES passphrase using
  `pyAesCrypt`; `--skip-encrypted` filters secrets during exports; imports
  accept `--target-user` overrides and `--allow-overwrite` when collisions are
  expected.
- Optional dependency: AES encryption/decryption requires `pyAesCrypt`. When
  the library is absent, the helpers raise friendly errors and the CLI blocks
  `--encrypt/--decrypt` usage.
- Source tagging: exports preserve the current row `source` values; successful
  imports update `source='pref-import'` while preserving `schema_version`
  whenever the payload provides one.
- Error handling: encrypted payloads without a passphrase raise
  `DecryptionRequiredError`; malformed payloads (missing keys, wrong types)
  raise `InvalidExportError`. The helpers surface descriptive messages so the
  CLI can provide actionable feedback for operators.
  sanitized sections as read-only. If a component still calls
  `ConfigManager.set_setting` for a migrated key, the JSON write succeeds
  locally but the DB state is not overwritten; the next bootstrap will simply
  reapply the sanitized defaults, so feature owners should finish their
  PreferenceManager migration instead of relying on JSON writes.
- **Failure mode**: When the preference database cannot be reached at launch,
  bootstrap code falls back to defaults (light theme, empty recents). Operators
  can re-run `json_to_preferences.migrate_preferences_from_config` to hydrate
  from the most recent JSON backup once the database becomes available again.
- **Drift detection**: Operations runbooks now include a sanity check that the
  sanitized JSON sections remain empty. If a migrated key ever repopulates in
  `config/rfu_config.json`, treat it as a signal that a module is still writing
  through JSON and schedule the remaining PreferenceManager migration work.

## Adoption

Short term:

- Read active theme via `PreferenceManager.get_theme()` in GUI bootstrap
- Tools may opt-in to favorites and directory prefs via the manager
- Hub interface toggle in `tabbed_hub.py` now persists mode through `HubPreferencesAdapter`, keeping PreferenceManager as the source of truth when available.

Medium term:

- Replace ad-hoc per-tool settings with namespaced categories
- Add minimal migration shims (config → DB) where user-facing
- Transition explorer-facing services to PreferenceManager (retiring the
  legacy `PreferenceService` shim once migrations and tests complete)

## Testing

Unit coverage (added):

- CRUD roundtrip with types
- Theming: active theme, save/load/list profiles
- Favorites: add/list/remove paths and tools
- Directories: set/get including defaults
- Explorer regression: `tests/unit/preferences/test_explorer_legacy_etl.py`
  now asserts the explorer schema omits the legacy table and that no migration
  helper remains.

Integration coverage:

- `tests/integration/test_preference_bootstrap_integration.py` validates
  first-launch hub mode defaults and theme persistence callbacks.

Future:

- Additional GUI-wiring coverage for interactive flows targeting real PyQt
  widgets.

## Risks & Mitigations

- Global DB contention → WAL mode and pooled connections already enabled
- Backwards settings drift → retain ConfigManager reads as fallback where needed
- Key sprawl → enforce clear category ownership and kebab-case naming
