# Hub Menu Integration Specification

**Constitution Reference**: §9  
**Version**: 1.37.0  
**Added**: 2026-04-24 (harmonization2 Phase 2)
**Updated**: 2026-04-24 (v1.37.0 — bumped to align with constitution v1.37.0 harmonization2 completion)

---

## Overview

This document is the canonical reference for Constitution §9 — Hub Menu
Integration Specification. It defines how the Hub and all Hub-launched tools
integrate with the Global Menu Bar defined in §7.

---

## 1. Hub Menu Registry API

All tools MUST use the Hub Menu Registry API. Direct Qt menu manipulation is
prohibited.

### 1.1 Registration

```python
# Tool registers its menu items via the Hub Menu Registry
hub.menu_registry.register(
    tool_id="my_tool",
    menu="Tools",
    label=ui_strings.MY_TOOL_ACTION,
    accelerator="Ctrl+Shift+M",
    enabled_condition=lambda: self.is_ready(),
    visible_condition=lambda: self.window().isVisible(),
    callback=self.on_action,
)
```

### 1.2 Deregistration

```python
# Tool deregisters its items when its window closes
def closeEvent(self, event):
    hub.menu_registry.deregister(tool_id="my_tool")
    super().closeEvent(event)
```

### 1.3 Conflict Handling

If an accelerator conflict is detected, the Hub:
1. Rejects the second registration
2. Surfaces a Guardian warning
3. Logs the conflict with tool ID, menu, and conflicting accelerator

---

## 2. Hub-Specific Menu Item Registry

The following items are Hub-owned and MUST always be present:

| Menu | Item | Shortcut | Condition |
|------|------|----------|-----------|
| File | Return to Hub | Ctrl+H | Tool windows only |
| File | Exit | Alt+F4 | Always |
| View | Show Hub Tabs | — | Always |
| View | Show Tool List | — | Always |
| View | Reset Layout | — | Always |
| Tools | Open Preferences… | Ctrl+, | Always |
| Tools | Reload Tool Registry | — | Always |
| Tools | Run Diagnostics… | — | Always |
| Window | Hub Home | Ctrl+0 | Always |
| Window | Open Tool Window… | Ctrl+Shift+O | Always |
| Window | Switch to Previous Tool | Ctrl+Tab | When ≥2 tools open |
| Help | Hub Documentation | F1 | Always |
| Help | Keyboard Shortcuts | Ctrl+? | Always |
| Help | About Hub | — | Always |

---

## 3. Tool Integration Checklist

For each tool to be Hub Menu compliant:

- [ ] Tool registers ALL menu items via `hub.menu_registry.register()`
- [ ] Tool deregisters ALL menu items in `closeEvent()`
- [ ] All menu items use `ui_strings` tokens (no raw strings)
- [ ] All menu items have non-conflicting accelerators
- [ ] Menu items appear only in: Tools, Reports, or View
- [ ] File → Return to Hub is present and maps to `Ctrl+H`
- [ ] Window → Reopen \<ToolName\> is registered
- [ ] Guardian fallback "Tool Unavailable" is handled

---

## 4. Navigation Flow

```
Hub
├── File → Return to Hub (only in tool windows)
├── Window
│   ├── Hub Home          (Ctrl+0)
│   ├── Open Tool Window… (Ctrl+Shift+O)
│   ├── Switch to Previous Tool (Ctrl+Tab)
│   └── Open Windows
│       ├── [Tool A]
│       ├── [Tool B]
│       └── [Tool C]
```

---

## 5. CI Tests

### T1 — No direct Qt menu manipulation
```
GIVEN tool source code
WHEN scanned by static analysis
THEN no calls to QMenu.addAction() or QMenuBar.addMenu() outside
     hub.menu_registry are present
```

### T2 — Deregistration on close
```
GIVEN a tool window
WHEN closeEvent() is called
THEN hub.menu_registry.deregister(tool_id=...) MUST be called
AND  no tool-specific items remain visible in the global menu bar
```

### T3 — Return to Hub
```
GIVEN any tool window
WHEN File menu is opened
THEN "Return to Hub" item MUST be present
AND  its shortcut MUST be Ctrl+H
AND  activation MUST call hub.show_hub() or equivalent
```

### T4 — Guardian degradation
```
GIVEN a tool whose menu registration fails
WHEN the Hub initializes
THEN a Guardian warning MUST be surfaced
AND  a "Tool Unavailable" fallback item MUST appear under Tools
```

### T5 — Accelerator uniqueness
```
GIVEN all registered tool accelerators
WHEN the full registry is validated
THEN no two items under the same parent menu share an accelerator
```

---

## 6. Migration Steps

### Step 1 — Replace Qt menu calls
Replace all direct `QMenu.addAction()` / `QMenuBar.addMenu()` calls with
`hub.menu_registry.register()` equivalents.

### Step 2 — Add deregistration
Add `hub.menu_registry.deregister(tool_id=self.tool_id)` to every tool's
`closeEvent()`.

### Step 3 — Add Return to Hub
Ensure File → Return to Hub is registered with `Ctrl+H` shortcut.

### Step 4 — Add Reopen action
Register `Window → Reopen <ToolName>` action calling `relaunch_tool_window()`.

### Step 5 — Guardian fallback
Implement degraded-mode handler that provides "Tool Unavailable" fallback item.

### Step 6 — CI gate
Enable §11.5.1 Menu Registry Schema validation. Confirm zero violations.

---

## Cross-References

- Constitution §9 (normative)
- Constitution §7 Menu Architecture & Nomenclature
- Constitution §11.5.1 CI schema validation rule
- .specify/memory/checklist-hub-menu-integration-compliance.md
