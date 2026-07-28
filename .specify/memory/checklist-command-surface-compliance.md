# Command Surface Harmonization Compliance Checklist

**Constitutional reference**: §8  
**Spec document**: docs/command-surface-spec.md  
**Version**: 1.35.0

Use this checklist during PR review for any PR that adds or modifies tool actions,
toolbars, context menus, or keyboard shortcuts.

---

## Section A — Action Tier Classification (§8.2)

- [ ] **A1** Every action in this PR is classified into exactly one of four tiers: Primary, Secondary, Advanced, or Destructive.
- [ ] **A2** Tier assignments are documented in the tool's implementation documentation.
- [ ] **A3** No action is left unclassified.

---

## Section B — Toolbar Layout (§8.4)

- [ ] **B1** Primary Action buttons are placed left-most in the toolbar's primary action group.
- [ ] **B2** Destructive Action buttons are visually separated (separator or spacing) from Primary and Secondary groups.
- [ ] **B3** No Advanced Action appears in any main toolbar.
- [ ] **B4** Advanced Actions are accessible through a menu or overflow panel.
- [ ] **B5** Primary buttons use `PrimaryButton` component (§10.5).
- [ ] **B6** Destructive buttons use `SecondaryButton` with danger styling (§10.6).

---

## Section C — Command Taxonomy (§8.3)

- [ ] **C1** Each action label uses one of the five canonical verbs (Inspect, Transform, Export, Apply, Revert) where applicable.
- [ ] **C2** Where no canonical verb applies, an imperative verb per §7.4.1 is used and the deviation is noted in the tool's implementation docs.
- [ ] **C3** No passive or ambiguous verb forms are used (per §7.4.1).

---

## Section D — Keyboard Shortcuts (§8.5)

- [ ] **D1** Every Primary Action has a keyboard shortcut (where technically feasible).
- [ ] **D2** No shortcut conflicts with global reserved accelerators (§7.5).
- [ ] **D3** All shortcuts are registered through the Hub Menu Registry (§9.4) — deferred until TODO(HUB_MENU_REGISTRY_API) resolves.
- [ ] **D4** Conflict detection is relied upon at registration time (§9.4.3).

---

## Section E — String Tokens (§8.6)

> **Note**: TODO(UI_STRINGS_MENU_TOKENS) is resolved. CI enforcement is active.

- [ ] **E1** All command labels are sourced from `ui_strings` tokens in `src/rfu/ui_strings.py`.
- [ ] **E2** New command tokens follow the naming convention in Section 6.1 of the spec.
- [ ] **E3** No raw string literals are used for command labels.

---

## Section F — Context Menus (§8.7)

- [ ] **F1** Context menu items are relevant to the currently selected item or context.
- [ ] **F2** Destructive Actions are placed at the bottom of the context menu, after a separator.
- [ ] **F3** Context menu items follow §7.4 nomenclature rules.
- [ ] **F4** No action is duplicated in both toolbar and context menu without a clear contextual reason.

---

## Section G — Tool Capability Matrix

- [ ] **G1** `docs/tool-capability-matrix.json` is updated for this tool if capabilities `MEN`, `NOM`, or `INT` have changed.

---

## Reviewer Sign-off

| Item | Status | Notes |
|------|--------|-------|
| Section A (Tiers) | ☐ | |
| Section B (Toolbar) | ☐ | |
| Section C (Taxonomy) | ☐ | |
| Section D (Shortcuts) | ☐ | |
| Section E (Tokens) | ☐ deferred | |
| Section F (Context menus) | ☐ | |
| Section G (Matrix) | ☐ | |

**Reviewer**: _______________  **Date**: _______________

---

## Section H — Command Surface Governance Triage (Next Steps)

Use this section when a PR touches command surfaces and constitutional TODOs are
still open.

### Priority P0

- [ ] **H1** `TODO(HUB_MENU_REGISTRY_API)` is explicitly addressed in this release plan (deliver now) or tracked with a dated milestone (defer with owner).
- [ ] **H2** `TODO(RELAUNCH_TOOL_WINDOW_API)` has a defined API signature and call sites listed for all affected tools.
- [ ] **H3** `TODO(OPS_PHASE3_SPEC)` impact on command execution semantics is acknowledged in PR notes (undo/redo, error taxonomy, logging, persistence).

### Priority P1

- [ ] **H4** `TODO(HUB_UX_COHESION)` acceptance criteria are documented for this tool: badge behavior, last-run state, and guardian health indicator exposure.
- [ ] **H5** Any deferred CI rule in Sections D/E is mapped to a concrete activation condition (what must land before enforcement is enabled).

### Source-of-Truth Consistency Check

- [ ] **H6** If constitution comments and checklists disagree on TODO status, latest normative section text is authoritative over historical Sync Impact notes, and this checklist links the follow-up amendment PR.

### Assigned Owner Roles and Milestones (Authoritative)

| TODO | Owner Role | Target Milestone | Enforcement Impact |
|------|------------|------------------|--------------------|
| TODO(HUB_MENU_REGISTRY_API) | Maintainer | v1.38.0 | deferred gate |
| TODO(RELAUNCH_TOOL_WINDOW_API) | Maintainer | v1.38.0 | deferred gate |
| TODO(OPS_PHASE3_SPEC) | Release Steward | v1.39.0 | deferred gate |
| TODO(HUB_UX_COHESION) | UX | v1.40.0 | none |
