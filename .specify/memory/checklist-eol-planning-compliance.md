# Reviewer Checklist — EOL Migration Planning Compliance

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §1 (Language & Framework / Additional Technical & Quality Constraints), §1.X
**Resolves**: TODO(EOL_PLANNING_DELIVERABLE) — open since v1.11.0
**Applied in constitution version**: v1.33.0

**See also**:
- `.specify/memory/constitution.md` §1, §1.X.1–§1.X.6
- `docs/eol-planning-deliverable-spec.md` (canonical spec, `eol.yaml` schema,
  CI gate logic, tests T1–T5)

---

## How to Use This Checklist

Mark each item ✓ (pass), ✗ (fail), or N/A. Any ✗ is a constitutional violation
that MUST be resolved before merge. Every section must be fully signed-off by a
reviewer and the CI pipeline.

---

## Section A — Existence and Location of `eol.yaml`

- [ ] **A.1** An `eol.yaml` (or equivalent EOL-tracking configuration file)
  exists in the repository at the designated location (repo root or designated
  config directory).
- [ ] **A.2** The file is committed to version control and included in CI
  checks.
- [ ] **A.3** The file lists all tracked upstream dependencies with their
  current versions and EOL dates.
- [ ] **A.4** The file is up to date — no known dependencies with approaching
  EOL are absent from the list.

*FAIL if*: `eol.yaml` is absent, not committed, or excludes known EOL-bound
dependencies.

---

## Section B — Migration Issue Existence

For each dependency with EOL < 90 days away:

- [ ] **B.1** A migration issue exists in the project's authoritative issue
  tracker (not a personal fork, private notes, or external platform).
- [ ] **B.2** The `migration_issue` field in `eol.yaml` is non-empty and
  references the correct tracker issue.
- [ ] **B.3** The issue creation timestamp is ≥90 days before the upstream
  EOL date (late creation does not retroactively satisfy).
- [ ] **B.4** The issue has not been created after the deadline and then
  backdated.

*FAIL if*: Any dependency with EOL < 90 days has no valid migration issue
reference in `eol.yaml`.

---

## Section C — Required Fields in the Migration Issue

Each migration issue for a dependency with EOL < 90 days MUST contain ALL of:

- [ ] **C.1** Upstream component name and version approaching EOL.
- [ ] **C.2** Upstream EOL date (explicitly stated in the issue body).
- [ ] **C.3** `migration_target` field in `eol.yaml` is non-empty and the
  issue body names the target version or replacement.
- [ ] **C.4** An **assigned owner** (a named, human-attributable person — not
  a bot, not a generic service account, not blank).
- [ ] **C.5** A **milestone with a due date** set on the issue (the milestone
  due date MUST be before or on the upstream EOL date).
- [ ] **C.6** An actionable description covering required migration steps or
  investigation tasks (not a placeholder such as "TBD" or "investigate later").

*FAIL if*: Any required field is absent, empty, or filled with a placeholder.

---

## Section D — Deadline Compliance

- [ ] **D.1** Issue creation date satisfies:
  `issue_creation_date ≤ upstream_eol_date − 90 days`.
- [ ] **D.2** No "retroactively planned" issues — issues created after the
  deadline do not satisfy the requirement even if all other fields are present.
- [ ] **D.3** The CI gate validates creation date, not just issue existence.

*FAIL if*: The issue was created within 90 days of the EOL date.

---

## Section E — Ownership and Accountability

- [ ] **E.1** The Maintainer or Release Steward is identified as the
  responsible party for EOL tracking in the project's operations documentation.
- [ ] **E.2** The migration issue's assignee is a named, human-attributable
  person with an active role in the project.
- [ ] **E.3** The issue is not assigned to a bot, CI service account, or
  collective team account without a designated individual.

---

## Section F — CI Gate Enforcement

### F.1 — Gate Configuration

- [ ] **F.1.1** CI includes an EOL-planning gate that runs on every build
  (not only on PRs touching `eol.yaml`).
- [ ] **F.1.2** The gate reads `eol.yaml` and validates each dependency with
  EOL < 90 days.
- [ ] **F.1.3** The gate validates all required issue fields (assignee,
  milestone, migration target, actionable description) — not just issue
  existence.
- [ ] **F.1.4** The gate CANNOT be bypassed by a flag, environment variable,
  or skip label without explicit maintainer approval recorded in the PR.

### F.2 — CI Failure Conditions

CI MUST fail (and the reviewer MUST confirm it fails) for each of the
following:

- [ ] **F.2.1** `eol.yaml` is absent from the repository.
- [ ] **F.2.2** Any dependency with EOL < 90 days has no `migration_issue`
  entry.
- [ ] **F.2.3** Any dependency with EOL < 90 days has no `migration_target`
  entry.
- [ ] **F.2.4** Referenced migration issue lacks an assignee.
- [ ] **F.2.5** Referenced migration issue lacks a milestone.
- [ ] **F.2.6** A PR introduces a new EOL-bound dependency without a
  compliant migration issue.

### F.3 — Required CI Tests

Each test must exist and pass in the CI pipeline:

| Test | Behaviour | Pass condition |
|---|---|---|
| **T1** | Compliant issue exists for imminent EOL | Gate passes; no violations |
| **T2** | EOL < 90 days, no issue in yaml | Gate FAILS with violation message |
| **T3** | Issue exists but missing assignee/milestone | Gate FAILS with violation message |
| **T4** | EOL < 180 days, > 90 days, no issue | Advisory warning only; no failure |
| **T5** | `eol.yaml` file absent | Gate FAILS (FileNotFoundError or equivalent) |

- [ ] **F.3.1** T1 passes.
- [ ] **F.3.2** T2 passes.
- [ ] **F.3.3** T3 passes.
- [ ] **F.3.4** T4 passes (confirms advisory-only, not a gate failure).
- [ ] **F.3.5** T5 passes.

---

## Sign-Off

| Role | Reviewer | Date | Pass/Fail |
|---|---|---|---|
| Developer | | | |
| Maintainer / Release Steward | | | |
| CI pipeline | | | |
