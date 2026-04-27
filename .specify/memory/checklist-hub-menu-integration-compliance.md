# Hub Menu Integration Compliance Checklist

**Constitution Reference**: §9  
**Version**: 1.34.0

## Section A — Hub Menu Registry

- [ ] A1. Tool registers ALL menu items via `hub.menu_registry.register()` — no direct Qt menu calls
- [ ] A2. Tool deregisters ALL menu items in `closeEvent()` via `hub.menu_registry.deregister()`
- [ ] A3. No `QMenu.addAction()` or `QMenuBar.addMenu()` calls exist in tool code outside the registry
- [ ] A4. Registration occurs before the tool window is shown

## Section B — Menu Items

- [ ] B1. All registered labels use `ui_strings` tokens
- [ ] B2. All registered items have non-empty, non-conflicting accelerators
- [ ] B3. Items are registered only under: Tools, Reports, or View
- [ ] B4. No items registered under: File, Edit, Window, Help (unless exempted)

## Section C — Hub Navigation

- [ ] C1. File → Return to Hub is present in the tool window
- [ ] C2. Return to Hub shortcut is `Ctrl+H`
- [ ] C3. `Window → Reopen <ToolName>` is registered and calls `relaunch_tool_window()`
- [ ] C4. Tool does not maintain its own "Open Windows" list

## Section D — Guardian & Degraded Mode

- [ ] D1. If menu registration fails, a Guardian warning is surfaced
- [ ] D2. Tool enters degraded mode on registration failure
- [ ] D3. Hub exposes "Tool Unavailable" fallback item under Tools

## Section E — Telemetry

- [ ] E1. Hub emits telemetry on menu item activation (tool MUST NOT)
- [ ] E2. Tool does NOT emit menu-event telemetry directly

## Section F — Accessibility

- [ ] F1. All menu items support keyboard navigation
- [ ] F2. All menu items expose accelerators
- [ ] F3. All menu items have accessible names and descriptions
- [ ] F4. Tool does NOT override Hub-provided accessibility metadata

## Section G — CI Enforcement

- [ ] G1. §11.5.1 Menu Registry Schema validation passes with zero violations
- [ ] G2. §11.4.7 MEN static analysis passes with zero violations
- [ ] G3. T1–T5 runtime tests from hub-menu-integration-spec.md all pass

## Reviewer Notes

_Date:_ _______________  
_Reviewer:_ _______________  
_Tool:_ _______________  
_Overall:_ ☐ Compliant · ☐ Non-Compliant · ☐ Exemption Granted
