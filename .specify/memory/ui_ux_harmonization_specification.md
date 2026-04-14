# ui_ux_harmonization_specification
---

# **UI/UX Harmonization Specification**  
**Version 0.7 — Aligned (Round 5 Q&A, April 2026)**

## **1. Scope**
This specification defines the mandatory and recommended UI/UX requirements for all applications launched through the Central Hub. It establishes a unified interaction model, visual language, accessibility baseline, and integration behavior to ensure consistency, predictability, and maintainability across independently developed applications.

This document applies to:
- All first‑party and third‑party applications integrated into the Hub  
- All future UI/UX components intended for Hub‑based deployment  
- All updates to existing applications that materially affect user experience  

---

# **2. Normative Language**
The following keywords are to be interpreted as defined in RFC 2119:
- **MUST / MUST NOT** — absolute requirements  
- **SHOULD / SHOULD NOT** — strong recommendations; deviations require justification  
- **MAY** — optional behavior  

---

# **3. Design Principles**

## **3.1 Consistency**
Applications **MUST** adhere to shared patterns, components, and interaction models defined in this specification. Uniformity of layout is not required; consistency of experience is.

## **3.2 Accessibility**
Accessibility is a non‑negotiable requirement. All applications **MUST** meet the accessibility standards defined in Section 6.

## **3.3 Predictability**
Common interactions (navigation, form behavior, error handling, theming) **MUST** behave consistently across all applications.

## **3.4 Configurability**
Applications **MUST** respect global Hub preferences (theme, language, etc.) and **SHOULD** expose additional user‑level preferences where appropriate.

---

# **4. Visual Design Standards**

## **4.1 Theming**
- Applications **MUST** support the Hub’s global light and dark themes.  
- Applications **MUST NOT** override Hub‑level theme settings.  
- Custom color palettes **MAY** be used if they:
  - Maintain WCAG AA contrast  
  - Do not conflict with Hub navigation colors  
  - Do not override reserved semantic colors  

### **4.1.1 Reserved Semantic Colors**
Four semantic roles — Success, Warning, Error, and Info — have constitutional reserved token keys. All token names and their required values for light and dark modes **MUST** be defined in the `TOKENS` dict within `themes.py` / `styles.py` (per §4.1.2). The canonical registry lives exclusively in those modules; no spec-level token table is maintained. Applications **MUST NOT** repurpose semantic tokens for non‑semantic use.

### **4.1.2 Token Implementation (PyQt5)**
In this PyQt5 project, all **global** light/dark theme tokens **MUST** be implemented as a single nested Python dict (`TOKENS`) within the existing `themes.py` / `styles.py` modules, organized by theme variant: `TOKENS['light'][key]` for light mode and `TOKENS['dark'][key]` for dark mode. `TOKENS` is the authoritative source for global theme values and is read at application startup to derive the active palette.

> **Architecture clarification:** `TOKENS` governs global light/dark theme switching. Per‑user personal theme presets are managed through the preference API (constitution §VI, `theming` preference category). These two stores are complementary and non‑overlapping: `TOKENS` holds global defaults; the preference framework holds user‑specific overrides. See §4.1.3 for preset scoping rules.

Token keys use underscore notation matching the semantic token name (e.g. `semantic_success`). Hard‑coded hex color values **MUST NOT** appear in tool or widget source files; all color references **MUST** resolve through the token dict.

Hub navigation colors **MUST** be defined in the token dict during Phase 1. The following keys are reserved for Hub navigation use:

| Token Key | Role |
|-----------|------|
| `hub_nav_background` | Navigation panel background |
| `hub_nav_foreground` | Navigation panel text |
| `hub_nav_accent` | Navigation accent / selected indicator |
| `hub_nav_border` | Navigation panel border |

Custom application palettes **MUST NOT** assign values to these keys.

### **4.1.3 Theme Preset Scoping**
Named theme presets follow the two‑tier ownership model defined in constitution §VI (authoritative):
- **Personal presets** — created, edited, renamed, and deleted by the owning account; available to `user`‑role and above.
- **System‑wide presets** — created and managed only by `admin`/`dev` role accounts; visible to all users as read‑only templates.

Accounts with `role = user` **MUST NOT** delete or modify system‑wide presets, but **MAY** create personal presets locally derived from them. `readonly` accounts **MUST NOT** modify any theme preferences. See constitution §VI and §21 for the complete normative rules.

---

## **4.2 Typography**
- Applications **MUST** use the Hub’s base font family.  
- Applications **MUST** follow the Hub’s typographic scale (`h1`, `h2`, `h3`, `body`, `caption`).  
- Custom fonts **MUST NOT** be introduced without governance approval.
### **4.2.1 Base Font and Scale (PyQt5)**
The Hub's base font family is **Segoe UI**, applied via `QFont` in a shared `Typography` class. This class does not yet exist and **MUST** be created as part of this harmonization effort. The typographic scale maps to the following point sizes:

| Role | Point Size | Weight |
|------|-----------|--------|
| `h1` | 18 pt | Bold |
| `h2` | 14 pt | Bold |
| `h3` | 12 pt | SemiBold |
| `body` | 10 pt | Regular |
| `caption` | 8 pt | Regular |

The `Typography` class **MUST** be the sole source of font construction; tools **MUST NOT** call `QFont()` with explicit family/size arguments outside it. The `Typography` class **MUST** expose class methods for each scale role (e.g. `Typography.h1()`, `Typography.body()`, `Typography.caption()`), each returning a pre‑configured `QFont` instance.
---

## **4.3 Layout & Spacing**
- Applications **MUST** use an 8‑point spacing grid.  
- Minimum interactive target size **MUST** be 44×44 **logical (device‑independent) pixels**, consistent with WCAG 2.1 SC 2.5.8 (see constitution §7(g)).  
- Standard container padding **MUST** be 16 px; dense mode **MAY** reduce to 8 px.  
- Dense mode is a **developer decision made at design time** (hard‑coded per tool). It is not a global Hub preference and is not user‑configurable at runtime.  

---

# **5. Interaction Standards**

## **5.1 Navigation**
- Applications **MUST NOT** implement their own global navigation.  
- Local navigation (tabs, sidebars) **MAY** be used if:
  - It does not visually compete with Hub navigation  
  - It uses Hub‑provided components where available  

> **Open Item:** The current `UtilityWindow` menubar‑clone pattern (which reproduces the Hub menubar in each tool window) has not yet been resolved as compliant or non‑compliant. It is documented as **DEV-002** in `DEVIATIONS.md` and **MUST** be re-evaluated when a shared menu component is formally specified.

---

## **5.2 Buttons & Actions**
- Each view **MUST** have at most one primary action.  
- Secondary actions **SHOULD** be visually de‑emphasized.  
- Destructive actions:
  - **MUST** use the semantic error color  
  - **MUST** require explicit confirmation  
- Operations with side effects **MUST** surface the dry-run option as a visible UI element before the user initiates the operation (constitution §II.1). A dry-run control (e.g. checkbox, button, or toggle) **MUST** be present and reachable in the default view prior to the primary action being available.  

---

## **5.3 Forms**
- Labels **MUST** be persistently visible (no placeholder‑only labeling).  
- Validation **MUST** be inline and immediate.  
- Error messages **MUST** be actionable and specific.  

---

# **6. Accessibility Requirements**

## **6.1 Minimum Standards**
Applications **MUST** meet:
- WCAG 2.1 AA contrast (see constitution §7 for exact ratios: standard text ≥4.5:1, large text ≥3:1, non‑text UI components ≥3:1)  
- Full keyboard navigability  
- Screen reader compatibility (validated against **Windows Narrator** and **NVDA**)  
- Visible focus indicators  
- No keyboard traps  
- All interactive controls **MUST** carry accessible labels (`setAccessibleName` / `setAccessibleDescription` or equivalent) for screen reader compatibility (constitution §7(e))  
- Respect for the **OS reduced‑motion preference**: all animated or transitioning UI elements **MUST** respond to the OS reduced‑motion setting  

---

## **6.2 Required Accessibility Smoke Tests**
Applications **MUST** pass the following tests before integration:

### **6.2.1 Tab Order Test**
- Logical, predictable, and complete tab sequence.

### **6.2.2 Contrast Test**
- Automated contrast scan + manual verification of key screens.

### **6.2.3 Resize Test**
- UI remains functional at 200% zoom.

### **6.2.4 Color‑Blind Simulation**
- No loss of meaning under common color‑blindness filters.

---

# **7. Component Standards**

## **7.1 Shared Components**
Applications **MUST** use Hub‑provided components when available:
- Buttons  
- Inputs  
- Modals  
- Toast notifications  
- Breadcrumbs  
- Loading indicators  

> **Library Status:** The Hub shared component library does not yet exist. An initial version containing a **minimum subset** of the six component types listed above **MUST** be available before per‑tool migration begins. The remaining component types **MAY** be built concurrently with per‑tool migration. The minimum subset that unblocks migration **MUST** be agreed upon and documented during Phase 1. Until the library exists, all tool components are considered provisional and subject to replacement.

If a shared component is not used:
- The alternative **MUST** match the shared component’s behavior and semantics.  
- The deviation **MUST** be documented in `DEVIATIONS.md`.  
> **Critical Engine Classification:** Components or modules performing batch operations, irreversible operations, security-sensitive processing, or multi-file writes **MUST** be classified as critical engines per constitution §G.6 and §III.1. Classification imposes stricter test coverage requirements (property-based and scenario edge tests in addition to standard unit tests).
### **7.2 ComponentGuardian Registration**
All PyQt5 GUI component classes integrated into the Hub **MUST** register with `ComponentGuardian` (located in `src/core/guardian/`) before the component is made available to users (constitution §V). Registration requires:
- `widget` — the component widget instance
- `health_check` — a zero-argument callable returning a boolean health status
- `degraded_fallback` — a zero-argument callable invoked when the component enters degraded state

The `degraded_fallback` **MUST** render the component as visible with reduced functionality; the component **MUST NOT** be hidden or removed from the UI. Each tool's implementation documentation **MUST** define which capabilities are disabled in degraded mode.

Recovery from degraded state is **automatic**: when `health_check()` returns `True`, the component **MUST** return to full functionality without manual intervention (constitution §V.2).

---

# **8. Behavior & State Management**

## **8.1 Loading States**
- Operations exceeding 300 ms **MUST** display a loading indicator sourced from the Hub shared component library's Loading Indicators component.  
- Skeleton screens **SHOULD** be used for content‑heavy views.  
- The 300 ms threshold is measured as **wall‑clock time via `QTimer`**, starting when the operation is initiated on the UI thread.  
- Operations that require a loading indicator and are of extended duration **MUST** also expose cancellable progress per §8.4.  

---

## **8.2 Error Handling**
- User‑facing errors **MUST** be clear, actionable, and non‑technical.  
- Technical details **MAY** be logged but **MUST NOT** be shown to users.  
- Fatal errors **MUST** redirect to the Hub’s global error screen.  > **Fatal Error Definition:** A "fatal" error is any error that prevents the tool from continuing to function (e.g. unrecoverable state failure, critical resource unavailable). Non‑fatal errors (e.g. a single failed file operation) **MUST** be surfaced inline and **MUST NOT** trigger the global error screen.
> **Creation Required:** The Hub global error screen does not yet exist. It **MUST** be created as part of this harmonization effort. Until it exists, tools **MUST** display an accessible, non‑technical error dialog as a provisional fallback.
---

## **8.3 Empty States**
Empty states **MUST** include:
- A concise explanation  
- A recommended next action  
- Optional illustration (if used, **MUST** use SVG icons from the project's existing icon set at `assets/images/`; custom illustrations require governance review)  

---

## **8.4 Performance Requirements**
- All tool operations performing file, network, or compute work **MUST** run off the UI thread (worker thread or process pool).  
- The UI (main) thread **MUST NOT** be blocked for ≥ 100 ms at any point, consistent with constitution §6 and §IV.  
- Long-running operations **MUST** expose cancellable progress.  

---

# **9. Integration with the Central Hub**

## **9.1 Launch Behavior**
- Applications **MUST** load within the Hub’s defined container.  
- Applications **MUST NOT** resize or override Hub layout.  
- New windows **MUST NOT** be opened unless explicitly required.  
> **Clarification:** The `UtilityWindow` separate‑window launch pattern is **compliant** with this section, provided tool windows do not alter the Hub window's own geometry, size, or position. "Hub's defined container" means the Hub's visual and theme context, not a physical embedded panel.
---

## **9.2 Global Preferences**
Applications **MUST** respect:
- Theme  
- Language  
- User identity and permissions  

> **Language / i18n Clarification:** The project is English‑only for this effort. All user‑visible strings **MUST** be soft‑wired via `src/rfu/ui_strings.py` to enable future i18n without source changes. This file does not yet exist and **MUST** be created as part of this effort using namespace classes per tool (e.g. `class FileManager: TITLE = "File Manager"`) so that each tool's strings are grouped under their own class. Direct string literals in widget constructors **MUST NOT** be used for user‑visible text.

---

## **9.3 Telemetry & Auditability**
Applications **MUST** emit:
- View load events  
- Error events  
- Key user actions (non‑PII)  
- Performance metrics  

Telemetry **MUST** comply with Hub governance and privacy requirements.

> **Implementation:** UI telemetry **MUST** route to the existing SQLite audit log. The audit log schema **MUST** be extended with the following UI‑specific event types: `ui_view_load`, `ui_user_action`, `ui_error_event`, `ui_performance_metric`. All events **MUST** include the following fields:
> - Shared mandatory fields (per §16.X, constitution): `actor_username`, `session_id`
> - UI‑event mandatory fields: `timestamp` (ISO‑8601), `event_type` (one of the four types above), `tool_id`
> - Additional per‑event fields are implementation‑defined.
>
> UI telemetry events **MUST** be retained for a minimum of **30 days**. Identity‑related events in the same log remain subject to the constitution §16 ≥365‑day retention requirement. All events **MUST** be non‑PII and comply with the privacy requirements of the constitution §16 and §16.X.
>
> **Constitutional deviation:** UI telemetry events are partially exempt from the §16.X.2 mandatory field set (`device_id` and `app_instance_id` are excluded for UI-specific event types). The accepted deviation is recorded as **DEV-001** in `DEVIATIONS.md`.

---

# **10. Quality Gates**

## **10.1 Automated Checks**
Applications **MUST** pass:
- Linting  
- Accessibility scan  
- Theming compliance validation  
- Component usage validation  
- Theming visual smoke test (required for all theming changes, constitution DW §11)  

> **Tooling:** The specific automated check tools for theming compliance and component usage validation **MUST** be selected and defined as Phase 1 deliverables (see Migration Guide Phase 1.3). No tooling is mandated at specification time.

> **Constitutional CI gates prerequisite:** The constitutional §5 CI gates (lint, type check, unit + integration tests, coverage ≥85%, GUI smoke test, tool validation, dry-run surface check) are a prerequisite for UI harmonization sign-off. Sequencing and gate details are in Migration Guide Phase 4.1.

---

## **10.2 Manual Review**
Applications **MUST** undergo:
- UX consistency review  
- Accessibility spot checks  
- Interaction flow validation  
- Error handling review  

---

## **10.3 Documentation Requirements**
Applications **MUST** provide:
- `UX_COMPLIANCE.md`  
- `DEVIATIONS.md` (if applicable)  
- Screenshots of key flows (stored in `docs/ui-ux-harmonization/screenshots/{tool-name}/`; distinct from the Phase 1.1 full UI inventory in `assets/ui_captures/{tool-name}/`)  
- Accessibility test results  

---

# **11. Governance & Change Control**
- Changes to this specification **MUST** undergo governance review.  
- Breaking changes **MUST** be announced one release cycle in advance.  
- Applications **MUST** comply with updated standards within **30 days** of the date the new standard is published (see Migration Guide §5.3).  

---