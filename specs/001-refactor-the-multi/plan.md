# Implementation Plan: Multi-Pane Explorer Hub Interface Refactor

**Branch**: `001-refactor-the-multi` | **Date**: October 1, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-refactor-the-multi/spec.md`

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

Refactor the Multi-Pane Explorer to be one of two selectable hub interfaces (alongside the existing tabbed interface) for Richards File Utilities. The Multi-Pane Explorer provides a flexible 1-4 pane layout system with a fixed left pane (Bookmarks/Recent/Tools tabs), configurable center panes (file navigation), and a fixed right pane (Preview/Properties tabs). Users can quick-toggle between hub interfaces and configure layout preferences including pane count (1-4) and arrangement (horizontal/vertical/grid). The system persists all user preferences and implements graceful fallback behaviors for unavailable resources.

## Technical Context

**Language/Version**: Python 3.8+ (existing RFU codebase requirement)
**Primary Dependencies**: PyQt5 (GUI framework), existing RFU core modules (config_manager, log_manager, database)
**Storage**: JSON configuration files (rfu_config.json), SQLite database (optional, for tracking usage)
**Testing**: pytest, pytest-qt (for GUI testing), existing RFU test infrastructure
**Target Platform**: Cross-platform desktop (Windows, macOS, Linux) - GUI application
**Project Type**: Single desktop application with modular architecture
**Performance Goals**:

- UI responsiveness: <100ms for user interactions (main thread)
- Large directory handling: 10k+ files without UI freeze
- Layout switching: perceived as instant (<200ms)
- Bookmark/Recent list loading: <1 second
  **Constraints**:
- Must integrate with existing RFU architecture (config_manager, hub.py, tool discovery)
- Must maintain cross-platform consistency (Windows/macOS/Linux)
- Must support graceful degradation when optional features unavailable
- Must preserve user preferences across sessions reliably
  **Scale/Scope**:
- 3 major pane types (left, center, right) with 9 key entities
- 1-4 configurable center panes
- 55 functional requirements
- Estimated ~15-20 new/modified Python modules

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**I. Cross-Platform Consistency**: ✅ PASS

- All features (layout switching, pane configurations, quick-toggle) are OS-agnostic
- Qt5 abstracts platform differences
- No platform-specific behavior required

**II. Safety & Data Integrity**: ✅ PASS

- No destructive operations in this feature
- All operations are UI layout/preference changes
- Fallback behaviors preserve user experience (defaults to system drive when preferred unavailable)
- Configuration changes are non-destructive

**III. Test-Driven Quality & Observability**: ⚠️ REQUIRES ATTENTION

- TDD approach required for all new functionality
- Minimum 85% coverage must be maintained
- Structured logging via existing log_manager required
- UI testing with pytest-qt for interactive components
- Edge cases (empty states, unavailable drives) must have explicit tests

**IV. Performance & Scalability**: ✅ PASS

- Large directory handling requirement (10k+ files) aligns with constitution
- UI responsiveness <100ms matches requirement
- Worker threads for file system operations (existing pattern)
- Progress reporting for long operations (not primary focus but supported)

**V. Simplicity & Extensible Modularity**: ✅ PASS

- Builds on existing modular architecture (PaneManager, ConfigManager)
- Single responsibility: hub interface selection and pane layout management
- Clear extension point: pane types are discoverable/pluggable (existing pattern)
- No premature generalization - implements specified requirements only

**Additional Constraints Compliance**:

- ✅ PEP 8, mypy type checking (existing enforcement)
- ✅ Validated inputs (file paths, configuration values)
- ✅ Structured logging with actionable errors
- ✅ Keyboard accessibility (Qt5 default + explicit shortcuts)
- ✅ Documentation required for new components
- ✅ Configuration changes via ConfigManager (persistence guaranteed)
- ✅ Backward compatibility: new feature, no breaking changes to existing APIs

**Initial Assessment**: PASS with TDD focus required

**Action Items**:

1. Write failing tests before implementing each component
2. Ensure coverage ≥85% for all new modules
3. Document all new pane types and configuration options
4. Performance baseline tests for large directories and layout switching

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
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
│   ├── main.py                          # Application entry point
│   ├── hub.py                           # Existing hub interface (modify for dual-mode)
│   ├── config_manager.py                # Configuration persistence (existing)
│   └── log_manager.py                   # Structured logging (existing)
├── file_explorer/
│   ├── explorer_controller.py           # Main explorer controller (modify)
│   ├── ui/
│   │   ├── pane_manager.py             # Existing pane management (enhance)
│   │   ├── file_explorer_pane.py       # Center pane implementation (existing)
│   │   ├── left_pane.py                # NEW: Left pane with tabs
│   │   ├── right_pane.py               # NEW: Right pane with tabs
│   │   ├── bookmarks_widget.py         # NEW: Bookmarks tab content
│   │   ├── recent_widget.py            # NEW: Recent items tab content
│   │   ├── tools_widget.py             # NEW: Tools tab content
│   │   ├── preview_widget.py           # NEW: Preview tab content
│   │   ├── properties_widget.py        # NEW: Properties tab content
│   │   └── layout_manager.py           # NEW: Pane layout orchestration
│   ├── models/
│   │   ├── bookmark.py                 # NEW: Bookmark data model
│   │   ├── recent_item.py              # NEW: Recent item data model
│   │   ├── pane_configuration.py       # NEW: Pane layout configuration
│   │   └── hub_interface_mode.py       # NEW: Hub mode enumeration
│   ├── services/
│   │   ├── bookmark_service.py         # NEW: Bookmark management
│   │   ├── recent_items_service.py     # NEW: Recent items tracking
│   │   ├── tools_discovery_service.py  # NEW: RFU tool discovery
│   │   └── preference_service.py       # NEW: User preference management
│   └── features/
│       └── hub_interface_toggle.py     # NEW: Quick-toggle button component
├── gui/
│   └── widgets/
│       └── notification_widget.py       # NEW: User notifications (fallback messages)
└── config/
    └── rfu_config.json                  # Configuration storage (existing)

tests/
├── file_explorer/
│   ├── unit/
│   │   ├── test_bookmark_service.py    # NEW
│   │   ├── test_recent_items_service.py # NEW
│   │   ├── test_tools_discovery.py     # NEW
│   │   ├── test_preference_service.py  # NEW
│   │   ├── test_pane_configuration.py  # NEW
│   │   └── test_layout_manager.py      # NEW
│   ├── integration/
│   │   ├── test_hub_toggle.py          # NEW: Hub interface switching
│   │   ├── test_pane_layout_changes.py # NEW: Dynamic layout reconfiguration
│   │   ├── test_preference_persistence.py # NEW: Config save/load
│   │   └── test_empty_states.py        # NEW: Empty bookmark/recent scenarios
│   └── ui/
│       ├── test_left_pane.py           # NEW: pytest-qt tests
│       ├── test_right_pane.py          # NEW: pytest-qt tests
│       ├── test_bookmarks_widget.py    # NEW
│       ├── test_recent_widget.py       # NEW
│       ├── test_tools_widget.py        # NEW
│       ├── test_preview_widget.py      # NEW
│       └── test_properties_widget.py   # NEW
└── performance/
    ├── test_large_directory_load.py    # NEW: 10k+ files benchmark
    └── test_layout_switching_speed.py  # NEW: <200ms requirement
```

**Structure Decision**: Single desktop application (Option 1) with modular architecture. This refactor extends the existing `src/file_explorer/` module with new UI components, data models, and services. The existing `src/rfu/` core modules (config_manager, hub.py) will be enhanced to support the dual hub interface mode. All new code follows the established RFU pattern of separation: models, services, UI, and features.

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:

   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts

_Prerequisites: research.md complete_

1. **Extract entities from feature spec** → `data-model.md`:

   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:

   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:

   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:

   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/\*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach

_This section describes what the /tasks command will do - DO NOT execute during /plan_

**Task Generation Strategy**:

The /tasks command will generate a comprehensive task list following TDD principles:

1. **Contract Test Tasks** (7 tasks, parallelizable):
   - Each service contract → failing test suite
   - PreferenceService, BookmarkService, RecentItemsService
   - ToolsDiscoveryService, LayoutManager, StorageDeviceService, NotificationService
2. **Data Model Tasks** (9 tasks, parallelizable):
   - Create enumeration classes (HubInterfaceMode, LayoutType, BookmarkType, etc.)
   - Create dataclasses (Bookmark, RecentItem, PaneConfiguration, etc.)
   - Implement validation logic per entity
3. **Service Implementation Tasks** (7 tasks, sequential dependencies):
   - Implement services to make contract tests pass
   - Order: PreferenceService → BookmarkService → RecentItemsService → StorageDeviceService → ToolsDiscoveryService → LayoutManager → NotificationService
4. **UI Widget Tasks** (9 tasks, some parallel):
   - Left pane tabs: BookmarksWidget, RecentWidget, ToolsWidget
   - Right pane tabs: PreviewWidget, PropertiesWidget
   - Container widgets: LeftPane, RightPane
   - Layout orchestration: LayoutManager widget integration
   - Quick-toggle button: HubInterfaceToggle widget
5. **Integration Tasks** (8 tasks, sequential):
   - Modify hub.py for dual-mode support
   - Modify explorer_controller.py to use new pane types
   - Wire up preference persistence
   - Implement empty state widgets
   - Implement fallback notifications
   - Connect preview/properties to file selection
   - Performance optimization (large directories)
   - Cross-platform testing
6. **Testing Tasks** (5 tasks):
   - UI integration tests (pytest-qt)
   - End-to-end workflow test
   - Performance benchmarks
   - Empty state testing
   - Fallback behavior testing

**Ordering Strategy**:

- **Phase 2.1 - Foundation** (Tasks 1-16): Contract tests + data models
  - All parallelizable, no dependencies
- **Phase 2.2 - Services** (Tasks 17-23): Service implementations
  - Sequential by dependency: Preference → Bookmark/Recent → Storage/Tools → Layout/Notification
- **Phase 2.3 - UI Components** (Tasks 24-32): Widget creation
  - Left/right pane widgets parallelizable
  - LayoutManager depends on pane widgets
- **Phase 2.4 - Integration** (Tasks 33-40): Connect to existing RFU
  - Sequential, builds on previous phases
- **Phase 2.5 - Validation** (Tasks 41-45): Testing & optimization
  - Can be parallelized across team members

**Estimated Output**: 45 tasks in tasks.md

**Complexity Indicators**:

- [P] = Parallelizable (no blocking dependencies)
- [S] = Sequential (depends on prior tasks)
- [UI] = Requires UI testing (pytest-qt)
- [PERF] = Performance-sensitive (benchmarking required)

**Task Template Example**:

```markdown
### Task 01: Create PreferenceService Contract Tests [P]

**Type**: Testing  
**File**: `tests/file_explorer/contract/test_preference_service_contract.py`  
**Dependencies**: None  
**Estimated Effort**: 30 minutes  
**Acceptance**:

- [ ] Test for load_preferences() with missing config
- [ ] Test for load_preferences() with valid config
- [ ] Test for save_preferences() persistence
- [ ] Test for reset_to_defaults()
- [ ] All tests fail (no implementation yet)
```

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

_These phases are beyond the scope of the /plan command_

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

_Fill ONLY if Constitution Check has violations that must be justified_

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |

## Progress Tracking

_This checklist is updated during execution flow_

**Phase Status**:

- [x] Phase 0: Research complete (/plan command)
  - ✅ research.md created with 7 technical decisions documented
  - ✅ All NEEDS CLARIFICATION resolved from spec
  - ✅ Technology dependencies identified
- [x] Phase 1: Design complete (/plan command)
  - ✅ data-model.md created with 9 entities defined
  - ✅ contracts/service-contracts.md created with 7 service interfaces
  - ✅ quickstart.md created with 10 test scenarios
  - ✅ .github/copilot-instructions.md updated
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
  - ✅ Task generation strategy documented (45 tasks estimated)
  - ✅ Ordering strategy defined (5 sequential phases)
  - ✅ Complexity indicators defined [P], [S], [UI], [PERF]
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS
  - ✅ Cross-platform consistency validated
  - ✅ Safety & data integrity N/A (no destructive ops)
  - ✅ TDD approach required and documented
  - ✅ Performance requirements specified
  - ✅ Simplicity & modularity maintained
- [x] Post-Design Constitution Check: PASS
  - ✅ No new violations introduced
  - ✅ Service contracts follow single responsibility
  - ✅ All interfaces are testable
  - ✅ No premature generalization
- [x] All NEEDS CLARIFICATION resolved
  - ✅ All 5 clarifications from spec addressed in research
- [x] Complexity deviations documented
  - ✅ No deviations required (Complexity Tracking section empty)

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
