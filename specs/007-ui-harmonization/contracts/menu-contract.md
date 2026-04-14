# Contract: Menu Structure

**Contract ID**: `menu-contract-v1`
**Feature**: `007-ui-harmonization`
**Owner**: `src/gui/menu_manager.py`
**Tested by**: `tests/contract/gui/test_menu_contract.py`

---

## Required Top-Level Menus (ordered)

| Index | Label | Shortcut prefix |
|---|---|---|
| 0 | File | `&File` |
| 1 | Edit | `&Edit` |
| 2 | View | `&View` |
| 3 | Tools | `&Tools` |
| 4 | Help | `&Help` |

No other top-level menus may appear between these five. Additional tool-specific menus MAY be appended AFTER `Help`.

---

## File Menu — Required Actions (ordered)

| Position | Action ID | Label | Shortcut |
|---|---|---|---|
| 0 | `open_file` | `&Open…` | Ctrl+O |
| 1 | `save_file` | `&Save` | Ctrl+S |
| 2 | `save_as_file` | `Save &As…` | Ctrl+Shift+S |
| — | separator | — | — |
| 3 | `import_data` | `&Import…` | — |
| 4 | `export_data` | `&Export…` | — |
| — | separator | — | — |
| 5 | `show_preferences` | `&Preferences…` | Ctrl+, |
| — | separator | — | — |
| 6 | `exit` | `E&xit` | Ctrl+Q |

When a standard File-menu action has no direct meaning for a tool, it MUST be renamed to a tool-relevant label (e.g., `Open Report…`, `Export Log…`, `Save Results…`). Actions MUST NOT be hidden or greyed out.

---

## View Menu — Required Actions

| Action ID | Label | Type | Behaviour |
|---|---|---|---|
| `theme` | `&Theme` | Submenu | Contains: Light, Dark, System (radio group) |
| `font_picker` | `&Font…` | Action | Opens `FontPickerDialog` |
| `working_directory_picker` | `&Working Directory…` | Action | Opens `DirectoryPickerDialog` |

Additional view actions (zoom, sidebar, etc.) MAY be added by individual tools BEFORE or AFTER these three, but these three MUST always be present.

---

## Help Menu — Required Actions

| Position | Action ID | Label |
|---|---|---|
| last | `about` | `&About RFU…` |

The About action MUST always be the final item in the Help menu.

---

## About Dialog — Required Content

The dialog opened by `about` MUST display all of the following:

1. Tool display name
2. RFU suite version (read from `src/__version__.py` or `importlib.metadata`)
3. Tool-specific version (if defined; otherwise same as suite version)
4. Python version (`sys.version`)
5. PyQt5 version (`PyQt5.QtCore.PYQT_VERSION_STR`)
6. Qt5 version (`PyQt5.QtCore.QT_VERSION_STR`)

---

## Edit Menu — Tool-Specific (no required items)

The Edit menu is entirely tool-defined. No actions are mandated by this contract.
Contract tests do NOT validate Edit menu contents.

Tools that provide editable content typically include: `Undo`, `Redo`, `Cut`, `Copy`, `Paste`, `Select All`.
Tools with no editable content MAY leave the Edit menu empty.

---

## Tools Menu — Tool-Specific (no required items)

The Tools menu is entirely tool-defined. No actions are mandated by this contract.
Contract tests do NOT validate Tools menu contents.

---

## Contract Validation

The contract is verified by `tests/contract/gui/test_menu_contract.py` which:

1. Iterates every tool class registered in `ToolManifest`.
2. Instantiates each using `QApplication` with offscreen platform (`-platform offscreen`).
3. Checks that `menuBar().actions()` returns at least 5 items.
4. Checks labels match `["File", "Edit", "View", "Tools", "Help"]` for positions 0–4.
5. Inspects the File menu for required action IDs via `objectName()`.
6. Inspects the View menu for `font_picker` and `working_directory_picker` action IDs.
7. Inspects the Help menu and verifies the last action is `about`.

Tests MUST pass WITHOUT a physical display.
