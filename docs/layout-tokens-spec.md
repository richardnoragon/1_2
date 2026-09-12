# Layout Token Specification

**Constitution Reference**: §8.9, §12.1 (LYT)
**Version**: 1.37.0
**Added**: 2026-04-25 (harmonization2 Phase 2 — resolves TODO(LAYOUT_TOKENS_SPEC))
**Status**: Constitutionally complete — see §8.9. CI enforcement gated on
TODO(LAYOUT_TOKENS_IMPL).

---

## Overview

This document is the canonical specification for Layout Structure compliance
(LYT capability, §12.1). It defines the mandatory layout token taxonomy,
naming conventions, safe-area margins, and CI enforcement semantics that all
tools MUST follow. No tool MAY use hardcoded spacing, padding, or margin
values outside the token system.

Issue #81's UI/UX modernization pass uses the shared token and accessibility baseline described here and in the common style helpers, keeping the refreshed window and dialog surfaces consistent with the layout contract.

---

## 1. Token Taxonomy

All tokens live in `src/rfu/layout_tokens.py` (implementation: Phase 2
deliverable — TODO(LAYOUT_TOKENS_IMPL)).

### 1.1 Spacing Tokens

| Token Name | Value | Use |
|------------|-------|-----|
| `spacing.xs` | 2 px | Icon-to-label inline gap, tight list row padding |
| `spacing.sm` | 4 px | Default internal control padding, compact form rows |
| `spacing.md` | 8 px | Default spacing between controls in a row/column |
| `spacing.lg` | 16 px | Spacing between logical sections within a panel |
| `spacing.xl` | 24 px | Spacing between major layout zones (panels, cards) |
| `spacing.xxl` | 32 px | Full-bleed section separators, large-form gap |

### 1.2 Margin Tokens (Safe-Area)

| Token Name | Value | Use |
|------------|-------|-----|
| `margin.window` | 16 px | Outer margin from window edge to all content |
| `margin.panel` | 12 px | Inner margin of a panel or card widget |
| `margin.toolbar` | 4 px | Top/bottom padding within the main toolbar |
| `margin.dialog` | 16 px | Content margin inside dialog/modal windows |
| `margin.statusBar` | 4 px | Status bar internal padding |

### 1.3 Border Radius Tokens

| Token Name | Value | Use |
|------------|-------|-----|
| `radius.sm` | 3 px | Small interactive controls (buttons, inputs) |
| `radius.md` | 6 px | Cards, panels, group boxes |
| `radius.lg` | 10 px | Full modal dialogs, floating overlays |

### 1.4 Icon / Control Sizing Tokens

| Token Name | Value | Use |
|------------|-------|-----|
| `icon.sm` | 16 × 16 px | Inline / list-row icons |
| `icon.md` | 24 × 24 px | Toolbar icons (standard) |
| `icon.lg` | 32 × 32 px | Feature / hero icons |
| `control.minHeight` | 28 px | Minimum height for interactive controls |
| `control.minTouchTarget` | 44 px | Minimum touch target (A11Y WCAG 2.5.5) |

---

## 2. Usage Rules

### 2.1 MUST rules

- All layout spacing and padding MUST be defined via named tokens.
- Tokens MUST be resolved through `layout_tokens.get(token_name)` at
  widget initialisation.
- Safe-area margins (`margin.window`, `margin.dialog`) MUST be applied to
  all root layout containers in tool windows and dialogs.

### 2.2 MUST NOT rules

- Tools MUST NOT pass integer literals to `setContentsMargins()`,
  `setSpacing()`, `setFixedHeight()`, or `setFixedWidth()` without deriving
  the value from a token (e.g., `layout_tokens.get("spacing.md")`).
- Tools MUST NOT hard-code layout sizes in stylesheet properties
  (e.g., `padding: 8px; margin: 4px;`).

### 2.3 Exception

- Single-pixel borders/lines for separators (`QPainter.drawLine`, `QFrame`)
  are exempt from the token requirement. All other dimensions are not.

---

## 3. Theme Integration

Layout tokens participate in the Theming subsystem (TH capability):

- Token values MAY vary per density preset
  ("Compact" = multiply by 0.75; "Comfortable" = multiply by 1.0;
  "Spacious" = multiply by 1.25).
- `_on_theme_changed` handlers MUST call `layout_tokens.reload()` when the
  theme density changes.

---

## 4. Deferred Items

- **TODO(LAYOUT_TOKENS_IMPL)**: Implement `src/rfu/layout_tokens.py` module
  with `get(token_name)` → `int` and `reload()` functions. Wire to the
  `_on_theme_changed` lifecycle hook. Phase 2 deliverable.
  Until TODO(LAYOUT_TOKENS_IMPL) is resolved:
  - CI MUST NOT fail for hardcoded layout values (LYT non-compliance tolerated).
  - The LYT capability MUST remain `false` in `docs/tool-capability-matrix.json`
    for all tools until the module is implemented and tools are migrated.

---

## 5. CI Enforcement

Once TODO(LAYOUT_TOKENS_IMPL) is resolved:

- CI MUST detect and fail on:
  - `setContentsMargins(` with integer literals not derived from a token
  - `setSpacing(` with integer literals not derived from a token
  - Stylesheet `padding:` or `margin:` with hardcoded pixel values
  - `setFixedHeight(` / `setFixedWidth(` with hardcoded sizes (outside token)

See: .specify/memory/constitution.md §11.4 (LYT static analysis rules),
docs/ci-enforcement-spec.md §LYT.

---

## 6. Cross-References

- Constitution §8.9 (Layout Tokens — Deferred; TODO(LAYOUT_TOKENS_SPEC) resolved here)
- Constitution §12.1 (LYT capability definition)
- Constitution §11.4 (CI static analysis — LYT)
- docs/tool-capability-matrix.json (per-tool LYT compliance: all false pending
  TODO(LAYOUT_TOKENS_IMPL))
- TODO(LAYOUT_TOKENS_IMPL) — implementation deferred to Phase 2
