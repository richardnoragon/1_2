# File Validation Exemption — Compliance Checklist

**Constitutional authority**: §IX.X.1–§IX.X.7  
**Canonical spec**: docs/file-validation-exemption-spec.md  
**Status**: Normative  
**Version**: 1.0.0 (aligned with constitution v1.29.0)  
**Last updated**: 2026-04-05  

Reviewers MUST verify all items before approving any PR that modifies file
reading logic, temp file handling, plugin integration, IPC channels, session
management, or any code path that opens files for reading or transformation.

---

## Section A — Same-Instance Exemption Scope (§IX.X.2)

- [ ] A.1  The validation exemption is applied ONLY when all four conditions hold: same process (PID), same tool instance, same session (session UUID), no external exposure
- [ ] A.2  The exemption is implemented via a single, named helper function (e.g., `open_validated()` / `open_internal_temp_same_instance()`) — not scattered ad-hoc throughout the codebase
- [ ] A.3  The in-memory registry tracks `(absolute_path, process_id, session_id)` tuples — no weaker/broader key is used
- [ ] A.4  Files written via `write_internal_temp()` (or equivalent) are correctly registered before any read is attempted
- [ ] A.5  The helper function verifies both process ID and session ID before granting the exemption
- [ ] A.6  CI test T1 (same-instance exemption — no validation called) passes

---

## Section B — Boundaries That Invalidate the Exemption (§IX.X.3)

- [ ] B.1  **Process boundary**: a file written by one PID that is read by a different PID triggers full validation
- [ ] B.2  **Tool boundary**: a file written by Tool A and read by Tool B (even within the same process) triggers full validation
- [ ] B.3  **Plugin boundary**: a file written by any plugin (even ComponentGuardian-registered) triggers full validation when read by core code
- [ ] B.4  **Session boundary**: a file written in session N and read in session N+1 triggers full validation
- [ ] B.5  **IPC boundary**: a file whose path arrives via socket, pipe, shared memory, or message queue triggers full validation
- [ ] B.6  **Shared temp directory**: files in shared OS temp directories (`%TEMP%`, `/tmp`) trigger full validation unless the current process itself wrote and registered them
- [ ] B.7  **Background/scheduled task**: files handed off to background workers or scheduled jobs trigger full validation
- [ ] B.8  CI test T2 (cross-tool read validates) passes
- [ ] B.9  CI test T3 (plugin output validates) passes
- [ ] B.10 CI test T4 (cross-session read validates) passes
- [ ] B.11 CI test T5 (shared temp — different process — validates) passes

---

## Section C — Plugin Isolation (§IX.X.4)

- [ ] C.1  Plugin code CANNOT import or call the exemption-granting helper (`open_internal_temp_same_instance` / `register_internal_temp`)
- [ ] C.2  Plugin output files are never added to the in-memory exemption registry
- [ ] C.3  The `file_validation_gate` module (or equivalent) has a documented access control policy specifying which modules may import it
- [ ] C.4  ComponentGuardian plugin registration does NOT implicitly confer any validation exemption
- [ ] C.5  Any code review touching plugin-to-core data flow verifies that the core reads via `open_validated()` (full validation path)

---

## Section D — In-Memory Registry Integrity (§IX.X.6)

- [ ] D.1  The exemption registry is stored in memory only — NOT written to disk, database, or any persistent store
- [ ] D.2  The registry is cleared automatically on process exit (inherent in memory-only storage)
- [ ] D.3  No serialization/deserialization path exists for the registry
- [ ] D.4  The session ID used in the registry key is generated fresh on each process start (e.g., `uuid4()` at module import time)
- [ ] D.5  The registry cannot be populated by loading a file, reading a config, or deserializing data from a previous session

---

## Section E — Codebase Audit: All File Opens Go Through the Gate (§IX)

- [ ] E.1  A grep/static-analysis check confirms no raw `open()` or `Path.open()` calls exist outside of `file_validation_gate.py` (or equivalent) in tool or core code
- [ ] E.2  Any remaining direct `open()` calls are documented with an explicit justification comment and tagged for re-review
- [ ] E.3  All cross-tool data flows that involve file paths have been audited and validated paths confirmed
- [ ] E.4  IPC-received file paths are validated before first `open()` call
- [ ] E.5  Background task file paths (received from queue, scheduler, or event) are validated before first `open()` call

---

## Section F — Test Coverage and CI Gate (§IX.X.7)

- [ ] F.1  CI tests T1–T5 (as defined in docs/file-validation-exemption-spec.md §5) are implemented and passing
- [ ] F.2  CI pipeline includes tests T1–T5 as a **required gate** (not optional or skippable)
- [ ] F.3  Tests cover: same-instance exemption (T1), cross-tool read (T2), plugin output (T3), cross-session read (T4), shared-temp-dir cross-process (T5)
- [ ] F.4  Static analysis rule exists to flag direct `open()` calls not routed through the gate
- [ ] F.5  Test coverage for `file_validation_gate.py` (or equivalent) ≥ 90%
- [ ] F.6  No existing validation or file-handling test has been weakened or removed

---

## Notes

- The "same tool instance" condition means the **same Python object** (or equivalent runtime object) in the same process — not merely the same tool class or tool name.
- When in doubt about whether a boundary is crossed, **always validate**. The exemption is a performance optimisation, not a security relaxation.
- The `component-guardian-spec.md` defines plugin registration; registration confers lifecycle management, not trust for file I/O purposes.

---

## Cross-References

| Reference | Location |
|-----------|----------|
| Canonical spec | docs/file-validation-exemption-spec.md |
| Constitutional authority | §IX.X.1–§IX.X.7 (.specify/memory/constitution.md) |
| Q16 answer | .specify/memory/constitution_clairification_uiux_harmonny_r8.md §Q16 |
| ComponentGuardian spec | docs/component-guardian-spec.md |
| Audit origin metadata checklist | .specify/memory/checklist-audit-origin-metadata-compliance.md |
| PII scan UX checklist | .specify/memory/checklist-pii-scan-ux-compliance.md |
| is_protected checklist | .specify/memory/checklist-is-protected-compliance.md |
