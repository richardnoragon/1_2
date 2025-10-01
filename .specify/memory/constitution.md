<!--
Sync Impact Report
Version change: (none prior) → 1.0.0
Modified principles: N/A (initial ratification)
Added sections: Core Principles; Additional Technical & Quality Constraints; Development Workflow & Quality Gates; Governance
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ (version reference updated)
  - .specify/templates/spec-template.md ✅ (no version reference; aligned implicitly)
  - .specify/templates/tasks-template.md ✅ (no changes needed)
  - .specify/templates/agent-file-template.md ✅ (no constitution references yet)
Follow-up TODOs: None
-->

# RFU (Richard's File Utilities) Constitution

## Core Principles

### I. Cross-Platform Consistency

All supported operating systems (Windows, macOS, Linux) MUST deliver identical
functional capabilities (feature flags may only disable OS-infeasible actions).
UI labels, shortcuts (where feasible), and behaviors MUST remain consistent.
Platform-specific code MUST be isolated behind clearly named adapter modules.
Rationale: Predictable behavior across environments reduces user friction and
lowers maintenance cost by preventing divergent code paths.

### II. Safety & Data Integrity (NON‑NEGOTIABLE)

Destructive operations (delete, secure wipe, overwrite) MUST be opt-in and
require explicit user confirmation (or a signed CLI flag in headless mode).
Default behavior for move/copy/sync MUST preserve source data unless user
chooses otherwise. Secure deletion MUST use verified overwrite patterns.
All operations MUST support dry‑run simulation. Metadata manipulations MUST
validate schema before commit. Rationale: File utilities operate on critical
user assets; irreversible loss must be virtually eliminated.

### III. Test-Driven Quality & Observability

All new functionality MUST begin with failing automated tests (unit and where
relevant integration). Minimum global line coverage MUST remain ≥ 85% and MUST
not decrease in a PR. Critical engines (duplicate detection, secure delete,
batch processors) MUST have property-based or scenario edge tests. Structured
logging (levelled, machine-parsable) and error classification MUST accompany
features. Rationale: Fast feedback and rich telemetry enable safe evolution.

### IV. Performance & Scalability of Batch Operations

Core batch operations (search, duplicate scan, metadata extraction, copying)
MUST stream and avoid loading entire directory trees or large files wholly in
memory. Operations on N files MUST scale approximately O(N) with clear
progress reporting. UI interactions MUST stay responsive (no blocking main GUI
thread > 100ms; use worker threads/process pools). Rationale: User trust and
enterprise viability depend on predictable performance under large workloads.

### V. Simplicity & Extensible Modularity

Features MUST be implemented as modular, discoverable tool components with
clear single responsibility. Public interfaces (CLI / scripted APIs) MUST be
stable; changes require deprecation cycle (see Governance). Avoid premature
generalization: implement minimum set that satisfies explicit requirements.
Extension points (tool discovery, engines) MUST document contracts and failure
modes. Rationale: Lean, modular design reduces coupling and accelerates safe
innovation.

## Additional Technical & Quality Constraints

1. Language & Framework: Python ≥ 3.8, Qt5 GUI. Migration past EOL versions
   MUST be planned before upstream EOL minus 90 days.
2. Code Style: PEP 8 enforced; mypy type checking with no new errors allowed.
3. Security: All external inputs (paths, metadata) MUST be validated; no
   shell command execution without explicit sanitization. Secure delete MUST
   document overwrite algorithm. Sensitive logs MUST be redactable.
4. Logging & Errors: No silent failures; user-facing errors MUST provide
   actionable remediation guidance. Internal stack traces logged at DEBUG+.
5. Coverage & Gates: PRs MUST pass: lint, type check, unit + integration tests,
   coverage ≥ threshold, GUI smoke test (launch + tool open). Failing gate →
   reject.
6. Performance Baselines: Duplicate scanning: ≥ 10k files/min on reference
   dataset (documented). UI main thread blocked < 100ms segments. Long-running
   tasks MUST expose cancellable progress.
7. Accessibility: Key actions reachable via keyboard; color selections MUST
   maintain WCAG AA contrast for text.
8. Documentation: New tools MUST include: purpose, usage examples, expected
   performance characteristics, error codes, and test strategy summary.
9. Dependency Management: New runtime dependency MUST justify: necessity,
   security posture, maintenance health. Vendoring considered for small libs.
10. Backward Compatibility: Public CLI flags and scripting APIs require a
    deprecation period ≥ 1 MINOR release unless security issue mandates fast
    removal.

## Development Workflow & Quality Gates

1. Branching: feature/_, fix/_, chore/_, docs/_ naming. One logical change per
   PR. PR description MUST map changes to affected principles (checklist).
2. TDD Flow: Write failing tests → implement → refactor with green tests.
3. Reviews: Minimum 2 maintainer approvals for: destructive engine changes,
   security-sensitive code, or performance-critical paths; otherwise ≥ 1.
4. Static Analysis: Lint (flake8/black), mypy, security scanning (bandit or
   equivalent) MUST pass before review request.
5. Release Process: Semantic Versioning (SemVer). Automated CI builds assets
   (binaries / PyPI wheel) after tag push. Changelog entry REQUIRED.
6. Documentation Gate: PR adding/changing user-visible behavior MUST update
   user guide + API reference before merge.
7. Test Categories: Unit (fast, isolated), Integration (engines, DB, FS), GUI
   smoke (launch + open representative tools), Performance (nightly), Security
   (pattern scans). Critical regressions block release.
8. Incident Handling: Production-impacting defect (data loss, security) MUST
   trigger post-mortem within 72h including root cause, principle impacts, and
   remediation tasks.
9. Artifact Retention: Build + test logs retained ≥ 180 days for audit.
10. Contribution Onboarding: New contributor PR triggers automated checklist
    comment with principle summary and required gates.

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
6. Deprecation Cycle: Announce deprecated public API in CHANGELOG with target
   removal version; MUST supply migration guidance.
7. Emergency Amendments: Security/data-loss critical changes may bypass
   normal cycle with expedited review (≥ 2 approvals) then retroactive audit.
8. Enforcement: Every PR template MUST include a "Constitution Compliance"
   checklist; reviewers MUST block until all mandatory gates pass.
9. Ratification: This initial version (1.0.0) is ratified by founding
   maintainers on the date below. Future amendments update Last Amended.
10. Dispute Resolution: If reviewers deadlock, escalate to maintainer vote; a
    simple majority decides within 5 business days.

**Version**: 1.0.0 | **Ratified**: 2025-09-29 | **Last Amended**: 2025-09-29
