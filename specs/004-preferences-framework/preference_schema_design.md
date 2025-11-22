# Preference Database Schema Design

Status: Draft · Last Updated: 2025-11-03 · Owner: Core Platform

## Goals

- Provide a single, typed schema for all RFU user preferences.
- Ensure compatibility with JSON-backed ConfigManager defaults; explorer-specific tables have been removed in beta builds.
- Enable auditing, migrations, and future encryption without breaking existing readers.

## Table Definitions

### user_preferences

```sql
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    preference_category TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT NOT NULL,
    value_type TEXT NOT NULL CHECK (value_type IN ('string','int','float','bool','json')),
    is_encrypted BOOLEAN NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'rfu-core',
    schema_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, preference_category, preference_key)
);
```

- `user_id`: RFC-consistent identifier, defaults to `default` for single-user mode.
- User identity resolution: `PreferenceManager` accepts explicit IDs; when
  omitted it checks `RFU_USER_ID`, then the OS username (`getpass.getuser()`),
  finally falling back to `default`.
- `preference_category`: kebab-case or scoped namespace (`module_settings/<module>`).
- `preference_key`: non-empty ASCII token; profiles use prefixes (e.g., `profile:dark`).
- `source`: provenance tag (`rfu-core`, historical `explorer-migration`, etc.) for observability.
- `schema_version`: row-level version to support future structural upgrades.

### preference_audit_log

```sql
CREATE TABLE IF NOT EXISTS preference_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    preference_category TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    change_type TEXT NOT NULL CHECK (change_type IN ('insert','update','delete')),
    value_type TEXT,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT,
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- Captures every write operation (post-migration) with before/after payloads.
- `changed_by` records actor (GUI tool, CLI, automation).
- `change_reason` optional free-form rationale for admin operations.

### preference_migrations

```sql
CREATE TABLE IF NOT EXISTS preference_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_key TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by TEXT,
    notes TEXT
);
```

- Records idempotent migrations (data backfills, schema upgrades).
- `migration_key` naming convention: `pref/<yyyy-mm-dd>/<slug>`.

## Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_category
    ON user_preferences(user_id, preference_category);

CREATE INDEX IF NOT EXISTS idx_user_preferences_category_key
    ON user_preferences(preference_category, preference_key);

CREATE INDEX IF NOT EXISTS idx_user_preferences_updated_at
    ON user_preferences(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_preference_audit_user_time
    ON preference_audit_log(user_id, created_at DESC);
```

## Triggers

```sql
CREATE TRIGGER IF NOT EXISTS trg_user_preferences_updated
AFTER UPDATE ON user_preferences
BEGIN
    UPDATE user_preferences
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_user_preferences_audit_insert
AFTER INSERT ON user_preferences
BEGIN
    INSERT INTO preference_audit_log (
        user_id, preference_category, preference_key,
        change_type, value_type, new_value, changed_by
    ) VALUES (
        NEW.user_id, NEW.preference_category, NEW.preference_key,
        'insert', NEW.value_type, NEW.preference_value, NEW.source
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_user_preferences_audit_update
AFTER UPDATE ON user_preferences
BEGIN
    INSERT INTO preference_audit_log (
        user_id, preference_category, preference_key,
        change_type, value_type, old_value, new_value, changed_by
    ) VALUES (
        NEW.user_id, NEW.preference_category, NEW.preference_key,
        'update', NEW.value_type, OLD.preference_value, NEW.preference_value,
        CASE WHEN NEW.source IS NOT NULL THEN NEW.source ELSE 'rfu-core' END
    );
END;

CREATE TRIGGER IF NOT EXISTS trg_user_preferences_audit_delete
AFTER DELETE ON user_preferences
BEGIN
    INSERT INTO preference_audit_log (
        user_id, preference_category, preference_key,
        change_type, value_type, old_value, changed_by
    ) VALUES (
        OLD.user_id, OLD.preference_category, OLD.preference_key,
        'delete', OLD.value_type, OLD.preference_value, OLD.source
    );
END;
```

## Migration Path

1. **JSON Config Backfill**

   - Read `config/rfu_config.json` (via `ConfigManager`) and persist a backup in
     `config/backups/` with timestamp + hash metadata.
   - Map to namespaced categories using `src/config/schema_map.py` to convert
     `general.theme`, `default_directory`, `recent_directories`, and
     `show_hidden` payloads into canonical keys.
   - Upsert via `PreferencesStore.set_category` using
     `source='config-migration'` so audit rows capture provenance and the
     bootstrap remains idempotent.

2. **Explorer Legacy Table (retired)**

   - Beta builds ship without the explorer `user_preferences` table. Alpha
     installations may still contain residual data in `data/file_explorer.db`;
     once the bootstrap completes, no further writes occur and the table is
     safe to drop.

3. **Audit Baseline**

   - Seed `preference_audit_log` with synthetic `insert` events for existing rows
     post-migration (denoted with `change_reason = 'initial-import'`).

4. **Migration Tracking**

   - Record completion in `preference_migrations` using key
     `pref/2025-11-11/config-bootstrap` (or later dated keys as needed).
   - Subsequent incremental migrations follow the same key pattern.

## Post-Migration Contract

- The SQLite preference store becomes the source of truth for every category
  migrated out of JSON (`theming`, `directories`, and future namespaces added
  to the schema map). Config-dependent modules must read through
  `PreferenceManager` (or its adapters) rather than querying the JSON file.
- The JSON `config/rfu_config.json` artifact remains on disk solely as a
  sanitized backup. During the migration we blank the migrated keys so that
  downstream components that still open the file see neutral defaults instead
  of stale user data.
- Legacy modules that still call `ConfigManager` receive defaults after the
  migration. They must not rely on writing those keys back into JSON—those
  writes no longer promote into the preference database and will be discarded
  the next time the bootstrap runs.
  experience by re-running the migration helper against the most recent JSON
  backup once the database reconnects. This keeps JSON firmly in a
  read-only/backup role while still offering a recovery path.

## Portability Contract

- The portability helper in `src/core/preferences/portability.py` exports
  timestamped JSON payloads into `backups/preferences/<user_id>`. Files adopt
  the naming pattern `preferences_<timestamp>.json` with optional `.json.aes`
  suffix when encrypted via `pyAesCrypt`.
- AES operations depend on `pyAesCrypt`. When the library is unavailable the
  helper surfaces descriptive errors and the CLI disables encrypted export and
  import flags.
- Export payloads encode `category`, `key`, `value`, `value_type`,
  `is_encrypted`, `source`, and `schema_version` per row. Values are emitted
  as native JSON types matching the deserialized `PreferencesStore` output;
  the `source` field reflects the row's current provenance.
- Imports hydrate through `PreferencesStore.set`, skipping collisions by
  default. Successful writes retag rows with `source='pref-import'` while
  leaving any supplied `schema_version` intact. Operators can rerun imports
  with `--allow-overwrite` to force updates and `--target-user` to fan out
  seeded defaults to new user IDs.
- Script entry point: `scripts/tools/preferences_portability.py` wires the
  helpers into a Click CLI with `export`/`import` commands and AES passphrase
  prompts. Automation can call the Python functions directly for bespoke
  workflows.

## Ownership & Implementation Notes

- Canonical DDL resides in `src/database/database_manager.py`; legacy callers
  import through this module to avoid duplicate schema definitions.
- Every write path (GUI, CLI, automation) must route through `PreferenceManager` to ensure audit triggers fire; explorer services now rely on `ExplorerPreferences` rather than a schema-local table.
- Envelope encryption work will replace `preference_value` with encrypted payloads while retaining plaintext access via service-layer decryptors.

## Open Questions

- Do we require per-user quota limits for preference rows? (Not yet enforced.)
- Should audit log include request identifiers for correlation with telemetry?
- When explorer stack is deprecated, can `source` be limited to `rfu-*` values only?
