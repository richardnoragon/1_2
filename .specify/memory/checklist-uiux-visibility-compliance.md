# Checklist — UI/UX Visibility Compliance

**Cross-reference**: `constitution.md` §G.1, §G.2, §VI Portability, §15
Credential Reset, Development Workflow §6
**Applies to**: All PR reviews that add, change, or remove any element
described as "user-visible" or "user-discoverable" in the codebase.
**Version**: 1.0 (introduced 2026-04-03, aligned with constitution v1.14.0)

---

## A. Determining the Required Visibility Level

Before reviewing the implementation, establish which level the constitution
requires for the element under review.

| Context | Required level | Constitutional reference |
|---|---|---|
| Skipped-item summary during preference import | User-visible | §VI Portability, §G.1 |
| Offline breached-password warning | User-visible | §15, §G.1 |
| Any other "user-visible warning" or "user-visible summary" | User-visible | §G.1 |
| Dry-run supplementary detail | User-discoverable | §II, §G.2 |
| Documentation Gate trigger (DW §6) | User-visible | DW §6, §G.1 |

---

## B. User-Visible Checklist (§G.1)

Use this section when the constitution requires a **user-visible** element.

### B1 — Surface type
- [ ] Element appears as one of the **permitted** surfaces:
  - modal dialog
  - inline banner rendered in the main content area
  - automatic toast/notification appearing in the main viewport without
    user action
- [ ] Element does **NOT** use a disallowed surface:
  - [ ] NOT a status bar or status bar icon
  - [ ] NOT a notification tray or taskbar badge
  - [ ] NOT a collapsible/expandable panel (unless already expanded at
        the time of the event)
  - [ ] NOT a tooltip requiring hover
  - [ ] NOT a log panel or output panel
  - [ ] NOT a sidebar requiring an explicit open action

### B2 — Automatic appearance
- [ ] Element appears **automatically** when the triggering condition
  occurs — no user action is needed to trigger its display.

### B3 — No navigation required
- [ ] User does **not** need to navigate away from the current view to
  see the element.
- [ ] User does **not** need to expand, scroll, or interact with any
  other control before the element is visible.

### B4 — Suppressibility
- [ ] The element is **not suppressible by default** (user cannot
  pre-configure it to be hidden).
- [ ] If the element can be dismissed, it reappears on the next
  triggering event.

### B5 — Content completeness
- [ ] The element clearly describes the condition it is reporting.
- [ ] For skipped-item summaries: each skipped item is listed with its
  reason.
- [ ] For warnings: the warning states the implication of the condition.

### B6 — CI testability
- [ ] The element is reachable via widget-tree or DOM inspection without
  navigation.
- [ ] A test exists (or is added in this PR) that asserts the element's
  presence in the active foreground viewport when the triggering
  condition fires.
- [ ] FAIL if: the test only checks that the element "exists in the
  component hierarchy" without verifying it appears in the foreground.

---

## C. User-Discoverable Checklist (§G.2)

Use this section when the constitution permits (not requires) a
**user-discoverable** surface, or when validating supplementary
diagnostic content.

### C1 — One navigation step
- [ ] The element is reachable in **exactly one** navigation step from
  the current active UI state.
  - Permitted steps: click a top-level tab, open a clearly labelled
    sidebar, select a single first-level menu item, expand a single
    visible accordion.

### C2 — No external knowledge required
- [ ] The element is reachable without consulting external documentation.
- [ ] The element is reachable without knowledge of hidden or non-obvious
  UI patterns.

### C3 — Does not replace user-visible
- [ ] FAIL if: a surface that should be user-visible (per column B) has
  been downgraded to user-discoverable.
- [ ] Check: verify that mandatory warnings, skipped-item summaries, and
  offline notices are not relegated to logs, sidebars, or panels.

---

## D. Documentation Gate Check (DW §6)

- [ ] If this PR adds or changes **user-visible behavior** (as defined in
  §G.1), the user guide has been updated.
- [ ] If this PR adds or changes **user-visible behavior**, the API
  reference has been updated.
- [ ] FAIL if: a new user-visible alert, banner, or modal is added without
  a corresponding update to the user guide.

---

## E. Quick Fail Conditions (any one of these → PR must be revised)

1. A required user-visible element surfaces only in a log panel, status bar,
   badge, or collapsed panel.
2. A required user-visible element requires the user to navigate before
   seeing it.
3. A user-visible warning can be turned off by default configuration.
4. A skipped-item summary lists items without reasons.
5. No automated test exercises the user-visible element in the foreground
   viewport.
6. A user-discoverable surface is used where §G.1 requires user-visible.
7. DW §6 documentation update is missing for a PR that adds user-visible
   behavior.

---

## F. Cross-References

| Document | Section | Relevance |
|---|---|---|
| `constitution.md` | §G.1 | Normative definition of user-visible |
| `constitution.md` | §G.2 | Normative definition of user-discoverable |
| `constitution.md` | §VI Portability | Skipped-item summary obligation |
| `constitution.md` | §15 Credential Reset | Offline warning obligation |
| `constitution.md` | Development Workflow §6 | Documentation Gate |
| `constitution.md` | §II Safety & Data Integrity | Dry-run visible UI element |
| `constitution.md` | Additional Constraints §5 | Dry-run surface coverage gate |
