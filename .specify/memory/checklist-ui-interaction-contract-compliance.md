# UI Interaction Contract Compliance Checklist

**Constitution Reference**: §10  
**Version**: 1.34.0

## Section A — Interaction Principles

- [ ] A1. Identical actions behave identically across tools (Predictability)
- [ ] A2. All destructive actions require explicit confirmation (Reversibility — §II.2)
- [ ] A3. System state and progress are visible via LoadingIndicator / status (Visibility — §G.1)
- [ ] A4. No UI thread blocking ≥ 100 ms (Non-blocking UI — §IV)
- [ ] A5. All interactions are keyboard-navigable and zoom-safe (Accessibility — §7 constraint)
- [ ] A6. No hidden side effects (Determinism — §G.3)

## Section B — Action Classification

- [ ] B1. All tool actions are classified as: Primary, Secondary, Destructive, or Advanced
- [ ] B2. Classification is documented in the tool's README or implementation docs
- [ ] B3. All action classes are exposed consistently (same layout, same component)

## Section C — Primary Actions

- [ ] C1. Primary actions use `PrimaryButton` shared component
- [ ] C2. `PrimaryButton` is placed in the bottom-right of dialogs/panels
- [ ] C3. Primary action label uses an imperative verb
- [ ] C4. Primary action emits `telemetry.emit("ui_user_action", ...)`
- [ ] C5. Primary action respects dry-run mode

## Section D — Destructive Actions

- [ ] D1. Destructive actions use `SecondaryButton` with danger styling
- [ ] D2. Destructive actions trigger `ConfirmationModal` before execution
- [ ] D3. `ConfirmationModal` lists affected items and irreversible consequences
- [ ] D4. Destructive actions support dry-run mode
- [ ] D5. Destructive actions emit `telemetry.emit("ui_error_event", ...)` on failure

## Section E — Long-Running Operations

- [ ] E1. All operations > 100 ms run on a QThread worker (not the UI thread)
- [ ] E2. `LoadingIndicator` appears within 100 ms of operation start
- [ ] E3. Conflicting controls are disabled during the operation
- [ ] E4. `telemetry.emit("perf_start", ...)` called at start
- [ ] E5. `telemetry.emit("perf_end", ...)` called at completion
- [ ] E6. Cancellation is supported where feasible

## Section F — Error Handling

- [ ] F1. All errors surface via `ModalError` shared component
- [ ] F2. Error messages are actionable and user-friendly
- [ ] F3. No raw `str(exception)` or traceback appears in user-visible messages
- [ ] F4. All error paths emit `telemetry.emit("ui_error_event", ...)`
- [ ] F5. Guardian fallback is provided if the tool becomes degraded

## Section G — Navigation

- [ ] G1. File → Return to Hub is present (per §9.8.1)
- [ ] G2. Tool is registered with the Hub Window Manager
- [ ] G3. Global menu structure (§7) is respected
- [ ] G4. Consistent keyboard shortcuts are exposed

## Section H — CI Enforcement

- [ ] H1. §11.6.1 INT runtime tests pass: PrimaryButton, confirmation modals, LoadingIndicator, UI thread
- [ ] H2. §11.4.3 CP static analysis passes (no raw Qt widgets for primary patterns)
- [ ] H3. §11.4.5 ERR static analysis passes (no raw str(e) in UI)

## Reviewer Notes

_Date:_ _______________  
_Reviewer:_ _______________  
_Tool:_ _______________  
_Overall:_ ☐ Compliant · ☐ Non-Compliant · ☐ Partial (document in Notes)
