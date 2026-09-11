# Issue #79 Implementation: Package-Level Architecture and Tool Lifecycle Standardization

**Status**: Completed and closed · Updated 2026-09-11

## Completion Record

- Issue: https://github.com/richardnoragon/1_2/issues/79
- Project board status: Done
- Outcome: package-level architecture and lifecycle standardization baseline documented and synchronized with core architecture references.

## Scope Delivered

This pass documents the package-level architectural decomposition needed to make the RFU application consistent across shared runtime services, GUI entry points, and tool-specific modules. It covers the architectural contract that underpins launch resolution, tool registration, lifecycle tracking, and the shared application-state façade used by hub-style entry points.

The work is scoped to the repo-wide package architecture, not just the active UI/preferences cluster, and it is documented alongside the architecture references already maintained in this repository.

## Clarification Decisions Applied

- Package scope: full RFU application package architecture across core, GUI, tool, and utility layers.
- Documentation target: architecture docs plus an issue-linked architecture note in the docs set.
- Repository boundary: repo-wide architecture package documentation, not limited to the current UI/preferences spec cluster.

## Issue Record Sync

This issue note is intentionally synchronized with the project architecture docs so the issue record and the implementation documentation reflect the same package contract:

- `RFU_Architecture_Documentation_Index.md` links the issue note into the architecture index.
- `RFU_Architecture_Component_Details.md` references the package-level architecture standard.
- `src/core/application_state.py`, `src/core/tool_manifest.py`, and `src/core/tool_lifecycle.py` remain the source-of-truth implementation references for this architecture pass.

## Architectural Goal

The package architecture should make the following rules explicit and repeatable:

1. Shared runtime contracts live in the core package and are imported by both hub and tool entry points.
2. Tool identity and launch metadata are registered once, then resolved through the same contract from all launch paths.
3. Tool lifecycle tracking is not ad hoc per window class; it is centralized in a single runtime tracker.
4. Entry points share the same app-state façade instead of recreating equivalent wiring in separate classes.

## Package-Level Decomposition

### 1) `src/core/`

This layer owns the system-wide lifecycle and runtime contracts that are not tool-specific.

Key responsibilities:

- application startup and runtime service assembly in `application_state.py`
- manifest-backed tool identity in `tool_manifest.py`
- launch resolution and tracker lifecycle in `tool_lifecycle.py`
- centralized telemetry and audit hooks in `audit_trail.py` and `observability.py`
- shared error handling and normalization in `error_handler.py`

Canonical package outputs:

- `ApplicationState` for shared hub/service wiring
- `ToolManifestEntry` and `ToolManifestRegistry` for tool metadata
- `ToolLaunchRequest` and `ToolRuntimeTracker` for launch and runtime lifecycle
- shared audit/observability and error normalization services

### 2) `src/gui/`

This layer owns UI conventions, presentation behavior, window shells, and common styling contracts.

Key responsibilities:

- standard window behavior and shared UI contracts
- common styles and accessibility-aware theme values
- reusable dialogs and widget-level conventions
- hub and tool-window presentation without embedding tool-specific logic

This package should not own package registry logic or tool launch semantics; those remain in the core package and manifest registry.

### 3) `src/tools/`

This layer owns domain-specific tools and their operational logic.

Key responsibilities:

- tool-specific UI implementation and business logic
- tool-level configuration behaviors, file operations, and domain tasks
- local integrations with shared preference and audit services

Each tool should be discoverable through manifest metadata rather than hidden behind ad hoc launcher dictionaries.

### 4) `src/utilities/`

This package retains compatibility and legacy utility entry points for existing tool implementations. It is still part of the package architecture, but its responsibility is narrower than the core contract layer.

It should be treated as:

- a compatibility layer for existing tool launchers
- a place for utilities that are not yet fully migrated to the canonical `src/tools/` layout
- a migration target for packages that need to move onto the manifest-first model

### 5) Entry points (`main.py`, `src/tabbed_hub.py`)

The entry points should remain thin and orchestration-focused:

- resolve application state
- configure shared services
- resolve tool metadata from the manifest when available
- pass a canonical launch request into the runtime tracker
- keep tool-specific instantiation separate from app bootstrap logic

## Core Package Contracts

### ApplicationState

`ApplicationState` is the shared façade for hub-style entry points. It bundles the logger, config manager, preference manager, audit trail, and database availability flag into a single object.

This reduces duplication and ensures that multiple UI entry points do not each re-invent the same startup wiring logic.

### Tool Manifest Registry

`ToolManifestEntry` declares stable metadata for each tool, including:

- `tool_id`
- `display_name`
- `module_path`
- `class_name`
- `category`
- minimum window geometry constraints
- optional version and headless metadata

The registry resolves tool information deterministically and acts as the single source of truth for:

- tool identity
- launch targeting
- minimum size rules
- category classification for audit and observability

### Tool Launch Request Resolution

`resolve_tool_launch_request()` accepts a tool name plus optional module/class overrides. It follows this rule:

- if explicit module/class information is passed, use it directly
- otherwise, resolve against the manifest registry
- return a canonical `ToolLaunchRequest` for downstream launch flow

This eliminates the drift that appears when launch code is duplicated across different hub or launcher implementations.

### ToolRuntimeTracker

`ToolRuntimeTracker` standardizes the lifecycle for runtime tool windows. It handles:

- `register()`
- `unregister()`
- `update_progress()`
- `snapshot()`
- `clear()`

Each action emits structured lifecycle events with runtime metadata such as:

- actor
- session ID
- tool name
- category
- progress summary or operation state

The tracker is therefore the canonical place for tool lifecycle signals, rather than each individual GUI class defining its own custom status model.

## Integration Pattern

The package architecture should enforce the following relationship:

- `src/core` provides shared contracts and registry services
- `src/gui` provides the visual shell and consistent UI behavior
- `src/tools` implements domain logic behind the manifest registry
- `src/utilities` remains a compatibility surface during migration
- `main.py` and the hub orchestrate the assembly but do not re-implement domain logic

This keeps application bootstrap and tool lifecycle stable while allowing tool modules to evolve independently.

## Documentation References

- `src/core/application_state.py`
- `src/core/tool_manifest.py`
- `src/core/tool_lifecycle.py`
- `src/core/__init__.py`
- `src/tabbed_hub.py`
- `main.py`

## Follow-up Recommendations

1. Convert any remaining direct tool-launch hardcoded paths into manifest-backed registration where feasible.
2. Keep `ToolManifestRegistry` as the source of truth for identity and minimum geometry metadata.
3. Continue adding package-level architecture notes whenever a new shared runtime contract is introduced.
4. Keep issue-linked documentation aligned with the architecture index so package changes remain discoverable.
