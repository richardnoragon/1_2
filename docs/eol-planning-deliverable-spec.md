# EOL Migration Planning Deliverable — Canonical Specification

**Document version**: 1.0.0
**Status**: Normative
**Constitutional basis**: §1 (Language & Framework / Additional Technical & Quality Constraints), §1.X
**Source clarification**: constitution_clairification_uiux_harmonny_r8.md — Q20
**Applied in constitution version**: v1.33.0
**Resolves**: TODO(EOL_PLANNING_DELIVERABLE) — open since v1.11.0

**See also**:
- `.specify/memory/constitution.md` §1, §1.X.1–§1.X.6
- `.specify/memory/checklist-eol-planning-compliance.md`
- `docs/direct-db-audit-spec.md` (§17.Z — parallel resolved-TODO spec)

---

## 1. Purpose

§1 requires: *"Migration past EOL versions MUST be planned before upstream EOL
minus 90 days."*

The word *"planned"* was constitutionally required but undefined since v1.11.0
(TODO(EOL_PLANNING_DELIVERABLE)). Without a minimum deliverable definition, the
90-day deadline cannot be audited, verified in a PR, or enforced by CI.

This document defines the minimum enforceable deliverable, the responsible
party, the CI enforcement mechanism (`eol.yaml`), and the obligations that close
that ambiguity.

---

## 2. Definition of "Planned"

A migration is considered **"planned"** only when a **migration issue** exists
in the project's authoritative issue tracker that contains ALL of the following:

| Required field | Description |
|---|---|
| Upstream component + version | Which dependency / framework is approaching EOL |
| Upstream EOL date | The exact date support ends |
| Migration target | The replacement version or alternative being migrated to |
| Assigned owner | A named, human-attributable person (not a bot or generic account) |
| Milestone with due date | A tracker milestone whose due date is before or on the EOL date |
| Actionable description | Required migration steps or investigation tasks (MAY reference an external doc) |

### 2.1 What Does NOT Satisfy "Planned"

| Candidate | Why it fails |
|---|---|
| Mental note by a developer | Not trackable or auditable |
| Informal team discussion | Not auditable |
| Filed issue with no milestone | No deadline — meaningless |
| Filed issue with no assignee | No ownership — meaningless |
| Issue created after the 90-day deadline | Late creation does not retroactively satisfy |
| Issue in a non-canonical tracker | Not visible in CI gate or PR review |

---

## 3. Deadline

The migration issue MUST be created **no later than 90 days before the upstream
EOL date**:

```
issue_creation_date ≤ upstream_eol_date − 90 days
```

---

## 4. Responsible Party

The **Maintainer or Release Steward** is responsible for:

1. Monitoring upstream EOL dates for all project dependencies.
2. Creating the migration issue before the 90-day deadline.
3. Ensuring the issue is assigned (to themselves or a delegated owner).
4. Ensuring the issue has a milestone with a due date.
5. Keeping the `eol.yaml` configuration file up to date.
6. Ensuring CI passes the EOL-planning gate on every build.

---

## 5. `eol.yaml` Configuration File

CI enforces the EOL-planning gate via a machine-readable configuration file
committed in the repository root (or a designated config directory). The
canonical filename is `eol.yaml`.

### 5.1 Schema

```yaml
# eol.yaml — EOL tracking configuration
# Required fields per entry:
#   component:    Upstream dependency name (string)
#   version:      Currently used version (string)
#   eol_date:     Upstream EOL date (ISO 8601 date, YYYY-MM-DD)
#   migration_issue: Tracker issue ID or URL (string, required when
#                    eol_date < today + 90 days)
#   migration_target: Target version or replacement (string)
#   notes:        Optional free-text notes

dependencies:
  - component: "Python"
    version: "3.12"
    eol_date: "2028-10-31"
    migration_issue: ""          # Not yet required (>90 days away)
    migration_target: ""
    notes: "Monitor annually"

  - component: "PyQt5"
    version: "5.15"
    eol_date: "2026-06-30"
    migration_issue: "https://github.com/org/repo/issues/42"
    migration_target: "PyQt6 6.x"
    notes: "See issue #42 for migration plan and test strategy"
```

### 5.2 Required Fields When EOL < 90 Days Away

When `eol_date < today + 90 days`, the entry MUST have:

- `migration_issue` — non-empty tracker reference
- `migration_target` — non-empty migration target

Empty strings in these fields with an imminent EOL date MUST cause CI to fail.

---

## 6. CI Enforcement

### 6.1 Gate Logic (pseudocode)

```python
from datetime import date, timedelta
import yaml

DEADLINE_DAYS = 90
WARNING_DAYS = 180

def check_eol_gate(eol_yaml_path: str) -> list[str]:
    """
    Returns a list of violation messages.
    Empty list = gate passes.
    Non-empty = gate FAILS.
    """
    violations = []
    today = date.today()

    with open(eol_yaml_path) as f:
        config = yaml.safe_load(f)

    for dep in config.get("dependencies", []):
        component = dep["component"]
        eol = date.fromisoformat(dep["eol_date"])
        days_until_eol = (eol - today).days

        if days_until_eol < DEADLINE_DAYS:
            # Mandatory gate: migration issue MUST exist and be complete
            issue = dep.get("migration_issue", "").strip()
            target = dep.get("migration_target", "").strip()

            if not issue:
                violations.append(
                    f"FAIL: {component} EOL in {days_until_eol} days "
                    f"but no migration_issue is set in eol.yaml"
                )
            if not target:
                violations.append(
                    f"FAIL: {component} EOL in {days_until_eol} days "
                    f"but no migration_target is set in eol.yaml"
                )
            if issue:
                # CI also validates the issue has assignee + milestone
                # (via tracker API call or static check)
                issue_valid = validate_issue_fields(issue)
                if not issue_valid:
                    violations.append(
                        f"FAIL: {component} migration issue {issue} is "
                        f"missing required fields (assignee and/or milestone)"
                    )

        elif days_until_eol < WARNING_DAYS:
            # Advisory only — does not fail CI
            print(f"WARN: {component} EOL in {days_until_eol} days — "
                  f"consider creating migration issue soon")

    return violations


def validate_issue_fields(issue_ref: str) -> bool:
    """
    Check that the referenced issue has:
    - an assigned owner (non-bot, non-empty)
    - a milestone with a due date
    - actionable content (non-placeholder description)
    Implementation: query tracker API or parse issue metadata file.
    """
    ...
```

### 6.2 CI Failure Conditions

CI MUST fail if any of the following are true:

| Condition | Gate result |
|---|---|
| `eol.yaml` file is absent from the repository | FAIL |
| Any dependency with EOL < 90 days has no `migration_issue` | FAIL |
| Any dependency with EOL < 90 days has no `migration_target` | FAIL |
| Referenced migration issue lacks an assignee | FAIL |
| Referenced migration issue lacks a milestone | FAIL |
| Referenced migration issue has placeholder/empty description | FAIL |
| A PR introduces a new EOL-bound dependency without a migration issue | FAIL |
| A PR removes or alters EOL metadata without justification | FAIL |

CI MAY warn (but MUST NOT fail) when EOL < 180 days with no issue yet.

---

## 7. CI Tests

### T1 — Gate Passes with Compliant Issue

```python
def test_t1_gate_passes_compliant():
    eol_yaml = build_eol_yaml(
        component="PyQt5",
        eol_date=today() + timedelta(days=30),   # <90 days
        migration_issue="https://tracker/issues/42",
        migration_target="PyQt6 6.x",
    )
    mock_issue_valid(True)
    violations = check_eol_gate(eol_yaml)
    assert violations == []
```

### T2 — Gate Fails: EOL < 90 Days, No Issue

```python
def test_t2_gate_fails_no_issue():
    eol_yaml = build_eol_yaml(
        component="PyQt5",
        eol_date=today() + timedelta(days=30),
        migration_issue="",
        migration_target="",
    )
    violations = check_eol_gate(eol_yaml)
    assert any("migration_issue" in v for v in violations)
```

### T3 — Gate Fails: Issue Missing Assignee

```python
def test_t3_gate_fails_missing_assignee():
    eol_yaml = build_eol_yaml(
        component="PyQt5",
        eol_date=today() + timedelta(days=30),
        migration_issue="https://tracker/issues/42",
        migration_target="PyQt6 6.x",
    )
    mock_issue_valid(False)  # issue has no assignee
    violations = check_eol_gate(eol_yaml)
    assert any("missing required fields" in v for v in violations)
```

### T4 — Advisory Warning for EOL < 180 Days (No Fail)

```python
def test_t4_advisory_warning_no_fail():
    eol_yaml = build_eol_yaml(
        component="Python",
        eol_date=today() + timedelta(days=120),  # <180 but >90
        migration_issue="",
        migration_target="",
    )
    violations = check_eol_gate(eol_yaml)
    assert violations == []   # advisory only — no failure
```

### T5 — Missing `eol.yaml` Fails Gate

```python
def test_t5_missing_eol_yaml():
    with pytest.raises((FileNotFoundError, SystemExit)):
        check_eol_gate("nonexistent_path/eol.yaml")
```

---

## 8. Cross-References

| Document | Relevant section |
|---|---|
| `.specify/memory/constitution.md` | §1 (Language & Framework bullet), §1.X.1–§1.X.6 |
| `.specify/memory/checklist-eol-planning-compliance.md` | Reviewer checklist Sections A–F |
| `docs/direct-db-audit-spec.md` | §17.Z — parallel resolved-TODO spec (CLI wrapper) |
| `docs/theme-backup-trigger-spec.md` | §21.X — parallel resolved-ambiguity spec |
