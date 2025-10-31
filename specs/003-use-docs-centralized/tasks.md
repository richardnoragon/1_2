# Tasks: Centralized File Type Validator

**Input**: Design documents from `/specs/003-use-docs-centralized/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Phase 3.1: Setup

- [x] T001 Ensure branch `003-use-docs-centralized` is active and sync plan artifacts in `specs/003-use-docs-centralized/`
- [x] T002 Audit existing file-type checks to confirm migration path; document findings in `specs/003-use-docs-centralized/research.md`

## Phase 3.2: Tests First (TDD)

- [x] T003 Draft pytest fixture corpus for representative files (PDF, PNG, ZIP, DOCX, EXE) under `tests/fixtures/file_validator/` [P]
- [x] T004 Create failing unit tests for signature detection confidence tiers in `tests/unit/file_validator/test_signatures.py`
- [x] T005 Write failing policy enforcement tests covering reject/warn/auto modes in `tests/unit/file_validator/test_policy.py`
- [x] T006 Add integration test ensuring GUI tool consumes validator responses via notification framework in `tests/integration/gui/test_validator_notifications.py`
- [x] T007 Author CLI/batch integration test that exercises validator telemetry logging in `tests/integration/cli/test_validator_telemetry.py`

## Phase 3.3: Core Implementation

- [x] T008 Scaffold `src/file_validator/__init__.py` exposing public API surface [P]
- [x] T009 Implement `src/file_validator/signatures.py` with curated magic-number tables and loading helpers [P]
- [x] T010 Implement `src/file_validator/heuristics.py` with text/binary heuristics and container detectors [P]
- [x] T011 Implement `src/file_validator/utils.py` for header reading, extension normalization, and MIME fallback utilities [P]
- [x] T012 Implement core detection pipeline in `src/file_validator/detector.py`, returning structured results and evidence trail
- [x] T013 Add `src/file_validator/exceptions.py` defining validator-specific error types [P]
- [x] T014 Implement policy orchestration and risk stratification logic in `src/file_validator/policy.py`
- [x] T015 Integrate centralized validator into representative RFU tool (e.g., `src/utilities/file_management/advanced_folders/core/content_search_engine.py`) to replace legacy checks
- [x] T016 Provide logging hooks and telemetry emission via existing log manager in `src/file_validator/telemetry.py`

## Phase 3.4: Integration

- [ ] T017 Wire validator notification outputs to GUI notification framework in `src/rfu/hub.py`
- [ ] T018 Ensure headless workflows (e.g., network transfer) respect policy outcomes by updating `src/utilities/network/transfer/network_transfer.py`
- [ ] T019 Update configuration management to permit per-workflow validator policies in `src/rfu/config_manager.py`
- [ ] T020 Create compatibility shim for modules still using legacy helpers in `src/file_validator/compat.py`

## Phase 3.5: Polish

- [ ] T021 Write documentation quickstart in `specs/003-use-docs-centralized/quickstart.md`
- [ ] T022 Update agent context via `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
- [ ] T023 Generate performance validation report by running validator against sample corpus and documenting results in `specs/003-use-docs-centralized/research.md`
- [ ] T024 Review telemetry dashboards/log outputs to ensure mismatch evidence is captured, documenting in `specs/003-use-docs-centralized/data-model.md`
- [ ] T025 Final validation: run `pytest tests/unit/file_validator/ tests/integration/gui/test_validator_notifications.py tests/integration/cli/test_validator_telemetry.py`

## Dependencies

- T003 before T004-T007 (fixture corpus shared)
- T004-T007 must fail before T008 onward
- T009, T010, T011 feed into T012 (core detection)
- T012 must complete before T014, T015, T016
- T015 prerequisite for T017 and T018
- T019 depends on policy decisions (T014)
- T025 requires all prior tasks complete

## Parallel Execution Examples

- Initial tests: run T003, T004, T005, T006, T007 concurrently until failing state achieved.
- Core helpers: execute T008, T009, T010, T011, T013 in parallel (distinct files) before unblocking T012.

## Validation Checklist

- [ ] All tests authored before implementation
- [ ] Every entity/contract covered by tasks
- [ ] No [P]-marked tasks share file paths
- [ ] Performance validation included
- [ ] Documentation and agent context updated
