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

### finder

#### DEV-008 — search_pushButton Not Replaced (Qt Designer .ui File)

| Field | Value |
|---|---|
| **Deviation ID** | DEV-008 |
| **Scope** | `finder` tool — `src/tools/file_management/finder/file_finder.py` / backing `.ui` file |
| **Document section** | Spec §5.2 (Buttons & Actions) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement:** Primary action buttons MUST use `PrimaryButton`.

**Deviation:** The search trigger button (`search_pushButton`) is defined in a Qt Designer `.ui` file and loaded via `uic.loadUi()`. Replacing it with a `PrimaryButton` instance requires either (a) editing the `.ui` XML to use a promoted widget, or (b) post-loading programmatic replacement. Both approaches carry risk of breaking existing signal connections and layout geometry. Button remains as `QPushButton` from `.ui` load.

**Constraints:**
- If the `.ui` file is redesigned, `search_pushButton` MUST be promoted to `PrimaryButton` at that time.

---

### organizer

#### DEV-009 — QLineEdit Fields in Dialog Layouts Not Replaced with TextInput

| Field | Value |
|---|---|
| **Deviation ID** | DEV-009 |
| **Scope** | `organizer` tool — `src/tools/file_management/organizer/organize.py` (dialog QLineEdit fields) |
| **Document section** | Spec §5.3 (Form Controls) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§5.3):** Text input controls MUST use the `TextInput` shared component with a persistent visible label.

**Deviation:** QLineEdit fields in the organizer's rule-editor dialogs are embedded in `QFormLayout` rows alongside `QLabel` pairs. Replacing with `TextInput` (which renders its own internal label) would duplicate the label and require restructuring the form layout. Fields remain as `QLineEdit`.

**Constraints:**
- If the dialog layout is redesigned, TextInput replacement MUST be evaluated at that time.

---

### advanced_catalog

#### DEV-010 — directory_edit QLineEdit Not Replaced with TextInput

| Field | Value |
|---|---|
| **Deviation ID** | DEV-010 |
| **Scope** | `advanced_catalog` tool — `src/tools/file_management/advanced_catalog/advanced_catalog_window.py` (`directory_edit` in QGridLayout) |
| **Document section** | Spec §5.3 (Form Controls) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§5.3):** Text input controls MUST use the `TextInput` shared component.

**Deviation:** `directory_edit` is paired with a `QLabel` in a `QGridLayout` row. Replacing it with `TextInput` would duplicate the label and require layout restructuring. Field remains as `QLineEdit`.

**Constraints:**
- If the layout row is redesigned, TextInput replacement MUST be evaluated at that time.

---

### system_diagnostics

#### DEV-011 — LoadingIndicator Not Applied (No QThread Operations)

| Field | Value |
|---|---|
| **Deviation ID** | DEV-011 |
| **Scope** | `system_diagnostics` tool — `src/tools/system/diagnostics_monitoring/system_diagnostics_gui.py` |
| **Document section** | Spec §8.1 (Loading / Progress Indicators) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§8.1):** Operations that may take ≥ 300 ms MUST display a `LoadingIndicator` wired to the worker's `started` and `finished` signals.

**Deviation:** All diagnostic action methods (`run_system_check`, `check_disk_space`, `run_memory_test`, `run_performance_benchmark`) are placeholder stubs that execute synchronously. No `QThread` worker exists to wire `LoadingIndicator` signals to.

**Constraints:**
- When any diagnostic method is implemented with a `QThread` worker, `LoadingIndicator` MUST be added for that operation and this deviation MUST be updated or closed.

---

### software_maintenance

#### DEV-012 — LoadingIndicator Not Applied (Integrated progress_bar Present)

| Field | Value |
|---|---|
| **Deviation ID** | DEV-012 |
| **Scope** | `software_maintenance` tool — `src/tools/system/software_maintenance/gui/maintenance_hub.py` |
| **Document section** | Spec §8.1 (Loading / Progress Indicators) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§8.1):** Operations that may take ≥ 300 ms MUST display a `LoadingIndicator`.

**Deviation:** The maintenance hub already uses an integrated `QProgressBar` (`self.progress_bar`) and `QLabel` (`self.status_label`) for progress feedback, wired to its own worker signals. Adding a `LoadingIndicator` overlay would duplicate the progress display. The existing progress_bar mechanism satisfies the intent of spec §8.1 for this tool.

**Constraints:**
- If the integrated progress_bar is removed in a future refactor, `LoadingIndicator` MUST be added as its replacement.

---

### metadata

#### DEV-013 — EXIF/GPS QLineEdit Fields Not Replaced with TextInput

| Field | Value |
|---|---|
| **Deviation ID** | DEV-013 |
| **Scope** | `metadata` tool — `src/tools/metadata/image_metadata/gui.py` (`exif_fields` and `gps_fields` QLineEdit dicts in QGridLayout) |
| **Document section** | Spec §5.3 (Form Controls) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§5.3):** Text input controls MUST use the `TextInput` shared component.

**Deviation:** EXIF metadata fields (title, author, subject, keywords, comments, copyright) and GPS coordinate fields are QLineEdit widgets stored in `self.exif_fields` and `self.gps_fields` dicts, each paired with a `QLabel` in a `QGridLayout`. Replacing with `TextInput` would duplicate labels and require restructuring the two-column grid layout. Fields remain as `QLineEdit`.

**Constraints:**
- If the metadata form layout is redesigned, TextInput replacement MUST be evaluated at that time.

---

### preferences

#### DEV-014 — QLineEdit Form Fields Not Replaced with TextInput

| Field | Value |
|---|---|
| **Deviation ID** | DEV-014 |
| **Scope** | `preferences` tool — `src/tools/preferences/portability_launcher.py` (7 QLineEdit fields in QFormLayout) |
| **Document section** | Spec §5.3 (Form Controls) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§5.3):** Text input controls MUST use the `TextInput` shared component.

**Deviation:** Seven QLineEdit fields (`export_user_edit`, `export_dest_edit`, `export_categories_edit`, `export_passphrase_edit`, `import_source_edit`, `import_target_user_edit`, `import_passphrase_edit`) are embedded as the right-hand widget in `QFormLayout` rows with paired `QLabel` entries. Replacing with `TextInput` would duplicate labels and require replacing `QFormLayout` with a `QVBoxLayout` of `TextInput` instances. Fields remain as `QLineEdit`.

**Constraints:**
- If the export/import form layout is redesigned, TextInput replacement MUST be evaluated at that time.

---

### secure_delete

#### DEV-015 — LoadingIndicator Not Applied (threading.Thread, Not QThread)

| Field | Value |
|---|---|
| **Deviation ID** | DEV-015 |
| **Scope** | `secure_delete` tool — `src/tools/security/secure_delete/secure_delete.py` |
| **Document section** | Spec §8.1 (Loading / Progress Indicators) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§8.1):** Operations that may take ≥ 300 ms MUST display a `LoadingIndicator` wired to the worker's `started` and `finished` signals.

**Deviation:** The secure delete background operation uses `threading.Thread` (Python stdlib) rather than `QThread`. The `LoadingIndicator` `start()` and `stop()` methods require wiring to Qt signals; `threading.Thread` has no Qt signal interface. Wiring would require either migrating to `QThread` or bridging via `QMetaObject.invokeMethod`. Both approaches are out of scope for the CP pass.

**Constraints:**
- When the worker is migrated to `QThread`, `LoadingIndicator` MUST be added and this deviation MUST be closed.

---

### security_scanner

#### DEV-016 — LoadingIndicator Not Applied (QThread Worker Structurally Broken)

| Field | Value |
|---|---|
| **Deviation ID** | DEV-016 |
| **Scope** | `security_scanner` tool — `src/tools/security/security_scanner/security_scanner.py` (`SecurityScanWorker`) |
| **Document section** | Spec §8.1 (Loading / Progress Indicators) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§8.1):** Operations that may take ≥ 300 ms MUST display a `LoadingIndicator` wired to the worker's `started` and `finished` signals.

**Deviation:** `SecurityScanWorker` is structurally broken — it does not inherit from `QThread` or `QObject`, has no `run()` method, and does not emit `started`/`finished` signals. Wiring `LoadingIndicator` to this worker is not possible without first rebuilding the worker as a proper `QThread` subclass.

**Constraints:**
- When `SecurityScanWorker` is rebuilt as a `QThread` subclass, `LoadingIndicator` MUST be added and this deviation MUST be closed.

---

### encryption

#### DEV-017 — password_edit QLineEdit Not Replaced with TextInput

| Field | Value |
|---|---|
| **Deviation ID** | DEV-017 |
| **Scope** | `encryption` tool — `src/tools/security/encryption/en_and_decrypt.py` (`password_edit`) |
| **Document section** | Spec §5.3 (Form Controls) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§5.3):** Text input controls MUST use the `TextInput` shared component.

**Deviation:** `password_edit` uses `QLineEdit.Password` echo mode for secure password entry. The `TextInput` shared component does not support echo mode configuration. Replacing with `TextInput` would expose the password as plain text. Field remains as `QLineEdit`.

**Constraints:**
- If `TextInput` is extended to support echo mode (e.g., a `password=True` parameter), `password_edit` MUST be migrated and this deviation MUST be closed.

---

### pdf_tools

#### DEV-018 — Dynamic-Color Category and Program Card Buttons Not Replaced

| Field | Value |
|---|---|
| **Deviation ID** | DEV-018 |
| **Scope** | `pdf_tools` tool — `src/tools/pdf_tools/widgets/enhanced_pdf_tools_widget.py` (`create_category_button`, `create_program_button`) |
| **Document section** | Spec §5.2 (Buttons & Actions) |
| **Migration task** | CP (CP pass rows 4–25) |
| **Status** | Accepted — 2026 |

**Spec requirement (§5.2):** Action buttons MUST use `PrimaryButton` or `SecondaryButton`.

**Deviation:** The category card buttons in `create_category_button()` and program card buttons in `create_program_button()` are `QPushButton` instances dynamically styled with category-specific colors (green, blue, red, orange, purple, blue-grey). These colors encode category identity; replacing with `PrimaryButton`/`SecondaryButton` (which use a single theme-driven accent color) would remove the visual category distinction and degrade navigability. The card-button pattern is a display/navigation widget, not a primary action trigger.

**Constraints:**
- If the card layout is redesigned to separate navigation from action semantics, the action trigger within each card MUST use `PrimaryButton` or `SecondaryButton` and this deviation MUST be updated.

#### DEV-019 — Bookmark form compatibility shims retain QLineEdit/QPushButton references

| Field | Value |
|---|---|
| **Deviation ID** | DEV-019 |
| **Scope** | `src/tools/network/bookmarks/bookmark_manager.py` |
| **Document section** | Spec §5.2 (Buttons & Actions) and Spec §5.3 (Form Controls) |
| **Migration task** | CP final compliance pass |
| **Status** | Accepted — 2026 |

**Spec requirement (§5.2 / §5.3):** Buttons and text inputs SHOULD use the harmonized shared components (`PrimaryButton`, `SecondaryButton`, `TextInput`).

**Deviation:** `BookmarkDialog.init_ui()` and `BookmarkManagerGUI.create_toolbar()` intentionally keep compatibility fallbacks such as `TextInput(...) if TextInput else QLineEdit()` and `PrimaryButton(...) if PrimaryButton else QPushButton(...)`. In the project runtime these branches are not active because the shared component library is available, but the AST scan still sees the fallback constructors and trips the bare-widget rule.

**Rationale:** These are non-executing compatibility shims used to preserve standalone execution compatibility when the shared component module is unavailable. They do not represent live UI code in the current project configuration and are therefore not a functional repo violation.

**Constraints:**
- The active runtime path MUST continue to prefer `TextInput` and shared buttons.
- If the compatibility fallback is removed entirely, this deviation MUST be closed and the direct constructors deleted.

#### DEV-020 — PDF functional integration uses generated dialogs with legacy raw Qt widgets

| Field | Value |
|---|---|
| **Deviation ID** | DEV-020 |
| **Scope** | `src/tools/pdf_tools/pdf_functional_integration.py` |
| **Document section** | Spec §5.2 (Buttons & Actions), Spec §5.3 (Form Controls), Spec §8.1 (Progress Indicators) |
| **Migration task** | CP final compliance pass |
| **Status** | Accepted — 2026 |

**Spec requirement:** Generated dialog controls SHOULD use shared components where they are structurally fixed and persistent.

**Deviation:** This file builds many temporary parameter dialogs at runtime using raw `QDialog`, `QLineEdit`, and `QPushButton` widgets. These dialogs are created dynamically in helper methods, vary by operation type, and are not backed by a stable shared-component abstraction for each operation. The file already uses a centralized `PDFProgressDialog` and the project continues to favor functionality-first integration over a large-scale dialog refactor on this legacy adapter layer.

**Rationale:** The runtime-generated parameter dialogs are not static forms and are intentionally local to the integration layer. Replacing every ephemeral widget with a shared component would require a substantial UI abstraction layer beyond the scope of the current issue. The actual active tool surfaces have already been migrated to the project-standard components.

**Constraints:**
- The dynamic dialogs in this file MUST remain functionally equivalent to the current user flow.
- If a dedicated shared dialog/component layer is introduced for these PDF parameter forms, this deviation MUST be reviewed and closed.

