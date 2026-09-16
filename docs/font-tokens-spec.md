# Font Token Specification

**Constitution Reference**: §8.1, §12.1 (FNT)
**Version**: 1.37.0
**Added**: 2026-04-25 (harmonization2 Phase 2 — resolves TODO(FONT_TOKENS_SPEC))
**Status**: Token API and shared-widget integration implemented. Full tool
migration remains open; see [implementation status](harmonization2/implementation-status.md).

---

## Overview

This document is the canonical specification for Typography & Font Token
compliance (FNT capability, §12.1). It defines the mandatory font token system
that all tools MUST use. No tool MAY reference raw font families, raw pixel
sizes, or raw Qt font objects outside the token system.

---

## 1. Token Taxonomy

All tokens live in `src/rfu/font_tokens.py`.

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

> **Resolved 2026-09-16**: The table governs, as confirmed by the user.
> `font.body` uses `setPointSizeF(14)`, not 10 points. Qt handles display DPI;
> accessibility scaling multiplies token sizes relative to the application's
> initial font size and never reduces a token below its table size.

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

- Project minimum legibility sizes:
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

Implemented APIs: `get(name)` returns a fresh font; `bind(widget, name)` applies
and maintains a live token; `reload()` refreshes bound widgets. Body-family
fallbacks are Segoe UI/Arial on Windows, SF Pro Text/Helvetica Neue/Arial on
macOS, and Noto Sans/DejaVu Sans/Liberation Sans on Linux. Monospace resolution
falls back to Qt's system fixed font. Legacy `Typography` and `Fonts` calls
resolve through this module. Shared components and twelve tool modules now use
live bindings. Remaining raw-font and stylesheet users still require migration.
`apply_profile(window, family, body_size)` integrates UAP preferences without
flattening heading/caption sizes. Factory body size is 14; legacy smaller saved
sizes remain readable in storage but render at the minimum. Application font
changes use Qt's `fontChanged` signal to update bindings safely.

- **TODO(FONT_TOKENS_IMPL)**: Finish migrating every tool and its appearance
  lifecycle to the implemented token API. This is a Phase 2 deliverable.
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
