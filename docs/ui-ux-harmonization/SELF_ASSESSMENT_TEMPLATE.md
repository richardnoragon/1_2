# UI/UX Harmonization — Compliance Self-Assessment Template

**Version 1.0 — April 2026**  
**Authority:** UI/UX Harmonization Specification v0.7 / Migration Guide v0.6 §1.2  
**Usage:** Complete one copy of this template per tool before Phase 3 migration begins.  
Store the completed copy at `docs/ui-ux-harmonization/{tool-name}/ASSESSMENT.md`.

---

## Tool Information

| Field | Value |
|---|---|
| **Tool name** | *(fill in)* |
| **Tool directory** | *(e.g. `src/utilities/file_management/`)* |
| **Assessor** | *(fill in)* |
| **Assessment date** | *(fill in)* |
| **Spec version assessed against** | v0.7 |

---

## How to Mark

Mark each item **exactly once** using the following values:

| Mark | Meaning |
|---|---|
| `[C]` | **Compliant** — item fully satisfies the spec requirement |
| `[N]` | **Non-compliant** — item does not satisfy the spec; record a finding below the checklist |
| `[A]` | **Not applicable** — this tool has no surface to satisfy this item; record brief justification |

Every `[N]` item MUST become a remediation entry in `REMEDIATION_PLAN.md`.  
Every `[A]` item MUST have a one-line justification.

---

## Section 1 — Screens & User Flows

*Spec §3.3, §5. Does the tool expose all flows through a navigable, predictable interface?*

**Instructions:** For each distinct screen or major flow the tool supports, confirm it is documented and reachable without hidden states.

- [ ] `[C]` / `[N]` / `[A]` — All major screens are documented in the inventory
- [ ] `[C]` / `[N]` / `[A]` — No hidden or undiscoverable flows (unreachable by keyboard)
- [ ] `[C]` / `[N]` / `[A]` — Screen transitions are predictable and reversible
- [ ] `[C]` / `[N]` / `[A]` — Empty states are handled gracefully (not blank or crashing)
- [ ] `[C]` / `[N]` / `[A]` — Loading/progress states are visible to the user (no silent waits > 300 ms)

**Findings (required for each `[N]`):**

*(none)*

---

## Section 2 — Components

*Spec §7. Does the tool use Hub-approved shared components where they are available?*

**Instructions:** Check each shared component type against what the tool uses. If the tool uses a custom alternative, it must be documented in `DEVIATIONS.md`.

- [ ] `[C]` / `[N]` / `[A]` — **Buttons:** `PrimaryButton`, `SecondaryButton`, `DestructiveButton` from `src.gui.components.buttons` (or documented deviation)
- [ ] `[C]` / `[N]` / `[A]` — **Text Inputs:** `TextInput` from `src.gui.components.inputs` (or documented deviation)
- [ ] `[C]` / `[N]` / `[A]` — **Modals:** `Modal` / `ConfirmationModal` from `src.gui.components.modal` (or documented deviation)
- [ ] `[C]` / `[N]` / `[A]` — **Toast Notifications:** `ToastNotification` from `src.gui.components.toast` (or documented deviation)
- [ ] `[C]` / `[N]` / `[A]` — **Breadcrumbs:** `Breadcrumb` from `src.gui.components.breadcrumb` where local navigation is present (or documented deviation)
- [ ] `[C]` / `[N]` / `[A]` — **Loading Indicators:** `LoadingIndicator` from `src.gui.components.loading_indicator` (or documented deviation)
- [ ] `[C]` / `[N]` / `[A]` — **Error Screen:** `HubErrorScreen` wired for fatal errors (via `UtilityWindow` — auto-covered by P1-C16)
- [ ] `[C]` / `[N]` / `[A]` — No undocumented custom alternatives to any of the above

**Findings:**

*(none)*

---

## Section 3 — Theming

*Spec §4.1, §4.2. Does the tool use Hub tokens for all color and font values?*

**Instructions:** Review all `.py` files in the tool directory. Any hard-coded hex color (`#XXXXXX`) or bare `QFont()` call with explicit family/size is non-compliant.

- [ ] `[C]` / `[N]` / `[A]` — No hard-coded hex color values in tool source files
- [ ] `[C]` / `[N]` / `[A]` — All colors resolved via `token(key)` from `src.gui.themes`
- [ ] `[C]` / `[N]` / `[A]` — No bare `QFont(family, size)` calls — all fonts via `Typography.*()` or `Fonts.*`
- [ ] `[C]` / `[N]` / `[A]` — Tool visually correct in **light** mode (verified manually or by smoke test)
- [ ] `[C]` / `[N]` / `[A]` — Tool visually correct in **dark** mode (verified manually or by smoke test)
- [ ] `[C]` / `[N]` / `[A]` — Reserved `hub_nav_*` tokens are NOT referenced in tool source

**Findings:**

*(none)*

---

## Section 4 — Navigation

*Spec §5.1. Does the tool avoid implementing its own global navigation?*

**Instructions:** Global navigation = any menu bar, sidebar, or nav panel that replicates the Hub's navigation chrome. Local navigation (tool-internal tabs, breadcrumbs, sub-panels) is permitted.

- [ ] `[C]` / `[N]` / `[A]` — Tool does NOT implement its own global menu bar (note: `UtilityWindow` menubar-clone is covered by project-wide DEV-002 and need not be recorded per-tool)
- [ ] `[C]` / `[N]` / `[A]` — Local navigation (if any) does not visually compete with Hub navigation
- [ ] `[C]` / `[N]` / `[A]` — Local navigation uses Hub-provided components (`Breadcrumb`, tabs) where available
- [ ] `[C]` / `[N]` / `[A]` — Tool does NOT alter Hub window geometry, size, or position

**Findings:**

*(none)*

---

## Section 5 — Accessibility

*Spec §6. Does the tool meet WCAG 2.1 AA and Qt accessibility requirements?*

**Instructions:** Use automated tooling (configured in `AUTOMATED_TOOLING.md`) as a first pass, then manually verify the items below.

- [ ] `[C]` / `[N]` / `[A]` — All interactive controls have `setAccessibleName()` set
- [ ] `[C]` / `[N]` / `[A]` — Complex controls also have `setAccessibleDescription()` set
- [ ] `[C]` / `[N]` / `[A]` — All text meets WCAG AA contrast (≥4.5:1 standard, ≥3:1 large text)
- [ ] `[C]` / `[N]` / `[A]` — All non-text UI components meet ≥3:1 contrast
- [ ] `[C]` / `[N]` / `[A]` — Full keyboard navigability — every action reachable by Tab + Enter/Space
- [ ] `[C]` / `[N]` / `[A]` — No keyboard traps
- [ ] `[C]` / `[N]` / `[A]` — Visible focus indicators on all focusable elements
- [ ] `[C]` / `[N]` / `[A]` — UI tested at 200% zoom — no truncation or layout breakage
- [ ] `[C]` / `[N]` / `[A]` — OS reduced-motion preference respected (no forced animations)
- [ ] `[C]` / `[N]` / `[A]` — Basic screen reader spot-check passed (Windows Narrator or NVDA)

**Findings:**

*(none)*

---

## Section 6 — Error Handling

*Spec §8 (referenced), Guide §3.3. Does the tool handle errors in a user-friendly, accessible way?*

**Instructions:** Trigger each known error path (invalid input, missing file, permissions error) and verify the error presentation.

- [ ] `[C]` / `[N]` / `[A]` — Errors are displayed to the user in plain language (no raw exception text)
- [ ] `[C]` / `[N]` / `[A]` — Error messages are actionable and specific (spec §5.3)
- [ ] `[C]` / `[N]` / `[A]` — Error code / technical detail is logged internally, NOT shown to user
- [ ] `[C]` / `[N]` / `[A]` — Fatal errors show `HubErrorScreen` with Retry and Go to Hub options
- [ ] `[C]` / `[N]` / `[A]` — Validation errors appear inline (not as separate modal dialogs)
- [ ] `[C]` / `[N]` / `[A]` — Error states are accessible (accessible name/description set on error elements)
- [ ] `[C]` / `[N]` / `[A]` — Destructive operations require explicit confirmation (`ConfirmationModal` or equivalent)

**Findings:**

*(none)*

---

## Section 7 — Telemetry & Logging

*Spec §9.3, DEV-001. Does the tool emit required telemetry events with correct fields?*

**Instructions:** Review logging calls. UI telemetry events are governed by DEV-001 (exempt from `device_id` and `app_instance_id`). Identity events are NOT exempt.

- [ ] `[C]` / `[N]` / `[A]` — `ui_view_load` event emitted when tool is opened
- [ ] `[C]` / `[N]` / `[A]` — `ui_user_action` event emitted for each key user action
- [ ] `[C]` / `[N]` / `[A]` — `ui_error_event` emitted when an error is shown to user
- [ ] `[C]` / `[N]` / `[A]` — All events include: `actor_username`, `session_id`, `timestamp`, `event_type`, `tool_id`
- [ ] `[C]` / `[N]` / `[A]` — No raw PII in any log or telemetry field
- [ ] `[C]` / `[N]` / `[A]` — Log retention for UI events ≤ 30 days (per DEV-001)

**Findings:**

*(none)*

---

## Section 8 — Key Actions

*Spec §7 / Constitution §7. Is the tool's `KEY_ACTIONS.md` created and accurate?*

**Instructions:** Open `docs/ui-ux-harmonization/{tool-name}/KEY_ACTIONS.md` and verify each action listed is reachable by keyboard and matches the tool's current UI.

- [ ] `[C]` / `[N]` / `[A]` — `KEY_ACTIONS.md` exists at the canonical path
- [ ] `[C]` / `[N]` / `[A]` — Each key action has a named keyboard shortcut or tab-navigation path
- [ ] `[C]` / `[N]` / `[A]` — Side-effect actions (irreversible, multi-file, security) are marked as such
- [ ] `[C]` / `[N]` / `[A]` — Every key action that has side effects has a corresponding dry-run or confirmation control (spec §5.2)
- [ ] `[C]` / `[N]` / `[A]` — Key actions list matches the tool's current feature set (no stale entries)

**Findings:**

*(none)*

---

## Summary

| Section | # Compliant | # Non-compliant | # N/A |
|---|---|---|---|
| 1 — Screens & Flows | | | |
| 2 — Components | | | |
| 3 — Theming | | | |
| 4 — Navigation | | | |
| 5 — Accessibility | | | |
| 6 — Error Handling | | | |
| 7 — Telemetry | | | |
| 8 — Key Actions | | | |
| **Total** | | | |

**Overall readiness:** `[ ]` Ready for Phase 3 (all Non-compliant items have remediation entries)  
**Assessor sign-off:** *(name, date)*

---

*Template version 1.0. Do not modify this template file. Copy it to the tool's directory as `ASSESSMENT.md` and fill in.*
