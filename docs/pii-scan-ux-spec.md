# PII Scan Result Delivery — Canonical Specification

**Constitutional authority**: §VIII.X.1–§VIII.X.6  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.28.0)  
**Last updated**: 2026-04-05  

---

## 1. Purpose

§VIII requires that PII detection results "MUST be reported to the user
without automatic deletion; remediation requires explicit user confirmation."
This specification defines the **delivery mechanism** for those results,
resolving the ambiguity between proactive surfacing and user-accessible
placement.

The core principle: **PII findings MUST NOT be silently ignorable.** The
delivery model differs by scan origin — user-initiated vs.
background/scheduled.

**See also**:  
- [.specify/memory/checklist-pii-scan-ux-compliance.md](../.specify/memory/checklist-pii-scan-ux-compliance.md) — reviewer checklist  
- [.specify/memory/constitution.md](../.specify/memory/constitution.md) — §VIII, §VIII.X  
- [.specify/memory/constitution_clairification_uiux_harmonny_r8.md](../.specify/memory/constitution_clairification_uiux_harmonny_r8.md) — round-8 Q15 answer  

---

## 2. Scan Type Delivery Matrix

| Scan Type | Proactive Surfacing Required? | Allowed Delivery Patterns | Modals Permitted? |
|-----------|------------------------------|--------------------------|-------------------|
| User-initiated | NO | Inline panel, results view | YES (user already engaged) |
| Background / scheduled | YES (MUST) | Persistent banner, notification badge, non-modal alert, dashboard ribbon | NO |

---

## 3. User-Initiated Scans (§VIII.X.2)

When a user explicitly triggers a PII scan:

- Results **MAY** be displayed inline within the scan panel or results view.
- The user is already engaged, expecting results, and context is clear.
- Proactive surfacing (banner, badge) is **NOT required**.
- A modal **MAY** be used only if the user explicitly triggered a
  workflow that naturally culminates in a modal (e.g., a dedicated
  "Scan now" wizard step).

### 3.1 Minimum Inline Display Requirements

Inline results MUST include:

- Total count of PII findings
- Per-finding: file path (sanitized), PII type (e.g., "email address",
  "national ID"), confidence level
- Clear remediation action(s) with explicit confirmation required before
  any change is applied

---

## 4. Background and Scheduled Scans (§VIII.X.3)

When PII detection runs automatically (scheduled, background daemon,
triggered by file-system watcher):

### 4.1 Proactive Surfacing — REQUIRED

Results **MUST** be surfaced proactively when detection completes. The user
MUST NOT need to navigate to a separate location to discover that findings
exist.

### 4.2 Permitted Delivery Patterns

Any of the following satisfy the proactive-surfacing requirement:

| Pattern | Description | Persistence Requirement |
|---------|-------------|------------------------|
| Persistent banner | Full-width or prominent banner in the main RFU hub viewport | MUST remain until user acknowledges |
| Notification badge | Badge on PII/security section with count of findings | MUST remain until user reviews |
| Non-modal alert | Alert panel that appears in the active view without blocking workflow | MUST remain until user acknowledges |
| Dashboard ribbon | Highlighted ribbon on the RFU dashboard tile for the relevant tool | MUST remain until user reviews |

### 4.3 Forbidden Delivery Patterns

The following MUST NOT be used for background/scheduled PII scan results:

| Pattern | Reason Forbidden |
|---------|-----------------|
| Modal dialog | Interrupts workflow; coercive; violates §VIII.X.3 |
| Forced-focus overlay | Blocks user activity; dark-pattern risk |
| Transient auto-dismissing toast | Disappears before user can act; violates §VIII.X.5 |
| Log-only / silent | User may never see; violates §VIII constitutional "reported" requirement |
| Navigation-required panel | Requires user to know findings exist to find them |

### 4.4 Indicator Persistence (§VIII.X.5)

Proactive surfacing indicators (all types above) MUST remain visible until
the user explicitly:

- Clicks "Review findings", OR
- Dismisses the indicator after viewing results

**Auto-dismissal after a timeout is PROHIBITED for background scan PII findings.**

---

## 5. User Agency and Remediation (§VIII.X.4)

Regardless of scan type:

- **PII MUST NOT be deleted automatically.** No background process may
  remove files, scrub content, or apply anonymization without user action.
- **Remediation requires explicit user confirmation.** The minimum
  acceptable confirmation is a deliberate user action — click, checkbox,
  or typed phrase — performed after the user has reviewed the findings.
- Irreversible remediation operations additionally require the two-step
  confirmation defined in §VIII (type phrase + click confirm).

---

## 6. Relationship to §G.1 (User-Visible) and §G.2 (User-Discoverable)

| Concept | Maps to |
|---------|---------|
| Background scan proactive surfacing | §G.1 **User-visible** — must appear in foreground without navigation |
| User-initiated scan inline display | §G.2 **User-discoverable** — already in active context |

Persistent banners and notification badges that appear automatically satisfy
§G.1 for background scan results. A panel behind a navigation step satisfies
§G.2 only, which is insufficient for background scans.

---

## 7. Reference Implementation

### 7.1 Background Scan Completion Handler

```python
from enum import Enum
from dataclasses import dataclass
from typing import List


class ScanOrigin(Enum):
    USER_INITIATED = "user_initiated"
    BACKGROUND = "background"
    SCHEDULED = "scheduled"


@dataclass
class PIIFinding:
    file_path: str          # sanitized (no shell metacharacters)
    pii_type: str           # e.g., "email_address", "national_id"
    confidence: float       # 0.0–1.0
    line_number: int | None = None


def on_scan_complete(
    findings: List[PIIFinding],
    origin: ScanOrigin,
    hub_controller,
) -> None:
    """
    Called when any PII scan completes.
    Delivers results per §VIII.X delivery requirements.
    """
    if not findings:
        return  # No findings — no surfacing required

    if origin == ScanOrigin.USER_INITIATED:
        # Inline display in scan panel — proactive surfacing not required
        hub_controller.display_inline_results(findings)
    else:
        # Background or scheduled — MUST surface proactively (§VIII.X.3)
        # MUST NOT use modal; MUST persist until acknowledged
        hub_controller.show_persistent_pii_banner(
            finding_count=len(findings),
            on_review_callback=lambda: hub_controller.display_inline_results(findings),
        )
```

### 7.2 Persistent Banner Widget (PyQt5 skeleton)

```python
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt


class PIIAlertBanner(QWidget):
    """
    Non-modal, persistent banner for background PII scan results.
    MUST NOT auto-dismiss. Satisfies §VIII.X.3 and §VIII.X.5.
    """

    def __init__(self, finding_count: int, on_review, parent=None):
        super().__init__(parent)
        self._on_review = on_review
        self._build_ui(finding_count)

    def _build_ui(self, finding_count: int) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        icon = QLabel("⚠")  # replace with accessible icon resource
        icon.setAccessibleName("Warning")
        layout.addWidget(icon)

        msg = QLabel(
            f"PII detected: {finding_count} finding(s) require review."
        )
        msg.setAccessibleName("PII detection alert")
        layout.addWidget(msg, stretch=1)

        review_btn = QPushButton("Review findings")
        review_btn.setAccessibleName("Review PII findings")
        review_btn.clicked.connect(self._handle_review)
        layout.addWidget(review_btn)

        # No auto-close timer — banner persists until explicitly dismissed

    def _handle_review(self) -> None:
        self._on_review()
        self.setVisible(False)   # Only hidden after user action
```

---

## 8. CI Tests

### T1 — Background scan surfaces banner automatically

```python
def test_background_scan_shows_persistent_banner(mock_hub, pii_scanner):
    """Background scan completion must trigger proactive banner, not modal."""
    findings = [PIIFinding("docs/report.txt", "email_address", 0.95)]
    on_scan_complete(findings, ScanOrigin.BACKGROUND, mock_hub)
    assert mock_hub.show_persistent_pii_banner.called
    assert not mock_hub.show_modal.called
```

### T2 — User-initiated scan shows inline results

```python
def test_user_initiated_scan_shows_inline_results(mock_hub, pii_scanner):
    """User-initiated scan must surface results inline, not via banner."""
    findings = [PIIFinding("notes.txt", "phone_number", 0.88)]
    on_scan_complete(findings, ScanOrigin.USER_INITIATED, mock_hub)
    assert mock_hub.display_inline_results.called
    assert not mock_hub.show_persistent_pii_banner.called
```

### T3 — No modal triggered for background scan

```python
def test_no_modal_for_background_scan(mock_hub, pii_scanner):
    """Modal MUST NOT be used for background scan result delivery."""
    findings = [PIIFinding("archive.zip", "national_id", 0.91)]
    on_scan_complete(findings, ScanOrigin.BACKGROUND, mock_hub)
    assert not mock_hub.show_modal.called
    assert not mock_hub.show_forced_focus_overlay.called
```

### T4 — Banner persists until user acknowledges

```python
def test_banner_persists_until_acknowledged(qtbot, finding_count=3):
    """Banner must not auto-dismiss; must remain until user acts."""
    banner = PIIAlertBanner(finding_count, on_review=lambda: None)
    qtbot.addWidget(banner)
    banner.show()

    # After 5 seconds without user action — banner still visible
    qtbot.wait(5000)
    assert banner.isVisible(), "Banner auto-dismissed without user action"
```

### T5 — Remediation requires explicit user confirmation

```python
def test_remediation_requires_explicit_confirmation(mock_hub, pii_remediation):
    """Remediation must not proceed without explicit user confirmation."""
    with pytest.raises(ConfirmationRequiredError):
        pii_remediation.apply_remediation(skip_confirmation=True)
```

### T6 — No automatic PII deletion

```python
def test_no_automatic_pii_deletion(pii_scanner, tmp_path):
    """PII must not be automatically deleted after detection."""
    test_file = tmp_path / "data.txt"
    test_file.write_text("user@example.com sensitive content")

    pii_scanner.run_background_scan(str(tmp_path))
    # File must still exist and be unmodified after scan
    assert test_file.exists()
    assert "user@example.com" in test_file.read_text()
```

### T7 — Scheduled scan also triggers proactive surfacing

```python
def test_scheduled_scan_surfaces_proactively(mock_hub, pii_scanner):
    """Scheduled scans are treated identically to background scans."""
    findings = [PIIFinding("backup/old.txt", "email_address", 0.80)]
    on_scan_complete(findings, ScanOrigin.SCHEDULED, mock_hub)
    assert mock_hub.show_persistent_pii_banner.called
```

### T8 — Empty results suppress banner/badge

```python
def test_no_findings_no_banner(mock_hub, pii_scanner):
    """When no PII is detected, no proactive surfacing should occur."""
    on_scan_complete([], ScanOrigin.BACKGROUND, mock_hub)
    assert not mock_hub.show_persistent_pii_banner.called
    assert not mock_hub.display_inline_results.called
```

---

## 9. Cross-References

| Reference | Location |
|-----------|----------|
| Constitutional authority | §VIII.X.1–§VIII.X.6 |
| PII detection scope & anonymization rules | §VIII (constitution) |
| Glossary: user-visible (§G.1) | constitution.md §G.1 |
| Glossary: user-discoverable (§G.2) | constitution.md §G.2 |
| Two-step irreversible confirmation | §VIII (constitution) |
| Data minimization in audit/telemetry | §VIII Data Minimization bullet |
| Reviewer checklist | .specify/memory/checklist-pii-scan-ux-compliance.md |
| Round-8 Q15 answer | .specify/memory/constitution_clairification_uiux_harmonny_r8.md §Q15 |
| UI/UX visibility checklist | .specify/memory/checklist-uiux-visibility-compliance.md |
