# UI/UX Harmonization — UAT Scenario Template

**Version 1.0 — April 2026**  
**Authority:** UI/UX Harmonization Migration Guide v0.6 §4.3  
**Usage:**  
1. Copy this template to `docs/ui-ux-harmonization/{tool-name}/UAT_SCENARIOS.md`.  
2. Add one scenario block per key user flow (derived from the Phase 1.1 user-flow inventory and `KEY_ACTIONS.md`).  
3. Fill in expected outcome precisely enough that pass/fail is deterministic — no ambiguity allowed.

---

## Scenario Record Format

Each scenario uses the block structure below. Do NOT abbreviate fields.

---

### Scenario Template Block

```
---
**Scenario ID:** {TOOL-NNN}
**Tool:** {Tool Name}
**Category:** {Functional | Accessibility | Theming | Error handling | Navigation}
**Priority:** {Critical | High | Medium}

**Pre-conditions:**
- (List every required setup step. E.g. "Application is running", "A directory containing ≥1 .txt file exists at a known path".)

**Steps:**
1. (Numbered, discrete user actions. E.g. "Click the Browse button.")
2. ...

**Expected outcome:**
(Single, unambiguous statement. Must be verifiable with a yes/no answer.)
(E.g. "The results list shows exactly the files matching *.txt in the specified directory, sorted by name ascending.")

**Actual outcome:**
(Filled in during test execution. Leave blank until tested.)

**Pass / Fail:** [ ] Pass  [ ] Fail

**Tester:** *(name, date)*

**Notes:**
(Optional. Record any unexpected behaviour, environment notes, or issue IDs.)
---
```

---

## Worked Example Scenario

The following is a complete, filled-in example for the **File Finder** tool. It demonstrates a keyboard-accessibility scenario derived from the Phase 1.1 user-flow inventory.

---

**Scenario ID:** FINDER-001  
**Tool:** File Finder  
**Category:** Accessibility  
**Priority:** Critical

**Pre-conditions:**
- RFU application is running and the File Finder tool is open.
- A test directory exists at a known path that contains at least three `.log` files and two `.txt` files.
- No mouse is used during this scenario (keyboard-only).

**Steps:**
1. Press `Tab` until the **Search Directory** field is focused (visible focus indicator present).
2. Type the known test directory path.
3. Press `Tab` to move to the **File Extension** field.
4. Type `.log`.
5. Press `Tab` to move to the **Search** button.
6. Press `Enter` to trigger the search.
7. Wait for results to appear (loading indicator MUST show if search takes > 300 ms).
8. Confirm screen reader announces the result count (Windows Narrator or NVDA).
9. Press `Tab` to navigate through the results list.

**Expected outcome:**  
The results list displays exactly three files (all `.log` files from the test directory). The screen reader announces "3 results found" or equivalent. Every interactive element (fields, button, results) was reachable without a mouse. No keyboard trap occurred.

**Actual outcome:**  
*(fill in during test)*

**Pass / Fail:** [ ] Pass  [ ] Fail

**Tester:** *(name, date)*

**Notes:**  
*(none)*

---

## Scenario Writing Guidelines

| Guideline | Details |
|---|---|
| **One expected outcome per scenario** | Split complex scenarios. One scenario = one verifiable assertion. |
| **Derive from KEY_ACTIONS.md** | Every key action listed in `KEY_ACTIONS.md` MUST have at least one covering scenario. |
| **Side-effects need dry-run coverage** | Any action marked as having side effects in `KEY_ACTIONS.md` MUST have a separate scenario verifying the dry-run or confirmation control exists and is reachable by keyboard. |
| **Accessibility scenarios are mandatory** | Every tool MUST have at least one keyboard-only scenario and one screen-reader scenario. |
| **Theming scenarios are mandatory** | At least one scenario per tool MUST verify correct rendering after `apply_theme("dark")` is called. |
| **Error-handling scenarios are mandatory** | At least one scenario MUST trigger an error path and verify the error display is user-friendly and accessible. |
| **Expected outcome must be deterministic** | Avoid "should look correct" — state the exact verifiable condition (count, text, widget state, focus position). |

---

*Template version 1.0. Copy to tool directory as `UAT_SCENARIOS.md` and add scenario blocks.*
