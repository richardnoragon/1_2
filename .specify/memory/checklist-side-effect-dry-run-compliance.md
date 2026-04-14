# Checklist: Side-Effect & Dry-Run Compliance

**Governs**: §II.1–§II.4, §G.3, §G.4, §VI.1–§VI.3  
**Introduced**: Round 8 — Q2 (2026-04-03)  
**Companion checklist**: [checklist-uiux-visibility-compliance.md](checklist-uiux-visibility-compliance.md)

This checklist is for PR reviewers and authors. Every PR that introduces or
modifies an operation must be assessed against each section. A PR MUST NOT
merge until all applicable items are checked. Items marked **[CI]** MUST also
be enforced by automated tests.

---

## Section A — Operation Classification

Before applying any other section of this checklist, classify every new or
modified operation.

| Classification Question | Yes | No | N/A |
|---|---|---|---|
| A1. Does the operation produce any persistent change to user-visible state (file creation/deletion/modification, metadata mutation, external write)? If **Yes** → Tier 1 Side-effect (§G.3). | | | |
| A2. If A1 = Yes: is the change irreversible or hard to reverse (delete, overwrite, secure wipe, anonymization, lossy transformation)? If **Yes** → Tier 2 Destructive (§G.4). | | | |
| A3. If A1 = No: does the operation write only to RFU-internal structures (indexes, caches, audit logs) with no user-visible effect? If **Yes** → Internal operation (§II.3); skip Sections B, C, and D. | | | |
| A4. Does the PR description explicitly state the operation's classification (side-effect / destructive / internal)? | | | |

**Classification table for this PR:**

| Operation Name | Tier 1 (§G.3)? | Tier 2 (§G.4)? | Internal (§II.3)? |
|---|---|---|---|
| *(list each operation)* | | | |

---

## Section B — Dry-run Compliance (§G.3 / §II.1)

*Required for all Tier 1 and Tier 2 operations. Skip for Internal operations.*

| Item | Checked | [CI] |
|---|---|---|
| B1. A dry-run execution path exists and is reachable through the same interface as the real operation. | | ✓ |
| B2. Dry-run enumerates all intended changes to user-visible state without performing them. | | ✓ |
| B3. Dry-run presents a user-visible summary (§G.1) of all intended modifications. | | ✓ |
| B4. Dry-run presents a user-visible summary (§G.1) of all skipped items and the reason each was skipped (§VI.1). | | ✓ |
| B5. Skipped items are listed separately from intended changes in the dry-run report (§VI.2). | | ✓ |
| B6. The dry-run capability is visible in the tool's UI before the user initiates the real operation — documentation-only discoverability is insufficient (§II.1). | | ✓ |
| B7. The dry-run summary is structured such that reviewers can verify its presence via DOM or widget-tree inspection (§VI.3). | | ✓ |
| B8. The dry-run summary format is consistent with all other apps in the suite (§VI.3). | | |

---

## Section C — Confirmation Compliance (§G.4 / §II.2)

*Required for all Tier 2 (Destructive) operations only. Skip for Tier 1 and Internal operations.*

| Item | Checked | [CI] |
|---|---|---|
| C1. An explicit user-visible confirmation is required before the destructive operation executes. | | ✓ |
| C2. The confirmation blocks execution until the user explicitly approves — no auto-dismiss, no timeout approval (§II.2). | | ✓ |
| C3. The confirmation appears in a foreground, non-dismissed UI surface (§II.2, §G.1). | | ✓ |
| C4. The confirmation summarizes the irreversible consequences of the operation (§II.2). | | ✓ |
| C5. The confirmation lists all affected items (§II.2). | | ✓ |
| C6. If this is an irreversible anonymization operation: the elevated two-step confirmation (typed phrase + button click) defined in §VIII is used, NOT just a single step (§VIII). | | |
| C7. If this is any other destructive operation: a single explicit confirmation step is used (NOT the §VIII two-step) (§II). | | |
| C8. In headless mode (CLI without interactive GUI): a cryptographically signed HMAC token is required; a plain long-form flag is NOT accepted (§II). | | ✓ |

---

## Section D — Internal Operation Exclusion Check (§II.3)

*Required for any operation the author claims is "Internal" (Section A3 = Yes).*

| Item | Checked |
|---|---|
| D1. The operation writes ONLY to RFU-internal structures (indexes, caches, audit logs). | |
| D2. No user-visible state is changed — the user cannot observe the write directly in any UI surface. | |
| D3. The operation has NOT been classed as requiring dry-run or confirmation on this basis. | |
| D4. At least one other reviewer has independently agreed the operation is internal-only and signed off on Section A3. | |

**Note**: If any doubt exists about classification, default to Tier 1 (side-effect). Misclassifying a side-effect operation as internal is a §II.4 CI gate failure.

---

## Section E — CI Enforcement (§II.4)

| Item | [CI] |
|---|---|
| E1. CI test verifies that the dry-run path exists and is exercisable for each Tier 1/Tier 2 operation in this PR. | ✓ |
| E2. CI test verifies that the confirmation gate exists and is non-bypassable for each Tier 2 operation. | ✓ |
| E3. CI test verifies that internal operations do not expose a dry-run or confirmation path. | ✓ |
| E4. CI test verifies that the skipped-item summary (§VI.1) is present in the active foreground viewport via widget-tree or DOM inspection after a dry-run with at least one skipped item. | ✓ |
| E5. CI test verifies that skipped items appear separately from the intended-changes list in dry-run output (§VI.2). | ✓ |

---

## Section F — Cross-references

| Section in this checklist | Governing constitution reference |
|---|---|
| A — Operation Classification | §G.3 Side effect, §G.4 Destructive operation, §II.3 |
| B — Dry-run Compliance | §II.1, §G.3, §G.1, §VI.1, §VI.2, §VI.3 |
| C — Confirmation Compliance | §II.2, §G.4, §G.1, §VIII |
| D — Internal Operation Exclusion | §II.3 |
| E — CI Enforcement | §II.4, §VI.3 |

**Related checklists**:
- [checklist-uiux-visibility-compliance.md](checklist-uiux-visibility-compliance.md) — §G.1 / §G.2 user-visible and user-discoverable surface compliance

---

## Reviewer Sign-off

```
PR: ___________________________
Reviewer: _____________________
Date: _________________________

Section A classification confirmed: [ ]
Section B dry-run compliance: [ ] Applicable  [ ] N/A (all internal)
Section C confirmation compliance: [ ] Applicable  [ ] N/A (no destructive ops)
Section D internal exclusion review: [ ] Applicable  [ ] N/A
Section E CI gates passing: [ ]

Signature: ____________________
```
