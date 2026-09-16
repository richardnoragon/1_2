# Harmonization implementation status

Updated 2026-09-16. This is an integrated implementation pass, **not certification
that every tool or every roadmap phase is complete**.

## Confirmed decisions

- Scope includes phases 2–5, including localization, plugins and workflows.
- Font table wins over the contradictory footnote: body 14 pt, caption 12 pt,
  small text 11 pt. Sizes use Qt points, platform fallbacks and live scaling.
- Plugins are explicitly loaded local Python packages with JSON manifests.
- The original capability matrix's **35 tools** governed the initial rollout.
  The user-requested Storage Monitor extends the catalogue to **36 tools**.
  Historical missing paths were reconciled with existing implementations.
- English is the only shipping language for now; additional languages come later.
- Data Anonymizer performs CSV/JSON field redaction and pseudonymization.
- PDF Page Administration includes insertion from another PDF, along with reorder,
  rotate, remove, extract, preview and source-preserving Save As.
- The existing constitutional spelling, **Exit**, remains unchanged pending
  any requested platform exception.

## Implemented and exercised

| Area | Implemented behavior |
| --- | --- |
| Shared menus | Canonical category order; empty Reports hidden; action and mnemonic conflict rejection; shared labels; late-bound callbacks; unavailable legacy callbacks disabled; visible degraded-menu fallback |
| Navigation | Utility windows expose Ctrl+H Return to Hub; Window lists tracked windows for reopening; tool editing callbacks no longer operate on hub data |
| Typography | Eight font tokens; platform fallbacks; fresh QFonts; live font bindings in shared widgets and matrix entry points; appearance profiles preserve token hierarchy and minimums; shared stylesheet pixel-size overrides removed |
| Interaction | Background file inspection, delayed loading indicator, disabled conflicting controls, cancellation on close/Escape, explicit atomic export; toast severity validation and accessibility updates; destructive confirmation Cancel cannot emit acceptance |
| Undo | Shared Undo/Redo actions and history view for real QUndoStack owners; telemetry on history changes; manifest declaration distinguishes unsupported from undeclared |
| Operations | Versioned correlated start/end/failure telemetry; nested operation IDs; global error codes mapped to safe HubErrorScreen messages |
| Preferences | Typed/versioned bundles on PreferenceManager; migration hooks; complete validation before a single stored value; locale packs/settings, Enhanced Editor and Advanced Folders QSettings consumers use this backend; native values are retained after migration |
| Hub capabilities | Tools → Tool Capabilities shows source availability, reviewed capabilities, undo declarations, available Guardian state and recorded activity; missing evidence stays unverified |
| Guardian | Shared menu windows register with the existing guardian; menu contract failures report degradation and remain visible through fallback actions and health state |
| Localization | Validated JSON packs, placeholder/mnemonic checks, English fallback, live bindings, View → Load Language Pack, persistent locale selection |
| Plugins | Declarative commands, typed preferences and validated telemetry schemas; Tools → Load Local Plugin; atomic identity/schema validation, no import at manifest-read time; launch/reopen installed QWidget entry points; optional undo-stack integration |
| Scenario | PDF page draft → explicit export → PDF Link Extractor, with typed artifacts and worker correlation propagation; Tools → Inspect Files and Checksums: folder discovery → SHA-256 → explicit CSV export; inputs preserved; changing/unreadable files fail rather than yield a misleading complete report |
| CI | Real-Qt contracts and all 35 window probes across a Linux/Windows/macOS matrix; strict UI gates with individually reviewed document-style exceptions |

## New tool workflows

- **Data Anonymizer:** UTF-8 CSV with unique headers, or a JSON object/array of
  objects. Select top-level fields to keep, redact or pseudonymize. Nested values
  are replaced as a whole. Preview is limited to 100 records / 64 KiB; export
  includes all records. A fresh key is generated for each loaded dataset and is
  not persisted. Equal values in the same field share a pseudonym within that
  dataset. Pseudonymization does not guarantee that unselected fields cannot
  identify a person. CSV formula-like cells are escaped for spreadsheet use.
- **PDF Page Administration:** edits an undoable in-memory page plan; insertion
  adds all pages of another PDF after the selected page. Remove only changes the
  draft. Save As exports the draft; Extract exports selected pages in draft order.
  Preview rendering and export run in workers. Password-protected inputs need an
  unencrypted copy. Source paths remain protected even after their pages are
  removed. Undo affects the draft, not a previously exported output.
- **PDF Link Extractor:** now reads annotations without moving the source PDF or
  opening URLs. It previews up to 1,000 links and exports the full result only
  after Save As. This replaces the old implicit source-move behavior.
- Both application hub implementations use the same searchable catalogue (now 36 tools).
  Plugins remain separate additions and cannot replace built-in identities.

## Rollout corrections and verification evidence

The original four rollout notes have been replaced with concrete fixes and
repeatable checks. Evidence is scoped below; a passing launch is not evidence
that every action in a tool is compliant.

1. **Actions and preferences:** Secure Delete defaults to a read-only preview;
   Cancel cannot start deletion, and confirmed deletion runs in a cancellable
   worker. Empty Folders now connects worker-thread slots rather than executing
   its scan/delete lambda on the UI thread. Compression/extraction uses immutable
   previews, safe-default confirmation, cancellation and staged publication;
   extraction rejects traversal, links, special files and existing destinations.
   Rename validates the proposal, runs in a worker, never overwrites a destination,
   and retains reverse steps for completed changes. Permissions Editor preserves
   group/other bits, previews changes, applies them in a worker, and checks the
   target before applying or restoring a mode. Shared workers preserve controls
   that were already disabled. Encryption, secure-delete, splitter and software
   maintenance settings now import legacy JSON once into validated preference
   bundles; source files remain untouched. Explicit configuration exports and
   user documents remain JSON.
2. **Hard gates:** zero unexcepted Python/Designer UI font/menu findings, compared
   with the previous 99-finding baseline. The gate also rejects missing translation
   keys and malformed Designer XML. Eighteen fingerprinted exported-document CSS
   declarations remain separately reviewed in `static-exceptions.json`; the old
   baseline no longer grants UI exemptions. Every catalogue window has a visible-
   window event-loop monitor that reports gaps over 100 ms. Tests demonstrate
   detection of a deliberately blocked loop and responsiveness/cancellation while
   a worker is active. These checks do not establish every action's latency.
3. **Tool runtime:** all 35 entries pass isolated launch, visibility, health,
   forced degradation, failed retry, successful recovery, preserved-body and
   Return to Hub checks. The exercise found and corrected a blocking Image
   Metadata Editor fallback, invalid Empty Folders health check, missing deletion
   callbacks, Designer button constructor incompatibility and broken theme
   expressions. Active-tool dispatch now resolves legacy open/save/export/new/help
   callback aliases, respects focused editors and real undo stacks, and blocks
   conflicting commands while busy or degraded. Commands emit action/error and
   correlated timing events without document contents. There are 1,653 catalogued
   legacy English labels, including Designer metadata; live bindings preserve
   user-entered data. Additional languages are still not shipped.
4. **Platforms:** CI now runs the contract and 35-window inventory suites on Linux,
   native Windows Qt and native Intel macOS Qt, with per-platform JUnit/static
   artifacts. Linux results below were executed locally. The Windows/macOS jobs
   have **not** run in this workspace; configuring them is not a passing result.

### Evidence limits that remain open

- Full action-by-action coverage of all 35 tools, assistive-technology/tab-order
  checks, dynamic legacy messages and every operation's telemetry/preferences
  behavior are not certified by these tests. See
  [verification coverage](verification-coverage.md) for the exact tested scope.
  Matrix compliance flags remain unchanged where this broader evidence is absent.
- Native Windows/macOS job results require running the committed CI workflow on
  those operating systems. Linux offscreen results cannot substitute for them.
- Rename uses exclusive hard-link publication for regular files. Filesystems
  without hard-link support fail without overwriting a destination. Completed
  steps remain undoable after cancellation; this is not a transactional batch.
- Windows Permissions Editor controls the read-only flag, not Windows ACLs.
  POSIX mode-specific tests are explicitly skipped on Windows.

## Plugin manifest

Install the Python package into the application's environment first, then load:

```json
{
  "schema_version": 1,
  "tools": [{
    "tool_id": "example-inspector",
    "display_name": "Example Inspector",
    "module_path": "example_package.gui",
    "class_name": "InspectorWidget",
    "category": "analysis",
    "undo_supported": false
  }]
}
```

The class must construct a QWidget without required constructor arguments.
An undo-supporting plugin must expose `undo_stack: QUndoStack`. Entries cannot
replace a registered tool by ID or normalized display name. Loading is explicit
and session-scoped; there is no package downloader or automatic code discovery.

Optional per-tool declarations:

```json
{
  "commands": [{
    "id": "inspect", "label": "&Inspect", "menu": "Tools",
    "shortcut": "Ctrl+Alt+I", "method": "inspect"
  }],
  "preferences": {
    "schema_version": 1,
    "fields": {"enabled": {"type": "boolean", "default": true}}
  },
  "telemetry": {"inspected": {"count": "integer"}}
}
```

Command methods are public zero-argument methods on the plugin widget. The
registry rejects menu/shortcut conflicts. `widget.plugin_services` provides
`load_preferences()`, `save_preferences(values)` and `emit_event(name, **values)`.
Preference types are string, integer, number (float) and boolean; unknown fields
and incorrect types are rejected. Preference schemas currently support version 1;
a version change requires an explicit migration implementation. Command labels
are catalogued as `Plugin_<tool_id_with_underscores>.<command_id>`.

## Locale pack

```json
{
  "schema_version": 1,
  "locale": "de",
  "strings": {
    "Menu.FILE": "&Datei",
    "Menu.EDIT": "&Bearbeiten"
  }
}
```

This is a format example, not a complete German translation. Unknown keys and
changed placeholders are rejected. Missing keys use English. `LocaleService.load`
returns the missing-key list; `require_complete=True` rejects incomplete packs.
The catalogue is exported by `src.rfu.localization.catalogue()`. Loaded plugin command labels extend that catalogue in their own namespace.

## Validation

```sh
QT_QPA_PLATFORM=offscreen PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  .venv/bin/python -m pytest tests/harmonization tests/unit/core/test_tool_lifecycle.py -q
python3 scripts/quality/check_harmonization.py
git diff --check
```

109 tests passed locally on Linux with real PyQt5, including 35 isolated inventory
window/fallback probes, GUI confirmation/apply/undo, archive traversal rejection,
source preservation, cancellation, event-loop behavior, locale bindings, command
aliases, preference migration, plugin contracts and PDF/data workflows. Changed
Python sources parse successfully; `git diff --check` passes. The local Python
3.14 environment uses Pillow 12.0.0 because Pillow 11.1.0 has no matching wheel;
CI uses Python 3.12 with the repository's Pillow 11.1.0 pin. Native platform results
and complete per-tool action coverage remain pending as described above.

## Storage Monitor addition

The catalogue now includes [Storage Monitor](../storage-monitor.md), with mounted
local/network capacity, OS device activity and observed peaks, an optional
confirmed temporary-file benchmark, and an Always on Top toggle. Queries run in
an isolated process with a five-second timeout. Benchmark work is cancellable
between I/O calls and leaves existing files untouched.

The extended Linux suite passes 118 tests, including eight Storage Monitor tests
and all 36 inventory windows. Historical 35-tool/109-test figures above describe
the preceding rollout. Static gates remain at zero UI violations with 18 reviewed
exported-document style exceptions. Native/network limitations are documented in
the tool guide; no broad compliance flags were promoted for this addition.
