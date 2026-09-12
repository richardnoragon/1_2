# UI/UX Harmonization P4 UAT Scenarios

**Status:** Shared UAT scenario record  
**Date:** 2026-09-11  
**Scope:** shared acceptance scenarios for the Phase 4 verification gate. These scenarios cover the shared UI surfaces modernized in issue #81 and the hub-launched utility window pattern.

## Scenario Set

### UAT-01 Keyboard-only primary workflow

**Covers:** issue #31

**Pre-conditions:**
- RFU is running.
- A hub-launched tool window is open.
- Mouse input is not used.

**Expected outcome:**
- The primary workflow can be completed using `Tab`, `Shift+Tab`, arrow keys, and `Enter` only.
- No keyboard trap occurs and the visible focus indicator remains clear.

### UAT-02 Windows Narrator primary workflow

**Covers:** issue #32

**Pre-conditions:**
- RFU is running with Windows Narrator enabled.
- A hub-launched tool window is open.

**Expected outcome:**
- Narrator announces the active control, the primary action, and the resulting status text during the workflow.
- The user can complete the primary workflow without relying on visual-only cues.

### UAT-03 NVDA primary workflow

**Covers:** issue #33

**Pre-conditions:**
- RFU is running with NVDA enabled.
- A hub-launched tool window is open.

**Expected outcome:**
- NVDA announces the active control, the primary action, and the resulting status text during the workflow.
- The user can complete the primary workflow without relying on visual-only cues.

### UAT-04 High-contrast mode readability

**Covers:** issue #34

**Pre-conditions:**
- RFU is running with the operating system high-contrast theme enabled.
- A hub-launched tool window is open.

**Expected outcome:**
- Primary text, labels, and actionable controls remain readable.
- The workflow remains functional and no text becomes visually indistinguishable from its background.

### UAT-05 Color-blind simulation resilience

**Covers:** issue #35

**Pre-conditions:**
- RFU is running in a common color-blind simulation mode or equivalent visual filter.
- A hub-launched tool window is open.

**Expected outcome:**
- Meaning is not conveyed by color alone.
- Key statuses, warnings, and primary actions remain distinguishable by text, iconography, or structure.

### UAT-06 Fatal error surface

**Covers:** issue #26

**Pre-conditions:**
- RFU is running.
- A hub-launched tool window is open.
- A fatal error path is triggered in a controlled way.

**Expected outcome:**
- `HubErrorScreen` appears in place of the crashed surface.
- The error code is not shown to the user as the primary message.

### UAT-07 Non-fatal error surface

**Covers:** issue #27

**Pre-conditions:**
- RFU is running.
- A hub-launched tool window is open.
- A non-fatal validation or runtime error is triggered in a controlled way.

**Expected outcome:**
- The tool shows an inline, user-friendly error message.
- `HubErrorScreen` does not appear for the non-fatal path.

### UAT-08 Empty state behavior

**Covers:** issue #28

**Pre-conditions:**
- RFU is running.
- The selected tool has no data to show for the current view or filter.

**Expected outcome:**
- The empty state is explicit and user-friendly.
- The tool remains usable and does not present a blank or broken panel.

### UAT-09 Zoom resilience

**Covers:** issue #29

**Pre-conditions:**
- RFU is running.
- The operating system or application is zoomed to 200%.

**Expected outcome:**
- The tool remains functional at 200% zoom.
- Core controls remain reachable and the layout does not collapse into unusable overlap.

## Notes

- Issues #30, #31, #32, #33, #34, #35 are represented here as shared acceptance scenarios rather than per-tool checks.
- Issues #24 and #25 are covered by the same shared accessibility verification record because the shared UI surfaces already enforce the common focus, contrast, and screen-reader baseline used by the tool windows.
- This document is the repo evidence for the Phase 4 UAT gate and should be referenced alongside the verification and compliance summaries.