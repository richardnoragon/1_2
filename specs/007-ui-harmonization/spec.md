# Feature Specification: UI Harmonization — Unified Look & Feel

**Feature Branch**: `007-ui-harmonization`
**Created**: 2026-03-11
**Status**: Draft
**Scope**: Phase 1 — Unified Appearance Profile, Menu Contract, Dependency Lock, Packaging Documentation. Phases 2–4 (UI Interaction Contract §10, Command Surface §8, Operational Guarantees §13.2, Tool Capability Matrix / CI Enforcement §11–§12) are governed exclusively by their respective constitutional sections and published spec documents. This spec does NOT incorporate or duplicate Phase 2–4 requirements.
**Input**: User description: "Harmonize the look and feel of all RFU applications so they look and feel the same: consistent window size, font, working directory; same menu structure; same package versions; document frameworks, dependencies and packaging styles."

## Cluster Scope

This specification belongs to the repo-authoritative UI/preferences/documentation cluster already represented by the active specs and trackers. It is intentionally limited to the existing UI harmonization and preference portability path in `specs/004-preferences-framework/*` and `specs/007-ui-harmonization/*`, without expanding into unrelated backlog work outside the validated spec set.

## Execution Flow (main)

```text
1. Parse user description — four harmonization areas identified:
   a. Unified Appearance Profile (UAP): window size, font, font size, working directory
   b. Menu structure contract: identical menus, sub-menus, and resulting dialogs
   c. Dependency consistency: all tools use package versions declared in requirements.txt
   d. Framework & packaging audit: identify and document frameworks, dependencies, packaging styles

2. Extract key concepts:
   → Actors: user (from hub OR from individual tool window)
   → Data: UAP settings (window geometry, font family, font size, working directory)
   → Constraints: UAP editable from both hub and each tool; persisted per-user; default = "last used"
   → Scope: all tools that inherit from StandardWindow or launch via tabbed_hub.py

3. Identify gaps:
   → FR-010 [RESOLVED: min_window_width / min_window_height per-tool overrides are allowed; font family, font size, and working directory are strictly global]
   → FR-011 [RESOLVED: last_used_directory IS persisted across sessions (hub restart); new tool windows inherit it immediately on open in the same session]

4. Fill User Scenarios & Testing section.
5. Generate Functional Requirements.
6. Run Review Checklist.
```

---

## ⚡ Quick Guidelines

- ✅ Focus on WHAT users experience and WHY consistency matters.
- ✅ UAP is a first-class preference category (`uap`) governed by Principle VI.
- ✅ Menu contract must be testable: automated contract tests verify menu topology.
- ❌ Do not specify HOW the preference store is implemented (that is Plan/Phase 1 territory).
- 👥 Written for product owner + developers working on individual tools.

---

## User Scenarios & Testing _(mandatory)_

### Primary User Story

Richard opens the RFU hub, launches three different tools in sequence — File Finder, Duplicate Finder, and PDF Merge — and has an identical visual experience each time: the new window opens at the same size, uses the same font and size he last configured, and starts browsing from the directory he last used. When he changes the font inside Duplicate Finder, that change is reflected the next time he opens any tool. He can also pin a "predefined" profile so the window always opens at 1200 × 900 with Segoe UI 11pt starting in `C:\Projects`, regardless of his last-used values.

### Acceptance Scenarios

#### Area 1 — Unified Appearance Profile (UAP)

1. **Given** the user has never customized appearance, **When** they launch any tool from the hub, **Then** the tool window MUST open at the UAP defaults (window size: 1000 × 700, font: Segoe UI 10pt on Windows / system default on other platforms, directory: user home).
2. **Given** the user changes the font to "Courier New 12pt" inside the File Finder window, **When** they close File Finder and open Duplicate Finder, **Then** Duplicate Finder MUST open with "Courier New 12pt" (last-used mode).
3. **Given** the user has created a predefined profile named "Work", **When** they activate "Work" in the hub Appearance settings, **Then** every subsequent tool window MUST open with the profile's fixed geometry, font and directory until the user changes profiles.
4. **Given** the user changes the working directory inside a running tool, **When** they open another tool in the same session, **Then** the second tool MUST inherit that directory (last-used mode).
5. **Given** the user is in predefined mode, **When** they change the window size of a running tool, **Then** the change MUST apply to the current session only and MUST NOT overwrite the predefined profile.

#### Area 2 — Menu Structure Contract

6. **Given** any tool window that inherits the standard window base, **When** the menu bar is rendered, **Then** the top-level menu order MUST be: File → Edit → View → Tools → Help.
7. **Given** the File menu of any tool window, **When** it is opened, **Then** it MUST contain in order: (Open…), (Save / Save As…), separator, Import, Export, separator, Preferences, separator, Exit.
8. **Given** the View menu of any tool window, **When** it is opened, **Then** it MUST contain: Theme (submenu: Light / Dark / System), Font… (launches Font Picker dialog), Working Directory… (launches Directory Picker dialog).
9. **Given** the Preferences dialog opened from any tool, **When** the Appearance tab is shown, **Then** it MUST contain the same UAP controls as the hub Appearance settings panel: profile selector, window size inputs, font picker, and directory picker.
10. **Given** the Help menu of any tool window, **When** About is selected, **Then** the About dialog MUST display: application name, RFU suite version, tool version, Python version, and key framework versions (PyQt5, etc.).

#### Area 3 — Dependency Consistency

11. **Given** the `requirements.txt` at the repository root declares `PyQt5==5.15.11`, **When** any tool imports PyQt5, **Then** the installed version MUST match the declared version within the active virtual environment.
12. **Given** a new tool is added to the suite, **When** it declares its own pip dependencies, **Then** those MUST be listed in the canonical `requirements.txt` with a pinned version and a comment explaining their purpose.

#### Area 4 — Framework & Packaging Documentation

13. **Given** the `docs/architecture/` directory, **When** a developer onboards, **Then** a `frameworks-and-dependencies.md` document MUST exist describing all primary frameworks, their role in the suite, and the rationale for each.
14. **Given** the framework document, **When** any dependency's version or role changes, **Then** the document MUST be updated in the same PR as the code change.

### Edge Cases

- What happens when a saved UAP profile references a directory that no longer exists? The system MUST fall back to the user's home directory, show a non-blocking warning in the status bar, and leave the profile intact for the user to correct.
- What happens when a tool overrides the window geometry programmatically (e.g., a modal dialog with a fixed size)? The UAP MUST apply the font and directory but MUST NOT attempt to resize windows that have declared a fixed size.
- What happens if a tool is launched directly (not through the hub)? The tool MUST still read the UAP from the preference store and apply it; it MUST also offer the UAP edit controls in its own View menu.
- What happens when two tool windows are open and the user changes the font in one? The change takes effect in the originating window immediately and is persisted; already-open windows refresh on the next user interaction or a live-refresh signal if the signal bus is available.
- What happens if `requirements.txt` is missing or malformed? The application MUST log an ERROR and continue using whatever is installed; no silent version mismatch is tolerated.

---

## Requirements _(mandatory)_

### Functional Requirements

#### FR-001 — UAP Default Profile
System MUST provide a factory-default Unified Appearance Profile with: window size 1000 × 700 px, font family "Segoe UI" on Windows / "Helvetica Neue" on macOS / "DejaVu Sans" on Linux, font size 10pt, working directory = user home directory.

#### FR-002 — UAP Persistence Modes
System MUST support two UAP persistence modes that the user can switch between at any time:
- **last-used** (default): stores the values from the most recently closed tool window.
- **predefined**: stores one or more named profiles; the active profile is applied on every window launch.

`last_used` values MUST continue to update silently even while the system is in `predefined` mode. When the user switches from predefined back to last-used mode, the values reflect their true latest activity. No prompt is shown on mode switch.

#### FR-003 — UAP Editable from Hub
The hub's Appearance settings panel MUST expose full UAP editing: profile mode selector, window width/height inputs, font family picker, font size spinner (6–32pt), and working directory field with a Browse button.

#### FR-004 — UAP Editable from Individual Tools
Every tool window MUST provide View → Font… (opens Font Picker dialog) and View → Working Directory… (opens Directory Picker dialog) that update the active UAP and persist the change.

#### FR-005 — UAP Applied on Window Open
When any tool window is instantiated (whether from the hub or standalone), it MUST read the active UAP preference and apply: `resize(width, height)`, `setFont(family, size)`, and set the default browse path to the UAP directory.

#### FR-006 — Predefined Profiles
System MUST allow the user to create, rename, duplicate, and delete named UAP profiles. A profile MUST store: name, window width, window height, window x/y screen position, font family, font size, working directory. Deleting the last profile MUST be prevented; the factory-default profile MUST be permanently available but MUST be resettable, not deletable.

#### FR-007 — Working Directory Scope (QFileDialog Only)
Within a single application session, when the user navigates to a new directory in any tool window, the active UAP's working directory MUST be updated in-memory and offered to subsequent tool windows opened in the same session (last-used mode only). The working directory controls only the **starting path of `QFileDialog`** calls — it MUST NOT invoke `os.chdir()`. No global process working-directory side effects are permitted.

#### FR-008 — Standard Menu Topology
Every tool window MUST render a menu bar whose top-level items appear in this exact order and use these exact labels: `File`, `Edit`, `View`, `Tools`, `Help`. The `File`, `View`, and `Help` menus MUST follow the structures defined in the Menu Contract. The `Edit` and `Tools` menus are **entirely tool-specific** — no items are mandated; both MAY be empty. Contract tests do NOT validate Edit or Tools contents.

#### FR-009 — Tool-Subclassed Preferences Dialog
Every tool window exposes a Preferences dialog reachable from File → Preferences. The base class provides the `Appearance` tab as an embedded `UAPAppearanceWidget`.

Tools with extra preferences MUST subclass `PreferencesDialog` and inject their additional UI using `addTab()`.

Tools with no extra preferences MUST instantiate and show the base `PreferencesDialog` class directly without subclassing.

> **Governance Annotation — PreferencesDialog Subclassing Semantics (A1):**
> Earlier drafts of FR-009 contained a contradiction: one sentence required all tools to subclass `PreferencesDialog`, while another allowed tools with no extra preferences to instantiate the base class directly without subclassing.
> The corrected model is: tools with extra preferences subclass and add tabs via `addTab()`; tools with no extra preferences instantiate the base class directly. No tool MUST subclass `PreferencesDialog` without adding tabs. This preserves a clean, predictable integration model and prevents unnecessary subclassing.

#### FR-010 — Per-Tool UAP Overrides (Resolved)
Per-tool overrides are allowed **only** for `min_window_width` and `min_window_height` (declared in `ToolManifest`). Font family, font size, and working directory are governed by the global UAP and MUST NOT be overridden per tool. `UAPService.apply()` enforces `max(uap_value, tool.min_window_width/height)` for sizing, but applies font and directory without clamping.

#### FR-011 — Cross-Session Directory Propagation (Resolved)
The UAP working directory IS persisted across sessions. In last-used mode the last directory navigated to (in any tool) is written to the UAP store before the application quits, and read back when any tool opens in the next session.

#### FR-012 — Dependency Version Lock
All Python packages used by any RFU tool MUST be declared in `requirements.txt` with pinned exact versions (`==`) and a trailing comment indicating their purpose category (e.g., `# GUI framework`, `# PDF processing`).

#### FR-013 — Platform Condition Evaluation
A CI-runnable script (`scripts/check_dependencies.py`) MUST compare installed package versions against `requirements.txt` and MUST exit non-zero if any mismatch is detected.

The script MUST evaluate platform-conditional requirement lines (e.g., `; sys_platform=="win32"`) according to the following rules:

1. **Default Behavior (No Override Provided):** If the platform condition evaluates to `False` on the current machine, the audit script MUST **skip** the line. A skipped line MUST NOT cause a non-zero exit.

2. **Override Behavior (`--platform=<value>` Provided):** If the user specifies an explicit platform override via `--platform=<value>`, the audit script MUST evaluate all platform-conditional lines against the overridden platform value. Under an override, any platform-conditional line that evaluates to `False` MUST cause a non-zero exit.

3. **Non-Conditional Lines:** Lines without platform conditions MUST always be evaluated and MUST cause a non-zero exit on failure.

**Clarification:** A non-zero exit due to platform mismatch MUST occur **only** when the user explicitly overrides the evaluation context using `--platform=<value>`. When no override is provided, platform-conditional lines that do not match the current machine MUST be skipped and MUST NOT trigger a failure. This rule supersedes earlier wording that implied platform-conditional lines evaluating to `False` on the current machine should cause a non-zero exit.

> **Governance Annotation — Platform Condition Semantics**
> Earlier drafts of FR-013 implied that platform-conditional lines evaluating to `False` on the current machine should cause a non-zero exit. This interpretation would make the audit script unusable on non-Windows platforms (e.g., any line with `sys_platform=="win32"` would always fail on Linux/macOS).
>
> The correct behavior is that platform-conditional lines are **skipped by default** unless the user explicitly overrides the platform via `--platform`. This preserves cross-platform audit usability, ensures deterministic behavior, and prevents accidental enforcement of platform-specific rules on incompatible systems.
>
> This annotation prevents reintroduction of the incorrect behavior and maintains the integrity of the audit system across all supported environments.

#### FR-014 — Framework & Dependency Document
A `docs/architecture/frameworks-and-dependencies.md` document MUST be created (or updated) that lists every framework and key dependency, its pinned version, its role in the suite, the rationale for choosing it, and the minimum supported version.

#### FR-015 — Packaging Style Document
A `docs/architecture/packaging-style.md` document MUST be created that describes: virtual environment conventions (`venv` / `.venv312`), `requirements.txt` format rules, how to add a new dependency (checklist), and the activation scripts provided (`activate_env.bat`, `.ps1`, `.sh`, `.py`).

#### FR-016 — Menu Contract Tests
Automated tests (using `pytest-qt`) MUST verify for every tool class registered in the **`ToolManifest`** that: (a) a menu bar is present, (b) the top-level menus match the required order and labels, (c) File menu contains Preferences and Exit actions, (d) View menu contains Font and Working Directory actions, (e) Help menu contains About action. The `ToolManifest` is the sole enumeration source — tools present in source but not registered MUST NOT be implicitly included via module scanning. Detection of unregistered or orphaned tool classes is a separate governance concern (registration-completeness check) and is out of scope for FR-016.

#### FR-017 — About Dialog Content
The About dialog launched from Help → About in every tool MUST display: tool name, RFU suite version (from `src/__version__.py`), **tool-specific version** (from the tool module's `__version__` attribute; falls back to suite version if not defined), Python version (`sys.version`), PyQt5 version (`PyQt5.QtCore.PYQT_VERSION_STR`), and Qt version (`PyQt5.QtCore.QT_VERSION_STR`). Each tool module SHOULD define a module-level `__version__ = "x.y.z"` string; if absent the About dialog labels it "same as suite".

#### FR-018 — Font Picker Dialog
A shared `FontPickerDialog` (in `src/gui/dialogs/`) MUST be used by every tool for View → Font… It MUST show a font family list filtered to monospace and proportional families, a size spinner, a live preview, and OK / Cancel buttons. On OK, the selected font MUST be applied to the calling window and persisted to the active UAP.

#### FR-019 — Working Directory Picker
A shared `DirectoryPickerDialog` (in `src/gui/dialogs/`) MUST be used by every tool for View → Working Directory… It MUST show the current path, a Browse button (OS native folder dialog), and an option to "Use this directory for all tools (update profile)". On confirm, it MUST update the tool's browse root and optionally persist to the UAP.

#### FR-020 — Theme Propagation
When the user changes the theme (Light / Dark / System) from any tool's View → Theme menu, the change MUST apply to all currently open tool windows within 500ms via the shared `ThemeManager` signal bus.

#### FR-021 — UAP Font Propagation to Open Windows
When the user changes the font family or font size from any tool (View → Font…) or from the hub Appearance tab, the change MUST propagate via the shared UAP signal bus (`uap_font_changed`) to all currently open `StandardWindow` instances and take effect within 500ms. The font MUST apply to **every widget** in each window — menus, toolbars, status bar, list views, tables, labels, buttons, and file-path displays. No fixed-width or content-specific exemptions are permitted. The 500ms SLA applies to a maximum of **10 simultaneously open tool windows**; behaviour beyond this cap is undefined and need not be tested.

#### FR-022 — UAP Geometry Propagation to Open Windows
When the user changes window size or position from any tool or from the hub Appearance tab, a `uap_geometry_changed` signal MUST be emitted. All currently open `StandardWindow` instances MUST resize and reposition within 500ms. Cascade offset logic applies to repositioning (see FR-023). The 500ms SLA applies to a maximum of **10 simultaneously open tool windows** (consistent with FR-021).

#### FR-023 — Window Position: Center and Cascade
The UAP stores screen coordinates `(window_x, window_y)` in addition to dimensions. Sentinel value `(-1, -1)` means "use platform default placement". At window open:
- If `(x, y) == (-1, -1)` **and** no other tool windows are open: center the new window on the primary screen.
- If `(x, y) == (-1, -1)` **and** other tool windows are already open: cascade the new window (+20 px, +20 px from the most recently opened window).
- Otherwise: open at the stored `(x, y)` coordinates.
In last-used mode, `StandardWindow.closeEvent()` MUST persist the window's current position to `last_used_x` / `last_used_y`.

#### FR-024 — File Menu Action Labeling & Applicability

All tools MUST present the complete set of File menu actions defined by the platform's canonical menu topology. For each action, the tool MUST apply the following rules:

**Applicable Actions**  
If the action has a direct, meaningful equivalent within the tool, the tool MUST implement that action and MAY rename it to a tool-relevant label that preserves the action's semantics (e.g., `Open Report…`, `Export Log…`, `Save Results…`).

**Inapplicable Actions**  
If the action has no meaningful equivalent within the tool, the action MUST still appear in its canonical position using its generic platform label and MUST be presented in a disabled (greyed-out) state. Tools MUST NOT rename disabled inapplicable actions.

**Cross-Tool Layout Invariance**  
Tools MUST preserve the canonical ordering, presence, and labeling of File menu actions to maintain cross-tool visual and behavioral consistency. Omission, reordering, or semantic repurposing of File menu actions is prohibited.

> **Clarification (C2 — supersedes earlier wording)**: This requirement supersedes earlier FR-024 language that implied renaming inapplicable actions. Renaming applies only to actions that are both applicable and enabled.

#### FR-025 — Hub Appearance Tab
The hub's tabbed interface MUST include a dedicated **"Appearance"** tab displayed alongside the tool category tabs. This tab provides the full UAP controls: mode toggle (Last Used / Predefined), profile selector, window width/height spinboxes, window position inputs (with a "Use default placement" checkbox that sets sentinel `(-1, -1)`), font family picker, font size spinner, working directory field with Browse button, and profile management actions (New, Rename, Duplicate, Delete, Set Active).

#### FR-026 — Cross-Platform Profile Import Warning
When importing a UAP profile on a platform where one or more stored values are incompatible (directory path not valid on this OS, font family not available in `QFontDatabase`), the import MUST complete but MUST first show a **warning dialog** listing every field that was reset and the reason (e.g., "Font 'Segoe UI' is not available — reset to 'DejaVu Sans'"). The user confirms with OK. Import is not blocked; the reset values are written to the profile after confirmation.

> **Normative Note — Geometry Normalization (G3)**
> When importing an `AppearanceProfile`, undersized `window_width` and `window_height` values MUST be preserved exactly as provided.
> Geometry normalization (clamping to `min_window_width` / `min_window_height`) occurs exclusively at apply-time as defined in T021.
> Import MUST NOT mutate geometry values.

### Key Entities _(data involved)_

#### AppearanceProfile
Represents one named UAP profile. Attributes: `profile_id` (uuid), `profile_name` (string), `is_default` (boolean), `window_width` (int, default 1000), `window_height` (int, default 700), `window_x` (int, default -1 = center/cascade), `window_y` (int, default -1 = center/cascade), `font_family` (string), `font_size` (int, 6–32), `working_directory` (string path), `created_at` (timestamp), `updated_at` (timestamp), `profile_schema_version` (int, ≥1 — per-profile schema version), `is_user_created` (boolean, optional, default `false` — indicates whether the profile was created by the user or seeded by the system). Stored under preference category `uap`.

#### UAPSettings
Runtime settings that determine active profile mode. Attributes: `mode` (enum: `last_used` | `predefined`), `active_profile_id` (uuid, null in last-used mode), `last_used_width` (int), `last_used_height` (int), `last_used_x` (int, -1 = center/cascade), `last_used_y` (int, -1 = center/cascade), `last_used_font_family` (string), `last_used_font_size` (int), `last_used_directory` (string). Updated **continuously regardless of mode** — `last_used_*` fields track the user's true latest activity even while `mode == predefined`; switching back to last-used mode always shows current activity without any data loss or prompt.

#### MenuContract
Defines the required menu topology for validation. Attributes: `top_level` (ordered list of labels), `file_required_action_ids` (ordered list), `view_required_action_ids` (list), `help_required_action_ids` (list). `edit_action_ids` and `tools_action_ids` are intentionally absent — these menus are tool-specific and not validated by contract tests.

#### ToolManifest
Each registered tool MUST declare: `tool_id` (string slug), `display_name` (string), `module_path` (string), `class_name` (string), `category` (string), `min_window_width` (int, optional), `min_window_height` (int, optional), `tool_version` (string, optional — from module `__version__`; falls back to suite version if absent). Used by hub for launch and by UAP application logic.

#### DependencyRecord
Documents one package. Attributes: `package_name`, `pinned_version`, `purpose_category`, `rationale`, `min_acceptable_version`. Stored in `docs/architecture/frameworks-and-dependencies.md` as a markdown table.

---

## Review & Acceptance Checklist

> GATE: Automated checks run during main() execution

### Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness

- [x] FR-010 resolved — per-tool min_window_width/height overrides only; font and directory are global
- [x] FR-011 resolved — working directory IS persisted across sessions in last-used mode
- [x] All requirements are testable and unambiguous
- [x] Success criteria are measurable

---

## Clarifications

### Session 2026-04-25

- Q: Does this spec incorporate Phase 2–4 requirements from harmonization2 (UI Interaction Contract, Command Surface, Operational Guarantees, CI Enforcement)? → A: No. THIS spec covers Phase 1 only (4 original areas). Phases 2–4 are governed by Constitution §8–11 and their existing spec documents. This avoids duplication and preserves governance authority boundaries.
- Q: When a File menu action has no tool-relevant equivalent, should it be renamed, greyed out, or omitted? → A: It MUST appear with its canonical generic label and be disabled (greyed out). Renaming a disabled item is prohibited. Applicable actions MAY be renamed to a tool-relevant label. FR-024 updated to final harmonized text ("File Menu Action Labeling & Applicability").
- Q: What is the maximum number of simultaneously open tool windows the 500ms UAP propagation SLA must cover? → A: 10. The 500ms SLA applies within a cap of 10 simultaneously open tool windows. FR-021 and FR-022 updated accordingly.
- Q: Does `last_used` continue updating while the system is in predefined mode? → A: Yes. `last_used_*` values update silently at all times regardless of mode. Switching back to last-used mode reflects true latest activity; no prompt is shown. FR-002 and UAPSettings entity updated accordingly.
- Q: What is the source of truth for which tool classes FR-016 Menu Contract Tests must cover? → A: The `ToolManifest` registry only. Tools in source but not registered are out of scope for FR-016. Detection of unregistered classes is a separate registration-completeness check. FR-016 updated accordingly.
