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
  "$id": "appearance-profile-v1",
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
    "updated_at"
  ],
  "properties": {
    "profile_id":          { "type": "string", "format": "uuid" },
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
    "updated_at":          { "type": "string", "format": "date-time" }
  },
  "additionalProperties": false
}
```

---

## Invariants

| Rule | Description |
|---|---|
| **INV-001** | Exactly one profile per user MAY have `is_default = true`. |
| **INV-002** | The factory-default profile (`profile_name = "Default"`) MUST always exist and MUST NOT be deletable. |
| **INV-003** | `working_directory` MAY be empty string (resolved to home at apply-time); it MUST NOT be `null`. |
| **INV-004** | `updated_at` MUST be updated whenever any field is mutated. |
| **INV-005** | `profile_id` MUST be a valid UUID4; reuse of a deleted profile's ID is PROHIBITED. |
| **INV-006** | `window_x` and `window_y` MUST both be `-1` (use platform default) or both be valid non-negative screen coordinates. Mixed values are invalid. |

---

## Migration

Schema version tracked in key `uap.profile_schema_version` (integer).

| Version | Change |
|---|---|
| `1` | Initial schema (this document) |
| `2` | Added `window_x` and `window_y` position fields (default `-1`) |

Forward migration MUST preserve all known fields and add defaults for new required fields. Backward compatibility is NOT required once a migration has run.
