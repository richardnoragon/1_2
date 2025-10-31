# RFU Tabbed Hub Tool Launch Remediation Roadmap

**Prepared:** 2025-10-17  
**Maintainers:** RFU Platform Engineering  
**Scope:** All utilities launched from `src/tabbed_hub.py::RFUHub`

---

## Status Snapshot

| Area                                                  | Priority | Current Status                                        | Owner                     | Target Completion |
| ----------------------------------------------------- | -------- | ----------------------------------------------------- | ------------------------- | ----------------- |
| Launch mechanism diagnostics                          | Critical | In progress – discovery completed, validation pending | Core Platform             | 2025-10-22        |
| Dependency & environment validation                   | High     | In progress – automated checks scaffolded             | Build & Release           | 2025-10-20        |
| UI/UX workflow validation                             | High     | Planned – test scripts drafted                        | UX QA                     | 2025-10-23        |
| Accessibility compliance                              | High     | Planned – WCAG 2.1 AA checklist queued                | Accessibility Guild       | 2025-10-24        |
| Performance & responsiveness profiling                | Medium   | Not started – profiling playbook approved             | Performance Engineering   | 2025-10-27        |
| Browser compatibility audit (embedded/hand-off flows) | Medium   | Planned – environment setup in progress               | Web Integration           | 2025-10-26        |
| Cross-platform verification (Win/macOS/Linux)         | High     | In progress – Windows baseline captured               | Cross-Platform Tiger Team | 2025-10-28        |

---

## Mission Objectives

- Restore deterministic tool launches from the tabbed hub for all registered utilities.
- Institutionalize diagnostics covering imports, GUI instantiation, and runtime signals.
- Validate the end-to-end user experience, accessibility posture, and responsiveness.
- Maintain a single source of truth for investigation notes, remediation decisions, and verification evidence.

---

## Diagnostic Framework

1. **Inventory & Categorization**
   - Enumerate all `open_*` launchers defined in `src/tabbed_hub.py` (currently 54 entries) and map them to their module/class targets.
   - Cross-check against `RFUHub.launch_tool` dispatch rules (`open_{tool}` naming convention plus fallback variants). Flag tools without corresponding methods or mismatched naming.
2. **Baseline Reproduction**
   - Capture logs from `get_log_manager().get_logger("RFUHub")` during launches to identify failure signatures (ImportError, AttributeError, QWidget instantiation errors).
   - Use `pytest tests/test_tool_import.py::test_tabbed_hub_openers` to assert import reachability.
3. **Root Cause Pathways**
   - **Import Mapping Failures:** Incorrect relative imports (e.g., `from ..utilities...` vs `src.tools...`) or missing `__init__` exports.
   - **Dependency Gaps:** Missing PyQt5 widgets, optional packages (e.g., `PyPDF2`, `cryptography`), or Qt platform plugins.
   - **GUI Initialization Faults:** Widgets expecting parent contexts or relying on menu/state initialization not available when launched stand-alone.
   - **State Synchronization Bugs:** `register_tool`, `update_tool_progress`, or menu cloning for `UtilityWindow` not firing, causing silent failures.
4. **Verification Harness**
   - Extend `tests/pre_beta/tool_launch_validator_fixed_final.py` with parameterized cases aligned to the latest tool inventory; assert window creation and `status_bar` messaging.
   - Instrument `RFUHub.launch_tool` with temporary telemetry hooks (Guarded by config `enable_launch_diagnostics`).

---

## Issue Log & Remediation Playbook

### 1. Naming Inconsistencies in Launch Dispatch

- **Symptom:** `launch_tool("Duplicate Finder")` fails because method expects `open_duplicate_finder`, but discovery layer exposes `DuplicateFinderGUI` under alternate alias.
- **Root Cause Analysis:** `RFUHub.launch_tool` converts spaces/hyphens to underscores and looks for `open_*` methods only. Legacy tools registered via `register_tool` bypass this and register alternate callbacks.
- **Remediation Steps:**
  1. Generate authoritative map using script stub (`scripts/audit_tool_launches.py`) to diff actual callable names vs. expected dispatch targets.
  2. Standardize method names or add explicit `tool_aliases` dict consumed by `launch_tool` fallback.
  3. Add regression test verifying alias coverage.
- **Verification:** Run `pytest tests/test_tool_import.py::test_launch_dispatch_aliases` (new test) and manual launch smoke from hub GUI.
- **Status:** In progress – mapping script under review.
- **ETA:** 2025-10-20.

### 2. Mixed Import Path Strategies Causing ImportError

- **Symptom:** Tools referencing both `from ..utilities...` and `from src.tools...` fail under packaged execution where `src` is not root.
- **Root Cause Analysis:** Several launchers include dual try/except import branches. Environment differences cause fallbacks to trigger but target modules missing due to packaging.
- **Remediation Steps:**
  1. Confirm canonical import paths (`src.utilities.*` per architectural spec) and update modules accordingly.
  2. Add lint rule (flake8 plugin) to flag disallowed legacy imports.
  3. Update packaging scripts to ensure `src` added to `sys.path` at hub bootstrap.
- **Verification:**
  - Automated: `pytest tests/test_tool_import.py`, `pytest tests/test_dependencies.py`.
  - Manual: Launch each affected tool after environment normalization.
- **Status:** Discovery completed; patch backlog created.
- **ETA:** 2025-10-22.

### 3. Qt Platform Plugin & Optional Dependency Drift

- **Symptom:** Launch attempts crash with `Could not load the Qt platform plugin "xcb"` (Linux) or missing DLL warnings.
- **Root Cause Analysis:** Platform-specific dependencies not bundled or environment variables missing.
- **Remediation Steps:**
  1. Enhance `activate_env.py` to verify `QT_QPA_PLATFORM_PLUGIN_PATH` and presence of required DLLs.
  2. Integrate `pip check` + `PyQt5` version pin validation in CI.
  3. For optional engines (PDF, encryption), add dependency report to launch diagnostics overlay.
- **Verification:** Run `python activate_env.py --verify` (new flag) across target OS images.
- **Status:** Planned; scripting underway.
- **ETA:** 2025-10-24.

### 4. UI/UX Regression in Utility Windows

- **Symptom:** `UtilityWindow` clones menu bar but fails when `SimpleMenuManager` absent, leaving blank windows.
- **Root Cause Analysis:** `_clone_menu_bar` assumes `simple_menu_manager` importable; fallback not resilient.
- **Remediation Steps:**
  1. Wrap menu cloning in capability detection; show contextual toolbar when menu unavailable.
  2. Add UX smoke test verifying each tool shows title, actionable widget, and status message.
  3. Capture screenshots via `pytest-qt` for regression diff.
- **Verification:** `pytest tests/ui/test_gui_integration_simple.py::test_tool_windows_render` with screenshot artifact.
- **Status:** Planned – UX QA authoring test matrix.
- **ETA:** 2025-10-23.

### 5. Accessibility Gaps (Keyboard Navigation & Contrast)

- **Symptom:** Tab navigation stalls inside tool dialogs; button styles from `tabbed_hub` fail color contrast ratios on dark themes.
- **Root Cause Analysis:** Custom stylesheets override default focus rectangles; tool-specific widgets lack accessible names.
- **Remediation Steps:**
  1. Introduce `AccessibilityAuditor` helper to enforce `setAccessibleName/Description` for critical widgets.
  2. Update stylesheets to maintain visible focus outlines and verify contrast with tooling (e.g., `axe-core` via Qt WebEngine harness).
  3. Document keyboard paths in UX spec and test them via scripted key events.
- **Verification:** Manual + automated using `pytest tests/ui/test_accessibility.py` (to be created).
- **Status:** Planned; requirements locked.
- **ETA:** 2025-10-24.

### 6. Performance Degradation on First Launch

- **Symptom:** First launch of multi-engine tools (PDF, Duplicate Finder) exhibits >3s freeze.
- **Root Cause Analysis:** Lazy imports and heavy initialization performed on UI thread without spinner feedback.
- **Remediation Steps:**
  1. Profile `open_pdf_tools` and similar using `QElapsedTimer`; log metrics via `logger.info`.
  2. Defer heavy work to background threads (`QThreadPool`) with progress signals.
  3. Add UI skeleton loaders to maintain responsiveness.
- **Verification:**
  - Automated: Performance harness in `tests/performance/test_tool_launch_latency.py` (new) measuring <1.5s target.
  - Manual: Stopwatch sampling across platforms.
- **Status:** Not started – instrumentation backlog.
- **ETA:** 2025-10-27.

### 7. Browser Compatibility of Embedded Views

- **Symptom:** Tools leveraging `QWebEngineView` (documentation panels, PDF previews) render differently depending on Chromium version.
- **Root Cause Analysis:** Packaged binaries ship with locked QtWebEngine; external browser hand-offs rely on default system browser.
- **Remediation Steps:**
  1. Run smoke tests across Chrome, Edge, Firefox to verify external link flows.
  2. Validate internal `QWebEngineView` with standardized user agent and feature flags.
  3. Provide fallback for headless environments using plain text previews.
- **Verification:** Document results in `reports/browser_compatibility_matrix.md`; attach logs.
- **Status:** Planned; environment provisioning underway.
- **ETA:** 2025-10-26.

### 8. Cross-Platform Packaging Differences

- **Symptom:** macOS app bundle fails to locate resources defined via Windows-style paths; Linux builds hit case-sensitivity issues.
- **Root Cause Analysis:** Hardcoded path separators in imports and resource lookups.
- **Remediation Steps:**
  1. Audit all launchers for `os.path` normalization; enforce `Path` usage.
  2. Extend `tests/cross_platform/` suite to simulate POSIX/NT path differences using `pyfakefs`.
  3. Validate packaged builds via GitHub Actions matrix.
- **Verification:** Run `pytest tests/cross_platform/test_launch_paths.py` (new) and confirm packaging scripts copy resources correctly.
- **Status:** In progress – POSIX audit 40% complete.
- **ETA:** 2025-10-28.

---

## Dependency Verification Checklist

- [ ] Confirm `PyQt5>=5.15` and matching Qt platform plugins installed.
- [ ] Validate optional modules per tool category:
  - PDF: `PyPDF2`, `fitz` (PyMuPDF), `reportlab`.
  - Security: `cryptography`, `pyAesCrypt`.
  - Network: `psutil`, `scapy` (optional), `paramiko`.
- [ ] Run `pip check` and compare `requirements.txt` vs `requirements-test.txt` for drift.
- [ ] Execute `python activate_env.py --verify` to ensure environment parity.

---

## UI/UX Validation Matrix

| Scenario              | Tools                           | Validation Steps                                                           | Expected Result                                  | Status    |
| --------------------- | ------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------ | --------- |
| Launch from tab click | All primary categories          | Click button, observe `status_bar` message, ensure window renders controls | Window opens within 1s, status message displayed | Scheduled |
| Keyboard navigation   | File operations, security tools | Navigate tabs via `Ctrl+Tab`, enter tool via `Enter`                       | Focus order logical, no traps                    | Planned   |
| Visual regression     | Top 10 tools by usage           | Capture screenshots via `pytest-qt`                                        | Pixel diff < 1% baseline                         | Planned   |
| Error handling        | Tools with known optional deps  | Force dependency miss, observe dialog from `error_handler`                 | User-friendly guidance shown                     | Planned   |
| Accessibility audit   | Representative sample           | Run `axe-core` harness, check contrast                                     | No WCAG 2.1 AA violations                        | Planned   |

---

## Performance Profiling Plan

1. Instrument `open_*` methods to log `launch_start`/`launch_end` timestamps.
2. Use `pytest tests/performance/test_tool_launch_latency.py` to collect metrics.
3. Capture flame graphs using `py-spy` for slowest tools.
4. Set SLO: P95 launch latency <= 1.5s, UI thread blocked <500ms.
5. Publish results to `reports/performance/tool_launch_timing.csv`.

---

## Browser Compatibility Strategy

- **External Flow Validation:** Use Selenium Grid to open links triggered by hub (documentation, support) in Chrome/Edge/Firefox (latest + N-1).
- **Embedded WebViews:** Validate QtWebEngine content by forcing hardware acceleration off/on and testing offline scenarios.
- **Reporting:** Centralize outcomes in `reports/browser_compatibility_matrix.md` with pass/fail and screenshots.

---

## Accessibility Compliance Workflow

1. Apply `AccessibilityAuditor` helper to annotate widgets with accessible names.
2. Run assistive technology smoke tests with Windows Narrator and NVDA.
3. Ensure tab order defined via `setTabOrder` for complex dialogs.
4. Validate color contrast using internal `contrast_auditor.py` script (3:1 for large text, 4.5:1 for body text).
5. Document compliance evidence and remediation tickets in this log.

---

## Cross-Platform Verification

- **Windows (Baseline):** Already exercised via local QA; ensure `activate_env.bat` seeds environment variables.
- **macOS:** Build with `py2app`; validate app bundle resources and notarization prerequisites.
- **Linux:** Use AppImage build; verify `QT_QPA_PLATFORM` set, run on Ubuntu 22.04 and Fedora 39.
- **Artifacts:** Store findings under `tests/pre_beta/cross_platform_compatibility_issues_and_behaviors.md` with links to this roadmap.

---

## Timeline & Milestones

| Milestone                           | Deliverables                                        | Due        |
| ----------------------------------- | --------------------------------------------------- | ---------- |
| Diagnostic completion               | Updated launch mapping, dependency audit report     | 2025-10-22 |
| UX & accessibility validation       | Test scripts, screenshot pack, compliance checklist | 2025-10-24 |
| Performance & browser compatibility | Profiling results, compatibility matrix             | 2025-10-27 |
| Cross-platform sign-off             | Matrix test results, packaging validation           | 2025-10-28 |
| Final readiness review              | Consolidated report, regression test green          | 2025-10-29 |

---

## Next Actions

1. Finalize tool inventory script and merge into CI diagnostics stage.
2. Update `tests/pre_beta/tool_launch_validator_fixed_final.py` with new tool coverage list.
3. Schedule accessibility and UI/UX regression runs; capture baseline evidence.
4. Prepare performance harness and integrate into nightly pipeline.
5. Review progress in daily stand-up; update status snapshot accordingly.

---

_This document functions as the living troubleshooting log. Update status fields and add verification evidence as remediation steps progress._
