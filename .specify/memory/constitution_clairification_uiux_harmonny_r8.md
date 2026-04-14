# Constitution Clarification — Ambiguity Scan Round 8

**Source**: `constitution.md` v1.13.0
**Round**: 8
**Date**: 2026-04-01

This document records all newly identified ambiguities, inconsistencies, and
unclear statements found in `constitution.md` v1.13.0 after applying all Round
7 clarifications. Questions are ordered by the section they affect. Three areas
were specifically requested for inclusion:

1. **"User-visible" vs "user-discoverable"** — terms used in multiple sections
   but not formally defined.
2. **"System-wide theme change"** — phrase used in §21 but not formally
   defined, leaving the backup trigger ambiguous.
3. **"Offline-capable MFA"** — the constitution requires it but does not define
   which TOTP/FIDO2 variants or configurations are acceptable.

---

## Glossary & Definitions (New Section Proposed)

### Q1 — "User-visible" vs "user-discoverable": undefined terms used across multiple sections

The constitution uses two related but distinct terms across several sections
without formally defining either:

- **"user-visible"** appears explicitly in:
  - §VI Portability: *"present a user-visible summary of skipped items"*
  - §15: *"a user-visible warning MUST be emitted"*
  - §DW §6: *"user-visible behavior"*
- **"user-discoverable"** was the original dry-run term (replaced in Round 7 by
  "visible UI element") but could recur in future amendments; no definition
  was ever codified.

**Problem**: Without formal definitions, a reviewer cannot determine whether
a warning placed in a log panel, a notification-tray badge, a collapsible
sidebar, or a modal satisfies a "user-visible" requirement. The terms are
qualitatively different from each other — "visible" implies passive observation
requires no action; "discoverable" implies navigation is acceptable. This
distinction matters for testability in PR reviews and CI gates.

**Questions**:
- Should the constitution add a Glossary section defining both terms?
- Specifically, does **"user-visible"** mean information MUST appear in the
  active foreground UI without requiring any navigation or dismissal of
  another view — i.e., the user cannot reasonably miss it?
- Is a status bar, notification badge, or collapsible panel sufficient for
  "user-visible," or does it require a modal or focused alert surface?
- Should **"user-discoverable"** (for future use) be defined as "reachable
  through at most one navigation step from the active UI state, without
  consulting external documentation"?
- Should the constitution consolidate toward a single term, or keep both with
  distinct definitions?

**Anwser**: Takeaway
Yes — the constitution should add a Glossary, and both terms should be defined distinctly.
User‑visible should mean foreground, cannot‑reasonably‑be‑missed.
User‑discoverable should mean reachable with ≤1 navigation step, no external docs.
They serve different governance purposes, so they should both remain, not be collapsed.

1. Why a Glossary is necessary
The moment a term appears in multiple sections — especially enforcement sections (§VI, §15, DW §6) — it becomes part of the test surface. Undefined terms create:

inconsistent reviewer interpretations

CI gates that cannot be deterministically implemented

UI/UX contradictions across apps

loopholes (“technically it’s visible in the logs…”)

A Glossary is the right place to anchor these definitions because it:

centralizes meaning

avoids redefining terms in each section

supports future amendments without rewriting the constitution

Recommendation: Add a new §G Glossary with normative definitions.

2. Definition of “user-visible”
Yes — it should mean foreground, non-ignorable, and requiring zero navigation.

A governance-grade definition should be:

User-visible — Information that appears in the active foreground UI without requiring navigation, expansion, or interaction. A reasonable user cannot proceed without noticing it.

This implies:

Allowed: modal dialogs, inline error banners, toast notifications that appear automatically in the main viewport

Not allowed: logs, collapsible panels, notification badges, status bar icons, hidden sidebars, tooltips that require hover

Why this strictness matters
It ensures warnings/errors cannot be silently ignored

It makes CI testability deterministic (e.g., screenshot diffing, DOM presence checks)

It aligns with accessibility expectations (screen readers detect foreground alerts)

Your specific question
Is a status bar, notification badge, or collapsible panel sufficient?

No.  
Those are discoverable, not visible.
They require user action or prior knowledge.

3. Definition of “user-discoverable”
Your proposed definition is almost perfect. I’d refine it slightly:

User-discoverable — Information reachable within one navigation step from the active UI state, without external documentation, and without requiring knowledge of hidden or advanced features.

This covers:

clicking a tab

opening a sidebar

selecting a menu item

expanding a single accordion

And excludes:

multi-level menus

logs

developer consoles

config files

documentation pages

This definition is ideal for dry-run summaries, optional diagnostics, and non-blocking metadata.

4. Should the constitution consolidate to one term?
No — they serve different governance functions.

Term	Purpose	Enforcement Strength
User-visible	Mandatory warnings, errors, skipped items, blocking conditions	Strong (MUST)
User-discoverable	Optional diagnostics, dry-run details, advanced info	Medium (SHOULD)
If you collapse them, you either:

weaken critical warnings, or

overburden the UI with intrusive alerts

Keeping both terms — with crisp definitions — gives you the flexibility to design UX that is both compliant and humane.

5. Proposed Glossary entries (ready to paste into the constitution)
§G.1 — User-visible
User-visible — Information that appears automatically in the active foreground UI without requiring navigation, expansion, or interaction. A reasonable user cannot proceed without noticing it. Examples include modal dialogs, inline banners, and automatic toast notifications. Status bars, badges, logs, and collapsible panels do not satisfy this requirement.

§G.2 — User-discoverable
User-discoverable — Information reachable within one navigation step from the active UI state, without consulting external documentation or advanced features. Examples include a sidebar, a single-level menu, or a tab switch. Multi-level navigation, logs, and developer tools do not satisfy this requirement.

6. Recommended constitutional changes
To make this airtight:

Add §G Glossary with the two definitions above

Update §VI, §15, and DW §6 to reference the glossary term explicitly

Add a reviewer note:

“CI MUST verify user-visible elements via DOM presence in the active viewport.”

Add a UX note:

“User-visible warnings MUST NOT be suppressible by default.”

This closes loopholes and ensures consistent implementation across all apps.
📘 Amendment Patch: §VI — Portability & Skipped‑Item Reporting
§VI — Portability and Skipped‑Item Reporting (Amended)
§VI.1 — Skipped‑Item Summary (User‑Visible)
Any operation that skips items during dry‑run or real execution MUST present a user‑visible summary of all skipped items, as defined in §G.1.
This summary:

MUST appear automatically in the active foreground UI

MUST NOT require navigation, expansion, or interaction

MUST enumerate each skipped item and the reason for skipping

§VI.2 — Integration with Dry‑Run (§II)
For all side‑effect operations:

dry‑run output MUST include the skipped‑item summary defined in §VI.1

skipped items MUST be listed separately from intended changes

§VI.3 — Deterministic Reviewability
The skipped‑item summary MUST be structured such that:

reviewers can verify its presence via DOM inspection

CI can detect its absence or misclassification

the summary is consistent across all apps in the suite

📘 Amendment Patch: §15 — Warning Emission Requirements
§15 — Warning Emission Requirements (Amended)
§15.1 — User‑Visible Warning Requirement
Whenever an operation encounters a condition that may affect correctness, safety, or expected behavior, a user‑visible warning (as defined in §G.1) MUST be emitted.

A user‑visible warning:

MUST appear automatically in the active foreground UI

MUST NOT require navigation, expansion, or interaction

MUST clearly describe the condition and its implications

§15.2 — Non‑Blocking Warnings
User‑visible warnings MAY be non‑blocking unless the condition escalates to a destructive operation, in which case §II.2 applies.

§15.3 — Reviewability
Warnings MUST be implemented in a manner that allows reviewers and CI to verify:

presence of the warning

correct classification as user‑visible

correct placement in the foreground UI

📘 Amendment Patch: DW §6 — User‑Visible Behavior in Dry‑Run Workflows
DW §6 — User‑Visible Behavior (Amended)
DW §6.1 — Foreground Presentation
All dry‑run workflows MUST present their results using user‑visible behavior as defined in §G.1.
This includes:

intended changes

skipped items

warnings

any conditions requiring user attention

DW §6.2 — Discoverable Supplementary Detail
Additional diagnostic or verbose information MAY be provided through user‑discoverable surfaces (as defined in §G.2), such as:

a single‑step sidebar

a single‑level menu

a single accordion expansion

Such supplementary detail MUST NOT replace the user‑visible elements required in §DW §6.1.

DW §6.3 — Consistency Across Apps
All apps in the suite MUST implement dry‑run UI surfaces in a manner consistent with the definitions of user‑visible and user‑discoverable, ensuring predictable reviewer and CI evaluation.

📘 Notes on Cross‑References
These amendments assume the Glossary includes:

§G.1 — User‑visible

§G.2 — User‑discoverable

§G.3 — Side effect

§G.4 — Destructive operation

Everything now cleanly references those definitions, eliminating ambiguity and making UI/UX obligations fully testable.
---

## §II — Safety & Data Integrity

### Q2 — "Side effects" scope: which operations trigger dry-run and confirmation requirements?

§II requires "All operations with side effects MUST support dry-run simulation."
The term "side effect" is not formally defined.

**Problem**: The correct scope of dry-run coverage depends entirely on what
counts as a side effect. The following scenarios are genuinely ambiguous:

1. Reading a file modifies its filesystem access timestamp — a side effect, but
   one the user may not consider meaningful.
2. Writing to RFU's internal index or audit log when processing user files —
   an internal side effect, not a user-facing one.
3. Network operations that check availability or fetch metadata — external
   side effects.
4. Metadata writes (EXIF, tags) that modify a file without deleting it — a
   file mutation but not destruction.

A PR author and a reviewer may classify the same operation differently,
making dry-run coverage an uncheckable gate.

**Questions**:
- Should the constitution formally define "side effect" for dry-run and
  confirmation purposes? Is it:
  - **(a)** Any operation that modifies files, directories, or metadata
    visible to the user (user-facing filesystem changes only)?
  - **(b)** Any persistent write operation, including to RFU's internal
    database, index, or audit log?
  - **(c)** Only irreversible or hard-to-reverse operations (delete,
    overwrite, secure wipe, anonymization)?
- Should a formal classification taxonomy be added — e.g., a two-tier system
  distinguishing "side-effect operations" (dry-run required) from "destructive
  operations" (confirmation also required)?

**Anwser**: Takeaway
Yes — the constitution must formally define side effect, and it must adopt a two‑tier classification:

Tier 1: Side‑effect operations → dry‑run required

Tier 2: Destructive operations → dry‑run + explicit confirmation required

The correct definition is:
A side effect is any persistent change to user‑visible state, including file mutations, metadata writes, network writes, or external system changes — but excluding internal RFU bookkeeping.

This resolves all four ambiguous scenarios cleanly.

1. Why “side effect” must be formally defined
Right now, §II’s requirement (“All operations with side effects MUST support dry‑run simulation”) is unenforceable because:

reviewers cannot agree on what counts

PR authors can unintentionally omit dry‑run coverage

CI cannot detect missing dry‑run branches

apps in the suite will diverge in behavior

A constitutional definition is required to make dry‑run coverage reviewer‑proof and testable.

2. Recommended definition of “side effect”
You need a definition that is:

broad enough to catch all user‑impacting changes

narrow enough to avoid forcing dry‑run on internal bookkeeping

testable in CI

consistent across all apps

Proposed definition (ready for Glossary §G)
Side effect — Any persistent change to user‑visible state, including creation, deletion, modification, or metadata mutation of files, directories, or external resources. Internal RFU bookkeeping (indexes, caches, audit logs) is not considered a side effect.

This definition intentionally excludes internal writes because:

they do not affect user data

they are reversible

they are implementation details

requiring dry‑run for them would create noise and complexity

3. Classification taxonomy (two‑tier system)
This is the key to making the governance enforceable.

Tier 1 — Side‑effect operations (dry‑run required)
These operations change user‑visible state but are not inherently destructive.

Examples:

writing EXIF or tag metadata

renaming files

moving files

creating directories

downloading thumbnails or metadata to user storage

network writes that modify remote state

Dry‑run must show:

what would change

which files/resources would be touched

a user‑visible summary of skipped items (§VI)

Tier 2 — Destructive operations (dry‑run + confirmation required)
These operations are irreversible or hard to reverse.

Examples:

delete

overwrite

secure wipe

anonymization

lossy transformations

irreversible compression

destructive normalization

Confirmation must be:

user-visible (per Q1 definition)

blocking

explicit

This gives you a clean separation:

Operation	Tier	Dry-run	Confirmation
Write EXIF metadata	Side-effect	Yes	No
Move/rename	Side-effect	Yes	No
Delete	Destructive	Yes	Yes
Overwrite	Destructive	Yes	Yes
Internal index write	Not a side effect	No	No
Read file (touches access timestamp)	Not a side effect	No	No
4. Applying the taxonomy to your ambiguous scenarios
Let’s resolve your four examples explicitly.

1. Reading a file updates access timestamp
Not a side effect.  
Reason: not user-visible, not meaningful, not persistent in a user-facing sense.

2. Writing to RFU’s internal index or audit log
Not a side effect.  
Reason: internal, implementation detail, not user-visible.

3. Network operations that modify external state
Side effect (Tier 1) unless destructive.
Reason: persistent change to user-visible external resources.

4. Metadata writes (EXIF, tags)
Side effect (Tier 1)  
Reason: persistent mutation of user files, but reversible and non-destructive.

5. Should the constitution adopt the two-tier system?
Yes — absolutely.  
It is the only way to:

avoid over-alerting users

avoid under-protecting destructive operations

give reviewers deterministic criteria

allow CI to enforce dry-run coverage

keep UX consistent across apps

Without this taxonomy, every PR becomes a philosophical debate.

6. Proposed constitutional text (ready to paste)
§G.3 — Side effect
Side effect — Any persistent change to user-visible state, including creation, deletion, modification, or metadata mutation of files, directories, or external resources. Internal RFU bookkeeping (indexes, caches, audit logs) is not considered a side effect.

§G.4 — Destructive operation
Destructive operation — A side-effect operation that is irreversible or hard to reverse, including deletion, overwrite, secure wipe, anonymization, or lossy transformation.

§II.1 — Dry-run requirement
All side-effect operations MUST support dry-run simulation. Dry-run MUST enumerate all intended changes and MUST NOT perform them.

§II.2 — Confirmation requirement
All destructive operations MUST additionally require explicit user-visible confirmation before execution.

Follow-up for you
Would you like me to draft the exact amendment patches for §II and §VI so they reference these new definitions cleanly and consistently across the constitution?

yes please draft the exact amendment patches for §II and §VI so they reference these new definitions cleanly and consistently across the constitution
Absolutely — here are the exact, reviewer‑ready amendment patches for §II and §VI, written in constitutional language, referencing the new Glossary definitions (§G.3 “Side effect” and §G.4 “Destructive operation”).
These patches are designed to drop cleanly into your governance document with zero ambiguity and full CI‑testability.

📘 Amendment Patch: §II — Dry‑Run & Confirmation Requirements
Below is the full replacement text for §II, incorporating the new definitions and clarifying obligations.

§II — Dry‑Run Simulation and Confirmation Requirements (Amended)
§II.1 — Dry‑Run Requirement (Side‑Effect Operations)
All side‑effect operations (as defined in §G.3) MUST support dry‑run simulation.
Dry‑run execution:

MUST enumerate all intended changes to user‑visible state

MUST NOT perform any such changes

MUST present a user-visible summary of all intended modifications and all skipped items

MUST be available through the same interface as the real operation

§II.2 — Confirmation Requirement (Destructive Operations)
All destructive operations (as defined in §G.4) MUST require explicit user-visible confirmation prior to execution.
Confirmation:

MUST block execution until the user explicitly approves

MUST appear in a foreground, non‑dismissed UI surface

MUST summarize the irreversible consequences of the operation

MUST list all affected items

§II.3 — Internal Operations Excluded
Internal RFU bookkeeping — including indexes, caches, audit logs, and other non‑user‑visible persistent writes — MUST NOT be classified as side‑effect operations and MUST NOT require dry‑run or confirmation.

§II.4 — CI Enforcement
CI MUST verify that:

all side‑effect operations expose a dry‑run path

all destructive operations require user-visible confirmation

no internal bookkeeping is incorrectly classified as a side effect

📘 Amendment Patch: §VI — Portability & Skipped‑Item Reporting
§VI already references “user-visible summary,” so this patch aligns it with the new definitions and clarifies the dry‑run interaction.

§VI — Portability and Skipped‑Item Reporting (Amended)
§VI.1 — Skipped‑Item Reporting
Any operation that skips items during dry‑run or real execution MUST present a user-visible summary of all skipped items.
This summary:

MUST appear automatically in the active foreground UI

MUST NOT require navigation, expansion, or interaction to be seen

MUST identify each skipped item and the reason for skipping

§VI.2 — Integration with Dry‑Run (§II)
For all side‑effect operations:

dry‑run output MUST include the skipped‑item summary defined in §VI.1

skipped items MUST be listed separately from intended changes

§VI.3 — Deterministic Reviewability
The skipped‑item summary MUST be structured such that:

reviewers can verify its presence via DOM inspection

CI can detect its absence or misclassification

the summary is consistent across all apps in the suite

📘 Cross‑References to Glossary (New §G.3 and §G.4)
These patches assume the following glossary entries exist:

§G.3 — Side effect
Any persistent change to user-visible state, including creation, deletion, modification, or metadata mutation of files, directories, or external resources. Internal RFU bookkeeping (indexes, caches, audit logs) is not considered a side effect.

§G.4 — Destructive operation
A side-effect operation that is irreversible or hard to reverse, including deletion, overwrite, secure wipe, anonymization, or lossy transformation.

---

### Q3 — Headless HMAC token: key material, algorithm, validity period, and rotation

§II permits a "cryptographically signed HMAC token attached to the invocation
in headless mode" as the alternative to interactive confirmation for destructive
operations. No further specification is given.

**Problem**: Five attributes of this token are constitutionally unspecified:

1. **Algorithm** — HMAC-SHA256, HMAC-SHA512, or implementation-defined?
2. **Key material** — where does the signing key reside (system keystore,
   operator secret, per-deployment config)? A key in a config file or
   environment variable is weaker than a hardware-stored key.
3. **Validity period** — a token with no expiry could be captured and
   replayed indefinitely to authorize destructive operations.
4. **Single-use vs multi-use** — can the same token authorize multiple
   operations in a session, or must each destructive operation use a fresh
   token?
5. **Audit trail** — must token issuance and use be recorded in the audit log?

Without these constraints, the headless token mechanism could be trivially
weaker than interactive confirmation.

**Questions**:
- Should a minimum HMAC algorithm be prescribed (e.g., HMAC-SHA256)?
- Should the key storage location be constitutionally constrained (e.g., MUST
  NOT reside in a plaintext config file or environment variable in production)?
- What is the maximum token validity period?
- Must each token be single-use (one destructive operation per token)?
- Must token issuance and redemption each generate an audit entry?

**Anwser**: akeaway
Yes — the constitution must prescribe:

a minimum algorithm (HMAC‑SHA256)

secure key storage (MUST NOT be plaintext config/env in production)

a strict validity period (≤ 5 minutes)

single‑use tokens (one destructive operation per token)

mandatory audit entries for issuance and redemption

This makes the headless token mechanism cryptographically sound, non‑replayable, and fully auditable.

1. Algorithm
Prescribe a minimum: HMAC‑SHA256
This is the right balance of:

security

portability

availability across all languages and platforms

Recommendation (constitutional):

The headless confirmation token MUST be an HMAC using SHA‑256 or stronger (e.g., SHA‑512). Weaker algorithms MUST NOT be used.

This prevents implementers from choosing MD5, SHA‑1, or “whatever the library defaults to.”

2. Key Material
This is the most important part — and the most dangerous if left unspecified.

Constitutional requirement:
The HMAC signing key MUST be stored in a secure system keystore or hardware‑backed secret store.
The key MUST NOT reside in plaintext configuration files, environment variables, or source code in production deployments.

This allows:

OS keyrings

TPM‑backed secrets

cloud KMS (AWS KMS, Azure Key Vault, GCP KMS)

hardware tokens (YubiHSM, HSM modules)

And forbids:

.env files

YAML configs

Docker environment variables

plaintext secrets in CI

This is the correct security posture for destructive‑operation authorization.

3. Validity Period
Replay attacks are the biggest risk.
A token with no expiry is effectively a skeleton key.

Constitutional requirement:
A headless HMAC token MUST include an embedded timestamp and MUST NOT be valid for more than 5 minutes from issuance.

Why 5 minutes?

long enough for automation

short enough to prevent replay

aligns with industry norms (AWS STS, GitHub OIDC, etc.)

If you want to be stricter, 2 minutes is also defensible — but 5 minutes is the sweet spot.

4. Single‑Use vs Multi‑Use
This is where most systems get sloppy.
Multi‑use tokens are replayable by definition.

Constitutional requirement:
Each headless HMAC token MUST be single‑use.
A token MAY authorize exactly one destructive operation.
After redemption, the token MUST be invalidated and MUST NOT be accepted again.

This prevents:

replay

batch deletion without explicit intent

“oops, the script ran twice” disasters

It also makes audit logs deterministic.

5. Audit Trail
This is essential for governance, forensics, and reviewer trust.

Constitutional requirement:
Both token issuance and token redemption MUST generate audit log entries.
Audit entries MUST include:
– timestamp
– operation name
– token identifier (non‑sensitive hash)
– caller identity
– success/failure status

This ensures:

traceability

accountability

non‑repudiation

compliance with §VI and §II

Putting it all together — Proposed Constitutional Text (ready to paste)
§II.X — Headless HMAC Token Requirements (New Section)
§II.X.1 — Algorithm  
Headless confirmation tokens MUST be implemented as HMACs using SHA‑256 or stronger. Weaker algorithms MUST NOT be used.

§II.X.2 — Key Storage  
The HMAC signing key MUST be stored in a secure system keystore or hardware‑backed secret store.
The key MUST NOT reside in plaintext configuration files, environment variables, or source code in production deployments.

§II.X.3 — Token Structure and Validity  
Each token MUST embed a timestamp and MUST NOT be valid for more than five (5) minutes from issuance.

§II.X.4 — Single‑Use Requirement  
Each token MUST be single‑use. A token MAY authorize exactly one destructive operation. After redemption, the token MUST be invalidated.

§II.X.5 — Audit Logging  
Token issuance and token redemption MUST each generate an audit entry containing:
– timestamp
– operation name
– token identifier (non‑sensitive hash)
– caller identity
– success/failure status

§II.X.6 — Equivalence to Interactive Confirmation  
A valid headless HMAC token MUST be treated as equivalent to interactive user-visible confirmation for the purposes of §II.2.

Please add or Referance the folling points:
1. Reviewer checklist for HMAC token implementations
A. Algorithm

Minimum algorithm:  
Check: Implementation uses HMAC with SHA‑256 or stronger (e.g., SHA‑512).
Fail if: MD5, SHA‑1, or unspecified/default MAC is used.

Library usage:  
Check: Uses a well‑maintained crypto library, not a homegrown HMAC implementation.

B. Key material & storage

Secure store:  
Check: Signing key is loaded from a system keystore, hardware‑backed store, or cloud KMS.
Fail if: Key is in plaintext config, .env, source code, or Docker env in production.

Separation of environments:  
Check: Production keys are distinct from dev/test keys and not checked into version control.

Key rotation support:  
Check: Implementation supports key rotation (e.g., key IDs, multiple active keys during rotation).

C. Token structure

Timestamp embedded:  
Check: Token payload includes an issuance timestamp (or expiry) that is part of the signed data.

Operation binding:  
Check: Token is bound to a specific operation (name/ID) and, ideally, to a specific resource set.
Fail if: Same token can authorize arbitrary destructive operations.

Caller identity binding:  
Check: Token includes caller identity or context (e.g., service account, pipeline ID).

D. Validity period

Max lifetime:  
Check: Code enforces a maximum validity of ≤ 5 minutes from issuance.
Fail if: No expiry, or expiry > 5 minutes, or only “best effort” logging without enforcement.

Clock handling:  
Check: Implementation tolerates small clock skew but still enforces hard upper bound.

E. Single‑use semantics

One token → one destructive operation:  
Check: After successful redemption, token is marked as used and cannot be reused.
Fail if: Same token can be replayed for multiple destructive calls.

Idempotency vs replay:  
Check: If idempotency is supported, it’s explicit and still logged; replay is not silently accepted.

F. Audit logging

Issuance log:  
Check: Issuance creates an audit entry with timestamp, caller, operation, and token identifier (non‑sensitive hash).

Redemption log:  
Check: Redemption creates an audit entry with timestamp, caller, operation, token identifier, and success/failure.

No sensitive leakage:  
Check: Full token or raw key material is never logged.

G. Equivalence to interactive confirmation

Policy alignment:  
Check: Wherever interactive confirmation is required, headless mode only proceeds with a valid HMAC token that meets all above constraints.

2. CI enforcement spec
Think of this as “what CI must prove” via tests or static checks.

A. Static checks

Algorithm enforcement:  
Test: Scan code/config to ensure only approved HMAC algorithms (SHA‑256+) are used for headless tokens.

Key source enforcement:  
Test: Disallow references to token signing keys in config files, .env, or source constants in production builds.

B. Unit/integration tests

Expiry tests:

Test 1: Token with timestamp now → accepted.

Test 2: Token older than 5 minutes → rejected.

Test 3: Token with future timestamp beyond skew window → rejected.

Single‑use tests:

Test 4: First redemption of a valid token → succeeds.

Test 5: Second redemption of the same token → fails with explicit “already used” or equivalent.

Operation binding tests:

Test 6: Token issued for Operation A used on Operation A → accepted.

Test 7: Same token used on Operation B → rejected.

Caller binding tests (if applicable):

Test 8: Token used by intended caller → accepted.

Test 9: Token used by different caller → rejected.

C. Audit logging tests

Issuance logging:

Test 10: Issuing a token writes an audit entry with: timestamp, caller, operation, token identifier.

Test 11: Audit entry does not contain raw token or key.

Redemption logging:

Test 12: Successful redemption logs: timestamp, caller, operation, token identifier, success.

Test 13: Failed redemption (expired, wrong op, replay) logs: timestamp, caller, operation (if known), token identifier (if parseable), failure reason.

D. Negative tests

Test 14: Token with tampered payload → rejected.

Test 15: Token with invalid signature → rejected.

Test 16: Token with unsupported algorithm → rejected.

3. Token lifecycle diagram
Here’s a compact, text‑friendly lifecycle you can drop into docs.

text
+------------------+
| 1. Request Token |
| (headless client)|
+--------+---------+
         |
         v
+--------------------------+
| 2. Issue & Sign Token    |
| - Build payload:         |
|   { op_id, caller, ts }  |
| - Sign with HMAC(key)    |
| - Store issuance record  |
+--------+-----------------+
         |
         v
+--------------------------+
| 3. Invoke Destructive    |
|    Operation (Headless)  |
| - Client sends token     |
+--------+-----------------+
         |
         v
+--------------------------+
| 4. Validate Token        |
| - Verify HMAC signature  |
| - Check expiry (<=5 min) |
| - Check op_id matches    |
| - Check caller matches   |
| - Check not used before  |
+--------+-----------------+
   |            |
   | valid      | invalid
   v            v
+--------------------------+      +--------------------------+
| 5a. Redeem & Execute     |      | 5b. Reject Operation     |
| - Mark token as used     |      | - Log failed redemption  |
| - Perform destructive op |      | - Return error           |
+--------+-----------------+      +--------------------------+
         |
         v
+--------------------------+
| 6. Audit Logging         |
| - Log redemption result  |
| - Link to issuance entry |
+--------------------------+
---

## §III — Test-Driven Quality & Observability

### Q4 — "Critical engines" classification: exhaustive list or extensible criteria?

§III requires property-based or scenario edge tests (covering five named
scenarios) for "Critical engines (duplicate detection, secure delete, batch
processors)." These three are listed in parentheses without stating whether
the list is exhaustive.

**Problem**: The codebase continues to grow — PDF tools, network tools,
compression engines, and future categories are not mentioned. If the list is
exhaustive, new high-risk engines escape the stricter testing requirement
automatically. If it is illustrative, there is no defined process for
classifying a new engine as critical, leaving it to individual PR authors
or reviewers to decide inconsistently.

**Questions**:
- Is the parenthetical list (duplicate detection, secure delete, batch
  processors) exhaustive, or illustrative of a broader category?
- If illustrative, what criteria determine whether a module qualifies as a
  "critical engine" (e.g., operates on user data at scale, performs
  irreversible operations, processes untrusted external input)?
- Who has authority to classify a new module as a critical engine — the PR
  author (self-declaration), any maintainer (classification at review), or
  does it require a constitutional amendment?
- Should the constitution replace the named list with a definition of
  "critical engine" by criteria?

**Anwser**: Takeaway
The parenthetical list is illustrative, not exhaustive.
The constitution should replace it with a criteria‑based definition of “critical engine,” and classification authority should rest with any maintainer during review, not PR authors and not constitutional amendments.

This gives you:

deterministic classification

consistent reviewer expectations

automatic coverage for future modules

no need to amend the constitution every time a new engine appears

1. Is the list exhaustive or illustrative?
It must be illustrative.

If it were exhaustive:

new high‑risk modules (PDF redaction, compression, OCR, network sync, etc.) would escape strict testing

PR authors could avoid property‑based tests simply by naming a module differently

the constitution would require constant amendments

Therefore:

The list (“duplicate detection, secure delete, batch processors”) is illustrative of a broader category of modules that meet the criteria of a critical engine.

2. What criteria determine a “critical engine”?
You need a criteria‑based definition that is:

objective

testable

future‑proof

reviewer‑consistent

Here is the governance‑grade definition:

A module qualifies as a critical engine if it meets ANY of the following criteria:
Criterion 1 — Irreversible or destructive operations
The module performs operations that are irreversible or hard to reverse, including:

deletion

overwrite

secure wipe

anonymization

lossy transformation

Criterion 2 — Large‑scale or batch operations
The module can operate on multiple user files or resources at once, where a defect could cause widespread damage.

Examples:

batch renamers

batch converters

batch metadata writers

multi‑file processors

Criterion 3 — High‑impact data transformations
The module performs transformations where correctness is critical and errors are costly:

deduplication

compression

OCR

PDF extraction

image normalization

checksum or integrity engines

Criterion 4 — Processing untrusted external input
The module ingests or processes untrusted or externally supplied data:

network sync

remote metadata fetch

external file parsing

archive extraction

Criterion 5 — Security‑sensitive behavior
The module interacts with:

encryption

secure deletion

authentication

token validation

sandbox boundaries

3. Who has authority to classify a module as a critical engine?
You need a governance model that is:

flexible

fast

reviewer‑driven

not bottlenecked by constitutional amendments

The correct authority is:

Any maintainer during PR review may classify a module as a critical engine if it meets the criteria in §G.X.  
This classification MUST be documented in the module’s README or metadata file.

This avoids:

PR authors self‑downgrading risk

constitutional amendments for every new engine

inconsistent reviewer interpretations

And ensures:

maintainers can elevate risk classification immediately

CI can enforce the stricter test suite automatically

4. Should the constitution replace the named list with a criteria‑based definition?
Yes — absolutely.

The list should be removed and replaced with:

a definition

criteria

examples (non‑exhaustive)

This is the same pattern you used for “side effects” and “user‑visible.”

Proposed Constitutional Text (ready to paste)
§G.X — Critical Engine (New Glossary Entry)
Critical engine — A module that meets one or more of the following criteria:
(a) performs irreversible or hard‑to‑reverse operations;
(b) operates on multiple user files or resources at scale;
(c) performs high‑impact data transformations where correctness is essential;
(d) processes untrusted external input;
(e) performs security‑sensitive operations.
Examples include, but are not limited to: duplicate detection engines, secure deletion engines, batch processors, compression engines, PDF processors, and network synchronization modules.

§III — Testing Requirements (Amended)
Replace the parenthetical list with:

All critical engines (as defined in §G.X) MUST implement property‑based tests or scenario edge tests covering the five required scenarios in §III.
The examples previously listed (duplicate detection, secure delete, batch processors) are illustrative and not exhaustive.

§III.Y — Classification Authority (New Subsection)
Any maintainer MAY classify a module as a critical engine during PR review if it meets the criteria in §G.X.
This classification MUST be recorded in the module’s metadata or README.
PR authors MAY self‑declare but maintainers have final authority.

please Include these there drafts into the documention and Referance them

1) Reviewer Checklist — “Is this module a Critical Engine?”
This checklist is designed for maintainers performing PR review.
A module is a critical engine if it meets ANY of the criteria below.

A. Irreversible or Destructive Behavior
Does the module delete, overwrite, wipe, anonymize, or perform lossy transformations?

Does a defect risk permanent data loss?

If yes → Critical Engine.

B. Large‑Scale or Batch Operations
Can the module operate on multiple files/resources at once?

Could a defect propagate across many user assets?

If yes → Critical Engine.

C. High‑Impact Data Transformations
Does the module perform transformations where correctness is essential?
Examples: deduplication, compression, OCR, PDF extraction, checksum engines.

Would incorrect behavior silently corrupt or misclassify data?

If yes → Critical Engine.

D. Untrusted External Input
Does the module ingest or process data from external or untrusted sources?
Examples: network sync, remote metadata fetch, archive extraction.

If yes → Critical Engine.

E. Security‑Sensitive Operations
Does the module interact with encryption, secure deletion, authentication, token validation, or sandbox boundaries?

If yes → Critical Engine.

F. Reviewer Override
Even if none of the above apply, does the reviewer believe the module’s failure mode is high‑impact?

Does the module’s behavior interact with other critical engines?

If yes → Reviewer may classify as Critical Engine.

G. Documentation Requirement
If classified as critical:

PR MUST include a note in the module’s README or metadata:
critical_engine: true

PR MUST include property‑based or scenario edge tests per §III.

2) CI Enforcement Spec — Property‑Based Tests for Critical Engines
This spec defines what CI must enforce automatically.

A. Detection of Critical Engines
CI MUST detect modules marked with:

critical_engine: true in metadata

or a CRITICAL_ENGINE flag in module configuration

or a reviewer‑added classification file (e.g., critical.json)

CI MUST treat all such modules as critical.

B. Required Test Artifacts
For each critical engine, CI MUST verify:

Presence of a property‑based test suite
OR

Presence of scenario edge tests covering the five required scenarios in §III

CI MUST fail the build if:

No property‑based tests exist

No scenario edge tests exist

Tests exist but do not reference the module under test

Tests exist but are skipped, disabled, or marked TODO

C. Test Execution Requirements
CI MUST:

Execute property‑based tests with a minimum iteration count (e.g., 500–1000 runs)

Fail on any nondeterministic behavior

Fail if the module panics, crashes, or produces inconsistent outputs

Fail if destructive operations are not guarded by dry‑run and confirmation logic

D. Coverage Requirements
CI MUST verify:

All public entry points of the critical engine are exercised

All destructive paths are covered

All error paths are covered

All boundary conditions (empty input, large input, malformed input) are tested

E. Reviewer Override
CI MUST allow maintainers to add new modules to the critical list without code changes.

3) Migration Patch — Updating Existing Modules to Declare Classification
This is a governance‑aligned migration patch you can apply across the repo.

Step 1 — Add Metadata Field
Add a new field to each module’s metadata file (e.g., module.yaml, module.json):

yaml
critical_engine: true | false
If the module meets ANY criteria from §G.X, set it to true.

Step 2 — Update Existing Modules
Apply the following classifications:

Already Known Critical Engines
yaml
duplicate_detection:
  critical_engine: true

secure_delete:
  critical_engine: true

batch_processor:
  critical_engine: true
Likely Critical (based on criteria)
yaml
pdf_tools:
  critical_engine: true

compression_engine:
  critical_engine: true

network_sync:
  critical_engine: true

archive_extractor:
  critical_engine: true
Non‑Critical Examples
yaml
theme_manager:
  critical_engine: false

ui_layout:
  critical_engine: false

settings_panel:
  critical_engine: false
Step 3 — Add Reviewer Notes
Each module’s README MUST include:

Code
## Critical Engine Classification
This module is classified as a critical engine under §G.X because:
- <criterion(s) from the checklist>
Step 4 — CI Integration
Add a CI rule:

If critical_engine: true → enforce property‑based tests

If critical_engine: false → skip strict enforcement

Step 5 — Document the Classification Process
Add a new file:

docs/critical-engines.md

Containing:

the criteria

the reviewer checklist

the CI rules

the classification table
---

## §V — Simplicity & Extensible Modularity

### Q5 — ComponentGuardian: recovery path from degraded state

§V defines when a component *enters* degraded state (initialization failure or
`health_check()` returning `False` at runtime) but does not define how or
whether a component can *exit* degraded state without a full application
restart.

**Problem**: If the underlying cause of degradation is resolved at runtime
(e.g., a missing file is restored, a transient lock is released), the
constitution provides no mechanism for the component to return to healthy
operation. A component could legitimately self-heal but remain permanently
degraded because no recovery path exists.

**Questions**:
- Can a component recover from degraded state back to fully functional state
  while the application is running?
- If yes, what triggers this transition — the next `health_check()` poll
  returning `True`, an explicit developer call to a recovery API, or a
  user-initiated action?
- If no (degraded is permanent until restart), should the constitution state
  this explicitly so implementations are not built with false recovery
  expectations?
- Must recovery from degraded state be logged as an audit or structured log
  event?

**Anwser**: Takeaway
Yes — components can recover from degraded state at runtime.
Recovery is triggered by a subsequent successful health_check(), not by developer calls or user actions.
Recovery MUST be logged.
The constitution should explicitly define this transition so implementations behave consistently.

1. Can a component recover from degraded state?
Yes — recovery MUST be allowed.

A degraded state is meant to reflect current operational health, not a permanent failure.
Many degradation causes are transient:

missing file restored

network reconnects

lock released

dependency restarts

temporary permissions issue resolved

If the constitution forbids recovery, you force:

unnecessary restarts

brittle workflows

false alarms

degraded UX

So the constitution should explicitly allow recovery.

2. What triggers recovery?
The only correct trigger is:

A subsequent health_check() returning True.
This is:

deterministic

testable

consistent across components

independent of UI or developer intervention

aligned with the existing degradation model

Not allowed as recovery triggers:
Developer calls — too implementation‑specific

User actions — unpredictable and not constitutional

Implicit heuristics — not reviewer‑testable

Why health_check() is the right trigger
It already defines degradation, so it should also define recovery.
Symmetry = clarity.

3. If recovery were not allowed, should the constitution say so?
Yes — but we are not choosing that model.

A “degraded until restart” model is:

brittle

surprising

inconsistent with self‑healing systems

harmful for long‑running batch or daemonized apps

So instead, the constitution should explicitly define the recovery path.

4. Must recovery be logged?
Yes — absolutely.

Recovery is a state transition with operational significance.
It must be logged for:

auditability

debugging

observability

incident analysis

user support

Required log fields:
timestamp

component name

previous state (“degraded”)

new state (“healthy”)

reason (e.g., “health_check() returned True”)

Proposed Constitutional Text (ready to paste)
§V.X — Recovery from Degraded State (New Section)
§V.X.1 — Recovery Eligibility  
A component MAY recover from degraded state while the application is running.

§V.X.2 — Recovery Trigger  
Recovery MUST occur automatically when a subsequent invocation of health_check() returns True.
No developer action, user action, or external trigger MAY be required for recovery.

§V.X.3 — Recovery Behavior  
Upon recovery, the component MUST:
– resume normal operation;
– clear any degraded‑state indicators;
– re‑enter the regular health‑check polling cycle.

§V.X.4 — Recovery Logging  
Recovery from degraded state MUST generate a structured log or audit entry containing:
– timestamp;
– component identifier;
– previous state (“degraded”);
– new state (“healthy”);
– reason for recovery (e.g., health_check() returned True).

§V.X.5 — Deterministic Reviewability  
Implementations MUST ensure that both degradation and recovery transitions are testable via unit tests and observable via logs.
please include the following suggestion in the documentation and ensure it is cross referanced.:
### 1) State machine diagram for ComponentGuardian

```text
+--------------------+
|      HEALTHY       |
+---------+----------+
          |
          | health_check() == False
          v
+--------------------+
|     DEGRADED       |
+---------+----------+
          |
          | health_check() == True
          v
+--------------------+
|      HEALTHY       |
+--------------------+

Additional transitions:

HEALTHY
  - On init failure ---------------> DEGRADED
  - On successful init ------------> HEALTHY

DEGRADED
  - While health_check() == False -> remain DEGRADED
  - On shutdown ------------------> TERMINATED (if modeled)

Notes:
- Only health_check() drives Healthy <-> Degraded transitions.
- No direct user/dev “force healthy” transition is allowed.
```

---

### 2) Reviewer checklist for degradation/recovery behavior

**A. State model**

- **Explicit states:**  
  **Check:** Component has at least `HEALTHY` and `DEGRADED` states defined in code or metadata.  
- **Single source of truth:**  
  **Check:** There is a single state holder (no duplicated flags).

**B. Entry into degraded**

- **Init failure:**  
  **Check:** Initialization failure sets state to `DEGRADED` and logs it.  
- **Runtime failure:**  
  **Check:** `health_check()` returning `False` transitions from `HEALTHY` to `DEGRADED`.  
- **No hidden paths:**  
  **Check:** No other ad‑hoc flags bypass the official degraded state.

**C. Recovery from degraded**

- **Trigger:**  
  **Check:** Only `health_check()` returning `True` transitions from `DEGRADED` to `HEALTHY`.  
- **No manual override:**  
  **Check:** No developer or user API directly forces `HEALTHY` without a passing `health_check()`.  
- **Self‑healing:**  
  **Check:** Component resumes normal behavior after recovery (no “sticky degraded” logic).

**D. Logging & observability**

- **Degrade log:**  
  **Check:** Transition `HEALTHY → DEGRADED` logs: timestamp, component id, reason.  
- **Recovery log:**  
  **Check:** Transition `DEGRADED → HEALTHY` logs: timestamp, component id, reason (`health_check() == True`).  
- **Structured format:**  
  **Check:** Logs are structured (JSON/fields) and can be filtered by state transitions.

**E. Testability**

- **Unit tests:**  
  **Check:** Tests cover: init failure → degraded, health_check() false → degraded, health_check() true → recovery.  
- **Determinism:**  
  **Check:** No random or time‑only heuristics drive state transitions without `health_check()`.

---

### 3) CI test spec for enforcing recovery logic

**A. Required tests per component**

For each ComponentGuardian‑managed component, CI MUST run tests that:

- **Test 1 — Init degradation:**  
  Force initialization failure → assert state is `DEGRADED` and degrade log emitted.
- **Test 2 — Runtime degradation:**  
  Start in `HEALTHY`, simulate `health_check() == False` → assert state becomes `DEGRADED` and log emitted.
- **Test 3 — Recovery:**  
  From `DEGRADED`, simulate `health_check() == True` → assert state becomes `HEALTHY` and recovery log emitted.
- **Test 4 — Sticky degraded prevention:**  
  From `DEGRADED`, after `health_check() == True`, subsequent operations behave as healthy (no degraded‑only behavior persists).

**B. Negative tests**

- **Test 5 — No manual force‑healthy:**  
  Attempt to set `HEALTHY` without a passing `health_check()` → must be impossible or rejected.  
- **Test 6 — No silent transitions:**  
  Any state change must emit a structured log; tests fail if transitions occur without logs.

**C. CI enforcement rules**

- **Rule 1:**  
  CI fails if a ComponentGuardian component lacks tests covering both degradation and recovery.  
- **Rule 2:**  
  CI fails if logs for transitions cannot be parsed or are missing required fields.  
- **Rule 3:**  
  CI periodically runs a “contract test” suite that asserts the state machine semantics (only `health_check()` drives Healthy↔Degraded).

---

### 4) Migration patch for existing components

**Step 1 — Introduce explicit state field**

Add a state enum/field to each ComponentGuardian‑managed component:

```python
class HealthState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"

self.health_state = HealthState.HEALTHY
```

**Step 2 — Wire degradation on failure**

- **Initialization:**

```python
try:
    self._initialize()
except Exception as e:
    self.health_state = HealthState.DEGRADED
    log_degraded(component=self.name, reason="init_failure", error=str(e))
```

- **Runtime health_check:**

```python
def poll_health(self):
    ok = self.health_check()
    if not ok and self.health_state == HealthState.HEALTHY:
        self.health_state = HealthState.DEGRADED
        log_degraded(component=self.name, reason="health_check_false")
    elif ok and self.health_state == HealthState.DEGRADED:
        self.health_state = HealthState.HEALTHY
        log_recovered(component=self.name, reason="health_check_true")
```

**Step 3 — Remove ad‑hoc degraded flags**

- Replace any custom `is_broken`, `disabled`, `failed_once` flags with the unified `health_state`.

**Step 4 — Add structured logging helpers**

```python
def log_degraded(component, reason, error=None):
    logger.info({
        "event": "component_degraded",
        "component": component,
        "reason": reason,
        "error": error,
        "from_state": "healthy",
        "to_state": "degraded",
    })

def log_recovered(component, reason):
    logger.info({
        "event": "component_recovered",
        "component": component,
        "reason": reason,
        "from_state": "degraded",
        "to_state": "healthy",
    })
```

**Step 5 — Add tests**

- Add tests implementing the CI spec above for each component.  
- Mark completion in a migration tracker (e.g., `component_guardian_migration.md`) listing components and whether they now support degradation + recovery.

---

### Q6 — ComponentGuardian polling interval: constitutional bounds needed (TODO(GUARDIAN_POLL_INTERVAL))

TODO(GUARDIAN_POLL_INTERVAL) defers the runtime health-check polling interval
entirely to implementation documentation. This TODO has been open since v1.8.0.

**Problem**: Without any constitutional bounds, an implementation may poll
every 10 ms (continuous overhead that degrades performance) or every 24 hours
(so slow that a component enters degraded state undetected for almost a day).
Neither extreme satisfies the intent of runtime health monitoring — both are
technically compliant with the current text.

**Questions**:
- Should the constitution set a minimum polling frequency (e.g., "health
  checks MUST be performed at least every N seconds during active use")?
- Should the constitution set a maximum frequency to protect performance
  (e.g., "MUST NOT poll more often than every M seconds")?
- Or should polling remain entirely implementation-defined, with the
  constitution specifying only the behavioral obligation (degraded state
  MUST be detected and acted upon)?
- Should TODO(GUARDIAN_POLL_INTERVAL) be resolved now?

**Anwser**: Takeaway
Yes — the constitution must set both a minimum and a maximum polling interval.
Polling MUST occur at least every 5 seconds and no more frequently than every 500 ms.
This resolves TODO(GUARDIAN_POLL_INTERVAL) and creates a safe, testable, reviewer‑consistent range.

1. Should the constitution set a minimum polling frequency?
Yes — absolutely.

Without a minimum, a component could remain degraded for hours before detection.

The right constitutional minimum is:

health checks MUST be performed at least once every 5 seconds during active use.

Why 5 seconds?

fast enough to detect degradation promptly

slow enough to avoid unnecessary overhead

aligns with typical health‑check intervals in distributed systems (Kubernetes, systemd, supervisord)

This is the “no slower than” bound.

2. Should the constitution set a maximum polling frequency?
Yes — also absolutely.

Without a maximum, implementations can accidentally DOS themselves with 10 ms polling loops.

The right constitutional maximum is:

health checks MUST NOT be performed more frequently than once every 500 ms.

Why 500 ms?

prevents CPU churn

prevents tight loops

still allows responsive detection for latency‑sensitive components

aligns with typical watchdog patterns

This is the “no faster than” bound.

3. Should polling remain implementation‑defined?
Polling behavior (e.g., jitter, backoff, adaptive polling) can remain implementation‑defined.

Polling bounds must be constitutional.

So the constitution should specify:

the allowed range (0.5 s to 5 s)

the obligation (must poll within that range)

the freedom (implementations may choose any strategy inside the range)

This gives you:

consistency

testability

flexibility

4. Should TODO(GUARDIAN_POLL_INTERVAL) be resolved now?
Yes — immediately.

Leaving it open:

creates inconsistent implementations

blocks CI enforcement

undermines ComponentGuardian’s purpose

forces reviewers to guess what “reasonable” means

This TODO is governance‑critical and should be closed in the next revision.

Proposed Constitutional Text (ready to paste)
§V.Y — Health‑Check Polling Interval (New Section)
§V.Y.1 — Minimum Polling Frequency  
During active use, each component’s health_check() MUST be invoked at least once every 5 seconds. Implementations MAY poll more frequently, subject to §V.Y.2.

§V.Y.2 — Maximum Polling Frequency  
Implementations MUST NOT invoke health_check() more frequently than once every 500 milliseconds to avoid excessive resource consumption.

§V.Y.3 — Implementation Flexibility  
Implementations MAY use fixed intervals, jitter, exponential backoff, or adaptive strategies, provided all polling remains within the bounds defined in §V.Y.1 and §V.Y.2.

§V.Y.4 — Deterministic Reviewability  
Polling intervals MUST be testable via unit tests and observable via logs or metrics. CI MUST verify that the effective polling interval remains within the constitutional bounds.

§V.Y.5 — Resolution of TODO(GUARDIAN_POLL_INTERVAL)  
This section resolves TODO(GUARDIAN_POLL_INTERVAL). No further implementation‑defined polling intervals are permitted outside the constitutional bounds.

please also include the following in the documents and cross referance_
1) Reviewer Checklist — Polling Interval Compliance
This checklist ensures every component’s health‑check loop respects the constitutional bounds and behaves predictably.

A. Interval Bound Compliance
Minimum interval:  
Check that health_check() is invoked no less frequently than every 5 seconds.
Fail if: interval > 5 s during active use.

Maximum interval:  
Check that health_check() is invoked no more frequently than every 500 ms.
Fail if: interval < 500 ms (tight loop, CPU churn).

B. Deterministic Scheduling
Check that the polling interval is explicitly defined (constant, config, or scheduler).

Check that the interval is not dependent on random jitter alone.

Check that jitter/backoff stays within constitutional bounds.

C. State Transition Behavior
Verify that:

health_check() == False → transitions to DEGRADED

health_check() == True → transitions to HEALTHY

Confirm no other triggers (user actions, developer calls) override the polling loop.

D. Logging & Observability
Check that each poll is observable via logs or metrics.

Check that transitions caused by polling are logged (degrade/recover).

E. Testability
Confirm that polling interval is testable in unit tests (mock timers, virtual clocks).

Confirm that tests assert both bounds (min/max).

2) CI Test Spec — Enforcing Polling Interval Bounds
CI must enforce that every ComponentGuardian‑managed component polls within the constitutional range.

A. Static Analysis
CI MUST detect:

Hardcoded intervals outside the allowed range.

Missing interval definitions.

Polling loops without sleep/delay.

Polling intervals derived from user input or unbounded config.

B. Unit Test Requirements
For each component, CI MUST run tests that verify:

Test 1 — Minimum Interval
Simulate active use → assert that the time between polls is ≤ 5 seconds.

Test 2 — Maximum Interval
Simulate active use → assert that the time between polls is ≥ 500 ms.

Test 3 — Jitter/Backoff Compliance
If jitter/backoff is used:

Assert that no interval violates the constitutional bounds.

Test 4 — State Transition Triggered by Polling
From HEALTHY, simulate health_check() == False → assert transition to DEGRADED.

From DEGRADED, simulate health_check() == True → assert transition to HEALTHY.

C. Negative Tests
Test that polling does not occur faster than 500 ms even under load.

Test that polling does not exceed 5 s even when the system is idle.

Test that transitions do not occur without a poll.

D. CI Failure Conditions
CI MUST fail if:

No polling interval tests exist.

Polling interval violates bounds.

Polling is nondeterministic or unobservable.

State transitions occur without logs.

3) Migration Patch — Updating Existing Components to Adopt the New Polling Model
This patch describes the steps needed to bring all components into compliance.

Step 1 — Introduce a Polling Interval Constant
Add to each component:

python
MIN_POLL_INTERVAL = 0.5   # seconds
MAX_POLL_INTERVAL = 5.0   # seconds
Or use a shared Guardian config:

python
guardian.poll_interval_min = 0.5
guardian.poll_interval_max = 5.0
Step 2 — Update the Polling Loop
Replace any existing polling logic with:

python
while running:
    start = now()

    ok = self.health_check()
    self._apply_state_transition(ok)

    elapsed = now() - start
    sleep_time = clamp(desired_interval - elapsed,
                       MIN_POLL_INTERVAL,
                       MAX_POLL_INTERVAL)
    sleep(sleep_time)
Where desired_interval is implementation‑defined but must remain within bounds.

Step 3 — Remove Unbounded or Ad‑Hoc Polling
Delete:

tight loops

polling based on CPU load

polling based on user events

polling based on random intervals without bounds

Step 4 — Add Logging for Poll Intervals
Add structured logs:

python
logger.debug({
    "event": "health_poll",
    "component": self.name,
    "interval": sleep_time,
})
Step 5 — Add Tests
Add unit tests verifying:

interval never < 500 ms

interval never > 5 s

degrade/recover transitions triggered by polling

Step 6 — Document the Polling Model
Update each component’s README:

Code
## Health-Check Polling
This component participates in ComponentGuardian polling.
Polling interval is bounded by the constitutional limits:
- Minimum: 500 ms
- Maximum: 5 seconds
4) Diagram — Polling Loop with Degradation & Recovery
text
+-------------------------------------------------------------+
|                     ComponentGuardian                       |
+-------------------------------------------------------------+

                (every 0.5s to 5s, inclusive)
                           |
                           v
                +-----------------------+
                |   health_check()      |
                +-----------------------+
                           |
          +----------------+----------------+
          |                                 |
          | ok == True                      | ok == False
          v                                 v
+-----------------------+        +-----------------------+
|  State = HEALTHY      |        |  State = DEGRADED     |
|  (if previously       |        |  (if previously       |
|   degraded → recover) |        |   healthy → degrade)  |
+-----------------------+        +-----------------------+
          |                                 |
          +----------------+----------------+
                           |
                           v
                +-----------------------+
                |   sleep(interval)     |
                |  (0.5s ≤ interval ≤ 5s) |
                +-----------------------+
                           |
                           v
                     (next poll)
This diagram shows:

polling loop

constitutional interval bounds

degrade and recover transitions

no external triggers

self‑healing behavior

1) Unified diff patch for the constitution (focused on §V + new glossary refs)
diff
diff --git a/constitution.md b/constitution.md
index abc1234..def5678 100644
--- a/constitution.md
+++ b/constitution.md
@@ -120,6 +120,52 @@
  §V — ComponentGuardian Runtime Health Monitoring
  ------------------------------------------------
 
-ComponentGuardian monitors component health at initialization and runtime.
-Components MAY enter a degraded state when initialization fails or when
-`health_check()` returns `False`.
+ComponentGuardian monitors component health at initialization and runtime.
+Components MAY enter a degraded state when initialization fails or when
+`health_check()` returns `False`. Components MAY recover from degraded state
+when `health_check()` subsequently returns `True`, as defined below.
+
+§V.1 — Health States
+--------------------
+
+Components managed by ComponentGuardian MUST support at least the following
+health states:
+
+- HEALTHY
+- DEGRADED
+
+The current health state MUST be represented by a single, authoritative state
+holder per component.
+
+§V.2 — Entry into Degraded State
+--------------------------------
+
+§V.2.1 — Initialization Failure
+If a component fails during initialization, it MUST enter the DEGRADED state
+and MUST emit a structured log or audit entry indicating:
+- timestamp
+- component identifier
+- previous state (if any)
+- new state ("degraded")
+- reason ("init_failure" or equivalent)
+
+§V.2.2 — Runtime Failure
+If a component is in the HEALTHY state and `health_check()` returns `False`,
+the component MUST transition to the DEGRADED state and MUST emit a structured
+log or audit entry indicating:
+- timestamp
+- component identifier
+- previous state ("healthy")
+- new state ("degraded")
+- reason ("health_check_false" or equivalent)
+
+§V.3 — Recovery from Degraded State
+-----------------------------------
+
+§V.3.1 — Recovery Eligibility
+A component MAY recover from the DEGRADED state while the application is
+running.
+
+§V.3.2 — Recovery Trigger
+Recovery MUST occur automatically when a subsequent invocation of
+`health_check()` returns `True`. No developer action, user action, or external
+trigger MAY be required for recovery.
+
+§V.3.3 — Recovery Behavior
+Upon recovery, the component MUST:
+- transition from DEGRADED to HEALTHY;
+- resume normal operation;
+- clear any degraded-state indicators;
+- re-enter the regular health-check polling cycle.
+
+§V.3.4 — Recovery Logging
+Recovery from the DEGRADED state MUST generate a structured log or audit entry
+containing:
+- timestamp
+- component identifier
+- previous state ("degraded")
+- new state ("healthy")
+- reason for recovery (e.g., "health_check_true").
+
+§V.3.5 — Deterministic Reviewability
+Implementations MUST ensure that both degradation and recovery transitions are
+testable via automated tests and observable via logs or metrics.
+
+§V.4 — Health-Check Polling Interval
+------------------------------------
+
+§V.4.1 — Minimum Polling Frequency
+During active use, each component’s `health_check()` MUST be invoked at least
+once every 5 seconds. Implementations MAY poll more frequently, subject to
+§V.4.2.
+
+§V.4.2 — Maximum Polling Frequency
+Implementations MUST NOT invoke `health_check()` more frequently than once
+every 500 milliseconds to avoid excessive resource consumption.
+
+§V.4.3 — Implementation Flexibility
+Implementations MAY use fixed intervals, jitter, exponential backoff, or
+adaptive strategies, provided all polling remains within the bounds defined in
+§V.4.1 and §V.4.2.
+
+§V.4.4 — Observability and Testability
+Polling intervals MUST be testable via automated tests and observable via logs
+or metrics. CI MUST verify that the effective polling interval remains within
+the constitutional bounds.
+
+§V.4.5 — Resolution of TODO(GUARDIAN_POLL_INTERVAL)
+This section resolves TODO(GUARDIAN_POLL_INTERVAL). No implementation-defined
+polling intervals are permitted outside the constitutional bounds.
2) ComponentGuardian reference implementation (Python-style)
python
from enum import Enum
import time
import logging

logger = logging.getLogger(__name__)


class HealthState(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class ComponentGuardian:
    MIN_POLL_INTERVAL = 0.5   # seconds
    MAX_POLL_INTERVAL = 5.0   # seconds

    def __init__(self, name, health_check, desired_interval=1.0):
        """
        :param name: component identifier
        :param health_check: callable -> bool
        :param desired_interval: target polling interval (bounded later)
        """
        self.name = name
        self.health_check = health_check
        self.state = HealthState.HEALTHY
        self.desired_interval = desired_interval

    def _log_transition(self, from_state, to_state, reason, error=None):
        payload = {
            "event": "component_state_transition",
            "component": self.name,
            "from_state": from_state.value if from_state else None,
            "to_state": to_state.value,
            "reason": reason,
            "error": str(error) if error else None,
        }
        logger.info(payload)

    def _enter_degraded(self, reason, error=None):
        if self.state is not HealthState.DEGRADED:
            prev = self.state
            self.state = HealthState.DEGRADED
            self._log_transition(prev, self.state, reason, error)

    def _recover(self, reason):
        if self.state is HealthState.DEGRADED:
            prev = self.state
            self.state = HealthState.HEALTHY
            self._log_transition(prev, self.state, reason)

    def initialize(self, init_fn):
        try:
            init_fn()
            self.state = HealthState.HEALTHY
        except Exception as e:
            self._enter_degraded(reason="init_failure", error=e)

    def _clamp_interval(self, elapsed):
        # desired_interval is implementation-defined but must respect bounds
        interval = max(self.desired_interval - elapsed, self.MIN_POLL_INTERVAL)
        interval = min(interval, self.MAX_POLL_INTERVAL)
        return interval

    def poll_loop(self, running_flag):
        """
        :param running_flag: callable -> bool, returns False to stop loop
        """
        while running_flag():
            start = time.monotonic()

            try:
                ok = self.health_check()
            except Exception as e:
                ok = False
                logger.warning(
                    {
                        "event": "health_check_exception",
                        "component": self.name,
                        "error": str(e),
                    }
                )

            if ok:
                self._recover(reason="health_check_true")
            else:
                self._enter_degraded(reason="health_check_false")

            elapsed = time.monotonic() - start
            interval = self._clamp_interval(elapsed)

            logger.debug(
                {
                    "event": "health_poll",
                    "component": self.name,
                    "interval": interval,
                    "elapsed": elapsed,
                    "state": self.state.value,
                }
            )

            time.sleep(interval)
This is intentionally minimal but hits all constitutional points: explicit states, degradation, recovery via health_check(), bounded polling, and structured logging.

3) Governance‑grade §V (integrated Q5 + Q6)
markdown
§V — ComponentGuardian Runtime Health Monitoring
------------------------------------------------

§V.1 — Purpose
ComponentGuardian provides a unified mechanism for monitoring component health
at initialization and runtime. Its goals are to:
- detect degraded components promptly;
- allow components to self-heal when conditions improve;
- expose health transitions via structured logs or audit entries;
- operate within constitutionally bounded polling intervals.

§V.2 — Health States
Components managed by ComponentGuardian MUST support at least the following
health states:
- HEALTHY
- DEGRADED

The current health state MUST be represented by a single, authoritative state
holder per component.

§V.3 — Entry into Degraded State

§V.3.1 — Initialization Failure  
If a component fails during initialization, it MUST enter the DEGRADED state
and MUST emit a structured log or audit entry indicating:
- timestamp
- component identifier
- previous state (if any)
- new state ("degraded")
- reason ("init_failure" or equivalent)

§V.3.2 — Runtime Failure  
If a component is in the HEALTHY state and `health_check()` returns `False`,
the component MUST transition to the DEGRADED state and MUST emit a structured
log or audit entry indicating:
- timestamp
- component identifier
- previous state ("healthy")
- new state ("degraded")
- reason ("health_check_false" or equivalent)

§V.4 — Recovery from Degraded State

§V.4.1 — Recovery Eligibility  
A component MAY recover from the DEGRADED state while the application is
running.

§V.4.2 — Recovery Trigger  
Recovery MUST occur automatically when a subsequent invocation of
`health_check()` returns `True`. No developer action, user action, or external
trigger MAY be required for recovery.

§V.4.3 — Recovery Behavior  
Upon recovery, the component MUST:
- transition from DEGRADED to HEALTHY;
- resume normal operation;
- clear any degraded-state indicators;
- re-enter the regular health-check polling cycle.

§V.4.4 — Recovery Logging  
Recovery from the DEGRADED state MUST generate a structured log or audit entry
containing:
- timestamp
- component identifier
- previous state ("degraded")
- new state ("healthy")
- reason for recovery (e.g., "health_check_true").

§V.4.5 — Deterministic Reviewability  
Implementations MUST ensure that both degradation and recovery transitions are
testable via automated tests and observable via logs or metrics.

§V.5 — Health-Check Polling Interval

§V.5.1 — Minimum Polling Frequency  
During active use, each component’s `health_check()` MUST be invoked at least
once every 5 seconds. Implementations MAY poll more frequently, subject to
§V.5.2.

§V.5.2 — Maximum Polling Frequency  
Implementations MUST NOT invoke `health_check()` more frequently than once
every 500 milliseconds to avoid excessive resource consumption.

§V.5.3 — Implementation Flexibility  
Implementations MAY use fixed intervals, jitter, exponential backoff, or
adaptive strategies, provided all polling remains within the bounds defined in
§V.5.1 and §V.5.2.

§V.5.4 — Observability and Testability  
Polling intervals MUST be testable via automated tests and observable via logs
or metrics. CI MUST verify that the effective polling interval remains within
the constitutional bounds.

§V.5.5 — Resolution of TODO(GUARDIAN_POLL_INTERVAL)  
This section resolves TODO(GUARDIAN_POLL_INTERVAL). No implementation-defined
polling intervals are permitted outside the constitutional bounds.
4) Reviewer training guide for Guardian behavior
markdown
# Reviewer Training Guide — ComponentGuardian Behavior

This guide helps reviewers consistently evaluate ComponentGuardian usage across
components, focusing on health states, degradation, recovery, and polling
intervals.

---

## 1. Mental model: what Guardian guarantees

ComponentGuardian is responsible for:

- Tracking a component’s health as either **HEALTHY** or **DEGRADED**.
- Moving into DEGRADED when initialization or `health_check()` fails.
- Moving back to HEALTHY when `health_check()` later succeeds.
- Polling `health_check()` within constitutional bounds (0.5s–5s).
- Emitting structured logs for all state transitions.

If any of these are missing or ad‑hoc, the implementation is not compliant.

---

## 2. What to look for in code

**A. Explicit state**

- There should be a single state holder (e.g., `HealthState.HEALTHY/DEGRADED`).
- Avoid multiple flags (`is_broken`, `disabled`, etc.) that duplicate state.

**B. Degradation paths**

- On init failure → state set to DEGRADED + log.
- On `health_check() == False` from HEALTHY → state set to DEGRADED + log.
- No “silent failure” paths that bypass the state machine.

**C. Recovery paths**

- On `health_check() == True` from DEGRADED → state set to HEALTHY + log.
- No manual “force healthy” APIs that skip `health_check()`.
- After recovery, normal behavior resumes (no sticky degraded behavior).

**D. Polling loop**

- A clear loop or scheduler that calls `health_check()` periodically.
- Interval is bounded: never < 500 ms, never > 5 s.
- Any jitter/backoff still respects those bounds.

---

## 3. What to look for in tests

- Tests that simulate:
  - init failure → DEGRADED
  - `health_check() == False` → DEGRADED
  - `health_check() == True` → HEALTHY
- Tests that assert:
  - polling interval stays within 0.5s–5s
  - transitions emit structured logs
- Tests that ensure:
  - no state change without a log
  - no recovery without a passing `health_check()`

If tests only cover degradation but not recovery, ask for additional coverage.

---

## 4. What to look for in logs/metrics

- Events like:
  - `component_state_transition` with from/to state and reason
  - `health_poll` with interval and state
- Ability to answer:
  - When did this component degrade?
  - When did it recover?
  - How often is it being polled?

If you cannot reconstruct these from logs/metrics, the implementation is weak.

---

## 5. Common anti‑patterns to reject

- Tight polling loops with `while True: health_check()` and no sleep.
- Polling intervals derived from user input without bounds.
- Manual “reset” or “force healthy” methods that bypass `health_check()`.
- Multiple overlapping health flags instead of a single state.
- Logs that say “failed” or “recovered” but lack structured fields.

---

## 6. Quick review checklist

1. **States:** Is there a clear HEALTHY/DEGRADED model?
2. **Degrade:** Do init failure and `health_check() == False` both lead to DEGRADED + log?
3. **Recover:** Does `health_check() == True` from DEGRADED lead to HEALTHY + log?
4. **Polling:** Is `health_check()` polled between 0.5s and 5s?
5. **Tests:** Are both degradation and recovery covered by automated tests?
6. **Logs:** Can you see transitions and poll intervals in structured logs?

If any answer is “no” or “not clear,” request changes before approving.

---

## §VI — User Preference Management & Personalization

### Q7 — Export encryption algorithm: implementation-defined or constitutionally prescribed?

§VI requires that export artifacts "MUST encrypt sensitive preference values."
The encryption algorithm, key derivation method, and format for the encrypted
values are not specified.

**Problem**: Without a prescribed algorithm, an implementation could use DES,
RC4, or a custom cipher and technically satisfy "encrypt." Export files are
used across devices and for backup/restore workflows, so algorithm
interoperability between implementations matters. Additionally, if the
encryption key is derived from a user passphrase, the key derivation function
(KDF) must be specified to ensure adequate strength.

**Questions**:
- Should the constitution prescribe a minimum algorithm (e.g., AES-256-GCM
  with Argon2id key derivation from a user-supplied passphrase)?
- Or is the algorithm implementation-defined provided it meets a minimum
  security bar (e.g., authenticated encryption, key size ≥ 128 bits)?
- Must the algorithm name and parameters be declared in the export file's
  metadata so a future import can correctly identify the decryption method?
- Must the encryption key be derived from a user-supplied passphrase, or may
  it be an application-managed key (risking that the key and data are only as
  separate as the same file system)?

**Anwser**: Takeaway
Yes — the constitution must prescribe:

a minimum encryption algorithm: AES‑256‑GCM

a minimum KDF: Argon2id with constitutional parameter floors

mandatory metadata describing algorithm + parameters

passphrase‑derived keys, not application‑managed keys

a portable, versioned encryption envelope format

This ensures interoperability, security, and reviewer‑testability across all implementations.

1. Should the constitution prescribe a minimum algorithm?
Yes — absolutely.

If you don’t prescribe a minimum, someone will eventually ship:

DES

RC4

AES‑ECB

a homegrown XOR cipher

or “encrypted” meaning “base64”

The correct constitutional minimum is:

AES‑256‑GCM
modern

authenticated encryption (AEAD)

widely supported

safe defaults

portable across languages and platforms

GCM is essential because it provides integrity, not just confidentiality.

2. Should the KDF be prescribed?
Yes — Argon2id MUST be required.

If you don’t specify a KDF, someone will use:

PBKDF2 with 1,000 iterations

SHA‑1 as a KDF

or no KDF at all

The correct constitutional minimum is:

Argon2id
With constitutional parameter floors:

memory ≥ 64 MB

iterations ≥ 3

parallelism ≥ 1

salt ≥ 16 bytes

These are conservative, portable, and secure.

3. Must the algorithm name + parameters be declared in metadata?
Yes — mandatory.

Otherwise, future imports cannot decrypt older exports.

The export file MUST include:

algorithm name (e.g., "aes-256-gcm")

KDF name ("argon2id")

KDF parameters (memory, iterations, parallelism)

salt

nonce

version number

This is the same pattern used by:

age

libsodium sealed boxes

encrypted ZIP formats

KeePass

Without metadata, interoperability collapses.

4. Must the encryption key be derived from a user passphrase?
Yes — MUST be passphrase‑derived.

Application‑managed keys are:

stored on the same filesystem

often in plaintext

not portable

not user‑controlled

not secure for backups

The constitution should require:

Export encryption keys MUST be derived from a user‑supplied passphrase using Argon2id.

This ensures:

portability

user control

separation of key and ciphertext

no silent weakening by implementers

5. Should the constitution allow implementation‑defined algorithms?
No — not for export encryption.

Export files must be:

portable

future‑proof

cross‑implementation compatible

Therefore:

algorithm MUST be prescribed

KDF MUST be prescribed

metadata MUST be standardized

Implementations MAY support additional algorithms, but the constitutional minimum must be the default.

Proposed Constitutional Text (ready to paste)
§VI.X — Export Encryption Requirements (New Section)
§VI.X.1 — Mandatory Encryption Algorithm  
All sensitive preference values in export artifacts MUST be encrypted using AES‑256‑GCM. Weaker algorithms or non‑AEAD modes MUST NOT be used.

§VI.X.2 — Key Derivation  
The encryption key MUST be derived from a user‑supplied passphrase using Argon2id with the following minimum parameters:
– memory ≥ 64 MB
– iterations ≥ 3
– parallelism ≥ 1
– salt length ≥ 16 bytes

§VI.X.3 — Metadata Requirements  
Export artifacts MUST include metadata specifying:
– encryption algorithm name
– KDF name
– KDF parameters (memory, iterations, parallelism)
– salt
– nonce
– version number
This metadata MUST be stored in plaintext within the export file header.

§VI.X.4 — Authenticated Encryption  
AES‑256‑GCM MUST be used in authenticated mode. Importers MUST verify authentication tags before accepting decrypted data.

§VI.X.5 — Passphrase Requirement  
The encryption key MUST be derived from a user‑supplied passphrase. Application‑managed keys MUST NOT be used for export encryption.

§VI.X.6 — Interoperability  
All implementations MUST support decrypting export artifacts produced by any other implementation conforming to this section.

§VI.X.7 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– AES‑256‑GCM is used
– Argon2id parameters meet minimums
– metadata is present and correct
– no plaintext sensitive values appear in the export

1) Reference encryption envelope format (JSON)
json
{
  "version": 1,
  "encryption": {
    "algorithm": "aes-256-gcm",
    "kdf": {
      "name": "argon2id",
      "memory_mb": 64,
      "iterations": 3,
      "parallelism": 1,
      "salt_b64": "BASE64_SALT"
    },
    "nonce_b64": "BASE64_NONCE",
    "tag_b64": "BASE64_AUTH_TAG"
  },
  "meta": {
    "created_at": "2026-04-02T16:27:00Z",
    "tool": "rfu-export",
    "schema_version": "prefs-v3"
  },
  "ciphertext_b64": "BASE64_CIPHERTEXT"
}
Plaintext fields: version, encryption, meta

Sensitive data: only inside ciphertext_b64

2) Reviewer checklist for export‑encryption compliance
Algorithm:

Check: encryption.algorithm == "aes-256-gcm".

Fail if: any other algorithm or mode (ECB, CBC, RC4, etc.).

KDF:

Check: kdf.name == "argon2id".

Check: memory_mb ≥ 64, iterations ≥ 3, parallelism ≥ 1, salt_b64 present and ≥ 16 bytes decoded.

Fail if: weaker KDF, missing salt, or parameters below floors.

Metadata presence:

Check: version, encryption, encryption.kdf, nonce_b64, tag_b64, ciphertext_b64 all present.

Check: meta includes at least created_at and schema_version.

Passphrase‑derived key:

Check in code: key is derived from a user passphrase via Argon2id, not loaded from app‑managed secrets.

No plaintext leakage:

Check: sensitive preference values do not appear outside ciphertext_b64.

Spot‑check: decode JSON and search for obvious secrets (tokens, passwords, API keys).

Interoperability:

Check: import path uses the same envelope fields and validates tag before accepting decrypted data.

3) CI enforcement spec
Static checks:

Rule 1: Scan code for export paths; ensure only AES‑256‑GCM is used for export encryption.

Rule 2: Scan for Argon2id usage with parameter floors (memory, iterations, parallelism).

Rule 3: Disallow app‑managed keys for export (no “export_key” constants, no config‑file keys).

Unit/integration tests:

Test 1 — Round‑trip:

Export with a known passphrase → import with same passphrase → preferences match exactly.

Test 2 — Wrong passphrase:

Import with incorrect passphrase → decryption fails, no partial data accepted.

Test 3 — Tag tampering:

Modify ciphertext_b64 or tag_b64 → import rejects with auth failure.

Test 4 — Metadata completeness:

Exported JSON must contain all required fields; CI fails if any are missing.

Test 5 — Parameter floors:

Assert Argon2id parameters in the envelope meet or exceed constitutional minimums.

CI failure conditions:

Any export artifact missing required envelope fields.

Any test showing successful decryption with wrong passphrase or tampered data.

Any use of non‑AES‑256‑GCM or non‑Argon2id in export code paths.

4) Migration plan for existing exports
Step 1 — Inventory formats

Identify: all existing export formats and versions.

Document: which are encrypted, which are plaintext, which use legacy crypto.

Step 2 — Introduce versioned envelope

Define version: 1 as the new AES‑256‑GCM + Argon2id envelope (above).

Keep legacy exports as version: 0 (or implicit) for backward‑compatible import only.

Step 3 — New exports use envelope

Change all export code to:

prompt for passphrase,

derive key via Argon2id,

encrypt with AES‑256‑GCM,

emit the JSON envelope.

Step 4 — Import supports both old and new

On import:

If JSON has version and encryption → treat as new envelope.

Else → treat as legacy; import, then re‑export using the new envelope when user next exports.

Step 5 — Deprecate legacy

Mark legacy export formats as deprecated in docs.

Optionally add a warning when importing legacy exports: “This export uses a legacy format; please re‑export to upgrade encryption.”

Step 6 — Tests and docs

Add tests for:

legacy import → new export,

new export → new import.

Update documentation to describe:

envelope format,

passphrase requirement,

migration behavior.

5) Encryption/decryption workflow diagram
text
           EXPORT WORKFLOW
           ----------------

+---------------------------+
| 1. Collect preferences    |
+-------------+-------------+
              |
              v
+---------------------------+
| 2. Ask user for           |
|    passphrase             |
+-------------+-------------+
              |
              v
+---------------------------+
| 3. Derive key via         |
|    Argon2id (salt, params)|
+-------------+-------------+
              |
              v
+---------------------------+
| 4. Encrypt prefs with     |
|    AES-256-GCM (nonce)    |
+-------------+-------------+
              |
              v
+---------------------------+
| 5. Build JSON envelope:   |
|    version, encryption,   |
|    meta, ciphertext_b64   |
+-------------+-------------+
              |
              v
+---------------------------+
| 6. Write export file      |
+---------------------------+


           IMPORT WORKFLOW
           ----------------

+---------------------------+
| 1. Read export file       |
+-------------+-------------+
              |
              v
+---------------------------+
| 2. Parse JSON envelope    |
|    (version, encryption)  |
+-------------+-------------+
              |
              v
+---------------------------+
| 3. Ask user for           |
|    passphrase             |
+-------------+-------------+
              |
              v
+---------------------------+
| 4. Derive key via         |
|    Argon2id using stored  |
|    salt & params          |
+-------------+-------------+
              |
              v
+---------------------------+
| 5. Decrypt with           |
|    AES-256-GCM (nonce,    |
|    tag, ciphertext)       |
+-------------+-------------+
              |
              v
+---------------------------+
| 6. Verify auth tag;       |
|    if OK, load prefs      |
+---------------------------+
---

### Q8 — "Round-trip fidelity": preference values only, or full record including timestamps?

§DW §13 requires: "export then import produces identical preference state."
The scope of "identical" is not bounded.

**Problem**: Preference records include system-generated metadata fields such
as `created_at` and `modified_at`. After an export-import cycle, these fields
will naturally differ — they are updated to the import timestamp, not
preserved from the original. A strict reading of "identical" fails every
round-trip test on these fields. The test requirement is therefore either
unenf orceable as written or silently partial.

**Questions**:
- Does "identical preference state" mean preference *values* are identical
  (comparing only `preference_category`, `preference_key`, `preference_value`,
  and `value_type`), with system-generated timestamp and metadata fields
  explicitly excluded from the comparison?
- Or does it mean the *full record* is byte-for-byte identical, including
  timestamps?
- Should the constitution explicitly list which fields are included in and
  excluded from the fidelity comparison?

**Anwser**: Takeaway
“Identical preference state” MUST mean identical preference values, not identical full records.
System‑generated metadata fields (timestamps, internal IDs, audit markers) MUST be explicitly excluded from round‑trip fidelity checks.
The constitution should list which fields are included and excluded.

This makes the requirement testable, reviewer‑proof, and future‑proof.

1. What “identical preference state” SHOULD mean
It must refer to the semantic state of user preferences, not the storage record.

Included in fidelity comparison (MUST match exactly):
preference_category

preference_key

preference_value

value_type

These define the actual preference state.

Excluded from fidelity comparison (MUST NOT be compared):
created_at

modified_at

imported_at

record_id

version

migration_flags

any system‑generated metadata

These fields are:

non‑portable

implementation‑specific

naturally changed by import

not part of the user’s preference semantics

Comparing them would make round‑trip fidelity impossible.

2. Why full‑record byte‑for‑byte identity is impossible
Because:

created_at will always reflect the original creation time

modified_at will always reflect the import time

importers may normalize values

storage formats may differ

ordering of fields may differ

internal IDs will differ

Byte‑for‑byte identity is not achievable and should not be required.

3. Should the constitution explicitly list included/excluded fields?
Yes — absolutely.

Without an explicit list:

reviewers guess

CI cannot enforce

implementations diverge

round‑trip tests become meaningless

A constitutional definition is required.

4. Proposed Constitutional Text (ready to paste)
§DW §13 — Round‑Trip Fidelity (Amended)
§DW §13.1 — Definition of Identical Preference State  
“Identical preference state” refers exclusively to the semantic preference values.
The following fields MUST match exactly after an export‑import cycle:
– preference_category  
– preference_key  
– preference_value  
– value_type

§DW §13.2 — Excluded Fields  
The following system‑generated metadata fields MUST be excluded from round‑trip fidelity comparison:
– created_at  
– modified_at  
– imported_at  
– record_id  
– version  
– migration_flags  
– any other implementation‑generated metadata not part of the preference value

§DW §13.3 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– all preference values round‑trip identically
– no system‑generated metadata is included in the fidelity comparison
– importers do not modify preference values except through explicit migration rules

§DW §13.4 — Ordering and Formatting  
Differences in record ordering, JSON formatting, or metadata timestamps MUST NOT cause a fidelity failure.

1) CI test suite for round‑trip fidelity
Goal: Prove that export → import preserves semantic preference state (category, key, value, value_type) and ignores system metadata.

Core tests
Test 1 — Simple round‑trip

Arrange: Create a preference set with diverse entries:

different categories

different value types (string, int, bool, list, object)

Act: Export → Import.

Assert: For every (preference_category, preference_key):

preference_value matches exactly

value_type matches exactly

No extra or missing keys.

Test 2 — Metadata ignored

Arrange: Same as Test 1.

Act: Export → Import.

Assert: CI explicitly does not compare:

created_at, modified_at, imported_at, record_id, version, migration_flags.

Test passes even if these differ.

Test 3 — Ordering and formatting

Arrange: Export preferences, then:

shuffle record order

reformat JSON (whitespace, field order)

Act: Import.

Assert: Semantic state still matches; no failures due to ordering/formatting.

Test 4 — Partial export/import

Arrange: Preferences with multiple categories; export a subset.

Act: Import subset into a clean profile.

Assert: Only exported preferences exist; each has identical (category, key, value, type).

Test 5 — Backward compatibility

Arrange: Legacy export (previous version).

Act: Import with current importer.

Assert: Same semantic fidelity rules hold.

CI failure conditions
Any mismatch in preference_category, preference_key, preference_value, or value_type.

Any test that tries to compare metadata fields as part of fidelity.

Any import that silently drops or mutates preference values without explicit migration rules.

2) Reviewer checklist for round‑trip fidelity
A. Scope of “identical”

Check: Code and tests clearly treat semantic fields as the fidelity target:

Included: preference_category, preference_key, preference_value, value_type.

Excluded: timestamps, IDs, version, migration flags.

Fail if: Tests or code try to enforce byte‑for‑byte record equality.

B. Export behavior

Check: All relevant preferences are exported with correct category/key/value/type.

Check: No sensitive values are left out without documented reason.

Check: No extra, non‑preference data is mixed into the preference payload in a way that confuses import.

C. Import behavior

Check: Import reconstructs the same set of (category, key) pairs.

Check: Values and types are preserved exactly (no silent coercion).

Check: Any migration logic is explicit and documented (not hidden in “magic” transforms).

D. Tests

Check: There is at least one explicit round‑trip test that:

Exports → Imports → compares semantic fields only.

Check: Tests do not assert equality on timestamps or IDs.

Fail if: Round‑trip tests are missing, trivial, or only check “file exists”.

E. Edge cases

Check: Behavior with:

empty preference sets

unknown categories

new value types

Check: Import does not crash or silently drop data in these cases.

3) Migration patch for existing exporters/importers
Step 1 — Define the canonical comparison set

In shared code, define something like:

python
ROUND_TRIP_FIELDS = [
    "preference_category",
    "preference_key",
    "preference_value",
    "value_type",
]
METADATA_FIELDS = [
    "created_at",
    "modified_at",
    "imported_at",
    "record_id",
    "version",
    "migration_flags",
]
Step 2 — Update exporters

Ensure exporters always emit the four canonical fields for each preference.

Keep metadata fields if needed, but clearly separate them (e.g., nested meta object or separate section).

Step 3 — Update importers

On import:

Reconstruct preferences using only ROUND_TRIP_FIELDS.

Treat METADATA_FIELDS as optional, non‑authoritative.

Remove any logic that tries to restore or compare timestamps as part of “fidelity”.

Step 4 — Update tests

Replace any tests that compare full records with tests that:

Compare only ROUND_TRIP_FIELDS.

Explicitly ignore METADATA_FIELDS.

Add at least one test that demonstrates timestamps differ but fidelity still passes.

Step 5 — Document behavior

In developer docs / DW section:

State clearly: “Round‑trip fidelity is defined over preference category/key/value/type only. Metadata is excluded.”

4) Diagram of the round‑trip process
text
          EXPORT PHASE
          ------------

+-------------------------------+
| 1. Read current preferences   |
|    (all records)              |
+---------------+---------------+
                |
                v
+-------------------------------+
| 2. Extract semantic fields    |
|    (category, key, value,     |
|     value_type)               |
+---------------+---------------+
                |
                v
+-------------------------------+
| 3. Attach optional metadata   |
|    (timestamps, IDs, etc.)    |
+---------------+---------------+
                |
                v
+-------------------------------+
| 4. Serialize to export format |
+-------------------------------+


          IMPORT PHASE
          ------------

+-------------------------------+
| 5. Read export artifact       |
+---------------+---------------+
                |
                v
+-------------------------------+
| 6. Parse records              |
+---------------+---------------+
                |
                v
+-------------------------------+
| 7. Reconstruct preferences    |
|    using ONLY:                |
|    - category                 |
|    - key                      |
|    - value                    |
|    - value_type               |
+---------------+---------------+
                |
                v
+-------------------------------+
| 8. Store preferences          |
|    (system regenerates        |
|     metadata: created_at,     |
|     modified_at, IDs, etc.)   |
+---------------+---------------+
                |
                v
+-------------------------------+
| 9. Round-trip check compares  |
|    semantic fields only       |
+-------------------------------+
---

## §VII — Identity & Access Control

### Q9 — "Offline-capable MFA": TOTP variant specification gaps

§VII accepts TOTP as an offline-capable MFA method but does not specify the
TOTP configuration. RFC 6238 (TOTP) and RFC 4226 (HOTP) both exist; within
TOTP, multiple configurations are possible: digest algorithm (SHA-1, SHA-256,
SHA-512), OTP length (6 or 8 digits), and time step (30 s or 60 s).
Standard authenticator apps (Google Authenticator, Authy, Microsoft
Authenticator) default to SHA-1 / 6 digits / 30 s. Enterprise or custom
implementations may differ.

**Problem**: Two TOTP implementations with different configurations are not
interoperable. A user enrolling with a SHA-256 / 8-digit / 60 s configuration
cannot authenticate on a system that expects SHA-1 / 6-digit / 30 s. Without
a prescribed default, every implementation may differ, breaking portability.

**Questions**:
- Should the constitution prescribe RFC 6238 TOTP compliance as the
  governing standard (time-based, not counter-based)?
- Should a default configuration be required for interoperability (e.g.,
  HMAC-SHA1, 6 digits, 30 s time step — the most broadly supported
  default)?
- Is HOTP (RFC 4226, counter-based one-time password) an acceptable
  offline-capable MFA method, or is TOTP the only permitted time-based
  variant?
- Are single-use backup/recovery codes (generated at enrollment, stored
  offline by the user) considered an enrolled "offline-capable MFA method"
  for the purpose of the activation gate, or are they not counted as an
  enrolled method?

**Anwser**: Takeaway
Yes — the constitution must:

prescribe RFC 6238 TOTP as the governing standard

mandate a default configuration for interoperability:
HMAC‑SHA1, 6 digits, 30‑second time step

forbid HOTP as a primary MFA method (allowed only as a fallback)

exclude backup codes from counting as an enrolled MFA method

This ensures that every implementation can interoperate with every authenticator app on Earth.

1. Should the constitution prescribe RFC 6238 TOTP?
Yes — MUST.

TOTP (RFC 6238) is:

time‑based

widely supported

offline‑capable

compatible with all major authenticator apps

HOTP (RFC 4226) is:

counter‑based

prone to desynchronization

not universally supported

not ideal for activation gates

Therefore:

TOTP (RFC 6238) MUST be the standard. HOTP MUST NOT be used as the primary offline MFA method.

2. Should a default configuration be required?
Yes — absolutely.

Without a default, interoperability collapses.

The correct constitutional default is the universal authenticator profile:

TOTP Default Profile (Constitutional Minimum)
Algorithm: HMAC‑SHA1

Digits: 6

Time step: 30 seconds

Drift tolerance: ±1 time step (±30 seconds)

Why this profile?

It is supported by every authenticator app (Google, Microsoft, Authy, 1Password, Duo, FreeOTP, etc.)

It is the de facto global standard

It ensures cross‑device portability

It avoids fragmentation

Implementations MAY support stronger variants (SHA‑256, SHA‑512, 8 digits), but:

All implementations MUST support the default profile for interoperability.

3. Is HOTP acceptable?
No — not as an enrolled MFA method.

HOTP is:

counter‑based

prone to drift

not supported by many authenticator apps

not suitable for activation gates

It MAY be supported as an optional fallback for legacy or accessibility reasons, but:

HOTP MUST NOT count as an enrolled offline‑capable MFA method for activation‑gate purposes.

4. Do backup/recovery codes count as an enrolled MFA method?
No — they MUST NOT count.

Backup codes are:

single‑use

intended for emergency access

not a factor that can be “enrolled”

not suitable for activation gates

Therefore:

Backup/recovery codes MUST NOT count as an enrolled MFA method.  
They MAY exist as an emergency fallback but do not satisfy MFA enrollment requirements.

Proposed Constitutional Text (ready to paste)
§VII.X — Offline‑Capable MFA Requirements (New Section)
§VII.X.1 — Mandatory Standard  
Offline‑capable MFA MUST use TOTP as defined in RFC 6238.
HOTP (RFC 4226) MAY be supported for legacy compatibility but MUST NOT count as an enrolled MFA method.

§VII.X.2 — Default TOTP Profile  
All implementations MUST support the following TOTP configuration for interoperability:
– Algorithm: HMAC‑SHA1  
– Digits: 6  
– Time step: 30 seconds  
– Drift tolerance: ±1 time step  
Implementations MAY support additional algorithms or parameters, but the default profile MUST always be accepted.

§VII.X.3 — Enrollment and Portability  
Enrollment MUST produce a TOTP secret compatible with the default profile.
Export/import of MFA configuration MUST preserve the TOTP secret and metadata.

§VII.X.4 — Backup Codes  
Single‑use backup/recovery codes MAY be provided as an emergency fallback but MUST NOT count as an enrolled MFA method for activation‑gate purposes.

§VII.X.5 — Deterministic Reviewability

1) Reviewer Checklist — MFA (TOTP) Compliance
This checklist ensures every implementation of offline‑capable MFA meets the constitutional requirements.

A. Standards Compliance
Check: MFA uses TOTP (RFC 6238), not HOTP.

Fail if: HOTP is treated as an enrolled MFA method.

B. Default TOTP Profile
Verify support for the constitutional default profile:

Algorithm: HMAC‑SHA1

Digits: 6

Time step: 30 seconds

Drift tolerance: ±1 time step

Fail if:

Only SHA‑256/SHA‑512 is supported

Only 8‑digit codes are supported

Time step differs from 30 seconds

Drift tolerance is missing or too strict

C. Enrollment Behavior
Check: Enrollment generates a TOTP secret compatible with the default profile.

Check: QR code / provisioning URI uses the default profile.

Check: Secret is stored securely (encrypted at rest).

D. Verification Behavior
Check: Verification accepts codes generated by standard authenticator apps.

Check: Drift tolerance is implemented correctly.

Check: Verification rejects codes outside the allowed window.

E. Backup Codes
Check: Backup codes exist only as emergency fallback.

Check: Backup codes are not counted as an enrolled MFA method.

F. Interoperability
Check: Export/import preserves the TOTP secret and metadata.

Check: Import does not break compatibility with the default profile.

G. Test Coverage
Check: Unit tests cover:

enrollment

verification

drift tolerance

invalid codes

backup code usage

Fail if: MFA tests are missing or trivial.

2) CI Enforcement Spec — MFA (TOTP) Compliance
CI must enforce constitutional MFA requirements automatically.

A. Static Analysis
CI MUST detect:

Use of TOTP (RFC 6238) in MFA code paths

Default profile parameters (SHA‑1, 6 digits, 30s)

No HOTP enrollment paths

No backup‑code‑as‑MFA logic

B. Unit Tests
CI MUST run tests that verify:

Test 1 — Default Profile Interoperability
Generate TOTP secret

Use a standard TOTP library to generate codes

Verify codes are accepted

Test 2 — Drift Tolerance
Generate codes for:

current time

+30 seconds

–30 seconds

Verify all are accepted

Verify +60s and –60s are rejected

Test 3 — Wrong Algorithm
Generate SHA‑256 or SHA‑512 codes

Verify they are rejected unless explicitly supported as optional

Test 4 — Wrong Digit Length
Generate 8‑digit codes

Verify they are rejected unless explicitly supported as optional

Test 5 — Backup Codes
Verify backup codes work

Verify they do not count as MFA enrollment

C. CI Failure Conditions
CI MUST fail if:

TOTP default profile is not supported

HOTP is treated as an enrolled MFA method

Backup codes are counted as MFA

Drift tolerance is missing or incorrect

MFA tests are missing or incomplete

3) Migration Plan — Updating Existing MFA Implementations
Step 1 — Inventory Current MFA Methods
Identify:

TOTP implementations

HOTP implementations

Backup code systems

Any custom MFA variants

Step 2 — Standardize on the Constitutional Default Profile
Update all TOTP enrollment flows to:

Algorithm: HMAC‑SHA1

Digits: 6

Time step: 30 seconds

Drift: ±30 seconds

Ensure provisioning URIs follow:

Code
otpauth://totp/Label?secret=SECRET&issuer=APP&algorithm=SHA1&digits=6&period=30
Step 3 — Update Verification Logic
Enforce default profile

Add drift tolerance

Reject unsupported algorithms/digit lengths unless explicitly enabled

Step 4 — Update Enrollment UI
Ensure QR codes encode the default profile

Ensure manual entry instructions match the default profile

Step 5 — Update Backup Code Logic
Ensure backup codes:

are single‑use

are not counted as MFA enrollment

are stored securely

Step 6 — Update Export/Import
Ensure TOTP secret and metadata are preserved

Ensure import does not break compatibility

Step 7 — Update Tests
Add tests for:

enrollment

verification

drift tolerance

backup code behavior

default profile interoperability

Step 8 — Document the New Standard
Update developer docs and §VII references.

4) Diagram — TOTP Enrollment + Verification Workflow
text
                ENROLLMENT
                -----------

+-------------------------------+
| 1. User requests MFA setup    |
+---------------+---------------+
                |
                v
+-------------------------------+
| 2. System generates TOTP      |
|    secret (random 160-bit)    |
+---------------+---------------+
                |
                v
+-------------------------------+
| 3. System constructs          |
|    otpauth:// URI using       |
|    default profile:           |
|    - SHA1                     |
|    - 6 digits                 |
|    - 30s period               |
+---------------+---------------+
                |
                v
+-------------------------------+
| 4. Display QR code / secret   |
|    to user                    |
+---------------+---------------+
                |
                v
+-------------------------------+
| 5. User scans into            |
|    authenticator app          |
+---------------+---------------+
                |
                v
+-------------------------------+
| 6. User enters current TOTP   |
|    code to confirm enrollment |
+-------------------------------+


                VERIFICATION
                -------------

+-------------------------------+
| 1. User enters TOTP code      |
+---------------+---------------+
                |
                v
+-------------------------------+
| 2. System derives expected    |
|    codes for:                 |
|    - current time             |
|    - +30s                     |
|    - -30s                     |
+---------------+---------------+
                |
                v
+-------------------------------+
| 3. Compare user code to       |
|    expected codes             |
+---------------+---------------+
                |
                v
      +---------+---------+
      |                   |
      v                   v
+-----------+     +----------------+
| 4a. Pass  |     | 4b. Reject     |
|  MFA OK   |     |  MFA failed    |
+-----------+     +----------------+

Draft constitutional amendment text for §VII

VII — Identity & Access Control (Amended)
§VII.X — Offline‑Capable Multi‑Factor Authentication (MFA)
§VII.X.1 — Mandatory Standard  
Offline‑capable MFA MUST use Time‑Based One‑Time Passwords (TOTP) as defined in RFC 6238.
Counter‑based One‑Time Passwords (HOTP, RFC 4226) MAY be supported for legacy compatibility but MUST NOT count as an enrolled MFA method for activation‑gate purposes.

§VII.X.2 — Default TOTP Profile (Interoperability Requirement)  
All implementations MUST support the following TOTP configuration for interoperability with standard authenticator applications:
– Algorithm: HMAC‑SHA1  
– Code length: 6 digits  
– Time step: 30 seconds  
– Drift tolerance: ±1 time step  
This profile MUST be accepted by all implementations.
Implementations MAY additionally support stronger or alternative profiles (e.g., SHA‑256, SHA‑512, 8‑digit codes, 60‑second steps), but these MUST NOT replace or disable the default profile.

§VII.X.3 — Enrollment Requirements  
Enrollment MUST generate a TOTP secret compatible with the default profile.
Enrollment MUST provide the user with a provisioning URI or QR code encoding the default profile parameters.
The TOTP secret MUST be stored securely and encrypted at rest.

§VII.X.4 — Verification Requirements  
Verification MUST compute expected TOTP values using the default profile and MUST accept codes within the configured drift tolerance.
Verification MUST reject codes generated using unsupported algorithms, digit lengths, or time steps unless explicitly configured as optional secondary profiles.

§VII.X.5 — Backup and Recovery Codes  
Single‑use backup or recovery codes MAY be provided as an emergency fallback mechanism.
Backup codes MUST NOT count as an enrolled MFA method for activation‑gate purposes.
Backup codes MUST be generated with sufficient entropy and MUST be stored securely.

§VII.X.6 — Export and Import of MFA Configuration  
Export and import workflows MUST preserve the TOTP secret and associated metadata required for verification.
Importers MUST NOT alter the TOTP secret or profile parameters unless explicitly migrating from a legacy format.
All implementations MUST remain interoperable with the default TOTP profile after import.

§VII.X.7 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– TOTP is implemented according to RFC 6238
– the default profile (SHA‑1 / 6 digits / 30 seconds) is supported
– HOTP is not treated as an enrolled MFA method
– backup codes are not counted as MFA enrollment
– drift tolerance is implemented correctly
– enrollment and verification are covered by automated tests

§VII.X.8 — Security Requirements  
TOTP secrets MUST be generated using a cryptographically secure random number generator.
Secrets MUST be at least 160 bits.
Secrets MUST be encrypted at rest and never logged in plaintext.
Verification MUST validate the full 6‑digit code and MUST NOT accept partial matches or truncated comparisons.

---

### Q10 — FIDO2 scope: roaming hardware security key only, or platform authenticator too?

§VII names "FIDO2 hardware token" as an offline-capable MFA method. The FIDO2
standard defines two classes of authenticator:

- **Roaming authenticators** (hardware security keys: YubiKey, Titan Key,
  etc.) — physical devices detachable from the host, usable on any device.
- **Platform authenticators** (built-in: Windows Hello, Touch ID, Face ID,
  device TPM) — bound to a specific device; offline-capable but device-tied.

**Problem**: "FIDO2 hardware token" could be read as roaming-only (physical
external token) or as including platform authenticators (which are
hardware-backed but embedded in the host device). Platform authenticators
introduce a recovery problem: if the device is lost, the platform FIDO2
enrollment cannot be transferred to a replacement device without admin
intervention. This affects the "offline-capable" guarantee and the account
recovery path.

**Questions**:
- Is "FIDO2 hardware token" restricted to *roaming* authenticators (physical
  security keys detachable from the host device)?
- Or does it also include *platform* authenticators (device TPM, biometric
  sensors) that implement FIDO2 but are device-bound?
- If platform authenticators are accepted, must they be paired with at least
  one roaming authenticator or TOTP enrollment to ensure recovery?
- Should the constitution use the more precise FIDO2 terminology
  (roaming / platform) to eliminate ambiguity?

**Anwser**: Takeaway
“FIDO2 hardware token” MUST mean roaming authenticators only.
Platform authenticators MAY be supported, but they MUST NOT count as an enrolled offline‑capable MFA method unless paired with a roaming key or TOTP.
The constitution MUST adopt explicit FIDO2 terminology (“roaming” vs “platform”) to eliminate ambiguity.

This preserves portability, recoverability, and offline capability — the three pillars of §VII.

1. Is “FIDO2 hardware token” restricted to roaming authenticators?
Yes — MUST be restricted.

A “hardware token” in common security governance refers to:

a detachable

cross‑device

roaming

external

user‑controlled

security key.

Platform authenticators:

are tied to a single device

cannot be moved

cannot be exported

cannot be recovered if the device is lost

break the “offline‑capable” guarantee

Therefore:

“FIDO2 hardware token” MUST mean a FIDO2 roaming authenticator.

2. Does the definition include platform authenticators?
No — not for the purpose of satisfying the MFA enrollment requirement.

Platform authenticators MAY be supported as an additional convenience factor, but:

they are not portable

they are not recoverable

they do not satisfy the offline‑capable requirement

they cannot be used across devices

they cannot be used to bootstrap a new device

Thus:

Platform authenticators MUST NOT count as an enrolled offline‑capable MFA method.

They are allowed, but not sufficient.

3. If platform authenticators are accepted, must they be paired with a roaming key or TOTP?
Yes — MUST be paired.

If a user enrolls only a platform authenticator and loses the device, they lose access permanently unless:

a roaming key

or a TOTP enrollment

or an admin recovery path

exists.

To avoid this:

Platform authenticators MAY be enrolled, but only in addition to at least one roaming authenticator or TOTP method.

This ensures:

recoverability

portability

offline capability

no single point of failure

4. Should the constitution use precise FIDO2 terminology?
Yes — absolutely.

The constitution MUST explicitly distinguish:

FIDO2 roaming authenticators

FIDO2 platform authenticators

This eliminates ambiguity and aligns with the FIDO2 standard.

Proposed Constitutional Text (ready to paste)
§VII.Y — FIDO2 Authenticator Requirements (New Section)
§VII.Y.1 — Definitions  
A FIDO2 roaming authenticator is a detachable hardware security key (e.g., USB‑A/C, NFC, BLE) that can be used across devices.
A FIDO2 platform authenticator is a device‑bound authenticator integrated into the host device (e.g., Windows Hello, Touch ID, Face ID, TPM‑backed keys).

§VII.Y.2 — Offline‑Capable MFA Requirement  
For the purpose of satisfying the offline‑capable MFA enrollment requirement, only FIDO2 roaming authenticators and TOTP (RFC 6238) qualify.

§VII.Y.3 — Platform Authenticators  
Platform authenticators MAY be supported as additional MFA methods but MUST NOT count as an enrolled offline‑capable MFA method unless the user has also enrolled at least one of:
– a FIDO2 roaming authenticator, or
– a TOTP method.

§VII.Y.4 — Recovery and Portability  
Because platform authenticators are device‑bound and non‑portable, they MUST NOT be the sole MFA method for any account.
Implementations MUST ensure that users can recover access using a roaming authenticator or TOTP if the platform device is lost or replaced.

§VII.Y.5 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– roaming authenticators satisfy the MFA enrollment requirement
– platform authenticators do not satisfy the requirement alone
– enrollment flows clearly distinguish roaming vs platform
– recovery paths exist for platform‑only users
– documentation uses the correct FIDO2 terminology

1) Reviewer Checklist — FIDO2 Compliance
This checklist ensures that MFA implementations correctly distinguish roaming vs platform authenticators and enforce the constitutional requirements for offline‑capable MFA.

A. Terminology & Classification
Check: Code and documentation explicitly distinguish:

FIDO2 roaming authenticators (detachable hardware keys)

FIDO2 platform authenticators (device‑bound)

Fail if: “FIDO2 hardware token” is used ambiguously or refers to platform authenticators.

B. Enrollment Requirements
Check: Enrollment flow clearly identifies whether the authenticator is:

roaming

platform

Check: Only roaming authenticators are counted as satisfying the offline‑capable MFA requirement.

Fail if: Platform authenticators are treated as sufficient for MFA enrollment.

C. Recovery & Portability
Check: If a platform authenticator is enrolled, the user MUST also have:

at least one roaming authenticator, or

a TOTP enrollment

Fail if: A user can end up with only a platform authenticator.

D. Verification Behavior
Check: Verification correctly handles:

FIDO2 assertions

user presence (UP)

user verification (UV)

Check: Platform authenticator verification does not bypass the requirement for a roaming/TOTP method.

Fail if: Platform-only accounts can authenticate without a fallback.

E. Export/Import Behavior
Check: Roaming authenticator metadata is exportable/importable.

Check: Platform authenticator credentials are not exported (they are device‑bound).

Fail if: Platform credentials are exported or treated as portable.

F. UI/UX Requirements
Check: UI clearly labels:

“Security Key (Roaming FIDO2)”

“This Device (Platform FIDO2)”

Fail if: UI hides the distinction or misleads users.

G. Test Coverage
Check: Tests cover:

roaming enrollment

platform enrollment

recovery scenarios

device‑loss scenarios

fallback to roaming/TOTP

Fail if: Tests do not simulate device loss or platform‑only enrollment.

2) CI Enforcement Spec — FIDO2 Compliance
This spec ensures CI automatically enforces the constitutional rules for FIDO2 MFA.

A. Static Analysis Rules
CI MUST detect:

Use of FIDO2 APIs for:

roaming authenticators

platform authenticators

Explicit classification of authenticator type

No code path that treats platform authenticators as “hardware tokens”

No code path that counts platform authenticators as offline‑capable MFA

CI MUST fail if:

Platform authenticators are labeled as “hardware tokens”

Platform authenticators are counted as MFA enrollment

B. Unit Test Requirements
Test 1 — Roaming Enrollment
Enroll a roaming authenticator

Assert: MFA requirement satisfied

Test 2 — Platform Enrollment
Enroll a platform authenticator

Assert: MFA requirement not satisfied

Assert: UI prompts user to add roaming/TOTP

Test 3 — Device Loss Scenario
Enroll platform authenticator

Simulate device loss

Assert: user cannot authenticate

Assert: recovery path requires roaming/TOTP

Test 4 — Mixed Enrollment
Enroll platform + roaming

Assert: MFA requirement satisfied

Assert: roaming authenticator works on a second device

Test 5 — Export/Import
Export MFA configuration

Assert: roaming metadata exported

Assert: platform credentials not exported

C. Integration Test Requirements
Test 6 — Cross‑Device Authentication
Enroll roaming authenticator on Device A

Authenticate on Device B

Assert: success

Test 7 — Platform‑Only Authentication
Enroll platform authenticator

Attempt authentication on Device B

Assert: failure

D. CI Failure Conditions
CI MUST fail if:

Platform authenticators satisfy MFA enrollment

Roaming vs platform distinction is missing

Recovery path is not enforced

Export includes platform credentials

Tests for device‑loss scenarios are missing

drafts: 
1) Constitutional amendment patch for §VII.Y (FIDO2 roaming vs platform)
diff
diff --git a/constitution.md b/constitution.md
index 1234abc..5678def 100644
--- a/constitution.md
+++ b/constitution.md
@@ -250,6 +250,74 @@
  §VII — Identity & Access Control
  --------------------------------
 
+§VII.Y — FIDO2 Authenticator Requirements
+-----------------------------------------
+
+§VII.Y.1 — Definitions
+----------------------
+
+For the purposes of this constitution:
+
+- A **FIDO2 roaming authenticator** is a detachable hardware security key
+  (e.g., USB, NFC, BLE) that can be used across devices and is not bound to a
+  single platform.
+
+- A **FIDO2 platform authenticator** is a device-bound authenticator integrated
+  into the host device (e.g., Windows Hello, Touch ID, Face ID, TPM-backed
+  keys) and not portable across devices.
+
+§VII.Y.2 — Offline-Capable MFA Requirement
+------------------------------------------
+
+For the purpose of satisfying the offline-capable MFA enrollment requirement
+in §VII, only the following methods qualify:
+
+- FIDO2 roaming authenticators; and
+- TOTP (RFC 6238) as defined in §VII.X.
+
+FIDO2 platform authenticators MAY be supported as additional MFA methods but
+MUST NOT, by themselves, satisfy the offline-capable MFA enrollment
+requirement.
+
+§VII.Y.3 — Platform Authenticator Pairing
+-----------------------------------------
+
+If a user enrolls a FIDO2 platform authenticator, the implementation MUST
+ensure that the user has also enrolled at least one of:
+
+- a FIDO2 roaming authenticator; or
+- a TOTP method compliant with §VII.X.
+
+Implementations MUST NOT allow an account to rely solely on a platform
+authenticator as its only MFA method.
+
+§VII.Y.4 — Recovery and Portability
+-----------------------------------
+
+Because platform authenticators are device-bound and non-portable, they MUST
+NOT be the sole MFA method for any account. Implementations MUST ensure that
+users can recover access using a roaming authenticator or TOTP if the platform
+device is lost, replaced, or becomes unavailable.
+
+§VII.Y.5 — Enrollment and UI Clarity
+------------------------------------
+
+Enrollment flows and user interfaces MUST clearly distinguish between:
+
+- “Security Key” or equivalent label for FIDO2 roaming authenticators; and
+- “This Device” or equivalent label for FIDO2 platform authenticators.
+
+Implementations MUST NOT label platform authenticators as “hardware tokens” or
+otherwise imply that they are portable across devices.
+
+§VII.Y.6 — Deterministic Reviewability
+--------------------------------------
+
+CI and reviewers MUST verify that:
+
+- roaming and platform authenticators are correctly classified in code and UI;
+- only roaming authenticators and TOTP count toward the offline-capable MFA
+  requirement;
+- platform-only enrollment is rejected or requires pairing with roaming/TOTP;
+- recovery paths exist for platform-authenticator users; and
+- no export/import workflow treats platform credentials as portable artifacts.
+
2) Reference implementation of FIDO2 enrollment logic (WebAuthn-style, TypeScript/JS)
This is a reference flow that:

clearly distinguishes roaming vs platform

enforces “platform must be paired with roaming/TOTP”

is aligned with WebAuthn/FIDO2 best practices

ts
// Types for clarity
type AuthenticatorAttachment = "platform" | "cross-platform";

interface User {
  id: string;
  username: string;
  hasRoamingFido2: boolean;
  hasTotp: boolean;
}

// --- Helpers -------------------------------------------------------------

function buildPublicKeyCredentialCreationOptions(
  user: User,
  attachment: AuthenticatorAttachment
): PublicKeyCredentialCreationOptions {
  return {
    rp: {
      name: "Example App",
      id: window.location.hostname,
    },
    user: {
      id: new TextEncoder().encode(user.id),
      name: user.username,
      displayName: user.username,
    },
    pubKeyCredParams: [
      { type: "public-key", alg: -7 },   // ES256
      { type: "public-key", alg: -257 }, // RS256
    ],
    authenticatorSelection: {
      authenticatorAttachment: attachment, // "platform" or "cross-platform"
      userVerification: "preferred",
      residentKey: "preferred",
    },
    timeout: 60000,
    challenge: window.crypto.getRandomValues(new Uint8Array(32)),
  };
}

async function registerFido2Authenticator(
  user: User,
  attachment: AuthenticatorAttachment
): Promise<void> {
  const options = buildPublicKeyCredentialCreationOptions(user, attachment);

  const credential = (await navigator.credentials.create({
    publicKey: options,
  })) as PublicKeyCredential | null;

  if (!credential) {
    throw new Error("FIDO2 enrollment was cancelled or failed.");
  }

  // Send credential to server for verification & storage
  await fetch("/api/mfa/fido2/register", {
    method: "POST",
    body: JSON.stringify({
      userId: user.id,
      attachment,
      id: credential.id,
      rawId: bufferToBase64Url(credential.rawId),
      response: {
        clientDataJSON: bufferToBase64Url(
          credential.response.clientDataJSON
        ),
        attestationObject: bufferToBase64Url(
          (credential.response as AuthenticatorAttestationResponse)
            .attestationObject
        ),
      },
      type: credential.type,
    }),
    headers: { "Content-Type": "application/json" },
  });
}

// --- Constitutional enforcement on the server side ----------------------

// Pseudocode (language-agnostic) for server-side enforcement:

/*
function completeFido2Registration(request) {
    const { userId, attachment, credential } = request;

    // 1) Verify attestation, origin, RP ID, etc. (standard WebAuthn checks)
    verifyWebAuthnAttestation(credential);

    // 2) Persist credential with attachment type
    saveCredentialToDatabase({
        userId,
        credentialId: credential.id,
        attachment, // "platform" or "cross-platform"
        // ...other metadata
    });

    // 3) Update user MFA state
    if (attachment === "cross-platform") {
        markUserHasRoamingFido2(userId, true);
    } else if (attachment === "platform") {
        markUserHasPlatformFido2(userId, true);
    }

    // 4) Enforce constitutional rule:
    //    platform authenticators MUST NOT be the sole MFA method.
    const user = loadUser(userId);

    const hasRoaming = user.hasRoamingFido2;
    const hasTotp = user.hasTotp;

    if (attachment === "platform" && !hasRoaming && !hasTotp) {
        // Enrollment is allowed, but user is NOT considered MFA-complete.
        // UI should prompt: "Add a security key or TOTP to complete MFA."
        setUserMfaStatus(userId, "incomplete_platform_only");
    } else {
        // User has at least one roaming or TOTP method.
        setUserMfaStatus(userId, "complete");
    }
}
*/

// --- Utility -------------------------------------------------------------

function bufferToBase64Url(buf: ArrayBuffer): string {
  const bytes = new Uint8Array(buf);
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
Key constitutional points reflected in the implementation:

Explicit attachment type: authenticatorAttachment: "platform" | "cross-platform"

Server stores attachment type and uses it to classify roaming vs platform

MFA completeness is only granted if the user has at least one roaming FIDO2 credential or TOTP

Platform-only enrollment is allowed but marked as incomplete, matching §VII.Y.3 and §VII.Y.4

---

### Q11 — Idle-timeout default: uniform across all roles, or role-differentiated?

§VII Session Controls states: "The out-of-box default idle timeout is 30 min."
The default applies to all roles without distinction.

**Problem**: Account roles carry substantially different risk profiles. An
`admin` or `dev` session left idle presents a far greater attack surface than
a `readonly` session. Many enterprise and regulatory security frameworks
prescribe shorter default timeouts for privileged accounts. The current
constitution applies the same 30-minute default to all roles, which may be
inadequate for high-privilege accounts and over-restrictive for low-privilege
ones.

**Questions**:
- Does the 30-minute out-of-box default apply uniformly to all roles
  (`dev`, `admin`, `user`, `readonly`)?
- Or should the constitution define role-differentiated defaults (e.g., a
  shorter default for `admin`/`dev` than for `user`/`readonly`)?
- Or is role-specific default timeout left entirely as an admin configuration
  responsibility with no constitutional prescription?

**Anwser**: Takeaway
The 30‑minute out‑of‑box idle timeout MUST NOT apply uniformly to all roles.
The constitution MUST define role‑differentiated defaults, with shorter timeouts for privileged roles (admin, dev) and longer defaults for low‑risk roles (user, readonly).
Administrators MAY override these defaults, but the constitutional baseline must be explicit.

This gives you security, predictability, and reviewer‑proof clarity.

1. Does the 30‑minute default apply uniformly today?
Yes — as written, §VII applies the 30‑minute default to all roles.

But this is a governance flaw, not a governance decision.

Uniform timeouts ignore:

privilege level

risk exposure

regulatory norms

enterprise security expectations

So the current text is insufficient and must be amended.

2. Should the constitution define role‑differentiated defaults?
Yes — MUST.

This is the only secure and interoperable choice.

Why?
admin and dev sessions are high‑risk

user and readonly sessions are low‑risk

Many frameworks (NIST, CIS, ISO 27001, SOC2) require shorter timeouts for privileged roles

Reviewers need deterministic rules

Implementations need predictable defaults

Recommended constitutional defaults:
Role	Default Idle Timeout
admin	10 minutes
dev	15 minutes
user	30 minutes
readonly	45 minutes
These values strike the right balance between security and usability.

3. Should role‑specific defaults be left to admin configuration?
No — not as the baseline.

Admins MAY override defaults, but the constitution MUST define:

the minimum security floor

the default values

the role‑based differentiation

Otherwise:

implementations diverge

reviewers cannot enforce consistency

security posture becomes unpredictable

So: admin configuration is optional, not foundational.

4. Proposed Constitutional Text (ready to paste)
§VII.Z — Idle Timeout Requirements (Amended)
§VII.Z.1 — Purpose  
Idle‑timeout controls mitigate the risk of unauthorized access to unattended sessions. Defaults MUST reflect the privilege level of the account.

§VII.Z.2 — Role‑Differentiated Default Idle Timeouts  
The out‑of‑box default idle timeout MUST be:
– 10 minutes for admin roles
– 15 minutes for dev roles
– 30 minutes for user roles
– 45 minutes for readonly roles

§VII.Z.3 — Minimum Security Floor  
Implementations MUST NOT allow any role to be configured with an idle timeout longer than 60 minutes without explicit administrative override.

§VII.Z.4 — Administrative Overrides  
Administrators MAY configure stricter or more permissive idle timeouts, subject to §VII.Z.3.
Administrative overrides MUST be logged and auditable.

§VII.Z.5 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– role‑differentiated defaults are implemented
– privileged roles (admin, dev) have shorter defaults than non‑privileged roles
– no implementation applies a uniform 30‑minute default
– administrative overrides are logged

1) Reviewer checklist for idle‑timeout compliance
A. Role‑differentiated defaults

Default mapping:  
Check: Implementation defines explicit defaults per role:

admin: 10 minutes

dev: 15 minutes

user: 30 minutes

readonly: 45 minutes
Fail if: A single uniform default (e.g., 30 minutes) is applied to all roles.

Privilege ordering:  
Check: Privileged roles (admin, dev) have shorter or equal timeouts than non‑privileged roles.
Fail if: admin or dev has a longer default than user or readonly.

B. Security floor and ceilings

Max timeout:  
Check: No role can be configured with an idle timeout > 60 minutes without explicit admin override.
Fail if: UI or config allows > 60 minutes as a silent default.

Min timeout:  
Check: Extremely low values (e.g., < 1 minute) are not used as defaults unless clearly justified (e.g., kiosk mode).

C. Administrative overrides

Override mechanism:  
Check: Admins can change timeouts per role or per policy, not only globally.
Check: Overrides are logged (who changed what, when, from → to).
Fail if: Overrides are silent or unlogged.

D. Session behavior

Idle detection:  
Check: Implementation clearly defines “idle” (no input, no API calls, etc.).
Check: Timeout is based on last activity, not just login time.

Timeout action:  
Check: On timeout, session is locked or logged out according to policy.
Fail if: Session remains usable after timeout threshold.

E. Tests and documentation

Tests:  
Check: Automated tests cover each role’s default timeout and override behavior.
Docs:  
Check: Documentation states role‑based defaults and the 60‑minute ceiling.

2) CI enforcement spec
A. Configuration validation

Static config check:  
Rule: CI parses default role configuration and asserts:

admin default = 10 minutes

dev default = 15 minutes

user default = 30 minutes

readonly default = 45 minutes

no default > 60 minutes
Fail if: Any role missing, mis‑mapped, or exceeding 60 minutes.

Code scan:  
Rule: CI searches for hard‑coded uniform idle timeout constants (e.g., 30 * MINUTE used for all roles).
Fail if: A single constant is applied across roles.

B. Unit/integration tests

Test 1 — Role defaults:  
Arrange: Create sessions as admin, dev, user, readonly.
Assert: Each session reports the expected default timeout.

Test 2 — Activity reset:  
Arrange: Simulate user activity just before timeout.
Assert: Idle timer resets; session does not expire prematurely.

Test 3 — Timeout enforcement:  
Arrange: Simulate inactivity beyond the role’s timeout.
Assert: Session is locked/logged out.

Test 4 — Admin override:  
Arrange: Admin sets custom timeout for a role (e.g., user → 20 minutes).
Assert:

New sessions use 20 minutes.

Change is logged.

Still ≤ 60 minutes.

C. CI failure conditions

Any role default missing or incorrect.

Any role default > 60 minutes without explicit “override” flag in config.

Tests for idle‑timeout behavior missing or failing.

Detection of a single global idle timeout applied to all roles.

3) Diagram: session lifecycle and idle‑timeout enforcement
text
          SESSION LIFECYCLE WITH ROLE-BASED TIMEOUTS
          ------------------------------------------

+-------------------------------+
| 1. User logs in               |
|    (role: admin/dev/user/ro)  |
+---------------+---------------+
                |
                v
+-------------------------------+
| 2. System assigns idle        |
|    timeout based on role:     |
|    - admin: 10 min            |
|    - dev: 15 min              |
|    - user: 30 min             |
|    - readonly: 45 min         |
+---------------+---------------+
                |
                v
+-------------------------------+
| 3. User activity loop         |
|    - input/API calls reset    |
|      last-activity timestamp  |
+---------------+---------------+
                |
                v
+-------------------------------+
| 4. Idle timer checks          |
|    now - last_activity >=     |
|    role_timeout ?             |
+---------------+---------------+
        |                 |
        | no              | yes
        v                 v
   (back to 3)     +----------------------+
                   | 5. Enforce timeout   |
                   |    - lock session    |
                   |    or log out        |
                   +----------------------+

---

### Q12 — is_protected scope: password resets, role changes, and username changes (TODO(IS_PROTECTED_SCOPE))

§17 defines `is_protected` as blocking deletion and deactivation; Round 8
extended it to also block suspension. TODO(IS_PROTECTED_SCOPE) has been open
since v1.11.0.

**Problem**: Three attack vectors against always-available accounts remain
unaddressed:

1. **Password reset by another admin**: §VII Admin Resets requires passing
   the resetting admin's own MFA challenge — but does not explicitly prevent
   one admin from resetting another admin's protected account.
2. **Role demotion**: §19 states role demotion requires no approval. An admin
   could demote the always-available `admin` account to `readonly`, effectively
   removing administrative capability without triggering the deletion guard.
3. **Username change**: §VII states `admin` and `dev` are fixed usernames for
   the always-available accounts; but no mechanism other than the fixed-name
   statement explicitly blocks renaming at the database API level.

**Questions**:
- Does `is_protected` block password resets initiated by other admins (as
  distinct from self-service password changes)?
- Does `is_protected` block role changes (both escalation and demotion)?
- Does `is_protected` block username changes beyond the existing "fixed
  username values" statement?
- Should TODO(IS_PROTECTED_SCOPE) be resolved in this round?

**Anwser**: Takeaway
is_protected MUST block all three of the following:

password resets initiated by other admins

role changes (both escalation and demotion)

username changes

And yes — TODO(IS_PROTECTED_SCOPE) must be resolved in this round.

This is the only way to guarantee that always‑available accounts remain always available, always privileged, and never modifiable by other admins.

1. Does is_protected block password resets by other admins?
Yes — it MUST.

If another admin can reset the password of a protected account, then:

the protected account is no longer protected

the attacker gains full control

the “always‑available” guarantee collapses

Therefore:

is_protected MUST block all password resets except self‑service resets by the account owner.

This includes:

admin‑initiated resets

API‑initiated resets

automated resets

Self‑service resets remain allowed because the account owner is trusted.

2. Does is_protected block role changes?
Yes — it MUST block both escalation and demotion.

Why?
Demotion attack:  
An admin demotes the protected admin account to readonly.
→ The system loses its guaranteed administrative foothold.

Escalation attack:  
An admin escalates a protected readonly account to admin.
→ Privilege boundaries collapse.

Therefore:

is_protected MUST freeze the role of the account.  
No role changes allowed — neither up nor down.

3. Does is_protected block username changes?
Yes — it MUST.

The constitution already states that admin and dev usernames are fixed, but:

this is a semantic rule

not an enforced rule

nothing in the DB/API prevents renaming today

If a protected account can be renamed:

audit logs break

recovery paths break

MFA bindings break

the “always‑available” identity becomes mutable

Therefore:

is_protected MUST block username changes at the API and DB layers.

4. Should TODO(IS_PROTECTED_SCOPE) be resolved now?
Yes — absolutely.

Leaving it open:

creates inconsistent implementations

undermines the entire protected‑account model

leaves three critical attack vectors unaddressed

blocks CI enforcement

confuses reviewers

This TODO is governance‑critical and must be closed in this revision.

Proposed Constitutional Text (ready to paste)
§17.X — Scope of is_protected (New Section)
§17.X.1 — Purpose  
The is_protected flag designates accounts that MUST remain permanently available, permanently privileged, and immune to administrative modification.

§17.X.2 — Password Reset Protection  
For accounts where is_protected == true:
– Self‑service password changes by the account owner are permitted.
– Password resets initiated by any other administrator or automated system are forbidden.
– Admin‑initiated resets MUST fail with a protected‑account error.

§17.X.3 — Role Change Protection  
For accounts where is_protected == true:
– Role changes (escalation or demotion) are forbidden.
– The role assigned at creation time is immutable.
– Attempts to modify the role MUST fail with a protected‑account error.

§17.X.4 — Username Protection  
For accounts where is_protected == true:
– The username is immutable.
– Renaming the account is forbidden at all layers (UI, API, DB).
– Attempts to rename MUST fail with a protected‑account error.

§17.X.5 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– protected accounts cannot be password‑reset by other admins
– protected accounts cannot be role‑changed
– protected accounts cannot be renamed
– all forbidden operations produce explicit, testable errors
– self‑service password changes remain allowed

1) Reviewer Checklist — is_protected Enforcement
This checklist ensures that protected accounts (admin, dev, and any future constitutionally protected identities) cannot be modified, weakened, or hijacked by other administrators or automated systems.

A. Password Reset Protection
Check:  
Admin‑initiated password resets fail for protected accounts.

Check:  
Only self‑service password changes by the protected account owner are allowed.

Check:  
Reset endpoints explicitly check is_protected == true before performing any action.

Fail if:

Any admin can reset another protected admin’s password.

Reset UI/API does not distinguish protected vs non‑protected accounts.

Reset attempts succeed silently or partially.

B. Role Change Protection
Check:  
Role changes (promotion or demotion) are blocked for protected accounts.

Check:  
The role of a protected account is immutable after creation.

Check:  
Attempts to modify the role produce a protected‑account error, not a generic failure.

Fail if:

An admin can demote the protected admin account to readonly.

An admin can escalate a protected readonly account to admin.

Role changes are allowed via DB migrations, API calls, or UI flows.

C. Username Protection
Check:  
Username changes for protected accounts are blocked at all layers:

UI

API

database persistence

Check:  
The system enforces immutability even if a developer attempts a direct DB write.

Fail if:

Protected usernames can be changed via any code path.

Username immutability relies solely on documentation or convention.

D. Deletion, Deactivation, Suspension
Check:  
Protected accounts cannot be:

deleted

deactivated

suspended

Check:  
All such attempts produce explicit, testable errors.

Fail if:

Suspension is allowed (this was fixed in Round 8 — must be enforced).

Deactivation is allowed via API or DB.

E. Logging & Auditability
Check:  
All blocked operations generate structured logs:

actor

target account

attempted operation

reason: "protected_account_violation"

Fail if:

Violations are not logged.

Logs lack actor or reason fields.

F. Test Coverage
Check:  
Automated tests cover:

blocked password resets

blocked role changes

blocked username changes

blocked deletion/deactivation/suspension

allowed self‑service password changes

Fail if:

Tests only cover deletion/deactivation but not role/username/password.

Tests do not assert explicit protected‑account errors.

2) CI Enforcement Spec — is_protected Compliance
This spec ensures CI automatically enforces the constitutional guarantees around protected accounts.

A. Static Analysis Rules
CI MUST detect:

Any code path that performs:

password reset

role change

username change

deletion

deactivation

suspension

without checking is_protected first.

Any direct DB write that modifies:

password_hash

role

username

is_active

is_suspended

without a guard clause.

CI MUST fail if:

A protected‑account guard is missing.

A protected‑account guard is present but inverted or incorrect.

A code path bypasses the guard via internal APIs.

B. Unit Test Requirements
Test 1 — Password Reset Block
Attempt admin‑initiated reset on protected account → MUST fail.

Test 2 — Self‑Service Password Change Allowed
Protected account changes its own password → MUST succeed.

Test 3 — Role Change Block
Attempt to change role of protected account → MUST fail.

Test 4 — Username Change Block
Attempt to rename protected account → MUST fail.

Test 5 — Deletion/Deactivation/Suspension Block
Attempt any of these operations → MUST fail.

Test 6 — Logging
Each blocked operation MUST produce a structured log entry.

C. Integration Test Requirements
Test 7 — API Enforcement
All API endpoints must reject protected‑account modifications.

Test 8 — UI Enforcement
UI must hide or disable modification controls for protected accounts.

Test 9 — DB Enforcement
Attempt direct DB update in test harness → MUST be rejected by DB constraints or service layer.

D. CI Failure Conditions
CI MUST fail if:

Any protected‑account modification succeeds.

Any test for protected‑account behavior is missing.

Any code path bypasses the protected‑account guard.

Logging is incomplete or missing.

Username, role, or password immutability is not enforced.

---

### Q13 — Crash recovery session clearing: behaviour and sequence (TODO(CRASH_RECOVERY_SESSION))

§VII Session Controls states: "Tokens or session secrets MUST be stored in
memory only and cleared on logout or **crash recovery**." TODO(CRASH_RECOVERY_SESSION)
has been open since v1.11.0, deferring the definition of crash recovery
clearing behaviour.

**Problem**: "Cleared on crash recovery" is ambiguous about both *when* and
*how* clearing occurs:

- *When*: Does clearing happen in the crash handler (in-process, before the
  process terminates), on next startup (before any preference or session
  operations), or both?
- *How*: If the process dies unexpectedly (SIGKILL, OOM killer, power loss),
  there is no in-process handler running. What constitutes "cleared" in that
  scenario?

**Questions**:
- Does crash recovery clearing occur within the crash handler (before process
  termination) or on next startup?
- If on next startup: must the application check for and purge any in-memory
  state persisted by OS swap, crash dumps, or core files?
- Is the application required to detect a previous crash state on startup (e.g.,
  via a crash sentinel file) and refuse to restore the prior session?
- Should TODO(CRASH_RECOVERY_SESSION) be resolved in this round?

**Anwser**: Takeaway
Crash‑recovery clearing MUST occur on next startup, not only in the crash handler.
The application MUST detect prior crash state and MUST purge all session secrets before performing any session or preference operations.
Crash handlers MAY attempt in‑process clearing, but this is best‑effort only and cannot be relied upon.
Yes — TODO(CRASH_RECOVERY_SESSION) must be resolved in this round.

This is the only model that is secure, portable, and testable.

1. Does crash‑recovery clearing occur in the crash handler or on next startup?
Answer: Both — but only one is mandatory.
A. Crash handler clearing (optional, best‑effort)
If the process receives a recoverable signal (e.g., SIGTERM, SIGINT), it MAY attempt to clear in‑memory secrets before exiting.

But this is not sufficient because:

SIGKILL cannot be caught

OOM killer cannot be caught

power loss cannot be caught

kernel panic cannot be caught

container eviction cannot be caught

Therefore:

B. Startup‑time clearing (mandatory)
On startup, the application MUST:

Detect whether the previous shutdown was clean.

If not clean, treat it as a crash.

Purge all session secrets unconditionally.

Refuse to restore any prior session.

Start with a clean session state.

This is the only reliable way to guarantee clearing after unexpected termination.

2. Must the application purge OS‑persisted memory (swap, crash dumps, core files)?
Yes — to the extent possible.
The constitution cannot require the application to override OS‑level behavior, but it CAN require:

Crash dumps MUST NOT contain session secrets.  
(Disable dumps or scrub sensitive memory regions.)

Swap MUST NOT contain session secrets.  
(Use mlock/VirtualLock or equivalent to pin session memory.)

Core files MUST NOT contain session secrets.  
(Disable core dumps or mark memory as non‑dumpable.)

Thus:

The application MUST ensure that no OS‑level persistence mechanism can retain session secrets.

This is the only interpretation consistent with “MUST be stored in memory only.”

3. Must the application detect a previous crash state on startup?
Yes — MUST.
This is the heart of crash‑recovery clearing.

The application MUST:

maintain a crash sentinel (e.g., “clean shutdown” flag)

set it to “dirty” on startup

set it to “clean” only on graceful shutdown

on next startup:

if sentinel = dirty → previous run crashed

purge all session secrets

refuse to restore any session

This is deterministic, testable, and reviewer‑proof.

4. Should TODO(CRASH_RECOVERY_SESSION) be resolved now?
Yes — MUST.
Leaving it unresolved:

breaks the security model

leaves session secrets exposed after crashes

creates inconsistent implementations

prevents CI enforcement

confuses reviewers

violates the “memory‑only” requirement

This TODO is security‑critical and must be closed in this round.

Proposed Constitutional Text (ready to paste)
§VII.W — Crash‑Recovery Session Clearing (New Section)
§VII.W.1 — Purpose  
Session tokens and session secrets MUST remain in volatile memory only.
They MUST NOT survive process termination, crash, or restart.

§VII.W.2 — Crash Handler Clearing (Best‑Effort)  
Implementations MAY attempt to clear session secrets in crash handlers for recoverable signals.
This behavior is best‑effort only and MUST NOT be relied upon for correctness.

§VII.W.3 — Startup‑Time Clearing (Mandatory)  
On startup, the implementation MUST determine whether the previous shutdown was clean.
If the previous shutdown was not clean, the implementation MUST:
– purge all session secrets;
– refuse to restore any prior session;
– begin with a clean session state.

§VII.W.4 — Crash Sentinel  
Implementations MUST maintain a crash sentinel indicating clean vs unclean shutdown.
The sentinel MUST be set to “dirty” on startup and set to “clean” only on graceful shutdown.

§VII.W.5 — OS‑Level Persistence Protections  
Implementations MUST ensure that session secrets do not leak into:
– swap
– crash dumps
– core files
– hibernation images
Implementations MUST disable or restrict these mechanisms or mark session memory as non‑dumpable.

§VII.W.6 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– crash sentinel logic is implemented;
– startup‑time clearing is unconditional after unclean shutdown;
– no session is restored after a crash;
– session secrets are excluded from swap and crash dumps;
– crash‑recovery behavior is covered by automated tests.
1) Reviewer checklist for crash‑recovery compliance
A. Session secret lifecycle

In‑memory only:  
Check: Session tokens/secrets are only ever stored in volatile memory, not in files, DB, or config.
Fail if: Any persistent storage of session secrets exists.

No session restore after crash:  
Check: After an unclean shutdown, the application never restores a prior session.
Fail if: “Remembered” sessions survive a simulated crash.

B. Crash sentinel behavior

Sentinel semantics:  
Check: There is a clear “clean vs dirty” sentinel (file/flag/record).
Check: Sentinel is set to dirty on startup, clean on graceful shutdown.
Fail if: Sentinel is only written on shutdown, or never set to dirty.

Crash detection:  
Check: On startup, if sentinel is dirty or missing, the run is treated as a crash.
Fail if: Startup proceeds normally without checking sentinel.

C. Startup‑time clearing

Mandatory purge:  
Check: On detecting a prior crash, the app purges all session state before any session/preference operations.
Fail if: Any session is reused or “resumed” after a crash.

User experience:  
Check: Users are required to re‑authenticate after crash recovery.
Fail if: Users remain logged in.

D. OS‑level persistence protections

Swap / paging:  
Check: Sensitive session memory is pinned or otherwise protected from being swapped where supported.
Crash dumps / core files:  
Check: Crash dumps are disabled or configured to exclude session memory.
Fail if: Session secrets can appear in core dumps or swap by design.

E. Tests & documentation

Tests:  
Check: Automated tests simulate crash (unclean shutdown) and verify:

sentinel behavior

no session restore

forced re‑login

Docs:  
Check: Crash‑recovery behavior is documented and matches implementation.

2) CI enforcement spec
A. Static checks

Sentinel presence:  
Rule: CI verifies existence of crash‑sentinel logic (e.g., functions like markDirtyOnStartup, markCleanOnShutdown, checkCrashOnStartup).
Fail if: No code path sets a “dirty” flag on startup or “clean” on graceful shutdown.

Session restore paths:  
Rule: CI scans for any “restore session” logic and asserts it is gated by a “clean shutdown” check.
Fail if: Sessions can be restored without consulting the sentinel.

Persistent storage:  
Rule: CI searches for session tokens/secrets being written to disk/DB.
Fail if: Any such writes are found.

B. Unit/integration tests (must run in CI)

Test 1 — Clean shutdown path:

Start app → login → mark sentinel dirty.

Graceful shutdown → sentinel set to clean.

Next startup: app sees clean sentinel → normal login behavior.

Test 2 — Crash path:

Start app → login → sentinel dirty.

Simulate crash (no graceful shutdown, sentinel remains dirty).

Next startup: app detects dirty sentinel → purges sessions → requires re‑login.

Test 3 — No session restore:

After simulated crash, verify no API/UI path can access prior session context.

Test 4 — OS‑level protections (where testable):

Verify configuration flags for disabling core dumps / marking memory non‑dumpable are set in supported environments.

C. CI failure conditions

CI MUST fail if:

No crash sentinel logic is present.

Startup does not branch on sentinel state.

Any test shows a session surviving a simulated crash.

Session tokens are written to persistent storage.

Crash‑recovery tests are missing or skipped.

3) Reference implementation of crash sentinel logic
Here’s a language‑agnostic pattern, with a concrete example in Python‑style pseudocode.

Conceptual model
On startup:

Mark sentinel dirty.

Check previous sentinel state:

If previously dirty → treat as crash → purge sessions.

On graceful shutdown:

Mark sentinel clean.

Pseudocode
python
import json
from pathlib import Path

SENTINEL_PATH = Path("/var/lib/app/crash_sentinel.json")

def load_sentinel():
    if not SENTINEL_PATH.exists():
        return {"state": "unknown"}
    return json.loads(SENTINEL_PATH.read_text())

def save_sentinel(state: str):
    SENTINEL_PATH.write_text(json.dumps({"state": state}))

def mark_dirty_on_startup():
    save_sentinel("dirty")

def mark_clean_on_shutdown():
    save_sentinel("clean")

def purge_all_sessions():
    # Implementation-specific: clear in-memory stores, session DB tables, caches, etc.
    pass

def on_startup():
    previous = load_sentinel()

    # Mark this run as dirty immediately
    mark_dirty_on_startup()

    if previous.get("state") != "clean":
        # Previous run did not shut down cleanly → treat as crash
        purge_all_sessions()
        # Optionally log: "Crash detected, sessions purged"

    # Continue normal startup (no session restore allowed here)

def on_graceful_shutdown():
    # Perform normal shutdown tasks...
    mark_clean_on_shutdown()
Key properties:

Dirty first: Sentinel is set to dirty at the very beginning of startup.

Clean only on success: Only a fully graceful shutdown sets it to clean.

Crash detection: Any state other than "clean" is treated as a crash.

Purge before use: Session purge happens before any session/preference logic runs.

---

### Q14 — Audit log origin metadata: minimum required fields (TODO(AUDIT_ORIGIN_METADATA))

§16 states: "Each attempt (success or failure) MUST be logged with timestamp
and origin metadata." TODO(AUDIT_ORIGIN_METADATA) has been open since v1.11.0.

**Problem**: "Origin metadata" is constitutionally required but undefined.
Without a minimum field definition, implementations may log very different
data. One may log IP address and hostname; another may log only a session ID;
another may log nothing beyond what is already required (timestamp, username,
actor). An audit log that is legally or operationally useless cannot be
distinguished from a compliant one without a field definition.

There is also a privacy consideration: storing IP addresses or hostnames in
audit logs may require GDPR compliance decisions in regulated environments.

**Questions**:
- What fields are required at minimum for "origin metadata"? Candidates:
  IP address, hostname, OS-level username executing the application, port,
  protocol, or application session ID.
- Are there privacy or GDPR constraints that should limit which fields are
  constitutionally required (e.g., IP address may be PII in some jurisdictions)?
- Is the minimum field list the same for all event types, or are some fields
  required only for specific events (e.g., IP address for `login_failure`)?
- Should TODO(AUDIT_ORIGIN_METADATA) be resolved in this round?

**Anwser**: Takeaway
“Origin metadata” MUST have a constitutionally defined minimum field set.
The minimum MUST balance forensic value with privacy constraints, and MUST be uniform across all event types, with a few additional fields required only for network‑originating events.

Yes — TODO(AUDIT_ORIGIN_METADATA) must be resolved in this round.

1. What fields are required at minimum for “origin metadata”?
We need a set that is:

universally available

privacy‑respectful

legally defensible

operationally useful

consistent across platforms

The correct constitutional minimum is:

Minimum Origin Metadata (Required for ALL audit events)
Field	Purpose	Notes
actor_username	Who performed the action	Already required, but part of origin context
session_id	Which authenticated session produced the event	Non‑PII, stable, essential
device_id	Logical device identifier (hashed)	Avoids raw hardware identifiers
app_instance_id	Which app instance generated the event	Required for multi‑node deployments
These four fields are non‑PII, universally available, and sufficient for baseline forensic traceability.

Additional Required Fields for Network‑Originating Events
For events that originate from a network request (e.g., login, API call):

Field	Purpose	Notes
client_ip (pseudonymized)	Network origin	MUST be hashed or truncated to avoid storing raw PII
user_agent	Device/browser fingerprint	Non‑PII when stored as raw string
protocol	http/https, ssh, etc.	Useful for forensic reconstruction
Why pseudonymized IP?
Raw IP addresses are PII under GDPR.

Hashing or truncation preserves forensic value (correlation) without storing personal data.

This is the industry‑standard compromise.

2. Are there privacy/GDPR constraints?
Yes — and they must shape the constitutional minimum.
Raw IP addresses are PII → cannot be required constitutionally.

Hashed or truncated IP is not PII and is GDPR‑safe.

Hostname may contain personal data → cannot be required.

OS‑level username is often personal → cannot be required.

Device fingerprinting must be minimal and non‑unique.

Therefore:

The constitution MUST require pseudonymized IP, not raw IP.  
The constitution MUST forbid requiring hostnames or OS usernames.

3. Is the minimum field list the same for all event types?
Mostly yes — with one exception.
All events must include the core four fields.

Network‑originating events must include the network trio (pseudonymized IP, user_agent, protocol).

Local events (e.g., background tasks) omit network fields.

This is clean, deterministic, and reviewer‑friendly.

4. Should TODO(AUDIT_ORIGIN_METADATA) be resolved now?
Yes — MUST.
Leaving it unresolved:

breaks audit portability

prevents CI enforcement

creates inconsistent logs

risks GDPR violations

undermines forensic usefulness

This TODO is governance‑critical and must be closed in this revision.

Proposed Constitutional Text (ready to paste)
§16.X — Origin Metadata Requirements (New Section)
§16.X.1 — Purpose  
Origin metadata provides the contextual information necessary to attribute audit events to a specific actor, session, device, and network origin.

§16.X.2 — Minimum Origin Metadata (All Events)  
All audit events MUST include the following origin metadata fields:
– actor_username  
– session_id  
– device_id (hashed or pseudonymized)
– app_instance_id

§16.X.3 — Additional Metadata for Network‑Originating Events  
For events originating from a network request, the following fields MUST also be included:
– client_ip_hash (pseudonymized; raw IP MUST NOT be stored)
– user_agent  
– protocol

§16.X.4 — Privacy Constraints  
Implementations MUST NOT store:
– raw IP addresses
– hostnames
– OS‑level usernames
– hardware serial numbers
– any unique device identifiers beyond a pseudonymized device_id

§16.X.5 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– all audit events include the required minimum fields
– network events include the required network fields
– no prohibited PII fields are logged
– pseudonymization of IP and device identifiers is implemented
– audit logs are consistent across all event types

1) Reviewer Checklist — Audit‑Origin Metadata Compliance
This checklist ensures that every audit event contains the constitutionally required origin metadata, avoids prohibited PII, and maintains forensic usefulness.

A. Minimum Metadata (All Events)
Check: Every audit event includes the four mandatory fields:

actor_username

session_id

device_id (hashed/pseudonymized)

app_instance_id

Fail if:

Any of these fields are missing.

Device identifiers are stored in raw form (serial numbers, MAC addresses, etc.).

Session ID is omitted for background tasks (it must be present but may be a synthetic “system” session).

B. Network‑Originating Events
Check: For events triggered by a network request, the following fields are present:

client_ip_hash (pseudonymized)

user_agent

protocol

Fail if:

Raw IP addresses are logged.

Hostnames are logged.

OS‑level usernames are logged.

Network events lack network metadata.

C. Privacy & GDPR Compliance
Check: Implementation uses pseudonymization for:

IP addresses

device identifiers

Check: No prohibited PII is logged:

raw IP

hostname

OS username

hardware serial numbers

unique device fingerprints

Fail if: Any PII appears in logs without explicit opt‑in and documented justification.

D. Consistency Across Event Types
Check: All event types (login, logout, preference change, MFA events, admin actions, failures) include the same minimum metadata.

Fail if:

Some events include origin metadata while others omit it.

Metadata schema varies unpredictably across event types.

E. Logging Format & Structure
Check: Metadata fields are:

structured

machine‑parseable

consistently named

consistently typed

Fail if:

Metadata is embedded in free‑text messages.

Field names vary across events.

F. Test Coverage
Check: Automated tests verify:

presence of required fields

absence of prohibited fields

pseudonymization behavior

correct handling of network vs non‑network events

Fail if:

Tests only check login events but not admin actions or failures.

Tests do not validate pseudonymization.

2) CI Enforcement Spec — Audit‑Origin Metadata
This spec ensures CI automatically enforces the constitutional requirements for origin metadata.

A. Static Analysis Rules
CI MUST detect:

presence of required fields in audit‑logging code paths

absence of prohibited PII fields

pseudonymization functions for IP and device identifiers

consistent field names across all event types

CI MUST fail if:

Raw IP addresses appear in logging code.

Hostnames or OS usernames are logged.

Device identifiers are logged without hashing.

Any audit event type lacks the required metadata fields.

B. Schema Validation
CI MUST validate that the audit‑log schema includes:

actor_username

session_id

device_id

app_instance_id

client_ip_hash (for network events)

user_agent

protocol

CI MUST fail if:

Fields are missing.

Fields are inconsistently typed.

Fields are renamed without migration logic.

C. Unit Tests (Required)
Test 1 — All Events Include Minimum Metadata
Generate each event type → assert presence of the four core fields.

Test 2 — Network Events Include Network Metadata
Simulate network request → assert presence of client_ip_hash, user_agent, protocol.

Test 3 — Pseudonymization
Assert:

IP hashing function is applied

device ID hashing function is applied

raw values never appear in logs

Test 4 — Prohibited Fields
Assert logs do not contain:

raw IP

hostname

OS username

hardware serial numbers

Test 5 — Consistency
Assert all event types use the same field names and structure.

D. Integration Tests
Test 6 — End‑to‑End Logging
Trigger real user actions (login, MFA, preference change, admin action) → verify logs contain required metadata.

Test 7 — Failure Events
Simulate login failure, MFA failure, permission denial → verify metadata is still present.

E. CI Failure Conditions
CI MUST fail if:

Any required metadata field is missing from any event type.

Any prohibited PII appears in logs.

Pseudonymization is not applied.

Logging schema is inconsistent.

Tests for origin metadata are missing or incomplete.

Constitutional Amendment Patch — §16.X (Origin Metadata Requirements)
diff
diff --git a/constitution.md b/constitution.md
index 1234abc..7890def 100644
--- a/constitution.md
+++ b/constitution.md
@@ -310,6 +310,86 @@
  §16 — Audit Logging
  -------------------

+§16.X — Origin Metadata Requirements
+------------------------------------
+
+§16.X.1 — Purpose
+------------------
+Origin metadata provides the contextual information necessary to attribute
+audit events to a specific actor, session, device, and network origin. It
+ensures forensic usefulness while respecting privacy and regulatory
+constraints.
+
+§16.X.2 — Minimum Origin Metadata (All Events)
+----------------------------------------------
+All audit events MUST include the following origin metadata fields:
+
+- `actor_username`
+- `session_id`
+- `device_id` (hashed or pseudonymized)
+- `app_instance_id`
+
+These fields MUST be present regardless of event type, including background
+tasks, administrative actions, authentication events, and failures.
+
+§16.X.3 — Additional Metadata for Network-Originating Events
+------------------------------------------------------------
+For events originating from a network request, the following fields MUST also
+be included:
+
+- `client_ip_hash` (pseudonymized; raw IP MUST NOT be stored)
+- `user_agent`
+- `protocol`
+
+If an event does not originate from a network request (e.g., scheduled task,
+local system action), these fields MAY be omitted.
+
+§16.X.4 — Privacy Constraints
+-----------------------------
+Implementations MUST NOT store the following in audit logs:
+
+- raw IP addresses
+- hostnames
+- OS-level usernames
+- hardware serial numbers
+- unique device identifiers beyond a pseudonymized `device_id`
+
+Pseudonymization MUST be applied using a stable, one-way hashing mechanism
+that allows correlation across events without revealing personal data.
+
+§16.X.5 — Field Consistency
+---------------------------
+All audit events MUST use consistent field names, types, and structures for
+origin metadata. Implementations MUST NOT vary field names across event
+types or modules.
+
+§16.X.6 — Deterministic Reviewability
+-------------------------------------
+CI and reviewers MUST verify that:
+
+- all audit events include the required minimum metadata fields;
+- network-originating events include the required network metadata fields;
+- no prohibited PII fields are logged;
+- pseudonymization of IP addresses and device identifiers is implemented;
+- origin metadata is consistent across all event types;
+- automated tests cover presence, absence, and pseudonymization behavior.
+
+§16.X.7 — Backward Compatibility
+--------------------------------
+Existing audit logs MAY omit fields introduced in this section. However,
+all new audit events generated after this amendment MUST comply fully with
+§16.X.
+

---

## §VIII — Privacy, PII Protection & Data Minimization

### Q15 — PII scan results: proactive display or user-initiated access?

§VIII states: "Detection results MUST be reported to the user without automatic
deletion; remediation requires explicit user confirmation." The delivery
mechanism for this report is not specified.

**Problem**: Two UX models satisfy the literal requirement:

- **(a)** Results are placed in a report accessible through a menu, dedicated
  panel, or dashboard that the user must navigate to. This meets "reported"
  but allows results to be ignored indefinitely.
- **(b)** Results surface automatically (e.g., a modal alert, persistent
  banner, or forced-focus overlay) when detection completes, ensuring the user
  cannot proceed without acknowledging them.

This distinction has significant behavioral consequences for background or
scheduled scans — a model-(a) background scan may detect PII that goes
unnoticed for weeks.

**Questions**:
- Must PII scan results be surfaced *proactively* (shown automatically without
  requiring user navigation) when detection completes?
- Or is it sufficient to place results in a user-accessible location
  (report panel, notification badge, dashboard tile) that the user may review
  at their discretion?
- Does the answer differ between *user-initiated* scans and
  *background/scheduled* scans?
- If proactive display is required for background scans, must it interrupt the
  user's current workflow (modal) or may it be non-interrupting (banner,
  notification badge)?

**Anwser**: Takeaway
PII scan results MUST be surfaced proactively for background/scheduled scans, but MAY be user‑initiated for manual scans.
Proactive surfacing MUST be non‑interrupting (banner, notification, badge), not modal or workflow‑blocking.
Yes — TODO(AUDIT_ORIGIN_METADATA) must be resolved in this round.

This preserves user agency, avoids dark‑pattern coercion, and ensures PII findings cannot be silently ignored.

1. Must PII scan results be surfaced proactively?
A. For background/scheduled scans → YES (MUST).
If a background scan detects PII and the result is hidden behind a menu:

the user may never see it

the privacy guarantee collapses

the system silently accumulates sensitive data

the constitutional requirement (“MUST be reported”) becomes meaningless

Therefore:

Background/scheduled scans MUST surface results proactively.

But:

They MUST NOT interrupt the user’s workflow with a modal.

Instead, use:

persistent banner

notification badge

non‑blocking alert

“PII detected — review required” ribbon

This ensures visibility without coercion.

B. For user‑initiated scans → NO (not required).
If the user explicitly triggers a scan:

they are already engaged

they expect results

surfacing them in the same panel is sufficient

Therefore:

User‑initiated scans MAY display results inline without proactive surfacing.

2. Is it sufficient to place results in a user‑accessible location?
Only for user‑initiated scans.
For background scans, no — because:

“accessible” is not “reported”

users rarely check dashboards proactively

privacy risks accumulate silently

So:

Background scan results MUST be surfaced automatically.  
User‑initiated scan results MAY be placed in a panel.

3. Does the answer differ between user‑initiated and background scans?
Yes — MUST differ.
Scan Type	Required Behavior
User‑initiated	Inline display is sufficient
Background / scheduled	MUST proactively surface results
This distinction is essential for privacy and user agency.

4. If proactive display is required, must it interrupt the user?
No — MUST NOT interrupt.
A modal or forced‑focus overlay:

is coercive

breaks workflows

violates accessibility norms

creates dark‑pattern risk

Therefore:

Proactive surfacing MUST be non‑interrupting.  
Banners, badges, notifications are allowed.  
Modals are forbidden unless the user explicitly requested the scan.

Proposed Constitutional Text (ready to paste)
§VIII.X — PII Scan Result Delivery Requirements (New Section)
§VIII.X.1 — Purpose  
PII detection results MUST be visible to the user in a timely and non‑coercive manner, ensuring informed remediation without silent accumulation of sensitive data.

§VIII.X.2 — User‑Initiated Scans  
For scans explicitly initiated by the user, results MAY be displayed inline within the scan panel or results view.
Proactive surfacing is NOT required.

§VIII.X.3 — Background and Scheduled Scans  
For scans initiated automatically (background or scheduled), results MUST be surfaced proactively to the user.
Proactive surfacing MUST be non‑interrupting and MAY take the form of:
– a persistent banner
– a notification badge
– a non‑modal alert
– a dashboard ribbon
Modal dialogs or forced‑focus overlays MUST NOT be used.

§VIII.X.4 — User Agency and Remediation  
PII MUST NOT be deleted automatically.
Remediation requires explicit user confirmation, regardless of scan type.

§VIII.X.5 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– background scans surface results proactively
– user‑initiated scans may display results inline
– proactive surfacing is non‑interrupting
– no modal or blocking UI is used for background scans
– remediation requires explicit user confirmation

1) Reviewer Checklist — PII‑Scan UX Compliance
This checklist ensures that PII‑scan results are surfaced in a way that satisfies §VIII’s privacy guarantees, preserves user agency, and prevents silent accumulation of sensitive data.

A. Background/Scheduled Scans — Proactive Surfacing
Check:  
Background or scheduled scans surface results automatically when detection completes.

Check:  
Proactive surfacing is non‑interrupting, using one of:

persistent banner

notification badge

dashboard ribbon

non‑modal alert

Fail if:

Results are hidden behind a menu or panel.

User must navigate manually to discover findings.

A modal or forced‑focus overlay is used for background scans.

B. User‑Initiated Scans — Inline Display
Check:  
User‑initiated scans may display results inline within the scan panel.

Check:  
Inline display is immediate and visible within the context where the user initiated the scan.

Fail if:

User‑initiated scans require navigating to a separate location to see results.

Results are delayed or hidden.

C. No Automatic Deletion
Check:  
PII is never deleted automatically.

Check:  
Remediation requires explicit user confirmation (button, checkbox, or equivalent).

Fail if:

Any PII is removed without user action.

“Auto‑clean” or “silent cleanup” exists.

D. Visibility & Persistence
Check:  
Proactive indicators (banner, badge, ribbon) remain visible until the user acknowledges or reviews the results.

Fail if:

Indicators disappear automatically.

Indicators are easy to miss (e.g., transient toast notifications).

E. Accessibility & Non‑Coercion
Check:  
Proactive surfacing does not block workflows (no modals, no forced focus).

Check:  
Indicators meet accessibility requirements (contrast, screen‑reader labels).

Fail if:

User is forced to stop their work to view results.

Indicators are visually inaccessible.

F. Test Coverage
Check:  
Automated tests cover:

background scan proactive surfacing

user‑initiated scan inline display

persistence of indicators

explicit confirmation for remediation

absence of modals for background scans

Fail if:

Tests only cover user‑initiated scans.

Tests do not verify proactive surfacing.

2) CI Enforcement Spec — PII‑Scan UX Compliance
This spec ensures CI automatically enforces the constitutional requirements for PII‑scan result delivery.

A. Static Analysis Rules
CI MUST detect:

presence of proactive‑surfacing logic for background scans

absence of modal dialogs in background‑scan code paths

presence of inline‑display logic for user‑initiated scans

presence of explicit user‑confirmation logic for remediation

absence of auto‑deletion code paths

CI MUST fail if:

Background scans do not trigger proactive surfacing.

A modal is used for background scan results.

Any code path deletes PII automatically.

Remediation does not require explicit confirmation.

B. Unit Test Requirements
Test 1 — Background Scan Proactive Surfacing
Simulate background scan → assert banner/badge/ribbon appears automatically.

Test 2 — User‑Initiated Scan Inline Display
Trigger manual scan → assert results appear inline in the scan panel.

Test 3 — No Modal for Background Scans
Simulate background scan → assert no modal or blocking UI is triggered.

Test 4 — Indicator Persistence
Simulate background scan → assert indicator remains until user acknowledges.

Test 5 — Explicit Remediation Confirmation
Attempt remediation → assert user confirmation is required.

Test 6 — No Automatic Deletion
Simulate detection → assert PII remains until user confirms deletion.

C. Integration Test Requirements
Test 7 — End‑to‑End Background Scan Flow
Background scan runs

Results surface proactively

User acknowledges

User chooses remediation

PII is deleted only after confirmation

Test 8 — Accessibility
Verify proactive indicators meet accessibility requirements (contrast, ARIA labels).

D. CI Failure Conditions
CI MUST fail if:

Background scans do not surface results automatically.

A modal is used for background scan results.

PII is deleted without explicit user confirmation.

Indicators are not persistent.

Tests for PII‑scan UX behavior are missing or incomplete.

---

## §IX — File Validation & Content Integrity

### Q16 — "Written by RFU itself": boundary definition for the validation exemption

§IX exempts "internal temporary files written and subsequently read back by
RFU itself" from per-`open()` validation. The boundary of "written by RFU
itself" is not formally defined.

**Problem**: Several edge cases are genuinely ambiguous:

1. **Cross-tool IPC**: Tool A writes a temp file, passes its path to Tool B
   via inter-process communication. Tool B reads it. Tool B did not write it.
2. **Plugin-written files**: A third-party plugin registered with
   ComponentGuardian writes a temp file that the core pipeline reads.
3. **Cross-session files**: An RFU tool writes a temp file in session 1; RFU
   reads it back in session 2.
4. **Shared temp directories**: Two RFU tool instances write to the OS temp
   directory; each reads files it did not write.

In edge cases 2–4, relaxing validation could allow a malicious file in a
shared temp directory to bypass detection.

**Questions**:
- Does "written by RFU itself" apply only when the reading and writing code
  paths are within the *same tool instance* in the *same process*?
- Or does it extend to any file written by any component of RFU within the
  same application session?
- Are plugin-written files considered "by RFU" if the plugin is registered
  with ComponentGuardian?
- Must files that cross process or session boundaries always be validated
  regardless of their origin?

**Anwser**: Takeaway
“Written by RFU itself” MUST mean written by the same tool instance, in the same process, during the same session, and consumed by the same instance without crossing any boundary.

Anything that crosses:

process boundary

tool boundary

plugin boundary

session boundary

temp‑directory boundary

MUST be validated.

This is the only interpretation that is secure, testable, and future‑proof.

1. Does the exemption apply only within the same tool instance and same process?
Yes — MUST.
The exemption applies only when:

the same process

the same tool instance

writes a file

and reads it back

without exposing it to any other component

This is the narrowest safe definition.

Anything broader becomes a privilege escalation vector.

2. Does it extend to any file written by any RFU component in the same session?
No — MUST NOT.
Session‑wide trust is unsafe because:

multiple tools may run in the same session

multiple processes may run in the same session

temp directories may be shared

plugins may run in the same session

Therefore:

Session‑wide trust is forbidden.  
Only same‑process, same‑instance trust is allowed.

3. Are plugin‑written files considered “by RFU”?
No — MUST NOT.
Even if a plugin is registered with ComponentGuardian:

it is third‑party code

it may be compromised

it may be malicious

it may be poorly written

it may run with different privileges

Therefore:

Plugin‑written files MUST be validated.  
Plugins never qualify for the exemption.

This is essential for supply‑chain security.

4. Must files that cross process or session boundaries always be validated?
Yes — MUST.
Any file that crosses:

process boundary

tool boundary

plugin boundary

session boundary

temp directory boundary

IPC boundary

MUST be validated, even if originally written by RFU.

This includes:

cross‑tool IPC

cross‑process pipelines

cross‑session reuse

shared temp directories

background tasks

scheduled tasks

plugin interactions

If the file leaves the originating process, the exemption evaporates.

Proposed Constitutional Text (ready to paste)
§IX.X — Definition of “Written by RFU Itself” (New Section)
§IX.X.1 — Purpose  
The exemption for “internal temporary files written and subsequently read back by RFU itself” applies only to files that never cross trust boundaries. This section defines the limits of that exemption.

§IX.X.2 — Same‑Process, Same‑Instance Requirement  
A file qualifies for the exemption only if:
– it is written by the same RFU tool instance;
– in the same process;
– during the same application session;
– and read back by that same instance without being exposed to any other component.

§IX.X.3 — Boundaries That Invalidate the Exemption  
The exemption MUST NOT apply if the file crosses any of the following boundaries:
– process boundary
– tool boundary
– plugin boundary
– session boundary
– inter‑process communication (IPC)
– shared temporary directories
– background or scheduled tasks
– any mechanism that exposes the file to another component

§IX.X.4 — Plugin‑Written Files  
Files written by third‑party plugins, even if registered with ComponentGuardian, MUST NOT qualify for the exemption.
Such files MUST undergo full validation before being read.

§IX.X.5 — Cross‑Session and Cross‑Process Files  
Files written in one session or process and read in another MUST always be validated, regardless of origin.

§IX.X.6 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– the exemption is applied only to same‑process, same‑instance files;
– plugin‑written files are always validated;
– cross‑tool, cross‑process, and cross‑session files are always validated;
– shared temp directories never bypass validation;
– all IPC‑transferred files undergo validation.

1) Reviewer checklist for §IX integrity enforcement
A. Exemption scope: same‑process, same‑instance only

Check: The “no‑validation” exemption is applied only when:

same process

same tool instance

same application session

file written and read by that same instance

Fail if: Any code treats “written by RFU” as:

“same session”

“same app”

“same temp directory”

“any RFU component”

B. Cross‑boundary files always validated

Check: Files are always validated when they cross:

process boundary

tool boundary

plugin boundary

session boundary

IPC boundary

shared temp directory

Fail if: Any cross‑boundary file can be opened without validation.

C. Plugin‑written files

Check: Files written by third‑party plugins are never treated as exempt.

Check: Plugin outputs are always passed through the validation pipeline before being read.

Fail if: Plugin‑written files are considered “internal” and bypass validation.

D. Cross‑tool IPC and shared temp

Check: When Tool A writes a file and Tool B reads it (via path, IPC, or shared temp), Tool B always validates before reading.

Fail if: Tool B assumes trust because Tool A is “also RFU”.

E. Cross‑session reuse

Check: Files written in session 1 and read in session 2 are always validated.

Fail if: Any “session cache” or “resume” mechanism reads files without validation.

F. Tests

Check: Automated tests cover:

same‑instance readback (exemption allowed)

cross‑tool read (validation required)

plugin output (validation required)

cross‑session read (validation required)

Fail if: Only the happy path (same‑instance) is tested.

2) CI enforcement spec
A. Static analysis rules

Rule: CI scans for file‑open/read operations and asserts:

either they call the validation pipeline, or

they are explicitly marked as “same‑instance exempt” with a guard.

Fail if:

Any file read lacks both validation and an explicit, scoped exemption.

Exemption annotations appear in plugin or cross‑tool code paths.

B. Exemption guard patterns

Rule: Exemption is only allowed behind a helper like open_internal_temp_same_instance(path) that:

verifies same process / same instance

is not callable from plugins or other tools

Fail if:

Exemption logic is duplicated ad‑hoc.

Helper is exposed to plugin or IPC layers.

C. Unit tests (must run in CI)

Test 1 — Same‑instance exemption:

Tool writes temp file, reads it back in same process/instance → allowed without validation.

Test 2 — Cross‑tool IPC:

Tool A writes file, Tool B reads → assert validation is invoked.

Test 3 — Plugin output:

Plugin writes file, core reads → assert validation is invoked.

Test 4 — Cross‑session:

Session 1 writes file, Session 2 reads → assert validation is invoked.

Test 5 — Shared temp directory:

Two instances write to same temp dir → assert each validates any file it did not create in‑process.

D. CI failure conditions

CI MUST fail if:

Any file read path bypasses validation without going through the tightly scoped exemption helper.

Exemption helper is used in plugin, IPC, or cross‑tool code.

Tests for cross‑boundary scenarios are missing or failing.

3) Reference implementation of the exemption logic
Here’s a language‑agnostic pattern, with concrete pseudocode (Python‑style) that encodes the same‑process, same‑instance, same‑session rule.

python
import os
import uuid
from pathlib import Path

APP_SESSION_ID = str(uuid.uuid4())
PROCESS_ID = os.getpid()

# In-memory registry of files that qualify for the exemption
_internal_temp_registry: set[tuple[str, int, str]] = set()
# Each entry: (absolute_path, process_id, app_session_id)

def register_internal_temp_file(path: Path) -> None:
    abs_path = str(path.resolve())
    _internal_temp_registry.add((abs_path, PROCESS_ID, APP_SESSION_ID))

def is_same_instance_internal_temp(path: Path) -> bool:
    abs_path = str(path.resolve())
    key = (abs_path, PROCESS_ID, APP_SESSION_ID)
    return key in _internal_temp_registry

def write_internal_temp_file(path: Path, data: bytes) -> None:
    # Only used by core RFU tool instance
    path.write_bytes(data)
    register_internal_temp_file(path)

def open_file_with_validation(path: Path, mode: str = "rb"):
    """
    Central entry point for all file reads.
    Applies validation unless the file is a same-instance internal temp file.
    """
    if is_same_instance_internal_temp(path):
        # Exemption: same process, same app session, same instance
        return path.open(mode)

    # For all other cases: validate before opening
    validate_file(path)
    return path.open(mode)

def validate_file(path: Path) -> None:
    """
    Full validation pipeline: content scanning, signature checks, etc.
    This is where ComponentGuardian and other validators plug in.
    """
    # Pseudocode:
    # - check extension / MIME
    # - run content scanners
    # - verify signatures / checksums
    # - enforce policy
    pass
Key properties:

Registry is in‑memory only → cannot be shared across processes or sessions.

Exemption is granted only if:

same process (PROCESS_ID)

same app session (APP_SESSION_ID)

file path registered by this instance

Any file crossing process, session, tool, or plugin boundaries will not be in the registry → it is always validated.

---

## §16 — Session Management & Auditing

### Q17 — Anomaly detection rolling 24-hour window: sliding or fixed-period?

§16 requires: "Automated anomaly detection MUST flag >10 failed attempts within
any rolling 24-hour window per user."

**Problem**: "Rolling" is operationally ambiguous. There are two common
implementations:

- **(a) Sliding window**: At every login attempt, count failures in the 24
  hours immediately preceding the current moment. Precise but requires
  per-event timestamp evaluation.
- **(b) Fixed-period window**: The 24-hour period is anchored to fixed
  boundaries (e.g., calendar date, account-creation epoch). Attack sequences
  straddling a boundary can produce 20 failures without triggering the alert.

The two models have meaningfully different security properties and
implementation costs. "Rolling" implies sliding, but this is not codified.

**Questions**:
- Is the 24-hour window a *sliding* window evaluated at the time of each
  login attempt?
- Or is it a *fixed-period* calendar window?
- What is the time resolution of the window evaluation (per-second accuracy
  required, per-minute, or coarser)?
- Does exceeding the threshold trigger an immediate alert at the triggering
  attempt, or is detection deferred to a periodic background check?

**Anwser**: Takeaway
The 24‑hour window MUST be a sliding window, evaluated per attempt, with per‑second resolution, and alerts MUST trigger immediately at the attempt that crosses the threshold.

Fixed‑period windows are forbidden because they create predictable blind spots attackers can exploit.

1. Is the 24‑hour window sliding or fixed?
Sliding — MUST.
A fixed window (e.g., midnight‑to‑midnight) allows:

9 failures at 23:59

9 failures at 00:01

→ 18 failures without detection

This is unacceptable.

Therefore:

The 24‑hour window MUST be sliding, evaluated at each login attempt.

This is the only model that is secure, deterministic, and reviewer‑proof.

2. What is the time resolution?
Per‑second resolution — MUST.
A 24‑hour window means:

now − 24h ≤ failure.timestamp < now

Evaluated with second‑level precision.

Coarser resolutions (minute/hour) create measurable gaps attackers can exploit.

3. When does detection trigger?
Immediately — MUST.
At the moment the N+1th failure occurs:

the system evaluates the sliding window

if >10 failures in the last 24 hours

→ anomaly is flagged instantly

No batching.
No periodic background checks.
No deferred evaluation.

This ensures:

real‑time detection

real‑time alerting

real‑time lockout or throttling (if configured)

4. Is periodic background detection allowed?
Optional, but NOT sufficient.
Background sweeps MAY exist for analytics, but:

They MUST NOT replace per‑attempt evaluation.

Real‑time detection is mandatory.

5. Proposed Constitutional Text (ready to paste)
§16.Y — Sliding 24‑Hour Anomaly Detection Window (New Section)
§16.Y.1 — Purpose  
The anomaly‑detection threshold of “>10 failed attempts within any rolling 24‑hour window per user” requires a precise definition of “rolling” to ensure consistent and secure implementation.

§16.Y.2 — Sliding Window Requirement  
The 24‑hour window MUST be implemented as a sliding window evaluated at the time of each authentication attempt.
Fixed‑period or calendar‑anchored windows MUST NOT be used.

§16.Y.3 — Time Resolution  
The sliding window MUST be evaluated with per‑second resolution.
Coarser resolutions (minute, hour, or calendar boundaries) MUST NOT be used.

§16.Y.4 — Immediate Detection  
Exceeding the threshold MUST trigger anomaly detection immediately at the attempt that causes the count of failed attempts in the preceding 24 hours to exceed 10.
Detection MUST NOT be deferred to periodic background tasks.

§16.Y.5 — Background Sweeps (Optional)  
Implementations MAY perform periodic background sweeps for analytics or reporting, but such sweeps MUST NOT replace per‑attempt sliding‑window evaluation.

§16.Y.6 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– sliding‑window logic is implemented;
– per‑attempt evaluation is performed;
– per‑second timestamp resolution is used;
– fixed‑period windows are not used;
– alerts trigger immediately upon threshold crossing.

1) Reviewer checklist for anomaly‑detection compliance
A. Sliding vs fixed window

Sliding window:  
Check: Implementation counts failures in the last 24 hours relative to now at each attempt.
Fail if: Logic is anchored to calendar days (e.g., midnight‑to‑midnight) or fixed periods.

Per‑attempt evaluation:  
Check: Every failed attempt triggers a fresh window evaluation.
Fail if: Detection only runs in periodic jobs (e.g., hourly sweeps).

B. Time resolution

Per‑second timestamps:  
Check: Failure timestamps are stored with at least second‑level precision.
Fail if: Timestamps are rounded to minutes/hours or truncated to dates.

Window definition:  
Check: Window is effectively

now
−
24
h
≤
failure_ts
<
now
Fail if: Any coarser or approximate window is used.

C. Threshold behavior

Strict “>10” semantics:  
Check: The 11th failure within the sliding 24‑hour window triggers the anomaly.
Fail if: Threshold is treated as “≥10” or any other value.

Immediate alerting:  
Check: Alert/flag is raised at the triggering attempt, not later.
Fail if: Detection is deferred to batch processing.

D. Per‑user scoping

User isolation:  
Check: Counts are maintained per user, not globally.
Fail if: Multiple users’ failures are aggregated into one counter.

E. Tests

Check: Automated tests cover:

failures clustered within 24h (alert)

failures straddling >24h (no alert)

boundary case at exactly 24h

Fail if: Only trivial “many failures in a row” is tested without time spacing.

2) CI enforcement spec
A. Static checks

Sliding window implementation:  
Rule: CI verifies presence of logic that filters failures by timestamp >= now - 24h.
Fail if: Logic groups by date or uses fixed calendar windows.

Per‑attempt evaluation:  
Rule: CI ensures anomaly detection is invoked from the authentication attempt path.
Fail if: Detection is only referenced from background/cron code.

B. Unit tests (must run in CI)

Test 1 — Below threshold:  
10 failures within 24h → no anomaly.

Test 2 — Threshold crossing:  
11th failure within 24h → anomaly flagged immediately.

Test 3 — Boundary at 24h:  
10 failures, then wait just over 24h, then another failure → no anomaly.

Test 4 — Straddling midnight:  
Failures before and after midnight but within 24h → anomaly still triggers.

C. CI failure conditions

CI MUST fail if:

Any test shows fixed‑period behavior (e.g., reset at midnight).

Anomaly detection is not called from the login/attempt path.

Timestamps lack sufficient precision.

Threshold semantics deviate from “>10 in last 24h per user”.

3) Reference implementation of sliding‑window logic
Here’s a simple, language‑agnostic pattern in Python‑style pseudocode:

python
from datetime import datetime, timedelta
from typing import List

class FailedAttempt:
    def __init__(self, user_id: str, timestamp: datetime):
        self.user_id = user_id
        self.timestamp = timestamp

def get_failed_attempts_for_user(user_id: str) -> List[FailedAttempt]:
    # Fetch from persistent store (DB, log, etc.)
    ...

THRESHOLD = 10
WINDOW = timedelta(hours=24)

def record_failed_attempt(user_id: str) -> bool:
    """
    Returns True if anomaly is triggered for this attempt, False otherwise.
    """
    now = datetime.utcnow()

    # Persist this failure
    save_failed_attempt(FailedAttempt(user_id, now))

    # Fetch all failures for this user
    failures = get_failed_attempts_for_user(user_id)

    # Sliding window: keep only failures in the last 24 hours
    window_start = now - WINDOW
    recent_failures = [
        f for f in failures
        if window_start <= f.timestamp <= now
    ]

    if len(recent_failures) > THRESHOLD:
        flag_anomaly(user_id=user_id, at=now, count=len(recent_failures))
        return True

    return False

def save_failed_attempt(attempt: FailedAttempt) -> None:
    ...

def flag_anomaly(user_id: str, at: datetime, count: int) -> None:
    # Log, alert, or trigger downstream actions
    ...
Key properties:

Sliding window: filters by now - 24h on every attempt.

Per‑attempt: called synchronously on each failure.

Per‑user: scoped by user_id.

Immediate alert: anomaly flagged in the same call that crosses the threshold.

---

## §21 — Additional Constraints: Theme Security

### Q18 — "System-wide theme change": formal definition required

§21 requires "Theme backups MUST be created before applying any system-wide
theme change." The phrase "system-wide theme change" is not formally defined.
The backup trigger — and therefore the backup obligation — depends entirely on
this definition.

**Problem**: The following operations are all ambiguous with respect to whether
they constitute a "system-wide theme change":

| Operation | Ambiguous? |
|---|---|
| Modifying a token value in an existing system-wide preset | Clearly yes |
| Creating a new system-wide preset (no existing preset modified) | Unclear |
| Deleting an existing system-wide preset | Unclear |
| Switching the active system-wide preset (no preset values change) | Unclear |
| Renaming a system-wide preset (values unchanged, label changes) | Unclear |

Scenarios 2–5 each result in a different system-wide theme state but may not
be perceived as a "change to an existing preset." Storage and operational
behaviour differ depending on the answer.

**Questions**:
- Is a "system-wide theme change" limited to modifications of token values
  within an existing system-wide preset?
- Does *creating* a new system-wide preset constitute a change requiring a
  backup?
- Does *deleting* a system-wide preset constitute a change requiring a backup?
- Does *switching the active system-wide preset* (changing which preset is
  applied, without modifying any preset's values) constitute a change
  requiring a backup?
- Does a pure *rename* of a system-wide preset (no value changes) constitute
  a change requiring a backup?

**Anwser**: Takeaway
A system‑wide theme change means any operation that alters the effective system‑wide theme state, not just token edits.
Therefore, all five operations (modify, create, delete, switch, rename) MUST trigger a backup.

This is the only definition that is secure, deterministic, and reviewer‑proof.

1. Is a system‑wide theme change limited to modifying token values?
No — MUST NOT be limited.
If we only trigger backups on token edits, we miss:

preset creation

preset deletion

preset switching

preset renaming

All of which change the system‑wide theme state.

Therefore:

Token edits are one type of system‑wide theme change, but not the only one.

2. Does creating a new system‑wide preset require a backup?
Yes — MUST.
Creating a new preset changes:

the available preset set

the fallback resolution order

the system‑wide theme state graph

Even if no preset is currently active, the system’s theme configuration has changed.

Therefore:

Preset creation MUST trigger a backup.

3. Does deleting a system‑wide preset require a backup?
Yes — MUST.
Deletion is destructive and irreversible.
It changes:

the preset set

the active preset’s fallback chain

the system‑wide theme state

Therefore:

Preset deletion MUST trigger a backup.

4. Does switching the active system‑wide preset require a backup?
Yes — MUST.
Switching presets changes the effective theme applied to the entire system, even if no preset values change.

This is the most visible and impactful theme change.

Therefore:

Preset switching MUST trigger a backup.

5. Does renaming a system‑wide preset require a backup?
Yes — MUST.
Even though values don’t change, renaming:

changes the preset identity

affects references

affects auditability

affects deterministic preset resolution

Therefore:

Preset renaming MUST trigger a backup.

Unified Definition
A system‑wide theme change is:

Any operation that alters the effective system‑wide theme state, including but not limited to:
– modifying token values
– creating a preset
– deleting a preset
– switching the active preset
– renaming a preset

If the system‑wide theme state changes, a backup MUST be created.

Proposed Constitutional Text (ready to paste)
§21.X — Definition of “System‑Wide Theme Change” (New Section)
§21.X.1 — Purpose  
System‑wide theme changes affect the global appearance, accessibility, and user experience of the application. To ensure recoverability, a backup MUST be created before any such change.

§21.X.2 — Definition  
A “system‑wide theme change” is any operation that alters the effective system‑wide theme state. This includes, but is not limited to:
– modifying token values in an existing system‑wide preset;
– creating a new system‑wide preset;
– deleting an existing system‑wide preset;
– switching the active system‑wide preset;
– renaming a system‑wide preset.

§21.X.3 — Backup Requirement  
Before performing any system‑wide theme change as defined in §21.X.2, the implementation MUST create a theme backup.

§21.X.4 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– all operations listed in §21.X.2 trigger backups;
– no system‑wide theme change can occur without a backup;
– backups occur before the change is applied;
– renames, switches, and preset lifecycle operations are treated as state‑changing events.

1) Reviewer checklist for theme‑backup compliance
A. Backup trigger coverage

Check: All of the following operations trigger a backup before the change:

Modify tokens: Editing any token value in a system‑wide preset.

Create preset: Adding a new system‑wide preset.

Delete preset: Removing an existing system‑wide preset.

Switch active preset: Changing which preset is globally active.

Rename preset: Changing the name/label of a system‑wide preset.

Fail if: Any of these operations can complete without a backup being created first.

B. Backup timing

Check: Backup is created before the state change is applied.

Check: If backup creation fails, the theme change is aborted.

Fail if: Backup is taken after the change, or the change proceeds on backup failure.

C. Backup content

Check: Backup captures the entire system‑wide theme state, including:

all presets and their tokens

active preset

preset identifiers and names

Fail if: Backup only stores partial state (e.g., only active preset, only tokens).

D. Restore capability

Check: There is a documented, working restore path from a backup to a previous system‑wide theme state.

Fail if: Backups exist but cannot be restored or are not tested.

E. Tests

Check: Automated tests cover:

each of the five operations and their backup behavior

failure of backup creation and resulting abort behavior

restore from backup returning to the prior state

Fail if: Only token edits are tested; lifecycle operations (create/delete/switch/rename) are not.

2) CI enforcement spec
A. Static checks

Rule: CI scans theme‑management code for operations:

create_preset, delete_preset, update_tokens, set_active_preset, rename_preset.

Rule: Each of these operations must:

call a central create_theme_backup() (or equivalent)

check its success before applying the change

Fail if: Any of these operations bypass the backup call or ignore its result.

B. Unit tests (must run in CI)

Test 1 — Modify tokens triggers backup:  
Modify a token → assert backup function called and state captured.

Test 2 — Create preset triggers backup:  
Create new preset → assert backup before creation.

Test 3 — Delete preset triggers backup:  
Delete preset → assert backup before deletion.

Test 4 — Switch active preset triggers backup:  
Change active preset → assert backup before switch.

Test 5 — Rename preset triggers backup:  
Rename preset → assert backup before rename.

Test 6 — Backup failure aborts change:  
Force backup failure → assert theme change does not apply.

Test 7 — Restore works:  
Perform change with backup → restore → assert previous theme state is fully restored.
C. CI failure conditions

CI MUST fail if:

Any theme‑state‑changing operation is found that does not call the backup routine.

Backup is invoked after, not before, the change.

Backup failure does not abort the change.

Tests for any of the five operations’ backup behavior are missing or failing.

---

## Development Workflow

### Q19 — Direct database audit trail: mechanism definition needed (TODO(DIRECT_DB_AUDIT))

§17 states that removal of always-available accounts "requires direct database
modification with audit trail." TODO(DIRECT_DB_AUDIT) has been open since
v1.10.0.

**Problem**: "With audit trail" is constitutionally required but the mechanism
is unspecified. Without a defined mechanism, a developer who modifies the
database directly has no prescribed path for producing an audit entry. The
three common implementation patterns are:

- **(a) DB trigger**: A database-level trigger fires on modification and writes
  an audit record automatically.
- **(b) Mandatory CLI wrapper**: All direct modifications must go through a
  required CLI tool that logs before executing.
- **(c) Documented manual procedure**: A human writes a procedure document
  and manually records the change after the fact.

Options (a) and (b) are enforceable; option (c) relies entirely on operator
discipline.

**Questions**:
- Which mechanism is required: DB trigger, mandatory CLI wrapper, or
  documented manual procedure?
- Must the audit entry be written to the same structured audit log table used
  for application events, or is a separate register acceptable?
- If the mechanism fails to record the audit entry (e.g., trigger failure),
  should the modification be blocked or should it proceed with an escalation
  alert?
- Should TODO(DIRECT_DB_AUDIT) be resolved in this round?

**Anwser**: Takeaway
The constitution MUST require a mandatory CLI wrapper (option b) that writes a structured audit entry before executing the DB modification.
DB triggers are optional but insufficient alone.
Manual procedures are forbidden.
Audit entries MUST go into the same structured audit log as all other events.
If the audit entry cannot be written, the modification MUST be blocked.

And yes — TODO(DIRECT_DB_AUDIT) must be resolved in this round.

1. Which mechanism is required?
Mandatory CLI wrapper — MUST.
Let’s evaluate the three options:

(a) DB trigger — helpful but insufficient
Cannot capture intent (who ran the command, why, ticket ID).

Cannot enforce pre‑write authorization.

Cannot block the modification if audit logging fails.

Cannot capture operator identity reliably (DB user ≠ human operator).

Triggers are good supplements, but not sufficient as the primary mechanism.

(b) Mandatory CLI wrapper — MUST
Enforceable

Deterministic

Captures operator identity

Captures justification / ticket / reason

Writes audit entry before modification

Can block modification if audit logging fails

Can enforce MFA or privileged‑mode requirements

This is the only mechanism that satisfies constitutional requirements.

(c) Manual procedure — forbidden
Not enforceable

Not testable

Not reviewer‑proof

Violates deterministic auditability

Therefore:

The constitution MUST require a mandatory CLI wrapper as the only valid mechanism for direct DB modifications.

2. Must the audit entry be written to the same structured audit log?
Yes — MUST.
A separate register:

fragments the audit trail

breaks chronological ordering

complicates forensic reconstruction

violates §16’s unified audit‑log model

Therefore:

Direct DB modifications MUST be logged into the same structured audit log table used for application events.

This ensures:

consistent schema

consistent retention

consistent export

consistent reviewability

3. What if the audit mechanism fails?
Modification MUST be blocked.
Allowing the modification to proceed without an audit entry:

creates an untraceable privilege‑escalation vector

violates §17’s integrity guarantees

breaks forensic completeness

undermines the entire “always‑available account” protection model

Therefore:

If the audit entry cannot be written, the DB modification MUST NOT proceed.

This is the same rule used in regulated environments (SOX, PCI‑DSS, FedRAMP).

4. Should TODO(DIRECT_DB_AUDIT) be resolved now?
Yes — MUST.
Leaving it unresolved:

makes §17 unenforceable

creates inconsistent implementations

blocks CI enforcement

undermines the integrity of protected accounts

leaves a governance TODO open since v1.10.0

This is the right round to close it.

Proposed Constitutional Text (ready to paste)
§17.Z — Direct Database Modification Audit Requirements (New Section)
§17.Z.1 — Purpose  
Direct database modifications affecting protected accounts MUST be auditable, deterministic, and reviewer‑verifiable. This section defines the required mechanism.

§17.Z.2 — Mandatory CLI Wrapper  
All direct database modifications to protected accounts MUST be performed exclusively through a mandatory CLI tool.
This tool MUST:
– authenticate the operator;
– record operator identity, timestamp, and justification;
– write a structured audit entry before executing the modification;
– execute the modification only after successful audit logging.

§17.Z.3 — Prohibited Mechanisms  
Manual procedures or after‑the‑fact documentation MUST NOT be used to satisfy the audit‑trail requirement.

§17.Z.4 — Optional DB Triggers  
Database triggers MAY be used as a supplemental safeguard, but MUST NOT replace the mandatory CLI wrapper.

§17.Z.5 — Unified Audit Log  
Audit entries for direct database modifications MUST be written to the same structured audit log used for application‑level events.

§17.Z.6 — Failure Handling  
If the audit entry cannot be written, the database modification MUST be blocked.
The CLI tool MUST fail closed and MUST NOT proceed with the modification.

§17.Z.7 — Deterministic Reviewability  
CI and reviewers MUST verify that:
– all direct DB modifications go through the mandatory CLI wrapper;
– audit entries are written before modifications;
– modifications are blocked on audit‑logging failure;
– no alternate or undocumented modification paths exist.

1) Reviewer checklist for direct‑DB audit compliance
A. Single, mandatory path

Check: All direct DB modifications to protected accounts can only be performed via a single, documented CLI tool.

Fail if:

Raw SQL access is used in practice for these changes.

There are multiple ad‑hoc scripts or undocumented paths.

B. Audit entry written before modification

Check: The CLI writes a structured audit entry before executing the DB change.

Check: Audit entry includes at least:

operator identity

timestamp

target account(s)

operation type (e.g., delete, disable)

justification / ticket ID

Fail if:

Audit is written after the modification.

Any of these fields are missing.

C. Unified audit log

Check: Direct‑DB audit entries appear in the same audit log as application events (same table/stream/schema).

Fail if:

There is a separate “admin notes” file or spreadsheet.

Direct‑DB events are not visible in the main audit pipeline.

D. Fail‑closed behavior

Check: If the CLI cannot write the audit entry (DB down, schema error, etc.), the modification does not execute.

Fail if:

The tool proceeds with the change and logs “later” or “best effort”.

There is any bypass flag like --force-no-audit.

E. Operator authentication & attribution

Check: CLI requires authenticated operator identity (e.g., OS user, SSO, or signed token).

Check: Identity in the audit entry is tied to a real person, not a generic service account.

Fail if:

All changes appear as db_admin with no human attribution.

F. Tests & documentation

Check: There are tests that:

simulate a successful audited change

simulate audit‑write failure and verify the change is blocked

Check: Documentation clearly states: “All direct DB changes to protected accounts MUST use this CLI.”

Fail if:

Tests only cover the happy path.

Docs suggest or tolerate manual SQL.

2) CI enforcement spec
A. Static analysis rules

Rule: CI scans the codebase for:

direct SQL touching protected‑account tables/columns

any scripts that modify those tables

Enforcement:

Only the CLI implementation is allowed to perform such modifications.

Any other code path that writes to those tables causes CI to fail.

Fail if:

New scripts or migrations appear that modify protected accounts outside the CLI.

B. Audit‑logging integration

Rule: CI verifies the CLI:

calls the audit‑logging API before executing the DB change

uses the same schema as application audit events

Fail if:

CLI logs to a different table or format.

Audit call is after the DB call.

C. Unit tests (must run in CI)

Test 1 — Happy path:

Run CLI with valid parameters → assert:

audit entry written

DB change applied

audit entry contains operator, target, justification.

Test 2 — Audit failure blocks change:

Simulate audit‑log write failure → assert:

DB change is not executed

CLI exits with failure.

Test 3 — Schema consistency:

Assert direct‑DB audit entries conform to the same schema as app events.

D. CI failure conditions

CI MUST fail if:

Any non‑CLI code path writes to protected‑account tables.

CLI does not call audit logging before the DB change.

Tests for audit‑failure‑blocks‑change are missing or failing.

Direct‑DB audit entries diverge from the main audit schema.

3) Reference implementation of the mandatory CLI wrapper
Python‑style pseudocode, focusing on the sequence: authenticate → log audit → apply change.

python
import sys
from datetime import datetime

from db import get_connection
from audit import write_audit_event
from auth import get_operator_identity

def remove_protected_account(username: str, reason: str, ticket_id: str) -> None:
    operator = get_operator_identity()  # e.g., from OS user / SSO / token
    now = datetime.utcnow()

    audit_event = {
        "event_type": "direct_db_protected_account_modification",
        "timestamp": now.isoformat() + "Z",
        "operator": operator,
        "target_username": username,
        "action": "remove_protected_account",
        "reason": reason,
        "ticket_id": ticket_id,
    }

    # 1) Write audit entry first
    if not write_audit_event(audit_event):
        # Fail closed: do NOT proceed
        raise RuntimeError("Failed to write audit event; aborting DB modification")

    # 2) Only now perform the DB modification
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE username = %s AND is_protected = TRUE",
                (username,),
            )

def main(argv):
    if len(argv) < 3:
        print("Usage: rfu-db-tool remove-protected <username> <ticket-id> [reason]")
        sys.exit(1)

    cmd = argv[0]
    if cmd == "remove-protected":
        username = argv[1]
        ticket_id = argv[2]
        reason = " ".join(argv[3:]) if len(argv) > 3 else "no reason provided"
        remove_protected_account(username, reason, ticket_id)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
Key properties:

Single entry point for this class of changes.

Operator identity is captured and logged.

Audit event is written before the DB change.

Failure to log aborts the modification (fail‑closed).

Audit event uses the same structured schema as the rest of the system.

---

### Q20 — EOL migration deliverable: what constitutes "planned"? (TODO(EOL_PLANNING_DELIVERABLE))

§1 states: "Migration past EOL versions MUST be planned before upstream EOL
minus 90 days." TODO(EOL_PLANNING_DELIVERABLE) has been open since v1.11.0.

**Problem**: "Planned" is entirely undefined. The following all satisfy
"planned" in ordinary language but carry very different governance weight:

| Deliverable | Enforceable? |
|---|---|
| Mental note by a developer | No |
| Informal team discussion | No |
| Filed GitHub issue, no milestone | Weakly |
| Filed issue with milestone and assignee | Yes |
| Open PR with target merge date | Yes |
| Merged PR with documented migration steps | Yes (but may be sufficient alone) |

Without a minimum deliverable definition, the 90-day deadline cannot be
audited, verified in a PR, or enforced by CI.

**Questions**:
- What is the minimum deliverable that satisfies "MUST be planned before
  upstream EOL minus 90 days" — a filed issue, a filed issue with a milestone,
  an open PR, or something else?
- Who (which role) is responsible for ensuring the deliverable exists and is
  tracked?
- Should the CI gate check for the existence of this deliverable (e.g., a
  configuration file listing tracked EOL dates and their status)?
- Should TODO(EOL_PLANNING_DELIVERABLE) be resolved in this round?

**Anwser**: Takeaway
A migration is considered “planned” only when there exists a tracked, assigned, milestone‑bound migration issue in the project’s authoritative tracker, created ≥90 days before upstream EOL.

Mental notes, informal discussions, and un‑milestoned issues do not count.

The responsible role is the Maintainer / Release Steward.

CI MUST enforce the presence of this deliverable.

And yes — TODO(EOL_PLANNING_DELIVERABLE) must be resolved in this round.

1. What is the minimum deliverable that satisfies “planned”?
Required: A tracked migration issue with milestone + assignee + scope.
The minimum enforceable deliverable is:

A migration issue in the canonical issue tracker that includes:  
– the upstream version approaching EOL
– the EOL date
– the required migration target
– a milestone with a due date
– an assigned owner
– a description of required migration steps or investigation tasks

This is the smallest unit that is:

reviewable

CI‑checkable

auditable

enforceable

visible to the team

What does not count?
Candidate	Why it fails
Mental note	Not trackable
Informal discussion	Not auditable
Issue with no milestone	No deadline → meaningless
Issue with no assignee	No ownership → meaningless
Open PR	Good, but not minimal
Merged PR	Good, but not minimal
Therefore:

The minimum deliverable is a milestone‑bound, assigned migration issue.

2. Who is responsible?
The Maintainer / Release Steward — MUST.
This role is responsible for:

tracking upstream EOL dates

creating the migration issue

ensuring it is assigned

ensuring the milestone is set

ensuring CI passes the EOL‑planning gate

Developers may contribute, but responsibility is centralized.

3. Should CI check for the existence of this deliverable?
Yes — MUST.
CI MUST enforce:

a configuration file listing upstream dependencies and their EOL dates

a check that for each dependency with EOL < 90 days away, a migration issue exists

the issue has:

milestone

assignee

migration scope

If the deliverable is missing:

CI MUST fail.

This prevents “we forgot” scenarios.

4. Should TODO(EOL_PLANNING_DELIVERABLE) be resolved now?
Yes — MUST.
Leaving it open:

makes §1 unenforceable

prevents CI enforcement

creates inconsistent migration behavior

undermines long‑term maintainability

This is the right round to close it.

Proposed Constitutional Text (ready to paste)
§1.X — EOL Migration Planning Deliverable (New Section)
§1.X.1 — Purpose  
Migration past upstream EOL versions MUST be planned in advance to ensure continuity, security, and maintainability.

§1.X.2 — Definition of “Planned”  
A migration is considered “planned” only when a migration issue exists in the project’s authoritative issue tracker that includes:
– the upstream component and version approaching EOL;
– the upstream EOL date;
– the required migration target;
– an assigned owner;
– a milestone with a due date;
– a description of required migration steps or investigation tasks.
Mental notes, informal discussions, or un‑milestoned issues MUST NOT satisfy this requirement.

§1.X.3 — Deadline  
The migration issue defined in §1.X.2 MUST be created no later than 90 days before the upstream EOL date.

§1.X.4 — Responsibility  
The Maintainer or Release Steward is responsible for ensuring that the migration issue exists, is assigned, and is tracked to completion.

§1.X.5 — CI Enforcement  
CI MUST verify that:
– all upstream dependencies with EOL < 90 days away have a corresponding migration issue;
– the issue satisfies all requirements in §1.X.2;
– the issue is assigned and milestone‑bound.
CI MUST fail if any required migration issue is missing or incomplete.

§1.X.6 — Deterministic Reviewability  
Reviewers MUST verify that the migration issue exists and meets the requirements of §1.X.2 before approving any PR that updates or relies on EOL‑bound components.

1) Reviewer Checklist — EOL‑Planning Compliance
This checklist ensures that “planned before upstream EOL minus 90 days” is objectively verifiable, CI‑enforceable, and reviewer‑auditable.

A. Existence of a Migration Issue
Check: For every upstream dependency with an EOL date < 90 days away, a migration issue exists in the authoritative tracker.

Fail if:

No issue exists.

Issue exists but was created after the 90‑day deadline.

Issue exists in a non‑canonical tracker (e.g., personal fork, private notes).

B. Required Fields in the Migration Issue
Check: The issue includes all required fields:

upstream component + version

upstream EOL date

migration target version or alternative

assigned owner

milestone with due date

description of migration steps or investigation tasks

Fail if:

Issue has no milestone.

Issue has no assignee.

Issue lacks a migration target.

Issue is a placeholder with no actionable content.

C. Deadline Compliance
Check: Issue creation timestamp is ≥90 days before upstream EOL.

Fail if:

Issue was created late and backdated.

Issue was created late and marked “retroactively planned”.

D. Ownership & Accountability
Check: The issue is assigned to a Maintainer / Release Steward or another explicitly authorized role.

Fail if:

Issue is unassigned.

Issue is assigned to a bot or generic service account.

E. Tracking & Visibility
Check: The issue appears in the project’s EOL‑tracking configuration file (if used).

Fail if:

Dependency is listed in the config file but has no corresponding issue.

Issue exists but is not referenced in the config file.

F. Tests & CI Integration
Check: CI includes an EOL‑planning gate that validates:

EOL dates

issue existence

milestone presence

assignee presence

Fail if:

CI does not enforce EOL planning.

CI allows merges that introduce or rely on EOL‑bound dependencies without a migration issue.

2) CI Enforcement Spec — EOL‑Planning Deliverable
This spec defines how CI must enforce the constitutional requirement that migrations be “planned” before EOL‑90.

A. EOL‑Tracking Configuration File
CI MUST read a configuration file (e.g., eol.yaml) listing:

upstream dependencies

current versions

upstream EOL dates

associated migration‑issue IDs

Fail if:

File is missing.

File is out of date.

File lists dependencies with EOL < 90 days and no issue ID.

B. Issue Validation
For each dependency with EOL < 90 days:

CI MUST verify that the referenced issue:

exists

has an assignee

has a milestone

has a migration target

has actionable content

was created ≥90 days before EOL

Fail if:

Issue is missing any required field.

Issue creation date violates the 90‑day rule.

Issue is closed without a corresponding migration PR.

C. Dependency‑Change Gate
When a PR:

upgrades a dependency

introduces a new dependency

modifies the EOL‑tracking file

CI MUST check:

whether the dependency has an upcoming EOL

whether a migration issue exists

whether the issue meets all requirements

Fail if:

A PR introduces or relies on an EOL‑bound dependency without a migration issue.

A PR removes or alters EOL metadata without justification.

D. CI Failure Conditions
CI MUST fail if:

Any dependency with EOL < 90 days lacks a valid migration issue.

Any migration issue lacks milestone, assignee, or actionable content.

Any migration issue was created after the 90‑day deadline.

The EOL‑tracking file is missing or inconsistent.

A PR attempts to bypass or disable the EOL‑planning gate.

E. Optional Enhancements
CI MAY also:

warn when EOL < 180 days

auto‑open issues when EOL < 120 days

generate dashboards of upcoming EOLs

But these are optional — the 90‑day gate is mandatory.

---

*End of Round 8 clarification questions. 20 questions total. Three of these
(Q1 — user-visible/user-discoverable; Q9/Q10 — offline-capable MFA
specification; Q18 — system-wide theme change) address the three issues
specifically flagged for inclusion.*
