<!--
Sync Impact Report
Version change: 1.37.0 → 1.37.0 (amendment — no version bump)
TODOs resolved in this amendment:
   - TODO(FONT_TOKENS_SPEC): RESOLVED — docs/font-tokens-spec.md published (v1.37.0).
     Full typography & font token specification (8 tokens, platform fallbacks,
     prohibited practices, CI enforcement) is now normative.
   - TODO(COMMAND_TAXONOMY): RESOLVED — docs/command-surface-spec.md §9 updated
     (v1.37.0) with complete per-tool command taxonomy tables for all 35 tools
     across 9 categories (§9.1–§9.11).
   - TODO(LAYOUT_TOKENS_SPEC): RESOLVED — docs/layout-tokens-spec.md published
     (v1.37.0). Full layout token taxonomy (spacing xs–xxl, margin, border radius,
     icon/control sizing) is now normative.
   - TODO(UI_STRINGS_MENU_TOKENS): RESOLVED — src/rfu/ui_strings.py expanded:
     Menu class (hub-level tokens §9.6) + 9 new tool classes added (Phase 2).
Companion file updates (this amendment):
   - docs/font-tokens-spec.md created (v1.37.0)
   - docs/layout-tokens-spec.md created (v1.37.0)
   - docs/command-surface-spec.md updated to v1.37.0 (per-tool taxonomy §9)
   - docs/tool-capability-matrix-template.md already at v1.37.0
   - docs/tool-capability-matrix.json: generated_by updated to constitution v1.37.0
   - docs/menu-architecture-spec.md: bumped to v1.37.0
   - docs/ui-interaction-contract-spec.md: bumped to v1.37.0
   - docs/hub-menu-integration-spec.md: bumped to v1.37.0
   - docs/ci-enforcement-spec.md: bumped to v1.37.0
   - src/rfu/ui_strings.py: Phase 2 Menu + tool classes appended

Previous Sync Impact Report
Sync Impact Report
Version change: 1.36.0 → 1.37.0
Modified principles (2026-04-24 harmonization2 clarification round 3 applied):
   - §11.7 Matrix Compliance Rules — JSON schema alignment note added:
     "Partial" and "Unknown" are governance-level semantic states, not JSON
     values. `null` maps to Unknown; CI MUST fail on `null` for required
     capabilities. "Partial" = incomplete compliance treated as `false`. No
     new JSON values added. The `?` in the template is display-only.
   - §9.8.2 Relaunch Tool Window — TODO(RELAUNCH_TOOL_WINDOW_API) added:
     `relaunch_tool_window()` does not exist in the codebase (zero grep
     matches in src/). API contract to be defined and implemented in Phase 2.
     CI MUST NOT fail for missing calls until this TODO is resolved.
   - §9.5 Hub Menu Structure — Clarifying note added: §9.5 governs the
     population order of menu *sources* across the whole menu bar (global →
     Hub-specific → tool-registered). §9.7.4 governs item ordering *within*
     each individual menu. These rules are complementary, not contradictory.
   - §8.4 Toolbar Layout Rules — Context label "(Toolbar Surfaces)" added;
     cross-reference to §10.5 (Dialog Surfaces) for dialog placement. This
     resolves apparent conflict with §10.5 by making surface scope explicit.
   - §10.5 Primary Action Rules — Context label "(Dialog Surfaces)" added;
     cross-reference to §8.4 (Toolbar Surfaces) for toolbar placement. Both
     rules are now surface-scoped, eliminating the apparent placement conflict.
Added sections: none
Modified sections: §8.4 (scope label + cross-ref), §9.5 (ordering note),
  §9.8.2 (TODO added), §10.5 (scope label + cross-ref),
  §11.7 (JSON schema alignment note).
New TODOs:
   - TODO(RELAUNCH_TOOL_WINDOW_API): Define and implement
     `relaunch_tool_window()` API (Phase 2). Zero matches in src/ confirmed.
Clarifications applied:
   - §11.7 "Partial"/"Unknown" vs JSON schema: true/false/null is the full
     JSON schema; "Partial"/"Unknown" are semantic CI interpretations only.
   - §9.8.2 relaunch_tool_window() gap: gated behind TODO; not CI-enforced yet.
   - §9.5 vs §9.7.4 ordering: complementary rules at different abstraction
     levels; clarifying note prevents future misinterpretation.
   - §10.5 vs §8.4 Primary Action placement: different UI surfaces; explicit
     scope labels resolve the apparent contradiction.
Companion file updates:
   - docs/tool-capability-matrix-template.md updated to v1.37.0: NOM, WRD,
     FNT, LYT definitions updated to match §12.1 (v1.36.0 sharpened defs).

Previous Sync Impact Report
Sync Impact Report
Version change: 1.35.0 → 1.36.0
Modified principles (2026-04-24 harmonization2 clarification round 2 applied):
   - §7.3 File menu scope — Session lifecycle clarification added: Hub
     navigation items (e.g., "Return to Hub") qualify as session lifecycle
     actions and MUST be placed under File. Resolves latent conflict between
     §7.3 (File for document/data ops) and §9.6 (Hub-Specific Menu Items
     including "Return to Hub" under File). Hub-provided status per §9.7.1
     confirmed; no conflict with tool File-item restriction.
   - §8.1 Purpose — TODO(FONT_TOKENS_SPEC) added: harmonization2 source
     designated §8 as "Typography & Font Token Specification" (§8.1–§8.7);
     that content is deferred; font tokens belong to TH (Theming); full
     Typography spec will be constitutionalized in a future phase.
   - §8.9 Layout Tokens (new sub-section) — Stub section added stating LYT
     requirement for spacing/safe-area margins/non-hardcoded layout values;
     TODO(LAYOUT_TOKENS_SPEC) gates CI enforcement until layout token taxonomy
     and naming conventions are defined.
   - §12.1 NOM capability — Definition sharpened: NOM = structural UI naming
     (menu items, action labels, command names, reserved verbs — §7.4.1,
     §7.4.4). Previously "Nomenclature & wording compliance (§7.4)".
   - §12.1 WRD capability — Definition sharpened: WRD = contextual runtime
     text (tooltips, body text, error messages, toasts — §7.4.2, §7.4.3).
     Previously "Wording & microcopy compliance". Boundary with NOM now crisp.
   - §12.1 FNT capability — Note added referencing TODO(FONT_TOKENS_SPEC).
   - §12.1 LYT capability — Note added referencing §8.9 and
     TODO(LAYOUT_TOKENS_SPEC).
   - §12.3 CI Integration — Specific tool count "35 tools" replaced with
     "refer to docs/tool-capability-matrix.json" to prevent future drift.
   - §13.1 Phase 2 — Marked "constitutionally complete" as of v1.36.0. All
     three items (§13.1.1 UI Interaction, §13.1.2 CSH, §13.1.3 Hub UX Cohesion)
     are governed by normative sections. Hub UX Cohesion implementation
     (badges, last-run state, health indicators) noted as backlog, not
     constitutional requirement.
Added sections: §8.9 Layout Tokens (Deferred)
Modified sections: §7.3 (session lifecycle clarification), §8.1 (TODO added),
  §12.1 (NOM/WRD/FNT/LYT definitions sharpened), §12.3 (tool count de-hardcoded),
  §13.1 (Phase 2 marked complete).
New TODOs:
   - TODO(FONT_TOKENS_SPEC): [RESOLVED v1.37.0 — see docs/font-tokens-spec.md]
     Constitutionalize Typography & Font Token Specification.
   - TODO(FONT_TOKENS_IMPL): Implement font token module in src/rfu/ TBD.
   - TODO(LAYOUT_TOKENS_SPEC): [RESOLVED v1.37.0 — see docs/layout-tokens-spec.md]
     Define full layout token taxonomy, naming conventions, safe-area margin
     values, and CI enforcement semantics.
   - TODO(HUB_UX_COHESION): Hub-level implementation of capability badges,
     last-run state, and health indicators (implementation backlog only).
Clarifications applied:
   - §7.3 vs §9.6 conflict: resolved — "Return to Hub" is a session lifecycle
     item ⇒ File is correct. Hub provides it; tools do not register it.
   - NOM vs WRD boundary: NOM = structural naming; WRD = runtime copy.
   - §12.3 tool count: de-hardcoded; registry is authoritative.
   - Phase 2 completeness: constitutionally complete; Hub UX Cohesion is
     implementation backlog only.

Previous Sync Impact Report
Sync Impact Report
Version change: 1.34.0 → 1.35.0
Modified principles (2026-04-24 harmonization2 clarification round applied):
   - §8 Command Surface Harmonization — new constitutional section added:
     §8.1 Purpose; §8.2 Action Classification (four tiers: Primary, Secondary,
     Advanced, Destructive); §8.3 Command Taxonomy (five verbs: Inspect,
     Transform, Export, Apply, Revert — full per-tool mappings deferred to
     TODO(COMMAND_TAXONOMY)); §8.4 Toolbar Layout Rules (Primary left-most,
     Destructive separated, Advanced in menu/overflow only); §8.5 Keyboard
     Shortcut Rules (Primary actions MUST have shortcuts, Hub Registry
     registration required); §8.6 String Tokens (ui_strings required; CI
     enforcement deferred to TODO(UI_STRINGS_MENU_TOKENS)); §8.7 Context Menus
     (Destructive last after separator); §8.8 CI Enforcement.
   - §9.7.1 Hub Menu Integration — clarification note added: "File → Return to
     Hub" (§9.8.1) is a Hub-provided item, not a tool-registered addition to
     File; §9.7.1 governs tool-registered items only. Resolves apparent conflict
     between §7.3 (File allowance) and §9.7.1 (File prohibition for tools).
   - §9.4 Hub Menu Registry — TODO(HUB_MENU_REGISTRY_API) added: Python
     interface for hub_menu_registry is not yet defined; CI enforcement for raw
     Qt API rejection (§9.12) is gated behind this TODO.
   - §12.1 OPS capability — TODO(OPS_PHASE3_SPEC) added inline: OPS marked
     Required to track intent; CI MUST NOT fail for OPS non-compliance until
     Phase 3 constitutional sections (§13.2) are published.
   - §12.3 CI Integration — canonical machine-readable matrix path added
     (docs/tool-capability-matrix.json); tool count corrected from "22" to "35"
     (reflecting actual codebase state as of v1.35.0); current phase noted
     (Phase 1 complete; Phase 2 newly active).
   - §13.1.2 Command Surface Harmonization — TODO(COMMAND_TAXONOMY) added:
     full per-tool action-to-verb mapping deferred to Phase 2 implementation.
Added sections: §8 (§8.1–§8.8)
Modified sections: §9.4 (TODO added), §9.7.1 (clarification note added),
  §12.1 (TODO added to OPS row), §12.3 (matrix path, tool count, phase note
  added), §13.1.2 (TODO added).
New TODOs:
   - TODO(COMMAND_TAXONOMY): [RESOLVED v1.37.0 — see docs/command-surface-spec.md §9]
     Full Command Taxonomy per-tool mappings (Phase 2).
   - TODO(HUB_MENU_REGISTRY_API): Python interface for Hub Menu Registry (Phase 2).
   - TODO(UI_STRINGS_MENU_TOKENS): [RESOLVED v1.37.0 — Menu class + 9 tool classes
     appended to src/rfu/ui_strings.py (Phase 2)]
     Populate menu/command tokens in ui_strings.py
   - TODO(OPS_PHASE3_SPEC): Constitutionalize Phase 3 Operational Guarantees
     (§13.2) before OPS capability is CI-enforced.
New spec document: docs/command-surface-spec.md
New checklist: .specify/memory/checklist-command-surface-compliance.md
New machine-readable matrix: docs/tool-capability-matrix.json (35 tools,
  all capabilities initialised to false/non-compliant baseline).
Fact corrections:
   - "22 tools" → 35 tools (§12.3 and §11); prior count from harmonization2
     source docs reflected an older codebase state.
   - §8 gap resolved: §8 = Command Surface Harmonization (§13.1.2 scope).

Previous Sync Impact Report
Sync Impact Report
Version change: 1.33.0 → 1.34.0
Modified principles (2026-04-24 harmonization2 Phase 2–4 applied):
   - New constitutional section §7 Menu Architecture & Nomenclature added:
     §7.1 Purpose; §7.2 Global Menu Bar (seven top-level menus, exact order);
     §7.3 Menu Taxonomy & Allowed Scope (File, Edit, View, Tools, Reports,
     Window, Help — scope rules for each); §7.4 Nomenclature Rules (verb
     forms, ellipsis, capitalization, reserved names); §7.5 Interaction
     Behavior (keyboard navigation, accelerators, accessibility);
     §7.6 Tool-Specific Menus (allowed categories: Tools, Reports, View only);
     §7.7 CI Enforcement (top-level menu prohibition, nomenclature violations,
     missing accelerators, raw strings, wrong category).
   - New constitutional section §9 Hub Menu Integration Specification added:
     §9.1 Purpose; §9.2 Scope; §9.3 Hub as the Menu Authority; §9.4 Hub Menu
     Registry (registration rules, deregistration, conflict handling);
     §9.5 Hub Menu Structure; §9.6 Hub-Specific Menu Items; §9.7 Tool Menu
     Integration Rules (allowed categories, naming, visibility, ordering);
     §9.8 Hub–Tool Navigation Integration (Return to Hub, Relaunch, cross-tool);
     §9.9 Accessibility Requirements; §9.10 Telemetry Requirements;
     §9.11 Guardian Integration; §9.12 CI Enforcement; §9.13 Future Extensibility.
   - New constitutional section §10 UI Interaction Contract added:
     §10.1 Purpose; §10.2 Scope; §10.3 Interaction Principles (predictability,
     reversibility, visibility, non-blocking UI, accessibility, determinism);
     §10.4 Action Classification (Primary, Secondary, Destructive, Advanced);
     §10.5 Primary Action Rules; §10.6 Destructive Action Rules; §10.7
     Long-Running Operations; §10.8 Error Handling; §10.9 Navigation Rules;
     §10.10 Accessibility Rules; §10.11 CI Enforcement.
   - New constitutional section §11 CI Enforcement Specification added:
     §11.1 Purpose; §11.2 Scope; §11.3 CI Architecture Overview (five layers:
     Static Analysis, Schema Validation, Runtime Test, Matrix Compliance,
     Reporting); §11.4 Static Analysis Rules (TH, DR, CP, A11Y, ERR, STR, MEN,
     FNT, LYT, WRD); §11.5 Schema Validation Rules (menu registry, telemetry,
     preference, tool metadata); §11.6 Runtime Test Rules (INT, GRD, CE, PERF);
     §11.7 Matrix Compliance Rules; §11.8 Reporting Requirements (machine-
     readable JSON, human-readable Markdown, Hub dashboard); §11.9 Failure
     Conditions; §11.10 Future Extensibility.
   - New constitutional section §12 Tool Capability Matrix added: normative
     capability codes (TH, DR, CP, A11Y, PERF, ERR, GRD, TEL, STR, CE, HUB,
     MEN, NOM, FNT, LYT, WRD, INT, OPS, CI, L10N); reviewer-facing template;
     governance dashboard linkage.
   - New reference section §13 Harmonization Roadmap added: Phases 2–5
     documented for governance traceability.
Added sections: §7 (§7.1–§7.7), §9 (§9.1–§9.13), §10 (§10.1–§10.11),
  §11 (§11.1–§11.10), §12, §13
Modified sections: None
New spec documents: docs/menu-architecture-spec.md,
  docs/hub-menu-integration-spec.md, docs/ui-interaction-contract-spec.md,
  docs/ci-enforcement-spec.md, docs/tool-capability-matrix-template.md
New checklists: .specify/memory/checklist-menu-architecture-compliance.md,
  .specify/memory/checklist-hub-menu-integration-compliance.md,
  .specify/memory/checklist-ui-interaction-contract-compliance.md,
  .specify/memory/checklist-ci-enforcement-compliance.md

Previous Sync Impact Report
Version change: 1.32.0 → 1.33.0
Modified principles (2026-04-05 round-8 Q20 clarification applied):
   - Additional Technical & Quality Constraints §1 (Language & Framework)
     → EOL-planning sentence extended to reference §1.X for the formal
     definition of "planned".
   - §1.X new sub-chapter added, resolving TODO(EOL_PLANNING_DELIVERABLE)
     open since v1.11.0:
   - §1.X.1 — Purpose.
   - §1.X.2 — Definition of "Planned": milestone-bound, assigned migration
     issue in authoritative tracker; mental notes / un-milestoned issues
     explicitly forbidden.
   - §1.X.3 — Deadline: issue MUST exist ≥90 days before upstream EOL.
   - §1.X.4 — Responsibility: Maintainer / Release Steward.
   - §1.X.5 — CI Enforcement: eol.yaml config + per-dependency issue
     validation gate; CI MUST fail if any required issue is missing or
     incomplete.
   - §1.X.6 — Deterministic Reviewability: reviewer obligations.
   - TODO(EOL_PLANNING_DELIVERABLE): RESOLVED in v1.33.0.
Added sections: §1.X.1–§1.X.6
Modified sections: §1 EOL-planning sentence (added §1.X cross-ref);
  TODO(EOL_PLANNING_DELIVERABLE) inline comment resolved;
  historical Q&A entry added.
New spec document: docs/eol-planning-deliverable-spec.md
New checklist: .specify/memory/checklist-eol-planning-compliance.md

Previous Sync Impact Report
Version change: 1.31.0 → 1.32.0
Modified principles (2026-04-05 round-8 Q19 clarification applied):
   - §17 Lockout Prevention → audit-trail bullet extended to reference §17.Z
     for the mandatory CLI wrapper requirement.
   - §17.Z new sub-chapter added, resolving TODO(DIRECT_DB_AUDIT) open
     since v1.10.0:
   - §17.Z.1 — Purpose.
   - §17.Z.2 — Mandatory CLI Wrapper: authenticate, audit-before-modify,
     fail-closed; MUST be the sole path for direct DB modifications to
     protected accounts.
   - §17.Z.3 — Prohibited Mechanisms: manual procedures forbidden.
   - §17.Z.4 — Optional DB Triggers: supplemental only; MUST NOT replace
     CLI wrapper.
   - §17.Z.5 — Unified Audit Log: direct-DB entries MUST use same
     schema/table as application audit events.
   - §17.Z.6 — Failure Handling: fail-closed; modification blocked if
     audit cannot be written.
   - §17.Z.7 — Deterministic Reviewability: CI obligations.
   - TODO(DIRECT_DB_AUDIT): RESOLVED in v1.32.0.
Added sections: §17.Z.1–§17.Z.7
Modified sections: §17 audit-trail bullet (added §17.Z cross-ref);
  TODO(DIRECT_DB_AUDIT) inline comment resolved;
  historical Q&A entry added.
New spec document: docs/direct-db-audit-spec.md
New checklist: .specify/memory/checklist-direct-db-audit-compliance.md

Previous Sync Impact Report
Version change: 1.30.0 → 1.31.0
Modified principles (2026-04-05 round-8 Q18 clarification applied):
   - §21 Theme Security → theme-backup bullet now references §21.X for the
     formal definition of "system-wide theme change".
   - §21.X new sub-chapter added resolving the "system-wide theme change"
     definition ambiguity (five operations all MUST trigger backup):
   - §21.X.1 — Purpose.
   - §21.X.2 — Definition: five triggering operations enumerated;
     limited-to-token-edits interpretation explicitly forbidden.
   - §21.X.3 — Backup Requirement: backup MUST precede ANY listed operation;
     if backup fails, the operation MUST be aborted.
   - §21.X.4 — Backup Content: full snapshot of all presets, active preset,
     identifiers and names; partial snapshots MUST NOT satisfy the requirement.
   - §21.X.5 — Deterministic Reviewability: CI and reviewer obligations.
Added sections: §21.X.1–§21.X.5
Modified sections: §21 theme-backup bullet (added §21.X cross-ref);
  historical Q&A entry added.
New spec document: docs/theme-backup-trigger-spec.md
New checklist: .specify/memory/checklist-theme-backup-compliance.md

Previous Sync Impact Report
Version change: 1.29.0 → 1.30.0
Modified principles (2026-04-05 round-8 Q17 clarification applied):
   - §16 Session Management & Auditing → anomaly-detection bullet now
     references §16.Y for sliding-window, per-second, and immediate-
     detection requirements.
   - §16.Y new sub-chapter added resolving the "rolling 24-hour window"
     implementation ambiguity:
   - §16.Y.1 — Purpose.
   - §16.Y.2 — Sliding Window Requirement: window MUST be sliding;
     fixed-period or calendar-anchored windows MUST NOT be used.
   - §16.Y.3 — Time Resolution: window MUST be evaluated with per-second
     resolution; coarser resolutions MUST NOT be used.
   - §16.Y.4 — Immediate Detection: anomaly MUST be flagged at the
     attempt that crosses the threshold; deferred/batch detection
     MUST NOT replace per-attempt evaluation.
   - §16.Y.5 — Background Sweeps (Optional): MAY exist for analytics
     but MUST NOT replace per-attempt evaluation.
   - §16.Y.6 — Deterministic Reviewability: CI and reviewer obligations.
Added sections: §16.Y.1–§16.Y.6
Modified sections: §16 anomaly-detection bullet (added §16.Y cross-ref);
  historical Q&A entry updated to note §16.Y resolution.
New spec document: docs/anomaly-detection-sliding-window-spec.md
New checklist: .specify/memory/checklist-anomaly-detection-compliance.md

Previous Sync Impact Report
Version change: 1.28.0 → 1.29.0
Modified principles (2026-04-05 round-8 Q16 clarification applied):
   - §IX File Validation & Content Integrity → new sub-chapter §IX.X added,
     formally defining the boundary of the "written by RFU itself" validation
     exemption.
   - §IX.X.1 — Purpose: exemption applies only to files that never cross
     trust boundaries.
   - §IX.X.2 — Same-Process, Same-Instance Requirement: exemption requires
     same tool instance, same process, same session, consumed by same
     instance without exposure to any other component.
   - §IX.X.3 — Boundaries That Invalidate the Exemption: process boundary,
     tool boundary, plugin boundary, session boundary, IPC, shared temp
     directories, background/scheduled tasks—all require full validation.
   - §IX.X.4 — Plugin-Written Files: ComponentGuardian-registered plugins
     never qualify for the exemption; all plugin output MUST be validated.
   - §IX.X.5 — Cross-Session and Cross-Process Files: always validated
     regardless of origin.
   - §IX.X.6 — Exemption Guard Pattern: the exemption MUST be implemented
     via a tightly scoped helper with an in-process registry; the helper
     MUST NOT be accessible from plugins or cross-tool code.
   - §IX.X.7 — Deterministic Reviewability: CI and reviewers MUST verify
     exemption scope, plugin validation, cross-boundary validation,
     absence of shared-temp-dir bypasses, and test coverage.
Added sections: §IX.X.1–§IX.X.7
Modified sections: §IX File Validation & Content Integrity (§IX.X
  sub-chapter appended); historical Q&A entry updated to reflect resolution.
New spec document: docs/file-validation-exemption-spec.md
New checklist: .specify/memory/checklist-file-validation-exemption-compliance.md

Previous Sync Impact Report
Version change: 1.27.0 → 1.28.0
Modified principles (2026-04-05 round-8 Q15 clarification applied):
   - §VIII Privacy, PII Protection & Data Minimization → new sub-chapter
     §VIII.X added, defining PII scan result delivery requirements.
   - §VIII.X.1 — Purpose: PII results must be visible in a timely,
     non-coercive manner; no silent accumulation of sensitive data.
   - §VIII.X.2 — User-Initiated Scans: results MAY be displayed inline
     within the scan panel; proactive surfacing is NOT required.
   - §VIII.X.3 — Background & Scheduled Scans: results MUST be surfaced
     proactively via persistent banner, notification badge, non-modal
     alert, or dashboard ribbon; modals and forced-focus overlays
     MUST NOT be used.
   - §VIII.X.4 — User Agency & Remediation: PII MUST NOT be deleted
     automatically; explicit user confirmation required regardless of
     scan type.
   - §VIII.X.5 — Indicator Persistence: proactive indicators (banner,
     badge, ribbon) MUST remain visible until the user acknowledges or
     reviews results; transient auto-dismissing toasts do not satisfy
     this requirement.
   - §VIII.X.6 — Deterministic Reviewability: CI and reviewers MUST
     verify proactive surfacing for background scans, inline display
     for user-initiated scans, absence of modals for background scans,
     indicator persistence, and explicit remediation confirmation.
Added sections: §VIII.X.1–§VIII.X.6
Modified sections: §VIII Privacy, PII Protection & Data Minimization
  (§VIII.X sub-chapter appended).
Follow-up TODOs resolved: none new
New spec document: docs/pii-scan-ux-spec.md
New checklist: .specify/memory/checklist-pii-scan-ux-compliance.md

Previous Sync Impact Report
Version change: 1.26.0 → 1.27.0
Modified principles (2026-04-05 round-8 Q14 clarification applied):
   - §16 Session Management & Auditing → new sub-chapter §16.X added,
     resolving TODO(AUDIT_ORIGIN_METADATA). Minimum required fields for
     ALL audit events: actor_username, session_id, device_id
     (pseudonymized), app_instance_id.
   - §16.X.3 — Additional fields for network-originating events:
     client_ip_hash (pseudonymized; raw IP MUST NOT be stored),
     user_agent, protocol.
   - §16.X.4 — Privacy Constraints: raw IP addresses, hostnames,
     OS-level usernames, hardware serial numbers, and non-pseudonymized
     device identifiers MUST NOT be stored in audit logs.
   - §16.X.5 — Field Consistency: all event types MUST use consistent
     field names, types, and structure for origin metadata.
   - §16.X.6 — Deterministic Reviewability: CI and reviewers MUST verify
     required fields, absence of prohibited PII, pseudonymization
     implementation, and consistency across all event types.
   - §16.X.7 — Backward Compatibility: existing logs MAY omit new fields;
     all new events generated after this amendment MUST comply fully.
   - TODO(AUDIT_ORIGIN_METADATA): RESOLVED — closed in §16.X.
Added sections: §16.X.1–§16.X.7
Modified sections: §16 Session Management & Auditing (§16.X sub-chapter
  appended; RESOLVED comment added); TODO list item 16 marked resolved.
Follow-up TODOs resolved: TODO(AUDIT_ORIGIN_METADATA) ✓ CLOSED
Structural change: §16.X is a new normative sub-chapter with seven
  subsections constitutionally prescribing origin metadata requirements
  for all audit events.
Updated documents: docs/audit-origin-metadata-spec.md (new — canonical
  spec, reference implementation, CI tests T1–T9, migration Steps 1–3);
  .specify/memory/checklist-audit-origin-metadata-compliance.md (new —
  reviewer checklist Sections A–F).

Previous Sync Impact Report
Version change: 1.25.0 → 1.26.0
Modified principles (2026-04-04 round-8 Q13 clarification applied):
   - §VII Session Controls narrative updated: "crash recovery" now references
     §G.13 and §VII.W for normative clearing requirements.
   - §G Normative Glossary → one new normative entry added:
     §G.13 Crash sentinel: dirty/clean state table; lifecycle rules (dirty on
     startup, clean only on graceful shutdown, missing → treated as dirty);
     required properties (process-external, readable at earliest startup);
     deterministic testability requirement.
   - §VII.W Crash-Recovery Session Clearing → six new subsections:
     §VII.W.1 Purpose (secrets volatile-only; MUST NOT survive process death);
     §VII.W.2 Crash Handler Clearing (best-effort; MUST NOT be relied upon);
     §VII.W.3 Startup-Time Clearing (mandatory 4-step sequence: read sentinel,
       set dirty, if not clean then purge+refuse restore, then proceed);
     §VII.W.4 Crash Sentinel (process-external; dirty on startup; clean only
       on graceful shutdown; missing → dirty; readable before any session logic);
     §VII.W.5 OS-Level Persistence Protections (swap: mlock/VirtualLock;
       crash dumps: disabled or non-dumpable; core files: disabled/restricted;
       hibernation: treated as crash dumps; undocumented omissions prohibited);
     §VII.W.6 Deterministic Reviewability (CI MUST verify sentinel logic, unconditional
       startup clearing, no session restore after crash, OS persistence exclusions,
       test coverage).
   - TODO(CRASH_RECOVERY_SESSION): RESOLVED — closed in §G.13 and §VII.W.
Added sections: §G.13 Crash sentinel, §VII.W.1–§VII.W.6
Modified sections: §VII Session Controls ("crash recovery" now references §G.13
  and §VII.W); §G.12 duplicate entry removed.
Follow-up TODOs resolved: TODO(CRASH_RECOVERY_SESSION) ✓ CLOSED
Structural change: §VII.W is a new normative sub-chapter with six subsections
  constitutionally prescribing crash-recovery session clearing. The prior
  "cleared on crash recovery" phrase is now fully normatively defined.
Updated documents: docs/crash-recovery-spec.md (new — canonical spec,
  reference implementation, CI tests T1–T9, migration Steps 1–5);
  .specify/memory/checklist-crash-recovery-compliance.md (new — reviewer
  checklist Sections A–E).
Also fixed: duplicate §G.12 entry removed from Glossary.

Previous Sync Impact Report
Version change: 1.24.0 → 1.25.0
Modified principles (2026-04-04 round-8 Q12 clarification applied):
   - §G Normative Glossary → one new normative entry added:
     §G.12 is_protected scope: defines the six protected operations (deletion,
     deactivation, suspension, admin password reset, role change, username
     change); self-service exception; error contract (protected_account_error +
     audit log); enforcement layer requirements.
   - §DW §17 Lockout Prevention → body text updated to reference §G.12 and
     §DW17.X; §DW17.X new sub-section group added with six subsections:
     §DW17.X.1 Purpose;
     §DW17.X.2 Password Reset Protection (self-service permitted; all other
       resets blocked with protected_account_error);
     §DW17.X.3 Role Change Protection (escalation and demotion forbidden;
       role immutable after creation);
     §DW17.X.4 Username Protection (username immutable at all layers; DB
       constraints recommended);
     §DW17.X.5 Audit Logging for Blocked Operations (all five fields required;
       silent failures PROHIBITED);
     §DW17.X.6 Deterministic Reviewability (CI MUST verify all six blocked
       operations, self-service pass, audit log completeness, no bypass paths).
   - §VII Always-Available Accounts narrative updated: is_protected now
     references §G.12 and §DW17.X; all six blocked operations listed.
   - §VII Account Suspension updated: is_protected sentence now lists all six
     blocked operations and references §G.12 and §DW17.X.
   - TODO(IS_PROTECTED_SCOPE): RESOLVED — closed as HTML comment in §DW17.
Added sections: §G.12 is_protected scope, §DW17.X.1–§DW17.X.6
Modified sections: §DW §17 Lockout Prevention, §VII Always-Available Accounts,
  §VII Account Suspension
Follow-up TODOs resolved: TODO(IS_PROTECTED_SCOPE) ✓ CLOSED
Structural change: §DW17 now has a normative sub-section group (§DW17.X) with
  six subsections constitutionally prescribing the full scope of is_protected.
  The prior text only covered deletion/deactivation; password reset, role
  change, and username change are now normatively blocked.
Updated documents: docs/is-protected-spec.md (new — canonical spec, reference
  implementation, CI tests T1–T9, migration Steps 1–6);
  .specify/memory/checklist-is-protected-compliance.md (new — reviewer
  checklist Sections A–F).

Previous Sync Impact Report
Version change: 1.23.0 → 1.24.0
Modified principles (2026-04-04 round-8 Q11 clarification applied):
   - §VII Identity & Access Control → §VII Session Controls: uniform 30-minute
     default idle timeout replaced with role-differentiated defaults per §G.11
     (admin 10 min, dev 15 min, user 30 min, readonly 45 min); 60-minute
     ceiling and admin override rules added; reference to §VII.Z inserted.
   - §G Normative Glossary → one new normative entry added:
     §G.11 Role-differentiated idle timeout defaults: per-role table (admin 10,
     dev 15, user 30, readonly 45); 60-minute ceiling; override logging rule;
     rationale.
   - §VII.Z Idle Timeout Requirements → five new subsections:
     §VII.Z.1 Purpose (defaults MUST reflect privilege level; uniform default
       MUST NOT be applied);
     §VII.Z.2 Role-Differentiated Default Idle Timeouts (per-role table;
       single global constant MUST NOT be used; privileged roles MUST have
       shorter or equal defaults);
     §VII.Z.3 Maximum Timeout Ceiling (60-minute ceiling; explicit admin
       override requires deliberate action + audit log entry; 8-hour absolute
       ceiling unchanged);
     §VII.Z.4 Administrative Overrides (admins MAY configure per-role values
       subject to §VII.Z.3; all overrides MUST be logged);
     §VII.Z.5 Deterministic Reviewability (CI MUST verify role-differentiated
       defaults, privilege ordering, no global constant, override logging,
       test coverage).
Added sections: §G.11 Role-differentiated idle timeout defaults, §VII.Z.1–§VII.Z.5
Modified sections: §VII Session Controls (uniform 30-min sentence replaced;
  §G.11 and §VII.Z cross-references added)
Removed sections: None
Follow-up TODOs resolved: None
Structural change: §VII.Z is a new normative sub-chapter with five subsections
  prescribing role-based idle timeout defaults; the prior single uniform
  30-minute default is constitutionally superseded.
Updated documents: docs/idle-timeout-spec.md (new — canonical spec, default
  table, Python reference implementation, CI tests T1–T6, migration Steps
  1–6, session lifecycle diagram);
  .specify/memory/checklist-idle-timeout-compliance.md (new — reviewer
  checklist Sections A–E).

Previous Sync Impact Report
Version change: 1.22.0 → 1.23.0
Modified principles (2026-04-04 round-8 Q10 clarification applied):
   - §VII Identity & Access Control → "FIDO2 hardware token" resolved to
     "FIDO2 roaming authenticator". §VII MFA narrative updated with explicit
     §G.10 and §VII.Y references; platform authenticators (§G.10) noted as
     convenience factors that MUST NOT alone satisfy the enrollment requirement.
   - §G Normative Glossary → one new normative entry added:
     §G.10 FIDO2 authenticator classes: defines "FIDO2 roaming authenticator"
     (detachable, cross-device; satisfies enrollment requirement) and "FIDO2
     platform authenticator" (device-bound, non-portable; MUST NOT satisfy
     enrollment requirement alone; pairing rule with roaming/TOTP prescribed).
   - §VII.Y FIDO2 Authenticator Requirements → six new subsections:
     §VII.Y.1 Definitions (roaming vs platform; "hardware token" alias resolved);
     §VII.Y.2 Offline-Capable MFA Requirement (roaming + TOTP qualify; platform
       does not qualify alone);
     §VII.Y.3 Platform Authenticator Pairing (platform enrollment MUST be paired
       with roaming or TOTP; sole-platform accounts MUST NOT exist);
     §VII.Y.4 Recovery and Portability (recovery path via roaming/TOTP MUST exist;
       platform credentials MUST NOT be exported as portable artifacts);
     §VII.Y.5 Enrollment and UI Clarity (roaming MUST be labelled "Security Key";
       platform MUST be labelled "This Device"; "hardware token" label for
       platform MUST NOT be used);
     §VII.Y.6 Deterministic Reviewability (CI MUST verify classification,
       enrollment rules, platform-pairing enforcement, recovery paths, no
       portable platform export).
Added sections: §G.10 FIDO2 authenticator classes, §VII.Y.1–§VII.Y.6
Modified sections: §VII Multi-Factor Authentication (narrative terminology
  updated: "FIDO2 hardware token" → "FIDO2 roaming authenticator (§G.10)")
Removed sections: None
Follow-up TODOs resolved: None
Structural change: §VII.Y is a new normative sub-chapter with six subsections
  prescribing FIDO2 authenticator classification and enforcement; all prior
  "FIDO2 hardware token" references in normative body text now point to §G.10.
Updated documents: docs/fido2-spec.md (new — canonical FIDO2 spec, WebAuthn
  pseudocode reference, CI test suite T1–T7, migration Steps 1–7, enrollment
  diagram);
  .specify/memory/checklist-fido2-compliance.md (new — reviewer checklist
  Sections A–G).

Previous Sync Impact Report
Version change: 1.21.0 → 1.22.0
Modified principles (2026-04-04 round-8 Q9 clarification applied):
   - §VII Identity & Access Control → TOTP implementation now constitutionally
     prescribed. §VII MFA narrative updated to reference §G.9 (TOTP default
     profile) and §VII.X (Offline-Capable MFA Requirements).
   - §G Normative Glossary → one new normative definition added:
     §G.9 TOTP default profile (HMAC-SHA1 / 6 digits / 30 s / ±1 step;
     normative provisioning URI form; HOTP explicitly excluded).
   - §VII.X Offline-Capable Multi-Factor Authentication (MFA) Requirements →
     seven new subsections:
     §VII.X.1 Mandatory Standard (RFC 6238 TOTP MUST; HOTP MUST NOT count
       as enrolled method);
     §VII.X.2 Default TOTP Profile (§G.9; SHA-1/6/30s/±1; default MUST be
       accepted; stronger variants MAY be added but MUST NOT replace default);
     §VII.X.3 Enrollment Requirements (secret compatible with §G.9;
       provisioning URI/QR with default profile; secret encrypted at rest);
     §VII.X.4 Verification Requirements (drift tolerance ±1 step; reject
       unsupported configs unless explicitly enabled);
     §VII.X.5 Backup and Recovery Codes (MAY exist as emergency fallback;
       MUST NOT count as enrolled method; sufficient entropy; stored
       securely);
     §VII.X.6 Export and Import of MFA Configuration (TOTP secret preserved;
       importers MUST NOT alter secret or profile; default profile
       interoperability maintained after import);
     §VII.X.7 Deterministic Reviewability (CI MUST verify RFC 6238
       compliance, default profile support, no HOTP enrollment, no backup-
       code-as-MFA, correct drift tolerance, test coverage).
Added sections: §G.9 TOTP default profile, §VII.X.1–§VII.X.7
Modified sections: §VII Multi-Factor Authentication (narrative updated with
  §G.9 and §VII.X cross-references)
Removed sections: None
Follow-up TODOs resolved: None
Structural change: §VII now has a normative sub-chapter (§VII.X) with seven
  subsections prescribing TOTP interoperability requirements; prior §VII MFA
  text was TOTP-algorithm-agnostic.
Updated documents: docs/totp-spec.md (new — canonical TOTP spec, reference
  implementation, CI test suite T1–T5, migration Steps 1–8, enrollment and
  verification diagrams);
  .specify/memory/checklist-totp-compliance.md (new — reviewer checklist
  Sections A–G).

Previous Sync Impact Report
Version change: 1.20.0 → 1.21.0
Modified principles (2026-04-04 round-8 Q8 clarification applied):
   - Development Workflow §13 Preference Portability Gate → "identical
     preference state" is now constitutionally defined. Four new subsections:
     §DW13.1 Definition of Identical Preference State (semantic fields only:
     preference_category, preference_key, preference_value, value_type);
     §DW13.2 Excluded Fields (created_at, modified_at, imported_at,
     record_id, version, migration_flags, and all other implementation-
     generated metadata MUST NOT be compared);
     §DW13.3 Deterministic Reviewability (CI MUST compare semantic fields
     only; MUST NOT compare metadata; MUST reject silent coercion);
     §DW13.4 Ordering and Formatting (record order, JSON formatting, and
     timestamp differences MUST NOT cause a fidelity failure).
   - §G Normative Glossary → one new normative definition added:
     §G.8 Round-trip fidelity (the guarantee that export then import
     preserves exactly the four semantic preference fields; metadata excluded).
Added sections: §G.8 Round-trip fidelity, §DW13.1–§DW13.4
Modified sections: Development Workflow §13 Preference Portability Gate
Removed sections: None
Follow-up TODOs resolved: None
Structural change: Development Workflow §13 now has four normative
  subsections defining the scope and CI requirements of round-trip fidelity;
  prior vague "identical preference state" sentence is now backed by §DW13.1.
Updated documents: docs/round-trip-fidelity-spec.md (new — canonical field
  constants, CI test suite T1–T5, migration patch Steps 1–5, diagram);
  checklist-round-trip-fidelity.md (new — reviewer checklist Sections A–F).

Previous Sync Impact Report
Version change: 1.19.0 → 1.20.0
Modified principles (2026-04-04 round-8 Q7 clarification applied):
   - §VI Portability → export encryption is now constitutionally prescribed.
     Encryption algorithm, KDF, minimum parameters, metadata, and
     passphrase requirement are all normative. Seven new subsections added:
     §VI.4.1 Mandatory Encryption Algorithm (AES-256-GCM — AEAD required;
     weaker algorithms or non-AEAD modes MUST NOT be used);
     §VI.4.2 Key Derivation (Argon2id — memory ≥ 64 MB, iterations ≥ 3,
     parallelism ≥ 1, salt ≥ 16 bytes);
     §VI.4.3 Metadata Requirements (algorithm name, KDF name, KDF
     parameters, salt, nonce, version — all in plaintext header);
     §VI.4.4 Authenticated Encryption (GCM auth tags MUST be verified
     before accepting decrypted data);
     §VI.4.5 Passphrase Requirement (key MUST be passphrase-derived;
     application-managed keys MUST NOT be used);
     §VI.4.6 Interoperability (all implementations MUST read exports
     produced by any conforming implementation);
     §VI.4.7 Deterministic Reviewability (CI and reviewers MUST verify
     algorithm, KDF parameters, metadata, and no plaintext leakage).
   - §VI Portability body text updated: "Export artifacts MUST encrypt
     sensitive preference values" now references §VI.4 explicitly.
   - §G Normative Glossary → one new normative definition added:
     §G.7 Export encryption envelope (the portable, versioned, plaintext-
     header JSON structure wrapping AES-256-GCM ciphertext per §VI.4).
   - TODO(PORTABILITY_FORMAT): partially resolved — encryption envelope
     format is now constitutionally prescribed. Remaining scope (full
     JSON/YAML schema publication) deferred until portability.py stabilizes.
Added sections: §G.7 Export encryption envelope, §VI.4 (§VI.4.1–§VI.4.7)
Modified sections: §VI Portability (body text encryption sentence updated)
Removed sections: None
Follow-up TODOs resolved: None (TODO(PORTABILITY_FORMAT) partially addressed;
  encryption envelope prescribed — schema publication still pending)
Structural change: §VI now has export-encryption subsection group §VI.4;
  §VI.1–§VI.3 (skipped-item summary, dry-run, reviewability) unchanged.
Updated documents: docs/export-encryption-spec.md (new — full spec with
  envelope format, reference implementation, CI test spec, migration plan);
  checklist-export-encryption-compliance.md (new — reviewer checklist
  Sections A–F).

Previous Sync Impact Report
Modified principles (2026-04-04 round-8 Q6 clarification applied):
   - §V Simplicity & Extensible Modularity → health-check polling interval
     now constitutionally bounded. Five new subsections added:
     §V.6.1 Minimum Polling Frequency (at least once every 5 seconds
     during active use); §V.6.2 Maximum Polling Frequency (no more
     frequently than once every 500 milliseconds); §V.6.3 Implementation
     Flexibility (fixed intervals, jitter, backoff, or adaptive strategies
     all permitted provided bounds are respected); §V.6.4 Deterministic
     Reviewability (bounds MUST be testable and CI-enforceable);
     §V.6.5 Resolution of TODO(GUARDIAN_POLL_INTERVAL) (this TODO is
     formally closed by this section; no implementation-defined intervals
     outside the constitutional bounds are permitted).
   - §V body text updated: stale reference to
     "Q6 / TODO(GUARDIAN_POLL_INTERVAL)" replaced with normative reference
     to §V.6 with inline bound summary.
Added sections: §V.6 (§V.6.1–§V.6.5)
Modified sections: §V Simplicity & Extensible Modularity (body text)
Removed sections: None
Follow-up TODOs resolved: TODO(GUARDIAN_POLL_INTERVAL) (closed by §V.6.5)
Structural change: §V now has complete lifecycle specification:
  §V.1 Recovery Eligibility; §V.2 Recovery Trigger; §V.3 Recovery
  Behavior; §V.4 Recovery Logging; §V.5 Deterministic Reviewability;
  §V.6 Health-Check Polling Interval (§V.6.1–§V.6.5).
Updated documents: docs/component-guardian-spec.md (Section 3.2 polling
  bounds filled; Section 10 polling reference implementation added);
  checklist-component-guardian-recovery.md (Section H Polling Interval
  Compliance added).

Previous Sync Impact Report
Sync Impact Report
Version change: 1.17.0 → 1.18.0
Modified principles (2026-04-04 round-8 Q5 clarification applied):
   - §V Simplicity & Extensible Modularity → recovery from degraded state
     now explicitly defined. Five new subsections added:
     §V.1 Recovery Eligibility (component MAY recover at runtime);
     §V.2 Recovery Trigger (only health_check() returning True; no developer
     or user action required); §V.3 Recovery Behavior (resume normal
     operation; clear degraded indicators; re-enter polling cycle);
     §V.4 Recovery Logging (structured log entry required: timestamp,
     component id, previous state, new state, reason); §V.5 Deterministic
     Reviewability (both degradation and recovery MUST be testable via
     unit tests and observable via logs). Existing §V body text updated:
     sentence about "The polling interval" updated to remove stale
     TODO(GUARDIAN_POLL_INTERVAL) reference (Q6 will resolve that TODO;
     for Q5 the sentence is updated to acknowledge that the polling
     interval bounds will be constitutionally constrained).
Added sections: §V.1–§V.5 (ComponentGuardian recovery subsections)
Modified sections: §V Simplicity & Extensible Modularity
Removed sections: None
Follow-up TODOs resolved: None (TODO(GUARDIAN_POLL_INTERVAL) remains for Q6)
New supporting documents: checklist-component-guardian-recovery.md,
  docs/component-guardian-spec.md.

Previous Sync Impact Report
Sync Impact Report
Version change: 1.16.0 → 1.17.0
Modified principles (2026-04-04 round-8 Q4 clarification applied):
   - §G Normative Glossary → one new normative definition added:
     §G.6 Critical engine (a module meeting one or more of five criteria:
     irreversible/destructive operations; large-scale/batch operations;
     high-impact data transformations; untrusted external input;
     security-sensitive operations). The parenthetical examples (duplicate
     detection, secure delete, batch processors) are now explicitly
     illustrative and not exhaustive. New examples added: compression,
     PDF processors, network sync, archive extractors, OCR engines.
   - §III Test-Driven Quality & Observability → parenthetical "(duplicate
     detection, secure delete, batch processors)" replaced with "(as
     defined in §G.6)"; existing parenthetical examples preserved as
     illustrative note.
   - §III.1 Critical Engine Classification Authority → new subsection:
     any maintainer MAY classify a module as a critical engine during PR
     review; classification MUST be recorded in the module metadata;
     PR authors MAY self-declare but maintainer has final authority;
     CI enforces stricter test suite when classification is present.
Added sections: §G.6 Critical engine, §III.1 Classification Authority
Modified sections: §III Test-Driven Quality & Observability
Removed sections: None
Follow-up TODOs resolved: None
Structural change: §III parenthetical list replaced with §G.6 reference;
  new §III.1 subsection governs classification governance. New supporting
  documents: checklist-critical-engine-classification.md,
  docs/critical-engines.md.

Previous Sync Impact Report
Sync Impact Report
Version change: 1.15.0 → 1.16.0
Modified principles (2026-04-03 round-8 Q3 clarification applied):
   - §G Normative Glossary → one new normative definition added:
     §G.5 Headless HMAC token (cryptographically signed single-use token
     used as the headless-mode alternative to interactive confirmation for
     destructive operations; five mandatory attributes: HMAC-SHA256 or
     stronger, secure key storage, ≤5-minute validity, single-use,
     dual audit entries). The §15 credential reset token is explicitly
     distinguished from §G.5.
   - §II Safety & Data Integrity → new §II.5 Headless HMAC Token
     Requirements block added (six subsections: §II.5.1 Algorithm;
     §II.5.2 Key Storage; §II.5.3 Token Structure and Validity;
     §II.5.4 Single-Use Requirement; §II.5.5 Audit Logging;
     §II.5.6 Equivalence to Interactive Confirmation). Opening paragraph
     of §II updated to cross-reference §G.5 and §II.5. §II.2 closing
     parenthetical updated to reference §II.5.
   - §15 Credential Reset → distinction note added: §15 reset token
     (1-hour validity, out-of-band account recovery) is explicitly
     separate from §G.5 headless HMAC token (5-minute validity,
     destructive-operation authorization).
   - §16 Session Management & Auditing → HMAC token issuance and
     redemption events (§II.5.5) noted as additional auditable event
     types subject to the ≥ 365-day retention requirement.
Added sections: §G.5 Headless HMAC token, §II.5 (§II.5.1–§II.5.6)
Modified sections: §II Safety & Data Integrity (opening paragraph, §II.2),
  §15 Credential Reset, §16 Session Management & Auditing
Removed sections: None
Follow-up TODOs resolved: None
Structural change: §II expanded with §II.5 (six labeled subsections
  §II.5.1–§II.5.6); cryptographic constraints for headless tokens are now
  normative and CI-enforceable.

Previous Sync Impact Report
Sync Impact Report
Version change: 1.14.0 → 1.15.0
Modified principles (2026-04-03 round-8 Q2 clarification applied):
   - §G Normative Glossary → two new normative definitions added:
     §G.3 Side effect (any persistent change to user-visible state; internal
     RFU bookkeeping excluded); §G.4 Destructive operation (a side-effect
     operation that is irreversible or hard to reverse). Both terms were
     previously used in §II without formal definition, making dry-run coverage
     unenforceable and unverifiable.
   - §II Safety & Data Integrity → restructured with four explicit subsections:
     §II.1 Dry-run Requirement (side-effect operations per §G.3 MUST expose
     dry-run; enumerate changes; MUST NOT perform them; present §G.1 summary;
     same interface as real operation); §II.2 Confirmation Requirement
     (destructive operations per §G.4 additionally MUST require user-visible
     blocking confirmation; summarize irreversible consequences; list affected
     items); §II.3 Internal Operations Excluded (internal bookkeeping MUST NOT
     be classified as side-effect operations and MUST NOT require dry-run or
     confirmation); §II.4 CI Enforcement (CI MUST verify all three obligations).
     First paragraph updated to reference §G.4 for "destructive operations."
   - §VI User Preference Management → Portability skipped-item summary labeled
     §VI.1; §VI.2 Dry-run Integration added (for all side-effect ops, dry-run
     MUST include §VI.1 skipped-item summary, listed separately from changes);
     §VI.3 Deterministic Reviewability added (summary format consistent across
     apps; CI detectable).
Added sections: §G.3 Side effect, §G.4 Destructive operation
Modified sections: §II Safety & Data Integrity, §VI Portability
Removed sections: None
Follow-up TODOs resolved: None
Structural change: §II expanded from single block to four labeled subsections
  (§II.1–§II.4); all prior uses of "side effect" now carry §G.3 cross-reference;
  all prior uses of "destructive operation" now carry §G.4 cross-reference.

Previous Sync Impact Report
Version change: 1.13.0 → 1.14.0
Modified principles (2026-04-03 round-8 Q1 clarification applied):
   - §G Normative Glossary → new section added with two normative definitions:
     §G.1 User-visible (foreground, cannot-reasonably-be-missed, zero
     navigation required; status bars, badges, collapsible panels do NOT
     satisfy); §G.2 User-discoverable (reachable within one navigation step,
     no external docs, no hidden features; multi-level menus, logs, and
     developer consoles do NOT satisfy). These terms were previously used
     across multiple sections (§VI, §15, DW §6) without formal definition.
   - VI. User Preference Management → Portability skipped-item summary now
     explicitly references §G.1; behavioral constraints added: summary MUST
     appear in active foreground UI automatically, MUST NOT require navigation,
     MUST enumerate each item and reason, MUST be verifiable by CI via
     widget-tree inspection.
   - §15 (Additional Constraints) → Credential Reset user-visible offline
     warning now explicitly references §G.1; log panel / status bar placement
     stated as insufficient.
   - Development Workflow §6 → Documentation Gate "user-visible behavior"
     now explicitly references §G.1.
Added sections: §G Normative Glossary
Modified sections: §VI Portability, §15 Credential Reset, Development Workflow §6
Removed sections: None
Follow-up TODOs resolved: None
Structural change: §G Normative Glossary placed before §I Core Principles;
  all three prior uses of "user-visible" now carry a §G.1 cross-reference.

Previous Sync Impact Report
Version change: 1.12.0 → 1.13.0
Modified principles (2026-03-31 round-8 clarification session):
   - I. Cross-Platform Consistency → OS-infeasible designation gate added:
     only maintainers may approve; written justification required in PR;
     capabilities matrix MUST be updated.
   - II. Safety & Data Integrity → dry-run discoverability strengthened from
     "user-discoverable" to "visible UI element before any action begins";
     documentation-only is insufficient. Dry-run surface check added to
     Additional Constraints §5 coverage gates.
   - VI. User Preference Management → conflict detection clarified: uses live
     stored DB value; absent key = new key, not a conflict. Export format
     constrained to human-readable structured text only (JSON, YAML, TOML, or
     equivalent); binary and proprietary formats prohibited; exports MUST be
     portable without vendor-specific parsers.
   - VII. Identity & Access Control → Session Controls: admins MAY now also
     set a deployment-wide minimum idle timeout; users MUST choose within the
     admin-defined range. Account Suspension: dev-role MUST NOT suspend
     admin-role accounts; is_protected accounts MUST NOT be suspended under
     any circumstances. MFA: MFA-before-activation requirement confirmed as
     system-enforced (system rejects activation attempt without enrolled MFA).
   - VIII. Privacy → PII scan: system default scan scope REQUIRED; admins MAY
     configure deployment-wide default; users MAY override unless mandatory.
     Anonymization mode display: displaying mode inside confirmation dialog is
     constitutionally sufficient; separate prior step not required.
   - IX. File Validation → per-open() validation clarified: validate once per
     file per operation; subsequent opens MAY use cached result unless file
     has changed.
   - Additional Constraints §5 → dry-run surface check added as a named
     coverage gate.
   - Additional Constraints §6 → "segments" wording updated to match §IV:
     "UI thread blocking MUST NOT reach or exceed 100ms for any continuous
     blocked period."
   - Additional Constraints §7 → 44 × 44 px clarified as logical
     (device-independent) pixels, consistent with WCAG 2.1 SC 2.5.8.
   - Additional Constraints §14 → §14 parenthetical corrected: `breakglass`
     removed as a lifecycle transition target for regular accounts; regular
     accounts MUST NEVER transition to `breakglass` status.
   - Additional Constraints §15 → breached-password denylist source defined:
     implementation-defined with three mandatory constraints: offline local
     denylist required; k-anonymity required if external API used; full
     passwords and full hashes MUST NEVER be transmitted externally.
   - Additional Constraints §18 → annual drill: responsible party added
     (admin-role); documented results format added (/test-evidence/breakglass/
     with minimum required fields); TODO(BREAKGLASS_DRILL_DOCS) resolved.
     Rotation confirmation: system-only hash detection insufficient; explicit
     admin/dev action required; audit entry mandatory.
   - Additional Constraints §21 → theme backup granularity added: "a backup"
     = full snapshot of all system-wide presets; "five most recent" = five
     most recent full snapshots (not per-preset records).
   - Additional Constraints §22 → repair instruction minimum content defined:
     MUST include corrupted database path/identifier, required resolution
     action, and UI path or CLI command.
   - Development Workflow §3 → security-sensitive / performance-critical
     classification authority defined: any maintainer may classify; CI may
     enforce path-based triggers; PR authors cannot override.
Added sections: None
Modified sections: None
Removed sections: None
Follow-up TODOs resolved: TODO(BREAKGLASS_DRILL_DOCS)
Structural change: None

Previous Sync Impact Report (1.11.0 → 1.12.0)
Version change: 1.11.0 → 1.12.0
Modified principles (2026-03-31 round-7 clarification session):
   - II. Safety & Data Integrity → dry-run discoverability requirement added;
     confirmation-tier boundary clarified: §II governing rule is single
     explicit confirmation; §VIII two-step elevated confirmation is exclusive
     to irreversible anonymization operations.
   - IV. Performance & Scalability → §IV 100ms UI-thread wording unified with
     §6 governing gate: "MUST NOT reach or exceed 100ms".
   - VI. User Preference Management → theming named-preset ownership scopes
     defined (personal = user-and-above; system-wide = admin/dev only; user
     accounts may not delete or modify system-wide presets); Portability role
     permissions added (all roles may export; only user/admin/dev may import);
     infeasible-migration fallback: skip incompatible keys, import compatible
     keys, present user-visible summary of skipped items.
   - VII. Identity & Access Control → Session Controls: 60-second mandatory
     idle-timeout warning added before forced logout. Break-Glass: alert
     targets extended from admin-role only to admin-role AND dev-role accounts.
   - VIII. Privacy → anonymization mode-selection UI requirements:
     no pre-selection; explicit user choice before tool activates; selected
     mode visible before execution; implementation-defined per tool.
     Confirmation phrase for irreversible operations made implementation-
     defined per tool (shown to user, typed exactly as displayed).
   - IX. File Validation → Policy Enforcement: rejection reason must identify
     specific policy rule; UI pattern implementation-defined. Failure Modes:
     unrecognized-type approval specified as one-step confirmation dialog only.
   - Additional Constraints §7 → "key actions" obligation: each tool defines
     its own list in implementation docs. Four new constitutional minimums
     added: logical tab/focus order; accessible labels for interactive
     controls; reduced-motion support; ≥ 44 × 44 px touch/pointer target size.
   - Additional Constraints §14 → is_blocked and login_attempts MUST be
     atomically reset on transition out of active; account returns in clean
     unblocked state when restored to active.
   - Additional Constraints §18 → break-glass alert targets extended to
     admin-role AND dev-role; post-use rotation enforcement: enablement
     mechanism (CLI flag/env var) automatically invalidated after session;
     re-enablement blocked until rotation confirmed complete.
   - Additional Constraints §21 → theme backups: stored separately from live
     preference store; last 5 backups minimum; built-in UI restore action
     required; CLI optional.
   - Additional Constraints §22 → corrupted signature DB: affected tools
     remain visible in launcher; opening triggers hard error dialog with
     repair instructions (not degraded state).
   - Development Workflow §12 → auth verification artifacts MUST be stored
     in /test-evidence/auth/ repository directory; clearly annotated; format
     implementation-defined.
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)
Follow-up TODOs (new in 1.12.0): None
Structural change: Clarifications section converted to reverse-chronological
  order (newest first).

Previous Sync Impact Report (1.10.0 → 1.11.0):
Version change: 1.10.0 → 1.11.0
Modified principles (2026-03-12 round-6 clarification session):
   - VII. Identity & Access Control → MFA requirement extended from
     always-available accounts to ALL accounts with role = admin or role = dev;
     Account Suspension subsection added (suspended status lifecycle: set/unset
     by admin or dev role only; audit entry required for both events).
   - VI. User Preference Management → Portability: sensitive export values MUST
     be encrypted; omission is no longer a permitted alternative; every
     sensitive key MUST appear in the export in encrypted form.
   - Additional Constraints §7 → WCAG AA contrast ratios made explicit:
     standard text ≥ 4.5:1; large text (≥18 px regular or ≥14 px bold) ≥ 3:1;
     non-text UI components (icons, borders, interactive controls) ≥ 3:1.
   - Additional Constraints §VI theming → same WCAG AA ratio specifics added
     inline with a cross-reference to §7 Accessibility.
   - Additional Constraints §19 → readonly move block explicitly clarified as
     blocking initiation of any move regardless of source ownership or
     destination.
Added sections: §VII Account Suspension
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)
Follow-up TODOs (new in 1.11.0):
   12. TODO(AUTO_UNLOCK_WORKFLOW): Define automated unlock workflow for the
       lockout mechanism (§VII Lockout). Specify trigger conditions,
       time-based vs event-driven, and whether admin approval is required.
   13. ~~TODO(BREAKGLASS_DRILL_DOCS)~~: ✓ RESOLVED — see §18 and
     "Follow-up TODOs resolved" entries in later amendments.
   14. ~~TODO(CRASH_RECOVERY_SESSION)~~: ✓ RESOLVED in v1.26.0 — see §G.13
       and §VII.W. Startup-time clearing mandatory; crash sentinel (dirty/
       clean) prescribes detection; OS-level persistence protections (swap,
       dump, core) required; crash handler clearing best-effort only;
       deterministic CI reviewability prescribed in §VII.W.6.
   15. ~~TODO(IS_PROTECTED_SCOPE)~~: ✓ RESOLVED in v1.25.0 — see §G.12 and
       §DW17.X. All six protected operations (deletion, deactivation,
       suspension, admin password reset, role change, username change)
       constitutionally prescribed; self-service exception; error contract;
       CI reviewability requirements added.
   16. ~~TODO(AUDIT_ORIGIN_METADATA)~~: ✓ RESOLVED in v1.27.0 — see §16.X.
       Minimum fields (all events): actor_username, session_id, device_id
       (pseudonymized), app_instance_id. Network-event additional fields:
       client_ip_hash (pseudonymized; raw IP MUST NOT be stored),
       user_agent, protocol. Privacy constraints: raw IP, hostnames,
       OS-level usernames, and hardware serial numbers MUST NOT be stored.
       Pseudonymization via stable one-way hash required.
     17. ~~TODO(EOL_PLANNING_DELIVERABLE)~~: ✓ RESOLVED in v1.33.0 —
       see §1.X and docs/eol-planning-deliverable-spec.md.

Previous Sync Impact Report (1.9.0 → 1.10.0)
Version change: 1.9.0 → 1.10.0
Modified principles (2026-03-12 round-5 clarification session):
   - II. Safety & Data Integrity → dry-run requirement narrowed to side-effect
     operations only; secure deletion algorithm selection required at
     installation time with advance operator/developer notification.
   - VII. Identity & Access Control → break-glass accounts exempted from
     lockout mechanism; Admin Resets section cross-references §15 MFA
     challenge requirement; deployment-level MFA toggle MUST NOT override
     always-available accounts; accepted MFA second factors restricted to
     TOTP, email, and FIDO2 only ("other equivalent" clause removed);
     Argon2id constitutional minimum cost parameters added (m≥64MiB, t≥3,
     p≥4); break-glass plaintext/recovery credential scope clarified
     (Argon2id hash may remain in DB).
   - Additional Constraints §5 → GUI smoke test updated to specify every
     tool bundled under the launcher (replaces "representative tools").
   - Additional Constraints §6 → performance baselines added for file
     search (≥50k files/min), metadata extraction (≥20k files/min), and
     file copying (CPU overhead ≤10% above native OS baseline).
   - Additional Constraints §17 → TODO(DIRECT_DB_AUDIT) added for direct-DB
     audit-trail mechanism.
   - Additional Constraints §18 → break-glass credential storage restriction
     clarified: applies to plaintext/recovery credentials only; Argon2id
     hash MAY remain in DB.
   - Additional Constraints §21 → readonly accounts explicitly excluded from
     modifying any theme preferences.
   - Development Workflow §7 → GUI smoke definition updated to all bundled
     tools.
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)
Follow-up TODOs (new in 1.10.0):
   11. ~~TODO(DIRECT_DB_AUDIT)~~: ✓ RESOLVED in v1.32.0 — see §17.Z and
     docs/direct-db-audit-spec.md.

Previous Sync Impact Report (1.8.1 → 1.9.0):
Version change: 1.8.1 → 1.9.0
Modified principles (2026-03-12 round-4 clarification session):
   - V. Simplicity & Extensible Modularity → ComponentGuardian register() API
     description corrected (duplicate phrase removed).
   - VII. Identity & Access Control → break-glass account usernames renamed to
     `dev_breakglass` and `admin_breakglass`; `account_status` enum extended
     with `breakglass` value; always-available admin/dev MUST have MFA enrolled
     at installation; admin reset identity proof unified to "pass own MFA
     challenge".
   - VIII. Privacy → anonymization mode selection applies uniformly to all
     steps; mixing modes within a single operation is prohibited.
   - Additional Constraints §14 → `account_status` extended with `breakglass`;
     `is_breakglass` flag added to user_accounts schema; `pending`, `suspended`,
     and `breakglass` unified as non-blockable states.
   - Additional Constraints §15 → "admin identity proof" replaced with "pass
     own MFA challenge".
   - Additional Constraints §16 → anomaly detection alerts extended to
     `dev`-role users; audit log `action` field clarified as representative.
   - Additional Constraints §18 → break-glass accounts renamed to
     `dev_breakglass`/`admin_breakglass`; `breakglass` status and
     `is_breakglass` flag referenced; credential storage restriction extended
     to exclude the database.
   - Additional Constraints §19 → `account_status` enum updated with
     `breakglass`; default `role` value specified as sentinel `"unassigned"`.
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)
Follow-up TODOs (new in 1.9.0): None

Previous Sync Impact Report (1.7.0 → 1.8.1):
Version change: 1.7.0 → 1.8.1
Modified principles (2026-03-12 round-3 clarification session + addendum):
   - Additional Constraints §16 → `actor` field value specified for self-service
     events: equals `username` for `login_success`/`logout`; holds attempted
     username for `login_failure` regardless of identity verification.
   - V. Simplicity & Extensible Modularity → ComponentGuardian degraded state
     trigger defined: fires at initialization failure AND when health_check()
     returns False at runtime. Polling interval deferred to implementation
     (see TODO(GUARDIAN_POLL_INTERVAL)).
   - VI. User Preference Management → Canonical store bullet sentence repaired
     (missing "queries." restored). Portability import direction changed from
     "forward" to "up or down where technically feasible" to align with §12
     bidirectional migration policy.
   - VII. Identity & Access Control → TOTP-only enrollment requirement broadened
     to any offline-capable MFA method (TOTP or FIDO2 hardware token). Always-
     available account usernames (admin, dev) declared fixed and non-renameable;
     multiple admin/dev-role accounts permitted, distinguished by user_id and
     is_protected flag. Break-glass in-app notification clarified as persistent
     and queued for admins not currently online. MFA recovery identity
     verification specified as passing own MFA challenge.
   - Additional Constraints §12 → "where applicable" qualifier unified to
     "where technically feasible" to match §12 implementation qualifier.
   - Additional Constraints §14 → lockout status field names made explicit:
     is_blocked flag + login_attempts counter.
   - Additional Constraints §18 → break-glass in-app notification clarified
     as persistent/queued (mirrors §VII clarification).
   - Additional Constraints §19 → default role for new accounts specified as
     unset; admin must explicitly assign role before activation.
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)
Follow-up TODOs (new in 1.8.0):
  10. ~~TODO(GUARDIAN_POLL_INTERVAL)~~: ✓ RESOLVED — see §V.6.5.

Previous Sync Impact Report (1.6.0 → 1.7.0):
Version change: 1.6.0 → 1.7.0
Modified principles (2026-03-12 round-2 clarification session):
   - V. Simplicity & Extensible Modularity → ComponentGuardian degraded state
     specified: component MUST remain visible with reduced functionality (not
     hidden or removed); per-tool capability definitions deferred to
     implementation docs (see TODO(GUARDIAN_DEGRADED_UX)).
   - VI. User Preference Management → JSON fallback changed from MAY to MUST.
   - VII. Identity & Access Control → MFA explicit named second factors: email
     and FIDO2 hardware token added alongside TOTP. FIDO2 accepted as offline-
     capable. MFA recovery defined as administrator-performed account-level
     reset with identity verification. Unenrollment of last enrolled MFA method
     blocked until another method is added.
   - VIII. Privacy → Reversible (pseudonymization) operations now require an
     audit entry for each step.
   - Additional Constraints §12 → "forward-only" constraint removed; schemas
     MUST support up and down migration paths where technically feasible.
   - Additional Constraints §14 → user_accounts keyed by unique user_id
     surrogate primary key; username is a unique attached field, not the PK.
   - Additional Constraints §16 → username/actor distinction clarified:
     username = subject of action, actor = performer. Scoped-token/service-
     account mechanism for headless auth deferred (TODO(HEADLESS_AUTH)).
   - Additional Constraints §19 → explicit bootstrap exception added: always-
     available admin and dev accounts provisioned to active at installation.
   - Additional Constraints §22 → clarified as higher-level restatement of §IX;
     same validation checkpoint, not two distinct checkpoints.
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)
Follow-up TODOs (new in 1.7.0):
   8. TODO(GUARDIAN_DEGRADED_UX): Define per-tool reduced-functionality UX for
      ComponentGuardian degraded state. Each tool must document which
      capabilities are disabled and which remain available when the component
      enters degraded state. (Constraint: component MUST remain visible.)
   9. TODO(HEADLESS_AUTH): Define scoped API token and service account
      mechanism for headless automation credential persistence. Requirements
      to include: token expiry, scope limits, revocation mechanism. Deferred
      to a future implementation.

Previous Sync Impact Report (1.5.0 → 1.6.0):
Version change: 1.5.0 → 1.6.0
Modified principles (2026-03-12 clarification session):
   - II. Safety & Data Integrity → "headless mode" defined as CLI invocation
     without an interactive GUI session.
   - VI. User Preference Management → UAP defined as User Attribute Profile;
     module_settings namespace separator changed to underscore
     (module_settings_<module>); JSON fallback isolation clarified as one
     file per user_id.
   - VII. Identity & Access Control → always-available account bootstrap-to-active
     documented as explicit exception; lockout and anomaly-detection mechanisms
     documented as independent with mutual-exclusion flag; MFA MUST require
     TOTP enrollment (email-only enrollment rejected by system).
   - VIII. Privacy → path sanitization scope narrowed to external processes only
     (UI display removed from sanitization requirement).
   - IX. File Validation → validation exemption for internal RFU-written temp
     files added.
   - Additional Constraints §11 → module_settings namespace example corrected
     to snake_case (module_settings_af).
   - Additional Constraints §16 → anomaly-detection independence from lockout
     mechanism clarified.
   - Additional Constraints §19 → role demotion clarified as always approval-free.
   - Additional Constraints §22 → representative test corpus cross-referenced
     to §6 reference dataset.
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)

Previous Sync Impact Report (1.4.0 → 1.5.0):
Version change: 1.4.0 → 1.5.0
Modified principles (2026-03-11 clarification session):
   - II. Safety & Data Integrity → "signed CLI flag" now requires cryptographic
     HMAC token (not a plain long-form flag); overwrite algorithm now
     configurable per-deployment and documented in release notes.
   - III. Test-Driven Quality → coverage denominator is all of src/ with no
     exclusions; ±0.1 % rounding tolerance band added.
   - V. Simplicity & Extensible Modularity → ComponentGuardian location fixed
     to src/core/guardian/; register() API now requires health_check callable
     and degraded_fallback callable in addition to widget instance.
   - VI. User Preference Management → sensitive key designation via
     sensitive=True registry flag (not ad-hoc); conflict definition during
     import expanded to any key with a differing value; new User Isolation
     bullet clarifies full per-user_id isolation for UAP and all preferences.
   - VII. Identity & Access Control → fresh-install bootstrap clarified (always-
     available admin approves first users via normal workflow); idle timeout is
     user-configurable up to the system cap; MFA is a two-level opt-in (admin
     gates deployment; user enrolls within gate).
   - VIII. Privacy → PII detection scope configured by user per scan session.
   - IX. File Validation → validation boundary is every individual file open()
     call (not just tool-entry-point boundary).
   - Additional Constraints §1 → Python minimum raised from 3.8 to 3.12.
   - Additional Constraints §11 → preference category naming is snake_case only
     (kebab-case no longer permitted).
Added sections: None
Modified sections: None
Removed sections: None
Templates requiring updates: None (existing templates remain compatible)

Previous Sync Impact Report (1.3.0 → 1.4.0):
Version change: 1.3.0 → 1.4.0
Modified principles:
   - V. Simplicity & Extensible Modularity → expanded with Tool Interface Validator contract enforcement
     and Component Guardian pattern for GUI stability.
   - VI. User Preference Management & Personalization → expanded with preference portability
     (export/import) requirements for cross-device and backup scenarios.
   - VII. Identity & Access Control → expanded with MFA hook service requirements and
     idle-timeout watchdog obligations.
Added sections:
   - VIII. Privacy, PII Protection & Data Minimization — new governing principle covering
     privacy tools (anonymizer, privacy_cleaner), PII detector, directory security (pii_detector.py),
     and data retention policies.
   - IX. File Validation & Content Integrity — new governing principle covering the
     file_validator module (content-based detection, policies, signatures, heuristics, telemetry).
   - Directory & Theme Security subsections in Additional Technical & Quality Constraints
     (items 20-22).
   - Preference Portability Gate in Development Workflow & Quality Gates (item 13).
Removed sections: None
Templates requiring updates:
   - .specify/templates/plan-template.md ✅ (Constitution Check section already covers new principles)
   - .specify/templates/spec-template.md ✅ (privacy + file validation sections covered by existing req format)
   - .specify/templates/tasks-template.md ✅ (task categories accommodate new gates)
Follow-up TODOs:
   1. TODO(AUTH_DOCS): Publish operator guide for account provisioning/reset (docs/authentication.md) once CLI tooling is finalized.
   2. TODO(BREAK_GLASS_PROCEDURE): Document sealed-envelope storage and rotation procedure for break-glass credentials.
   3. TODO(ROLE_MIGRATION): Add migration scripts to provision always-available and break-glass accounts in existing databases.
   4. TODO(MFA_POLICY): Finalize MFA enrollment and recovery policy document once mfa_hook_service.py API stabilizes.
   5. TODO(PORTABILITY_FORMAT): Publish preference export/import schema (JSON schema or protobuf) once portability.py API is stable.
   6. TODO(PII_SCAN_BASELINE): Define baseline PII detection ruleset and false-positive threshold for pii_detector.py.
   7. TODO(FILE_VALIDATOR_SIGS): Publish and version the signature database used by signatures.py.
-->

# RFU (Richard's File Utilities) Constitution

## Normative TODO Authority and Register

### Authority Rule

For TODO status interpretation in this constitution, the latest normative
section text is authoritative. Historical Sync Impact reports and
Clarifications logs are archival records and MUST NOT override current
normative status.

### Canonical Open TODO Register

The TODO items below are the active constitutional TODO set.

| TODO | Status | Owner Role | Target Milestone | Enforcement Impact |
|------|--------|------------|------------------|--------------------|
| TODO(HUB_MENU_REGISTRY_API) | Open | Maintainer | v1.38.0 | deferred gate |
| TODO(RELAUNCH_TOOL_WINDOW_API) | Open | Maintainer | v1.38.0 | deferred gate |
| TODO(OPS_PHASE3_SPEC) | Open | Release Steward | v1.39.0 | deferred gate |
| TODO(HEADLESS_AUTH) | Open | Security | v1.39.0 | none |
| TODO(AUTO_UNLOCK_WORKFLOW) | Open | Security | v1.39.0 | none |
| TODO(BREAK_GLASS_PROCEDURE) | Open | Security | v1.39.0 | none |
| TODO(ROLE_MIGRATION) | Open | Maintainer | v1.39.0 | none |
| TODO(MFA_POLICY) | Open | Security | v1.39.0 | none |
| TODO(PORTABILITY_FORMAT) | Open (partially addressed) | Release Steward | v1.40.0 | none |
| TODO(PII_SCAN_BASELINE) | Open | Security | v1.40.0 | none |
| TODO(FILE_VALIDATOR_SIGS) | Open | Maintainer | v1.40.0 | none |
| TODO(AUTH_DOCS) | Open | Release Steward | v1.40.0 | none |
| TODO(GOVERNANCE_DOC) | Open | Release Steward | v1.40.0 | none |
| TODO(HUB_UX_COHESION) | Open | UX | v1.40.0 | none |
| TODO(FONT_TOKENS_IMPL) | Open | UX | v1.40.0 | none |
| TODO(LAYOUT_TOKENS_IMPL) | Open | UX | v1.40.0 | none |
| TODO(GUARDIAN_DEGRADED_UX) | Open | UX | v1.40.0 | none |

### Canonical Resolved TODO Register

The TODO items below are resolved and MUST be treated as closed in governance
tracking:

- TODO(BREAKGLASS_DRILL_DOCS)
- TODO(GUARDIAN_POLL_INTERVAL)
- TODO(EOL_PLANNING_DELIVERABLE)
- TODO(DIRECT_DB_AUDIT)
- TODO(AUDIT_ORIGIN_METADATA)
- TODO(CRASH_RECOVERY_SESSION)
- TODO(IS_PROTECTED_SCOPE)
- TODO(FONT_TOKENS_SPEC)
- TODO(LAYOUT_TOKENS_SPEC)
- TODO(COMMAND_TAXONOMY)
- TODO(UI_STRINGS_MENU_TOKENS)

## Normative Glossary

The following terms carry precise, normative meanings throughout this
constitution. Where a section obligation uses a term defined here, the
definition in this section is authoritative. Sections that introduce or
refine additional terms define them inline and cross-reference here for
traceability.

### §G.1 — User-visible

**User-visible** — Information that appears automatically in the active
foreground UI without requiring navigation, expansion, or interaction. A
reasonable user cannot proceed without noticing it.

Permitted surfaces that **satisfy** this requirement:
- Modal dialogs
- Inline error or warning banners rendered in the main content area
- Automatic toast/snackbar notifications that appear in the main viewport
  without requiring any action to trigger them

Surfaces that **do not satisfy** this requirement:
- Status bars or status bar icons
- Notification tray badges or taskbar badges
- Collapsible or expandable panels (unless already expanded)
- Tooltips requiring hover
- Log panels or output panels
- Sidebars that require opening
- Any surface that requires navigation away from the current view

**CI enforcement note**: CI MUST verify user-visible elements via DOM or
widget-tree presence in the active foreground viewport. User-visible warnings
and summaries MUST NOT be suppressible by default.

### §G.2 — User-discoverable

**User-discoverable** — Information reachable within one navigation step from
the active UI state, without consulting external documentation or advanced
features and without requiring knowledge of hidden or non-obvious UI elements.

Permitted surfaces that **satisfy** this requirement:
- Clicking a top-level tab
- Opening a sidebar via a clearly labelled control in the current view
- Selecting a single item from a top-level or first-level menu
- Expanding a single accordion section that is already visible

Surfaces that **do not satisfy** this requirement:
- Multi-level or cascading menu navigation
- Log panels, developer consoles, or debug output areas
- Configuration or settings files
- External documentation pages
- Any surface that requires more than one navigation step from the current
  active UI state

**Governance note**: user-discoverable is appropriate for optional diagnostics,
dry-run supplementary detail, and non-blocking informational metadata. It MUST
NOT replace user-visible surfaces where the constitution requires user-visible.

### §G.3 — Side effect

**Side effect** — Any persistent change to user-visible state, including
creation, deletion, modification, or metadata mutation of files, directories,
or external resources. Internal RFU bookkeeping (indexes, caches, audit logs)
is not considered a side effect.

Resolved ambiguous scenarios:
- Reading a file that updates its filesystem access timestamp: **not** a side
  effect — not user-visible and not persistent in a user-facing sense.
- Writing to RFU's internal index or audit log: **not** a side effect —
  internal implementation detail, not user-visible.
- Network operations that modify remote state: **side effect** — persistent
  change to user-visible external resources.
- Metadata writes (EXIF, tags): **side effect** — persistent mutation of user
  files, reversible and non-destructive (see §G.4 for the destructive
  sub-class).

**CI enforcement note**: CI MUST verify that all operations classified as
side-effect operations expose a dry-run path (§II.1). Operations that write
only to internal RFU bookkeeping MUST NOT be classified as side-effect
operations.

### §G.4 — Destructive operation

**Destructive operation** — A side-effect operation (§G.3) that is irreversible
or hard to reverse, including deletion, overwrite, secure wipe, anonymization,
or lossy transformation.

Examples of destructive operations:
- File deletion
- File overwrite
- Secure wipe
- Anonymization or PII scrubbing
- Lossy compression or irreversible normalization

**CI enforcement note**: CI MUST verify that all destructive operations require
explicit user-visible confirmation (§II.2) in addition to dry-run.

### §G.6 — Critical engine

**Critical engine** — A module that meets one or more of the following criteria:

- **(a) Irreversible or destructive operations** — the module performs operations
  that are irreversible or hard to reverse, including deletion, overwrite,
  secure wipe, anonymization, or lossy transformation (see §G.4).
- **(b) Large-scale or batch operations** — the module can operate on multiple
  user files or resources at once (e.g., batch renamers, batch converters,
  batch metadata writers, multi-file processors) such that a single defect
  could propagate across many user assets.
- **(c) High-impact data transformations** — the module performs transformations
  where correctness is critical and errors are costly: deduplication,
  compression, OCR, PDF extraction, image normalization, checksum or integrity
  verification.
- **(d) Untrusted external input** — the module ingests or processes untrusted
  or externally supplied data, including network sync, remote metadata fetch,
  external file parsing, or archive extraction.
- **(e) Security-sensitive operations** — the module interacts with encryption,
  secure deletion, authentication, token validation, or sandbox boundaries.

Examples include, but are not limited to: duplicate detection engines, secure
deletion engines, batch processors, compression engines, PDF processors, network
synchronization modules, archive extractors, and OCR engines. The prior
parenthetical list in §III is illustrative, not exhaustive.

**Classification authority**: Any maintainer MAY classify a module as a critical
engine during PR review if it meets one or more of the criteria above (see
§III.1). PR authors MAY self-declare but maintainers hold final authority.
Classification MUST be recorded in the module's metadata or README.

**CI enforcement note**: CI MUST enforce the §III property-based / scenario
edge test requirement for all modules declared as critical engines. Modules
without a classification are not presumed critical, but reviewer override
applies (see §III.1).

### §G.5 — Headless HMAC token

**Headless HMAC token** — A cryptographically signed token used as the
alternative to interactive user confirmation for destructive operations (§G.4)
in headless mode (CLI invocation without an interactive GUI session). A
compliant headless HMAC token MUST satisfy all five attributes defined in §II.5.

Normative attribute summary (full requirements in §II.5):
- **Algorithm**: HMAC with SHA-256 or stronger; weaker algorithms (MD5, SHA-1,
  or unspecified defaults) MUST NOT be used.
- **Key storage**: secure system keystore or hardware-backed secret store; MUST
  NOT reside in plaintext config files, environment variables, or source code
  in production deployments.
- **Validity period**: ≤ 5 minutes from issuance; an embedded timestamp MUST
  be part of the signed payload.
- **Single-use**: authorizes exactly one destructive operation; MUST be
  invalidated immediately after redemption.
- **Audit trail**: both issuance and redemption MUST each generate an audit log
  entry (fields defined in §II.5.5).

**Distinction from §15 credential reset token**: The §15 account-recovery token
has a separate governance scope (credential reset, out-of-band delivery, 1-hour
validity). The §G.5 headless HMAC token governs destructive-operation
authorization only (§II.5, maximum validity 5 minutes). The two MUST NOT be
conflated.

**CI enforcement note**: CI MUST verify that headless execution paths accept
only tokens satisfying §II.5.1–§II.5.5. Non-compliant algorithms or plaintext
key sources MUST be treated as CI gate failures.

### §G.7 — Export encryption envelope

**Export encryption envelope** — The portable, versioned, plaintext-header
structure in which encrypted preference export artifacts are delivered. A
compliant export encryption envelope MUST satisfy all requirements defined in
§VI.4 (algorithm, KDF, metadata, passphrase derivation, and interoperability).

Normative property summary (full requirements in §VI.4):
- **Algorithm**: AES-256-GCM (authenticated encryption; weaker algorithms or
  non-AEAD modes MUST NOT be used — see §VI.4.1).
- **Key derivation**: Argon2id with minimum parameter floors (memory ≥ 64 MB,
  iterations ≥ 3, parallelism ≥ 1, salt ≥ 16 bytes — see §VI.4.2).
- **Metadata**: plaintext header containing algorithm, KDF name, KDF
  parameters, salt, nonce, and version — stored inside the export file so
  any conforming importer can decrypt without out-of-band information
  (see §VI.4.3).
- **Key source**: passphrase-derived only; application-managed keys MUST NOT
  be used (see §VI.4.5).
- **Versioned format**: version field in the envelope root enables future
  algorithm migrations without breaking imports (see §VI.4.3).

**Reference envelope shape**:
```json
{
  "version": 1,
  "encryption": {
    "algorithm": "aes-256-gcm",
    "kdf": {
      "name": "argon2id",
      "memory_mb": 64,
      "iterations": 3,
      "parallelism": 1,
      "salt_b64": "<BASE64_SALT>"
    },
    "nonce_b64": "<BASE64_NONCE>",
    "tag_b64": "<BASE64_AUTH_TAG>"
  },
  "meta": {
    "created_at": "<ISO8601_TIMESTAMP>",
    "tool": "rfu-export",
    "schema_version": "<PREF_SCHEMA_VERSION>"
  },
  "ciphertext_b64": "<BASE64_CIPHERTEXT>"
}
```
All fields except `ciphertext_b64` are plaintext. Sensitive data lives
exclusively inside `ciphertext_b64`.

**CI enforcement note**: CI MUST verify that export artifacts conform to this
envelope shape, that algorithm and KDF fields meet minimums, and that no
sensitive preference values appear outside `ciphertext_b64`.

### §G.8 — Round-trip fidelity

**Round-trip fidelity** — The guarantee that performing an export followed by
an import produces a preference state that is semantically identical to the
original. Fidelity is evaluated over **semantic preference fields only**; it
does not require and MUST NOT require full-record byte-for-byte identity.

Fields **included** in the fidelity comparison (constitutional, per §DW13.1):
- `preference_category`
- `preference_key`
- `preference_value`
- `value_type`

Fields **excluded** from the fidelity comparison (constitutional, per §DW13.2):
- `created_at`, `modified_at`, `imported_at` (timestamps)
- `record_id` (internal storage identifier)
- `version`, `migration_flags` (storage record metadata)
- Any other implementation-generated metadata not part of the preference value

**Rationale**: Timestamp and record-identity fields are regenerated on import
by design. Requiring them to match would make round-trip fidelity impossible
and unenforceable across any compliant implementation.

**CI enforcement note**: CI MUST verify round-trip fidelity by comparing only
the four semantic fields. Tests that compare timestamps, IDs, or full records
MUST be treated as non-compliant and corrected.

### §G.9 — TOTP default profile

**TOTP default profile** — The constitutional minimum configuration for
Time-Based One-Time Password (TOTP) MFA that all implementations MUST support
for interoperability with standard authenticator applications (Google
Authenticator, Microsoft Authenticator, Authy, 1Password, etc.).

| Parameter | Constitutional value |
|-----------|---------------------|
| Standard | RFC 6238 (TOTP) |
| Algorithm | HMAC-SHA1 |
| Code length | 6 digits |
| Time step | 30 seconds |
| Drift tolerance | ±1 time step (±30 s) |

**Normative provisioning URI form**:
```
otpauth://totp/Label?secret=SECRET&issuer=APP&algorithm=SHA1&digits=6&period=30
```

Implementations MAY additionally support stronger profiles (SHA-256, SHA-512,
8-digit codes, 60-second steps), but MUST NOT replace or disable the default
profile. **HOTP (RFC 4226)** is explicitly excluded from the default profile
and MUST NOT be treated as an enrolled offline-capable MFA method.

**Cross-references**: §VII.X (Offline-Capable MFA Requirements),
docs/totp-spec.md, checklist-totp-compliance.md.

### §G.10 — FIDO2 authenticator classes

**FIDO2 roaming authenticator** — A detachable hardware security key (e.g.,
YubiKey, Titan Key, USB-A/C, NFC, BLE) implementing the FIDO2/WebAuthn
standard that is physically separate from the host device and can be used
across any number of devices. Roaming authenticators satisfy the
offline-capable MFA enrollment requirement in §VII.

**FIDO2 platform authenticator** — A device-bound authenticator integrated
directly into the host device (e.g., Windows Hello, Apple Touch ID, Face ID,
TPM-backed keys) that implements FIDO2/WebAuthn but whose credentials are tied
to the specific platform and cannot be transferred to a replacement device.
Platform authenticators do **not** satisfy the offline-capable MFA enrollment
requirement when enrolled alone.

**Pairing requirement** (§VII.Y.3): If a user enrolls a FIDO2 platform
authenticator, they MUST also have at least one FIDO2 roaming authenticator or
TOTP method (§G.9) enrolled to satisfy the offline-capable MFA requirement.

**Cross-references**: §VII.Y (FIDO2 Authenticator Requirements),
docs/fido2-spec.md, checklist-fido2-compliance.md.

### §G.11 — Role-differentiated idle timeout defaults

**Role-differentiated idle timeout defaults** — The constitutional per-role
out-of-box idle timeout values that all implementations MUST use when no
administrator or user has explicitly configured an idle timeout. These values
reflect the privilege and risk profile of each account role.

| Role | Constitutional default timeout |
|------|-------------------------------|
| `admin` | 10 minutes |
| `dev` | 15 minutes |
| `user` | 30 minutes |
| `readonly` | 45 minutes |

**Security ceiling**: No role's idle timeout MAY be configured longer than
60 minutes unless an administrator explicitly overrides it with a documented
justification. The 8-hour absolute system ceiling defined in §VII Session
Controls applies independently.

**Rationale**: Privileged roles (`admin`, `dev`) present a substantially
greater attack surface when sessions are left unattended; shorter defaults
reduce the window of exposure. Lower-privilege roles (`user`, `readonly`)
tolerate longer defaults without proportionate security risk.

**Administrative overrides**: Administrators MAY configure per-role idle
timeout values stricter or more permissive than these defaults, subject to the
60-minute ceiling. All overrides MUST be logged and auditable.

**Cross-references**: §VII.Z (Idle Timeout Requirements),
docs/idle-timeout-spec.md, checklist-idle-timeout-compliance.md.

### §G.12 — is_protected scope

**`is_protected`** — A boolean flag on user account records that designates
accounts which MUST remain permanently available, permanently privileged, and
immune to administrative modification. The flag covers **six protected
operations** (resolved from TODO(IS_PROTECTED_SCOPE)):

| Operation | `is_protected = true` effect |
|-----------|------------------------------|
| Deletion | MUST be blocked |
| Deactivation | MUST be blocked |
| Suspension | MUST be blocked |
| Password reset by another admin | MUST be blocked |
| Role change (escalation or demotion) | MUST be blocked |
| Username change | MUST be blocked |

**Self-service exception**: A protected account owner MAY change their own
password (self-service). All other modifications by any other actor are
forbidden.

**Error contract**: Every blocked operation MUST fail with an explicit
`protected_account_error` (not a generic failure or silent no-op) and MUST
emit a structured audit-log entry recording the actor, target account,
attempted operation, and reason.

**Enforcement layers**: The guard MUST be enforced at the service/API layer and
MUST NOT rely solely on UI controls, documentation, or convention. Database-
level constraints are strongly recommended as a defence-in-depth measure.

**Cross-references**: §DW §17 (Lockout Prevention / Always-Available Accounts),
§VII Always-Available Accounts, docs/is-protected-spec.md,
checklist-is-protected-compliance.md.
Resolves: TODO(IS_PROTECTED_SCOPE).

### §G.13 — Crash sentinel

**Crash sentinel** — A persistent, process-external state indicator (file,
record, or flag) used to distinguish a clean shutdown from an unclean
termination (crash, OOM kill, power loss, SIGKILL, container eviction, etc.).

**Semantics**:

| Sentinel state | Meaning |
|----------------|---------|
| `dirty` | Process started but did not complete graceful shutdown |
| `clean` | Previous process completed graceful shutdown |
| `missing` / unknown | Treated as `dirty` (conservative default) |

**Lifecycle**:

- Set to `dirty` **at the very start of startup**, before any session or
  preference operations.
- Set to `clean` **only** on graceful shutdown completion.
- If the sentinel is `dirty` or missing at startup, the previous run MUST be
  treated as a crash: all session secrets MUST be purged before proceeding.

**Properties**:
- MUST be process-external (i.e., survives process termination and cannot be
  cleared by an in-process crash handler that never runs).
- MUST be readable at the earliest point in the next startup before any
  session-related logic.
- MUST be deterministically testable: CI tests MUST be able to simulate a
  crash by leaving the sentinel in the `dirty` state.

**Cross-references**: §VII.W (Crash-Recovery Session Clearing),
docs/crash-recovery-spec.md, checklist-crash-recovery-compliance.md.
Resolves: TODO(CRASH_RECOVERY_SESSION) (in conjunction with §VII.W).

---

## Core Principles

### I. Cross-Platform Consistency

All supported operating systems (Windows, macOS, Linux) MUST deliver identical
functional capabilities (feature flags may only disable OS-infeasible actions).
An action may only be designated OS-infeasible with explicit approval from at
least one maintainer (distinct from the PR author). A written justification for
the designation MUST appear in the PR description, and the project capabilities
matrix MUST be updated to record the designation, the affected platform(s), and
the approving maintainer. No feature flag may suppress a capability on any
platform without this review gate.
UI labels, shortcuts (where feasible), and behaviors MUST remain consistent.
Platform-specific code MUST be isolated behind clearly named adapter modules.
Rationale: Predictable behavior across environments reduces user friction and
lowers maintenance cost by preventing divergent code paths.

### II. Safety & Data Integrity (NON‑NEGOTIABLE)

Destructive operations (as defined in §G.4) MUST be opt-in and require a
single explicit user confirmation (or a cryptographically signed HMAC token
attached to the invocation in headless mode (defined as CLI invocation without
an interactive GUI session; see §G.5 and §II.5 for full token requirements) —
a plain long-form flag is insufficient). The
elevated two-step confirmation (typed phrase + button click) defined in §VIII
applies exclusively to irreversible anonymization operations; all other
destructive operations require a single explicit confirmation step only.
Default behavior for move/copy/sync MUST preserve source data unless user
chooses otherwise. Secure deletion MUST use overwrite patterns that are
configurable per-deployment; the overwrite algorithm MUST be explicitly
selected by the operator or developer during the installation process before
the system is considered production-ready (installation documentation MUST
communicate this required decision to operators and developers in advance);
the selected algorithm MUST also be documented in each release's security notes.

#### §II.1 — Dry-run Requirement (Side-effect Operations)

All side-effect operations (as defined in §G.3) MUST support dry-run
simulation. Dry-run execution MUST:

- Enumerate all intended changes to user-visible state
- NOT perform any of those changes
- Present a user-visible summary (as defined in §G.1) of all intended
  modifications and all skipped items
- Be available through the same interface as the real operation

Documentation-only discoverability is insufficient: the capability MUST be
visible in the tool's UI prior to the user initiating the operation. The
specific UI pattern for surfacing dry-run is implementation-defined per tool.

#### §II.2 — Confirmation Requirement (Destructive Operations)

All destructive operations (as defined in §G.4) additionally MUST require
explicit user-visible confirmation prior to execution. Confirmation MUST:

- Block execution until the user explicitly approves
- Appear in a foreground, non-dismissed UI surface
- Summarize the irreversible consequences of the operation
- List all affected items

(The HMAC token mechanism for headless mode is formally defined in §G.5 and
fully specified in §II.5. The §VIII two-step exception for irreversible
anonymization is described in the opening paragraph of §II.)

#### §II.3 — Internal Operations Excluded

Internal RFU bookkeeping — including indexes, caches, audit logs, and other
non-user-visible persistent writes — MUST NOT be classified as side-effect
operations (§G.3) and MUST NOT require dry-run or confirmation.

#### §II.4 — CI Enforcement

CI MUST verify that:

- All side-effect operations expose a dry-run path
- All destructive operations require user-visible confirmation
- No internal bookkeeping is incorrectly classified as a side-effect operation

Metadata manipulations MUST validate schema before commit. Rationale: File
utilities operate on critical user assets; irreversible loss must be virtually
eliminated.

#### §II.5 — Headless HMAC Token Requirements

The HMAC token referenced in the opening paragraph of §II (see §G.5 for
normative summary) as the headless-mode alternative to interactive confirmation
MUST satisfy the following constraints.

##### §II.5.1 — Algorithm
Headless confirmation tokens MUST be implemented as HMACs using SHA-256 or
stronger (e.g., SHA-512). Weaker algorithms (MD5, SHA-1, or unspecified
defaults) MUST NOT be used.

##### §II.5.2 — Key Storage
The HMAC signing key MUST be stored in a secure system keystore or
hardware-backed secret store (e.g., OS keyring, TPM-backed secret, cloud KMS,
or HSM module). The signing key MUST NOT reside in plaintext configuration
files, environment variables, source code, or container environment variables
in production deployments. Development and production signing keys MUST be
distinct and MUST NOT be shared across environments.

##### §II.5.3 — Token Structure and Validity
Each token MUST embed an issuance timestamp as part of the signed payload.
A token MUST NOT be accepted as valid more than five (5) minutes after its
issuance timestamp. Implementations MAY tolerate minor clock skew provided
the hard upper bound of 5 minutes is never exceeded.

##### §II.5.4 — Single-Use Requirement
Each token MUST be single-use. A token MAY authorize exactly one destructive
operation. After successful redemption the token MUST be invalidated and MUST
NOT be accepted again.

##### §II.5.5 — Audit Logging
Both token issuance and token redemption MUST generate audit log entries.
Each audit entry MUST include:
- timestamp
- operation name
- a non-sensitive token identifier (e.g., a hash of the token — MUST NOT
  be the raw token or raw key material)
- caller identity
- success or failure status

Full token content and raw key material MUST NEVER appear in audit log entries.
These events are auditable events under §16 and subject to the ≥ 365-day
retention requirement.

##### §II.5.6 — Equivalence to Interactive Confirmation
A headless HMAC token satisfying §II.5.1–§II.5.5 MUST be treated as equivalent
to the interactive user-visible confirmation required by §II.2 for the single
destructive operation it authorizes.

### III. Test-Driven Quality & Observability

All new functionality MUST begin with failing automated tests (unit and where
relevant integration). Minimum global line coverage MUST remain ≥ 85% and MUST
not decrease in a PR by more than 0.1 % (tolerance band for floating-point
rounding by the coverage tool). The coverage denominator is all source files
under src/; no files are excluded — auto-generated, vendored, and import-only
files are all counted. Critical engines (as defined in §G.6 — illustrative
examples include duplicate detection, secure delete, and batch processors)
MUST have property-based or scenario edge tests that collectively cover all of
the following scenarios: empty input, single-element input,
maximum-expected-size input, random/unexpected input (fuzz or property-based),
and adversarial/malformed input. No minimum number of test cases is prescribed
beyond satisfying all five scenarios. Structured logging (levelled,
machine-parsable) and error classification MUST accompany features.
Rationale: Fast feedback and rich telemetry enable safe evolution.

#### §III.1 — Critical Engine Classification Authority

Any maintainer MAY classify a module as a critical engine during PR review if
it meets one or more of the criteria in §G.6. Classification MUST be recorded
in the module's metadata or README (e.g., `critical_engine: true` in the
module's metadata file). PR authors MAY self-declare a module as critical; such
declarations are accepted without further review. Maintainers hold final
classification authority and MAY override a PR author's absence of
classification. A maintainer override MUST be documented in the PR description.

Once classified, a module MUST satisfy the §III property-based / scenario edge
test requirement for all five scenarios. CI MUST enforce this requirement via
the module classification declaration. The list of classified critical engines
MUST be maintained in `docs/critical-engines.md`.

### IV. Performance & Scalability of Batch Operations

Core batch operations (search, duplicate scan, metadata extraction, copying)
MUST stream and avoid loading entire directory trees or large files wholly in
memory. Operations on N files MUST scale at worst O(N log N); any algorithm
with superlinear growth beyond O(N log N) (e.g., O(N²)) fails this gate.
Clear progress reporting is required. UI interactions MUST stay responsive (UI
thread blocking MUST NOT reach or exceed 100ms; use worker threads/process
pools; §6 Performance Baselines is the governing enforcement gate). Rationale:
User trust and enterprise viability depend on predictable performance under
large workloads.

### V. Simplicity & Extensible Modularity

Features MUST be implemented as modular, discoverable tool components with
clear single responsibility. Public interfaces (CLI / scripted APIs) MUST be
stable; changes require deprecation cycle (see Governance
<!-- TODO(GOVERNANCE_DOC): A separate docs/governance.md document is planned;
     until it exists, the ≥ 1 MINOR release rule in §10 is authoritative. -->
). Avoid premature
generalization: implement minimum set that satisfies explicit requirements.
Extension points (tool discovery, engines, PyQt5 GUI registration) MUST
document contracts and failure modes with automated validation before launch.
For PyQt5-based tools: use `{ToolName}GUI` naming convention,
auto-discovery via metadata patterns, and graceful import fallbacks.

Tool contracts MUST be enforced through the `tool_interface_validator.py`
pipeline before a tool is made available to users; instantiation failures MUST
surface structured error messages, not raw stack traces. GUI components MUST
register with the `ComponentGuardian` (located in `src/core/guardian/`) to
enable runtime integrity checks and graceful degradation when a component
fails to initialize. The `ComponentGuardian.register(widget, health_check,
degraded_fallback)` API requires: the widget instance, a zero-argument
callable returning a boolean health status, and a zero-argument callable
invoked when the component enters a degraded state.
A component enters degraded state in two cases: (1) initialization failure,
or (2) the `health_check()` callable returns `False` at runtime. The polling
interval for runtime health checks is constitutionally bounded in §V.6
(minimum: at least once every 5 seconds; maximum: no more than once every
500 milliseconds; implementation strategy is flexible within those bounds).
When invoked, the `degraded_fallback` MUST render the component as visible with
reduced functionality; the component MUST NOT be hidden or removed from the UI.
The specific functionality disabled per tool in degraded mode MUST be defined in
that tool's implementation documentation (see TODO(GUARDIAN_DEGRADED_UX)).

#### §V.1 — Recovery Eligibility

A component MAY recover from degraded state while the application is running.
Degraded state reflects current operational health, not a permanent failure.
Implementations MUST NOT treat degraded state as terminal without an explicit
application restart.

#### §V.2 — Recovery Trigger

Recovery MUST occur automatically when a subsequent invocation of
`health_check()` returns `True`. No developer action, user action, API call,
or external trigger MAY be the sole mechanism for transitioning a component
from degraded state to healthy state. The state machine MUST be driven
exclusively by the return value of `health_check()`:

- `health_check()` returns `False` while `HEALTHY` → transition to `DEGRADED`
- `health_check()` returns `True` while `DEGRADED` → transition to `HEALTHY`

No direct "force healthy" path is permitted without a passing `health_check()`.

#### §V.3 — Recovery Behavior

Upon successful recovery (§V.2 trigger met), the component MUST:
- Resume normal operation immediately
- Clear all degraded-state indicators (visual or functional)
- Re-enter the regular health-check polling cycle

No residual "sticky degraded" logic MUST persist after a successful recovery
transition.

#### §V.4 — Recovery Logging

Every state transition — both degradation and recovery — MUST generate a
structured log entry. The log entry for recovery MUST contain:
- `timestamp`
- `component_id` (the registered component identifier)
- `from_state` (`"degraded"`)
- `to_state` (`"healthy"`)
- `reason` (e.g., `"health_check() returned True"`)

The log entry for degradation MUST contain:
- `timestamp`
- `component_id`
- `from_state` (`"healthy"` or `"initializing"`)
- `to_state` (`"degraded"`)
- `reason` (e.g., `"initialization failure"` or `"health_check() returned False"`)

Raw exceptions or stack traces MUST NOT be the sole log artifact; the above
structured fields MUST be present. Log entries MUST be parseable by the
structured logging system (§III).

#### §V.5 — Deterministic Reviewability

Implementations MUST ensure that both degradation and recovery transitions are:
- **Unit-testable**: each transition (init failure → degraded; runtime
  `health_check() == False` → degraded; runtime `health_check() == True` →
  healthy) MUST be covered by at least one automated test.
- **Log-observable**: each transition MUST produce a parseable structured log
  entry satisfying §V.4. CI MUST fail if a transition occurs without the
  required log fields.

See `docs/component-guardian-spec.md` for the canonical state machine diagram,
CI test spec, and migration patch.

#### §V.6 — Health-Check Polling Interval

##### §V.6.1 — Minimum Polling Frequency
During active use, each component's `health_check()` MUST be invoked at least
once every 5 seconds. Implementations MAY poll more frequently, subject to the
maximum bound in §V.6.2.

##### §V.6.2 — Maximum Polling Frequency
Implementations MUST NOT invoke `health_check()` more frequently than once
every 500 milliseconds. This prevents CPU churn, tight loops, and resource
consumption disproportionate to the value of rapid health detection.

##### §V.6.3 — Implementation Flexibility
Implementations MAY use fixed intervals, jitter, exponential backoff, or
adaptive polling strategies, provided that all polling remains within the
bounds defined in §V.6.1 and §V.6.2. The effective interval MUST never
fall outside the constitutional range [500 ms, 5 s] during active use.

##### §V.6.4 — Deterministic Reviewability
Polling intervals MUST be testable via unit tests (e.g., using mock timers or
virtual clocks) and observable via structured logs or metrics. CI MUST verify
that the effective polling interval remains within the constitutional bounds
(§V.6.1–§V.6.2). Tests MUST assert both the minimum and maximum bounds.

##### §V.6.5 — Resolution of TODO(GUARDIAN_POLL_INTERVAL)
This section resolves TODO(GUARDIAN_POLL_INTERVAL) (open since v1.8.0). No
implementation-defined polling interval outside the range [500 ms–5 s] is
permitted. The implementation strategy within that range remains
implementation-defined per §V.6.3.

Rationale: Lean, modular design reduces coupling and accelerates safe
innovation. Validated contracts and guarded components prevent cascading
failures and provide clear failure attribution.

### VI. User Preference Management & Personalization

User personalization is a first-class capability backed by a robust, modular
preference framework:

- Canonical store: Preferences MUST persist in a database table
  (`user_preferences`) with strong namespacing: `user_id`,
  `preference_category`, `preference_key` → `preference_value` + `value_type`.
  Implement triggers to maintain timestamps and use indexes for category/user
  queries. If the database is unavailable, a JSON file fallback MUST be used
  transparently without loss of correctness; user isolation MUST be preserved
  by maintaining one JSON file per `user_id` (separate files per user).
- Extensibility: Modules MUST define preferences under their own category
  namespace (e.g., `theming`, `favorites`, `directories`,
  `module_settings_<module>`). Categories and keys MUST be discoverable via a
  registry API with validation (type, allowed range, default, description).
- Universal theming: A single theme system MUST provide shared tokens (colors,
  typography, spacing) consumed by all modules. Theme storage uses preferences
  under the `theming` category with profile support (named presets) and WCAG AA
  contrast compliance (standard text ≥ 4.5:1; large text ≥ 3:1; non-text UI
  components ≥ 3:1 — consistent with §7 Accessibility). Named theme presets
  have two ownership scopes: personal presets (created, edited, renamed, and
  deleted by the owning account; available to `user`-role and above) and
  system-wide presets (created and managed only by `admin`/`dev` role accounts;
  visible to all users as read-only templates). Accounts with `role = user`
  MUST NOT delete or modify system-wide presets but MAY create personal presets
  locally derived from them.
- Favorites & directories: Users MUST be able to mark favorites (tools,
  paths, actions) and persist directory preferences (e.g., last opened,
  default start locations, visibility of hidden files) across modules.
- Security & privacy: Sensitive preferences (e.g., encryption settings, saved
  keys paths) MUST be storable as encrypted values with envelope encryption and
  redactable logs. A preference key is designated as sensitive by declaring
  `sensitive=True` in its per-key registry entry; the preference framework
  enforces encryption transparently on write for all such keys. No secrets in
  plain text; credential material (passwords, tokens, recovery phrases) MUST
  live in the Identity & Access Control layer and may only reference preference
  data through opaque identifiers.
- Portability: All account roles (including `readonly`) MAY export their own
  full preference set; only `user`, `admin`, and `dev` role accounts MAY
  import preferences (import is a write operation; `readonly` accounts MUST
  NOT import). The export and import format MUST be versioned and
  schema-validated. Permitted export formats are human-readable structured
  text only: JSON, YAML, TOML, or an equivalent structured text format. Binary
  formats (e.g., protobuf, MessagePack) and proprietary formats are NOT
  permitted. Exports MUST be portable to any compliant implementation without
  vendor-specific parsers. Export artifacts MUST encrypt
  sensitive preference values using AES-256-GCM with Argon2id key derivation
  (per §VI.4); omission is not a permitted alternative — every sensitive key MUST be present in the
  export in encrypted form to preserve round-trip fidelity. Import MUST
  validate schema version and migrate up or down where technically feasible;
  if migration of specific keys is not technically feasible, the system MUST
  import all compatible keys, skip incompatible keys, and present a
  user-visible summary (as defined in §G.1) of skipped items with the reason
  each key was skipped.
  Conflict detection is performed against the live value stored in the
  database at the time of import. A key that is entirely absent from the
  database is NOT a conflict; it is treated as a new key and accepted without
  requiring conflict resolution. Any existing key whose stored value differs
  from the imported value constitutes a conflict. All conflicting keys MUST be presented
  to the user in a single review UI before any overwrite occurs; the user MAY
  individually accept or reject each conflicting key (per-key selective
  resolution). Non-conflicting keys are automatically pre-approved in the
  pending import set (no per-key action required from the user); they are
  NOT written to the database ahead of the conflicting-key review. The user
  MAY also choose "accept all" or "reject all" as batch shortcuts. The
  import operation MUST NOT commit any key — conflicting or non-conflicting
  — until the user confirms the full resolution set in a single atomic write.
  §VI.1 — Skipped-item summary requirements: the user-visible summary of
  skipped items required by this section MUST conform to the definition of
  user-visible in §G.1 — it MUST appear automatically in the active
  foreground UI, MUST NOT require navigation or interaction to be seen, and
  MUST enumerate each skipped item and the reason it was skipped. Skipped
  items listed in this summary MUST be presented separately from any list of
  accepted items. CI MUST be able to verify the presence of the summary via
  widget-tree or DOM inspection of the active foreground surface.
  §VI.2 — Dry-run Integration (§II.1, §G.3): For all side-effect operations
  (as defined in §G.3), dry-run output MUST include the skipped-item summary
  defined in §VI.1. Skipped items recorded during dry-run simulation MUST be
  listed separately from intended changes in the dry-run report.
  §VI.3 — Deterministic Reviewability: The skipped-item summary MUST be
  structured such that reviewers can verify its presence via DOM or
  widget-tree inspection, CI can detect its absence or misclassification, and
  the summary format is consistent across all apps in the suite.
  §VI.4 — Export Encryption Requirements: Export artifacts that contain
  sensitive preference values MUST use the AES-256-GCM + Argon2id encryption
  envelope (§G.7). The following subsections are normative.
  §VI.4.1 — Mandatory Encryption Algorithm: All sensitive preference values
  in export artifacts MUST be encrypted using AES-256-GCM. Weaker algorithms
  (DES, RC4, 3DES, AES-ECB, AES-CBC without integrity) or non-AEAD modes MUST
  NOT be used for export encryption.
  §VI.4.2 — Key Derivation: The encryption key MUST be derived from a
  user-supplied passphrase using Argon2id with the following minimum
  parameter floors:
  – memory ≥ 64 MB
  – iterations ≥ 3
  – parallelism ≥ 1
  – salt length ≥ 16 bytes
  Implementations MAY use stronger parameters. Weaker KDFs (PBKDF2, bcrypt,
  scrypt without parameter floors, MD5-based derivation) MUST NOT be used.
  §VI.4.3 — Metadata Requirements: Export artifacts MUST include a plaintext
  header within the export file containing at minimum:
  – encryption algorithm name
  – KDF name
  – KDF parameters (memory, iterations, parallelism)
  – salt (base64-encoded)
  – nonce (base64-encoded)
  – authentication tag (base64-encoded)
  – version number
  This metadata enables any conforming importer to decrypt without
  out-of-band information. See §G.7 for the normative envelope shape.
  §VI.4.4 — Authenticated Encryption: AES-256-GCM MUST be used in
  authenticated mode. Importers MUST verify the GCM authentication tag before
  accepting or processing any decrypted data. A failed tag verification MUST
  result in import rejection with a user-visible error; partial data from a
  failed decryption MUST NOT be accepted.
  §VI.4.5 — Passphrase Requirement: The encryption key MUST be derived from
  a user-supplied passphrase. Application-managed keys (keys stored in
  config files, environment variables, hard-coded constants, or application
  secrets managers) MUST NOT be used for export encryption. This ensures
  portability and user control.
  §VI.4.6 — Interoperability: All implementations MUST be capable of
  decrypting export artifacts produced by any other implementation that
  conforms to §VI.4. An implementation MAY support additional algorithms
  for decryption of legacy or third-party formats, but MUST use the
  prescribed envelope for all new exports.
  §VI.4.7 — Deterministic Reviewability: CI and reviewers MUST verify that:
  – AES-256-GCM is used for all export encryption (no other algorithm);
  – Argon2id KDF parameters meet or exceed the floors in §VI.4.2;
  – all required metadata fields are present in the export envelope;
  – no sensitive preference values appear outside the encrypted ciphertext
    field of the export envelope.
- Migration & compatibility: Preference schemas MUST be versioned. Additive
  changes are MINOR; breaking changes require a migration with fallback
  defaults. Module independence MUST be preserved—each module may evolve its
  preferences without impacting others.

- User isolation: All preference data — including UAP (User Attribute Profile)
  profiles, last-used values, themes, and directory history — is fully isolated
  per `user_id`. Multiple users sharing a single installation MUST NOT share
  any preference state. A session MUST be bound to exactly one `user_id` before
  any preference read or write occurs.

Rationale: A consistent, typed, and discoverable preference layer enables rich
customization while preserving safety, performance, and maintainability across
independent modules.

### VII. Identity & Access Control

Authentication and authorization guard every executable surface and obey the
following non-negotiable rules:

#### Role-Based Access Matrix

The system enforces **four account roles** with distinct privilege levels:

| Role       | Description                                                            | Key Capabilities                                                                     |
| ---------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `dev`      | Developer access with full debugging/diagnostic capabilities           | All user + admin capabilities, plus debug logging, diagnostics, and internal tooling |
| `admin`    | Administrator access with user management and configuration privileges | User management, account approval/reset/unblock, configuration changes, audit review |
| `user`     | Standard user access for regular application functionality             | Normal file operations, preference management, tool usage                            |
| `readonly` | Read-only access with no write/modification capabilities               | View-only access to files and reports; no destructive operations                     |

> **Account Status vs. Role:** `pending` is **not** a role. It is a value of a
> separate `account_status` field on the account record (valid values:
> `pending` | `active` | `suspended` | `breakglass`). `breakglass` is the
> permanent default status for break-glass emergency accounts; accounts in
> `breakglass` status cannot authenticate through normal login flows and
> require explicit CLI flag or environment variable enablement. The `role`
> field and `account_status` field are independent columns in `user_accounts`.
> An account with `account_status = pending` has no access regardless of its
> assigned role until an admin sets the status to `active`.

Role assignment MUST be explicit; default new accounts MUST start with
`account_status = pending` (a separate field from `role`) until approved by an
admin. **Exception (explicitly documented):** Always-available accounts (`admin`
and `dev`) MUST be bootstrapped directly to `account_status = active` during
database initialization; the `pending` default does not apply to these protected
accounts. On a fresh installation the always-available `admin` account serves as
the first approver and MUST use the normal approval workflow to activate the
first `user` accounts — no automatic approval bypass is permitted for any other
account type. Role escalation (e.g., user → admin) MUST require admin approval
and emit an audit entry.

#### Always-Available Accounts

To prevent operator lockout, **two accounts MUST always be available** and
active at system initialization:

| Account Type | Purpose                                                              |
| ------------ | -------------------------------------------------------------------- |
| **dev**      | Guaranteed developer access for debugging and development operations |
| **admin**    | Guaranteed administrator access for user management and recovery     |

These accounts:

- MUST be provisioned automatically during database initialization or migration.
- MUST NOT be deletable or deactivatable through normal UI/CLI flows.
- MUST have their passwords set via secure operator procedures (not hard-coded).
- MUST emit audit entries for every login and action.
- MUST NOT have their usernames changed; `admin` and `dev` are fixed username
  values for the always-available accounts. Additional accounts with
  `role = admin` or `role = dev` MAY exist and are distinguished from the
  always-available accounts by their unique `user_id`; the always-available
  accounts are identified by the `is_protected` flag combined with their fixed
  usernames (`admin` and `dev`).
- The `is_protected` flag enforces six protected operations per §G.12 and
  §DW17.X: deletion, deactivation, suspension, admin-initiated password reset,
  role change, and username change are ALL blocked. Self-service password
  changes by the account owner remain permitted. Every blocked attempt MUST
  produce a `protected_account_error` and an audit-log entry.

#### Break-Glass Emergency Access

**Two break-glass accounts** provide emergency recovery when primary accounts
are compromised or locked:

| Account Type           | Purpose                                                            |
| ---------------------- | ------------------------------------------------------------------ |
| **dev_breakglass**     | Emergency developer access when primary dev account is unavailable |
| **admin_breakglass**   | Emergency admin access when primary admin account is unavailable   |

Break-glass accounts:

- MUST have plaintext and recovery credentials stored offline in a sealed
  envelope or secure vault (not in version control, not in config files, not
  in the database). The Argon2id password hash MAY reside in the database
  solely to enable authentication verification; all other credential material
  MUST remain offline.
- MUST be disabled by default and require explicit enablement (CLI flag or
  environment variable) before authentication succeeds.
- MUST trigger an immediate alert upon successful login to all active
  admin-role and dev-role accounts via two channels: (1) a persistent in-app
  notification delivered to all active admin-role and dev-role accounts
  (queued for recipients not currently logged in; MUST be displayed upon their
  next login), and (2) an out-of-band email notification to all active
  admin-role and dev-role accounts if an email delivery channel is configured.
  Both channels MUST be attempted; failure to deliver one channel MUST be
  logged but does not suppress the other. A high-priority audit entry MUST
  also be created.
- MUST require immediate password rotation after use; the system MUST enforce
  rotation and block further break-glass operations until rotation completes.
- MUST be tested annually to verify credentials remain valid and recovery
  procedures are documented.

#### Credential Storage

- User passwords MUST be hashed with Argon2id (memory-hard). Cost parameters
  MUST meet the following constitutional minimums: memory ≥ 64 MiB,
  iterations ≥ 3, parallelism ≥ 4. Actual parameters MUST be documented per
  release; higher parameters are permitted. No plaintext or reversible formats
  allowed. Password updates MUST rotate salts.

#### Lockout & Monitoring

- After 5 consecutive failed logins (an unbroken streak with no intervening
  successful login) the account MUST be blocked until an administrator (or
  automated unlock workflow) resets the counter. A successful login resets
  the failed-attempt counter to zero. Each attempt (success or failure) MUST
  be logged with timestamp and origin metadata. The consecutive-failure lockout
  mechanism and the rolling-24h anomaly-detection mechanism (§16) are
  independent: they maintain separate counters and do not share state. Once the
  lockout mechanism fires and sets `is_blocked`, anomaly detection does not
  additionally apply to that account while it remains blocked; conversely, an
  anomaly alert does not trigger lockout.
- Always-available accounts (`admin`, `dev`) are subject to the same lockout
  rules and MUST be recoverable via break-glass accounts (e.g., if the
  always-available `admin` is locked, `admin_breakglass` can unblock it).
  Break-glass accounts are NOT subject to the lockout mechanism; they
  authenticate only via the explicit CLI flag or environment variable and do
  not participate in the normal login flow on which the lockout counter
  operates.

#### Admin Resets & Unblock

- Administrative resets MUST generate a temporary
  password (or secure reset token) without exposing password hashes. Unblocks
  MUST reset counters, emit audit entries, and confirm actor identity by the
  actor passing their own MFA challenge (same requirement as §15 Credential
  Reset).

#### Account Suspension

- Only accounts with `role = admin` or `role = dev` MAY set another
  account's `account_status` to `suspended`. Accounts with `role = dev` MUST
  NOT suspend accounts with `role = admin`. Accounts identified by
  `is_protected = true` MUST NOT be suspended under any circumstances; the
  `is_protected` flag blocks suspension in addition to deletion, deactivation,
  admin-initiated password reset, role change, and username change (see §G.12
  and §DW17.X for the complete scope). The same roles MAY unsuspend an account
  by setting
  `account_status` back to `active` (or the appropriate prior status). Both
  the suspension and the unsuspension event MUST generate an audit entry
  recording the actor, the target username, and the before/after
  `account_status` value.
- A `suspended` account has no access regardless of its `role` assignment
  (consistent with the access rules for `pending` and `breakglass` statuses).

#### Preference Linkage

- Each account MUST reference a dedicated preference
  namespace identifier so that personalization never leaks between users. Tying
  a session to preferences MUST happen immediately after authentication.

#### Session Controls

- Long-running sessions MUST support manual logout and idle
  timeout. The out-of-box default idle timeout is **role-differentiated** per
  §G.11 and §VII.Z (admin 10 min, dev 15 min, user 30 min, readonly 45 min);
  implementations MUST NOT apply a single uniform default across all roles.
  No role's idle timeout MAY be configured longer than 60 minutes without an
  explicit administrative override (see §VII.Z.3). This is NOT a hard
  ceiling on all time values. Admins MAY configure an installation-wide maximum idle-timeout cap
  anywhere from 1 min up to an absolute system ceiling of 8 hours. Admins MAY
  additionally configure an installation-wide minimum idle-timeout floor; if a
  minimum floor is set, users MUST NOT configure a value below it. Users MAY
  freely configure their own idle-timeout threshold within the admin-defined
  range (minimum floor to maximum cap), or from 1 min up to the absolute
  system ceiling of 8 hours if no admin range is configured. The role-based
  defaults (§G.11) apply only as the user's active setting until they
  explicitly change it; they do not act as a ceiling on user configuration.
  Tokens or session secrets MUST be stored in memory only
  and cleared on logout or crash recovery (see §G.13 and §VII.W for the
  normative crash-recovery clearing requirements). An idle-timeout watchdog MUST
  monitor session activity and force logout after the configured threshold;
  the watchdog MUST be unit-testable in isolation with configurable thresholds.
  The system MUST display a warning to the user at least 60 seconds before
  session expiry due to idle timeout; the warning MUST give the user the
  opportunity to extend the session. The exact UI pattern and countdown display
  beyond the 60-second minimum are implementation-defined.

#### Multi-Factor Authentication

- The system MUST provide an MFA hook service (`mfa_hook_service`) as a
  two-level opt-in extension point for second-factor verification. The only
  accepted second-factor types are TOTP (time-based one-time password), email,
  and FIDO2 roaming authenticator (§G.10); no other second-factor types are
  currently accepted. FIDO2 roaming authenticators (§G.10) are accepted as an
  offline-capable second factor alongside TOTP. FIDO2 platform authenticators
  (§G.10) MAY be enrolled as convenience factors but MUST NOT, by themselves,
  satisfy the offline-capable MFA enrollment requirement (see §VII.Y).
  **Network availability is assumed** for email-based MFA; email MFA is not
  guaranteed to function in offline/air-gapped environments. TOTP MUST always
  be available as an offline-capable MFA method when MFA is enabled; TOTP MUST
  be implemented according to RFC 6238 using the default profile defined in
  §G.9 (see §VII.X for all TOTP configuration requirements). The system MUST
  require that at least one offline-capable MFA method (TOTP or FIDO2 roaming
  authenticator, §G.10) is enrolled for any account enabling MFA; enrollment
  with email as the sole MFA method MUST be rejected by the system.
  1. **Deployment level**: an `admin` or `dev` account enables or disables
     MFA availability for the entire installation. This toggle MUST NOT
     disable MFA for any account with `role = admin` or `role = dev`; MFA
     MUST remain enforced for all admin-role and dev-role accounts at all
     times regardless of the deployment setting.
  2. **User level**: within a MFA-enabled installation, each individual user
     with `role = user` or `role = readonly` enrolls or unenrolls MFA for
     their own account.
  All accounts with `role = admin` or `role = dev` MUST have at least one
  offline-capable MFA method enrolled. MFA enrollment MUST be completed for
  always-available `admin` and `dev` accounts before the installation is
  considered production-ready; all other admin-role and dev-role accounts
  MUST have MFA enrolled before their `account_status` is set to `active`.
  This requirement is system-enforced: the system MUST reject any attempt to
  set `account_status = active` for an admin-role or dev-role account that
  does not have at least one offline-capable MFA method enrolled; operator
  compliance alone is not sufficient.
  When MFA is enabled for an account, authentication MUST NOT succeed on
  primary credential alone. MFA enrollment, unenrollment, and recovery MUST
  emit audit entries. MFA recovery path: if a user loses access to all
  enrolled MFA methods, an administrator MUST perform an account-level MFA
  reset; the administrator MUST pass their own MFA challenge to verify identity
  before the reset is permitted, and the action MUST generate an audit entry. A user MUST NOT be
  permitted to unenroll their last enrolled MFA method; the system MUST block
  the unenrollment unless at least one other enrolled MFA method remains on
  the account. MFA state MUST be stored per-user in the canonical database,
  separate from the password hash.

Rationale: Centralized, auditable identity enforcement prevents privilege
escalation, enforces regulatory requirements, and protects the high-risk file
operations delivered by RFU. The always-available and break-glass accounts
guarantee that operators are never permanently locked out, while maintaining
full audit trails for accountability.

#### §VII.X — Offline-Capable Multi-Factor Authentication (MFA) Requirements

The sections below prescribe the TOTP variant, enrollment rules, and backup
code scope for all offline-capable MFA implementations. They resolve the
interoperability gap present in the existing §VII MFA text.

##### §VII.X.1 — Mandatory Standard

Offline-capable MFA MUST use Time-Based One-Time Passwords (TOTP) as defined
in RFC 6238.  
Counter-based One-Time Passwords (HOTP, RFC 4226) MAY be supported for legacy
compatibility but MUST NOT count as an enrolled MFA method for
activation-gate purposes.

##### §VII.X.2 — Default TOTP Profile (Interoperability Requirement)

All implementations MUST support the TOTP default profile defined in §G.9
(HMAC-SHA1 / 6 digits / 30-second time step / ±1 step drift tolerance). This
profile MUST be accepted by every implementation.  
Implementations MAY additionally support stronger or alternative profiles
(e.g., SHA-256, SHA-512, 8-digit codes, 60-second steps), but these MUST NOT
replace or disable the default profile.

##### §VII.X.3 — Enrollment Requirements

Enrollment MUST generate a TOTP secret that is compatible with the default
profile in §G.9.  
Enrollment MUST provide the user with a provisioning URI or QR code that
encodes the default profile parameters.  
The TOTP secret MUST be stored encrypted at rest.

##### §VII.X.4 — Verification Requirements

Verification MUST compute expected TOTP values using the default profile and
MUST accept codes within the configured drift tolerance (±1 time step).  
Verification MUST reject codes generated using unsupported algorithms, digit
lengths, or time steps unless those are explicitly configured as optional
secondary profiles.

##### §VII.X.5 — Backup and Recovery Codes

Single-use backup or recovery codes MAY be provided as an emergency fallback
mechanism.  
Backup codes MUST NOT count as an enrolled MFA method for activation-gate
purposes.  
Backup codes MUST be generated with sufficient entropy and MUST be stored
securely.

##### §VII.X.6 — Export and Import of MFA Configuration

Export and import workflows MUST preserve the TOTP secret and associated
metadata required for verification.  
Importers MUST NOT alter the TOTP secret or profile parameters unless
explicitly migrating from a documented legacy format.  
All implementations MUST remain interoperable with the default TOTP profile
after import.

##### §VII.X.7 — Deterministic Reviewability

CI and reviewers MUST verify that:
- TOTP is implemented according to RFC 6238
- The default profile (SHA-1 / 6 digits / 30 seconds / ±1 step) is supported
- HOTP is not treated as an enrolled MFA method
- Backup codes are not counted as MFA enrollment
- Drift tolerance is implemented correctly
- Enrollment and verification are covered by automated tests

See: docs/totp-spec.md (canonical spec, reference implementation, CI tests),
.specify/memory/checklist-totp-compliance.md (reviewer checklist).

#### §VII.Y — FIDO2 Authenticator Requirements

The sections below prescribe FIDO2 authenticator classification and resolve the
ambiguity in the term "FIDO2 hardware token" used in earlier §VII text.

##### §VII.Y.1 — Definitions

For the purposes of this constitution two FIDO2 authenticator classes exist;
see §G.10 for normative definitions:

- A **FIDO2 roaming authenticator** is a detachable hardware security key
  (e.g., USB-A/C, NFC, BLE) that can be used across devices.
- A **FIDO2 platform authenticator** is a device-bound authenticator integrated
  into the host device (e.g., Windows Hello, Touch ID, Face ID, TPM-backed
  keys) that is not portable across devices.

The term "FIDO2 hardware token" as used in any earlier §VII text MUST be
interpreted as "FIDO2 roaming authenticator".

##### §VII.Y.2 — Offline-Capable MFA Requirement

For the purpose of satisfying the offline-capable MFA enrollment requirement,
only the following methods qualify:

- FIDO2 roaming authenticators (§G.10); and
- TOTP compliant with §VII.X and §G.9.

FIDO2 platform authenticators MUST NOT, by themselves, satisfy the
offline-capable MFA enrollment requirement.

##### §VII.Y.3 — Platform Authenticator Pairing

Platform authenticators MAY be enrolled as additional MFA methods. If the only
enrolled FIDO2 method is a platform authenticator, the implementation MUST
ensure the user also has at least one of the following:

- a FIDO2 roaming authenticator, or
- a TOTP method compliant with §VII.X.

Implementations MUST NOT allow an account to rely solely on a platform
authenticator as its only MFA method.

##### §VII.Y.4 — Recovery and Portability

Because platform authenticators are device-bound and non-portable, a user who
loses their enrolled device loses access to the platform-authenticator
credential. Implementations MUST ensure:

- a recovery path exists via a roaming authenticator or TOTP; and
- platform authenticators are never exported as portable credential artifacts.

##### §VII.Y.5 — Enrollment and UI Clarity

Enrollment flows and user interfaces MUST clearly distinguish between the
two classes:

- Roaming authenticator MUST be labelled "Security Key" or equivalent.
- Platform authenticator MUST be labelled "This Device" or equivalent.

Implementations MUST NOT label platform authenticators as "hardware tokens"
or otherwise imply portability.

##### §VII.Y.6 — Deterministic Reviewability

CI and reviewers MUST verify that:
- Roaming and platform authenticators are correctly classified in code and UI
- Only roaming authenticators and TOTP count toward the offline-capable MFA
  enrollment requirement
- Platform-only enrollment is rejected (or requires pairing with roaming/TOTP)
- Recovery paths exist when the sole platform device is lost
- No export/import workflow treats platform credentials as portable artifacts

See: docs/fido2-spec.md (canonical spec, reference implementation, CI tests),
.specify/memory/checklist-fido2-compliance.md (reviewer checklist).

#### §VII.Z — Idle Timeout Requirements

The sections below replace the prior uniform 30-minute default and prescribe
role-differentiated idle timeout values for all implementations.

##### §VII.Z.1 — Purpose

Idle-timeout controls mitigate the risk of unauthorized access to unattended
sessions. Default values MUST reflect the privilege level and risk profile of
each account role; a uniform default MUST NOT be applied across all roles.

##### §VII.Z.2 — Role-Differentiated Default Idle Timeouts

The out-of-box default idle timeout (the value used when neither the
administrator nor the user has configured anything) MUST be the value
prescribed in §G.11 for each role:

| Role | Default idle timeout |
|------|---------------------|
| `admin` | 10 minutes |
| `dev` | 15 minutes |
| `user` | 30 minutes |
| `readonly` | 45 minutes |

Implementations MUST NOT apply a single global constant across all roles.
Privileged roles (`admin`, `dev`) MUST have shorter or equal defaults compared
to non-privileged roles (`user`, `readonly`).

##### §VII.Z.3 — Maximum Timeout Ceiling

No role's idle timeout MAY be configured longer than **60 minutes** without an
explicit administrative override. An explicit override requires:

1. A deliberate administrator action (not a default value or silent config
   change); and
2. An audit-log entry recording the actor, the role affected, the new value,
   and the timestamp.

The absolute system ceiling of 8 hours (§VII Session Controls) remains in
effect independently of this rule.

##### §VII.Z.4 — Administrative Overrides

Administrators MAY configure per-role idle timeout values that are stricter or
more permissive than the §VII.Z.2 defaults, subject to §VII.Z.3.  
All administrative overrides MUST be logged and auditable (actor, role,
previous value, new value, timestamp).

##### §VII.Z.5 — Deterministic Reviewability

CI and reviewers MUST verify that:
- Role-differentiated defaults (§G.11) are implemented in code and configuration
- Privileged roles (`admin`, `dev`) have shorter or equal defaults than
  non-privileged roles (`user`, `readonly`)
- No single global constant applies the same timeout to all roles
- Administrative overrides are logged
- Automated tests cover each role's default and at least one override scenario

See: docs/idle-timeout-spec.md (canonical spec, reference implementation, CI
tests), .specify/memory/checklist-idle-timeout-compliance.md (reviewer
checklist).

#### §VII.W — Crash-Recovery Session Clearing

The sections below resolve TODO(CRASH_RECOVERY_SESSION) (open since v1.11.0)
and prescribe mandatory behaviour for clearing session secrets after a crash.

##### §VII.W.1 — Purpose

Session tokens and session secrets MUST remain in volatile memory only. They
MUST NOT survive process termination, crash, or restart. The "cleared on crash
recovery" language in §VII Session Controls is normatively defined by
§VII.W.2–§VII.W.6 and by §G.13 (crash sentinel).

##### §VII.W.2 — Crash Handler Clearing (Best-Effort)

Implementations MAY attempt to clear session secrets in crash handlers for
recoverable signals (e.g., SIGTERM, SIGINT). This behaviour is **best-effort
only** and MUST NOT be relied upon for correctness — SIGKILL, OOM kill, power
loss, and container eviction cannot be caught.

##### §VII.W.3 — Startup-Time Clearing (Mandatory)

On startup the implementation MUST:

1. Read the crash sentinel (§G.13) state from its previous value **before**
   writing the new startup state.
2. Immediately set the crash sentinel to `dirty`.
3. If the previous sentinel state was not `clean` (i.e., it was `dirty`,
   missing, or unknown), treat the previous run as a crash and:
   - **Purge all session secrets** unconditionally.
   - **Refuse to restore any prior session.**
   - Begin with a clean session state.
4. Continue normal startup only after the purge is complete.

The startup-time clearing MUST occur before any session, preference, or
authenticated operation is performed.

##### §VII.W.4 — Crash Sentinel

Implementations MUST maintain a crash sentinel (§G.13) that satisfies:
- It is set to `dirty` at the very start of every startup (step 2 above).
- It is set to `clean` only on graceful shutdown completion.
- Any state other than explicit `clean` is treated as `dirty` (crash).
- It is stored process-externally (file, record, or equivalent) so that it
  survives a hard process kill.
- It is readable at the earliest point in the next startup before any
  session-related logic executes.

##### §VII.W.5 — OS-Level Persistence Protections

Implementations MUST ensure that session secrets do not leak into OS-level
persistence mechanisms. Where the platform supports the mechanism, the
implementation MUST:

- **Swap / paging**: Pin session memory or otherwise prevent swapping
  (e.g., `mlock(2)` on Linux/macOS, `VirtualLock` on Windows).
- **Crash dumps**: Disable crash dumps or mark session memory regions as
  non-dumpable (e.g., `MADV_DONTDUMP` on Linux, `MiniDumpWriteDump`
  exclusion on Windows).
- **Core files**: Disable or restrict core file generation for the process.
- **Hibernation images**: Treat as equivalent to crash dumps.

If a platform mechanism is unavailable or not applicable, the implementation
MUST document why instead of silently omitting the protection.

##### §VII.W.6 — Deterministic Reviewability

CI and reviewers MUST verify that:
- Crash sentinel logic is implemented (mark-dirty-on-startup,
  mark-clean-on-shutdown, check-on-startup functions all present)
- Startup-time clearing is unconditional when the sentinel is not `clean`
- No session is restored after a simulated crash
- Session secrets are excluded from swap and crash dumps (per §VII.W.5,
  where platform support exists)
- Crash-recovery behaviour is covered by automated tests

See: docs/crash-recovery-spec.md (canonical spec, reference implementation,
CI tests T1–T9, migration Steps 1–5);
.specify/memory/checklist-crash-recovery-compliance.md (reviewer checklist
Sections A–E).

### VIII. Privacy, PII Protection & Data Minimization

User privacy is a first-class obligation. The system MUST actively detect,
surface, and protect Personally Identifiable Information (PII) wherever it
could inadvertently appear in the user's file system or in application data.

- PII Detection: The directory security layer MUST include a PII detector that
  scans file paths, metadata, and file content (within scope configured by the
  user at the start of each scan session — file paths only, metadata only,
  full content, or any combination) for known PII patterns (names, email
  addresses, ID numbers, etc.). A system default scan scope MUST exist for
  new sessions; if no admin or user has configured a scope, the system default
  applies. Admins MAY configure a deployment-wide default scan scope; users
  MAY override the default unless the admin has marked the default mandatory.
  Detection results MUST be reported to the user without automatic deletion;
  remediation requires explicit user confirmation.
- Anonymization: Privacy tools (anonymizer, privacy cleaner) MUST provide
  opt-in anonymization workflows. At the start of every anonymization
  operation the user MUST explicitly select the mode — there is no default;
  no mode may be pre-selected. The user MUST make an explicit choice before
  the tool activates, and the selected mode MUST be clearly displayed to the
  user before execution begins. Displaying the selected mode prominently
  within the confirmation dialog satisfies this requirement — a separate
  prior step is not required. The specific UI pattern enforcing these
  requirements is implementation-defined.
  Irreversible operations MUST require explicit two-step confirmation: the
  user MUST type a confirmation phrase AND click a confirm button as a
  separate action; both steps are required before the operation executes.
  The specific confirmation phrase is implementation-defined per tool,
  provided that (i) it is explicitly shown to the user immediately before the
  typing step, and (ii) the user must type it exactly as displayed. The
  confirmation dialog MUST clearly state the irreversibility of the action. The operation MUST
  also log an audit entry. The following classification MUST be documented in the tool
  UI and in the developer API reference:

  **Reversible operations** (pseudonymization — originals recoverable via
  a stored mapping):
  - Name substitution (replace with placeholder token + stored mapping)
  - Email address masking (replace with token + stored mapping)
  - Generic address replacement (replace with placeholder + stored mapping)
  - Phone number tokenization
  - User-defined custom pattern replacement with mapping stored

  Each reversible operation step MUST log an audit entry.

  **Irreversible operations** (true anonymization — no recovery path):
  - Cryptographic hash replacement of any PII field
  - SSN / national-ID full redaction (overwrite with fixed redacted marker)
  - Financial account number redaction
  - Biometric data removal or hash replacement
  - Bulk scrub of all detected PII without per-field mapping
  - Any operation explicitly requested irreversible by the user

  The selected mode applies uniformly to all steps within the operation;
  mixing reversible and irreversible steps within a single operation is
  NOT permitted.
- Data Minimization: Application logs, telemetry, and audit entries MUST NOT
  contain raw file content or sensitive PII. File paths in logs MUST be
  sanitized or truncated to the minimum required for diagnostics.
- Retention & Deletion: Privacy cleaner tools MUST support user-defined
  retention policies and MUST document what data they touch. Cleanup operations
  MUST be dry-run capable before any destructive step.
- Error Recovery: Privacy operations MUST include recoverable error handling
  so that partial failures do not leave data in an inconsistent state; rollback
  checkpoints MUST be created before batch operations begin.
- Path Sanitization: All file paths presented to external processes MUST pass
  through the path sanitizer to strip shell metacharacters and prevent injection
  vectors.

Rationale: RFU operates directly on users' file systems, making it a high-risk
surface for accidental PII exposure and injection attacks. Proactive detection
and minimization protect users and meet regulatory obligations (GDPR, CCPA).

#### §VIII.X — PII Scan Result Delivery Requirements

##### §VIII.X.1 — Purpose

PII detection results MUST be visible to the user in a timely and
non-coercive manner, ensuring informed remediation without silent
accumulation of sensitive data.

##### §VIII.X.2 — User-Initiated Scans

For scans explicitly initiated by the user, results MAY be displayed
inline within the scan panel or results view. Proactive surfacing is NOT
required for user-initiated scans.

##### §VIII.X.3 — Background and Scheduled Scans

For scans initiated automatically (background or scheduled), results MUST
be surfaced proactively to the user when detection completes.

Proactive surfacing:

- MUST be non-interrupting (no modal dialogs, no forced-focus overlays);
- MUST use one of: persistent banner, notification badge, non-modal
  alert, or dashboard ribbon;
- MUST NOT require the user to navigate to a separate location in order
  to discover that findings exist.

Modal dialogs and forced-focus overlays MUST NOT be used for background or
scheduled scan results.

##### §VIII.X.4 — User Agency and Remediation

- PII MUST NOT be deleted automatically.
- Remediation (deletion or anonymization of detected PII) requires
  explicit user confirmation, regardless of whether the scan was
  user-initiated or background/scheduled.

##### §VIII.X.5 — Indicator Persistence

Proactive surfacing indicators (banners, badges, ribbons) MUST remain
visible until the user explicitly acknowledges or reviews the results.
Transient auto-dismissing toast notifications do NOT satisfy the
proactive-surfacing requirement under §VIII.X.3.

##### §VIII.X.6 — Deterministic Reviewability

CI and reviewers MUST verify that:

- background and scheduled scans surface results proactively when
  detection completes;
- user-initiated scans may display results inline without proactive
  surfacing;
- no modal dialog or forced-focus overlay is triggered for background
  scan results;
- proactive surfacing indicators persist until the user acknowledges
  or reviews results;
- remediation of any scan type requires explicit user confirmation;
- automated tests cover all of the above.

See: docs/pii-scan-ux-spec.md (canonical spec, reference implementation,
CI tests T1–T8),
.specify/memory/checklist-pii-scan-ux-compliance.md
(reviewer checklist Sections A–F).

### IX. File Validation & Content Integrity

Files processed or produced by RFU MUST be validated for content integrity
using content-based (magic bytes + heuristics) detection, not solely extension
or MIME type claims from the operating system.

- Content-Based Detection: The `file_validator` module MUST use signature
  databases and heuristics to determine actual file type independent of
  extension. Detection MUST precede every individual file `open()` call within
  any tool that reads or transforms file content sourced externally or from the
  user's filesystem; internal temporary files written and subsequently read back
  by RFU itself are exempt from this validation requirement. Where a tool opens
  the same file multiple times within a single operation, validation MUST be
  performed at least once per file per operation; subsequent opens of that same
  file within the same operation MAY use the cached validation result, provided
  the file has not changed (verified by metadata comparison such as modification
  time and size) since the initial validation.
- Policy Enforcement: Configurable policies MUST allow operators to define
  allow/deny lists for file types per operation context. Denied file types MUST
  NOT be processed; the user MUST receive a clear rejection reason that
  identifies the specific policy rule that triggered the denial. The UI pattern
  for surfacing the rejection reason is implementation-defined.
- Compatibility: The validator MUST expose a compatibility layer that
  normalizes results across Python versions and OS environments.
- Telemetry: Validation telemetry MUST record validation outcomes (type,
  result, latency) in structured form for observability. Telemetry MUST NOT
  include file content or PII.
- Failure Modes: Validation failures MUST raise typed exceptions with
  actionable messages. Operations MUST abort on failure unless the user
  explicitly approves processing an unrecognized type. Approval for an
  unrecognized file type MUST be obtained via a one-step confirmation dialog;
  no typed confirmation phrase or persistent per-session policy toggle is
  required for this approval.
- Signature Currency: Signature databases MUST be versioned and bundled in
  release artifacts. Updates to signature sets require a version bump:
  PATCH for new or updated signatures that introduce no API or policy
  change; MINOR for changes that introduce a new file-type category,
  modify the policy schema, or remove a previously supported type.

Rationale: Processing files based solely on user-supplied extensions is an
injection and malfunction risk. Content-based validation closes this attack
surface and prevents tools from silently corrupting unrecognized file formats.

#### §IX.X — Boundary Definition for "Written by RFU Itself" Exemption

##### §IX.X.1 — Purpose

The exemption for "internal temporary files written and subsequently read
back by RFU itself" (per the Content-Based Detection bullet above) applies
only to files that never cross trust boundaries. This section formally
defines those boundaries.

##### §IX.X.2 — Same-Process, Same-Instance Requirement

A file qualifies for the validation exemption only if ALL of the following
conditions are satisfied:

- the file is written by the **same RFU tool instance**;
- in the **same process** (identical OS process ID);
- during the **same application session**;
- and read back by **that same instance** without being exposed to any
  other component, tool, plugin, or external actor.

##### §IX.X.3 — Boundaries That Invalidate the Exemption

The exemption MUST NOT apply if the file crosses any of the following
boundaries after it is written:

- **process boundary** — read by a different OS process
- **tool boundary** — read by a different RFU tool (e.g., Tool A writes,
  Tool B reads)
- **plugin boundary** — written or read by a third-party plugin
- **session boundary** — written in session N, read in session N+1
- **IPC boundary** — path passed via inter-process communication
- **shared temporary directory** — any file written to a shared OS temp
  directory that another process could access
- **background or scheduled task boundary** — any handoff to a background
  worker or scheduled task

If a file crosses any of these boundaries, it MUST undergo full validation
before being opened, regardless of its stated origin.

##### §IX.X.4 — Plugin-Written Files

Files written by third-party plugins MUST NOT qualify for the exemption,
even if the plugin is registered with ComponentGuardian. Such files MUST
undergo full validation before being read by any part of the RFU core
pipeline. This is required for supply-chain security.

##### §IX.X.5 — Cross-Session and Cross-Process Files

Files written in one session or process and read in another MUST always
be validated, regardless of their origin or the identity of the writer.

##### §IX.X.6 — Exemption Guard Pattern

The exemption MUST be implemented via a tightly scoped internal helper
(e.g., `open_internal_temp_same_instance()`) backed by an **in-memory
registry** (process-local; cleared on process exit) that tracks only files
written and registered by the current process and session. The helper:

- MUST NOT be callable from plugin code;
- MUST NOT be callable from cross-tool or IPC code paths;
- MUST verify same-process and same-session identity before granting
  the exemption;
- MUST NOT persist the registry to disk (persistence would allow
  cross-session abuse).

##### §IX.X.7 — Deterministic Reviewability

CI and reviewers MUST verify that:

- the exemption is applied only to same-process, same-instance files;
- plugin-written files are always passed through the validation pipeline;
- files crossing tool, process, session, IPC, or shared-temp boundaries
  are always validated;
- the exemption helper is not accessible from plugin or cross-tool code;
- the registry is in-memory only (never persisted);
- automated tests cover same-instance exemption, cross-tool reads,
  plugin output reads, cross-session reads, and shared-temp-dir reads.

See: docs/file-validation-exemption-spec.md (canonical spec, reference
implementation, CI tests T1–T5),
.specify/memory/checklist-file-validation-exemption-compliance.md
(reviewer checklist Sections A–F).

## §7 — Menu Architecture & Nomenclature

### §7.1 Purpose

This section defines the mandatory structure, naming, behavior, and interaction
rules for all menus across the application suite. Its purpose is to ensure
cross-tool predictability, accessibility, and cognitive consistency, regardless
of platform or tool-specific GUI.

### §7.2 Global Menu Bar

All tools that expose a windowed GUI MUST inherit the **Global Menu Bar** unless
explicitly exempted by governance decision.

The Global Menu Bar consists of the following top-level menus, in this exact order:

1. **File**
2. **Edit**
3. **View**
4. **Tools**
5. **Reports** *(optional; only shown if the tool registers reporting actions)*
6. **Window**
7. **Help**

No tool may introduce additional top-level menus.

### §7.3 Menu Taxonomy & Allowed Scope

#### File
Contains actions related to opening, saving, exporting, importing, session
lifecycle, and application exit. Tools MAY add items under File only if they
relate to document- or data-level operations.

**Session lifecycle clarification**: Hub navigation items (e.g., "Return to Hub")
qualify as session lifecycle actions and MUST be placed under File. These items
are provided by the Hub (not tool-registered — see §9.7.1) and therefore do not
conflict with the tool File-item restriction in §9.7.1.

#### Edit
Contains: Undo / Redo, Cut / Copy / Paste, Select All, Find / Replace (if
applicable). Tools MAY NOT add domain-specific actions here.

#### View
Contains: Zoom controls, Layout toggles, Theme switching, Panel visibility.
Tools MAY add view-related toggles but MUST NOT place actions that modify data.

#### Tools
Contains tool-specific actions, transformations, validations, and operations
that affect data or state. This is the primary extension point for
tool-specific functionality.

#### Reports
Contains generated reports, summaries, and exports of analytical or aggregated
data. Tools MAY register reporting actions here. If no tool registers a
reporting action, the menu is hidden.

#### Window
Contains window management and navigation between open tool windows.
Hub navigation (e.g., "Return to Hub") is provided by the Hub under File
(see §7.3 File and §9.6) — it is not a Window-menu item.

#### Help
Contains About, Diagnostics, Documentation, Keyboard shortcuts, and Telemetry
& privacy information. Tools MAY NOT add items here except contextual help.

### §7.4 Nomenclature Rules

#### §7.4.1 Verb Forms
Actions MUST use imperative verbs: *"Export Report…"*, *"Validate Input"*,
*"Apply Changes"*. Passive or ambiguous forms are prohibited: *"Processing…"*,
*"Handler…"*, *"Do Action"*.

#### §7.4.2 Ellipsis Usage
Use "…" ONLY when the action opens a dialog requiring further user input. No
ellipsis for immediate actions.

#### §7.4.3 Capitalization
Title Case for menu items. Sentence case for tooltips.

#### §7.4.4 Reserved Names
The following names are globally reserved and MUST NOT be altered:
- **Preferences** (not "Settings")
- **Exit** (not "Quit")
- **About**
- **Check for Updates…**
- **Export…**
- **Undo / Redo**
- **Zoom In / Zoom Out / Reset Zoom**

### §7.5 Interaction Behavior

All menus MUST:
- Be fully keyboard navigable
- Expose accelerators (Alt+F, Alt+E, etc.)
- Expose shortcuts where applicable (Ctrl+S, Ctrl+Z, etc.)
- Respect accessibility zoom and high-contrast modes
- Maintain consistent ordering of items within each menu

### §7.6 Tool-Specific Menus

Tools with their own GUI MAY add items only under:
- **Tools**
- **Reports**
- **View**

Tools MUST NOT create new top-level menus.

### §7.7 CI Enforcement

CI MUST reject merges if:
- A tool introduces a new top-level menu
- A menu item violates nomenclature rules
- A menu item lacks an accelerator
- A menu item uses a raw string instead of a `ui_strings` token
- A menu item appears in the wrong menu category

See: docs/menu-architecture-spec.md,
.specify/memory/checklist-menu-architecture-compliance.md

---

## §8 — Command Surface Harmonization

### §8.1 Purpose

This section establishes the normative rules for how tools classify, name, and
surface their commands across all interaction surfaces: toolbars, context menus,
keyboard shortcuts, and action menus. It ensures command intent is communicated
predictably and that users can form consistent mental models across the full
suite.

<!-- RESOLVED(FONT_TOKENS_SPEC) v1.37.0: Typography & Font Token Specification
     published as docs/font-tokens-spec.md (v1.37.0). Defines 8 font tokens
     (font.body, font.bodyBold, font.mono, font.caption, font.captionBold,
     font.title, font.toolHeader, font.small), platform fallback stacks,
     minimum legibility thresholds, prohibited practices (no raw QFont
     constructors), and CI enforcement rules. TODO(FONT_TOKENS_IMPL) remains
     open for the implementation-side module in src/rfu/.
-->

<!-- RESOLVED(COMMAND_TAXONOMY) v1.37.0: Full per-tool Command Taxonomy
     published in docs/command-surface-spec.md §9 (v1.37.0). Complete
     per-tool tables covering all 35 tools across 9 categories (§9.1–§9.11)
     map each tool's Primary Action, Secondary, Destructive, Advanced, and
     Taxonomy Verbs (Inspect/Transform/Export/Apply/Revert).
-->

### §8.2 Action Classification

All tool actions MUST be classified into exactly one of four tiers:

| Tier | Label | Definition |
|------|-------|------------|
| **Primary** | Primary Action | The main, expected operation (e.g., Apply, Run, Validate) |
| **Secondary** | Secondary Action | Supportive, non-destructive operations (e.g., Preview, Export) |
| **Advanced** | Advanced Action | Expert-level or rarely used operations |
| **Destructive** | Destructive Action | Irreversible or high-impact operations (per §G.4) |

Each tool MUST document its tier assignments in its implementation documentation.

### §8.3 Command Taxonomy (Phase 2)

Commands MUST be named using the following five constitutional verbs when
applicable. Where none of the five verbs fits, an imperative verb consistent
with §7.4.1 MUST be used and the deviation noted in the tool's implementation
documentation.

| Verb | Applies to |
|------|-----------|
| **Inspect** | Read-only analysis and examination of files, metadata, or state |
| **Transform** | Reversible or lossless content modification |
| **Export** | Output to a file, clipboard, or external format |
| **Apply** | Commit a change, write a result, or perform a side-effect operation |
| **Revert** | Undo, restore, or roll back to a previous state |

Full per-tool command taxonomy mappings are published in docs/command-surface-spec.md §9
(RESOLVED v1.37.0 — see RESOLVED(COMMAND_TAXONOMY) comment above and §13.1.2).

### §8.4 Toolbar Layout Rules *(Toolbar Surfaces)*

> **Scope**: §8.4 governs **toolbar surfaces** only. For primary action
> placement on dialog surfaces, see §10.5 (Dialog Surfaces).

Where a tool exposes a toolbar:
- Primary Action buttons MUST be placed left-most in the primary action group.
- Destructive Action buttons MUST be visually separated (separator or spacing)
  from the Primary and Secondary action groups.
- Advanced Actions MUST NOT be placed in the main toolbar; they MUST appear
  in a menu or an overflow panel.
- Toolbar buttons MUST follow the component rules in §10.5 (PrimaryButton) and
  §10.6 (SecondaryButton with danger styling for Destructive Actions).

### §8.5 Keyboard Shortcut Rules

- Each Primary Action MUST have a keyboard shortcut where technically feasible.
- Keyboard shortcuts MUST NOT conflict with the global reserved accelerators
  defined in §7.5.
- If a shortcut conflict is detected at registration time the Hub MUST reject
  it per §9.4.3.
- Shortcut assignments MUST be registered through the Hub Menu Registry (§9.4)
  and MUST use the `ui_strings` token system (see §8.6).

### §8.6 String Tokens

All command labels, toolbar button labels, and context menu item labels MUST be
sourced from `ui_strings` tokens (`src/rfu/ui_strings.py`).

**Note on current status**: `src/rfu/ui_strings.py` includes the required
menu-item and command-label token coverage for the governed tool set.
CI enforcement of the `ui_strings` token requirement (§7.7, §9.12) is active
according to the canonical TODO registers in this constitution.

<!-- RESOLVED(UI_STRINGS_MENU_TOKENS) v1.37.0: Menu-item and command-label
  tokens were added for governed tool classes in src/rfu/ui_strings.py.
  This TODO is closed and no longer gates CI enforcement. -->

### §8.7 Context Menus

- Context menus MUST contain only actions relevant to the currently selected
  item or context.
- Context menu items MUST follow the same nomenclature rules as regular menu
  items (§7.4).
- Destructive Actions in context menus MUST be placed at the bottom, after a
  separator.
- Context menus MUST NOT duplicate the primary toolbar action without a clear
  contextual reason.

### §8.8 CI Enforcement

CI MUST reject merges if:
- A tool action is not classified into one of the four tiers in §8.2
- A context menu places a destructive action without a preceding separator
- A command label uses a raw string instead of a `ui_strings` token

See: docs/command-surface-spec.md,
.specify/memory/checklist-command-surface-compliance.md

### §8.9 Layout Tokens (Deferred)

Layout Tokens (LYT) are required by §11.4.9 for spacing, safe-area margins,
and non-hardcoded layout values. All tools MUST use layout tokens rather than
hardcoded spacing constants.

<!-- RESOLVED(LAYOUT_TOKENS_SPEC) v1.37.0: Layout token taxonomy published
     as docs/layout-tokens-spec.md (v1.37.0). Defines spacing tokens (xs=2px
     through xxl=32px), margin tokens (window=16px, panel=12px, item=8px,
     inline=4px), border radius tokens (sharp/soft/round/pill), and
     icon/control sizing tokens. CI MAY begin enforcing LYT compliance
     once TODO(LAYOUT_TOKENS_IMPL) is resolved (implementation module).
-->

---

## §9 — Hub Menu Integration Specification

### §9.1 Purpose

This section establishes the mandatory rules for how the **Hub** and all
**Hub-launched tools** integrate with the Global Menu Bar defined in §7.
It ensures predictable navigation, consistent menu behavior, deterministic
fallback paths, cross-tool discoverability, and a unified product identity.

The Hub is the **root of truth** for menu structure, menu registration, and
menu behavior.

### §9.2 Scope

This specification applies to:
- The Hub window
- All tool windows launched from the Hub
- All tool GUIs that expose their own menu bar
- All menu items registered by tools

This specification supersedes any tool-specific menu definitions.

### §9.3 Hub as the Menu Authority

The Hub is the **canonical owner** of:
- Top-level menu structure
- Menu taxonomy
- Reserved menu items
- Global accelerators
- Global wording and nomenclature

Tools MAY register menu items, but MAY NOT modify top-level menu names, top-level
menu ordering, reserved menu items, or global accelerators.

Tools MUST register all menu items through the **Hub Menu Registry**.

### §9.4 Hub Menu Registry

The Hub exposes a **Menu Registry API** that all tools MUST use.

<!-- TODO(HUB_MENU_REGISTRY_API): A formal Python interface specification for
     the Hub Menu Registry is not yet defined. Tools cannot comply with the
     registry requirement until this API is designed and published.
     Deliverables:
       1. Python interface definition in src/rfu/hub_menu_registry.py
       2. Registration/deregistration contract with error handling
       3. Conflict detection API returning structured errors
       4. Spec document: docs/hub-menu-registry-spec.md
     Responsible: Phase 2 implementation team.
     CI enforcement for §9.12 (raw Qt menu API rejection) MUST be gated behind
     this TODO resolving. Do not fail CI for raw Qt usage until the registry
     API is available for tools to use.
-->

#### §9.4.1 Registration Rules
Tools MUST register: their menu items, their accelerators, their tooltips,
their enable/disable conditions, and their visibility conditions.
Tools MUST NOT directly manipulate Qt menu objects.

#### §9.4.2 Deregistration
When a tool window closes, all tool-specific menu items MUST be automatically
removed. Global menu items MUST remain unaffected.

#### §9.4.3 Conflicts
If two tools attempt to register the same accelerator, the Hub MUST reject the
second registration, the Hub MUST surface a Guardian warning, and CI MUST fail
if this occurs in automated tests.

### §9.5 Hub Menu Structure

The Hub MUST expose the Global Menu Bar exactly as defined in §7:
File, Edit, View, Tools, Reports, Window, Help.

The Hub MUST populate global items, Hub-specific items, and tool-registered
items — in that order.

**Note**: §9.5 governs the *population order* of menu sources across the
entire menu bar (global → Hub-specific → tool-registered). §9.7.4 governs
the *item ordering within* each individual menu (tool actions first,
Hub-provided items last). These rules are complementary and operate at
different levels of abstraction.

### §9.6 Hub-Specific Menu Items

The Hub MUST expose the following items in addition to the global reserved items:

**File**: Return to Hub *(visible only in tool windows)*, Exit.

**View**: Show Hub Tabs, Show Tool List, Reset Layout.

**Tools**: Open Preferences…, Reload Tool Registry, Run Diagnostics….

**Window**: Hub Home, Open Tool Window…, Switch to Previous Tool.

**Help**: Hub Documentation, Keyboard Shortcuts, About Hub.

These items MUST always be present and MUST NOT be overridden by tools.

### §9.7 Tool Menu Integration Rules

#### §9.7.1 Allowed Menu Categories
Tools MAY add items only under: **Tools**, **Reports**, **View**.
Tools MUST NOT add items under File, Edit, Window, or Help unless explicitly
granted an exemption.

**Clarification on §9.8.1 (File → Return to Hub)**: The "File → Return to Hub"
item required by §9.8.1 is a **Hub-provided item** injected by the Hub into
every tool window's menu bar. It is not a tool-registered addition to File.
This distinction resolves the apparent conflict with §7.3 (which permits tools
to add document/data items to File): §9.7.1 governs items registered by tools
through the Hub Menu Registry (§9.4); Hub-provided items are exempt from this
restriction. Tools MUST NOT register their own items under File directly.

#### §9.7.2 Tool Menu Naming
Tools MUST prefix their menu items with their tool name when ambiguity is
possible (e.g., "Budgetinator: Validate Budget" if not unique).

#### §9.7.3 Tool Menu Visibility
Tool menu items MUST appear only when the tool window is active, disappear
when the tool window closes, and respect enable/disable conditions defined by
the tool.

#### §9.7.4 Tool Menu Ordering
Within each allowed menu:
1. Tool-specific actions
2. Tool-specific advanced actions
3. Tool-specific diagnostics
4. Separator
5. Hub-provided items (always last)

### §9.8 Hub–Tool Navigation Integration

#### §9.8.1 Return to Hub
Every tool window MUST expose **File → Return to Hub**, a keyboard shortcut
(default: Ctrl+H), and a Guardian fallback if the Hub is unavailable.

#### §9.8.2 Relaunch Tool Window
Tools MUST register a relaunch action: **Window → Reopen \<ToolName\>** calling
`relaunch_tool_window()`.

<!-- TODO(RELAUNCH_TOOL_WINDOW_API): `relaunch_tool_window()` does not yet
     exist in the codebase (confirmed grep: zero matches in src/). The API
     contract, signature, and integration with the Hub Window Manager (§9.8.3)
     MUST be defined and implemented during Phase 2 before this requirement
     becomes CI-enforced. Until this TODO is resolved, CI MUST NOT fail for
     missing `relaunch_tool_window()` calls. Responsible: Phase 2
     implementation team. -->

#### §9.8.3 Cross-Tool Navigation
The Hub MUST maintain a list of open tool windows and expose them under
**Window → Open Windows**. Tools MUST NOT manage this list themselves.

### §9.9 Accessibility Requirements

All Hub and tool menu items MUST: support keyboard navigation, expose
accelerators, respect zoom scaling, respect high-contrast mode, and provide
accessible names and descriptions. Tools MUST NOT override accessibility
metadata provided by the Hub.

### §9.10 Telemetry Requirements

The Hub MUST emit telemetry for: menu item activation, menu item visibility
changes, accelerator usage, tool menu registration events, and tool menu
deregistration events. Tools MUST NOT emit telemetry for menu events directly.

### §9.11 Guardian Integration

If a tool fails to register its menu items, the Hub MUST surface a Guardian
warning, the tool MUST enter degraded mode, and the Hub MUST expose a fallback
"Tool Unavailable" item under Tools.

### §9.12 CI Enforcement

CI MUST reject merges if:
- A tool attempts to add a top-level menu
- A tool registers items under prohibited menus
- A tool uses raw Qt menu APIs
- A tool registers a menu item without a `ui_strings` token
- A tool registers a menu item without an accelerator
- A tool registers a menu item with a conflicting accelerator
- A tool fails to deregister its menu items on close

### §9.13 Future Extensibility

The Hub MUST support: dynamic menu injection, dynamic menu removal, menu
versioning, menu schema validation, and localization of all menu items.
Tools MUST NOT implement their own localization logic.

See: docs/hub-menu-integration-spec.md,
.specify/memory/checklist-hub-menu-integration-compliance.md

---

## §10 — UI Interaction Contract

### §10.1 Purpose

This contract establishes the mandatory interaction patterns, behavioral
guarantees, and user-experience invariants that all tools MUST follow. Its
purpose is to ensure predictability, accessibility, and cognitive consistency
across the entire suite.

### §10.2 Scope

This contract applies to: all tool windows, all dialogs/modals/toasts, all
interactive controls, all destructive or irreversible actions, all long-running
operations, and all Hub-launched workflows.

### §10.3 Interaction Principles

All tools MUST adhere to the following principles:

1. **Predictability** — identical actions behave identically across tools
2. **Reversibility** — destructive actions require explicit confirmation
3. **Visibility** — system state and progress MUST be visible
4. **Non-blocking UI** — no UI thread blocking beyond 100 ms
5. **Accessibility** — all interactions MUST be keyboard-navigable and zoom-safe
6. **Determinism** — no hidden side effects

### §10.4 Action Classification

All actions MUST be classified as:
- **Primary Action** — the main operation (e.g., Apply, Run, Validate)
- **Secondary Action** — supportive operations (e.g., Preview, Export)
- **Destructive Action** — irreversible or high-impact operations
- **Advanced Action** — expert-level or rarely used operations

Tools MUST expose these classes consistently.

### §10.5 Primary Action Rules *(Dialog Surfaces)*

> **Scope**: §10.5 governs **dialog surfaces** only. For primary action
> placement on toolbar surfaces, see §8.4 (Toolbar Surfaces).

Primary actions MUST:
- Use a **PrimaryButton**
- Be placed in the **bottom-right** of dialogs
- Use imperative verbs
- Emit telemetry (`ui_user_action`)
- Respect dry-run mode

### §10.6 Destructive Action Rules

Destructive actions MUST:
- Use a **SecondaryButton** with danger styling
- Trigger a **confirmation modal**
- Support dry-run mode
- Emit telemetry (`ui_error_event` if failed)
- Provide a clear description of consequences

### §10.7 Long-Running Operations

All long-running operations MUST:
- Move work off the UI thread
- Display a **LoadingIndicator**
- Disable conflicting controls
- Emit telemetry (`perf_start` / `perf_end`)
- Support cancellation if feasible

### §10.8 Error Handling

All tools MUST:
- Surface errors using the shared **ModalError** component
- Provide actionable messages
- Avoid raw exception strings
- Emit telemetry (`ui_error_event`)
- Provide Guardian fallback if the tool becomes degraded

### §10.9 Navigation Rules

Tools MUST:
- Provide **Return to Hub** (per §9.8.1)
- Register with the Hub Window Manager
- Respect the global menu structure (per §7)
- Expose consistent keyboard shortcuts

### §10.10 Accessibility Rules

All tools MUST:
- Provide accessible names and descriptions
- Support full keyboard navigation
- Respect zoom scaling
- Avoid color-only indicators
- Maintain minimum touch targets (per §7 Accessibility constraint)

### §10.11 CI Enforcement

CI MUST reject merges if:
- A tool violates any interaction rule
- A destructive action lacks confirmation
- A long-running action blocks the UI thread
- A tool uses raw Qt widgets instead of shared components
- A tool omits telemetry for primary actions

See: docs/ui-interaction-contract-spec.md,
.specify/memory/checklist-ui-interaction-contract-compliance.md

---

## §11 — CI Enforcement Specification

### §11.1 Purpose

This specification defines the mandatory CI rules, automated checks, failure
conditions, and reporting requirements that enforce the **Tool Capability Matrix**
and all associated constitutional sections. Its purpose is to ensure:
- Deterministic enforcement of governance
- Prevention of regressions
- Uniform behavior across all tools
- Zero reliance on human memory or reviewer intuition
- Auditability and traceability of compliance

CI is the **final authority** on whether a tool is allowed to merge.

### §11.2 Scope

CI MUST enforce:
- All harmonization domains (TH, DR, CP, A11Y, PERF, ERR, GRD, TEL, STR, CE, HUB)
- All interaction rules (INT)
- All operational guarantees (OPS)
- All menu, nomenclature, typography, and layout rules (MEN, NOM, FNT, LYT, WRD)
- All localization readiness rules (L10N, when enabled)

CI MUST reject merges that violate any rule in this section.

### §11.3 CI Architecture Overview

CI MUST consist of the following enforcement layers:

1. **Static Analysis Layer** — Detects violations in code, strings, menus, fonts, and layout.
2. **Schema Validation Layer** — Validates tool metadata, menu registrations, telemetry schemas, and preference schemas.
3. **Runtime Test Layer** — Executes automated UI tests, Guardian tests, CE tests, and performance tests.
4. **Matrix Compliance Layer** — Ensures each tool satisfies all required capabilities.
5. **Reporting Layer** — Produces machine-readable compliance reports and human-readable summaries.

Each layer MUST run on every PR.

### §11.4 Static Analysis Rules

CI MUST fail if any of the following are detected:

#### §11.4.1 Theming (TH)
Raw color values (hex, rgb, rgba); raw font declarations; missing theme token
usage; missing `_on_theme_changed` handlers.

#### §11.4.2 Dry-Run (DR)
Destructive actions without dry-run branching; missing dry-run toggle wiring.

#### §11.4.3 Shared Components (CP)
Raw Qt widgets where shared components exist; custom button classes duplicating
Primary/SecondaryButton; custom modal implementations.

#### §11.4.4 Accessibility (A11Y)
Missing accessible names; missing accessible descriptions; color-only
indicators; touch targets below minimum size.

#### §11.4.5 Error Handling (ERR)
`str(e)` surfaced directly to UI; missing `logger.error`; missing error codes;
missing ModalError usage.

#### §11.4.6 Strings (STR)
Raw user-visible strings not in `ui_strings.py`; hardcoded English text;
missing string tokens.

#### §11.4.7 Menu Architecture (MEN)
Tools adding top-level menus; tools registering items under prohibited menus;
missing accelerators; violations of nomenclature rules.

#### §11.4.8 Typography (FNT)
Raw font families; raw pixel sizes; missing font tokens.

#### §11.4.9 Layout (LYT)
Missing safe-area margins; hardcoded spacing not using layout tokens;
inconsistent padding.

#### §11.4.10 Wording (WRD)
Non-imperative verbs in action labels; incorrect ellipsis usage; inconsistent
capitalization.

### §11.5 Schema Validation Rules

CI MUST validate:

#### §11.5.1 Menu Registry Schema
All menu items registered via Hub Menu Registry; no direct Qt menu manipulation;
no accelerator conflicts; correct menu category usage.

#### §11.5.2 Telemetry Schema
All events follow naming conventions; required fields present; no unregistered
event types.

#### §11.5.3 Preference Schema
All preferences follow naming conventions; versioning rules respected; migration
scripts present when needed.

#### §11.5.4 Tool Metadata Schema
Tool name, tool classification (Standard / CE), tool capabilities, tool owner.

### §11.6 Runtime Test Rules

CI MUST execute:

#### §11.6.1 UI Interaction Tests (INT)
Primary actions use PrimaryButton; destructive actions trigger confirmation
modals; LoadingIndicator appears for long-running operations; no UI thread
blocking > 100 ms.

#### §11.6.2 Guardian Tests (GRD)
`register_gui_component()` called; `health_check()` returns valid state;
`degraded_fallback()` functional.

#### §11.6.3 Critical Engine Tests (CE)
For CE-classified tools: property-based tests, scenario tests, irreversibility
tests, security-sensitive behavior tests.

#### §11.6.4 Performance Tests (PERF)
Worker offloading verified; no synchronous I/O on UI thread; perf markers
emitted.

### §11.7 Matrix Compliance Rules

CI MUST:
- Load the Tool Capability Matrix (§12)
- Evaluate each capability for the tool under test
- Fail if any required capability is missing
- Fail if any capability is marked "Partial"
- Fail if any capability is marked "Unknown"

Tools MUST be **fully compliant** to merge.

**JSON schema alignment**: The machine-readable matrix
(`docs/tool-capability-matrix.json`) uses three values: `true` (compliant),
`false` (non-compliant), `null` (unknown/undeclared). "Partial" and "Unknown"
in this section are **governance-level semantic states**, not JSON values.
`null` maps to the "Unknown" state; CI MUST fail on `null` for required
capabilities. "Partial" means incomplete compliance and is treated as `false`
by CI. No additional JSON values are defined. The `?` symbol used in
`docs/tool-capability-matrix-template.md` is a **display-only** representation
of `null` and carries no additional machine-readable semantics.

### §11.8 Reporting Requirements

#### §11.8.1 Machine-Readable Report
JSON file; one entry per capability; Pass/Fail/Not Applicable; error messages;
line numbers for violations.

#### §11.8.2 Human-Readable Summary
Markdown summary; capability table; violations grouped by category; suggested
fixes.

#### §11.8.3 Hub Dashboard Integration
CI MUST update the Hub's governance dashboard with: tool compliance status,
last reviewed date, reviewer, and phase gate status.

### §11.9 Failure Conditions

CI MUST fail the PR if any rule in §11.4–§11.7 is violated, any test fails,
any schema validation fails, any capability is missing, any reserved name is
violated, any accelerator conflict exists, or any raw string is detected.

CI MUST NOT allow overrides except by constitutional amendment.

### §11.10 Future Extensibility

CI MUST support: localization checks (L10N), plugin tool validation,
multi-tool scenario validation, and cross-tool consistency checks.
Tools MUST NOT implement their own CI logic.

See: docs/ci-enforcement-spec.md,
.specify/memory/checklist-ci-enforcement-compliance.md

---

## §12 — Tool Capability Matrix

The Tool Capability Matrix is the normative governance artifact that tracks
compliance for every tool in the suite. It MUST be maintained and updated
whenever a tool's compliance status changes.

### §12.1 Capability Codes

| Code | Domain | Required |
|------|--------|----------|
| **TH** | Theming compliance (tokens, live updates) | Yes |
| **DR** | Dry-run support before destructive actions | Yes |
| **CP** | Shared components (buttons, modals, toasts) | Yes |
| **A11Y** | Accessibility compliance | Yes |
| **PERF** | UI-thread audit, worker offloading | Yes |
| **ERR** | Error handling contract | Yes |
| **GRD** | Guardian registration & fallback | Yes |
| **TEL** | Telemetry events (load, action, error, perf) | Yes |
| **STR** | Centralized strings | Yes |
| **CE** | Critical Engine tests (if applicable) | Conditional |
| **HUB** | Hub integration & relaunch | Yes |
| **MEN** | Menu architecture compliance (§7) | Yes |
| **NOM** | Nomenclature — structural UI naming: menu items, action labels, command names, reserved verbs (§7.4.1, §7.4.4) | Yes |
| **FNT** | Font token compliance (see docs/font-tokens-spec.md v1.37.0 — RESOLVED) | Yes |
| **LYT** | Layout structure compliance (see docs/layout-tokens-spec.md v1.37.0 — RESOLVED) | Yes |
| **WRD** | Wording/Microcopy — contextual runtime text: tooltips, body text, error messages, toasts (§7.4.2, §7.4.3) | Yes |
| **INT** | UI Interaction Contract compliance (§10) | Yes |
| **OPS** | Operational Guarantees compliance <!-- TODO(OPS_PHASE3_SPEC): OPS compliance requires constitutionalizing Phase 3 (§13.2 — Undo/Redo Semantics, Cross-Tool Error Taxonomy, Cross-Tool Logging, State Persistence). Phase 3 is not yet constitutionalized as of v1.35.0. OPS is marked Required to track intent; however, CI MUST NOT fail for OPS non-compliance until the Phase 3 constitutional sections and their spec documents are published. This TODO is open until §13.2 items are formally constitutionalized. --> | Yes |
| **CI** | CI rule compliance (§11) | Yes |
| **L10N** | Localization readiness | Future |

### §12.2 Per-Tool Tracking

For each tool, the matrix MUST track:
- Compliance status per capability (☑ compliant / ☐ non-compliant / N/A)
- Tool Owner
- Last Reviewed date
- Reviewer name
- Phase Gate Status

The canonical template is maintained in docs/tool-capability-matrix-template.md.

### §12.3 CI Integration

The Tool Capability Matrix MUST be:
- Machine-readable (JSON or YAML)
- Validated by CI on every PR (per §11.7)
- Updated as part of any PR that changes tool capabilities

The canonical machine-readable matrix is maintained in
`docs/tool-capability-matrix.json`. This file is the authoritative tool
registry for CI validation. The authoritative tool count is determined by
`docs/tool-capability-matrix.json` — refer to the registry rather than any
numeric count in this document (the prior "22 tools" count in earlier
harmonization2 source documents reflected an earlier state of the codebase).

**Current harmonization phase**: Phase 1 is complete. Phase 2 (Interaction
Model & UX Determinism) is newly active as of v1.35.0. §10 (UI Interaction
Contract) and §8 (Command Surface Harmonization) are the Phase 2 governing
sections.

---

## §13 — Harmonization Roadmap

This section documents the harmonization roadmap for governance traceability.
The roadmap is organized by dependency order and governance leverage.

### §13.1 Phase 2 — Interaction Model & UX Determinism

Phase 2 is **constitutionally complete** as of v1.36.0. All three items below
are governed by normative sections. Implementation backlog items are tracked
outside the constitution.

- **§13.1.1 Unified Interaction Patterns** — Standardized modal patterns, toast
  semantics, LoadingIndicator semantics, navigation rules. Governed by §10.
- **§13.1.2 Command Surface Harmonization** — Normalized toolbar layout, keyboard
  shortcuts, context menus, action grouping (Primary, Secondary, Advanced).
  Command Taxonomy: Inspect, Transform, Export, Apply, Revert.
  Governed by §8 (structural framework). <!-- RESOLVED(COMMAND_TAXONOMY) v1.37.0:
  Full per-tool action-to-verb mapping published in docs/command-surface-spec.md §9;
  all 35 tools covered across 9 categories (§9.1–§9.11). -->
- **§13.1.3 Hub UX Cohesion** — Tool capability badges (DR, CE, A11Y,
  PERF-critical), recent activity / last-run state, tool health indicators
  from ComponentGuardian. Constitutional governance via §9 (Hub Menu
  Integration). <!-- TODO(HUB_UX_COHESION): Badges, last-run state, and
  health indicators are Hub-level implementation items. They are NOT
  constitutional requirements; they are implementation backlog only.
  This TODO is open until Hub UX Cohesion implementation is delivered. -->

### §13.2 Phase 3 — Operational Guarantees & Cross-Tool Contracts

Phase 3 makes the suite predictable, auditable, and enforceable.

- **§13.2.1 Unified Undo/Redo Semantics** — Tools MUST declare whether undo is
  supported; consistent Undo Stack view; undoable actions logged to telemetry.
- **§13.2.2 Cross-Tool Logging & Audit Trail** — Standard event schema, standard
  correlation IDs, standard error codes, standard perf markers.
- **§13.2.3 Cross-Tool Error Taxonomy** — Global error code registry; tool domain
  errors mapped into shared taxonomy; HubErrorScreen interprets all codes.
- **§13.2.4 State Persistence & Preference Contracts** — Preference schema
  contract: naming conventions, versioning rules, migration rules,
  export/import invariants; all tools use the same preference storage backend.

### §13.3 Phase 4 — Tool-Level Harmonization & Quality Gates

Phase 4 enforces consistency across all tools.

- **§13.3.1 Tool Capability Matrix** — Per-tool compliance sheet (§12).
  Implemented in §12. This is the governance dashboard.
- **§13.3.2 Cross-Platform Behavioral Parity** — Same keyboard shortcuts, layout
  rules, fallback behavior, and Guardian degradation semantics.
- **§13.3.3 CI Enforcement** — CI checks for missing ui_strings, missing
  telemetry, missing Guardian registration, missing dry-run support, missing
  accessibility metadata, UI-thread blocking > 100ms, preference schema
  violations. Implemented in §11.

### §13.4 Phase 5 — Future-Proofing & Extensibility

- **§13.4.1 Multilingual Support** — Locale packs, runtime locale switching,
  missing-string detection in CI.
- **§13.4.2 Plugin Architecture for Tools** — Declarative tool registration,
  command surfaces, preferences, and telemetry schemas.
- **§13.4.3 Cross-Tool Scenario Flows** — Tool pipelines (A → B → C), shared
  data models, shared validation rules.

---

## Additional Technical & Quality Constraints

1. Language & Framework: Python ≥ 3.12, Qt5 GUI. Migration past EOL versions
   MUST be planned before upstream EOL minus 90 days. "Planned" requires a
   milestone-bound, assigned migration issue in the authoritative tracker
   created ≥90 days before EOL; mental notes, informal discussions, and
   un-milestoned issues do not satisfy this requirement. See §1.X for the
   complete normative definition and CI enforcement requirements.

    <!-- TODO(EOL_PLANNING_DELIVERABLE): RESOLVED — see §1.X below.
         Minimum deliverable: milestone-bound, assigned migration issue
         in authoritative tracker. CI gate required. Maintainer / Release
         Steward is responsible. Closed in constitution v1.33.0. -->

    #### §1.X — EOL Migration Planning Deliverable

    ##### §1.X.1 — Purpose

    Migration past upstream EOL versions MUST be planned in advance to
    ensure continuity, security, and maintainability. This section defines
    what "planned" means for the purposes of §1 and makes the 90-day
    deadline CI-enforceable.

    ##### §1.X.2 — Definition of "Planned"

    A migration is considered **"planned"** only when a migration issue
    exists in the project's authoritative issue tracker that includes ALL
    of the following:

    - the upstream component and version approaching EOL;
    - the upstream EOL date;
    - the required migration target version or replacement;
    - an **assigned owner** (a named, human-attributable person);
    - a **milestone with a due date**;
    - a description of required migration steps or investigation tasks
      (MAY reference an external design document).

    The following MUST NOT satisfy the "planned" requirement:

    | Candidate | Reason it fails |
    |---|---|
    | Mental note by a developer | Not trackable or auditable |
    | Informal team discussion | Not auditable |
    | Filed issue with no milestone | No deadline |
    | Filed issue with no assignee | No ownership |

    ##### §1.X.3 — Deadline

    The migration issue defined in §1.X.2 MUST be created no later than
    **90 days before the upstream EOL date**. Late creation does not
    retroactively satisfy the requirement.

    ##### §1.X.4 — Responsibility

    The **Maintainer or Release Steward** is the responsible party for:

    - tracking upstream EOL dates for all project dependencies;
    - creating the migration issue before the 90-day deadline;
    - ensuring the issue is assigned and milestone-bound;
    - ensuring CI passes the EOL-planning gate.

    ##### §1.X.5 — CI Enforcement

    CI MUST enforce the EOL-planning requirement via an EOL-tracking
    configuration file (e.g., `eol.yaml`) that lists:

    - all tracked upstream dependencies and their current versions;
    - upstream EOL dates;
    - the migration-issue reference (tracker ID or URL) for each
      dependency whose EOL is within 90 days.

    CI MUST perform the following checks on every build:

    1. For each dependency with EOL < 90 days away, a migration issue
       reference MUST exist in the configuration file.
    2. The referenced issue MUST satisfy all requirements in §1.X.2
       (assignee, milestone, migration target, actionable description).
    3. **CI MUST fail** if any dependency with EOL < 90 days has no
       valid, compliant migration issue.

    CI MAY additionally warn when EOL is < 180 days (advisory), but the
    90-day gate is the mandatory enforcement boundary.

    ##### §1.X.6 — Deterministic Reviewability

    Reviewers MUST verify that:

    - the `eol.yaml` (or equivalent) configuration file exists and is
      up to date;
    - every dependency with EOL < 90 days has a compliant migration
      issue listed;
    - the migration issue was created before the 90-day deadline;
    - the CI EOL-planning gate is active and cannot be bypassed;
    - no PR introduces or upgrades an EOL-bound dependency without a
      compliant migration issue.

    See: docs/eol-planning-deliverable-spec.md (canonical spec, CI
    enforcement details, `eol.yaml` schema),
    .specify/memory/checklist-eol-planning-compliance.md
    (reviewer checklist Sections A–F).

2. Code Style: PEP 8 enforced; mypy type checking with no new errors allowed.
3. Security: All external inputs (paths, metadata) MUST be validated; no
   shell command execution without explicit sanitization. Secure delete MUST
   document overwrite algorithm. Sensitive logs MUST be redactable.
4. Logging & Errors: No silent failures; user-facing errors MUST provide
   actionable remediation guidance. Internal stack traces logged at DEBUG+.
5. Coverage & Gates: PRs MUST pass: lint, type check, unit + integration tests,
   coverage ≥ threshold, GUI smoke test (launch + open every tool bundled
   under the launcher + validate tool class imports), tool validation
   (import success + instantiation check), and dry-run surface check (every
   tool that performs side-effect operations MUST have a visible dry-run UI
   element present and reachable before any action begins). Failing gate →
   reject.
6. Performance Baselines: Duplicate scanning: ≥ 10k files/min on reference
   dataset (documented). File search (name-based traversal): ≥ 50k files/min
   on reference dataset. Metadata extraction: ≥ 20k files/min on reference
   dataset. File copying: CPU overhead MUST NOT exceed 10% above the native OS
   copy baseline on reference hardware (copying is I/O-bound; no hardware-
   independent throughput floor is prescribed). UI thread blocking MUST NOT
   reach or exceed 100ms for any continuous blocked period (consistent with
   §IV governing rule; prior wording "< 100ms segments" is superseded by this
   expression). Long-running tasks MUST expose cancellable progress.
7. Accessibility: Each tool MUST define its own "key actions" list in its
   implementation documentation; all defined key actions MUST be reachable via
   keyboard. The specific UI pattern is implementation-defined per tool. Color
   selections MUST meet the following WCAG AA contrast requirements: (a)
   standard text: ≥ 4.5:1 contrast ratio (base rule for all text unless an
   exception applies); (b) large text (≥ 18 px regular weight or ≥ 14 px bold
   weight): ≥ 3:1 contrast ratio; (c) icons, borders, and interactive controls
   (non-text UI components): ≥ 3:1 contrast ratio. Additionally: (d) logical
   tab/focus order MUST be maintained in all custom widgets, following the
   visual reading order; (e) all interactive controls MUST carry accessible
   labels (Qt accessibility text or equivalent) for screen reader
   compatibility; (f) any animated or transitioning UI elements MUST respect
   the operating system reduced-motion preference; (g) minimum interactive
   control touch/pointer target size MUST be ≥ 44 × 44 logical
   (device-independent) pixels, consistent with WCAG 2.1 SC 2.5.8.
8. Documentation: New tools MUST include: purpose, usage examples, expected
   performance characteristics, error codes, and test strategy summary.
9. Dependency Management: New runtime dependency MUST justify: necessity,
   security posture, maintenance health. Vendoring considered for small libs.
10. Backward Compatibility: Public CLI flags and scripting APIs require a
    deprecation period of **≥ 1 MINOR release** (canonical minimum;
    <!-- TODO(GOVERNANCE_DOC): "Governance §6" is a forward-pointer to a
         planned docs/governance.md. Until that document exists, the
         ≥ 1 MINOR release rule stated here is the complete authoritative
         deprecation rule. -->
    see Governance §6 [TODO: governance doc not yet created]) unless a
    security issue mandates fast removal.

11. Preference Schema & API:

    - Typed values: `value_type` MUST be enforced (`string`, `int`, `float`,
      `bool`, `json`). Invalid values MUST be rejected at write-time.
    - Namespacing: Categories MUST be snake_case (kebab-case is NOT permitted);
      module-owned categories MUST be prefixed with module scope
      (e.g., `module_settings_af`).
    - Auditability: Preference writes MUST emit structured audit events.
    - Caching: Read-through caching MAY be used but MUST invalidate on write.
    - Fallback: When DB is unavailable, JSON fallback MUST mirror API semantics
      and migrate to DB when restored.

12. Data Migration:

    - Schema updates MUST be idempotent and version-gated; both up and down
      migration paths MUST be supported where technically feasible.
    - Migrations MUST be tested (up/down where technically feasible) and time-bounded.
      Each migration file MUST declare its own expected maximum run duration
      inline (e.g., as a comment or metadata field at the top of the file);
      no universal ceiling is prescribed by the constitution.
    - On failure, system MUST roll back to a safe checkpoint and surface user
      guidance.

13. Separation of Concerns:

    - Core functionality MUST not embed user-specific defaults; read them via
      the preference API.
    - Modules MUST function with defaults if preferences are absent.

14. Authentication Data Handling:

    - `user_accounts` data MUST reside in the canonical database, keyed by a
      unique `user_id` surrogate primary key. Each record MUST also carry a
      unique `username` field. Other fields include: Argon2id password hash,
      per-user preference namespace, role,
      `account_status` (`pending` | `active` | `suspended` | `breakglass`),
      `is_blocked` flag, `is_breakglass` flag (permanently identifies a
      break-glass emergency account; authentication is permitted only when
      the break-glass CLI flag or environment variable is explicitly active),
      and `login_attempts` counter (together with `is_blocked`, constituting
      the lockout status).
      The `account_status` field is distinct from `role`; an account with
      `account_status = pending` has no access regardless of its `role` assignment.
      `is_blocked` is a sub-state of `active` only: the lockout counter and
      `is_blocked` flag are only meaningful when `account_status = active`.
      `pending`, `suspended`, and `breakglass` accounts already have no access
      and cannot be placed into a blocked state. Admin unblock operations reset
      `is_blocked` and the `login_attempts` counter only; they do not alter
      `account_status`. When an account transitions out of `active` (e.g., to
      `suspended`; a regular account MUST NEVER transition to `account_status =
      breakglass` — that status is reserved exclusively for break-glass
      emergency accounts provisioned with `is_breakglass = true`), the
      `is_blocked` flag and `login_attempts`
      counter MUST be atomically reset to their initial values (false and zero
      respectively); when the account subsequently returns to `active` status,
      it MUST be in a clean, unblocked state.
    - Credential APIs MUST never expose password hashes. Administrative tools
      MAY return generated temporary passwords once (on creation/reset) and MUST
      log the actor + delivery channel.
    - Failed login attempts MUST atomically increment `login_attempts`,
      update `last_failed_login`, and set `is_blocked` when the lockout
      threshold is reached. Successful logins MUST atomically reset
      `login_attempts` to zero and `is_blocked` to false, and stamp
      `last_login`; `last_failed_login` is NOT modified on a successful login.

15. Credential Reset & Account Lifecycle:

    - Password policies: minimum 12 characters, at least 3 character classes,
      reject breached passwords via denylist when network connectivity allows.
      The denylist source is implementation-defined, subject to the following
      constraints: (i) the system MUST support offline operation via a local
      denylist; (ii) if an external API is used, it MUST employ a
      privacy-preserving protocol (e.g., k-anonymity) such that no full
      password or full password hash is ever transmitted externally; (iii)
      full passwords and full password hashes MUST NEVER be transmitted to any
      external service regardless of the denylist implementation chosen.
      Breached-password checks are advisory when the network is unavailable —
      they MUST NOT block account creation or password reset in offline
      environments; a user-visible warning (as defined in §G.1) MUST be
      emitted instead. A user-visible warning under this section MUST appear
      automatically in the active foreground UI; placement in a log panel or
      status bar does not satisfy this requirement.
    - Reset flow MUST be auditable and require either the admin passing their
      own MFA challenge or a time-limited, cryptographically signed challenge
      token (e.g., an HMAC-signed reset token delivered via an out-of-band
      channel such as email or secure message). The token MUST be single-use, expire after a
      maximum of 1 hour (tokens not redeemed within 1 hour MUST be
      invalidated), and its issuance and redemption MUST both be
      recorded in the audit log.
      (This §15 reset token governs account-recovery operations only, with a
      maximum validity of 1 hour and out-of-band delivery. It is explicitly
      distinct from the §G.5 headless HMAC token, which governs
      destructive-operation authorization per §II.5 with a maximum validity
      of 5 minutes and is single-use per destructive operation.)
    - Account deletion MUST also delete or anonymize linked preference data.

16. Session Management & Auditing:

    - Session identifiers MUST be random, 128-bit entropy minimum, and stored
      in memory only. Scripts, automation, or headless processes that require
      credential persistence MUST use a separately designed credential
      mechanism (e.g., a scoped API token or service account); session
      identifiers MUST NOT be written to the OS keyring or any persistent
      storage. The design of this scoped-token or service-account mechanism
      is deferred to a future implementation (see TODO(HEADLESS_AUTH)).
    - Audit log retention for identity events MUST be ≥ 365 days. Log entries
      MUST include: `username` (the subject of the action — the account being
      acted upon), `actor` (the authenticated user performing the action, e.g.,
      the admin executing a reset or unblock; for self-service events
      (`login_success`, `logout`) `actor` equals `username`; for
      `login_failure` `actor` holds the attempted username regardless of
      whether the identity is verified), `action` (representative values
      include `login_success`, `login_failure`, `reset`, `unblock`, `logout`;
      additional action types are valid for other auditable events), and
      correlation IDs. Headless HMAC token issuance and redemption (§II.5.5)
      are additional auditable event types subject to this retention
      requirement; the required field set for these entries is defined in
      §II.5.5.
    - Automated anomaly detection MUST flag >10 failed attempts within any
      rolling 24-hour window per user, and escalate via two channels:
      (1) emit a `CRITICAL`-level structured log entry; and (2) surface
      an in-app alert in the RFU hub to all currently logged-in
      `admin`-role and `dev`-role users. No external email or webhook is required by
      the constitution. The anomaly-detection mechanism and the consecutive-
      failure lockout mechanism (§VII) are independent; once the lockout
      mechanism fires and `is_blocked` is set, anomaly detection does not
      additionally apply to that account while it remains blocked.
      The "rolling 24-hour window" MUST be implemented as a sliding window
      evaluated at per-second resolution on every authentication attempt;
      fixed-period or calendar-anchored windows MUST NOT be used; detection
      MUST trigger immediately at the attempt that crosses the threshold.
      See §16.Y for the full normative definition.

    <!-- TODO(AUDIT_ORIGIN_METADATA): RESOLVED — see §16.X below.
         Minimum origin metadata fields constitutionally prescribed.
         Privacy constraints (no raw IP, hostname, OS username) codified.
         CI reviewability requirements added. Closed in v1.27.0. -->

    #### §16.X — Origin Metadata Requirements (Resolves TODO(AUDIT_ORIGIN_METADATA))

    ##### §16.X.1 — Purpose

    Origin metadata provides the contextual information necessary to
    attribute audit events to a specific actor, session, device, and
    network origin. It ensures forensic usefulness while respecting privacy
    and regulatory constraints.

    ##### §16.X.2 — Minimum Origin Metadata (All Events)

    All audit events MUST include the following origin metadata fields:

    - `actor_username`
    - `session_id`
    - `device_id` (hashed or pseudonymized)
    - `app_instance_id`

    These fields MUST be present regardless of event type, including
    background tasks, administrative actions, authentication events,
    failures, and headless HMAC token events (§II.5.5).

    ##### §16.X.3 — Additional Metadata for Network-Originating Events

    For events originating from a network request, the following fields
    MUST also be included:

    - `client_ip_hash` (pseudonymized; raw IP MUST NOT be stored)
    - `user_agent`
    - `protocol`

    If an event does not originate from a network request (e.g., a
    scheduled task or local system action), these fields MAY be omitted.

    ##### §16.X.4 — Privacy Constraints

    Implementations MUST NOT store the following in audit logs:

    - raw IP addresses
    - hostnames
    - OS-level usernames
    - hardware serial numbers
    - unique device identifiers beyond a pseudonymized `device_id`

    Pseudonymization MUST be applied using a stable, one-way hashing
    mechanism that allows correlation across events without revealing
    personal data.

    ##### §16.X.5 — Field Consistency

    All audit events MUST use consistent field names, types, and structures
    for origin metadata. Implementations MUST NOT vary field names across
    event types or application modules.

    ##### §16.X.6 — Deterministic Reviewability

    CI and reviewers MUST verify that:

    - all audit events include the required minimum metadata fields;
    - network-originating events include the required network metadata
      fields;
    - no prohibited PII fields are logged;
    - pseudonymization of IP addresses and device identifiers is
      implemented;
    - origin metadata is consistent across all event types;
    - automated tests cover presence, absence, and pseudonymization
      behaviour.

    ##### §16.X.7 — Backward Compatibility

    Existing audit logs MAY omit fields introduced in this section.
    However, all new audit events generated after this amendment MUST
    comply fully with §16.X.

    See: docs/audit-origin-metadata-spec.md (canonical spec, reference
    implementation, CI tests T1–T9),
    .specify/memory/checklist-audit-origin-metadata-compliance.md
    (reviewer checklist Sections A–F).

    #### §16.Y — Sliding 24-Hour Anomaly Detection Window

    ##### §16.Y.1 — Purpose

    The anomaly-detection threshold of ">10 failed attempts within any
    rolling 24-hour window per user" requires a precise definition of
    "rolling" to ensure consistent, secure, and testable implementation.
    Fixed-period windows create exploitation blindspots; sliding-window
    evaluation with immediate detection closes them.

    ##### §16.Y.2 — Sliding Window Requirement

    The 24-hour window MUST be implemented as a **sliding window** evaluated
    at the time of each authentication attempt. The window spans:

    ```
    window_start = now − 24h
    window_end   = now
    ```

    where `now` is the UTC timestamp at the moment of the current attempt.
    Fixed-period windows (e.g., calendar day, midnight reset, or epoch-
    anchored periods) MUST NOT be used.

    ##### §16.Y.3 — Time Resolution

    The sliding window MUST be evaluated with **per-second resolution**.
    Failure timestamps MUST be stored with at least second-level precision
    (sub-second is permitted but not required). Coarser resolutions (minute,
    hour, or calendar boundaries) MUST NOT be used.

    ##### §16.Y.4 — Immediate Detection

    Anomaly detection MUST trigger **immediately** at the authentication
    attempt that causes the count of failed attempts in the preceding 24
    hours to exceed 10. Detection MUST NOT be deferred to background tasks,
    periodic sweeps, or batch processes.

    ##### §16.Y.5 — Background Sweeps (Optional)

    Implementations MAY perform periodic background sweeps for analytics
    or audit-reporting purposes. Such sweeps MUST NOT replace per-attempt
    sliding-window evaluation as the primary detection mechanism.

    ##### §16.Y.6 — Deterministic Reviewability

    CI and reviewers MUST verify that:

    - sliding-window logic evaluates `now − 24h` relative to the current
      attempt timestamp, not a fixed period;
    - per-attempt evaluation is invoked from the authentication attempt
      code path (not only from background jobs);
    - failure timestamps are stored at per-second (or finer) precision;
    - fixed-period or midnight-reset logic is absent;
    - detection triggers at attempt N+1 (where N = 10), not deferred;
    - automated tests cover: below-threshold clusters, threshold-crossing,
      boundary at exactly 24h, and straddling of calendar midnight.

    See: docs/anomaly-detection-sliding-window-spec.md (canonical spec,
    reference implementation, CI tests T1–T5),
    .specify/memory/checklist-anomaly-detection-compliance.md
    (reviewer checklist Sections A–E).

17. Lockout Prevention (Always-Available Accounts):

    - The system MUST provision two always-available accounts (one `dev`, one
      `admin`) during database initialization.
    - These accounts MUST NOT be deletable or deactivatable via standard
      UI/CLI/API flows; removal requires direct database modification with
      audit trail. The required audit-trail mechanism is a mandatory CLI
      wrapper that writes a structured audit entry before executing the
      modification; manual procedures are forbidden; if the audit entry
      cannot be written, the modification MUST be blocked. See §17.Z for
      the complete normative definition.
    - Password initialization MUST occur via secure operator procedure, never
      hard-coded defaults.
    - Implementation MUST include an `is_protected` flag on user records to
      enforce deletion/deactivation guards.
    - The full scope of `is_protected` is constitutionally defined per §G.12
      and §DW17.X below. The flag blocks six operations: deletion,
      deactivation, suspension, admin-initiated password reset, role change,
      and username change. Self-service password changes by the account owner
      remain permitted.

    #### §DW17.X — Scope of is_protected (Resolves TODO(IS_PROTECTED_SCOPE))

    ##### §DW17.X.1 — Purpose

    The `is_protected` flag designates accounts that MUST remain permanently
    available, permanently privileged, and immune to administrative
    modification. It is the sole constitutional mechanism for protecting
    always-available accounts from being weakened, hijacked, or renamed by
    other administrators or automated systems.

    ##### §DW17.X.2 — Password Reset Protection

    For accounts where `is_protected == true`:
    - Self-service password changes by the account owner are **permitted**.
    - Password resets initiated by any other administrator, automated system,
      or API caller are **forbidden**.
    - Admin-initiated and API-initiated resets MUST fail with a
      `protected_account_error` (not a generic failure or silent no-op).

    ##### §DW17.X.3 — Role Change Protection

    For accounts where `is_protected == true`:
    - Role changes (escalation or demotion) are **forbidden**.
    - The role assigned at account creation is immutable.
    - Attempts to modify the role via UI, API, migration, or direct DB write
      MUST fail with a `protected_account_error`.

    ##### §DW17.X.4 — Username Protection

    For accounts where `is_protected == true`:
    - The username is immutable.
    - Renaming the account is **forbidden** at all layers (UI, API, service
      layer, database).
    - Attempts to rename MUST fail with a `protected_account_error`.
    - Database-level constraints (unique + immutable username column guard)
      are strongly recommended as defence-in-depth.

    ##### §DW17.X.5 — Audit Logging for Blocked Operations

    Every operation blocked by `is_protected` MUST emit a structured audit-log
    entry recording:
    - Actor (who attempted the operation)
    - Target account (the protected account)
    - Attempted operation type
    - Reason: `"protected_account_violation"`
    - Timestamp

    Silent failures (no log, no error) are PROHIBITED.

    ##### §DW17.X.6 — Deterministic Reviewability

    CI and reviewers MUST verify that:
    - All six protected operations (deletion, deactivation, suspension,
      admin password reset, role change, username change) produce explicit
      `protected_account_error` responses when attempted on a protected account
    - Self-service password changes by the account owner succeed
    - Every blocked operation produces an audit-log entry with all required fields
    - No code path bypasses the `is_protected` guard via internal APIs or
      direct DB access

    See: docs/is-protected-spec.md (canonical spec, reference implementation,
    CI tests T1–T9), .specify/memory/checklist-is-protected-compliance.md
    (reviewer checklist Sections A–F).

    <!-- TODO(IS_PROTECTED_SCOPE): RESOLVED — see §DW17.X and §G.12.
         All six protected operations now constitutionally defined and
         enforcement requirements prescribed. Closed in constitution v1.25.0. -->

    <!-- TODO(DIRECT_DB_AUDIT): RESOLVED — see §17.Z below.
         Mandatory CLI wrapper required; manual procedures forbidden;
         fail-closed on audit-log failure; unified audit log required.
         Closed in constitution v1.32.0. -->

    #### §17.Z — Direct Database Modification Audit Requirements

    ##### §17.Z.1 — Purpose

    Direct database modifications affecting protected accounts MUST be
    auditable, deterministic, and reviewer-verifiable. This section defines
    the required mechanism for producing a constitutional audit trail when
    §17 permits removal of always-available accounts by direct database
    modification.

    ##### §17.Z.2 — Mandatory CLI Wrapper

    All direct database modifications to protected accounts MUST be performed
    exclusively through a mandatory CLI tool. This tool MUST:

    - authenticate the operator before any action is taken;
    - capture and record operator identity, UTC timestamp, target account(s),
      operation type, and justification/ticket ID;
    - write a structured audit entry into the unified audit log **before**
      executing the database modification;
    - execute the database modification **only after** the audit entry has
      been successfully persisted;
    - fail closed: if the audit entry cannot be written, the modification
      MUST NOT proceed.

    No other code path (raw SQL, ORM call, migration script, or database
    administration GUI) is permitted as the primary modification mechanism
    for protected accounts.

    ##### §17.Z.3 — Prohibited Mechanisms

    The following MUST NOT be used to satisfy the audit-trail requirement
    for direct database modifications to protected accounts:

    - manually written procedure documents;
    - after-the-fact log entries created by the operator;
    - database administration GUI tools without integrated audit logging;
    - any mechanism that writes the audit entry after the modification.

    ##### §17.Z.4 — Optional DB Triggers

    Database-level triggers MAY be implemented as a supplemental safeguard
    (defence-in-depth). Such triggers MUST NOT replace the mandatory CLI
    wrapper as the primary mechanism. Triggers alone are insufficient because
    they cannot capture operator intent, justification, or ticket ID, and
    cannot enforce pre-modification authorization.

    ##### §17.Z.5 — Unified Audit Log

    Audit entries written by the mandatory CLI wrapper for direct database
    modifications MUST be written to the **same structured audit log** used
    for application-level events. A separate log file, spreadsheet, or
    notes register MUST NOT substitute for the unified audit log. The audit
    entry schema MUST conform to the same field definitions used for
    application audit events (per §16).

    ##### §17.Z.6 — Failure Handling

    If the audit entry cannot be written for any reason (database
    unavailable, schema error, network failure), the CLI tool MUST:

    1. abort the database modification immediately;
    2. exit with a non-zero status code;
    3. print a clear error message to stderr identifying that the
       modification was prevented due to audit-logging failure;
    4. MUST NOT provide a `--force-no-audit` or equivalent bypass flag.

    ##### §17.Z.7 — Deterministic Reviewability

    CI and reviewers MUST verify that:

    - all direct DB modifications to protected accounts can only occur via
      the mandatory CLI wrapper — no other code path writes to protected-
      account records;
    - the CLI writes the audit entry before the DB modification in all
      execution paths;
    - audit-logging failure causes the CLI to exit without modifying the DB;
    - no bypass flag (`--force-no-audit` or equivalent) exists;
    - audit entries conform to the unified audit-log schema;
    - automated tests cover the happy path, audit-failure abort, and schema
      conformance.

    See: docs/direct-db-audit-spec.md (canonical spec, reference
    implementation, CI tests T1–T3),
    .specify/memory/checklist-direct-db-audit-compliance.md
    (reviewer checklist Sections A–F).

18. Break-Glass Emergency Access:

    - The system MUST provision two break-glass accounts (`dev_breakglass`
      and `admin_breakglass`) with `account_status = breakglass` and
      `is_breakglass = true` by default.
    - Enablement MUST require an explicit CLI flag or environment variable;
      break-glass accounts MUST NOT be accessible through normal login flows
      when `account_status = breakglass`.
    - Plaintext and recovery credentials MUST be stored offline (sealed
      envelope, hardware security module, or equivalent) and MUST NOT exist
      in version control, config files, or the database. The Argon2id
      password hash MAY reside in the database solely to enable authentication
      verification; all other credential material MUST remain offline.
    - Successful break-glass login MUST emit an immediate alert to all active
      admin-role and dev-role accounts via two channels: (1) a persistent
      in-app notification delivered to all active admin-role and dev-role
      accounts (queued for recipients not currently logged in; MUST be
      displayed upon their next login), and (2) an out-of-band email
      notification if an email delivery channel is configured. Both channels
      MUST be attempted; failure to deliver one channel MUST be logged but
      does not suppress the other. A high-priority audit entry MUST also be
      created.
    - Post-use password rotation MUST be enforced. The break-glass enablement
      mechanism (CLI flag or environment variable) MUST be automatically
      invalidated at the end of every break-glass session; the account MUST
      NOT be re-enabled for break-glass access until password rotation is
      confirmed complete. Rotation completion MUST be confirmed by an explicit
      action performed by an account with `role = admin` or `role = dev` (via
      UI or CLI); system-only detection of a new password hash in the database
      is NOT sufficient. Every rotation confirmation event MUST generate an
      audit entry recording the actor and the confirmation timestamp. The
      confirmed rotation reactivates the enablement mechanism.
    - Annual drill: break-glass credentials MUST be tested at least once per
      year. The drill MUST be conducted by an account with `role = admin`.
      Documented results MUST be stored in the `/test-evidence/breakglass/`
      repository directory and MUST include at minimum: (i) timestamp of the
      drill, (ii) actor (admin account username), (iii) steps performed,
      (iv) outcome (success or failure), and (v) whether post-use rotation
      was confirmed with a reference to the corresponding audit log entry.
      (Resolves TODO(BREAKGLASS_DRILL_DOCS).)

19. Role Taxonomy & Privilege Escalation:

    - The system enforces four roles: `dev`, `admin`, `user`, `readonly`.
      Account lifecycle state is tracked separately via an `account_status`
      field (`pending` | `active` | `suspended` | `breakglass`) — `pending`
      and `breakglass` are NOT roles.
    - New accounts MUST default to `account_status = pending` (a separate field from
      `role`) until an admin sets `account_status = active`. New accounts have
      `role` set to the sentinel string `"unassigned"` by default; an admin
      MUST explicitly assign a non-sentinel `role` value before setting
      `account_status = active`. **Exception
      (bootstrapped at installation):** The always-available `admin` and `dev`
      accounts are provisioned directly to `account_status = active` during
      installation; this is the sole documented exception to the `pending`
      default (see §VII Always-Available Accounts and §17).
    - Role escalation (e.g., `user` → `admin`) MUST require admin approval and
      emit an audit entry with before/after roles.
    - Role demotion does not require approval but MUST still emit an audit entry with before/after roles.
    - `readonly` accounts MUST be blocked from any destructive file operation
      (delete, move, sync with overwrite, secure wipe) regardless of feature
      flags. For move operations specifically, the block applies to initiating
      any move at all, regardless of source ownership or destination.

20. Directory & Path Security:

    - Directory operations MUST invoke `directory_security_manager` checks:
      permission validation, encryption-at-rest status, and audit logging.
    - Paths presented to external processes MUST be sanitized via
      `path_sanitizer` before use; unsanitized paths from untrusted sources
      constitute a critical security defect.
    - PII scanner results MUST NEVER trigger automatic deletion; they are
      advisory-only pending explicit user action.

21. Theme Security:

    - Theme configuration and custom CSS-equivalent values MUST be validated
      by the theme validator before application; malformed tokens MUST be rejected.
    - Theme access control MUST enforce role-based permissions: only `admin`
      and `dev` roles MAY modify system-wide theme settings; `user`-role
      accounts MAY modify only their own theme preferences; `readonly`
      accounts MUST NOT modify any theme preferences.
    - Theme backups MUST be created before applying any system-wide theme
      change and MUST be stored in a dedicated location separate from the live
      preference store (a separate database table or equivalent file). A theme
      backup is a full snapshot of all current system-wide presets at the
      moment of the change; a per-preset record of only the modified preset is
      NOT sufficient. At least the five most recent full-snapshot backups MUST
      be retained (“five most recent” counts full snapshots, not per-preset
      change records). Admins MUST have access to a built-in restore action
      within the theme UI; a CLI fallback restore path is optional. Recovery
      MUST be possible without data loss.

    #### §21.X — Definition of "System-Wide Theme Change"

    ##### §21.X.1 — Purpose

    The phrase "system-wide theme change" in §21 determines when a backup
    MUST be created. Without a formal definition, implementations may
    erroneously restrict backups to token edits only, leaving preset
    lifecycle operations (create, delete, switch, rename) unprotected.
    This section closes that ambiguity.

    ##### §21.X.2 — Definition

    A **"system-wide theme change"** is any operation that alters the
    effective system-wide theme state. The following five operations are
    all system-wide theme changes and MUST each trigger a backup:

    | Operation | Backup required |
    |---|---|
    | Modify token values in an existing system-wide preset | MUST |
    | Create a new system-wide preset | MUST |
    | Delete an existing system-wide preset | MUST |
    | Switch the active system-wide preset | MUST |
    | Rename a system-wide preset (values unchanged) | MUST |

    Limiting the backup obligation to token-value edits only is explicitly
    forbidden; all five operations change the system-wide theme state.

    ##### §21.X.3 — Backup Requirement

    Before performing any operation listed in §21.X.2, the implementation
    MUST:

    1. Create a full-snapshot theme backup (per the §21 retention and
       storage requirements).
    2. Verify that the backup was successfully persisted.
    3. If backup creation fails, **abort the theme operation**. The change
       MUST NOT be applied when the backup cannot be recorded.

    Backup-after-change ordering is forbidden; backups MUST precede the
    state change.

    ##### §21.X.4 — Backup Content

    The backup captured before any §21.X.2 operation MUST be a **full
    snapshot** of the system-wide theme state at the moment of capture,
    including:

    - all system-wide presets and their complete token sets;
    - the identity of the currently active preset;
    - preset names/labels and unique identifiers.

    Partial snapshots (e.g., only the preset being modified, only token
    values without names/identifiers) MUST NOT satisfy the backup
    requirement.

    ##### §21.X.5 — Deterministic Reviewability

    CI and reviewers MUST verify that:

    - all five operations in §21.X.2 invoke the backup routine before
      executing the state change;
    - backup creation failure causes the theme operation to abort;
    - backups are full snapshots (preset names, identifiers, token sets,
      active preset identity);
    - no theme-state-changing operation bypasses the backup call;
    - automated tests cover all five operations, backup-failure abort
      behaviour, and restore correctness.

    See: docs/theme-backup-trigger-spec.md (canonical spec, reference
    implementation, CI tests T1–T7),
    .specify/memory/checklist-theme-backup-compliance.md
    (reviewer checklist Sections A–E).

22. File Validator Integration:

    - Every tool that reads or transforms external files MUST invoke the
      `file_validator` pipeline before processing. (This requirement is a
      higher-level restatement of the §IX Content-Based Detection rule;
      §IX's per-`open()` validation and this pipeline invocation represent
      the same checkpoint, not two distinct checkpoints.) Bypassing validation
      requires an explicit operator policy exemption with a documented
      justification.
    - Signature databases bundled with releases MUST be integrity-checked at
      startup (hash verification). Corrupted signature databases MUST prevent
      affected tools from launching rather than silently failing. Affected
      tools MUST remain visible in the launcher UI; when a user attempts to
      open an affected tool, the tool MUST present a hard error dialog clearly
      explaining the signature database corruption and the steps required to
      repair it. The repair instructions MUST include at minimum: (i) the
      path or identifier of the corrupted signature database, (ii) the
      required resolution action (e.g., reinitialize, redownload, or replace
      the database), and (iii) the UI path or CLI command to perform the
      repair. Additional detail beyond these minimums is implementation-defined.
    - Heuristic false-positive rates MUST be tracked via telemetry and
      reviewed quarterly. The < 1% false-positive threshold applies at
      both levels: each individual tool's heuristic ruleset MUST stay
      below 1% on its representative test corpus (per-tool gate; the corpus
      is the reference dataset defined in §6 Performance Baselines), AND
      the combined production ruleset across all tools MUST also stay
      below 1% globally (global gate). Breaching either gate MUST
      trigger a patch release.

## Development Workflow & Quality Gates

1. Branching: feature/_, fix/_, chore/_, docs/_ naming. One logical change per
   PR. PR description MUST map changes to affected principles (checklist).
2. TDD Flow: Write failing tests → implement → refactor with green tests.
3. Reviews: Minimum 2 maintainer approvals for: destructive engine changes,
   security-sensitive code, tool discovery system changes, or performance-critical
   paths; otherwise ≥ 1. Any maintainer MAY classify a PR as touching
   security-sensitive code or performance-critical paths, triggering the
   2-maintainer requirement; CI MAY additionally enforce this requirement
   based on a list of designated sensitive paths. PR authors MUST NOT override
   or waive a classification made by any maintainer.
4. Static Analysis: Lint (flake8/black), mypy, security scanning (bandit is
   the required default; a substitute tool is permitted only if it covers all
   bandit checks at minimum, the substitution is documented in CI configuration,
   and the change has a maintainer-approved justification) MUST pass before
   review request.
5. Release Process: Semantic Versioning (SemVer). Automated CI builds assets
   (binaries / PyPI wheel) after tag push. Changelog entry REQUIRED.
6. Documentation Gate: PR adding/changing user-visible behavior (as defined
   in §G.1 — information that appears automatically in the active foreground
   UI) MUST update user guide + API reference before merge.
7. Test Categories: Unit (fast, isolated), Integration (engines, DB, FS), GUI
   smoke (launch, open every tool bundled under the launcher, validate tool
   class imports), Performance (nightly), Security (pattern scans). Critical
   regressions block release.
8. Incident Handling: Production-impacting defect (data loss, security) MUST
   trigger post-mortem within 72h including root cause, principle impacts, and
   remediation tasks.
9. Artifact Retention: Build + test logs retained ≥ 180 days for audit.
10. Contribution Onboarding: New contributor PR triggers automated checklist
    comment with principle summary and required gates.

11. Preference Layer Gates:

    - New/changed preferences MUST include: type, default, validation, and doc.
    - Preference migrations MUST have unit + integration tests and rollback
      guidance.
    - Theming changes MUST pass accessibility checks and visual smoke tests.

12. Authentication Compliance:

    - Features touching identity MUST list Principle VII impacts in PRs.
    - Login UI/CLI changes MUST include manual verification steps + screenshots
      or recordings; these artifacts MUST be stored in the
      `/test-evidence/auth/` directory in the repository. Artifacts MUST be
      clearly annotated; format (screenshot or screen recording) is
      implementation-defined.
    - Automated tests MUST exercise happy path, lockout, reset, MFA (when
      enabled), and audit logging before merge.

13. Preference Portability Gate:

    - Features touching preference export/import MUST validate round-trip
      fidelity (export then import produces identical preference state, as
      defined in §DW13.1 and §G.8) via automated tests.
    - Export artifacts MUST be reviewed for PII and sensitive values before
      the PR is merged; sensitive fields MUST be redacted or encrypted in the
      export format.

    §DW13.1 — Definition of Identical Preference State: "Identical preference
    state" refers exclusively to the semantic preference values. The following
    fields MUST match exactly after an export–import cycle:
    – `preference_category`
    – `preference_key`
    – `preference_value`
    – `value_type`

    §DW13.2 — Excluded Fields: The following system-generated metadata fields
    MUST be excluded from round-trip fidelity comparison:
    – `created_at`, `modified_at`, `imported_at`
    – `record_id`
    – `version`, `migration_flags`
    – Any other implementation-generated metadata not part of the preference value
    These fields are naturally regenerated on import and are not part of the
    user's preference semantics.

    §DW13.3 — Deterministic Reviewability: CI and reviewers MUST verify that:
    – All four semantic fields round-trip identically;
    – No system-generated metadata field is included in the fidelity comparison;
    – Importers do not modify preference values except through explicit,
      documented migration rules.

    §DW13.4 — Ordering and Formatting: Differences in record ordering, JSON
    field ordering, whitespace formatting, or metadata timestamps MUST NOT
    cause a round-trip fidelity failure.

14. Privacy & PII Compliance:

    - Features introducing new data collection or processing MUST include a
      PII impact assessment comment in the PR.
    - PII detector ruleset changes MUST be reviewed by at least one security-
      focused maintainer and include regression tests against a synthetic
      dataset.
    - Privacy cleaner and anonymizer operations MUST be tested for both
      dry-run accuracy and irrecoverability of the destructive path.

15. File Validator Compliance:

    - New file-processing tools MUST demonstrate integration with the
      `file_validator` pipeline in their implementation plan.
    - Policy configuration changes MUST include integration tests that verify
      allow and deny list behavior.
    - Telemetry coverage for new file types MUST be part of the DoD (Definition
      of Done) for any tool that introduces a new file format.

## Clarifications

### Session 2026-04-04 (Round 8 — Q13 Applied)

- Q: §VII Session Controls states tokens MUST be "cleared on crash recovery".
  TODO(CRASH_RECOVERY_SESSION) has been open since v1.11.0. Does clearing
  occur in the crash handler or on next startup? Must the application detect
  a prior crash state? Must the application purge OS-persisted memory?
  Should TODO(CRASH_RECOVERY_SESSION) be resolved in this round?
  → A: Yes to all. TODO(CRASH_RECOVERY_SESSION) is now CLOSED.
  **Startup-time clearing is mandatory; crash handler clearing is best-effort
  only.** The process cannot rely on in-process handlers because SIGKILL,
  OOM kill, power loss, and container eviction cannot be caught.
  **§G.13 — Crash sentinel**: new normative glossary entry defining the
  dirty/clean state indicator; lifecycle rules; required properties (process-
  external, earliest-startup readable, deterministically testable).
  **§VII.W.1 — Purpose**: session secrets are volatile-only; MUST NOT survive
  process termination, crash, or restart.
  **§VII.W.2 — Crash Handler Clearing**: MAY be attempted for recoverable
  signals; MUST NOT be relied upon for correctness.
  **§VII.W.3 — Startup-Time Clearing**: mandatory 4-step sequence (read
  sentinel, set dirty, if not clean then purge all secrets + refuse any session
  restore, then continue). MUST execute before any session/preference logic.
  **§VII.W.4 — Crash Sentinel**: process-external; dirty on startup; clean
  only on graceful shutdown; missing treated as dirty.
  **§VII.W.5 — OS-Level Persistence Protections**: swap (mlock/VirtualLock),
  crash dumps (disabled or non-dumpable), core files (disabled/restricted),
  hibernation images (treated as crash dumps). Undocumented omissions
  prohibited.
  **§VII.W.6 — Deterministic Reviewability**: CI MUST verify sentinel logic,
  unconditional startup clearing after unclean shutdown, no session restore
  after simulated crash, OS persistence exclusions, test coverage.
  Created: docs/crash-recovery-spec.md (canonical spec, reference
  implementation, CI tests T1–T9, migration Steps 1–5);
  .specify/memory/checklist-crash-recovery-compliance.md (reviewer checklist
  Sections A–E).
  Also fixed: duplicate §G.12 glossary entry removed.

### Session 2026-04-04 (Round 8 — Q12 Applied)

- Q: §17 defines `is_protected` as blocking deletion and deactivation; Round 8
  extended it to also block suspension. TODO(IS_PROTECTED_SCOPE) (open since
  v1.11.0) deferred three additional attack vectors: (1) password reset by
  another admin, (2) role demotion/escalation, (3) username change. Does
  `is_protected` block all three? Should TODO(IS_PROTECTED_SCOPE) be closed?
  → A: Yes to all. TODO(IS_PROTECTED_SCOPE) is now CLOSED.
  **§G.12 — is_protected scope**: new normative glossary entry defining the
  six protected operations (deletion, deactivation, suspension, admin password
  reset, role change, username change); self-service password change remains
  permitted; every blocked operation MUST produce a `protected_account_error`
  and an audit-log entry with actor/target/operation/reason/timestamp.
  **§DW17.X.1 — Purpose**: is_protected designates permanently available,
  permanently privileged, administratively immutable accounts.
  **§DW17.X.2 — Password Reset Protection**: self-service permitted; all
  other admin/API-initiated resets MUST fail with `protected_account_error`.
  **§DW17.X.3 — Role Change Protection**: escalation and demotion both
  forbidden; role immutable after creation; all layers (UI/API/DB) MUST block.
  **§DW17.X.4 — Username Protection**: username immutable at all layers; DB
  constraints recommended as defence-in-depth.
  **§DW17.X.5 — Audit Logging for Blocked Operations**: all five fields
  required (actor, target, operation, reason, timestamp); silent failures
  PROHIBITED.
  **§DW17.X.6 — Deterministic Reviewability**: CI MUST verify all six blocked
  operations, self-service pass, audit log completeness, no bypass paths.
  §VII Always-Available Accounts and §VII Account Suspension updated to
  reference §G.12 and §DW17.X and list all six blocked operations.
  Created documents: docs/is-protected-spec.md (canonical spec, reference
  implementation, CI tests T1–T9, migration Steps 1–6);
  .specify/memory/checklist-is-protected-compliance.md (reviewer checklist
  Sections A–F).

### Session 2026-04-04 (Round 8 — Q11 Applied)

- Q: §VII Session Controls states the out-of-box default idle timeout is
  30 minutes, applying uniformly to all roles. Should the constitution define
  role-differentiated defaults (shorter for privileged roles, longer for
  low-risk roles) rather than a single uniform value?
  → A: Yes. The uniform 30-minute default is constitutionally superseded.
  **§G.11 — Role-differentiated idle timeout defaults**: new normative glossary
  definition prescribing per-role out-of-box values (admin 10 min, dev 15 min,
  user 30 min, readonly 45 min); 60-minute ceiling; override logging rule.
  **§VII.Z.1 — Purpose**: idle-timeout defaults MUST reflect privilege level;
  a uniform default MUST NOT be applied across all roles.
  **§VII.Z.2 — Role-Differentiated Default Idle Timeouts**: per-role table
  matching §G.11; single global constant MUST NOT be used; privileged roles
  MUST have shorter or equal defaults than non-privileged roles.
  **§VII.Z.3 — Maximum Timeout Ceiling**: 60-minute ceiling without explicit
  admin override; override requires deliberate action and audit-log entry;
  8-hour absolute ceiling unchanged.
  **§VII.Z.4 — Administrative Overrides**: admins MAY configure per-role
  values subject to §VII.Z.3; all overrides MUST be logged (actor, role,
  previous value, new value, timestamp).
  **§VII.Z.5 — Deterministic Reviewability**: CI MUST verify role-
  differentiated defaults, privilege ordering, no global constant, override
  logging, test coverage.
  §VII Session Controls text updated: "30 min" uniform default sentence
  replaced with role-differentiated language referencing §G.11 and §VII.Z.
  Created documents: docs/idle-timeout-spec.md (canonical spec, default table,
  Python reference implementation, CI tests T1–T6, migration Steps 1–6,
  session lifecycle diagram);
  .specify/memory/checklist-idle-timeout-compliance.md (reviewer checklist
  Sections A–E).

### Session 2026-04-04 (Round 8 — Q10 Applied)

- Q: §VII names "FIDO2 hardware token" as an offline-capable MFA method but
  does not distinguish FIDO2 roaming authenticators (detachable hardware keys,
  e.g., YubiKey) from FIDO2 platform authenticators (device-bound, e.g.,
  Windows Hello, Touch ID). Platform authenticators break portability and
  recoverability if the device is lost. Should the constitution restrict
  "FIDO2 hardware token" to roaming authenticators only, adopt precise FIDO2
  terminology, and require pairing when a platform authenticator is enrolled?
  → A: Yes to all. **§G.10 — FIDO2 authenticator classes**: new normative
  glossary entry defining "FIDO2 roaming authenticator" (detachable, cross-
  device; satisfies offline-capable MFA enrollment requirement) and "FIDO2
  platform authenticator" (device-bound; does NOT satisfy the requirement
  alone; pairing rule with roaming key or TOTP prescribed).
  **§VII.Y.1 — Definitions**: "FIDO2 hardware token" alias explicitly resolved
  to "FIDO2 roaming authenticator"; both classes defined with §G.10 reference.
  **§VII.Y.2 — Offline-Capable MFA Requirement**: only FIDO2 roaming
  authenticators and TOTP (§VII.X / §G.9) count toward the enrollment
  requirement; platform authenticators MUST NOT satisfy it alone.
  **§VII.Y.3 — Platform Authenticator Pairing**: if only a platform
  authenticator is enrolled, the user MUST also have a roaming key or TOTP;
  sole-platform-only accounts MUST NOT be allowed.
  **§VII.Y.4 — Recovery and Portability**: recovery path via roaming/TOTP MUST
  exist; platform credentials MUST NOT be exported as portable artifacts.
  **§VII.Y.5 — Enrollment and UI Clarity**: roaming MUST be labelled "Security
  Key"; platform MUST be labelled "This Device"; "hardware token" label for
  platform MUST NOT be used.
  **§VII.Y.6 — Deterministic Reviewability**: CI MUST verify classification,
  enrollment rules, pairing enforcement, recovery paths, and no portable
  platform export.
  §VII MFA narrative updated: "FIDO2 hardware token" → "FIDO2 roaming
  authenticator (§G.10)" in all normative body text; platform authenticator
  caveat added.
  Created documents: docs/fido2-spec.md (canonical spec, WebAuthn pseudocode,
  CI tests T1–T7, migration Steps 1–7, enrollment diagram);
  .specify/memory/checklist-fido2-compliance.md (reviewer checklist
  Sections A–G).

### Session 2026-04-04 (Round 8 — Q9 Applied)

- Q: §VII accepts TOTP as an offline-capable MFA method but does not specify
  the TOTP configuration. RFC 6238 (TOTP) and RFC 4226 (HOTP) both exist;
  within TOTP, multiple configurations are possible (algorithm, digit length,
  time step). Without a prescribed default, two implementations may be
  mutually incompatible. Should the constitution prescribe RFC 6238 TOTP as
  the governing standard, mandate a default interoperability profile, exclude
  HOTP as a primary method, and exclude backup codes from enrollment counting?
  → A: Yes to all four. **§G.9 — TOTP default profile**: new normative
  glossary definition prescribing HMAC-SHA1 / 6 digits / 30-second time step /
  ±1 step drift tolerance, with normative provisioning URI form; HOTP
  explicitly excluded.
  **§VII.X.1 — Mandatory Standard**: RFC 6238 TOTP MUST be used. HOTP MUST
  NOT count as an enrolled MFA method.
  **§VII.X.2 — Default TOTP Profile**: §G.9 default profile MUST be accepted
  by all implementations; stronger profiles MAY be added but MUST NOT replace
  the default.
  **§VII.X.3 — Enrollment Requirements**: TOTP secret MUST be compatible with
  §G.9; provisioning URI/QR MUST encode default profile; secret MUST be
  encrypted at rest.
  **§VII.X.4 — Verification Requirements**: drift tolerance ±1 step; unsupported
  configs MUST be rejected unless explicitly enabled as secondary profiles.
  **§VII.X.5 — Backup and Recovery Codes**: MAY exist as emergency fallback;
  MUST NOT count as an enrolled MFA method.
  **§VII.X.6 — Export and Import**: TOTP secret preserved; importers MUST NOT
  alter secret or profile; default profile interoperability maintained after
  import.
  **§VII.X.7 — Deterministic Reviewability**: CI MUST verify RFC 6238
  compliance, default profile support, no HOTP enrollment, no backup-code-as-
  MFA, correct drift tolerance, test coverage.
  §VII MFA narrative updated to reference §G.9 and §VII.X.
  Created documents: docs/totp-spec.md (canonical spec, reference
  implementation, CI tests T1–T5, migration Steps 1–8, diagrams);
  .specify/memory/checklist-totp-compliance.md (reviewer checklist
  Sections A–G).

### Session 2026-04-04 (Round 8 — Q8 Applied)

- Q: §DW §13 requires "export then import produces identical preference
  state." System-generated fields (created_at, modified_at, record_id, etc.)
  will always differ after an import cycle. Does "identical" mean semantic
  values only, or full byte-for-byte record equality?
  → A: Semantic values only — the comparison is now constitutionally scoped.
  **§G.8 — Round-trip fidelity**: new normative glossary definition.
  Fidelity is over four semantic fields: preference_category, preference_key,
  preference_value, value_type. All metadata excluded.
  **§DW13.1 — Definition of Identical Preference State**: four included
  fields (category, key, value, value_type) MUST match exactly.
  **§DW13.2 — Excluded Fields**: created_at, modified_at, imported_at,
  record_id, version, migration_flags, and all implementation metadata MUST
  NOT be compared.
  **§DW13.3 — Deterministic Reviewability**: CI compares semantic fields
  only; must not compare metadata; must reject silent value coercion.
  **§DW13.4 — Ordering and Formatting**: record order, JSON formatting, and
  timestamp differences MUST NOT cause a fidelity failure.
  §DW §13 body text updated: "identical preference state" now references
  §DW13.1 and §G.8 explicitly.
  Created documents: docs/round-trip-fidelity-spec.md (canonical field
  constants, CI test suite T1–T5, migration patch Steps 1–5, diagram);
  .specify/memory/checklist-round-trip-fidelity.md (reviewer checklist
  Sections A–F).

### Session 2026-04-04 (Round 8 — Q7 Applied)

- Q: §VI requires that export artifacts encrypt sensitive preference values but
  does not prescribe an algorithm, KDF, or envelope format. Should the
  constitution prescribe a minimum algorithm? Should the KDF be specified?
  Must algorithm and parameters appear in the export metadata? Must the key
  be passphrase-derived?
  → A: Yes to all four — the constitution now prescribes:
  **§G.7 — Export encryption envelope**: new normative glossary definition.
  The envelope is the portable, versioned, plaintext-header JSON structure
  wrapping AES-256-GCM ciphertext. Reference shape defined in §G.7.
  **§VI.4 — Export Encryption Requirements**: new seven-subsection group.
  §VI.4.1: AES-256-GCM MUST be used; weaker algorithms or non-AEAD modes
  MUST NOT be used.
  §VI.4.2: Key MUST be derived via Argon2id; parameter floors: memory ≥
  64 MB, iterations ≥ 3, parallelism ≥ 1, salt ≥ 16 bytes.
  §VI.4.3: Export MUST include plaintext header: algorithm, KDF name, KDF
  params, salt, nonce, auth tag, version.
  §VI.4.4: GCM auth tag MUST be verified before accepting decrypted data;
  partial decryption MUST NOT be accepted.
  §VI.4.5: Key MUST be passphrase-derived; application-managed keys MUST
  NOT be used.
  §VI.4.6: All implementations MUST interoperate (read any conforming
  export).
  §VI.4.7: CI MUST verify algorithm, KDF parameter floors, metadata
  completeness, and no plaintext leakage.
  §VI Portability body text updated: encryption sentence now references
  §VI.4 explicitly (AES-256-GCM + Argon2id).
  TODO(PORTABILITY_FORMAT): partially addressed — encryption envelope is
  now prescribed; full schema publication remains pending (portability.py
  stability prerequisite unchanged).
  Created documents: docs/export-encryption-spec.md (full spec, reference
  implementation, CI test spec, migration plan);
  .specify/memory/checklist-export-encryption-compliance.md (reviewer
  checklist Sections A–F).

### Session 2026-04-04 (Round 8 — Q6 Applied)

- Q: TODO(GUARDIAN_POLL_INTERVAL) defers the runtime health-check polling
  interval entirely to implementation documentation. Should the constitution
  set minimum and maximum bounds? Should this TODO be resolved now?
  → A: Yes — both bounds are now normative. TODO(GUARDIAN_POLL_INTERVAL)
  is formally closed.
  **§V.6 — Health-Check Polling Interval**: new five-subsection block.
  §V.6.1 Minimum Polling Frequency: `health_check()` MUST be invoked at
  least once every 5 seconds during active use.
  §V.6.2 Maximum Polling Frequency: `health_check()` MUST NOT be invoked
  more frequently than once every 500 milliseconds.
  §V.6.3 Implementation Flexibility: fixed intervals, jitter, backoff, or
  adaptive strategies all permitted provided the effective interval stays
  within [500 ms–5 s] at all times.
  §V.6.4 Deterministic Reviewability: both bounds MUST be unit-tested
  (mock timers / virtual clocks) and CI-enforced.
  §V.6.5 Resolution of TODO(GUARDIAN_POLL_INTERVAL): formally closed;
  open since v1.8.0. No implementation-defined intervals outside [500 ms–5 s]
  are permitted.
  §V body text updated: stale "Q6 / TODO(GUARDIAN_POLL_INTERVAL)" reference
  replaced with normative §V.6 reference and inline bound summary.
  Updated documents: docs/component-guardian-spec.md (Section 3.2 polling
  bounds filled; Section 10 polling reference implementation added);
  checklist-component-guardian-recovery.md (Section H added).

### Session 2026-04-04 (Round 8 — Q5 Applied)

- Q: §V defines when a component enters degraded state but provides no
  mechanism for a component to recover from degraded state at runtime. Can
  components recover? What triggers recovery? Must recovery be logged?
  → A: Yes — components MUST be allowed to recover at runtime.
  **§V.1 — Recovery Eligibility**: component MAY recover from degraded state
  while the application is running; degraded is not permanent without restart.
  **§V.2 — Recovery Trigger**: recovery MUST occur automatically when
  `health_check()` returns True; no developer action, user action, or external
  trigger may substitute; no "force healthy" path without a passing
  `health_check()`. State machine: HEALTHY ↔ DEGRADED driven solely by
  `health_check()` return value.
  **§V.3 — Recovery Behavior**: on recovery, component MUST resume normal
  operation, clear all degraded indicators, and re-enter polling cycle. No
  sticky degraded logic permitted after successful recovery.
  **§V.4 — Recovery Logging**: every state transition (degradation AND
  recovery) MUST generate a structured log entry with: timestamp,
  component_id, from_state, to_state, reason. Raw stack traces alone are
  insufficient.
  **§V.5 — Deterministic Reviewability**: each transition MUST be unit-tested
  and log-observable; CI MUST fail if a transition occurs without required
  log fields.
  Note: TODO(GUARDIAN_POLL_INTERVAL) is not resolved by Q5 — it is addressed
  by Q6. §V body text updated to reference §V.2 and Q6 for polling bounds.
  New supporting documents: checklist-component-guardian-recovery.md,
  docs/component-guardian-spec.md (state machine, CI test spec, migration
  patch).

### Session 2026-04-04 (Round 8 — Q4 Applied)

- Q: Is the parenthetical list “(duplicate detection, secure delete, batch
  processors)” in §III exhaustive, or illustrative of a broader category?
  Who has authority to classify a new module as a critical engine?
  → A: The list is explicitly illustrative, not exhaustive. The constitution
  now defines critical engine by criteria.
  **§G.6 — Critical engine**: a module meeting one or more of five criteria:
  (a) irreversible or destructive operations; (b) large-scale or batch
  operations on multiple user assets; (c) high-impact data transformations
  where correctness is essential (dedup, compression, OCR, PDF, checksum);
  (d) untrusted external input (network sync, remote fetch, archive
  extraction); (e) security-sensitive operations (encryption, secure delete,
  auth, token validation, sandbox). Examples include but are not limited to:
  duplicate detection, secure delete, batch processors, compression, PDF
  processors, network sync, archive extractors, OCR engines.
  **§III updated**: parenthetical list replaced with §G.6 cross-reference;
  prior examples retained as illustrative-only note.
  **§III.1 — Classification Authority**: new subsection. Any maintainer MAY
  classify during PR review if criteria met. PR authors MAY self-declare.
  Maintainers hold final authority and MAY override with documented PR note.
  Classification MUST be recorded in module metadata/README
  (`critical_engine: true`). CI MUST enforce §III test requirement for all
  declared critical engines. Registry maintained in `docs/critical-engines.md`.
  Cross-references: §G.6 references §G.4 (destructive operation); §III
  references §G.6; §III.1 references §G.6 and §III.
  New supporting documents: checklist-critical-engine-classification.md,
  docs/critical-engines.md.

### Session 2026-04-03 (Round 8 — Q3 Applied)

- Q: §II permits a cryptographically signed HMAC token as the headless-mode
  alternative to interactive confirmation for destructive operations, but five
  critical attributes of that token are unspecified: algorithm, key material
  storage, validity period, single-use vs multi-use, and audit trail. Are
  these constitutionally prescribed?
  → A: Yes. All five attributes are now normative.
  **§G.5 — Headless HMAC token**: a cryptographically signed single-use token
  that is the headless-mode alternative to interactive confirmation for
  destructive operations (§G.4). Five mandatory attributes: HMAC-SHA256 or
  stronger; signing key in secure keystore (MUST NOT be plaintext config, env
  variable, or source code in production); ≤ 5-minute validity (embedded
  timestamp required); single-use (one destructive op per token, invalidated
  after redemption); both issuance and redemption MUST generate audit log
  entries with non-sensitive token identifier, caller identity, operation
  name, timestamp, and success/failure status.
  **§II.5 — Headless HMAC Token Requirements**: new six-subsection block
  (§II.5.1 Algorithm; §II.5.2 Key Storage; §II.5.3 Token Structure and
  Validity; §II.5.4 Single-Use Requirement; §II.5.5 Audit Logging;
  §II.5.6 Equivalence to Interactive Confirmation). Audit entries in §II.5.5
  are subject to the §16 ≥ 365-day retention requirement.
  **Distinction from §15**: The §15 credential reset token (1-hour validity,
  out-of-band delivery, account recovery) is explicitly distinct from the §G.5
  headless HMAC token (5-minute validity, destructive-operation authorization).
  §15 updated with inline distinction note.
  Cross-references: §II opening paragraph now references §G.5 and §II.5;
  §II.2 closing parenthetical updated to reference §II.5; §16 updated to
  include HMAC token events as additional auditable events.
  New checklist: checklist-hmac-token-compliance.md.

### Session 2026-04-03 (Round 8 — Q2 Applied)

- Q: The term "side effect" in §II is not formally defined, making dry-run
  coverage unenforceable. Which operations trigger dry-run, and which
  additionally require confirmation? Should a two-tier classification taxonomy
  be adopted?
  → A: Yes. A new two-tier taxonomy has been adopted.
  **§G.3 — Side effect**: any persistent change to user-visible state,
  including file mutations, metadata writes, network writes, or external system
  changes. Internal RFU bookkeeping (indexes, caches, audit logs) is NOT a side
  effect. All side-effect operations require dry-run.
  **§G.4 — Destructive operation**: a side-effect operation that is
  irreversible or hard to reverse (delete, overwrite, secure wipe,
  anonymization, lossy transformation). All destructive operations require
  dry-run PLUS explicit user-visible confirmation.
  **§II restructured** into four subsections: §II.1 Dry-run Requirement
  (side-effect ops per §G.3); §II.2 Confirmation Requirement (destructive ops
  per §G.4); §II.3 Internal Operations Excluded (bookkeeping is NOT a
  side-effect); §II.4 CI Enforcement. First paragraph updated to reference §G.4.
  **§VI Portability updated**: skipped-item summary labeled §VI.1; §VI.2
  Dry-run Integration added (side-effect dry-run MUST include §VI.1 summary,
  separately from changes); §VI.3 Deterministic Reviewability added.
  Cross-references: §II.1 and §II.2 now reference §G.3/§G.4; §VI.2 references
  §G.3 and §II.1. New checklist: checklist-side-effect-dry-run-compliance.md.

### Session 2026-04-03 (Round 8 — Q1 Applied)

- Q: The terms "user-visible" and "user-discoverable" appear across §VI, §15,
  and DW §6 without formal definitions. Does "user-visible" require appearance
  in the active foreground UI, and should both terms be added to a Glossary?
  → A: Yes. A new §G Normative Glossary has been added.
  **§G.1 — User-visible**: information that appears automatically in the
  active foreground UI without requiring navigation, expansion, or interaction.
  Status bars, notification badges, collapsible panels, log panels, and
  sidebars do NOT satisfy this requirement. CI MUST verify user-visible
  elements via widget-tree or DOM inspection of the active foreground viewport.
  User-visible warnings MUST NOT be suppressible by default.
  **§G.2 — User-discoverable**: information reachable within one navigation
  step from the active UI state, without consulting external documentation or
  requiring knowledge of hidden features. Multi-level menus, logs, developer
  consoles, and config files do NOT satisfy this requirement.
  Both terms are retained (not collapsed) because they serve distinct
  governance purposes: user-visible governs mandatory warnings and blocking
  conditions (MUST); user-discoverable governs optional diagnostics and
  supplementary information (SHOULD / MAY).
  Cross-references added: §VI Portability skipped-item summary now references
  §G.1; §15 Credential Reset offline warning now references §G.1; DW §6
  Documentation Gate now references §G.1. §G Normative Glossary added. §VI
  Portability, §15, and Development Workflow §6 updated.

### Session 2026-03-31 (Round 8)

- Q: Who may approve an OS-infeasible feature flag designation? → A: Only maintainers (distinct from PR author). Written justification MUST appear in PR; capabilities matrix MUST be updated. §I updated.
- Q: What is the testable definition of "user-discoverable" for dry-run? → A: Dry-run MUST be a visible UI element before any action begins; documentation-only is insufficient. Dry-run surface check added to §5 coverage gates. §II and §5 updated.
- Q: Is conflict detection performed against live DB value or schema default? → A: Live DB value only. A key absent from the DB is NOT a conflict — it is a new key. §VI Portability updated.
- Q: Is "equivalent" in export format constrained to human-readable text? → A: Yes. Permitted formats: JSON, YAML, TOML, or equivalent structured text. Binary and proprietary formats prohibited. Exports must be portable. §VI Portability updated.
- Q: Can admins set a minimum idle timeout in addition to a maximum cap? → A: Yes. Admins MAY set both a minimum floor and a maximum cap; users MUST stay within the admin-defined range. §VII Session Controls updated.
- Q: Can devs suspend admins? Can is_protected accounts be suspended? → A: Devs MUST NOT suspend admins. is_protected accounts MUST NOT be suspended under any circumstances. §VII Account Suspension updated.
- Q: Is MFA-before-activation system-enforced or procedural only? → A: System-enforced. System MUST reject activation without enrolled offline-capable MFA. §VII MFA updated.
- Q: Who conducts the annual break-glass drill, and what is "documented results"? → A: Admin-role accounts only. Results MUST be stored in /test-evidence/breakglass/ with 5 minimum fields. TODO(BREAKGLASS_DRILL_DOCS) resolved. §18 updated.
- Q: How is break-glass rotation completion confirmed — system-detected hash or explicit action? → A: Explicit admin/dev action only; hash detection is NOT sufficient. Audit entry mandatory. §18 updated.
- Q: Is there a system default PII scan scope, and can admins configure one? → A: Yes to both. System default MUST exist. Admins MAY set deployment-wide default; users MAY override unless admin marks it mandatory. §VIII updated.
- Q: Must the anonymization mode display appear before the confirmation dialog, or can it appear within it? → A: Displaying mode within the confirmation dialog is constitutionally sufficient; separate prior step not required. §VIII updated.
- Q: Must file validation run on every open() call, or once per file per operation? → A: Once per file per operation. Cached result permitted if file metadata unchanged. §IX updated.
- Q: What does "segments" mean in §6, and should it align with §IV wording? → A: "Segments" = each continuous blocked period. §6 updated to "MUST NOT reach or exceed 100ms for any continuous blocked period," superseding prior wording. §6 updated.
- Q: Are the 44 × 44 px touch targets logical or physical pixels? → A: Logical (device-independent) pixels, per WCAG 2.1 SC 2.5.8. §7 updated.
- Q: Can a regular account transition to `account_status = breakglass`? → A: No. Regular accounts MUST NEVER transition to breakglass. §14 parenthetical corrected. §14 updated.
- Q: What is the breached-password denylist source? → A: Implementation-defined with three mandatory constraints: offline local denylist required; k-anonymity if external API used; full passwords/hashes MUST NEVER be transmitted externally. §15 updated.
- Q: Is "a backup" a full snapshot or per-preset record? → A: Full snapshot of all system-wide presets. "Five most recent" = five most recent full snapshots. §21 updated.
- Q: What minimum content must repair instructions include? → A: Path/identifier of corrupted DB, required resolution action, UI path or CLI command. §22 updated.
- Q: Who may classify a PR as security-sensitive or performance-critical? → A: Any maintainer. CI MAY enforce path-based triggers. PR authors cannot override or waive the classification. §DW §3 updated.

### Session 2026-03-31 (Round 7)

- Q: In §II, how should dry-run simulation be exposed in the GUI? → A: Implementation-defined per tool. Each tool performing side-effect operations MUST expose the dry-run capability in a user-discoverable way before the operation is committed; the specific UI pattern is not prescribed. §II updated.
- Q: Does the §VIII two-step confirmation (typed phrase + button click) apply to all destructive operations in §II? → A: No. §II destructive operations require a single explicit confirmation step only. The §VIII two-step confirmation applies exclusively to irreversible anonymization operations. §II clarified.
- Q: Which boundary governs for 100ms UI thread blocking — §IV's `> 100ms` (100ms allowed) or §6's `< 100ms` (100ms a gate failure)? → A: §6 is the governing enforcement gate; 100ms is a gate failure. §IV updated to "MUST NOT reach or exceed 100ms", consistent with §6.
- Q: Who can create, edit, and delete theme named presets? → A: Two scopes: personal presets (created/edited/renamed/deleted by the owning account; `user`-role and above) and system-wide presets (created/managed by `admin`/`dev` only; read-only templates for all other roles; `user` accounts MUST NOT delete or modify system-wide presets but MAY create personal derivatives). §VI theming updated.
- Q: Which roles may export and import preferences? → A: Export: all roles including `readonly`. Import: `user`, `admin`, `dev` only; `readonly` accounts MUST NOT import. §VI Portability updated.
- Q: When schema migration is not feasible for an imported preference set, what happens? → A: Skip incompatible keys, import all compatible keys, and present a user-visible summary of skipped items with the reason each was skipped. §VI Portability updated.
- Q: Should the system warn the user before forced idle logout? → A: Yes. The system MUST warn the user at least 60 seconds before session expiry due to idle timeout, giving the user the opportunity to extend the session. Exact UI pattern is implementation-defined. §VII Session Controls updated.
- Q: Should break-glass login alerts reach admin-role only, or both admin-role and dev-role accounts? → A: Both admin-role and dev-role (aligning with §16 anomaly detection scope). §VII Break-Glass and §18 updated.
- Q: When an active+blocked account is suspended, should `is_blocked` and `login_attempts` be preserved or reset? → A: Reset atomically when the account transitions out of `active`; account returns in a clean, unblocked state when restored to `active`. §14 updated.
- Q: In §VIII anonymization, should the mode-selection UI pattern be prescribed or implementation-defined? → A: Implementation-defined, provided: (i) no mode is pre-selected, (ii) user makes an explicit choice before tool activates, and (iii) selected mode is clearly displayed before execution begins. §VIII updated.
- Q: Is the irreversible anonymization confirmation phrase fixed ("CONFIRM") or flexible? → A: Implementation-defined per tool, provided the phrase is explicitly shown to the user before the typing step and must be typed exactly as displayed. §VIII updated.
- Q: How should a clear rejection reason for a denied file type be surfaced? → A: UI pattern is implementation-defined, provided the reason is explicit, visible, and identifies the specific policy rule that triggered the denial. §IX updated.
- Q: Should approval of an unrecognized file type use the §VIII two-step ritual? → A: No. A one-step confirmation dialog only; no typed phrase or persistent session toggle is required. §IX updated.
- Q: What does "key actions reachable via keyboard" mean — every action, destructive actions, or a per-tool list? → A: Per-tool list. Each tool MUST define its key actions in its implementation documentation; the constitution sets the obligation. §7 updated.
- Q: Should the constitution add minimum accessibility requirements for tab order, screen reader labels, reduced-motion, and touch targets? → A: Yes. Four constitutional minimums added to §7: logical tab/focus order; accessible labels for interactive controls; reduced-motion support; ≥ 44 × 44 px touch/pointer target size. §7 updated.
- Q: In §18, what mechanism enforces the break-glass post-use rotation block? → A: The enablement mechanism (CLI flag or environment variable) MUST be automatically invalidated at session end; re-enablement blocked until rotation confirmed complete. §18 updated.
- Q: Where are theme backups stored, how many retained, and how does admin restore? → A: Separate storage from live preference store; last 5 backups minimum; built-in UI restore action required (CLI optional). §21 updated.
- Q: When a tool is blocked by a corrupted signature database, degraded state or hard error? → A: Tool remains visible in launcher; opening it triggers a hard error dialog with repair instructions (NOT ComponentGuardian degraded state). §22 updated.
- Q: Where should authentication verification artifacts (screenshots/recordings) be stored? → A: In `/test-evidence/auth/` directory in the repository; must be clearly annotated; format implementation-defined. §DW §12 updated.
- Q: Is the current Clarifications section ordering correct? → A: No. Clarifications MUST be ordered reverse-chronologically (newest first). Clarifications section reordered. §DW updated.

### Session 2026-03-12 (Round 6)

- Q: In §VII Admin Resets & Unblock, the requirement to pass an MFA challenge presupposes MFA is enabled for the acting admin. Does the deployment-level MFA toggle affect this? → A: No. ALL accounts with `role = admin` or `role = dev` MUST always have MFA enforced regardless of the deployment-level toggle; the toggle only affects `user` and `readonly` role accounts. §VII MFA Deployment level updated to extend the always-on MFA rule to all admin-role and dev-role accounts.
- Q: In §15, the reset flow lists two alternatives (admin MFA challenge vs HMAC token) with no stated priority. Is one preferred? → A: Neither method is preferred; either method is equally acceptable. No priority ordering added. Q&A record only.
- Q: What is the lifecycle of the `suspended` account status? → A: Only accounts with `role = admin` or `role = dev` may set or unset `suspended`. Both events require an audit entry recording actor, target, and before/after status. §VII Account Suspension subsection added.
- Q: In §VII Lockout, the "automated unlock workflow" is referenced but not defined. → A: Deferred. TODO(AUTO_UNLOCK_WORKFLOW) added.
- Q: In §VII / §18, what constitutes "documented results" for the annual break-glass credentials drill? → A: Deferred. TODO(BREAKGLASS_DRILL_DOCS) added.
- Q: In §VII Session Controls, what does "crash recovery" clearing mean precisely? → A: Deferred. TODO(CRASH_RECOVERY_SESSION) added.
- Q: In §17, does `is_protected` prevent operations beyond deletion and deactivation (e.g., password resets, role changes)? → A: Deferred. TODO(IS_PROTECTED_SCOPE) added.
- Q: In §VI Portability, are sensitive preference export values omitted or encrypted? → A: Encrypted; omission is not permitted. Sensitive keys MUST appear in the export in encrypted form. §VI Portability updated.
- Q: In §19, does the `readonly` move block cover initiating any move, or only moves where the account owns the source? → A: Blocked from initiating any move at all, regardless of source ownership or destination. §19 clarification added inline.
- Q: In §VII Lockout / §16, what fields form "origin metadata" in login-attempt audit entries? → A: Deferred in v1.11.0. ✓ RESOLVED in v1.27.0 — see §16.X and docs/audit-origin-metadata-spec.md. Minimum fields (all events): actor_username, session_id, device_id (pseudonymized), app_instance_id. Network-event additional fields: client_ip_hash (pseudonymized), user_agent, protocol. TODO(AUDIT_ORIGIN_METADATA) CLOSED.
- Q: In §7 and §VI theming, what specific contrast ratios does WCAG AA require? → A: Standard text: ≥ 4.5:1; large text (≥ 18 px regular weight or ≥ 14 px bold weight): ≥ 3:1; non-text UI components (icons, borders, interactive controls): ≥ 3:1. §7 Accessibility and §VI theming updated with explicit ratios.
- Q: In §1, what does "planned before EOL − 90 days" require as a deliverable? → A: Deferred. TODO(EOL_PLANNING_DELIVERABLE) added.
- Q: In §1, what is the minimum deliverable that satisfies "MUST be planned before upstream EOL minus 90 days"? → A: A milestone-bound, assigned migration issue in the authoritative issue tracker, created ≥90 days before upstream EOL. The issue MUST include: component + version, EOL date, migration target, assigned owner, milestone with due date, and actionable description. Mental notes, informal discussions, and un-milestoned issues MUST NOT satisfy the requirement. CI MUST enforce via an `eol.yaml` config file and fail if any compliant issue is absent. Responsible party: Maintainer / Release Steward. TODO(EOL_PLANNING_DELIVERABLE) RESOLVED in v1.33.0. See §1.X and docs/eol-planning-deliverable-spec.md.

### Session 2026-03-12 (Round 5)

- Q: In §VII Lockout, are break-glass accounts subject to the lockout mechanism? → A: No. Break-glass accounts are NOT subject to the lockout mechanism; they authenticate only via the explicit CLI flag or environment variable and do not participate in the normal login flow on which the lockout counter operates. Always-available accounts remain subject to lockout rules. §VII Lockout updated.
- Q: In §VII and §18 break-glass credential storage, does "not in the database" prohibit the Argon2id hash or only plaintext/recovery credentials? → A: Only plaintext and recovery credentials. The Argon2id password hash MAY reside in the database to enable authentication verification; all other credential material MUST remain offline. §VII Break-Glass and §18 updated.
- Q: Can the deployment-level MFA toggle disable MFA for always-available `admin` and `dev` accounts? → A: No. The deployment-level toggle MUST NOT disable MFA for always-available accounts; MFA MUST remain enforced for these accounts at all times regardless of the deployment setting. §VII MFA updated.
- Q: In §II, does "all operations MUST support dry-run simulation" include read-only operations? → A: No. The requirement applies only to operations with side effects. §II updated.
- Q: In §VII Admin Resets & Unblock, is actor identity confirmation the same MFA challenge process as §15? → A: Yes. The Admin Resets section now explicitly cross-references the §15 MFA challenge requirement. §VII Admin Resets updated.
- Q: In §17, what mechanism produces an audit trail when always-available account records are modified directly in the database? → A: Deferred. TODO(DIRECT_DB_AUDIT) added to §17.
- Q: In §17, what mechanism is required for direct DB modifications to always-available account records? → A: Mandatory CLI wrapper only. Manual procedures are forbidden. Audit entry MUST be written before the modification; if audit logging fails, the modification MUST be blocked. Entries MUST go into the unified audit log (same schema as application events). DB triggers are supplemental only. TODO(DIRECT_DB_AUDIT) RESOLVED in v1.32.0. See §17.Z and docs/direct-db-audit-spec.md.
- Q: In §VII MFA, does "or other equivalent second factor" allow implementation teams to accept additional MFA types? → A: No. The clause is removed. Only TOTP, email, and FIDO2 hardware token are accepted; no other types are currently permitted. §VII MFA updated.
- Q: In §21 Theme Security, can `readonly` accounts modify their own theme preferences? → A: No. `readonly` accounts MUST NOT modify any theme preferences; only `user`-role accounts and above may modify their own preferences. §21 updated.
- Q: In §6 Performance Baselines, should file search, copying, and metadata extraction have numeric baselines? → A: Yes. Added: file search (name-based) ≥ 50k files/min, metadata extraction ≥ 20k files/min, file copying CPU overhead ≤ 10% above native OS baseline on reference hardware. §6 updated.
- Q: In §II, must the secure deletion overwrite algorithm be explicitly selected before production deployment? → A: Yes. The algorithm MUST be selected during installation; installation documentation MUST communicate this required decision to operators and developers in advance. §II updated.
- Q: In §VII Credential Storage, is there a constitutional minimum for Argon2id cost parameters? → A: Yes. Constitutional minimums (OWASP interactive minimums): memory ≥ 64 MiB, iterations ≥ 3, parallelism ≥ 4. Higher values are permitted; actual parameters MUST be documented per release. §VII Credential Storage updated.
- Q: In §5 Additional Constraints and §7 Development Workflow, what does "representative tools" mean in the GUI smoke test? → A: Every tool bundled under the launcher. Both §5 and §7 updated to make this explicit.

### Session 2026-03-12 (Round 4)

- Q: In §V ComponentGuardian `register()` API, is the phrase "a zero-argument callable" duplicated? → A: Yes. The duplicate was removed. §V corrected.
- Q: Should §18 credential storage also exclude the database itself (as §VII already states)? → A: Yes. §18 updated to add "or the database itself" to match §VII.
- Q: Should anomaly detection alerts (§16) also surface to `dev`-role users, or only `admin`-role? → A: Both. Dev-role users MUST also receive anomaly detection alerts. §16 updated.
- Q: What column marks a break-glass account in `user_accounts`? → A: A new `is_breakglass` flag is added to `user_accounts`. This permanently identifies a break-glass account; authentication is permitted only when the break-glass CLI flag or environment variable is explicitly active. §14 and §18 updated.
- Q: What are the break-glass account usernames — are they `admin`/`dev` or distinct? → A: Distinct. The break-glass accounts use fixed usernames `dev_breakglass` and `admin_breakglass` to avoid collision with the always-available accounts. §VII, §18 updated.
- Q: What `account_status` value represents break-glass "disabled by default"? → A: A fourth value `breakglass` is added to the `account_status` enum. Accounts in `breakglass` status cannot authenticate through normal login flows; explicit CLI flag or environment variable is required. §VII callout, §14, §18, §19 updated.
- Q: In §15 reset flow, what constitutes "admin identity proof"? Is it the same as passing own MFA challenge as in §VII? → A: Yes, same concept. §15 updated to use "the admin passing their own MFA challenge". Admin and `dev` accounts MUST have MFA enrolled at installation. §VII MFA updated.
- Q: What is the stored value of the `role` field when unset for a new account? → A: The sentinel string `"unassigned"`. §19 updated.
- Q: In §VIII anonymization, can reversible and irreversible steps be mixed within a single operation? → A: No. The mode selected at the start of the operation applies uniformly to all steps; mixing is NOT permitted. §VIII updated.
- Q: Are the five `action` values in §16 an exhaustive list or representative examples? → A: Representative. Additional action types (e.g., account creation, MFA enrollment, role changes) are also valid. §16 updated.

### Session 2026-03-12 (Round 3)

- Q: In §VI canonical store, is the sentence introducing the JSON fallback complete? → A: It was not — the word "queries." was missing after "category/user." §VI repaired.
- Q: In §VII MFA, does FIDO2 satisfy the "at least one TOTP enrolled" requirement? → A: Yes. The requirement is broadened to "at least one offline-capable MFA method (TOTP or FIDO2 hardware token)." §VII updated.
- Q: In §14, does "lockout status" refer to `is_blocked` alone or also `login_attempts`? → A: Both — `is_blocked` flag and `login_attempts` counter together constitute the lockout status. §14 updated.
- Q: In §VII/§18 break-glass alerts, is the in-app notification real-time only or persistent/queued for all active admins? → A: Persistent and queued. The notification MUST be delivered to all active admin accounts; admins not currently logged in MUST see it upon next login. §VII and §18 updated. Anomaly detection (§16) remains real-time only for currently logged-in admins — the distinction is intentional.
- Q: In §VII MFA recovery, what does "verify their own identity" mean for the admin? → A: The admin MUST pass their own MFA challenge before performing the reset. §VII updated.
- Q: In §16 audit log, what value does `actor` hold for self-service events (`login_success`, `login_failure`, `logout`) where `username` and `actor` are the same person, or for `login_failure` where the actor is unauthenticated? → A: For `login_success` and `logout`, `actor` = `username` (same value). For `login_failure`, `actor` = the attempted username regardless of whether identity is verified. §16 updated.
- Q: In §V ComponentGuardian, does degraded state trigger at initialization only or also at runtime `health_check()` failures? → A: Both. Degraded state fires at initialization failure AND when `health_check()` returns `False` at runtime. Polling interval deferred to TODO(GUARDIAN_POLL_INTERVAL). §V updated.
- Q: In §19, what is the default `role` for new accounts? → A: Unset — no role is assigned by default; an admin MUST explicitly assign a `role` before setting `account_status = active`. §19 updated.
- Q: In §VII Always-Available Accounts, can the `admin`/`dev` accounts be renamed? → A: No. `admin` and `dev` are fixed username values that MUST NOT be changed. Multiple admin-role and dev-role accounts MAY exist; the always-available ones are distinguished by `is_protected = true` and their fixed usernames. §VII updated.
- Q: In §12, are "where applicable" (migration test qualifier) and "where technically feasible" (migration implementation qualifier) the same? → A: Yes, same meaning. §12 unified to "where technically feasible." §VI portability also updated from "migrate forward where possible" to "migrate up or down where technically feasible" to align with §12's bidirectional migration policy.

### Session 2026-03-12 (Round 2)

- Q: In §14, what is the primary key of `user_accounts` — `username` or `user_id`? → A: `user_id` is the unique surrogate primary key; `username` is a unique field attached to each record. §14 updated.
- Q: Does §19 need the same always-available bootstrap exception that appears in §VII? → A: Yes. §19 updated to add the explicit exception: always-available `admin` and `dev` accounts are provisioned directly to `account_status = active` at installation.
- Q: Is the §VI JSON fallback optional (MAY) or mandatory (MUST) when the DB is unavailable? → A: Mandatory. §VI updated from MAY to MUST.
- Q: §12 requires schemas be "forward-only" AND migrations be tested "up/down where applicable" — which applies? → A: Both up and down migration paths are supported where technically feasible; "forward-only" constraint removed. §12 updated.
- Q: In §VII MFA, what qualifies as a valid offline-capable equivalent to TOTP? Does FIDO2 count? → A: Both email and FIDO2 hardware token are named valid equivalents. Email is network-dependent; FIDO2 is accepted as an offline-capable second factor alongside TOTP. §VII updated.
- Q: What is the MFA recovery path when a user loses access to all enrolled MFA methods? → A: Administrator-performed account-level MFA reset. The admin must verify their own identity before proceeding; the action generates an audit entry. §VII updated.
- Q: If a user unenrolls their only enrolled MFA method, does that disable MFA or block unenrollment? → A: Block unenrollment (option B). The system MUST prevent removal of the last enrolled MFA method until at least one other method is enrolled. §VII updated.
- Q: In §16 audit log, are `username` and `actor` the same field or distinct? → A: Distinct. `username` = subject of the action (the account being acted upon); `actor` = the authenticated user performing the action (e.g., the admin). §16 updated.
- Q: Are §IX per-`open()` validation and §22 pipeline invocation two distinct checkpoints? → A: No. §22 is a higher-level restatement of §IX; they represent the same checkpoint. §22 updated with clarifying note.
- Q: Does §VIII require an audit entry for reversible (pseudonymization) anonymization operations? → A: Yes. Audit logging is required for both reversible and irreversible operations. §VIII updated.
- Q: What does ComponentGuardian "degraded state" mean to the user? → A: The component MUST remain visible with reduced functionality; it MUST NOT be hidden or removed from the UI. Per-tool capability definitions are deferred to implementation documentation (see TODO(GUARDIAN_DEGRADED_UX)). §V updated.
- Q: Is the scoped API token / service account mechanism for headless processes defined in the constitution? → A: Deferred to a future implementation. TODO(HEADLESS_AUTH) added to follow-up TODOs. §16 updated with deferral note.

### Session 2026-03-12

- Q: In §VIII and §20 path sanitization — which scope is authoritative: §VIII (external processes + UI display) or §20 (external processes only)? → A: Narrower scope. §VIII updated to match §20: sanitization applies to paths presented to external processes only.
- Q: In §VI and §11 namespace format — `module_settings/<module>` uses a slash; should snake_case apply uniformly? → A: Use snake_case everywhere. Slash is not permitted; module-scoped category names MUST use underscore separator (e.g., `module_settings_af`). Both §VI and §11 updated.
- Q: On fresh install, do always-available accounts bootstrap to `active`, bypassing `pending` — and is that an explicit documented exception? → A: Yes. Always-available accounts bootstrap directly to `account_status = active` as an explicit documented exception to the default `pending` rule. §VII updated with explicit exception callout.
- Q: What does "UAP" stand for in §VI User Isolation? → A: User Attribute Profile — a consistent mechanism for defining, managing, and mapping user attributes across protocols (SCIM, SAML, OIDC). §VI updated with inline definition.
- Q: How is "headless mode" defined in §II? → A: CLI invocation without an interactive GUI session. §II updated with inline definition.
- Q: Does the §IX per-`open()` validation apply to internal RFU-written temp files, or only externally sourced files? → A: Externally sourced files only (from the user's filesystem). Internal temp files written and read back by RFU itself are exempt. §IX updated. ✓ BOUNDARY DEFINED in v1.29.0 — exemption applies only to same-process, same-instance, same-session files. Plugin-written files, cross-tool, cross-process, and cross-session files MUST always be validated. See §IX.X and docs/file-validation-exemption-spec.md.
- Q: Do the §VII consecutive-failure lockout mechanism and the §16 rolling-24h anomaly-detection mechanism share state? → A: They are independent, maintaining separate counters. Once one fires, the other does not additionally apply to the same account for the triggering event (blocked accounts do not also generate anomaly alerts). Both §VII lockout section and §16 updated with independence clause.
- Q: If a user enrolls email-only MFA and goes offline, are they locked out? → A: The system MUST require at least one TOTP method enrolled before email-only MFA is accepted; email-as-sole-MFA enrollment MUST be rejected by the system. §VII MFA section updated.
- Q: Does "Role demotion MAY occur without approval" in §19 mean always approval-free, or optionally approval-free at admin discretion? → A: Always approval-free — role demotion does not require approval. §19 updated to use unambiguous language.
- Q: Is the "representative test corpus" in §22 the same dataset as the "reference dataset" in §6 Performance Baselines? → A: Yes, the same dataset. §22 updated with cross-reference to §6.
- Q: How does the §VI JSON fallback enforce `user_id` isolation? → A: Separate files per user — one JSON file per `user_id`. §VI updated to specify this requirement.

### Session 2026-03-11

- Q: Is the 30 min idle timeout a hard ceiling that no admin can exceed, or the out-of-box default with admins able to raise or lower it? → A: 30 min is the out-of-box default only. Admins MAY configure the installation cap higher or lower (up to an absolute system ceiling of 8 hours). Users configure within the admin cap.
- Q: Must RFU operate fully offline with formal graceful-degradation guarantees, or is online connectivity assumed with offline as best-effort? → A: Online availability is assumed for network-dependent features (email MFA, breached-password denylist, signature database updates). Offline operation is best-effort: breached-password checks emit a warning instead of blocking; TOTP MUST always be available as an offline MFA fallback; no formal air-gapped deployment guarantee.
- Q: Is "Governance §6" a section that should be added to the constitution, or a TODO forward-pointer to a separate document? → A: It is a TODO forward-pointer to a planned docs/governance.md. The constitution rule (≥ 1 MINOR release) is the complete authoritative deprecation rule until that document is created. Both occurrences annotated with TODO(GOVERNANCE_DOC).
- Q: For signature set updates in §IX, when is the version bump PATCH vs MINOR? → A: PATCH for new or updated signatures with no API or policy change. MINOR for: introducing a new file-type category, modifying the policy schema, or removing a previously supported type.
- Q: What counts as sufficient "property-based or scenario edge tests" for critical engines in §III? → A: The test set MUST collectively cover all five scenarios: empty input, single-element input, maximum-expected-size input, random/unexpected input (fuzz or property-based), adversarial/malformed input. No minimum test-case count is prescribed beyond satisfying all five scenarios.
- Q: In §VIII anonymization, when is reversible vs. irreversible mode used? → A: User-driven: the user MUST explicitly select the mode at the start of every operation (no default). Both modes are supported. The constitution now includes a documented classification: reversible operations = name substitution, email masking, address replacement, phone tokenization, custom pattern with mapping; irreversible operations = cryptographic hash replacement, SSN/national-ID redaction, financial account redaction, biometric removal/hash, bulk PII scrub, any user-declared irreversible step. Mixing is permitted per operation with per-step audit logging.
- Q: In §XVI audit log anomaly detection, what does "escalate to maintainers" mean in practice? → A: Two channels required: (1) emit a CRITICAL-level structured log entry; (2) surface an in-app alert in the RFU hub to all currently logged-in admin-role users. No external email or webhook is mandated by the constitution.
- Q: In §VII and §18 break-glass accounts, is post-use password rotation MUST or SHOULD level enforcement — is the system required to block continued break-glass operations, or only to prompt the operator? → A: MUST throughout. The system MUST enforce rotation and MUST block further break-glass operations until rotation completes; operator discretion is not permitted.
- Q: In §VI Portability, "non-conflicting keys are always imported without prompting" appears to conflict with "MUST NOT commit any key until the user confirms the full resolution set" — which atomicity model applies? → A: Model A — single atomic commit. Non-conflicting keys are automatically pre-approved (auto-staged) in the pending import set alongside conflicting keys awaiting user decisions; the review UI shows only conflicting keys. Nothing — conflicting or non-conflicting — is written to the database until the user confirms the full resolution set in one atomic operation.
- Q: In §16, should the OS keyring exception for "headless automation" be retained as a scoped exception or removed entirely? → A: Removed entirely. Session identifiers MUST be stored in memory only with no exceptions. Automation and headless processes that need credential persistence MUST use a separately designed mechanism (scoped API token, service account, etc.); session identifiers MUST NOT be written to the OS keyring or any persistent storage.
- Q: In §16 anomaly detection, does ">10 failed attempts/day/user" mean a calendar day (midnight reset) or a rolling 24-hour period? → A: Rolling 24-hour sliding window. The counter measures any consecutive 24-hour span; there is no midnight reset. ✓ FURTHER DEFINED in v1.30.0 — window MUST be sliding (not fixed-period), evaluated per-second at each attempt, detection MUST trigger immediately at the threshold-crossing attempt. See §16.Y and docs/anomaly-detection-sliding-window-spec.md.
- Q: In §15 Credential Reset, what is a "signed challenge token" — a time-limited HMAC token, a challenge-response, or intentionally unspecified? → A: A time-limited, cryptographically signed token (e.g., HMAC-signed reset token) delivered via an out-of-band channel. It MUST be single-use, expire after a maximum of 1 hour, and both issuance and redemption MUST be recorded in the audit log.
- Q: In §14/§17/§19, do `account_status`, `is_blocked`, and `is_protected` operate as independent orthogonal gates, or does `is_blocked` only apply to active accounts? → A: `is_blocked` is a sub-state of `active` only. Lockout is irrelevant for `pending` and `suspended` accounts (they have no access). Admin unblock resets `is_blocked` and the login counter only; `account_status` is unchanged. `is_protected` is independent of both — it prevents deletion/deactivation of always-available accounts regardless of their current `account_status`.
- Q: In §VII Credential Storage and §14, the password hashing algorithm is listed as "Argon2id or bcrypt" in §VII but only "Argon2id" in §14 — which is authoritative? → A: Argon2id only. §VII updated to remove bcrypt; Argon2id is the sole required algorithm across both sections.
- Q: In §VII Lockout, does "5 consecutive failed logins" mean a strict unbroken streak (reset by any success) or a cumulative total that only an admin can reset? → A: Strict consecutive streak. A successful login resets the failed-attempt counter to zero; only an unbroken run of 5 failures without an intervening success triggers lockout. §VII and §14 both updated to make this explicit.
- Q: In §VII Session Controls, when no admin cap is set, is the user's idle-timeout ceiling 30 min (the default) or the system ceiling of 8 hours? → A: 8-hour system ceiling. 30 min is the active default setting only — it applies as the user's configured value until they change it, but it does not cap what users can configure. When no admin cap is set, users may configure any value from 1 min up to the 8-hour system ceiling. §VII updated to separate default value from configuration ceiling.
- Q: In §VIII Anonymization, what does "double confirmation" mean for irreversible operations — two dialogs, a typed phrase, or unspecified? → A: The user MUST type a confirmation phrase (e.g., the target path or the word "CONFIRM") AND click a confirm button as two separate actions. Both steps are required. The dialog MUST clearly state the irreversibility. §VIII updated to replace "double confirmation" with this explicit definition.
- Q: In §21 Theme Security, should "theme encryption MUST protect sensitive organizational branding" be retained, narrowed to secrets only, or removed? → A: Removed entirely. Theme assets (colors, fonts, spacing tokens) are not sensitive data; encryption is over-engineered for a local file utility. The three remaining §21 bullets (validation, access control, backups) are sufficient.
- Q: In §21, what operations constitute a "system-wide theme change" that triggers the backup requirement? → A: All five: (1) modifying token values in an existing preset, (2) creating a new preset, (3) deleting a preset, (4) switching the active preset, and (5) renaming a preset. Limiting backups to token edits only is explicitly forbidden. If backup creation fails, the theme operation MUST be aborted. See §21.X and docs/theme-backup-trigger-spec.md. Resolved in v1.31.0.
- Q: In §11 Preference Schema, should "Preference writes SHOULD emit structured audit events" use SHOULD or MUST — is audit logging optional for preferences? → A: Changed to MUST. Preference writes are security-relevant (especially sensitive-key writes) and must be audited consistently with all other audit requirements in the constitution.
- Q: In §IV Performance, does "approximately O(N)" have a defined tolerance or is it a vague design intent? → A: Defined. O(N log N) is the worst acceptable complexity; any algorithm with superlinear growth beyond O(N log N) (e.g., O(N²)) is a gate failure. §IV updated accordingly.
- Q: In §14 Authentication Data Handling, does "Login attempts MUST update login_attempts, last_failed_login, and is_blocked" apply to all attempts or only failed ones — would a successful login overwrite last_failed_login? → A: Only failed attempts update login_attempts, last_failed_login, and is_blocked. Successful logins reset login_attempts and is_blocked, and stamp last_login; last_failed_login is untouched on success. §14 rewritten to make the two paths explicit.
- Q: In §15 Credential Reset, "expire after a short validity window" is undefined — how long is the maximum token validity? → A: 1 hour maximum. Tokens not redeemed within 1 hour MUST be invalidated. §15 updated to replace "short validity window" with this explicit bound.
- Q: In §6 Performance Baselines, "reference dataset (documented)" is never defined in the constitution — should minimum dataset specs be added inline? → A: No inline spec needed. The `(documented)` caveat is sufficient; the constitution requires only that a reference dataset be published externally. Implementation teams define and document the dataset in the appropriate performance documentation.
- Q: In §4 Static Analysis, what qualifies as an "equivalent" to bandit for security scanning — is the gate tool-agnostic or is bandit the required default? → A: Bandit is the required default. A substitute is permitted only if it covers all bandit checks at minimum, the substitution is documented in CI configuration, and a maintainer-approved justification exists. §4 updated accordingly.
- Q: In §I Cross-Platform, what makes a keyboard shortcut "infeasible" — is the qualifier defined? → A: Intentionally loose. "Where feasible" is a design-intent qualifier, not an enforceable gate. Implementation teams exercise judgement at implementation time. No definition added.
- Q: In §22, is the 1% heuristic false-positive threshold measured per-tool or globally? → A: Both gates apply independently: each tool's ruleset MUST be ≤ 1% on its representative test corpus (per-tool gate), AND the combined production ruleset across all tools MUST also be ≤ 1% globally. Breaching either gate triggers a patch release.
- Q: In §VII and §18 break-glass alerts, does "notify all active admins" mean in-app only (reaches currently logged-in admins), out-of-band to all active admin accounts, or strongest with a specified channel? → A: Strongest with specified channel (option C). Break-glass login MUST attempt two channels: (1) in-app notification to all active admin accounts, and (2) out-of-band email to all active admin accounts if an email delivery channel is configured. Both channels MUST be attempted; failure on one channel MUST be logged but does not suppress the other. §VII and §18 both updated to state this explicitly.
- Q: In §12 Data Migration, "time-bounded" is never defined — should a hard CI timeout or a per-migration inline declaration apply? → A: Per-migration inline declaration (option B). No universal ceiling is prescribed; each migration file MUST declare its own expected maximum run duration inline (e.g., as a comment or metadata field at the top of the file). §12 updated accordingly.
## Governance

1. Authority: This Constitution supersedes conflicting informal practices.
2. Amendment Proposal: Open a PR modifying this file plus a justification
   section in description referencing impacted principles and rationale.
3. Approval Requirements: Minor & Patch: ≥ 2 maintainer approvals. Major
   (adding/removing/redefining a principle or changing governance mechanics):
   ≥ 3 maintainer approvals + migration strategy document.
4. Versioning Policy (Governance Doc):
   - MAJOR: Backward-incompatible governance change; principle removal or
     semantic redefinition.
   - MINOR: New principle, new mandatory gate, or material expansion of a
     principle's normative rules.
   - PATCH: Clarifications, typo fixes, non-normative wording, formatting.
5. Compliance Review: Quarterly audit (end of Mar/Jun/Sep/Dec) produces a
   report listing deviations + corrective actions tracked as issues.
6. Deprecation Cycle: The minimum deprecation window is **≥ 1 MINOR release**
   (canonical; see also Additional Constraint §10). Announce deprecated public
   API in CHANGELOG with the target removal version; MUST supply migration
   guidance. Security-critical removals may skip this cycle with expedited
   review.
7. Data & Preference Migrations: Any breaking change to preference categories,
   keys, or types MUST ship with a migration plan, automated migration script,
   and fallback defaults. Cross-module migrations MUST not introduce coupling;
   each module owns its scope.
8. Emergency Amendments: Security/data-loss critical changes may bypass
   normal cycle with expedited review (≥ 2 approvals) then retroactive audit.
9. Enforcement: Every PR template MUST include a "Constitution Compliance"
   checklist; reviewers MUST block until all mandatory gates pass.
10. Ratification: This initial version (1.0.0) is ratified by founding
    maintainers on the date below. Future amendments update Last Amended.
11. Dispute Resolution: If reviewers deadlock, escalate to maintainer vote; a
    simple majority decides within 5 business days.

**Version**: 1.26.0 | **Ratified**: 2025-09-29 | **Last Amended**: 2026-04-04
