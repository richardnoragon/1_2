# UI/UX Harmonization — Component Library Scope

**Version 1.0 — April 2026**  
**Authority:** UI/UX Harmonization Specification v0.7 § 7.1  
**Status:** OD-1 RESOLVED — April 2026  
**Signed off by:** Richard Noragon, April 2026

---

## Purpose

This document records the resolution of **Open Decision OD-1**: *"Which components constitute the minimum component library subset that unblocks per-tool migration?"*

Spec §7.1 mandates that an initial version of the Hub shared component library containing the minimum subset MUST be available before per-tool migration (Phase 3) begins.

---

## OD-1 Resolution

**Decision:** The minimum component library subset consists of the **seven component types** listed below, implemented as **ten classes**, all residing in `src/gui/components/`. These components are delivered as part of Phase 1A (P1-C07 through P1-C14) and are available before any per-tool Phase 3 work begins.

**Rationale:** The six types mandated by spec §7.1 (Buttons, Inputs, Modals, Toast notifications, Breadcrumbs, Loading indicators) plus `HubErrorScreen` (required by spec §8.2 and wired into `UtilityWindow` by P1-C16) constitute a complete foundation. No tool migration can begin without all of these; none of them can be deferred.

---

## Minimum Subset — Delivered April 2026

| Component Type | Class(es) | File | Spec Ref |
|---|---|---|---|
| **Buttons** | `PrimaryButton`, `SecondaryButton`, `DestructiveButton` | `src/gui/components/buttons.py` | §7.1, §5.2 |
| **Text Inputs** | `TextInput` | `src/gui/components/inputs.py` | §7.1, §5.3 |
| **Modals** | `Modal`, `ConfirmationModal` | `src/gui/components/modal.py` | §7.1, §5.2 |
| **Toast Notifications** | `ToastNotification` | `src/gui/components/toast.py` | §7.1, §6.1 |
| **Breadcrumbs** | `Breadcrumb` | `src/gui/components/breadcrumb.py` | §7.1, §5.1 |
| **Loading Indicators** | `LoadingIndicator` | `src/gui/components/loading_indicator.py` | §7.1 |
| **Hub Error Screen** | `HubErrorScreen` | `src/gui/components/hub_error_screen.py` | §8.2 |

All components are importable via:

```python
from src.gui.components import (
    PrimaryButton, SecondaryButton, DestructiveButton,
    TextInput, Modal, ConfirmationModal,
    ToastNotification, Breadcrumb, LoadingIndicator, HubErrorScreen
)
```

---

## What Is Deferred

| Component Type | Status | Reason |
|---|---|---|
| **Data tables / grids** | Deferred to Phase 3 or later | Not mandatory for unblocking migration; tools with tabular data may use `QTableWidget` provisionally (document in `DEVIATIONS.md`) |
| **Toolbar / ribbon** | Deferred | DEV-002 covers the current menubar pattern; no spec mandate for a shared toolbar |
| **Tree / folder browser** | Deferred | Tool-specific; pattern defined per-tool in Phase 3 |
| **Split pane / panels** | Deferred | Layout concern, not a shared component |

Deferred components do NOT block per-tool Phase 3 migration. Tools requiring them MUST document any custom implementation in `DEVIATIONS.md`.

---

## Component Ownership & Contribution

- **Owner:** Richard Noragon (project owner)
- **Location:** `src/gui/components/`
- **Modification process:** Any change to a shared component MUST be reviewed for backward compatibility against all tools already using it. Breaking changes MUST increment the component file's version comment and notify all consuming tools.
- **Adding new components:** New shared components follow the same P1-C07 spec constraints — `token()` for all colors, `Typography.*()` for all fonts, `setAccessibleName()` in constructor, `setMinimumHeight(44)` on interactive elements.

---

## Delivery Target

All minimum-subset components were delivered **April 2026** as part of Phase 1A. Per-tool Phase 3 migration may begin immediately.

---

*OD-1 resolved. This document is the authoritative record of the resolution.*
