# UI/UX Harmonization — Technical Implementation Plan
**Version 1.0 — April 2026**  
**Authority:** UI/UX Harmonization Specification v0.7 + Migration Guide v0.6  
**Maintainer:** Richard Noragon  

---

## 1. Document Scope

This plan translates the UI/UX Harmonization Specification (v0.7) and Migration Guide (v0.6) into concrete, sequenced engineering tasks. It identifies every file that must be created or modified, the exact interface each new artifact must satisfy, and the order in which work must proceed to unblock per-tool migration.

---

## 2. Current Codebase State

### Shared Infrastructure (src/gui/)

| Artifact | Current State | Required State |
|---|---|---|
| `src/gui/themes.py` — color store | `LightColors` / `DarkColors` class attributes | `TOKENS` nested dict (spec §4.1.2) |
| `src/gui/themes.py` — typography | `Fonts` class (sizes 16/14/12/10) | `Typography` class with factory methods (sizes 18/14/12/10/8) |
| `src/gui/themes.py` — nav tokens | Not defined | `hub_nav_background/foreground/accent/border` keys in TOKENS |
| `src/gui/component_guardian.py` | Exists at `src/gui/` | Must be accessible at `src/core/guardian/` (spec §7.2) |
| `src/gui/components/` | Does not exist | Hub shared component library (spec §7.1) |
| `src/rfu/ui_strings.py` | Does not exist | Namespace-class string store (spec §9.2) |
| Hub global error screen | Does not exist | `src/gui/components/hub_error_screen.py` (spec §8.2) |

### Per-Tool Dry-Run Status

| Tool | `dry_run` in backend | UI checkbox/control visible before action |
|---|---|---|
| `synchronization_backup` | ✓ (`dry_run` option key) | ✓ (`dry_run_checkbox`) |
| All other tools | Not audited | Not audited |

### Accessibility Coverage

`setAccessibleName` / `setAccessibleDescription` confirmed in:
- `src/gui/widgets/empty_state_widget.py` ✓  
- `src/tools/file_management/advanced_folders/gui/folder_tree_view.py` ✓  
- `src/tools/file_management/advanced_folders/gui/directory_browser.py` ✓  
- All other tools: **not yet audited**

### Worker Thread Usage

`QThread` / `moveToThread` confirmed in:
- `src/tools/system/system_cleanup/system_cleanup_gui.py` ✓  
- All other tools: **not yet audited**

---

## 3. Definitions

**Shared infrastructure** — artifacts created once, reused by all tools.  
**Per-tool work** — migration steps applied independently to each of the ~20 tool GUIs.  
**Blocker** — a shared infrastructure item that must exist before any per-tool migration of a given type begins.

---

## 4. Phase 1 — Shared Infrastructure Bootstrap

All items below are Phase 1.3 deliverables per the Migration Guide. They MUST be complete before Phase 3 per-tool work begins on the corresponding dependency type.

---

### 4.1 TOKENS Dict in themes.py

**File:** `src/gui/themes.py`  
**Blocker for:** theming migration (Phase 3.2 for all tools)

**Required change:** Add a `TOKENS` dict below the existing `LightColors` / `DarkColors` class definitions. Values are derived directly from those classes.

```python
TOKENS: dict = {
    "light": {
        # Semantic colors (spec §4.1.1 — MUST NOT be repurposed)
        "semantic_success":  LightColors.SUCCESS,    # "#27AE60"
        "semantic_warning":  LightColors.WARNING,    # "#F39C12"
        "semantic_error":    LightColors.ERROR,      # "#E74C3C"
        "semantic_info":     LightColors.INFO,       # "#3498DB"
        # Hub navigation (spec §4.1.2 — MUST NOT be overridden by tools)
        "hub_nav_background": LightColors.PRIMARY,
        "hub_nav_foreground": LightColors.TEXT_PRIMARY,
        "hub_nav_accent":     LightColors.ACCENT,
        "hub_nav_border":     LightColors.SECONDARY,
        # General palette (mirrors LightColors for token-based access)
        "background":         LightColors.BACKGROUND,
        "window_background":  LightColors.WINDOW_BACKGROUND,
        "text_primary":       LightColors.TEXT_PRIMARY,
        "text_secondary":     LightColors.TEXT_SECONDARY,
        "button_primary":     LightColors.BUTTON_PRIMARY,
    },
    "dark": {
        "semantic_success":  DarkColors.SUCCESS,
        "semantic_warning":  DarkColors.WARNING,
        "semantic_error":    DarkColors.ERROR,
        "semantic_info":     DarkColors.INFO,
        "hub_nav_background": DarkColors.PRIMARY,
        "hub_nav_foreground": DarkColors.TEXT_PRIMARY,
        "hub_nav_accent":     DarkColors.ACCENT,
        "hub_nav_border":     DarkColors.SECONDARY,
        "background":         DarkColors.BACKGROUND,
        "window_background":  DarkColors.WINDOW_BACKGROUND,
        "text_primary":       DarkColors.TEXT_PRIMARY,
        "text_secondary":     DarkColors.TEXT_SECONDARY,
        "button_primary":     DarkColors.BUTTON_PRIMARY,
    },
}
```

`TOKENS` is read at application startup:
```python
_active_tokens: dict = TOKENS["light"]

def apply_theme(variant: str) -> None:
    """Switch active token set. variant must be 'light' or 'dark'."""
    global _active_tokens
    _active_tokens = TOKENS[variant]
    Colors.set_theme(variant)  # preserve backward compat with Colors class

def token(key: str) -> str:
    """Return the active token value for key. Raises KeyError if unknown."""
    return _active_tokens[key]
```

**Backward compatibility:** `LightColors`, `DarkColors`, and `Colors` classes remain in place unchanged. `TOKENS` is the new canonical source; tools migrated in Phase 3 switch to `token()` calls.

**Constraint:** Tools MUST NOT assign values to `hub_nav_*` keys in their own code.

---

### 4.2 Typography Class in themes.py

**File:** `src/gui/themes.py`  
**Blocker for:** all typography updates (Phase 3, all tools)

The existing `Fonts` class is retained for backward compatibility. `Typography` is added as the canonical class going forward. Tools migrated in Phase 3 switch to `Typography.*()` calls.

```python
class Typography:
    """Canonical typographic scale. Use class methods to obtain QFont instances.
    
    MUST be the sole source of QFont construction after Phase 3 migration.
    Do NOT call QFont() with explicit family/size arguments in tool code.
    """

    _FAMILY = "Segoe UI"

    @classmethod
    def h1(cls) -> QFont:
        """18 pt Bold — page/window title."""
        f = QFont(cls._FAMILY); f.setPointSize(18); f.setBold(True); return f

    @classmethod
    def h2(cls) -> QFont:
        """14 pt Bold — section heading."""
        f = QFont(cls._FAMILY); f.setPointSize(14); f.setBold(True); return f

    @classmethod
    def h3(cls) -> QFont:
        """12 pt SemiBold — subsection heading."""
        f = QFont(cls._FAMILY); f.setPointSize(12)
        f.setWeight(QFont.DemiBold); return f

    @classmethod
    def body(cls) -> QFont:
        """10 pt Regular — default body text."""
        f = QFont(cls._FAMILY); f.setPointSize(10); return f

    @classmethod
    def caption(cls) -> QFont:
        """8 pt Regular — labels, footnotes."""
        f = QFont(cls._FAMILY); f.setPointSize(8); return f
```

---

### 4.3 ComponentGuardian Relocation

**Current location:** `src/gui/component_guardian.py`  
**Required location:** `src/core/guardian/` (spec §7.2)  
**Blocker for:** ComponentGuardian registration in Phase 3

**Steps:**
1. Create `src/core/guardian/__init__.py`
2. Move `src/gui/component_guardian.py` → `src/core/guardian/component_guardian.py`
3. Add re-export shim at `src/gui/component_guardian.py`:
   ```python
   # Backward-compatibility shim — do not import directly in new code
   from src.core.guardian.component_guardian import (  # noqa: F401
       ComponentGuardian, ComponentState, ComponentError,
       ComponentDegradationError, ComponentRecoveryError,
       register_gui_component,
   )
   ```
4. Update any existing imports of `src.gui.component_guardian` to the new path.

---

### 4.4 Hub Shared Component Library

**Location:** `src/gui/components/`  
**Blocker for:** component replacement (Phase 3.1 for all tools)

The minimum subset that unblocks per-tool migration MUST be agreed and documented in `docs/ui-ux-harmonization/COMPONENT_LIBRARY_SCOPE.md` (one-time decision artifact, not a spec document).

**Minimum six component types required (spec §7.1):**

| Component | File | Key spec requirements |
|---|---|---|
| `PrimaryButton` / `SecondaryButton` | `src/gui/components/buttons.py` | One primary per view; destructive = semantic_error color; MUST have accessible label |
| `TextInput` | `src/gui/components/inputs.py` | Persistent label; inline validation; accessible label |
| `Modal` | `src/gui/components/modal.py` | Destructive actions require confirmation; accessible label |
| `ToastNotification` | `src/gui/components/toast.py` | Non-blocking; error/success/info token colors |
| `Breadcrumb` | `src/gui/components/breadcrumb.py` | Local nav only; does not reproduce Hub nav |
| `LoadingIndicator` | `src/gui/components/loading_indicator.py` | Shown after 300ms via QTimer; supports cancellation signal |

All components MUST:
- Set `setAccessibleName()` and `setAccessibleDescription()` on instantiation
- Use `token()` calls for all color values (no hard-coded hex)
- Use `Typography.*()` for all font construction

`src/gui/components/__init__.py` must export all six types.

---

### 4.5 LoadingIndicator — Cancellable Progress Contract

**File:** `src/gui/components/loading_indicator.py`  
**Spec references:** §8.1 (300ms threshold), §8.4 (cancellable progress)

```python
class LoadingIndicator(QWidget):
    cancelled = pyqtSignal()  # emitted when user cancels

    def __init__(self, parent=None, cancellable: bool = True): ...
    def start(self) -> None: ...   # shows after 300ms QTimer fires
    def stop(self) -> None: ...    # hides and resets timer
    def set_progress(self, value: int, maximum: int = 100) -> None: ...
```

`cancellable=True` renders a Cancel button using `SecondaryButton`. The `cancelled` signal is connected by the caller to abort the worker thread.

The 300ms delay MUST be implemented as:
```python
self._show_timer = QTimer(singleShot=True)
self._show_timer.setInterval(300)
self._show_timer.timeout.connect(self._show_widget)
# caller calls start() when the operation begins; widget stays hidden until 300ms elapses
```

---

### 4.6 Hub Global Error Screen

**File:** `src/gui/components/hub_error_screen.py`  
**Spec reference:** §8.2 (Creation Required)  
**Blocker for:** fatal error routing in Phase 3

```python
class HubErrorScreen(QWidget):
    """Displayed by the Hub when a tool raises a fatal (unrecoverable) error.
    
    Replaces the provisional error dialog fallback (spec §8.2).
    MUST be accessible (setAccessibleName set), non-technical, and actionable.
    """

    retry_requested = pyqtSignal()   # emitted when user clicks Retry
    go_home_requested = pyqtSignal() # emitted when user clicks Go to Hub

    def __init__(self, tool_name: str, error_code: str, parent=None): ...
    def set_message(self, user_message: str) -> None: ...
```

The Hub MUST intercept uncaught exceptions from tool windows and route fatal errors to this screen rather than crashing. Integration point: `src/tabbed_hub.py` `UtilityWindow` exception handler.

---

### 4.7 ui_strings.py

**File:** `src/rfu/ui_strings.py`  
**Spec reference:** §9.2  
**Blocker for:** i18n readiness audit in Phase 3

One namespace class per tool. Example structure:

```python
class Hub:
    TITLE = "Richard's File Utilities"
    LOADING = "Loading…"

class FileFinder:
    TITLE = "File Finder"
    SEARCH_BUTTON = "Search"
    # ...

class SyncBackup:
    TITLE = "Sync & Backup"
    DRY_RUN_LABEL = "Dry run (preview only — no files will be modified)"
    # ...
```

Direct string literals in widget constructors MUST NOT be used for user-visible text after Phase 3 migration. This file is created empty-per-tool and populated during Phase 3.3 for each tool.

---

### 4.8 Phase 1 Documentation Deliverables

These documents are created once by the project owner before Phase 3 begins:

| Document | Path | Description |
|---|---|---|
| Self-Assessment Template | `docs/ui-ux-harmonization/SELF_ASSESSMENT_TEMPLATE.md` | Eight-section checklist (one per Phase 1.1 inventory item) with Compliant/Non-compliant/N/A checkboxes |
| Issue Severity Rubric | `docs/ui-ux-harmonization/ISSUE_SEVERITY_RUBRIC.md` | Defines Critical, High, Medium, Low severity for all tools |
| UAT Scenario Template | `docs/ui-ux-harmonization/UAT_SCENARIO_TEMPLATE.md` | Lightweight scenario format with expected-outcome field |
| Component Library Scope | `docs/ui-ux-harmonization/COMPONENT_LIBRARY_SCOPE.md` | Minimum subset decision record |
| KEY_ACTIONS.md (per tool) | `docs/ui-ux-harmonization/{tool-name}/KEY_ACTIONS.md` | Per-tool keyboard-reachable action list |

---

## 5. Phase 2 — Gap Analysis & Remediation Planning

Each tool team produces `REMEDIATION_PLAN.md` at `docs/ui-ux-harmonization/REMEDIATION_PLAN.md` (one shared file, per-tool sections).

The gap analysis MUST address all items in the per-tool checklist (§6 below) using the Self-Assessment Template.

Critical engine classification MUST be assessed during Phase 2. The following tools are provisional critical engine candidates and MUST be verified or refuted:

| Tool | Suspected classification trigger |
|---|---|
| `synchronization_backup` | Batch file writes + irreversible moves/deletes |
| `duplicate_finder` | Batch destructive delete |
| `system_cleanup` | Batch/irreversible system file removal |
| `secure_delete` | Irreversible deletion |
| `encryption` | Security-sensitive processing |
| `security_scanner` | Security-sensitive output |
| `checksum` | Batch hash of large file sets |
| `pdf_tools` | Batch multi-file conversion |

Classification performed by: project owner, recorded in `docs/ui-ux-harmonization/CRITICAL_ENGINE_REGISTER.md`.

---

## 6. Phase 3 — Per-Tool Migration Checklist

Apply this checklist to each tool listed in §7. Every checkbox must be satisfied before Phase 4 sign-off for that tool.

### 6.1 Theming

- [ ] All hard-coded hex color values replaced with `token(key)` calls
- [ ] All `LightColors.*` / `DarkColors.*` direct references replaced
- [ ] All `QFont(family, size)` direct calls replaced with `Typography.*()` calls
- [ ] Tool responds correctly when `apply_theme("dark")` / `apply_theme("light")` is called at runtime
- [ ] Tool does NOT assign values to `hub_nav_*` token keys

### 6.2 Navigation & Dry-Run Surfacing

- [ ] Tool does NOT implement its own global navigation bar (if it does, document in DEVIATIONS.md per-tool section under DEV-002 or add a new per-tool entry)
- [ ] If the tool performs any side-effect operation (file write, delete, network call):
  - [ ] A dry-run control (checkbox, button, or toggle) is present in the default view
  - [ ] The dry-run control is reachable before the primary action button is enabled
  - [ ] The backend already gates on the dry-run flag OR the flag is added

### 6.3 Component Replacement

- [ ] Primary action button → `PrimaryButton` from `src/gui/components/buttons.py`
- [ ] Secondary / cancel buttons → `SecondaryButton`
- [ ] Any destructive action button uses `semantic_error` token color and shows confirmation modal
- [ ] Confirmation dialogs → `Modal` from `src/gui/components/modal.py`
- [ ] Toast / status notifications → `ToastNotification`
- [ ] Loading states → `LoadingIndicator` (start/stop wired to worker thread signals)
- [ ] If a shared component is NOT used, the deviation is documented in DEVIATIONS.md

### 6.4 Accessibility

- [ ] Every interactive control has `setAccessibleName()` set
- [ ] Every interactive control has `setAccessibleDescription()` set where description adds meaningful context beyond the name
- [ ] Tab order is logical and complete (verified manually)
- [ ] All color distinctions have non-color alternatives (icons, labels)
- [ ] Tool is functional at 200% zoom
- [ ] OS reduced-motion preference is respected (no unconditional animations)
- [ ] `KEY_ACTIONS.md` produced at `docs/ui-ux-harmonization/{tool-name}/KEY_ACTIONS.md`

### 6.5 Threading & Performance

- [ ] All file, network, and compute operations run off the UI thread (QThread / moveToThread pattern)
- [ ] UI thread is never blocked for ≥ 100ms
- [ ] `LoadingIndicator.start()` wired to worker `started` or equivalent
- [ ] `LoadingIndicator.stop()` wired to worker completion signal
- [ ] `LoadingIndicator.cancelled` wired to abort the worker thread
- [ ] Long-running operations expose cancellable progress (cancellable=True on LoadingIndicator)

### 6.6 Error Handling

- [ ] Fatal errors (unrecoverable) route to `HubErrorScreen` via the Hub's exception handler
- [ ] Non-fatal errors are surfaced inline (not via global error screen)
- [ ] User-facing error messages are clear, actionable, and non-technical
- [ ] Technical error details are logged (not shown in UI)
- [ ] Empty states include explanation + recommended action

### 6.7 ComponentGuardian Registration

- [ ] Tool's primary widget class registers with `ComponentGuardian` at `src/core/guardian/component_guardian.py` before the component is made available to users
- [ ] Registration includes: `widget`, `health_check` callable, `degraded_fallback` callable
- [ ] `degraded_fallback` renders the widget **visible** with reduced functionality (MUST NOT hide or remove the widget)
- [ ] Tool's implementation documentation defines which capabilities are disabled in degraded mode
- [ ] Recovery is automatic when `health_check()` returns `True` (no manual intervention code required — ComponentGuardian handles it)

### 6.8 Telemetry

- [ ] `ui_view_load` emitted on tool window show
- [ ] `ui_user_action` emitted for key user actions (non-PII)
- [ ] `ui_error_event` emitted on user-visible errors
- [ ] `ui_performance_metric` emitted for operations that trigger loading indicator
- [ ] All events include: `actor_username`, `session_id`, `timestamp`, `event_type`, `tool_id`
- [ ] Events do NOT include `device_id` or `app_instance_id` (DEV-001 exemption)
- [ ] Events routed to SQLite audit log

### 6.9 Strings

- [ ] All user-visible string literals replaced with references to `src/rfu/ui_strings.py` namespace class for this tool
- [ ] No bare string literals in widget constructors for user-visible text

### 6.10 Critical Engine (if classified)

- [ ] Tool is recorded in `docs/ui-ux-harmonization/CRITICAL_ENGINE_REGISTER.md`
- [ ] Property-based tests added (in addition to standard unit tests)
- [ ] Scenario edge-case tests added

---

## 7. Tool Migration Sequence

Tools are sequenced by risk and dependency. Tools with existing partial compliance go first to establish patterns.

### Tier 1 — Patterns Established (migrate first)

These tools have the most existing compliance work and will serve as reference implementations.

| # | Tool | Location | Known compliance head-start |
|---|---|---|---|
| 1 | `advanced_folders` | `src/tools/file_management/advanced_folders/` | Has `setAccessibleName`, `Typography`-like class, `QTimer` |
| 2 | `synchronization_backup` | `src/tools/file_management/synchronization_backup/` | Has `dry_run_checkbox`, `QThread` worker |
| 3 | `system_cleanup` | `src/tools/system/system_cleanup/` | Has `QThread` worker |

### Tier 2 — Standard Migration

| # | Tool | Location | Critical engine? |
|---|---|---|---|
| 4 | `duplicate_finder` | `src/tools/analysis/duplicate_finder/` | **Yes** (batch destructive) |
| 5 | `checksum` | `src/tools/analysis/checksum/` | **Yes** (batch hash) |
| 6 | `size_analyzer` | `src/tools/analysis/size_analyzer/` | No |
| 7 | `empty_folders` | `src/tools/analysis/empty_folders/` | No |
| 8 | `finder` | `src/tools/file_management/finder/` | No |
| 9 | `organizer` | `src/tools/file_management/organizer/` | No |
| 10 | `advanced_catalog` | `src/tools/file_management/advanced_catalog/` | No |
| 11 | `system_diagnostics` | `src/tools/system/system_diagnostics/` | No |
| 12 | `process_monitor` | `src/tools/system/process_monitor/` | No |
| 13 | `simple_system_info` | `src/tools/system/simple_system_info.py` | No |
| 14 | `software_maintenance` | `src/tools/system/software_maintenance/` | No |
| 15 | `network` | `src/tools/network/` | No |
| 16 | `logs` | `src/tools/logs/` | No |
| 17 | `metadata` | `src/tools/metadata/` | No |
| 18 | `preferences` | `src/tools/preferences/` | No |
| 19 | `file_operations` | `src/tools/file_operations/` | No |

### Tier 3 — Security-Sensitive (migrate last, extra review)

| # | Tool | Location | Critical engine? |
|---|---|---|---|
| 20 | `secure_delete` | `src/tools/file_operations/secure_delete/` | **Yes** (irreversible) |
| 21 | `encryption` | `src/tools/security/encryption/` | **Yes** (security-sensitive) |
| 22 | `security_scanner` | `src/tools/security/security_scanner/` | **Yes** (security-sensitive) |
| 23 | `password_generator` | `src/tools/security/password_generator/` | No |
| 24 | `pdf_tools` | `src/tools/pdf_tools/` | **Yes** (batch) |
| 25 | `privacy` | `src/tools/privacy/` | No |

---

## 8. Phase 4 — Verification Gates

### 8.1 Per-Tool Automated Checks

All constitutional CI gates must pass before UX harmonization sign-off (spec §10.1):

```
lint → type check → unit tests → integration tests → coverage ≥85% →
GUI smoke test → tool validation → dry-run surface check →
accessibility scan → theming compliance validation →
component usage validation → theming visual smoke test
```

**Theming visual smoke test** (constitution DW §11): render tool in both light and dark mode; screenshot diff must show token-driven color change. Must be run for every tool after Phase 3.2.

### 8.2 Per-Tool Manual Review Checklist

Using the Phase 4.2 items from the Migration Guide:
- Visual consistency with Hub color scheme in both themes
- Interaction predictability: primary button, cancel, destructive confirm
- Accessibility: Narrator + NVDA screen reader spot check
- Error handling: force a fatal error, verify HubErrorScreen appears
- Empty state: clear empty state widget present where applicable
- Dry-run: confirm dry-run control is visible before primary action

### 8.3 UAT Scenarios

Derived from Phase 1.1 user-flow inventory for each tool using the UAT Scenario Template. Each scenario documents expected outcome for unambiguous pass/fail.

---

## 9. Phase 5 — Integration & Monitoring

Each tool establishes its own baseline in `docs/ui-ux-harmonization/{tool-name}/POST_INTEGRATION_REPORT.md` before going live. Regressions measured against that baseline for 30 days.

Critical regression definition (until Issue Severity Rubric is published): any issue that (a) introduces an accessibility violation, (b) causes data loss or corruption, or (c) prevents a tool from launching or completing its primary function.

---

## 10. File Creation Summary

### New files to create (Phase 1 shared infrastructure)

| File | Phase | Purpose |
|---|---|---|
| `src/core/guardian/__init__.py` | 1.3 | Package init for relocated ComponentGuardian |
| `src/core/guardian/component_guardian.py` | 1.3 | Relocated from `src/gui/component_guardian.py` |
| `src/gui/components/__init__.py` | 1.3 | Component library exports |
| `src/gui/components/buttons.py` | 1.3 | PrimaryButton, SecondaryButton |
| `src/gui/components/inputs.py` | 1.3 | TextInput |
| `src/gui/components/modal.py` | 1.3 | Modal / confirmation dialog |
| `src/gui/components/toast.py` | 1.3 | ToastNotification |
| `src/gui/components/breadcrumb.py` | 1.3 | Breadcrumb |
| `src/gui/components/loading_indicator.py` | 1.3 | LoadingIndicator (300ms QTimer, cancellable) |
| `src/gui/components/hub_error_screen.py` | 1.3 | Hub global error screen |
| `src/rfu/ui_strings.py` | 1.3 | Per-tool namespace string store |
| `docs/ui-ux-harmonization/SELF_ASSESSMENT_TEMPLATE.md` | 1.3 | Eight-section compliance template |
| `docs/ui-ux-harmonization/ISSUE_SEVERITY_RUBRIC.md` | 1.3 | Critical/High/Medium/Low definitions |
| `docs/ui-ux-harmonization/UAT_SCENARIO_TEMPLATE.md` | 1.3 | UAT scenario format |
| `docs/ui-ux-harmonization/COMPONENT_LIBRARY_SCOPE.md` | 1.3 | Minimum subset decision record |
| `docs/ui-ux-harmonization/CRITICAL_ENGINE_REGISTER.md` | 2 | Classification outcomes |
| `docs/ui-ux-harmonization/REMEDIATION_PLAN.md` | 2 | Per-tool gap analysis + backlog |
| `docs/ui-ux-harmonization/{tool-name}/KEY_ACTIONS.md` | 1.3 | One file per tool (×25) |
| `docs/ui-ux-harmonization/{tool-name}/ASSESSMENT.md` | 1 | One file per tool |
| `docs/ui-ux-harmonization/{tool-name}/UX_COMPLIANCE.md` | 4 | One file per tool |
| `docs/ui-ux-harmonization/{tool-name}/VERIFICATION_REPORT.md` | 4 | One file per tool |
| `docs/ui-ux-harmonization/screenshots/{tool-name}/` | 3/4 | Key-flow screenshots per tool |
| `assets/ui_captures/{tool-name}/` | 1.1 | Full UI inventory per tool |

### Files to modify (Phase 1)

| File | Change |
|---|---|
| `src/gui/themes.py` | Add `TOKENS` dict, `Typography` class, `token()` / `apply_theme()` functions |
| `src/gui/component_guardian.py` | Replace with backward-compat shim pointing to `src/core/guardian/` |
| `src/tabbed_hub.py` | Add `HubErrorScreen` routing in `UtilityWindow` exception handler |

---

## 11. Dependency Graph

```
Phase 1.3 shared infrastructure
│
├── themes.py TOKENS + Typography
│   └── unblocks: all Phase 3.2 (theming) tasks
│
├── src/core/guardian/ (ComponentGuardian relocation)
│   └── unblocks: all Phase 3 §6.7 (registration) tasks
│
├── src/gui/components/ (shared library, min subset)
│   └── unblocks: all Phase 3.1 (component replacement) tasks
│   └── includes HubErrorScreen → unblocks Phase 3 §6.6 (fatal error routing)
│
├── src/rfu/ui_strings.py (skeleton)
│   └── unblocks: Phase 3.3 (string migration) per tool
│
└── Phase 1 documentation (templates, rubric, KEY_ACTIONS.md per tool)
    └── unblocks: Phase 2 (gap analysis) and Phase 4 (UAT)

Phase 2 (gap analysis + critical engine register)
└── unblocks: Phase 3 (tier ordering, extra tests for critical engines)

Phase 3 per-tool (Tier 1 → Tier 2 → Tier 3)
└── Tier 1 establishes reference implementations for Tier 2/3

Phase 4 (verification per tool)
└── requires: constitutional CI gates green + manual review pass

Phase 5 (integration + 30-day monitoring)
└── requires: Phase 4 sign-off
```

---

## 12. Open Decisions (must be resolved before Phase 1 work starts)

| # | Decision | Owner | Impacts |
|---|---|---|---|
| D1 | Which six components constitute the "minimum subset" of the component library that unblocks migration? | Richard Noragon | Phase 1.3 scope, Phase 3.1 start date |
| D2 | `ComponentGuardian` relocation: full move vs. thin re-export shim at old path? | Richard Noragon | Import updates across codebase |
| D3 | DEV-002 (UtilityWindow menubar-clone): adopt a shared minimal menubar component, or formally accept the current per-window pattern as compliant? | Richard Noragon | Phase 3.1 scope for all tool windows |
| D4 | `ui_strings.py` initial population scope: populated fully for all tools during Phase 1, or skeleton created in Phase 1 and filled per-tool in Phase 3? | Richard Noragon | Phase 1.3 effort estimate |

---

*This plan will be updated as Phase 1 deliverables are completed and open decisions are resolved.*
