# Menu Architecture Compliance Checklist

**Constitution Reference**: §7  
**Version**: 1.34.0

## Section A — Global Menu Bar Structure

- [ ] A1. Tool inherits the Global Menu Bar or has a documented governance exemption
- [ ] A2. Top-level menus appear in exact order: File, Edit, View, Tools, [Reports], Window, Help
- [ ] A3. No additional top-level menus are present
- [ ] A4. Reports menu is hidden when no reporting action is registered

## Section B — Menu Taxonomy

- [ ] B1. File menu contains only: open, save, export, import, session, exit operations
- [ ] B2. Edit menu is not extended with domain-specific actions
- [ ] B3. View menu contains no data-modifying actions
- [ ] B4. All tool-specific actions are in Tools or Reports
- [ ] B5. Help menu contains only: About, Diagnostics, Documentation, Shortcuts, Telemetry & Privacy info

## Section C — Nomenclature

- [ ] C1. All menu item labels use imperative verbs
- [ ] C2. Ellipsis "…" appears only on items that open a dialog
- [ ] C3. All menu item labels use Title Case
- [ ] C4. Tooltips use Sentence case
- [ ] C5. Reserved names are unaltered: Preferences, Exit, About, Check for Updates…, Export…, Undo, Redo, Zoom In, Zoom Out, Reset Zoom

## Section D — Interaction Behavior

- [ ] D1. All menus are fully keyboard navigable
- [ ] D2. All top-level menus expose Alt+\<letter\> accelerators
- [ ] D3. All items with shortcuts have shortcuts defined
- [ ] D4. Menu behavior is consistent in high-contrast mode
- [ ] D5. Menu behavior is consistent with zoom scaling active

## Section E — CI Enforcement

- [ ] E1. Static analysis CI gate (§11.4.7 MEN) passes with zero violations
- [ ] E2. No raw string literals in menu item registration code
- [ ] E3. All menu labels reference `ui_strings` tokens

## Reviewer Notes

_Date:_ _______________  
_Reviewer:_ _______________  
_Tool:_ _______________  
_Overall:_ ☐ Compliant · ☐ Non-Compliant · ☐ Exemption Granted
