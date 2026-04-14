# Constitution Clarification — Round 8 Review
**Source**: `constitution.md` v1.12.0
**Date**: 2026-03-31
**Scope**: Post-Round-7 review — new ambiguities, inconsistencies, and unclear statements

---

## §I — Cross-Platform Consistency

### Q1 — "OS-infeasible" actions: who judges, and is there a review gate?
§I states: "feature flags may only disable OS-infeasible actions." The term "OS-infeasible" is not defined. There is no stated process for designating an action as OS-infeasible, and no documentation or review gate is required.

**Problem**: A developer could silently disable a feature on one platform by declaring it "infeasible" without review. There is no constitutional check on this judgment.

**Question**: Who has authority to declare an action OS-infeasible (PR author, maintainer, automated CI check), and is a documented justification or review gate required? Should this decision be recorded in the PR or a capabilities matrix?
**Anwser**: Reasoning
“OS‑infeasible” is a powerful escape hatch — it allows disabling features per‑platform.

Without a review gate, a developer could silently disable functionality.

Cross‑platform consistency is a constitutional requirement; therefore, disabling features must be auditable.

The constitution should:

define who can declare infeasibility

require justification

require reviewer oversight

require documentation in a capabilities matrix

The correct authority is maintainers, not PR authors.

CI cannot judge feasibility; it can only enforce documentation presence.

Conclusion
Only maintainers may approve an OS‑infeasible designation.
A written justification MUST appear in the PR, and the capabilities matrix MUST be updated.
Feature flags cannot be disabled without this review gate.
---

## §II — Safety & Data Integrity

### Q2 — Testable definition of "user-discoverable" for dry-run
§II requires each tool to "expose the dry-run capability in a user-discoverable way before the operation is committed." "User-discoverable" is the constitutional quality bar but is not defined in testable terms.

**Problem**: A tool author could argue that a dry-run flag buried in documentation is "discoverable." There is no way to verify this in a PR review or CI gate.

**Question**: What is the minimum testable definition of "user-discoverable"? Is documentation-only sufficient, or must the dry-run capability be surfaced as a visible element in the tool's UI before any action sequence begins? Should a "dry-run surface check" be added to the §DW §5 coverage gates?
**Anwser**: Reasoning
“User‑discoverable” is too vague to test.

Documentation‑only discoverability is unacceptable — users rarely read docs.

The constitution must require visible UI presence before the action begins.

A PR reviewer must be able to verify this visually.

Therefore:

dry‑run must appear as a visible UI element

before the user initiates the operation

and must be included in §DW §5 coverage gates

Conclusion
Dry‑run MUST be surfaced as a visible UI element before any action begins.
Documentation‑only is insufficient.
A dry‑run surface check MUST be added to §DW §5 coverage gates.
---

## §VI — User Preference Management & Personalization

### Q3 — Conflict detection: live stored value vs schema default
§VI defines a conflict as: "any existing key whose stored value differs from the imported value." The phrase "existing key" and "stored value" is ambiguous when a user has never explicitly set a preference (i.e., the DB returns the schema default).

**Problem**: If a user has never changed a preference key, its stored representation may be: (a) the default value written to DB on first read, (b) absent from the DB entirely (default returned at query time), or (c) a null. Whether an imported value that differs from the schema default constitutes a "conflict" varies by implementation.

**Question**: Is conflict detection performed against the live value in the DB (whatever is actually stored, including writes-of-defaults), or against the schema-defined default? If the key is entirely absent from the DB (never set), does an imported value for that key constitute a conflict, or is it treated as a new key with no conflict?
**Anwser**: Reasoning
A conflict is defined as “existing key whose stored value differs from imported value.”

But “existing key” is ambiguous when the DB may not store defaults.

Three possible models:

(a) Compare against DB value
Clean, consistent, testable.

If the key is absent, there is no conflict.

(b) Compare against schema default
Causes false conflicts when user never set the value.

(c) Hybrid
Too complex and ambiguous.

The correct constitutional stance:

conflict detection must use actual stored values

absence of a key means no conflict

imported value simply becomes the new stored value

Conclusion
Conflict detection MUST compare against the live stored value.
If a key is absent from the DB, it is NOT a conflict — it is treated as a new key.
---

### Q4 — Export format "or equivalent": constrained or implementation-free?
§VI defines the export format as "versioned, schema-validated (JSON or equivalent)." The word "equivalent" is undefined.

**Problem**: Without a constraint on what "equivalent" means, an implementation team could choose a proprietary binary format or a human-unreadable format that makes external tooling or user inspection impossible.

**Question**: Is "equivalent" constrained to human-readable structured text formats (e.g., YAML, TOML, JSON), or may the implementation team choose any serialization format including binary (e.g., protobuf, MessagePack)? Should the constitution name the permitted formats or define a minimal portability requirement (e.g., "must be portable to any compliant implementation without a vendor-specific parser")?
**Anwser**: Reasoning
“Equivalent” is dangerously vague.

Binary formats reduce transparency and break portability.

The constitution must guarantee:

human readability

cross‑implementation portability

schema validation

Therefore:

restrict “equivalent” to human‑readable structured text formats

prohibit proprietary or binary formats

require that any compliant implementation can parse the export without vendor‑specific tooling

Conclusion
“Equivalent” means human‑readable structured text (JSON, YAML, TOML).
Binary or proprietary formats are NOT permitted.
Exports MUST be portable to any compliant implementation without vendor‑specific parsers.
---

### Q5 — Admin idle-timeout cap: maximum only, or minimum + maximum?
§VII Session Controls states admins MAY configure "an installation-wide cap anywhere from 1 min up to an absolute system ceiling of 8 hours." This is an upper-bound cap only.

**Problem**: An admin who wants to enforce a security policy requiring short sessions (e.g., max 5 min for regulated environments) can set the cap to 5 min. But an admin who wants to enforce a *minimum* session length (preventing users from setting a 30-second timeout that triggers cascading logouts) has no constitutional mechanism. Additionally, a user could set their idle timeout to 1 minute regardless of any admin preference, potentially creating excessive re-authentication friction.

**Question**: Can admins configure a deployment-wide *minimum* idle timeout in addition to the maximum cap? Or is the admin control strictly a ceiling and users are always free to configure any value from 1 minute up to that ceiling?

> *(Note: This is a §VII question but placed here because it touches preference management architecture.)*
**Anwser**: Reasoning
Current constitution defines only a maximum cap.

This allows users to set extremely short timeouts (e.g., 30 seconds), causing:

session thrashing

excessive MFA prompts

degraded UX

Admins may need to enforce a minimum timeout for stability.

Therefore:

admins should be able to set both a minimum and maximum

users must choose within that range

This mirrors OS and enterprise policy patterns (Windows, macOS, Linux PAM).

Conclusion
Admins MAY configure both a minimum and maximum idle‑timeout.
Users MUST choose a value within that admin‑defined range.
---

## §VII — Identity & Access Control

### Q6 — Suspension hierarchy: can admins/devs suspend each other?
§VII Account Suspension states: "Only accounts with `role = admin` or `role = dev` MAY set another account's `account_status` to `suspended`." No hierarchy is defined within admin and dev roles.

**Problem**: This permits an admin to suspend a dev account, a dev to suspend an admin account, or any admin to suspend any other admin. There is no protection against an adversarial admin suspending the always-available `admin` account (even though §17 says it cannot be "deleted or deactivated," suspension may be distinct from deactivation).

**Questions**:
- Can a `dev`-role account suspend an `admin`-role account, and vice versa?
- Can an `admin` suspend the always-available `admin` or `dev` accounts (the `is_protected` ones)?
- Is suspension of always-available accounts blocked by the `is_protected` flag, or is the protection limited to deletion/deactivation only?
**Anwser**: Reasoning
Current text allows:

dev suspending admin

admin suspending dev

admin suspending always‑available admin

This is dangerous.

The constitution must protect:

always‑available accounts

role hierarchy

Correct model:

devs cannot suspend admins

admins cannot suspend protected accounts

protected accounts cannot be suspended at all

Suspension is distinct from deletion/deactivation, but protection should apply to all destructive state transitions.
Conclusion
Devs MAY NOT suspend admins.
Admins MAY NOT suspend protected accounts.
Protected accounts cannot be suspended under any circumstances.
Admins MAY suspend non‑protected devs and non‑protected admins.
---

### Q7 — MFA enrollment before activation: system-enforced or procedural only?
§VII MFA states: "all other admin-role and dev-role accounts MUST have MFA enrolled before their `account_status` is set to `active`." No enforcement mechanism is specified.

**Problem**: "MUST have MFA enrolled" could be read as a procedural requirement (the operator must do this but the system does not block it), or as a hard system constraint (the system rejects the `active` status transition if MFA is not enrolled).

**Question**: Is the MFA-before-activation requirement enforced programmatically by the system (it is impossible to set `account_status = active` for an admin/dev account without at least one offline-capable MFA method enrolled), or is it a process mandate that relies on the operator to comply?
**Anwser**: Reasoning
MFA is a security boundary.

If it is procedural only, it will be violated.

Constitution uses MUST → implies enforceable constraint.

Therefore:

system must block activation until MFA is enrolled

operator cannot bypass this

this is consistent with enterprise IAM systems (Azure AD, Okta, AWS IAM)

Conclusion
The MFA‑before‑activation requirement is system‑enforced.
The system MUST reject any attempt to set account_status = active for admin/dev accounts without at least one offline‑capable MFA method enrolled.
---

### Q8 — Break-glass annual drill: who is responsible for conducting it?
§18 states: "break-glass credentials MUST be tested at least once per year with documented results." TODO(BREAKGLASS_DRILL_DOCS) (outstanding since v1.11.0) defers defining what "documented results" requires.

**Problems**:
1. The responsible party is undefined: any admin, any dev, a designated security officer?
2. TODO(BREAKGLASS_DRILL_DOCS) is unresolved and has been since v1.11.0.

**Questions**:
- Which role(s) are responsible for conducting the annual break-glass drill?
- What does "documented results" require at a minimum: a checklist entry, a PR to `/test-evidence/`, an audit log entry, or a separate governance document?
- Should the TODO(BREAKGLASS_DRILL_DOCS) be resolved in this round?
**Anwser**: Q8 — Break‑glass annual drill: who is responsible, what counts as documentation, and should the TODO be resolved now?
Reasoning
Break‑glass is the highest‑risk authentication path in the system.
Therefore, the annual drill must be:

owned by a specific role,

auditable,

repeatable,

reviewable,

not dependent on tribal knowledge,

not left to “any admin” (too vague),

not left to devs (devs may not have operational responsibility).

The correct responsible party is:
The correct responsible party is:

admin‑role, because break‑glass is an operational security mechanism, not a development mechanism.

Devs may assist, but they should not own the drill.

Next: “documented results.”

To be reviewer‑proof, documentation must be:

durable (lives in the repo),

inspectable (not ephemeral),

structured (not free‑form),

auditable (timestamp + actor),

reproducible (same format every year).

The best location is:
/test-evidence/breakglass/

consistent with your existing evidence directories

easy to review

easy to diff

easy to audit

Minimum documentation requirements:

Timestamp

Actor (admin account)

Steps performed

Outcome (success/failure)

Rotation confirmation performed

Audit log reference ID

Finally: the TODO(BREAKGLASS_DRILL_DOCS) has been outstanding since v1.11.0.
It should be resolved now — you have enough clarity to finalize it.

Conclusion
The annual break‑glass drill MUST be conducted by an admin‑role account.
Documented results MUST be stored in /test-evidence/breakglass/ and MUST include timestamp, actor, steps, outcome, and rotation confirmation.
The TODO(BREAKGLASS_DRILL_DOCS) SHOULD be resolved in this round.

---

### Q9 — Break-glass rotation confirmation: who, how, and is it audited?
§18 states: "Confirming rotation completion reactivates the enablement mechanism." The mechanism and actor for this confirmation are undefined.

**Problem**: "Confirming rotation completion" could mean: (a) a system-level detection that a new password hash is present in the DB, (b) a manual admin action in the UI or CLI, or (c) an out-of-band acknowledgment (e.g., a signed document). Without definition, an attacker who knows the CLI flag could attempt to assert rotation completion without actually rotating.

**Question**: What is the mechanism for confirming password rotation completion — system-detected (new hash present), an explicit admin/dev CLI command, or something else? Who (which role) may perform this confirmation? Must the confirmation generate an audit entry?
**Anwser**: Reasoning
Break‑glass is the highest‑risk authentication path in the entire system.
Therefore, rotation confirmation must be:

explicit (not inferred automatically)

role‑restricted (not anyone with CLI access)

audited (rotation is a security‑critical event)

tamper‑resistant (attacker cannot fake rotation completion)

Let’s evaluate the options:

(a) System‑detected (new hash present)
Too weak.

An attacker who knows the old password could rotate it to a new one and trick the system into thinking rotation is complete.

(b) Explicit admin/dev CLI or UI command
Strongest model.

Human‑verified rotation.

Allows audit logging.

Prevents attacker from bypassing rotation by simply changing the hash.

(c) Out‑of‑band acknowledgment
Overkill for most deployments.

Hard to automate.

Not testable in CI.

The correct constitutional stance is explicit human confirmation by a privileged role, with mandatory audit logging.

Conclusion
Rotation completion MUST be confirmed by an explicit admin/dev action (UI or CLI).
System‑detected hash changes are NOT sufficient.
Every rotation confirmation MUST generate an audit entry.
---

## §VIII — Privacy, PII Protection & Data Minimization

### Q10 — PII scan default scope: is there a default, and can admins set one?
§VIII states: "configured by the user at the start of each scan session — file paths only, metadata only, full content, or any combination." No default scope is defined.

**Problem**: If there is no default, users must actively choose a scope at the start of every session. This creates UX friction and may cause accidental under-scanning (user selects minimal scope to save time) or over-scanning (user selects full-content when they only need paths). Admins may want to configure a deployment-wide default scope (e.g., "full content scan required in regulated environments").

**Questions**:
- Is there a system default scan scope for new sessions (e.g., "file paths only" as the safest-fast default)?
- Can admins configure a deployment-wide default scan scope that users can deviate from, or is scope always fully user-controlled per session?
**Anwser**: Reasoning
No default = friction + inconsistent behavior.

User‑selected every time = error‑prone.

Admins in regulated environments need to enforce stricter defaults.

But users should still be able to override defaults unless the admin explicitly locks them.

Therefore:

There SHOULD be a system default.

Admins SHOULD be able to set a deployment‑wide default.

Users SHOULD be able to override it unless the admin marks it “mandatory.”

This mirrors enterprise DLP and compliance tools.

Conclusion
There MUST be a system default scan scope.
Admins MAY configure a deployment‑wide default.
Users MAY override it unless the admin marks the default as mandatory.
---

### Q11 — Mode display position relative to confirmation dialog
§VIII requires two things in sequence for irreversible anonymization:
1. "The selected mode MUST be clearly displayed to the user before execution begins."
2. The user must type a confirmation phrase AND click confirm.

**Problem**: The constitution does not specify whether the mode display must appear as a *distinct prior step* before the confirmation dialog, or whether displaying the mode *within* the confirmation dialog itself satisfies the requirement. These may produce different UX implementations.

**Question**: Must the anonymization mode be displayed before the confirmation dialog appears (as a distinct screen or step), or is displaying the mode prominently inside the confirmation dialog (alongside the typed phrase and confirm button) constitutionally sufficient?
**Anwser**: Reasoning
The constitution requires:

Mode must be displayed before execution begins.

Two‑step confirmation must occur.

It does not require a separate screen.
The key requirement is visibility, not sequence of screens.

If the mode is displayed prominently inside the confirmation dialog, the user sees it before clicking confirm.
This satisfies the requirement.

Forcing a separate step would over‑specify UX.

Conclusion
Displaying the mode prominently inside the confirmation dialog is constitutionally sufficient.
A separate prior screen is NOT required.
---

## §IX — File Validation & Content Integrity

### Q12 — Per-`open()` validation for the same file opened multiple times
§IX states: "Detection MUST precede every individual file `open()` call within any tool that reads or transforms file content sourced externally or from the user's filesystem."

**Problem**: Some tools may open the same external file multiple times within a single operation (e.g., reading a header block, then seeking back to read structured content, or a retry after a transient error). Running full signature detection on each `open()` call of the same file adds latency and may be unnecessary if the file has not changed.

**Question**: Does the per-`open()` validation requirement mean detection must run on *each individual `open()` call* regardless of whether the file was already validated earlier in the same operation, or is it sufficient to validate once per file per operation and cache the result for subsequent opens of the same path within that operation?
**Anwser**: Reasoning
The constitution says:

“Detection MUST precede every individual file open() call.”

But this is ambiguous for repeated opens of the same file within one operation.

Two interpretations:

Strict literal (validate every open)
Safe but wasteful.

Adds latency.

No additional security benefit if file hasn’t changed.

Per‑operation caching
Validate once per file per operation.

Cache result.

Revalidate only if file metadata changes (mtime, size, inode).

Matches antivirus and DLP patterns.

The correct constitutional stance is:
Security must not be reduced

Performance must not be unnecessarily degraded

Therefore:
validate once per file per operation, unless the file changes.

Conclusion
Validation MUST occur once per file per operation.
Subsequent opens of the same file MAY use a cached result unless the file has changed.
---

## §6 — Additional Constraints: Performance Baselines

### Q13 — "segments" wording and §IV / §6 wording consistency
§6 states: "UI main thread blocked < 100ms **segments**." §IV now states: "UI thread blocking MUST NOT reach or exceed 100ms."

**Two problems**:
1. The word "segments" in §6 is undefined: does it mean each individual uninterrupted blocking call must be below the threshold, or that the *total* time blocked within some measurement window must be below it?
2. §IV and §6 are now mathematically equivalent ("MUST NOT reach or exceed 100ms" = "< 100ms") but use different language, which creates unnecessary ambiguity about which phrasing is authoritative.

**Questions**:
- What does "segments" mean: each individual blocking call, each continuous blocked period, or cumulative blocking within a measurement unit (e.g., per frame)?
- Should §6 be updated to match §IV's wording ("MUST NOT reach or exceed 100ms") for consistency, since §6 is the "governing enforcement gate" per Round 7?
**Anwser**: Q13 — “segments” wording and consistency with §IV
Reasoning
Two issues:

1. What does “segments” mean?
Three possible interpretations:

individual blocking calls

continuous blocked periods

cumulative blocking time per frame

The only testable and reviewer‑proof interpretation is:

each continuous blocked period

This avoids loopholes like splitting a 300ms block into three 100ms calls.

2. Wording mismatch between §IV and §6
§IV: “MUST NOT reach or exceed 100ms”
§6: “blocked < 100ms segments”

These are mathematically equivalent but linguistically inconsistent.

Since §6 is the enforcement gate, §6 should adopt §IV’s clearer wording.

Conclusion
“Segments” means each continuous blocked period.
§6 SHOULD be updated to match §IV’s wording:
“UI thread blocking MUST NOT reach or exceed 100ms.”
---

## §7 — Additional Constraints: Accessibility

### Q14 — Touch/pointer target size: logical pixels or physical device pixels?
§7 requires: "minimum interactive control touch/pointer target size MUST be ≥ 44 × 44 px."

**Problem**: On high-DPI displays (e.g., Windows 200% scaling), "44 px" could mean 44 logical device-independent pixels (the standard for accessibility guidelines like WCAG 2.1, Apple HIG, Material Design) or 44 physical screen pixels (which at 200% DPI would appear as only 22 logical pixels — too small). The distinction matters significantly for implementation.

**Question**: Are the 44 × 44 px target sizes specified in logical (device-independent) pixels, consistent with WCAG 2.1 SC 2.5.8 and major HIG standards? Or are they physical device pixels?
**Anwser**: Q14 — Touch/pointer target size: logical vs physical pixels
Reasoning
WCAG, Apple HIG, Material Design, and Microsoft Fluent all define touch targets in logical (device‑independent) pixels, not physical pixels.

Physical pixels vary wildly with DPI scaling.

Using physical pixels would break accessibility on high‑DPI displays.

Therefore:
44×44 MUST be logical pixels.

Conclusion
The 44×44 px minimum refers to logical (device‑independent) pixels, not physical pixels.
---

### Q15 — Accessible label requirement: tooltip vs Qt accessibility API
§7 requires: "all interactive controls MUST carry accessible labels (Qt accessibility text or equivalent) for screen reader compatibility."

**Problem**: "Qt accessibility text" likely refers to `QWidget::setAccessibleName()` / `setAccessibleDescription()`. However, "or equivalent" is undefined. A tooltip set via `QWidget::setToolTip()` is visually similar but does not expose content through the Qt accessibility tree in the same way. Some developers may assume a tooltip satisfies the requirement.

**Questions**:
- Does "accessible label" specifically require using the Qt accessibility API (`setAccessibleName()` or equivalent), or is a tooltip sufficient?
- What does "or equivalent" mean — another Qt mechanism, a platform accessibility API, or any label-like text attached to the control?
**Anwser**: 
---

## §14 — Additional Constraints: Authentication Data Handling

### Q16 — Can any account transition to `breakglass` status?
§14 states: "When an account transitions out of `active` (e.g., to `suspended` or `breakglass`)..." This parenthetical implies a regular user account can transition to `breakglass` status.

**Problem**: §19 defines `breakglass` as the permanent default status for break-glass emergency accounts (provisioned by the system with `is_breakglass = true`). It is the initial and permanent status of `dev_breakglass` and `admin_breakglass`. No text in the constitution defines `breakglass` as a status that a regular `user`, `admin`, or `dev` account can ever reach. The §14 parenthetical may be misleading.

**Question**: Can a regular (non-break-glass) account ever have `account_status = breakglass`? If not, should the §14 parenthetical be corrected to remove `breakglass` from the list of statuses a regular account transitions to (leaving only "e.g., to `suspended`")?
**Anwser**: Q16 — Can any account transition to breakglass status?
Reasoning
§14 says:

“When an account transitions out of active (e.g., to suspended or breakglass)…”

This implies that any account could transition to breakglass.
But §19 defines:

breakglass is the permanent default status of special emergency accounts

These accounts have is_breakglass = true

They are provisioned by the system

They are not normal user/admin/dev accounts

They are not created or modified through normal lifecycle flows

Therefore:

A normal account must never transition to breakglass.

breakglass is not a lifecycle state; it is a special account class.

The §14 parenthetical is misleading and should be corrected.

The correct lifecycle transitions for normal accounts are:

active → suspended

active → deleted (if allowed)

active → locked (if blocked by login attempts)

never → breakglass

Break‑glass accounts:

start in breakglass

remain in breakglass

never transition to or from other statuses

are only “enabled” or “disabled” via the break‑glass enablement mechanism, not via account_status

Conclusion
No — a regular account can NEVER transition to breakglass.
The §14 parenthetical is incorrect and SHOULD be corrected to remove breakglass from the example list.
---

## §15 — Additional Constraints: Credential Reset & Account Lifecycle

### Q17 — Breached password denylist: external API, local bundle, or implementation-defined?
§15 states: "reject breached passwords via denylist when network connectivity allows."

**Problem**: The source of the denylist is not specified. Options include: (a) an external real-time API (e.g., HIBP k-anonymity API), (b) a locally bundled static database, (c) implementation-defined. Each has different privacy implications (k-anonymity API leaks a hash prefix; local bundle is always stale), maintenance requirements, and deployment constraints.

**Question**: Is the denylist sourced from an external online service, a locally bundled database (shipped with the application), or is the source implementation-defined? If implementation-defined, are there any constitutional constraints (e.g., must use k-anonymity to preserve privacy if an external API is used)?
**Anwser**: Q17 — Breached password denylist: external API, local bundle, or implementation‑defined?
Reasoning
There are three possible denylist sources:

(a) External API (e.g., HIBP k‑anonymity)
Pros: always up‑to‑date

Cons: privacy implications (hash prefix leakage), requires network, may violate offline‑first deployments

(b) Local bundled database
Pros: privacy‑preserving, offline‑capable

Cons: stale unless updated regularly

(c) Implementation‑defined
Pros: flexible

Cons: too vague unless constrained

The constitution must guarantee:

privacy (no raw password or full hash ever leaves the device)

offline functionality

portability

testability

Therefore:

The source SHOULD be implementation‑defined, but with constitutional constraints:

If external API is used → MUST use k‑anonymity or equivalent privacy‑preserving protocol

If local bundle is used → MUST be periodically refreshable

MUST NOT send full password or full hash to any external service

MUST work offline (fallback to local denylist)
Conclusion
**The denylist source is implementation‑defined, but MUST meet these constraints:

MUST support offline operation via a local denylist.

If an external API is used, it MUST use a privacy‑preserving protocol (e.g., k‑anonymity).

Full passwords or full hashes MUST NEVER be transmitted externally.**
---

## §21 — Additional Constraints: Theme Security

### Q18 — Theme backup granularity: all-presets snapshot vs per-changed-preset
§21 states: "Theme backups MUST be created before applying any system-wide theme change; at least the five most recent system-wide theme backups MUST be retained."

**Problem**: If there are ten system-wide presets and an admin changes one of them, the constitution does not define whether "a backup" means:
- **(a)** A full snapshot of all ten system-wide presets at the moment of the change (restoring to this backup restores all presets to their pre-change state), or
- **(b)** A per-preset backup of only the modified preset (restoring brings that one preset back, leaving others unchanged).

These have different storage implications and different restore semantics. "Five most recent" is also ambiguous: five most recent full snapshots, or five most recent changes per preset?

**Question**: Does "a theme backup" mean a full snapshot of all current system-wide presets, or a per-preset record of the changed preset only? And does "five most recent" count full snapshots or per-preset change records?
**Anwser**: Reasoning
Two models:

(a) Full snapshot of all presets
Pros: simple restore semantics

Cons: heavy storage, unnecessary duplication

(b) Per‑preset backup
Pros: efficient, minimal storage

Cons: restore semantics become per‑preset only

The constitution says:

“Theme backups MUST be created before applying any system‑wide theme change.”

A “system‑wide theme change” is a global state change, not a per‑preset change.
Therefore, the backup should reflect the entire system‑wide theme state, not just the modified preset.

This ensures:

restoring a backup returns the system to a consistent state

admins can undo a bad change even if multiple presets were affected indirectly

retention (“five most recent”) is unambiguous: five snapshots

Conclusion
A theme backup is a full snapshot of all system‑wide presets.
The “five most recent” refers to the five most recent full snapshots.
---

## §22 — Additional Constraints: File Validator Integration

### Q19 — Repair instruction content: implementation-defined or prescribed?
§22 states: "the tool MUST present a hard error dialog clearly explaining the signature database corruption and the steps required to repair it."

**Problem**: "The steps required to repair it" implies specific, actionable instructions. These could vary significantly depending on how the signature database is packaged (bundled binary, downloaded file, user-installed package). If the steps are entirely implementation-defined, the constitution's requirement is unverifiable in a PR review — any error dialog text could claim to satisfy it.

**Question**: Are the "steps required to repair it" constitutionally required to include specific minimum information (e.g., the file path of the corrupted database, a command or UI path to reinitialize it), or is the content of the repair instructions fully implementation-defined? Should the constitution add a minimum content requirement (e.g., "MUST identify the corrupted file and the resolution action")?
**Anwser**: Reasoning
The constitution says:

“MUST present a hard error dialog clearly explaining the corruption and the steps required to repair it.”

If “steps required” is implementation‑defined, a PR author could write:

“Please repair the database.”

…which is meaningless but technically “steps.”

To be testable and reviewer‑proof, the constitution must require minimum content:

identify the corrupted file

describe the required action (e.g., “reinitialize”, “redownload”, “replace”)

provide the UI path or CLI command

avoid implementation‑specific jargon

This ensures:

clarity

consistency

auditability

user empowerment

Conclusion
**The repair instructions MUST include at minimum:

The path or identifier of the corrupted signature database,

The required resolution action (e.g., reinitialize, redownload),

The UI path or CLI command to perform the repair.
Additional details are implementation‑defined.**
---

## Development Workflow

### Q20 — "Security-sensitive code" and "performance-critical paths": who decides?
§DW §3 requires minimum 2 maintainer approvals for: "destructive engine changes, security-sensitive code, tool discovery system changes, or performance-critical paths."

**Problem**: "Destructive engine changes" and "tool discovery system changes" are objective categories (identifiable by which files are modified). But "security-sensitive code" and "performance-critical paths" are subjective judgments with no defined criteria. A developer may disagree with a reviewer about whether a change qualifies.

**Question**: Who has final authority to classify a PR as touching "security-sensitive code" or "performance-critical paths" — the PR author (self-declaration), any one maintainer, or does the CI system have a list of designated security/performance paths that triggers the 2-reviewer requirement automatically? Should the constitution specify that any maintainer may elevate a PR to 2-reviewer status, or that only the PR author can waive the classification?
**Anwser**: Reasoning
The categories “security‑sensitive” and “performance‑critical” are subjective.
To avoid ambiguity, the constitution must define:

who can classify a PR as requiring 2 maintainers

whether the classification can be overridden

whether CI can enforce it

Three models:

(a) PR author self‑declares
Too weak; authors may under‑classify.

(b) Any maintainer may elevate a PR
Strong, simple, reviewer‑friendly.

Prevents under‑classification.

Mirrors common open‑source governance.

(c) CI auto‑detects based on file paths
Useful but incomplete; cannot detect semantic changes.

The best model is a hybrid:

CI enforces a baseline list of known sensitive paths

Any maintainer may elevate a PR to 2‑reviewer status

PR author cannot unilaterally downgrade the classification

Conclusion
Any maintainer may classify a PR as touching security‑sensitive or performance‑critical code, triggering the 2‑maintainer requirement.
CI MAY enforce additional path‑based triggers.
PR authors cannot override or waive this classification.
---

*Total questions: 20 | Document version: Round 8 draft | Based on constitution v1.12.0*
