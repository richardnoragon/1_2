# UI Interaction Contract Specification

**Constitution Reference**: §10  
**Version**: 1.37.0  
**Added**: 2026-04-24 (harmonization2 Phase 2)
**Updated**: 2026-04-24 (v1.37.0 — bumped to align with constitution v1.37.0 harmonization2 completion)

---

## Overview

This document is the canonical reference for Constitution §10 — UI Interaction
Contract. It defines mandatory interaction patterns, behavioral guarantees, and
user-experience invariants that all tools MUST follow.

The current issue #81 UI/UX modernization pass aligns this contract with the shared token-based styles, explicit keyboard focus visibility, and accessibility defaults now used by the common window and dialog layers.

---

## 1. Interaction Principles

All tools MUST satisfy all six principles:

| # | Principle | Requirement |
|---|-----------|-------------|
| 1 | Predictability | Identical actions behave identically across tools |
| 2 | Reversibility | Destructive actions require explicit confirmation (§II.2) |
| 3 | Visibility | System state and progress MUST be visible (§G.1) |
| 4 | Non-blocking UI | No UI thread blocking beyond 100 ms (§IV) |
| 5 | Accessibility | All interactions MUST be keyboard-navigable and zoom-safe (§7 Constraint) |
| 6 | Determinism | No hidden side effects (§G.3) |

---

## 2. Action Classification

Every action exposed by a tool MUST be classified in its implementation docs:

| Class | Description | Button Style | Placement |
|-------|-------------|-------------|-----------|
| Primary | Main operation (Apply, Run, Validate) | PrimaryButton | Bottom-right of dialog |
| Secondary | Supportive operation (Preview, Export) | SecondaryButton | Adjacent to Primary |
| Destructive | Irreversible or high-impact | SecondaryButton + danger styling | Secondary placement + confirmation modal |
| Advanced | Expert-level or rarely used | SecondaryButton | Advanced/overflow section |

---

## 3. Component Contracts

### 3.1 PrimaryButton Contract

```
MUST: Use PrimaryButton shared component (no custom button classes)
MUST: Be placed in bottom-right of dialog/panel
MUST: Use imperative verb label
MUST: Emit telemetry ui_user_action on activation
MUST: Respect dry-run mode (§II.1)
MUST NOT: Perform destructive actions without confirmation
```

### 3.2 Destructive Action Contract

```
MUST: Use SecondaryButton with danger styling
MUST: Trigger ConfirmationModal before execution
MUST: Show affected items and irreversible consequences
MUST: Support dry-run mode (§II.1)
MUST: Emit telemetry ui_error_event if execution fails
MUST NOT: Execute silently or skip the modal
```

### 3.3 LoadingIndicator Contract

```
MUST: Appear within 100 ms of a long-running operation starting
MUST: Move all work off the UI thread (QThread or equivalent)
MUST: Disable conflicting controls during operation
MUST: Emit telemetry perf_start at start, perf_end at completion
MUST: Support cancellation where technically feasible
MUST NOT: Block the Qt event loop
```

### 3.4 ModalError Contract

```
MUST: Use shared ModalError component for all error surfaces
MUST: Provide actionable, user-friendly message
MUST: Include error code reference
MUST: Emit telemetry ui_error_event
MUST NOT: Surface raw str(exception) or Python tracebacks to the user
MUST NOT: Silently swallow errors
```

---

## 4. Reference Patterns

### 4.1 Primary Action Pattern

```python
class MyToolWindow(QMainWindow):
    def setup_buttons(self):
        self.apply_btn = PrimaryButton(
            label=ui_strings.MY_TOOL_APPLY,
            parent=self
        )
        self.apply_btn.clicked.connect(self.on_apply)

    def on_apply(self):
        telemetry.emit("ui_user_action", tool="my_tool", action="apply")
        if self.dry_run_mode:
            self._show_dry_run_preview()
        else:
            self._execute_apply()
```

### 4.2 Destructive Action Pattern

```python
    def on_delete(self):
        modal = ConfirmationModal(
            title=ui_strings.CONFIRM_DELETE_TITLE,
            message=ui_strings.CONFIRM_DELETE_MESSAGE.format(
                items=self.selected_items
            ),
            consequence=ui_strings.CONFIRM_DELETE_CONSEQUENCE,
        )
        if modal.exec() == QDialog.Accepted:
            try:
                self._execute_delete()
            except Exception as e:
                telemetry.emit("ui_error_event", tool="my_tool",
                               error_code="ERR_DELETE_FAILED")
                ModalError.show(code="ERR_DELETE_FAILED",
                                message=ui_strings.DELETE_FAILED_MESSAGE)
```

### 4.3 Long-Running Operation Pattern

```python
    def on_run(self):
        self.loading = LoadingIndicator(parent=self)
        self.loading.show()
        self._disable_controls()
        telemetry.emit("perf_start", tool="my_tool", operation="run")

        self.worker = RunWorker(params=self.params)
        self.worker.finished.connect(self._on_run_complete)
        self.worker.error.connect(self._on_run_error)
        self.worker.start()

    def _on_run_complete(self, result):
        telemetry.emit("perf_end", tool="my_tool", operation="run")
        self.loading.hide()
        self._enable_controls()
        self._show_result(result)
```

---

## 5. CI Tests

### T1 — PrimaryButton usage
```
GIVEN all tool dialogs and panels
WHEN scanned by static analysis
THEN any call site for primary actions MUST use PrimaryButton
AND  PrimaryButton MUST be placed in the bottom-right layout position
```

### T2 — Destructive action confirmation
```
GIVEN all destructive action handlers (delete, overwrite, wipe, anonymize)
WHEN the handler is invoked
THEN a ConfirmationModal MUST appear before execution
AND  execution MUST be blocked until user explicitly confirms
```

### T3 — UI thread non-blocking
```
GIVEN all long-running operations (> 100 ms expected)
WHEN timed via Qt performance profiler
THEN the UI thread MUST NOT block for ≥ 100 ms continuously
AND  a LoadingIndicator MUST be visible during the operation
```

### T4 — ModalError usage
```
GIVEN all error handling paths
WHEN an exception is caught
THEN ModalError MUST be used (not QMessageBox.critical directly)
AND  str(exception) MUST NOT appear in any user-visible message string
```

### T5 — Telemetry completeness
```
GIVEN primary action handlers
WHEN any primary action is invoked
THEN telemetry.emit("ui_user_action", ...) MUST be called
```

---

## 6. Migration Steps

### Step 1 — Audit action classifications
Review all tool actions. Classify each as Primary, Secondary, Destructive,
or Advanced. Document in the tool's README.

### Step 2 — Replace custom buttons
Replace all custom button implementations with PrimaryButton / SecondaryButton
shared components.

### Step 3 — Add confirmation modals
For all destructive actions lacking confirmation modals, add ConfirmationModal.

### Step 4 — Offload long-running work
Move all operations > 100 ms to QThread workers. Add LoadingIndicator.

### Step 5 — Replace raw error dialogs
Replace all `QMessageBox.critical(str(e))` calls with `ModalError.show(...)`.

### Step 6 — Add telemetry
Add `telemetry.emit("ui_user_action", ...)` to all primary action handlers.

### Step 7 — CI gate
Enable §11.6.1 INT runtime tests. Confirm zero violations.

---

## Cross-References

- Constitution §10 (normative)
- Constitution §II Safety & Data Integrity (dry-run and confirmation)
- Constitution §IV Performance & Scalability (UI thread limit)
- Constitution §11.6.1 CI runtime test rule INT
- .specify/memory/checklist-ui-interaction-contract-compliance.md
