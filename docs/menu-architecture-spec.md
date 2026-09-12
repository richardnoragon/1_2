# Menu Architecture & Nomenclature Specification

**Constitution Reference**: §7  
**Version**: 1.37.0  
**Added**: 2026-04-24 (harmonization2 Phase 2)
**Updated**: 2026-04-24 (v1.37.0 — bumped to align with constitution v1.37.0 harmonization2 completion)

---

## Overview

This document is the canonical reference implementation for Constitution §7 —
Menu Architecture & Nomenclature. It defines the mandatory structure, naming,
behavior, and interaction rules for all menus across the RFU application suite.

---

## 1. Global Menu Bar Structure

All tools that expose a windowed GUI MUST inherit the Global Menu Bar. The
required top-level menus, in exact order:

| Position | Name | Required |
|----------|------|----------|
| 1 | File | Always |
| 2 | Edit | Always |
| 3 | View | Always |
| 4 | Tools | Always |
| 5 | Reports | Only if tool registers reporting actions |
| 6 | Window | Always |
| 7 | Help | Always |

Issue #81 does not change the canonical menu topology, but the shared UI modernization pass now applies the refreshed style tokens and accessibility defaults used by the menu containers and dialogs.

---

## 2. Menu Taxonomy

### 2.1 File
Allowed: open, save, export, import, session lifecycle, exit.
Forbidden: domain-specific transformations or validations.

### 2.2 Edit
Reserved items: Undo, Redo, Cut, Copy, Paste, Select All, Find/Replace.
Tools MUST NOT add domain-specific actions here.

### 2.3 View
Allowed: zoom controls, layout toggles, theme switching, panel visibility.
Forbidden: actions that modify data.

### 2.4 Tools
Primary extension point for tool-specific functionality:
- Tool-specific actions
- Transformations
- Validations
- State-affecting operations

### 2.5 Reports
Allowed: generated reports, summaries, analytical exports.
Menu is hidden if no tool registers a reporting action.

### 2.6 Window
Reserved: window management, navigation between tool windows, Return to Hub.

### 2.7 Help
Reserved: About, Diagnostics, Documentation, Keyboard shortcuts,
Telemetry & privacy information.
Tools MAY add contextual help only.

---

## 3. Nomenclature Rules

### 3.1 Verb Forms

| ✅ Correct | ❌ Forbidden |
|-----------|------------|
| Export Report… | Processing… |
| Validate Input | Handler… |
| Apply Changes | Do Action |
| Run Diagnostics… | Submit |

Actions MUST use imperative verbs. Passive and ambiguous forms are prohibited.

### 3.2 Ellipsis Usage

Use "…" ONLY when the action opens a dialog requiring further user input.

| ✅ Correct | ❌ Forbidden |
|-----------|------------|
| Open File… | Delete File… |
| Export Report… | Apply Changes… |
| Run Diagnostics… | Refresh… |

### 3.3 Capitalization

- Menu items: Title Case
- Tooltips: Sentence case

### 3.4 Reserved Names

These names are globally reserved and MUST NOT be altered or replaced:

| Reserved Name | Forbidden Alternatives |
|--------------|------------------------|
| Preferences | Settings, Options, Configure |
| Exit | Quit, Close App |
| About | About App, Info |
| Check for Updates… | Update, Upgrade |
| Export… | Save As… (for export flows) |
| Undo / Redo | Back / Forward |
| Zoom In / Zoom Out / Reset Zoom | Scale, Magnify |

---

## 4. Interaction Behavior

All menus MUST:
- Be fully keyboard navigable
- Expose accelerators (Alt+F for File, Alt+E for Edit, Alt+V for View,
  Alt+T for Tools, Alt+R for Reports, Alt+W for Window, Alt+H for Help)
- Expose shortcuts where applicable (Ctrl+S for Save, Ctrl+Z for Undo, etc.)
- Respect accessibility zoom and high-contrast modes
- Maintain consistent ordering of items within each menu

---

## 5. CI Test Suite

### T1 — No new top-level menus
```
GIVEN a PR modifying a tool
WHEN the tool is initialized
THEN the tool MUST NOT register any top-level menu not in {File, Edit, View,
     Tools, Reports, Window, Help}
```

### T2 — Nomenclature compliance
```
GIVEN a menu item label
WHEN analyzed by the static analysis layer
THEN the label MUST begin with an imperative verb
AND  ellipsis MUST only appear if the action opens a dialog
AND  capitalization MUST be Title Case
```

### T3 — Accelerator presence
```
GIVEN all menu items in the suite
WHEN any menu item is registered
THEN an accelerator MUST be defined
AND  no two items under the same parent MUST share an accelerator
```

### T4 — Reserved name integrity
```
GIVEN the global reserved name list
WHEN a tool registers a menu item
THEN no reserved name may be altered or duplicated under a different label
```

### T5 — String token enforcement
```
GIVEN any menu item label
WHEN inspected by static analysis
THEN the label MUST reference a ui_strings token
AND  no raw string literal MUST appear as a menu label in tool code
```

---

## 6. Migration Steps

### Step 1 — Audit existing menus
Run the static analysis layer against all tool files. Capture all violations.

### Step 2 — Add string tokens
For every raw string label found, add a corresponding entry to `ui_strings.py`.

### Step 3 — Add accelerators
Assign accelerators to all menu items. Verify no conflicts with the global
accelerator registry.

### Step 4 — Move items to correct categories
Move any domain-specific items from File/Edit/Help/Window into Tools or Reports.

### Step 5 — Rename reserved items
Replace any forbidden names (e.g., "Settings" → "Preferences", "Quit" → "Exit").

### Step 6 — CI gate
Enable the §11.4.7 MEN static analysis gate. Confirm zero violations on green build.

---

## Cross-References

- Constitution §7 (normative)
- Constitution §9 Hub Menu Integration Specification
- Constitution §11.4.7 CI enforcement rule MEN
- .specify/memory/checklist-menu-architecture-compliance.md
