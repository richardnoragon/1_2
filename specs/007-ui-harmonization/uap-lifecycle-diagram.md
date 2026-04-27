# UAP Lifecycle Diagram — Feature 007: UI Harmonization

**Status:** CANONICAL (Phase-3 — Resolved 2026-04-26)  
**Governing decisions:** P3-C01, P3-M02, P3-Q5, P3-L01  
**Authoritative record:** `speckit-analysis-report-pass3.md`

This diagram is the **canonical reference** for all Phase-4 and later implementation and review work. Any deviation from this lifecycle is a blocking issue.

---

## High-Level UAP Lifecycle

```
┌────────────────────────────────────────────────────────────┐
│                    Application Startup                     │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 1. StandardWindow.__init__()                               │
│    - Calls _setup_window()                                 │
│      • Sets minimum size constraints                       │
│      • MAY set placeholder geometry (non-authoritative)    │
│                                                            │
│    - Calls _setup_ui()                                     │
│      • Constructs widgets, layouts, menus                  │
│      • Window not yet shown                                │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 2. UAPService.apply(self, manifest_entry)   ◄── T031       │
│                   *** AUTHORITATIVE STEP ***                │
│                                                            │
│    Reads from PreferenceStore:                             │
│      active_width, active_height, active_x, active_y      │
│      font_family, font_size, browse_root                   │
│                                                            │
│    Applies to window:                                      │
│      self.resize(max(active_w, min_w), max(active_h, min_h)│
│      self.move(active_x, active_y)                         │
│      self.setFont(QFont(font_family, font_size))           │
│                                                            │
│    Stores tracking fields on window instance:             │
│      self._uap_font_family = font_family                   │
│      self._uap_font_size   = font_size                     │
│      self._uap_browse_root = browse_root                   │
│                                                            │
│    Registers window:                                       │
│      ThemeManager.instance().register(self)                │
│                                                            │
│    ⚠ No resize() or move() may follow apply() in __init__ │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 3. UAPService.place_window(self, registered_windows)       │
│    - Positions window relative to other open windows       │
│    - Cascade offset or smart-placement algorithm           │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 4. _create_status_bar()                                    │
│    - Must occur AFTER apply()                              │
│    - Status bar may display UAP-derived state              │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 5. show()                                                  │
│    - Window becomes visible                                │
│    - Displayed at UAP-authoritative geometry               │
│    - No geometry flicker (apply() ran before show())       │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 6. User Session (runtime)                                  │
│                                                            │
│    Font change (FR-021):                                   │
│      ThemeManager.instance().uap_font_changed.emit(f, s)  │
│      → _on_uap_font_changed(family, size)                  │
│      → self.setFont() + findChildren(QWidget).setFont()    │
│                                                            │
│    Geometry change:                                        │
│      ThemeManager.instance().uap_geometry_changed.emit()  │
│      → _on_uap_geometry_changed(w, h, x, y)               │
│      → self.resize(w, h); self.move(x, y)                  │
│                                                            │
│    ⚠ Tracking fields (_uap_*) updated only via apply()    │
│      They are NOT updated on mid-session signal events     │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 7. StandardWindow.closeEvent(event)         ◄── T032       │
│                                                            │
│    Step 1: Read tracking fields (set by apply()):          │
│      font_family = self._uap_font_family                   │
│      font_size   = self._uap_font_size                     │
│      browse_root = self._uap_browse_root                   │
│                                                            │
│    Step 2: Read geometry live:                             │
│      g = self.geometry()                                   │
│      x, y, w, h = g.x(), g.y(), g.width(), g.height()     │
│                                                            │
│    Step 3: Persist last-used state:                        │
│      UAPService().save_last_used(                          │
│          w, h, x, y, font_family, font_size, browse_root  │
│      )                                                     │
│                                                            │
│    Step 4: Unregister from ThemeManager:                   │
│      ThemeManager.instance().unregister(self)              │
│                                                            │
│    Step 5: Call superclass:                                │
│      super().closeEvent(event)                             │
└────────────────────────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│ 8. PreferenceStore persists updated UAP state              │
│    - save_last_used() writes full snapshot atomically      │
│    - Next window open reads this updated state             │
└────────────────────────────────────────────────────────────┘
```

---

## Step Table (Reviewer Reference)

| Step | Method | Task | Constitutional Rule |
|------|--------|------|---------------------|
| 1a | `_setup_window()` | — | Placeholder geometry only; non-authoritative (P3-M02) |
| 1b | `_setup_ui()` | — | Widget construction; window not shown |
| 2 | `UAPService.apply()` | T031 | **Authoritative** geometry, font, tracking fields (P3-M02, P3-Q5) |
| 3 | `UAPService.place_window()` | T031 | Smart placement relative to open windows |
| 4 | `_create_status_bar()` | — | After `apply()` only (P3-M02) |
| 5 | `show()` | — | At UAP-authoritative geometry |
| 6 | Signal handlers | T033 | Font/geometry updates via `ThemeManager.instance()` (P3-C01) |
| 7 | `closeEvent()` | T032 | Reads `_uap_*` fields + live geometry; persists; unregisters (P3-Q5, P3-L01) |
| 8 | `PreferenceStore` | T019 | Full-state write via `save_last_used()` only |

---

## Constitutional Rules Embedded in This Diagram

- **`UAPService.apply()` is the authoritative geometry and font step.** `_setup_window()` placeholder geometry is intentionally superseded (P3-M02).
- **Tracking fields `_uap_font_family`, `_uap_font_size`, `_uap_browse_root` MUST be set in `apply()`**, after applying font and directory (P3-Q5).
- **`closeEvent()` MUST read tracking fields**, not `self.font()` or a store re-read (P3-Q5).
- **Geometry MUST be read live** from `self.geometry()` in `closeEvent()` (P3-Q5).
- **`ThemeManager.instance().register/unregister` MUST bracket the window lifecycle** (P3-C01, P3-H03).
- **No code may `resize()` or `move()` the window after `apply()` returns in `__init__`** (P3-M02).
- **`save_last_used()` is called exclusively from `closeEvent()`** — no incremental full-state writes elsewhere (A2).

---

## Signal Flow (ThemeManager — Runtime Phase)

```
User changes font in UAPAppearanceWidget
    │
    ▼
UAPService.set_font_preferences(family, size)
    │
    ▼
PreferenceStore.set_font_preferences(family, size)
    │
    ▼
ThemeManager.instance().uap_font_changed.emit(family, size)
    │
    ├─► StandardWindow._on_uap_font_changed(family, size)
    │       self.setFont(QFont(family, size))
    │       for w in self.findChildren(QWidget): w.setFont(...)
    │
    └─► [all other registered windows receive same signal]
```

---

## Lifecycle Anti-Patterns (Reviewer Watchlist)

The following patterns are **blocking issues** if found in an implementation:

| Anti-Pattern | Rule Violated |
|---|---|
| `self.resize()` or `self.move()` after `apply()` in `__init__` | P3-M02 |
| Font read from `self.font()` in `closeEvent()` | P3-Q5 |
| `UAPService().get_active_settings()` called in `closeEvent()` | P3-Q5 |
| `_uap_*` tracking fields set before `apply()` applies font | P3-Q5 |
| `ThemeManager()` direct instantiation (not `instance()`) | P3-C01 |
| `save_last_used()` called outside `closeEvent()` | A2 |
| Module-level `_open_windows` WeakSet alongside `ThemeManager._registered_windows` | U2 |
| `super().closeEvent(event)` called before `unregister()` | P3-L01 |

---

## Related Artifacts

| Artifact | Location |
|----------|----------|
| Full finding record | `speckit-analysis-report-pass3.md` |
| Phase-3 governance summary | `phase3-governance-summary.md` |
| Task specifications (T031, T032, T033) | `tasks.md` |
| ThemeManager skeleton | `speckit-analysis-report-pass3.md` §P3-C01 |
