# System Cleanup — Degraded Mode Reference

**Tool:** `system_cleanup`  
**Source method:** `SystemCleanupGUI.degraded_fallback()` in  
`src/tools/system/system_cleanup/system_cleanup_gui.py`  
**Last updated:** April 2026

---

## When Degraded Mode Is Triggered

`degraded_fallback()` is called by `ComponentGuardian` whenever
`health_check()` returns `False`.  `health_check()` returns `False` when any
of the following conditions is detected:

| Condition | Root cause |
|-----------|-----------|
| `PYQT5_AVAILABLE` is `False` | PyQt5 was not importable at module load time |
| `self.tab_widget` is `None` or has 0 tabs | `customize_cleanup_interface()` raised a fatal error during `__init__` |
| `self.cleanup_tools` is empty or missing | `init_cleanup_tools()` could not import `TempFilesCleaner` / `SafetyManager` (i.e. `CLEANUP_TOOLS_AVAILABLE = False`) |

---

## Disabled Capabilities

When degraded mode is active, the following buttons are disabled via
`btn.setEnabled(False)`:

| Button attribute | Label | Why disabled |
|-----------------|-------|-------------|
| `quick_cleanup_button` | Run Quick Cleanup | Requires `self.cleanup_tools` non-empty |
| `estimate_button` | Estimate Space | Requires `TempFilesCleaner` for directory scan |
| `preview_button` | Preview Files | Same dependency as estimate |
| `execute_button` | Execute Cleanup | Requires cleanup tool + safety manager |
| `stop_cleanup_button` | Stop Operation | No operation possible; disabled for consistency |

All other controls (tab navigation, backup viewer, results display) remain
enabled because they do not depend on the cleanup backend.

---

## User-Visible Notice

An inline notice is written to the first available target:

1. `self.cleanup_status_label` (Quick Cleanup tab status bar)
2. `self.status_label` (parent `SystemDiagnosticsGUI` status label)
3. `self._toast` (ToastNotification — fallback when labels are absent)

Notice text: *"Degraded mode — cleanup tools unavailable. Some features have
been disabled."*

---

## Recovery

Degraded mode is **not self-healing at runtime**. To restore full
functionality:

1. Resolve the underlying cause (e.g. repair the `src/tools/system/system_cleanup/`
   package so `CLEANUP_TOOLS_AVAILABLE` becomes `True`).
2. Restart the application — `__init__` calls `init_cleanup_tools()` again on
   the new instance.
3. `ComponentGuardian` will call `health_check()` on the new instance and skip
   `degraded_fallback()` if the check passes.

See `GRD-5` in `docs/ui-ux-harmonization/TASKS.md` for the recovery
verification procedure.
