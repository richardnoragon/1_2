# Research: Centralized File Type Validator

## Source of Magic Numbers & Signatures

- **Decision**: Curate an internal signature registry seeded from RFU's existing tools (`corruption_detector`, `enhanced_file_model`) and verified against authoritative sources such as fileformat.info.
- **Rationale**: Maintains control over supported formats, enables rapid updates without external dependencies, and aligns with current RFU modules already using signature checks.
- **Alternatives Considered**:
  - **Use python-magic/libmagic bindings**: rejected due to platform-specific dependencies and heavier runtime footprint.
  - **Fully manual per-team maintenance**: rejected because duplicating logic across tools caused drift and inconsistent safety policies.

## Container Format Inspection Strategy

- **Decision**: Perform ZIP-based container inspection (DOCX, ODT, EPUB, JAR) using `zipfile` with early-abort after identifying characteristic entries; fall back to signature heuristics if container unreadable.
- **Rationale**: Aligns with existing RFU patterns (e.g., archive analyzers), respects performance constraint by scanning only entry names, and avoids full extraction.
- **Alternatives Considered**:
  - **External libraries (python-docx, ebooklib)**: rejected because they require full parsing and introduce heavier dependencies.
  - **Skip container inspection**: rejected due to inability to disambiguate zipped Office formats reliably.

## Policy Configuration Integration

- **Decision**: Extend `ConfigManager` to expose per-workflow validator profiles with defaults defined in `config/rfu_config.json`; workflows override via existing namespaced settings.
- **Rationale**: Reuses established configuration infrastructure, supports dynamic reload, and keeps policy governance centralized for audit compliance.
- **Alternatives Considered**:
  - **Environment-variable toggles**: rejected because they do not map cleanly to GUI workflows and lack persistence.
  - **Standalone YAML policy files**: rejected due to duplication of configuration sources and increased user complexity.

## Telemetry & Logging

- **Decision**: Emit structured mismatch events through `log_manager` with evidence array and confidence level, forwarding to existing telemetry sinks.
- **Rationale**: Satisfies Constitution Principle III, ensures observability with minimal new infrastructure, and integrates with established dashboards.
- **Alternatives Considered**:
  - **New telemetry pipeline**: rejected as unnecessary and higher maintenance cost.

## Performance Considerations

- **Decision**: Limit header reads to 2048 bytes, cache repeated evaluations per session, and offload batch scans to worker threads to avoid GUI blockage.
- **Rationale**: Meets Principle IV targets and matches prior implementation strategies in RFU's batch tools.
- **Alternatives Considered**:
  - **Full file hashing for verification**: rejected due to significant performance penalty without additional detection benefit.

## Legacy File-Type Checks Audit (T002)

- **Advanced Folders content indexer**: `src/tools/file_management/advanced_folders/core/content_search_engine.py` imports `python-magic` when available and calls `magic.from_file()` to derive a descriptive type string. The same module falls back to `mimetypes.guess_type()` in several extractors, producing inconsistent labels and lacking confidence tiers.
- **Advanced Folders metadata pipeline & search**: multiple helpers (`metadata_pipeline.py`, `search_engine.py`, `file_system_scanner.py`) duplicate `mimetypes.guess_type()` calls and operate on normalized extensions independently, which frequently misclassifies Office archives and executable payloads.
- **File Explorer classification**: `src/file_explorer/models/enhanced_file_model.py` maintains a large extension catalogue and uses `mimetypes` for MIME inference without verifying on-disk signatures, leading to blind trust of file extensions.
- **Other utilities**: assorted widgets and batch tools (e.g., preview panes, catalog builders) rely on extension-only checks and sparse MIME lookups, with no shared safeguards against malicious renames.

**Implication**: File-type logic is fragmented across modules, mixing optional `python-magic` usage with naive MIME heuristics. This supports migration to a centralized validator that surfaces structured confidence levels, consistent policy outcomes, and removes the optional system dependency on `python-magic`.
