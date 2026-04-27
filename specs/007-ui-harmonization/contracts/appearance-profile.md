# Contract: AppearanceProfile Schema

**Contract ID**: `appearance-profile-v1`
**Feature**: `007-ui-harmonization`
**Owner**: `src/core/preferences/uap/models.py`
**Tested by**: `tests/unit/preferences/test_uap_service.py`

---

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "appearance-profile-v2",
  "title": "AppearanceProfile",
  "type": "object",
  "required": [
    "profile_id",
    "profile_name",
    "is_default",
    "window_width",
    "window_height",
    "window_x",
    "window_y",
    "font_family",
    "font_size",
    "working_directory",
    "created_at",
    "updated_at",
    "profile_schema_version"
  ],
  "properties": {
    "profile_id": {
      "type": "string",
      "oneOf": [
        { "format": "uuid" },
        { "enum": ["factory_default"] }
      ]
    },
    "profile_name":        { "type": "string", "minLength": 1, "maxLength": 64 },
    "is_default":          { "type": "boolean" },
    "window_width":        { "type": "integer", "minimum": 400 },
    "window_height":       { "type": "integer", "minimum": 300 },
    "window_x":            { "type": "integer", "minimum": -1, "description": "-1 = use center/cascade default" },
    "window_y":            { "type": "integer", "minimum": -1, "description": "-1 = use center/cascade default" },
    "font_family":         { "type": "string", "minLength": 1 },
    "font_size":           { "type": "integer", "minimum": 6, "maximum": 32 },
    "working_directory":   { "type": "string" },
    "created_at":          { "type": "string", "format": "date-time" },
    "updated_at":          { "type": "string", "format": "date-time" },
    "profile_schema_version": { "type": "integer", "minimum": 1 },
    "is_user_created":     { "type": "boolean", "default": false }
  },
  "additionalProperties": false
}
```

---

## Invariants

| Rule | Description |
|---|---|
| **INV-001** | Exactly one profile per user MAY have `is_default = true`. |
| **INV-002** | The factory-default profile (`profile_id = "factory_default"`, `profile_name = "Default"`) MUST always exist and MUST NOT be deletable. The deletion guard MUST check `profile_id == "factory_default"`, not `profile_name`. The sentinel `"factory_default"` is the stable, constitutional identity of this profile and SHALL NOT be replaced with a UUID. |
| **INV-003** | `working_directory` MAY be empty string (resolved to home at apply-time); it MUST NOT be `null`. |
| **INV-004** | `updated_at` MUST be updated whenever any field is mutated. |
| **INV-005** | `profile_id` MUST be a valid UUID4 for all user-created profiles. The factory-default profile SHALL use the reserved sentinel `"factory_default"` and is exempt from the UUID4 requirement. Reuse of any UUID4 is PROHIBITED. |
| **INV-006** | `window_x` and `window_y` MUST both be `-1` (use platform default) or both be valid non-negative screen coordinates. Mixed values are invalid. |

> **Governance Annotation — `is_user_created` Field (N2 — Resolved 2026-04-26)**
> Earlier drafts of T018-B seeded `is_user_created=False` on the factory-default profile, but the field did not exist in the JSON schema, dataclass, or entity definition. `"additionalProperties": false` would have caused schema validation to reject any blob containing it.
>
> Per the N2 governance decision (Option C), `is_user_created` is an *optional* field with `"default": false`. It is listed in `"properties"` but NOT in `"required"`. Existing v1 and v2 profiles remain valid; no migration step is needed. The field allows tools to distinguish system-seeded profiles from user-created ones without relying on `profile_id` conventions.

> **Governance Annotation — `profile_id` Sentinel Exception (P3-H04 — Resolved 2026-04-26)**
> Earlier schema enforced `"format": "uuid"` on all `profile_id` values. This directly contradicted INV-002, which mandates `profile_id = "factory_default"` for the non-deletable factory profile. The contradiction would cause every `from_json()` call on the factory-default profile to raise a `ValidationError`, breaking T004 round-trip tests and T018-B seeding.
>
> The schema has been updated to use `"oneOf"` allowing either `"format": "uuid"` or `"enum": ["factory_default"]`. INV-005 has been updated accordingly. No migration is required. No task referencing `"factory_default"` needs modification.
>
> **The sentinel `"factory_default"` is permanent and constitutional. No code SHALL validate it as a UUID4.**

---

## Migration

Schema version tracked inside each AppearanceProfile JSON object as field `profile_schema_version`.

> **Governance Annotation — Placement of `profile_schema_version` (N1 — Resolved 2026-04-26)**
> Earlier drafts placed `profile_schema_version` inconsistently: some artifacts treated it as a top-level `uap.*` key, while others placed it inside each AppearanceProfile JSON blob.
>
> This annotation clarifies that schema versioning is a *per-profile* concern. Each AppearanceProfile MUST contain its own `profile_schema_version` field.
>
> This enables independent migration of profiles, avoids global version coupling, and aligns with T004, T015, T016, and T018-B.
>
> The top-level `uap.profile_schema_version` key is removed. **Resolved: Option A — per-profile field.**

| Version | Change |
|---|---|
| `1` | Initial schema. All base fields present. `profile_schema_version` not yet a persisted field inside the blob. |
| `2` | Added `profile_schema_version` as a required field inside each AppearanceProfile JSON blob. Forward migration from v1: set `profile_schema_version = 2`. |

> **Governance Annotation — AppearanceProfile Migration Correction**
> Earlier drafts of this table stated that `window_x` and `window_y` were added in Version 2. However, these fields already appear in the Version 1 `"required"` array above.
>
> `window_x` and `window_y` have been part of the schema since Version 1; no migration step introduced them. The Version 2 entry referencing their addition has been removed to eliminate the self-contradiction and preserve a coherent, monotonic migration history.
>
> This annotation prevents reintroduction of the incorrect Version 2 entry and ensures that schema evolution remains logically consistent.

Forward migration MUST preserve all known fields and add defaults for new required fields. Backward compatibility is NOT required once a migration has run.

**Migration Table Normalization Rule:** Version entries MUST be strictly chronological. Each version MUST describe only the delta from the previous version. No field may appear as “added” in a version if it already exists in any earlier version's `"required"` array.
