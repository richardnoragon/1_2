# CI Enforcement Compliance Checklist

**Constitution Reference**: §11  
**Version**: 1.34.0

## Section A — Static Analysis Layer (§11.4)

- [ ] A1. TH: No raw color literals (hex, rgb, rgba) in tool code
- [ ] A2. TH: No raw font declarations in tool code
- [ ] A3. TH: All theme tokens used (no hardcoded values)
- [ ] A4. TH: `_on_theme_changed` handler present in all QWidget subclasses
- [ ] A5. DR: All destructive methods have `if self.dry_run` branching
- [ ] A6. DR: Dry-run toggle wired in tool `__init__`
- [ ] A7. CP: No `QPushButton(` in tool code (use PrimaryButton/SecondaryButton)
- [ ] A8. CP: No `QMessageBox.critical(` in tool code (use ModalError)
- [ ] A9. A11Y: `setAccessibleName` present on all interactive widgets
- [ ] A10. A11Y: No color-only indicators
- [ ] A11. A11Y: All widgets ≥ 44px in logical pixels
- [ ] A12. ERR: No `str(e)` passed to UI display functions
- [ ] A13. ERR: All `except` blocks call `logger.error`
- [ ] A14. STR: No raw string literals in `setText`, `setTitle`, menu labels
- [ ] A15. MEN: No `menuBar().addMenu(` outside Hub Menu Registry
- [ ] A16. MEN: No `addAction(` on QMenu objects in tool code
- [ ] A17. FNT: No `QFont("` with raw family name in tool code
- [ ] A18. LYT: No `setSpacing(` or `setContentsMargins(` with integer literals
- [ ] A19. WRD: No menu/button labels starting with present-participle verbs

## Section B — Schema Validation Layer (§11.5)

- [ ] B1. Menu registry schema validates without errors (§11.5.1)
- [ ] B2. All registered menus are in the allowed set (Tools, Reports, View)
- [ ] B3. All registered items have `label_token` present in `ui_strings`
- [ ] B4. No accelerator conflicts in the registry
- [ ] B5. Telemetry schema validates: all events in registered event list (§11.5.2)
- [ ] B6. All telemetry events include required fields
- [ ] B7. Preference schema validates: all preferences have type, default, doc (§11.5.3)
- [ ] B8. Tool metadata schema validates: tool_id, classification, capabilities, owner (§11.5.4)

## Section C — Runtime Test Layer (§11.6)

- [ ] C1. INT: PrimaryButton used for primary actions
- [ ] C2. INT: ConfirmationModal triggered for all destructive actions
- [ ] C3. INT: LoadingIndicator visible for all long-running operations
- [ ] C4. INT: No UI thread blocking ≥ 100 ms (measured)
- [ ] C5. GRD: `register_gui_component()` called on tool initialization
- [ ] C6. GRD: `health_check()` returns valid state
- [ ] C7. GRD: `degraded_fallback()` is functional
- [ ] C8. CE: Property-based tests cover all 5 scenarios (if CE-classified)
- [ ] C9. PERF: Worker offloading verified for all long-running operations
- [ ] C10. PERF: No synchronous I/O on UI thread
- [ ] C11. PERF: Perf markers (`perf_start`, `perf_end`) emitted

## Section D — Matrix Compliance Layer (§11.7)

- [ ] D1. Tool Capability Matrix loaded and validated
- [ ] D2. All required capabilities (TH, DR, CP, A11Y, PERF, ERR, GRD, TEL, STR, HUB, MEN, NOM, FNT, LYT, WRD, INT, OPS, CI) are ☑
- [ ] D3. No capability is marked "Partial" or "Unknown"
- [ ] D4. CE capability is ☑ if tool is CE-classified, N/A otherwise

## Section E — Reporting Layer (§11.8)

- [ ] E1. Machine-readable JSON report produced with one entry per capability
- [ ] E2. Human-readable Markdown summary produced
- [ ] E3. Hub governance dashboard updated with compliance status

## Section F — Failure Conditions (§11.9)

- [ ] F1. CI pipeline fails if ANY §11.4–§11.7 rule is violated
- [ ] F2. No override mechanisms applied outside constitutional amendment
- [ ] F3. All failures have line-number references in the JSON report

## Reviewer Notes

_Date:_ _______________  
_Reviewer:_ _______________  
_Tool:_ _______________  
_CI Run ID:_ _______________  
_Overall:_ ☐ All gates pass · ☐ Failures present (see report)
