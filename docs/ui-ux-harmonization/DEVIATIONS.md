# UI/UX Harmonization — Deviations Register

**Project:** RFU (Richard's File Utilities)  
**Last updated:** April 2026  
**Scope:** Project-wide deviations from the UI/UX Harmonization Specification (constitutional or spec-level).  
**Storage:** This file is the single authoritative DEVIATIONS.md for the project. Per-tool deviations are added as per-tool sections below.

---

## Project-Wide Deviations

### DEV-001 — UI Event Fields: Partial §16.X.2 Compliance

| Field | Value |
|---|---|
| **Deviation ID** | DEV-001 |
| **Scope** | Project-wide (all tools) |
| **Document section** | Spec §9.3 (Telemetry & Auditability) |
| **Constitution reference** | §16.X.2 |
| **Status** | Accepted — April 2026 |

**Constitutional requirement (§16.X.2):** ALL audit events MUST include `actor_username`, `session_id`, `device_id` (pseudonymized), and `app_instance_id`.

**Deviation:** UI telemetry events (`ui_view_load`, `ui_user_action`, `ui_error_event`, `ui_performance_metric`) are **exempt from the `device_id` and `app_instance_id` fields**. UI events include only: `actor_username`, `session_id`, `timestamp`, `event_type`, and `tool_id`.

**Rationale:** UI telemetry events are high-frequency, ephemeral, and do not require the device-level attribution needed by identity-security events. Collecting `device_id` and `app_instance_id` for every UI action would create unnecessary PII surface without forensic benefit for non-identity events.

**Constraints:**
- This exemption applies ONLY to the four UI-specific event types listed in spec §9.3.
- All identity-related events (login, logout, MFA, session management, account changes) MUST include all four §16.X.2 fields without exception.
- UI events MUST still comply with all other §16.X requirements (field consistency, privacy constraints, no raw PII).
- Retention for UI events is 30 days (not the ≥365-day rule for identity events).

**Review cadence:** Revisit if the project introduces audit-trail requirements for UI events that require device attribution.

---

### DEV-002 — UtilityWindow Menubar-Clone Pattern

| Field | Value |
|---|---|
| **Deviation ID** | DEV-002 |
| **Scope** | Project-wide (all tools using UtilityWindow) |
| **Document section** | Spec §5.1 (Navigation) |
| **Constitution reference** | None — recorded at specification level only (spec §5.1 open item pending resolution) |
| **Status** | Pending resolution |

**Specification requirement (§5.1):** Applications MUST NOT implement their own global navigation. Local navigation MAY be used if it does not visually compete with Hub navigation.

**Deviation:** The current `UtilityWindow` pattern reproduces a Hub-style menubar in each tool window. This has not yet been formally resolved as compliant or non-compliant with §5.1.

**Constraints:**
- This deviation MUST be re-evaluated when a shared menu component is formally specified.
- Tools using this pattern MUST NOT alter the Hub window's own geometry, size, or position.
- All tools using UtilityWindow share this single deviation entry (no per-tool duplicate entries required).

---

## Per-Tool Deviations

### advanced_folders

#### DEV-003 — LoadingIndicator Not Applied

| Field | Value |
|---|---|
| **Deviation ID** | DEV-003 |
| **Scope** | `advanced_folders` tool — `advanced_folders_widget.py`, `configuration_dialog.py`, `config_tabs.py`, `directory_browser.py`, `folder_tree_view.py` |
| **Document section** | Spec §8.1 (Loading / Progress Indicators) |
| **Migration task** | CP-6 |
| **Status** | Accepted — April 2026 |

**Spec requirement (§8.1):** Operations that may take ≥ 300 ms MUST display a `LoadingIndicator`; the indicator MUST be wired to the worker's `started` and `finished` signals.

**Deviation:** `LoadingIndicator` was not added to any `advanced_folders` view. No tool-initiated background thread exists in the Tier 1 `advanced_folders` source set. All in-scope operations (`_save_configuration()`, `_validate_current_path()`, `load_folders()`) run synchronously on the UI thread. A synchronous call blocks the Qt event loop, so the indicator's 300 ms `QTimer` cannot fire; the widget would never become visible even if instantiated.

**Rationale:** The requirement is not applicable because there are no qualifying (≥ 300 ms, async) operations in this tool's current implementation. Adding a `LoadingIndicator` with no thread to wire it to would be dead UI that misleads future maintainers.

**Constraints:**
- If a future change introduces a `QThread`-based operation in `advanced_folders`, `LoadingIndicator` MUST be added for that operation and this deviation MUST be closed.
- The synchronous `compare_directories()` pattern noted in FN-020 for `synchronization_backup` applies equally to `advanced_folders` — any similar directory-scan addition MUST be threaded before adding a `LoadingIndicator`.

---

#### DEV-004 — Cancellation Wiring Not Applied

| Field | Value |
|---|---|
| **Deviation ID** | DEV-004 |
| **Scope** | `advanced_folders` tool — same files as DEV-003 |
| **Document section** | Spec §8.1 (Loading / Progress Indicators — cancellable mode) |
| **Migration task** | CP-7 |
| **Status** | Accepted — April 2026 |

**Spec requirement (§8.1):** For each long-running operation that uses `LoadingIndicator(cancellable=True)`, the `cancelled` signal MUST be connected to the worker's abort slot.

**Deviation:** Cancellation wiring was not implemented for `advanced_folders`. This is a direct consequence of DEV-003 — no `LoadingIndicator` exists in this tool, so there is no `cancelled` signal to wire.

**Rationale:** Not applicable for the same reasons as DEV-003.

**Constraints:**
- This deviation MUST be resolved in the same change that resolves DEV-003. Both share the same root cause and fix path.

---

#### DEV-007 — quick_search_edit Remains QLineEdit (Not Replaced with TextInput)

| Field | Value |
|---|---|
| **Deviation ID** | DEV-007 |
| **Scope** | `advanced_folders` tool — `advanced_folders_widget.py` (toolbar `quick_search_edit`) |
| **Document section** | Spec §5.3 (Form Controls — text inputs MUST use `TextInput` with persistent label) |
| **Migration task** | CP-9 (see FN-022) |
| **Status** | Accepted — April 2026 |

**Spec requirement (§5.3):** Text input controls MUST use the `TextInput` shared component, which supplies a persistent visible label above the field.

**Deviation:** `quick_search_edit` in the `AdvancedFoldersWidget` toolbar remains a plain `QLineEdit` with `setMaximumWidth(200)`, a placeholder text of "Quick search…", and no persistent label. It was excluded from the CP-9 `TextInput` replacement pass.

**Rationale:** The widget serves as a live-filter input in a compact toolbar row, not as a form data-entry field. Replacing it with `TextInput` (which renders a `QLabel` above the field and enforces a minimum 44 px height) would break the toolbar's single-row layout and misrepresent the widget's semantics. The placeholder text "Quick search…" provides sufficient affordance for a toolbar control; a persistent label is not required in this context. The control has `setAccessibleName("Quick search")` applied (A11Y-1c), which satisfies the accessibility requirement independently of the `TextInput` wrapping.

**Constraints:**
- If the toolbar is redesigned to have a multi-row layout, `TextInput` MUST be re-evaluated for this control.
- The `setAccessibleName("Quick search")` call MUST be retained if the widget is ever modified.

---

### synchronization_backup

#### DEV-005 — DestructiveButton + ConfirmationModal Not Applied

| Field | Value |
|---|---|
| **Deviation ID** | DEV-005 |
| **Scope** | `synchronization_backup` tool — `sync.py`, `sync.ui` |
| **Document section** | Spec §5.2 (Buttons & Actions — destructive actions) |
| **Migration task** | CP-3 |
| **Status** | Accepted — April 2026 |

**Spec requirement (§5.2):** Destructive (irreversible) actions MUST use `DestructiveButton` and MUST require explicit confirmation via `ConfirmationModal` before executing.

**Deviation:** Neither `DestructiveButton` nor `ConfirmationModal` was introduced into `sync.py`. No action in the synchronization tool meets the spec §5.2 definition of a destructive action for the following reasons:

- **Mirror / Update / Two-way sync:** Each file overwrite is preceded by `backup_file()` (which copies the target to a backup location before overwriting). The operation is recoverable.
- **Dry Run mode:** No files are modified; preview-only output is emitted.
- **Compare:** Read-only directory scan; no writes.

The primary sync action (`sync_pushButton`) already requires user intent (the user must click Synchronize and confirm the sync-settings dialog) and is not irreversible due to the backup mechanism.

**Rationale:** No qualifying irreversible action exists in the current `synchronization_backup` implementation. Applying `DestructiveButton` to the sync action would misrepresent its semantics to users (the spec reserves the destructive visual treatment for actions that cannot be undone).

**Constraints:**
- If a future mode removes the `backup_file()` step (e.g., a "fast sync without backup" option), that mode's trigger button MUST be implemented as `DestructiveButton` + `ConfirmationModal` and this deviation MUST be closed or updated.
- The existing sync-settings confirmation modal (`Modal(["Sync", "Cancel"])` shown before `_prepare_and_start_sync()`) is NOT a `ConfirmationModal` — this is intentional. The sync action is not destructive; the dialog is informational.

---

#### DEV-006 — LoadingIndicator Not Applied to compare_directories()

| Field | Value |
|---|---|
| **Deviation ID** | DEV-006 |
| **Scope** | `synchronization_backup` tool — `sync.py` → `compare_directories()` method |
| **Document section** | Spec §8.1 (Loading / Progress Indicators) |
| **Migration task** | CP-6 (see FN-020) |
| **Status** | Accepted — April 2026 (pending future refactor) |

**Spec requirement (§8.1):** Operations that may take ≥ 300 ms MUST display a `LoadingIndicator`.

**Deviation:** `compare_directories()` performs `os.listdir()` + file-attribute reads for both directories synchronously on the UI thread. For large or network-mounted directories this can exceed 300 ms, but `LoadingIndicator` cannot be used because the synchronous call blocks the Qt event loop — the indicator's 300 ms `QTimer` cannot fire and the widget would never become visible.

**Rationale:** The root cause is architectural: `compare_directories()` must be refactored to run in a `QThread` (equivalent to `SyncWorker`) before a `LoadingIndicator` can be meaningfully wired to it. This refactor is deferred as a follow-up task (FN-020). The `LoadingIndicator` IS wired to the actual file-sync operation (`_prepare_and_start_sync()` via `SyncWorker`) — only the pre-sync comparison step is excluded.

**Constraints:**
- When `compare_directories()` is refactored to use a `QThread`, `LoadingIndicator(cancellable=True)` MUST be added and this deviation MUST be closed.
- Until then, `compare_directories()` MUST remain a read-only operation (no writes) so that a mid-operation UI freeze does not result in data loss.

---

