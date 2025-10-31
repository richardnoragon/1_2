# Implementation Plan: Centralized File Type Validator

**Branch**: `003-use-docs-centralized` | **Date**: 2025-10-20 | **Spec**: [`specs/003-use-docs-centralized/spec.md`](spec.md)
**Input**: Feature specification from `/specs/003-use-docs-centralized/spec.md`

## Execution Flow (/plan command scope)

```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Consolidate all file-type verification logic into a centralized validator that provides consistent detection results, confidence scores, and policy-driven actions for every RFU module. The validator becomes the single integration point, enabling safer handling of mismatched or malicious files while offering extensible signature management and telemetry.

## Technical Context

**Language/Version**: Python 3.11 (project venv)
**Primary Dependencies**: PyQt5 application stack, standard library (`pathlib`, `zipfile`, `mimetypes`), existing RFU config/log managers
**Storage**: None (metadata persisted via existing config manager if needed)
**Testing**: pytest with existing unit/integration harness
**Target Platform**: Cross-platform desktop (Windows primary, macOS/Linux supported)
**Project Type**: Single-application toolbox (PyQt5 desktop suite)
**Performance Goals**: Validate ≥10k files/minute by reading ≤2KB headers; avoid blocking GUI thread >100ms
**Constraints**: Must honor Constitution principle II (safety) & IV (performance); adhere to centralized logging/metrics; ensure configurability per workflow
**Scale/Scope**: Applies to entire RFU suite (dozens of tools) scanning large enterprise datasets (hundreds of thousands of files per session)

## Constitution Check

- **Principle II – Safety & Data Integrity**: Plan enforces protective default actions and explicit policy modes. PASS
- **Principle III – Test-Driven Quality & Observability**: Commit to failing tests first, structured logging, and metrics capture. PASS
- **Principle IV – Performance & Scalability**: Header-only reads, worker integration, and telemetry align with streaming expectations. PASS
- **Additional Constraints**: No silent failures; configurability & logging aligned with governance. PASS

_No constitutional violations identified; Complexity Tracking remains empty._

## Project Structure

### Documentation (this feature)

```
specs/003-use-docs-centralized/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
src/
├── rfu/
│   ├── main.py
│   ├── hub.py
│   └── core/
├── utilities/
│   ├── file_management/
│   ├── file_operations/
│   ├── analysis/
│   ├── pdf_tools/
│   ├── network/
│   └── security/
├── tools/
│   └── analysis/
└── file_validator/           # NEW central validator package
    ├── __init__.py
    ├── detector.py
    ├── signatures.py
    ├── heuristics.py
    ├── utils.py
    └── exceptions.py

tests/
├── unit/
│   └── file_validator/       # NEW unit tests for validator
├── integration/
└── gui/
```

**Structure Decision**: Single-project structure retained; add dedicated `src/file_validator` package with mirrored unit tests under `tests/unit/file_validator`.

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context**:

   - Best practices for curated signature sets covering RFU-supported formats.
   - Container inspection strategies for Office/EPUB archives within performance budget.
   - Policy configuration patterns aligning with existing config manager.

2. **Generate and dispatch research agents**:

   ```
   Task: "Research authoritative magic-number sources for RFU-supported file types"
   Task: "Determine efficient container heuristics for ZIP-based formats in Python"
   Task: "Document how RFU config manager can expose per-workflow validator policies"
   ```

3. **Consolidate findings** in `research.md`:
   - Decision, rationale, alternatives (e.g., external libraries vs. in-house tables).

**Output**: `research.md` with resolved unknowns, references, and chosen strategies.

## Phase 1: Design & Contracts

1. **Data Model (`data-model.md`)**:

   - Document `DetectionResult`, `ValidationResult`, `PolicyProfile`, and ancillary entities (telemetry records, signature registry entries).
   - Capture relationships between validator results and consumer workflows.

2. **Contracts (`/contracts/`)**:

   - Define Python-facing API contract (`detect_file_type`, `validate_file_type`) and optional CLI/report interface for QA tools.
   - Provide JSON schema examples for structured responses (for logging/export).

3. **Contract Tests**:

   - Write pytest stubs asserting response shape, confidence tiers, and policy behavior (initially failing).

4. **Quickstart (`quickstart.md`)**:

   - Provide step-by-step guide to integrate validator into an existing tool, including configuration and telemetry hooks.

5. **Agent Context Update**:

   - After drafting Phase 1 docs, run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot` to record new tech/context for future automation.

6. **Post-Design Constitution Check**:
   - Reconfirm performance, safety, and documentation commitments; update section accordingly.

## Phase 2: Task Planning Approach

**Task Generation Strategy**:

- Derive tasks from contracts, data models, and quickstart instructions.
- Prioritize TDD: create failing tests for signature detection, policy enforcement, and telemetry metrics before implementation.
- Include parallelizable tasks (signature table curation vs. policy config integration) marked with [P].

**Ordering Strategy**:

1. Finalize unit tests and schemas.
2. Implement core detection + signatures.
3. Add policy enforcement + config integration.
4. Wire telemetry/logging.
5. Update consuming modules incrementally.

**Estimated Output**: 25–30 ordered tasks in `tasks.md` with dependencies and parallel indicators.

## Phase 3+: Future Implementation

- **Phase 3**: Execute `/tasks` to generate actionable checklist.
- **Phase 4**: Implement tasks via TDD, updating tools to consume validator.
- **Phase 5**: Validate via automated tests, sample corpus runs, and GUI smoke tests.

## Complexity Tracking

_No deviations from constitutional constraints._

## Progress Tracking

**Phase Status**:

- [ ] Phase 0: Research complete (/plan command)
- [ ] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [ ] Initial Constitution Check: PASS
- [ ] Post-Design Constitution Check: PASS
- [ ] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---

_Based on Constitution v1.0.1 - See `/.specify/memory/constitution.md`_
