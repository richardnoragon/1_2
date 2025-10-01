# Tasks: Multi-Pane Explorer Hub Interface Refactor

**Input**: Design documents from `/specs/001-refactor-the-multi/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/service-contracts.md

## Execution Flow

This tasks document was generated from the design documents following TDD principles. Tasks are organized into 5 phases with clear dependencies. Tasks marked [P] can be executed in parallel.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[UI]**: Requires UI testing with pytest-qt
- **[PERF]**: Performance-sensitive, requires benchmarking
- Include exact file paths in descriptions

---

## Phase 3.1: Setup (3 tasks)

- [ ] **T001** Create project structure per implementation plan

  - **Files**: `src/file_explorer/models/`, `src/file_explorer/services/`, `src/file_explorer/features/`, `src/file_explorer/ui/` directories
  - **Description**: Create all necessary directories for the Multi-Pane Explorer implementation
  - **Acceptance**: Directory structure matches plan.md Project Structure section

- [ ] **T002** [P] Add pytest-qt test fixtures for GUI testing

  - **Files**: `tests/conftest.py`
  - **Description**: Add qtbot fixtures and test application setup for PyQt5 testing
  - **Acceptance**: Test fixtures available for all UI tests

- [ ] **T003** [P] Configure linting and type checking for new modules
  - **Files**: `.flake8`, `mypy.ini`, `.github/workflows/ci.yml` (if needed)
  - **Description**: Ensure linting/type checking covers new file_explorer modules
  - **Acceptance**: All linters recognize new modules

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (7 tasks, all parallelizable)

- [ ] **T004** [P] Contract test PreferenceService in `tests/file_explorer/contract/test_preference_service_contract.py`

  - **Methods**: `load_preferences()`, `save_preferences()`, `reset_to_defaults()`
  - **Acceptance**: Tests for default loading, persistence, and reset - all failing

- [ ] **T005** [P] Contract test BookmarkService in `tests/file_explorer/contract/test_bookmark_service_contract.py`

  - **Methods**: `create_bookmark()`, `get_bookmarks()`, `delete_bookmark()`
  - **Acceptance**: Tests for CRUD operations, validation, filtering - all failing

- [ ] **T006** [P] Contract test RecentItemsService in `tests/file_explorer/contract/test_recent_items_service_contract.py`

  - **Methods**: `add_tool()`, `add_location()`, `get_recent_tools()`, `get_recent_locations()`, `clear_recent()`
  - **Acceptance**: Tests for LRU eviction, timestamp updates, retrieval - all failing

- [ ] **T007** [P] Contract test ToolsDiscoveryService in `tests/file_explorer/contract/test_tools_discovery_service_contract.py`

  - **Methods**: `get_all_tools()`, `search_tools()`, `get_tool_by_name()`
  - **Acceptance**: Tests for tool discovery, filtering, search - all failing

- [ ] **T008** [P] Contract test LayoutManager in `tests/file_explorer/contract/test_layout_manager_contract.py`

  - **Methods**: `apply_configuration()`, `get_current_configuration()`, `save_splitter_states()`
  - **Acceptance**: Tests for layout application, state capture - all failing

- [ ] **T009** [P] Contract test StorageDeviceService in `tests/file_explorer/contract/test_storage_device_service_contract.py`

  - **Methods**: `get_available_drives()`, `is_available()`
  - **Acceptance**: Tests for drive discovery (platform-specific), availability checks - all failing

- [ ] **T010** [P] Contract test NotificationService in `tests/file_explorer/contract/test_notification_service_contract.py`
  - **Methods**: `show_info()`, `show_warning()`, `show_error()`
  - **Acceptance**: Tests for notification display - all failing

### Integration Tests (5 tasks, all parallelizable)

- [ ] **T011** [P] Integration test hub toggle in `tests/file_explorer/integration/test_hub_toggle.py`

  - **Scenarios**: Switch between multi-pane and tabbed mode, context preservation
  - **Acceptance**: Tests for mode switching, <200ms performance - all failing

- [ ] **T012** [P] Integration test pane layout changes in `tests/file_explorer/integration/test_pane_layout_changes.py`

  - **Scenarios**: 1-4 pane configurations, horizontal/vertical/grid layouts
  - **Acceptance**: Tests for dynamic layout reconfiguration - all failing

- [ ] **T013** [P] Integration test preference persistence in `tests/file_explorer/integration/test_preference_persistence.py`

  - **Scenarios**: Save/load preferences, restart application
  - **Acceptance**: Tests for configuration survival across sessions - all failing

- [ ] **T014** [P] Integration test empty states in `tests/file_explorer/integration/test_empty_states.py`

  - **Scenarios**: Empty bookmarks, empty recent items, helpful messages
  - **Acceptance**: Tests for placeholder widgets - all failing

- [ ] **T015** [P] Integration test fallback behavior in `tests/file_explorer/integration/test_fallback_behavior.py`
  - **Scenarios**: Unavailable drives, missing bookmarks, notification display
  - **Acceptance**: Tests for graceful degradation - all failing

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models (9 tasks, all parallelizable)

- [ ] **T016** [P] Create HubInterfaceMode enum in `src/file_explorer/models/hub_interface_mode.py`

  - **Entities**: HubInterfaceMode (MULTI_PANE, TABBED)
  - **Acceptance**: Enum defined, validated

- [ ] **T017** [P] Create LayoutType enum and PaneConfiguration dataclass in `src/file_explorer/models/pane_configuration.py`

  - **Entities**: LayoutType (DISABLED, HORIZONTAL, VERTICAL, GRID), PaneConfiguration
  - **Acceptance**: Dataclass with validation rules implemented

- [ ] **T018** [P] Create LeftPaneTab enum in `src/file_explorer/models/left_pane_tab.py`

  - **Entities**: LeftPaneTab (BOOKMARKS, RECENT, TOOLS)
  - **Acceptance**: Enum defined

- [ ] **T019** [P] Create RightPaneTab enum in `src/file_explorer/models/right_pane_tab.py`

  - **Entities**: RightPaneTab (PREVIEW, PROPERTIES)
  - **Acceptance**: Enum defined

- [ ] **T020** [P] Create BookmarkType enum and Bookmark dataclass in `src/file_explorer/models/bookmark.py`

  - **Entities**: BookmarkType (TOOL, DRIVE, FOLDER, NETWORK_LOCATION), Bookmark
  - **Acceptance**: Dataclass with validation (target validation, timestamp, metadata)

- [ ] **T021** [P] Create RecentItemType enum and RecentItem dataclass in `src/file_explorer/models/recent_item.py`

  - **Entities**: RecentItemType (TOOL, LOCATION), RecentItem
  - **Acceptance**: Dataclass with validation (timestamp, metadata)

- [ ] **T022** [P] Create Tool dataclass in `src/file_explorer/models/tool.py`

  - **Entities**: Tool (name, description, category, launcher, icon, executable_path)
  - **Acceptance**: Dataclass defined with callable launcher

- [ ] **T023** [P] Create CenterPane dataclass in `src/file_explorer/models/center_pane.py`

  - **Entities**: CenterPane (id, current_path, history, history_index, selected_items, view_mode)
  - **Acceptance**: Dataclass with navigation state management

- [ ] **T024** [P] Create UserPreferences dataclass in `src/file_explorer/models/user_preferences.py`
  - **Entities**: UserPreferences (consolidates all other entities)
  - **Acceptance**: Dataclass aggregating all configuration, validation rules implemented

### Service Implementations (7 tasks, with dependencies)

- [ ] **T025** Implement PreferenceService in `src/file_explorer/services/preference_service.py`

  - **Dependencies**: T024 (UserPreferences), T004 (contract tests)
  - **Methods**: `load_preferences()`, `save_preferences()`, `reset_to_defaults()`
  - **Acceptance**: T004 contract tests pass, ConfigManager integration working

- [ ] **T026** [P] Implement BookmarkService in `src/file_explorer/services/bookmark_service.py`

  - **Dependencies**: T020 (Bookmark), T025 (PreferenceService), T005 (contract tests)
  - **Methods**: `create_bookmark()`, `get_bookmarks()`, `delete_bookmark()`
  - **Acceptance**: T005 contract tests pass, bookmark CRUD operations work

- [ ] **T027** [P] Implement RecentItemsService in `src/file_explorer/services/recent_items_service.py`

  - **Dependencies**: T021 (RecentItem), T025 (PreferenceService), T006 (contract tests)
  - **Methods**: `add_tool()`, `add_location()`, `get_recent_tools()`, `get_recent_locations()`, `clear_recent()`
  - **Acceptance**: T006 contract tests pass, LRU cache working correctly

- [ ] **T028** Implement StorageDeviceService in `src/file_explorer/services/storage_device_service.py`

  - **Dependencies**: T009 (contract tests)
  - **Methods**: `get_available_drives()`, `is_available()`
  - **Platform**: Windows/macOS/Linux adapters
  - **Acceptance**: T009 contract tests pass on all platforms

- [ ] **T029** Implement ToolsDiscoveryService in `src/file_explorer/services/tools_discovery_service.py`

  - **Dependencies**: T022 (Tool), T007 (contract tests)
  - **Methods**: `get_all_tools()`, `search_tools()`, `get_tool_by_name()`
  - **Integration**: RFU main.py tool registry
  - **Acceptance**: T007 contract tests pass, tool discovery from RFU working

- [ ] **T030** Implement LayoutManager service in `src/file_explorer/services/layout_manager.py`

  - **Dependencies**: T017 (PaneConfiguration), T025 (PreferenceService), T008 (contract tests)
  - **Methods**: `apply_configuration()`, `get_current_configuration()`, `save_splitter_states()`
  - **Acceptance**: T008 contract tests pass, layout orchestration working

- [ ] **T031** Implement NotificationService in `src/file_explorer/services/notification_service.py`
  - **Dependencies**: T010 (contract tests)
  - **Methods**: `show_info()`, `show_warning()`, `show_error()`
  - **UI**: Toast notification widgets
  - **Acceptance**: T010 contract tests pass, notifications display correctly

---

## Phase 3.4: UI Components (9 tasks, some parallel)

### Left Pane Widgets (3 tasks, all parallelizable)

- [ ] **T032** [P] [UI] Implement BookmarksWidget in `src/file_explorer/ui/bookmarks_widget.py`

  - **Dependencies**: T026 (BookmarkService)
  - **Features**: Display bookmarks (top: tools, bottom: locations), context menu (remove bookmark)
  - **Acceptance**: Bookmarks display correctly, user can remove bookmarks

- [ ] **T033** [P] [UI] Implement RecentWidget in `src/file_explorer/ui/recent_widget.py`

  - **Dependencies**: T027 (RecentItemsService)
  - **Features**: Display recent items (top: tools, bottom: locations), click to launch/navigate
  - **Acceptance**: Recent items display newest first, clicking works

- [ ] **T034** [P] [UI] Implement ToolsWidget in `src/file_explorer/ui/tools_widget.py`
  - **Dependencies**: T029 (ToolsDiscoveryService)
  - **Features**: Display all RFU tools, search/filter, context menu (bookmark tool)
  - **Acceptance**: All tools shown, search works, bookmark context menu functional

### Right Pane Widgets (2 tasks, parallelizable)

- [ ] **T035** [P] [UI] Implement PreviewWidget in `src/file_explorer/ui/preview_widget.py`

  - **Dependencies**: None (standalone preview system)
  - **Features**: Text preview, image preview, unsupported file type message
  - **Handlers**: TextPreviewHandler, ImagePreviewHandler, extensible protocol
  - **Acceptance**: Preview works for text/images, graceful fallback for unsupported types

- [ ] **T036** [P] [UI] Implement PropertiesWidget in `src/file_explorer/ui/properties_widget.py`
  - **Dependencies**: None (file metadata display)
  - **Features**: Display file size, modified date, permissions, path
  - **Acceptance**: Properties display correctly for selected file

### Container Widgets (2 tasks, sequential dependencies)

- [ ] **T037** [UI] Implement LeftPane container in `src/file_explorer/ui/left_pane.py`

  - **Dependencies**: T032, T033, T034 (tab widgets)
  - **Features**: QStackedWidget with 3 tabs, tab switching, default tab restoration
  - **Acceptance**: Tabs switch correctly, default tab from preferences works

- [ ] **T038** [UI] Implement RightPane container in `src/file_explorer/ui/right_pane.py`
  - **Dependencies**: T035, T036 (tab widgets)
  - **Features**: QStackedWidget with 2 tabs, tab switching, file selection listener
  - **Acceptance**: Tabs switch correctly, updates on center pane selection

### Layout Management (2 tasks, sequential)

- [ ] **T039** [UI] Implement LayoutManager UI integration in `src/file_explorer/ui/layout_manager.py`

  - **Dependencies**: T030 (LayoutManager service), T037, T038 (pane containers)
  - **Features**: QSplitter orchestration, dynamic layout changes, splitter state save/restore
  - **Acceptance**: 1-4 pane configurations work, layouts (horizontal/vertical/grid) work, splitter positions persist

- [ ] **T040** [UI] Implement HubInterfaceToggle button in `src/file_explorer/features/hub_interface_toggle.py`
  - **Dependencies**: T025 (PreferenceService)
  - **Features**: Quick-toggle button, switch between multi-pane and tabbed mode
  - **Acceptance**: Toggle works, <200ms switching, context preserved

---

## Phase 3.5: Integration (8 tasks, sequential)

- [ ] **T041** Modify hub.py for dual-mode support in `src/rfu/hub.py`

  - **Dependencies**: T040 (HubInterfaceToggle), T039 (LayoutManager UI)
  - **Changes**: Add mode switching logic, integrate MultiPaneExplorer widget
  - **Acceptance**: Hub can switch between tabbed and multi-pane interfaces

- [ ] **T042** Modify explorer_controller.py for pane management in `src/file_explorer/explorer_controller.py`

  - **Dependencies**: T041 (hub.py modifications), T039 (LayoutManager)
  - **Changes**: Support multiple center pane instances, coordinate pane state
  - **Acceptance**: Multiple panes can coexist, selection events propagate to right pane

- [ ] **T043** Wire up preference persistence in `src/file_explorer/explorer_controller.py`

  - **Dependencies**: T042 (explorer_controller modifications), T025 (PreferenceService)
  - **Changes**: Load preferences on startup, save on changes
  - **Acceptance**: T013 integration tests pass, preferences persist across restarts

- [ ] **T044** [UI] Implement empty state widgets in `src/gui/widgets/empty_state_widget.py`

  - **Dependencies**: None (reusable component)
  - **Features**: Centered icon + title + description + optional action button
  - **Acceptance**: T014 integration tests pass, empty states display helpful messages

- [ ] **T045** Implement fallback notifications in `src/file_explorer/explorer_controller.py`

  - **Dependencies**: T031 (NotificationService), T028 (StorageDeviceService)
  - **Features**: Detect unavailable drives, notify user, default to system root
  - **Acceptance**: T015 integration tests pass, graceful degradation works

- [ ] **T046** Connect preview/properties to file selection in `src/file_explorer/explorer_controller.py`

  - **Dependencies**: T038 (RightPane), T042 (explorer_controller)
  - **Changes**: Wire selection signals from center panes to right pane tabs
  - **Acceptance**: File selection updates preview/properties immediately

- [ ] **T047** [PERF] Performance optimization for large directories in `src/file_explorer/ui/file_explorer_pane.py`

  - **Dependencies**: None (existing component enhancement)
  - **Features**: Lazy loading, virtual scrolling (if not already implemented), worker threads
  - **Acceptance**: 10,000 files load in <2 seconds, UI remains responsive

- [ ] **T048** Cross-platform testing and adjustments
  - **Dependencies**: All previous tasks
  - **Platforms**: Windows, macOS, Linux
  - **Testing**: StorageDeviceService platform adapters, path handling, UI layout
  - **Acceptance**: Application works correctly on all platforms

---

## Phase 3.6: Testing & Validation (5 tasks, some parallel)

- [ ] **T049** [P] [UI] UI integration tests in `tests/file_explorer/ui/`

  - **Files**: `test_left_pane.py`, `test_right_pane.py`, `test_bookmarks_widget.py`, `test_recent_widget.py`, `test_tools_widget.py`, `test_preview_widget.py`, `test_properties_widget.py`
  - **Dependencies**: T037, T038, T032-T036 (UI widgets)
  - **Acceptance**: pytest-qt tests pass, widget interactions work correctly

- [ ] **T050** [P] End-to-end workflow test in `tests/file_explorer/integration/test_e2e_workflow.py`

  - **Dependencies**: All Phase 3.4-3.5 tasks
  - **Scenario**: Complete user workflow from quickstart.md Test 10
  - **Acceptance**: Full workflow completes without errors, all state persists

- [ ] **T051** [P] [PERF] Performance benchmarks in `tests/performance/`

  - **Files**: `test_large_directory_load.py`, `test_layout_switching_speed.py`
  - **Dependencies**: T047 (performance optimizations)
  - **Benchmarks**: <2s large directory, <200ms layout switch, <100ms UI interactions
  - **Acceptance**: All performance requirements met

- [ ] **T052** [P] Empty state testing per quickstart.md Test 6

  - **Dependencies**: T044 (empty state widgets)
  - **Scenarios**: Reset config, verify empty bookmark/recent messages
  - **Acceptance**: All empty states show helpful messages

- [ ] **T053** Fallback behavior testing per quickstart.md Test 7
  - **Dependencies**: T045 (fallback notifications)
  - **Scenarios**: Simulate unavailable drives, verify notifications
  - **Acceptance**: Graceful degradation works, notifications informative

---

## Dependencies Summary

### Phase Dependencies

- Phase 3.1 (Setup) → Phase 3.2 (Tests)
- Phase 3.2 (Tests) → Phase 3.3 (Core Implementation)
- Phase 3.3 (Core) → Phase 3.4 (UI Components)
- Phase 3.4 (UI) → Phase 3.5 (Integration)
- Phase 3.5 (Integration) → Phase 3.6 (Testing & Validation)

### Critical Path

```
T001 (setup) → T004-T015 (tests) → T016-T024 (models) → T025 (PreferenceService) →
T026-T031 (services) → T032-T040 (UI widgets) → T041-T048 (integration) →
T049-T053 (validation)
```

### Parallelizable Task Groups

**Group 1: Contract Tests (7 tasks)** - Can run simultaneously

```
Task: "Contract test PreferenceService in tests/file_explorer/contract/test_preference_service_contract.py"
Task: "Contract test BookmarkService in tests/file_explorer/contract/test_bookmark_service_contract.py"
Task: "Contract test RecentItemsService in tests/file_explorer/contract/test_recent_items_service_contract.py"
Task: "Contract test ToolsDiscoveryService in tests/file_explorer/contract/test_tools_discovery_service_contract.py"
Task: "Contract test LayoutManager in tests/file_explorer/contract/test_layout_manager_contract.py"
Task: "Contract test StorageDeviceService in tests/file_explorer/contract/test_storage_device_service_contract.py"
Task: "Contract test NotificationService in tests/file_explorer/contract/test_notification_service_contract.py"
```

**Group 2: Integration Tests (5 tasks)** - Can run simultaneously

```
Task: "Integration test hub toggle in tests/file_explorer/integration/test_hub_toggle.py"
Task: "Integration test pane layout changes in tests/file_explorer/integration/test_pane_layout_changes.py"
Task: "Integration test preference persistence in tests/file_explorer/integration/test_preference_persistence.py"
Task: "Integration test empty states in tests/file_explorer/integration/test_empty_states.py"
Task: "Integration test fallback behavior in tests/file_explorer/integration/test_fallback_behavior.py"
```

**Group 3: Data Models (9 tasks)** - Can run simultaneously

```
Task: "Create HubInterfaceMode enum in src/file_explorer/models/hub_interface_mode.py"
Task: "Create LayoutType enum and PaneConfiguration in src/file_explorer/models/pane_configuration.py"
Task: "Create LeftPaneTab enum in src/file_explorer/models/left_pane_tab.py"
Task: "Create RightPaneTab enum in src/file_explorer/models/right_pane_tab.py"
Task: "Create BookmarkType enum and Bookmark in src/file_explorer/models/bookmark.py"
Task: "Create RecentItemType enum and RecentItem in src/file_explorer/models/recent_item.py"
Task: "Create Tool dataclass in src/file_explorer/models/tool.py"
Task: "Create CenterPane dataclass in src/file_explorer/models/center_pane.py"
Task: "Create UserPreferences dataclass in src/file_explorer/models/user_preferences.py"
```

**Group 4: Left Pane Widgets (3 tasks)** - Can run simultaneously

```
Task: "Implement BookmarksWidget in src/file_explorer/ui/bookmarks_widget.py"
Task: "Implement RecentWidget in src/file_explorer/ui/recent_widget.py"
Task: "Implement ToolsWidget in src/file_explorer/ui/tools_widget.py"
```

**Group 5: Right Pane Widgets (2 tasks)** - Can run simultaneously

```
Task: "Implement PreviewWidget in src/file_explorer/ui/preview_widget.py"
Task: "Implement PropertiesWidget in src/file_explorer/ui/properties_widget.py"
```

**Group 6: Validation Tests (3 tasks)** - Can run simultaneously

```
Task: "UI integration tests in tests/file_explorer/ui/"
Task: "End-to-end workflow test in tests/file_explorer/integration/test_e2e_workflow.py"
Task: "Performance benchmarks in tests/performance/"
```

---

## Validation Checklist

**GATE: Checked before marking feature complete**

- [ ] All contract tests written before implementation (TDD verified)
- [ ] All 53 tasks completed
- [ ] T004-T015 contract/integration tests pass
- [ ] All entities have model implementations (T016-T024)
- [ ] All services implemented (T025-T031)
- [ ] All UI widgets functional (T032-T040)
- [ ] Integration complete (T041-T048)
- [ ] Validation tests pass (T049-T053)
- [ ] Performance requirements met (<2s, <200ms, <100ms)
- [ ] Test coverage ≥85%
- [ ] No mypy type errors
- [ ] No flake8 lint errors
- [ ] Cross-platform testing complete (Windows/macOS/Linux)
- [ ] quickstart.md manual tests completed
- [ ] Constitution compliance verified
- [ ] Code review completed
- [ ] Documentation updated

---

## Notes

- **TDD Enforcement**: Phases 3.2 (tests) MUST complete before 3.3 (implementation)
- **Parallel Execution**: [P] tasks can be distributed across team members
- **Commit Strategy**: Commit after each task completion
- **Performance Monitoring**: Use QElapsedTimer for timing measurements in [PERF] tasks
- **Platform Testing**: T048 requires access to all three platforms or CI/CD pipeline
- **UI Testing**: [UI] tasks require display environment (not headless)

---

**Total Tasks**: 53
**Estimated Time**:

- Setup: 2 hours
- Tests: 10 hours
- Core Implementation: 15 hours
- UI Components: 12 hours
- Integration: 8 hours
- Validation: 5 hours
- **Total**: ~52 hours (1-2 weeks with parallelization)
