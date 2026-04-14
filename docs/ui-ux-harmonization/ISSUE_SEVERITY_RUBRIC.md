# UI/UX Harmonization — Issue Severity Rubric

**Version 1.0 — April 2026**  
**Authority:** UI/UX Harmonization Specification v0.7 / Migration Guide v0.6 §3.6, §5.5  
**Usage:** Use this rubric to classify any issue found during Phase 3 implementation, Phase 4 verification, or post-integration monitoring.

The Critical level definition is normative for Guide §5.5 ("critical regression") purposes.

---

## Severity Levels

### Critical

**Definition:** An issue that prevents a user from launching or completing the tool's primary function, introduces an accessibility regression that creates a complete barrier for an assistive-technology user, or causes data loss or data corruption.

**Action required:** BLOCK RELEASE. The issue MUST be fixed and re-verified before any Phase 4 sign-off or Phase 5 deployment proceeds.

**Criteria (ANY one is sufficient):**
- Tool crashes or fails to launch
- A key action (as defined in `KEY_ACTIONS.md`) is completely unreachable
- Data is silently lost, overwritten, or corrupted
- An assistive-technology user (screen reader, keyboard-only) cannot complete the tool's primary function
- A security control is bypassed or a security-sensitive operation is exposed without confirmation

**RFU examples:**
- Secure Delete silently fails to delete files without informing the user
- The Duplicate Finder crashes when a scan directory is unmounted mid-scan
- A confirmation dialog is missing before an irreversible batch delete
- All focusable controls in a tool lose their accessible name after a theme switch
- Encryption dialog allows export of a private key with no confirmation step

---

### High

**Definition:** An issue that significantly degrades the experience for a user (including assistive-technology users) but does not completely block the primary function. The issue is likely to cause user confusion, errors, or effort.

**Action required:** FIX BEFORE PHASE 4 SIGN-OFF. Must be fixed and verified before the Phase 4 Reviewer Sign-off gate. MUST NOT ship to Phase 5 without resolution or an accepted deviation in `DEVIATIONS.md`.

**Criteria (ANY one is sufficient):**
- A key action is reachable but requires non-obvious or non-standard interaction
- Contrast ratio is below WCAG AA for standard text (< 4.5:1) or large text (< 3:1)
- An error message is unhelpful, non-actionable, or exposes a raw exception stack trace to the user
- A destructive action is missing a dry-run control (spec §5.2) but still has a confirmation dialog
- A loading state is missing, causing the UI to appear frozen for > 300 ms
- Keyboard navigation skips a significant set of controls
- The tool overrides a Hub theme token, causing a visible theming conflict

**RFU examples:**
- File Finder shows "AttributeError: 'NoneType' object has no attribute 'path'" to the user
- Size Analyzer has no progress indicator during a large directory scan
- Rename operation is missing a dry-run control (user cannot preview renames)
- Tab order in the Advanced Catalog skips the "Tag" input field
- A custom color in the Privacy tool causes 2.8:1 contrast ratio on mid-gray text

---

### Medium

**Definition:** An issue that causes a noticeable but non-blocking deviation from spec behavior or visual standards. Users can complete their tasks but will encounter friction or inconsistency.

**Action required:** FIX IN FOLLOW-UP. Must be added to the tool's `REMEDIATION_PLAN.md` with a target milestone. MAY be deferred to a follow-up release if a Phase 4 waiver is granted (documented in `DEVIATIONS.md`).

**Criteria (ANY one is sufficient):**
- A non-key action is unreachable by keyboard
- A component uses a custom alternative to a shared Hub component without a `DEVIATIONS.md` entry
- A label is placeholder-only (spec §5.3 violation) for a non-primary form field
- A button does not meet the 44×44 px minimum target size (spec §4.3)
- Typographic scale is not followed for a non-primary text element (wrong point size or weight)
- An accessible description is absent on a complex control that has an accessible name
- Animation does not respect the OS reduced-motion preference (but the animation is non-essential)
- A toast notification color does not map to the correct semantic token

**RFU examples:**
- The Metadata editor "Save" button is 36×28 px
- The Log Viewer uses a hard-coded font size of 9pt instead of `Typography.caption()`
- The Password Generator tooltip does not have `setAccessibleDescription()` set
- A secondary action button in the Network tool uses `#3498db` directly instead of `token("accent")`

---

### Low

**Definition:** A minor issue that does not affect function, accessibility, or compliance but represents a deviation from the spec, style guide, or project conventions.

**Action required:** NOTE AND TRACK. Record in `REMEDIATION_PLAN.md`. Fix opportunistically, or batch with the next scheduled maintenance pass. No release gate impact.

**Criteria (ANY one is sufficient):**
- Cosmetic styling inconsistency not covered by any mandatory spec rule
- A `KEY_ACTIONS.md` entry has an inaccurate keyboard path (the action is still reachable)
- Comment or documentation inconsistency in tool source
- A deprecated legacy color constant is still imported but not rendered
- Spacing deviation from the 8-point grid for a decorative element

**RFU examples:**
- The System Info tool uses 6 px padding instead of 8 px for a decorative icon
- A `KEY_ACTIONS.md` entry lists `Ctrl+R` as the refresh shortcut but the actual shortcut is `F5`
- `LightColors.ACCENT` is imported in the Organizer source but unused since token() was adopted

---

## Decision Tree

```
Is the tool's primary function completely broken, or is data at risk?
  └─ YES → Critical

Does it significantly damage usability or accessibility without blocking everything?
  └─ YES → High

Is it a noticeable but non-blocking spec deviation?
  └─ YES → Medium

Is it cosmetic, documentation, or minor?
  └─ YES → Low
```

---

## Classification Record (per review)

When filing an issue, include:

| Field | Value |
|---|---|
| Issue ID | *(sequential, e.g. `ISS-001`)* |
| Tool | *(tool name)* |
| Found during | *(Phase 3 / Phase 4 / post-integration)* |
| Severity | *(Critical / High / Medium / Low)* |
| Spec section | *(e.g. §5.2)* |
| Description | *(one sentence)* |
| Action | *(Block / Fix before sign-off / Follow-up / Note)* |
| Status | *(Open / In progress / Resolved)* |

---

*Rubric version 1.0. Critical definition is authoritative for Guide §5.5 "critical regression" purposes.*
