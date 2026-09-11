# Shared Component Usage Map

**Status:** Shared-layer P3 pass  
**Date:** 2026-09-11

## Purpose

This map records which shared Hub and framework components are used by the current modernization wave and whether any surfaces intentionally fall back to a custom pattern.

## Shared component inventory

| Component | Used by shared layer | Notes |
| --- | --- | --- |
| `ThemeManager` | Yes | Shared theme switching and variant-driven styling |
| `token()` | Yes | Canonical color lookup for shared styles |
| `Typography` | Yes | Shared text sizing and font conventions |
| `PrimaryButton` | Yes | Standard action affordance for common dialogs and launch surfaces |
| `SecondaryButton` | Yes | Used for secondary actions when a lower-emphasis control is needed |
| `Modal` | Yes | Shared confirmation and dialog presentation |
| `ToastNotification` | Yes | Used for non-blocking status communication |
| `LoadingIndicator` | Yes | Shared loading signal and progress state |
| `HubErrorScreen` | Yes | Shared fatal/non-fatal error handling surface |
| `UtilityWindow` | Yes | Standard hub-managed tool-window wrapper |
| `StandardWindow` | Partial | Used by the shared window baseline where appropriate |

## Shared-layer surfaces reviewed

- `src/gui/common/styles.py`
- `src/gui/common/dialogs.py`
- `src/gui/common/base_window.py`
- `src/tabbed_hub.py`
- `main.py`
- `src/gui/components/*`

## Deviation note

Custom tool windows that bypass shared base classes or directly embed hard-coded inline styles remain outside the shared-layer guarantee and should be evaluated per tool as part of the tool-specific verification flow.
