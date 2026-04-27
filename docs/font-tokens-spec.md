# Font Token Specification

**Constitution Reference**: §8.1, §12.1 (FNT)
**Version**: 1.37.0
**Added**: 2026-04-25 (harmonization2 Phase 2 — resolves TODO(FONT_TOKENS_SPEC))
**Status**: Constitutionally complete — see §8.1. CI enforcement gated on
TODO(FONT_TOKENS_IMPL).

---

## Overview

This document is the canonical specification for Typography & Font Token
compliance (FNT capability, §12.1). It defines the mandatory font token system
that all tools MUST use. No tool MAY reference raw font families, raw pixel
sizes, or raw Qt font objects outside the token system.

---

## 1. Token Taxonomy

All tokens live in `src/rfu/font_tokens.py` (implementation: Phase 2
deliverable — TODO(FONT_TOKENS_IMPL)).

### 1.1 Canonical Token Names

| Token Name | Role | Equivalent Size | Weight |
|------------|------|-----------------|--------|
| `font.body` | Body text, labels, list items | 14 pt | Normal |
| `font.bodyBold` | Emphasized body text, column headers | 14 pt | Bold |
| `font.mono` | Monospace: paths, hashes, hex values | 13 pt | Normal |
| `font.caption` | Captions, helper text, footnotes | 12 pt | Normal |
| `font.captionBold` | Bolded captions, section sub-headers | 12 pt | Bold |
| `font.title` | Panel titles, group box headers | 16 pt | SemiBold |
| `font.toolHeader` | Tool window title bar / top-level header | 18 pt | Bold |
| `font.small` | Legal text, keyboard shortcut hints | 11 pt | Normal |

> **Note on "pt" vs "px"**: All sizes above are in Qt logical points scaled at
> 96 DPI (i.e., `font.body` = `QFont` with `setPointSize(10)` at 96 DPI, not
> raw pixel values). Actual rendering adapts to OS DPI and accessibility zoom.

---

## 2. Usage Rules

### 2.1 MUST rules

- All visible text MUST reference a named font token.
- Font tokens MUST be resolved through `font_tokens.get(token_name)` at
  render time (never cached as hardcoded `QFont` instances at module level).
- Font scaling MUST respect Qt's `QApplication.font()` accessibility settings;
  tokens MUST multiply the base accessibility size factor.

### 2.2 MUST NOT rules

- Tools MUST NOT call `QFont("Arial", 12)`, `setFont(QFont(...))`, or any
  raw constructor with hardcoded family or size.
- Tools MUST NOT override or bypass font tokens via stylesheet `font-size:`
  or `font-family:` properties.
- Tools MUST NOT use pixel sizes (`setPixelSize()`); all sizes MUST use
  `setPointSizeF()` resolved from a token.

### 2.3 Accessibility scaling

- Minimum legibility sizes enforced per WCAG 2.1 AA:
  - Body text: ≥ 14 pt (normal weight)
  - Interactive controls: ≥ 14 pt
  - Captions/helper text: ≥ 12 pt (accepted minimum)
  - Small text: ≥ 11 pt (keyboard shortcut hints only)
- Zoom factors of 125%, 150%, 200% MUST remain fully legible.

---

## 3. Theme Integration

Font tokens participate in the Theming subsystem (TH capability):

- Font sizes MAY vary per theme preset (e.g., "Compact" vs "Comfortable").
- Font families MUST be overrideable via theme configuration, not hardcoded.
- `_on_theme_changed` handlers in tools MUST call `font_tokens.reload()` when
  the theme changes, if any widget caches resolved fonts.

---

## 4. Deferred Items

- **TODO(FONT_TOKENS_IMPL)**: Implement `src/rfu/font_tokens.py` module with
  `get(token_name)` → `QFont` and `reload()` functions. Wire to
  `_on_theme_changed` lifecycle hook. This is a Phase 2 deliverable.
  Until TODO(FONT_TOKENS_IMPL) is resolved:
  - CI MUST NOT fail for raw font usage (FNT non-compliance is tolerated).
  - The FNT capability MUST remain `false` in `docs/tool-capability-matrix.json`
    for all tools until the module is implemented and tools are migrated.

---

## 5. CI Enforcement

Once TODO(FONT_TOKENS_IMPL) is resolved:

- CI MUST detect and fail on:
  - `QFont(` with hardcoded family or size in any tool source file
  - `setPixelSize(` in any tool source file
  - Stylesheet `font-size:` or `font-family:` declarations in any tool source
  - Missing `font_tokens` import in any tool that renders text

See: .specify/memory/constitution.md §11.4 (FNT static analysis rules),
docs/ci-enforcement-spec.md §FNT.

---

## 6. Cross-References

- Constitution §8.1 (purpose, TODO(FONT_TOKENS_SPEC) resolved here)
- Constitution §12.1 (FNT capability definition)
- Constitution §11.4 (CI static analysis — FNT)
- docs/tool-capability-matrix.json (per-tool FNT compliance: all false pending
  TODO(FONT_TOKENS_IMPL))
- TODO(FONT_TOKENS_IMPL) — implementation deferred to Phase 2
