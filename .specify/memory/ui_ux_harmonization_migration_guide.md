# ui_ux_harmonization_migration_guide 
---

# **UI/UX Harmonization Migration Guide**  
**Version 0.6 — Aligned (Round 5 Q&A, April 2026)**

## **1. Purpose**
This Migration Guide defines the required process for bringing existing applications into compliance with the **UI/UX Harmonization Specification**. It establishes a structured, auditable workflow that ensures consistent adoption of shared standards across all applications integrated into the Central Hub.

This guide applies to:
- All existing applications currently deployed outside the Hub  
- All applications already integrated into the Hub but not yet compliant  
- Any legacy UI/UX patterns requiring modernization  

---

# **2. Migration Phases**
Migration is divided into **five mandatory phases**. Each phase has required deliverables, review gates, and acceptance criteria.

---

# **Phase 1 — Discovery & Assessment**

## **1.1 Inventory Collection**
Each application team MUST produce an inventory of:
- Screens and user flows  
- UI components used (custom + library)  
- Theming implementation  
- Navigation patterns  
- Accessibility features and gaps  
- Error handling patterns  
- Telemetry and logging behavior  
- **Key actions** (the tool’s defined list of key user actions reachable by keyboard, per constitution §7)  

> **UI Captures Storage:** Screenshots and screen recordings **MUST** be stored in `assets/ui_captures/{tool-name}/` (a new top‑level directory created as part of Phase 1).

## **1.2 Compliance Assessment**
Teams MUST complete the **UI/UX Compliance Self‑Assessment** (provided separately) and categorize findings as:
- **Compliant**  
- **Non‑compliant**  
- **Not applicable**  

> **Template Status:** The Self‑Assessment Template does not yet exist. It **MUST** be created by the project owner (Richard Noragon) before any per‑tool Phase 1 assessment begins. The template **MUST** contain one section for each of the **eight** inventory items in Phase 1.1, with Compliant / Non‑compliant / Not‑applicable checkboxes for each item.

## **1.3 Deliverables**
- `ASSESSMENT.md`  
- Full UI inventory (screenshots or screen recordings)  
- Component inventory  
- Accessibility audit results  
- **Self‑Assessment Template** (created once, shared across all tools)  
- **Hub shared component library — initial version** (created once before per‑tool migration begins)  
- **Automated compliance tooling** — tooling selected, configured, and validated; selection and configuration documented in `docs/ui-ux-harmonization/AUTOMATED_TOOLING.md`  
- **Hub navigation color token definitions** (defined in `themes.py` / `styles.py` token dict)  
- **`KEY_ACTIONS.md`** (per‑tool) — each tool's list of key user actions reachable by keyboard, stored at `docs/ui-ux-harmonization/{tool-name}/KEY_ACTIONS.md`; this document satisfies the constitution §7 implementation‑doc requirement  
- **Issue Severity Rubric** — a tool‑agnostic rubric defining Critical, High, Medium, and Low severity levels, required before Phase 3 sign‑off  
- **UAT Scenario Template** — a lightweight shared scenario format from which per‑tool test scenarios are derived from the Phase 1.1 user‑flow inventory  
- **`DEVIATIONS.md`** (created once, project-wide at `docs/ui-ux-harmonization/DEVIATIONS.md`; initially empty; per-tool sections added in Phase 3)  
- **Hub global error screen — initial implementation** (created once as part of this harmonization effort; replaces the provisional error dialog fallback described in spec §8.2)  
- **`ui_strings.py`** — created once at `src/rfu/ui_strings.py`; namespace-class string store enabling future i18n (spec §9.2); initially contains stub classes with `TITLE` and `LOADING` only  
- **`COMPONENT_LIBRARY_SCOPE.md`** — created once at `docs/ui-ux-harmonization/COMPONENT_LIBRARY_SCOPE.md`; records the OD-1 minimum-component-subset decision before Phase 1A P1-C07 work begins  
- **`CRITICAL_ENGINE_REGISTER.md`** (empty placeholder) — created once at `docs/ui-ux-harmonization/CRITICAL_ENGINE_REGISTER.md`; pre-populated with eight provisional candidates; populated with confirmed classifications in Phase 2  

## **1.4 Exit Criteria**
- All required documentation submitted  
- No missing or incomplete inventories  
- Reviewer acknowledges assessment completeness  

---

# **Phase 2 — Gap Analysis & Remediation Planning**

## **2.1 Gap Identification**
Teams MUST map all non‑compliant items to the corresponding sections of the Harmonization Specification.

## **2.2 Remediation Plan**
Teams MUST produce a remediation plan that includes:
- Required changes  
- Estimated effort  
- Dependencies (technical, design, or governance)  
- Risks and constraints  
- Proposed timeline  

## **2.3 Prioritization**
Gaps MUST be prioritized using the following order:
1. **Accessibility violations**  
2. **Navigation and interaction inconsistencies**  
3. **Theming and visual inconsistencies**  
4. **Component deviations**  
5. **Telemetry and integration gaps**  

## **2.4 Deliverables**
- `REMEDIATION_PLAN.md` (serves as the prioritized backlog; no external tracking system is used)  

## **2.5 Exit Criteria**
- Plan approved by UX Governance  
- All gaps mapped to actionable items  
- Timeline accepted  

> **UX Governance:** For this project, UX Governance is fulfilled by the project owner (Richard Noragon). Approval is self‑approval with documented rationale recorded in `REMEDIATION_PLAN.md`.

---

# **Phase 3 — Implementation**

## **3.1 Component Replacement**
Teams MUST replace non‑compliant components with Hub‑approved shared components where available.

If a shared component is unavailable:
- Teams MAY use a custom component  
- The custom component MUST match the shared component’s semantics and behavior  
- The deviation MUST be documented in `DEVIATIONS.md`  

## **3.2 Theming Integration**
Applications MUST:
- Adopt Hub theme tokens  
- Remove hard‑coded colors  
- Support light/dark modes  

## **3.3 Interaction Model Alignment**
Teams MUST update:
- Navigation patterns  
- Button hierarchy  
- Form behavior  
- Error handling flows  

## **3.4 Accessibility Remediation**
Teams MUST:
- Fix contrast issues  
- Ensure keyboard navigability  
- Set Qt accessibility properties (`setAccessibleName`, `setAccessibleDescription`, `QAccessibleWidget` where required)  
- Implement visible focus states  
- Validate screen reader compatibility  

## **3.5 Deliverables**
- Updated application build  
- Updated documentation  
- Updated component usage map  

## **3.6 Exit Criteria**
- All remediation items implemented  
- No remaining critical or high‑severity issues, as defined by the Issue Severity Rubric (Phase 1.3 deliverable)  

---

# **Phase 4 — Verification & Review**

## **4.1 Automated Verification**
Applications MUST pass **all constitutional CI gates** (§5 of the constitution: lint, type check, unit + integration tests, coverage ≥85%, GUI smoke test, tool validation, dry‑run surface check) in addition to the following UI‑specific checks:
- Accessibility scan  
- Theming compliance validation  
- Component usage validation  
- Theming visual smoke test (for all theming changes, per constitution DW §11)  

## **4.2 Manual UX Review**
Reviewers MUST validate:
- Visual consistency  
- Interaction predictability  
- Accessibility spot checks  
- Error handling behavior  
- Empty state compliance  

## **4.3 User Acceptance Testing**
Teams MUST conduct:
- Scenario‑based testing (scenarios **MUST** be derived from the Phase 1.1 user‑flow inventory using the UAT Scenario Template; each scenario **MUST** document the expected outcome so that pass/fail is unambiguous)  
- Keyboard‑only testing  
- Screen reader testing (**Windows Narrator** and **NVDA** both required)  
- High‑contrast mode testing  

## **4.4 Deliverables**
- `VERIFICATION_REPORT.md`  
- Accessibility test results  
- Reviewer sign‑off  

## **4.5 Exit Criteria**
- All automated checks passed  
- All manual review findings resolved  
- Reviewer approval granted  

---

# **Phase 5 — Integration & Monitoring**

## **5.1 Hub Integration**
Applications MUST:
- Load within the Hub container  
- Respect global preferences  
- Emit required telemetry  

## **5.2 Post‑Integration Monitoring**
For the first 30 days post‑integration, teams MUST monitor:
- Error rates  
- Performance metrics  
- User feedback  
- Accessibility regressions  

> **Thresholds:** No global thresholds are defined. Each tool **MUST** establish its own baseline values for error rate and performance metrics in `POST_INTEGRATION_REPORT.md` before integration. Regressions are measured against that per‑tool baseline.

## **5.3 Continuous Compliance**
Applications MUST:
- Adopt new shared components as they become available  
- Update to new standards within **30 days** of the date the new standard is published  
- Participate in periodic UX audits  

## **5.4 Deliverables**
- `POST_INTEGRATION_REPORT.md`  
- Telemetry summary  
- Regression fixes (if applicable)  

## **5.5 Exit Criteria**
- No critical regressions  
- Telemetry within acceptable thresholds  
- Final governance approval  

> **Critical Regression Definition:** A post‑integration issue is a "critical regression" if it meets the Critical severity level as defined by the Issue Severity Rubric (Phase 1.3 deliverable). Until the rubric exists, a critical regression is any issue that (a) introduces an accessibility violation, (b) causes data loss or corruption, or (c) prevents a tool from launching or completing its primary function.

> **Governance Approval:** Final governance approval is granted by the project owner (Richard Noragon) via signed checklist. The signed `POST_INTEGRATION_REPORT.md` serves as the approval record.

---

# **Appendix A — Required Documents**
Every migrating application MUST produce the following:

| Document | Purpose |
|---------|---------|
| `ASSESSMENT.md` | Initial compliance assessment |
| `KEY_ACTIONS.md` | Per‑tool key‑actions list (constitution §7 implementation‑doc requirement) |
| `REMEDIATION_PLAN.md` | Detailed remediation plan |
| `DEVIATIONS.md` | Documented exceptions (shared project file at `docs/ui-ux-harmonization/DEVIATIONS.md`; created in Phase 1.3; per-tool sections added as needed) |
| `UX_COMPLIANCE.md` | Final compliance declaration |
| `VERIFICATION_REPORT.md` | Automated + manual review results |
| `POST_INTEGRATION_REPORT.md` | 30‑day monitoring summary |

> **Storage Location:** All required documents for this project are stored globally under `docs/ui-ux-harmonization/`. There is one shared set of documents for the overall project. Tool‑specific deviations are tracked in a single shared `DEVIATIONS.md` with per‑tool sections.
>
> **UtilityWindow menubar‑clone deviation** is recorded as **one shared project‑wide entry** in `DEVIATIONS.md`, covering all tools that use the pattern, rather than a separate entry per tool.
>
> **Screenshots:** `assets/ui_captures/{tool-name}/` (Phase 1.1 full UI inventory) and `docs/ui-ux-harmonization/screenshots/{tool-name}/` (spec §10.3 key‑UX‑flow screenshots) are **distinct sets** and MUST both be produced.
>
> **KEY_ACTIONS.md path:** Each tool's `KEY_ACTIONS.md` is stored at `docs/ui-ux-harmonization/{tool-name}/KEY_ACTIONS.md`. Separate files per tool; not a shared file.

---

# **Appendix B — Migration Timeline Expectations**
All tools follow the same harmonized migration process regardless of perceived size. Size‑based timeline tiers are not used. Each tool's `ASSESSMENT.md` **MUST** include a proposed migration timeline with rationale, subject to project‑owner approval.

---
