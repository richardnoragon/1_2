# Research: UI Harmonization — Phase 0 Findings

**Feature**: `007-ui-harmonization`
**Date**: 2026-03-11
**Status**: Complete — no NEEDS CLARIFICATION blockers remain after field survey

---

## 1. Clarification Resolutions

### FR-010 — Per-Tool UAP Overrides
**Decision**: Per-tool overrides are ALLOWED for `min_window_width` / `min_window_height` (already in `ToolManifest`) but NOT for font or working directory. The global UAP governs font and directory system-wide. This prevents the proliferation of per-tool preference namespaces while still honouring tools that have a physical minimum size.

### FR-011 — Cross-Session Directory Propagation Scope
**Decision**: The UAP working directory IS persisted across sessions. In last-used mode the last directory the user navigated to (in any tool) is written to the UAP store before the application quits, and read back when any tool opens next session. This matches the "default = last used" expectation throughout.

---

## 2. Existing Infrastructure Audit

### 2.1 GUI Base Classes
| Component | File | Status |
|---|---|---|
| `StandardWindow` | `src/gui/standard_window.py` | ✅ Exists — all tools should subclass this |
| `SafeStandardWindow` | `src/gui/safe_standard_window.py` | ✅ Exists — hardened version for tools handling sensitive files |
| `ThemeManager` | `src/gui/themes.py` | ✅ Exists — `Colors`, `Fonts`, `Spacing`, `Dimensions` defined |
| `MenuManager` | `src/gui/menu_manager.py` | ✅ Exists — `create_standard_menubar()` covers File/Edit/View/Tools/Help |
| `SettingsDialog` | `src/gui/settings_dialog.py` | ✅ Exists — Appearance tab partially implemented |
| `ComponentGuardian` | `src/gui/component_guardian.py` | ✅ Exists |

**Gap**: `MenuManager._create_view_menu()` does not yet expose Font… or Working Directory… actions. These must be added.

**Gap**: No shared `FontPickerDialog` exists in `src/gui/dialogs/`. Must be created.

**Gap**: No shared `DirectoryPickerDialog` exists in `src/gui/dialogs/`. Must be created (distinct from `QFileDialog` wrapper — needs "apply to all tools" checkbox).

### 2.2 Preference System
| Component | File | Status |
|---|---|---|
| `PreferenceManager` | `src/core/preferences/manager.py` | ✅ Exists — generic category/key/value store |
| `PreferencesStore` | `src/core/preferences/store.py` | ✅ Exists — SQLite-backed with JSON fallback |
| `preference_profile.py` | `src/core/preferences/models/preference_profile.py` | ✅ Exists — model class |
| `portability.py` | `src/core/preferences/portability.py` | ✅ Exists — export/import |
| UAP category (`uap`) | — | ❌ Not defined — must create preference namespace |

**Decision**: UAP preferences live under category `uap` in `PreferenceManager`. Keys: `mode`, `active_profile_id`, `last_used_width`, `last_used_height`, `last_used_font_family`, `last_used_font_size`, `last_used_directory`. Profiles stored as JSON blobs under keys `profile:<uuid>`.

### 2.3 Menu Structure — Current State
`MenuManager.create_standard_menubar()` creates: File, Edit, View, Tools, Help.

- File menu: matches spec (Open, Save, Save As, Import, Export, Preferences, Exit) ✅
- View menu: Theme submenu exists ✅; Font and Working Directory actions MISSING ❌
- Help menu: About action exists ✅; About dialog content is minimal (needs suite + tool versions) ❌

### 2.4 Tool Inventory
Tools confirmed to subclass `StandardWindow` (from `tool_window_interface_standards.md` + `src/gui/standard_window.py` audit):

**File Management** (`src/tools/file_management/`)
- `finder/` — File Finder
- `advanced_catalog/` — Advanced Catalog
- `organizer/` — File Organizer
- `synchronization_backup/` — Sync & Backup
- `advanced_folders/` — Advanced Folders

**File Operations** (`src/tools/file_operations/`)
- `catalog.py` — Catalog
- `file_finder.py` — File Finder (legacy)
- `organize.py` — Organizer
- `compression/` — Compression
- `enhanced_editor/` — Enhanced Editor
- `rename/` — Rename Tool
- `file_splitter/` — File Splitter
- `secure_delete/` — Secure Delete

**Analysis** (`src/tools/analysis/`)
- `duplicate_finder/` — Duplicate Finder
- `size_analyzer/` — Size Analyzer
- `checksum/` — Checksum
- `empty_folders/` — Empty Folder Finder

**PDF Tools** (`src/tools/pdf_tools/`) — engine-based, multiple sub-tools

**Network** (`src/tools/network/`)
- `connectivity/` — Network Connectivity
- `scanner/` — Network Scanner
- `transfer/` — File Transfer
- `bookmarks/` — Bookmarks

**Security** (`src/tools/security/`)
- `encryption/` — Encrypt/Decrypt
- `password_generator/` — Password Generator
- `security_scanner/` — Security Scanner

**System** (`src/tools/system/`)
- `system_diagnostics/`, `system_cleanup/`, `diagnostics_monitoring/`, `process_monitor/`, `permissions/`, `software_maintenance/`, `enhanced_clipboard/`

**Privacy** (`src/tools/privacy/`)
- `anonymizer/`, `cleaner/`, `privacy_cleaner/`, `privacy_tools/`

**Total estimated tool classes**: ~30–40 tool windows.

### 2.5 Dependency & Packaging Audit
Current state of `requirements.txt` (root):
- All packages use `==` pinning ✅
- Comments use `# PurposeCategory (inline)` format ✅
- Some comments run together without spaces (minor style issue)
- No `docs/architecture/frameworks-and-dependencies.md` exists ❌
- No `docs/architecture/packaging-style.md` exists ❌
- No `scripts/check_dependencies.py` audit script exists ❌
- `speckit==1.0.1` and `control==0.10.2` appear unrelated to the file utilities domain — require clarification but are non-breaking

**Virtual Environment**:
- `venv/` (Python 3.x, legacy) and `.venv312/` (Python 3.12, active) both present
- Activation scripts: `activate_env.bat`, `activate_env.ps1`, `activate_env.sh`, `activate_env.py` ✅
- No canonical `packaging-style.md` documents which venv to use ❌

### 2.6 Docs Architecture Directory
`docs/architecture/` exists but contains only integration/fix docs. No dependency inventory or packaging standards are documented there.

---

## 3. Clarification Resolutions — speckit.clarify session (2026-03-11)

All ambiguities raised in the Phase 0 clarification pass are now resolved. Decisions recorded here supersede any tentative statements elsewhere in this document.

### Q1 — Font/Profile Live Propagation to Already-Open Windows
**Decision (A)**: When the user changes font, size, or active UAP profile from any tool or from the hub, all other **currently open** tool windows MUST refresh immediately via the shared UAP signal bus — within 500ms. This is the same propagation contract already in place for theme changes.

### Q2 — Window Size Live Propagation
**Decision (A)**: A UAP size change made from the hub or any tool applies live to all open `StandardWindow` instances within 500ms. Open windows MUST resize and reposition (cascade logic applies; see Q3).

### Q3 — Window Position Included in UAP
**Decision (A — all three options apply)**: The UAP includes screen coordinates `(x, y)` in addition to `(width, height)`.
- **First open / no saved position**: window is centered on the primary screen.
- **Multiple windows open simultaneously**: each subsequent window cascades (+20 px, +20 px from the most recently opened window).
- **Subsequent opens (last-used mode)**: the last closed position of any tool window is stored and restored on next open.
Sentinel value `(-1, -1)` means "use center/cascade default". `UAPService.apply(window)` resolves this at runtime.

### Q4 — Font Applies to All UI Elements (No Fixed-Width Exemptions)
**Decision**: The UAP font (family + size) applies to **every widget** in the tool window — menus, toolbars, status bar, list views, tables, labels, buttons, and file-path displays. Fixed-width / monospace content areas are **not** exempt. If a user selects a proportional font, file paths and log output will render in that font.

### Q5 — Edit and Tools Menus Are Entirely Tool-Specific
**Decision (B)**: The `Edit` and `Tools` menus have **no required items**. Each tool defines its own contents. Tools with no editable content MAY leave these menus empty or may omit items entirely. The contract tests do NOT validate Edit or Tools menu contents.

### Q6 — File Menu: Non-Applicable Actions Are Renamed
**Decision (C)**: When a standard File menu action (Open, Save, Import, Export, etc.) has no direct meaning for a tool, it MUST be **renamed** to a tool-relevant label (e.g., `Open Report…`, `Export Log…`, `Save Results…`). Actions MUST NOT be hidden or greyed out. This preserves the uniform visual layout across all tools while making every item meaningful.

### Q7 — Preferences Dialog: Each Tool Subclasses PreferencesDialog
**Decision (B)**: The `PreferencesDialog` is a base class. Each tool opens its own Preferences window by subclassing `PreferencesDialog`. The base class provides the `Appearance` tab as an embedded widget (`UAPAppearanceWidget`). Tool-specific tabs are added by each subclass via `addTab()`. Tools with no extra preferences simply instantiate and show the base class directly.

### Q8 — Working Directory: QFileDialog Only (No os.chdir)
**Decision (A)**: The UAP working directory controls only the **starting path of `QFileDialog`** open/save dialogs. No `os.chdir()` call is made. This avoids global process side effects that would surprise other tools sharing the same process.

### Q9 — Dependency Audit Conditionals: Fail Unless --platform
**Decision (C)**: When `scripts/check_dependencies.py` encounters a platform-conditional line (e.g., `; sys_platform=="win32"`) and the condition evaluates to `False` on the current machine, the script MUST **exit with code 1** (fail) unless the `--platform <target>` flag is explicitly passed. Passing `--platform win32` on a Linux machine causes the audit to evaluate all conditions as if running on Windows. This ensures cross-platform correctness is verifiable in CI.

### Q10 — Tool Version: Independent Per-Tool __version__
**Decision (B)**: Each tool module SHOULD define a module-level `__version__ = "x.y.z"` string. If not defined, the About dialog falls back to the RFU suite version for that tool. The About dialog displays both the suite version (from `src/__version__.py`) and the tool-specific version (from the tool module's `__version__`, or "same as suite" if absent).

### Q11 — Hub Appearance Settings Location: Dedicated Tab
**Decision (A)**: The hub's tabbed interface MUST include a dedicated **"Appearance" tab** alongside the tool category tabs (File Management, Analysis, etc.). This tab provides the full UAP controls: profile selector, mode toggle, window size/position inputs, font picker, working directory field, and profile management (create/rename/duplicate/delete).

### Q12 — Cross-Platform Profile Import: Warning Dialog
**Decision (B)**: When importing a UAP profile on a different platform where saved values are incompatible (directory path format, unavailable font family), the import MUST complete but MUST first display a **warning dialog** listing every field that was reset and the reason (e.g., "Font 'Segoe UI' is not available on this platform — reset to 'DejaVu Sans'"). The user confirms with OK before the profile is applied. Import is NOT blocked (contrast with option C).

## 3. Technology Decisions

| Area | Decision | Rationale |
|---|---|---|
| UAP persistence | `PreferenceManager` category `uap` | Consistent with Principle VI; leverages existing SQLite + JSON fallback |
| UAP profile model | New `AppearanceProfile` dataclass; JSON-serialized as preference value | Avoids new DB table; profiles are user data, not application schema |
| Font Picker | New `src/gui/dialogs/font_picker_dialog.py` using `QFontDialog` internally + live preview | Native font picker via Qt; wraps it with UAP persistence |
| Directory Picker | New `src/gui/dialogs/directory_picker_dialog.py` wrapping `QFileDialog.getExistingDirectory` | Adds "apply to all tools" checkbox beyond native picker |
| Menu contract tests | `tests/contract/gui/test_menu_contract.py` using `pytest-qt` | Ensures topology; complements `test_tool_interface.py` |
| Dependency audit script | `scripts/check_dependencies.py` parsing `requirements.txt` and `pip list` | Zero-dependency; runnable in CI without extra packages |
| Docs format | Markdown tables in `docs/architecture/` | Consistent with existing docs style |

---

## 4. Resolved Unknowns (NEEDS CLARIFICATION → closed)

| ID | Question | Resolution |
|---|---|---|
| FR-010 | Per-tool UAP overrides? | Allowed for window size only; font and directory are global |
| FR-011 | Cross-session directory propagation? | Yes — last-used directory persists across sessions |

---

## 5. Out of Scope for this Feature

- MFA hooks, authentication, and session management (covered by 006-baseline-login-password)
- New tool development (harmonization applies to existing tools)
- PDF engine architecture changes
- CI/CD pipeline configuration beyond the audit script
