# PII Scan Result Delivery — UX Compliance Checklist

**Constitutional authority**: §VIII.X.1–§VIII.X.6  
**Canonical spec**: docs/pii-scan-ux-spec.md  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.28.0)  
**Last updated**: 2026-04-05  

Reviewers MUST verify all items before approving any PR that modifies PII
detection, background scanning, scan result display, or remediation
confirmation flows.

---

## Section A — Background & Scheduled Scans: Proactive Surfacing (§VIII.X.3)

- [ ] A.1  Background scan completion triggers proactive surfacing automatically — no user navigation required
- [ ] A.2  Scheduled scan completion triggers proactive surfacing automatically — treated identically to background scans
- [ ] A.3  Proactive surfacing uses one of the permitted patterns: persistent banner, notification badge, non-modal alert, or dashboard ribbon
- [ ] A.4  No modal dialog is used to deliver background or scheduled scan results
- [ ] A.5  No forced-focus overlay is used to deliver background or scheduled scan results
- [ ] A.6  Proactive surfacing appears in the active/foreground view — user cannot proceed without noticing it (satisfies §G.1 user-visible)
- [ ] A.7  When no PII is found, no spurious banner or badge is shown
- [ ] A.8  CI test T1 (background scan shows persistent banner) passes
- [ ] A.9  CI test T7 (scheduled scan triggers proactive surfacing) passes

---

## Section B — User-Initiated Scans: Inline Display (§VIII.X.2)

- [ ] B.1  User-initiated scan results are displayed inline within the scan panel or results view
- [ ] B.2  Inline display is immediate and visible within the context where the scan was triggered
- [ ] B.3  Proactive surfacing (banner, badge) is NOT required for user-initiated scans — inline display is sufficient
- [ ] B.4  A modal MAY be used for user-initiated scans only when it fits naturally in the wizard/step flow
- [ ] B.5  Results are not hidden behind a secondary navigation step for user-initiated scans
- [ ] B.6  CI test T2 (user-initiated scan shows inline results, not banner) passes

---

## Section C — Indicator Persistence (§VIII.X.5)

- [ ] C.1  Proactive surfacing indicators (banners, badges, ribbons) remain visible until the user explicitly acknowledges or reviews findings
- [ ] C.2  No auto-dismiss timer is applied to any background/scheduled scan indicator
- [ ] C.3  Transient toast notifications are NOT used as the sole delivery mechanism for background scan results
- [ ] C.4  After the user clicks "Review findings" or equivalent, the indicator is dismissed — but only at that point
- [ ] C.5  CI test T4 (banner persists until acknowledged) passes

---

## Section D — No Automatic PII Deletion & Remediation Confirmation (§VIII.X.4)

- [ ] D.1  PII is NEVER deleted automatically by any background, scheduled, or system process
- [ ] D.2  Remediation (deletion or anonymization) requires explicit user confirmation regardless of scan type
- [ ] D.3  The confirmation action is a deliberate user gesture (click, checkbox, or typed phrase) — not a passive timeout
- [ ] D.4  Irreversible remediation operations additionally use the two-step confirmation (type phrase + click confirm) per §VIII
- [ ] D.5  No "auto-clean" or "silent cleanup" code path exists in background scan handlers
- [ ] D.6  CI test T5 (remediation requires explicit confirmation) passes
- [ ] D.7  CI test T6 (no automatic PII deletion after scan) passes

---

## Section E — Accessibility & Non-Coercion (§VIII.X.3, §VIII.X.6)

- [ ] E.1  Proactive surfacing does NOT block the user's current workflow (no modals, no forced focus)
- [ ] E.2  Banner/badge/ribbon indicators carry accessible labels (ARIA or Qt accessibility text)
- [ ] E.3  Indicators meet WCAG AA contrast requirements (§7 Accessibility: ≥ 4.5:1 for standard text, ≥ 3:1 for non-text components)
- [ ] E.4  Banner/badge is compatible with screen reader announcement (auto-announced without user focus)
- [ ] E.5  Reduced-motion OS preference is respected by any animated indicator elements

---

## Section F — Test Coverage and CI Gate (§VIII.X.6)

- [ ] F.1  CI tests T1–T8 (as defined in docs/pii-scan-ux-spec.md §8) are implemented and passing
- [ ] F.2  CI pipeline includes tests T1–T8 as a **required gate** (not optional or skippable)
- [ ] F.3  Tests cover both scan origins: USER_INITIATED and BACKGROUND/SCHEDULED
- [ ] F.4  Tests verify persistence of indicators (no auto-dismiss)
- [ ] F.5  Tests verify absence of modals for background scan delivery
- [ ] F.6  Tests verify no automatic deletion occurs after scan
- [ ] F.7  No existing scan or detection test has been weakened to accommodate UI changes
- [ ] F.8  CI test T8 (empty results suppress banner) passes — no false proactive surfacing

---

## Notes

- The distinction between user-initiated and background/scheduled scans is based on **scan origin**, not scan result severity. Even a single low-confidence finding from a background scan MUST trigger proactive surfacing.
- "Proactive surfacing" satisfies the §G.1 user-visible definition — it appears automatically in the foreground viewport without requiring navigation.
- For user-initiated scans, §G.2 user-discoverable (inline panel) is sufficient.
- If a background scan produces no findings, no indicator should appear — spurious alerts degrade trust.

---

## Cross-References

| Reference | Location |
|-----------|----------|
| Canonical spec | docs/pii-scan-ux-spec.md |
| Constitutional authority | §VIII.X.1–§VIII.X.6 (.specify/memory/constitution.md) |
| Q15 answer | .specify/memory/constitution_clairification_uiux_harmonny_r8.md §Q15 |
| UI/UX visibility definitions (§G.1, §G.2) | .specify/memory/checklist-uiux-visibility-compliance.md |
| Audit origin metadata checklist | .specify/memory/checklist-audit-origin-metadata-compliance.md |
| is_protected checklist | .specify/memory/checklist-is-protected-compliance.md |
| HMAC token checklist | .specify/memory/checklist-hmac-token-compliance.md |
