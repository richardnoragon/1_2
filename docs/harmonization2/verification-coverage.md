# Verification coverage

Evidence updated 2026-09-16. Every row passes the same isolated, temporary-profile
real-Qt launch/visibility/health, injected degradation, rejected retry, validated
recovery, body retention and Return to Hub checks. These checks invoke each tool's
actual fallback where present. Injected health answers verify recovery gating;
they do not prove that a tool diagnoses every possible internal failure.

`tests/harmonization/test_inventory_windows.py` runs each entry in a separate
process with a 30-second deadline. Native platform results remain pending.

The catalogue now has 36 entries following the user-requested Storage Monitor addition.

The action column records narrower tests and does not promote matrix compliance
flags. “Inventory/runtime only” means no claim of complete action coverage.

| Matrix tool | Additional exercised scope |
| --- | --- |
| File Finder | Inventory/runtime only |
| Catalog Files | Inventory/runtime only |
| Rename Files | GUI confirmation, cancelled proposal, apply and undo; exclusive destination and traversal tests |
| Organize Files | Inventory/runtime only |
| Advanced Folders | Preference migration |
| Synchronize | Inventory/runtime only |
| Compress/Decompress | ZIP/TAR round trips; read-only planning; cancellation; changed source; unsafe member rejection |
| Split/Join Files | Inventory/runtime only |
| Enhanced Editor | Preference migration and shared focused-editor dispatch |
| Secure Delete | GUI dry-run, cancelled confirmation and accepted-dispatch boundary; worker lifecycle tested separately |
| Size Analyzer | Inventory/runtime only |
| Duplicate Finder | Inventory/runtime only |
| File Checksum | Inventory/runtime only |
| Empty Folders | Inventory/runtime only |
| Security Preferences | Inventory/runtime only |
| Encrypt/Decrypt | Shared legacy preference contract; no encryption action claim |
| Permissions Editor | GUI preview, cancelled confirmation, apply and mode restoration; target-change rejection (POSIX) |
| Edit Image Metadata | Inventory/runtime only |
| Office Metadata Editor | Inventory/runtime only |
| File Touch | Inventory/runtime only |
| PDF Utilities | Inventory/runtime only |
| Extract Links | Annotation preview/export and source preservation |
| Page Administration | Page plan, insert/reorder/rotate/remove/extract, undo/redo, preview/export and handoff |
| Network Connectivity | Inventory/runtime only |
| Network Scanner | Inventory/runtime only |
| Network Transfer | Inventory/runtime only |
| Bookmark Manager | Inventory/runtime only |
| Privacy Cleaner | Inventory/runtime only |
| Data Anonymizer | CSV/JSON transformations, preview/export, field policies, source preservation |
| Process Monitor | Inventory/runtime only |
| Enhanced Clipboard | Inventory/runtime only |
| System Diagnostics | Inventory/runtime only |
| System Cleanup | Inventory/runtime only |
| Software Maintenance | Shared legacy preference contract; no install/uninstall action claim |
| Preference Portability | Inventory/runtime only |
| Storage Monitor | Rate/reset/missing-counter logic, network discovery, benchmark cleanup/confirmation/cancellation, capacity, toggles/resizing, timeout and real probe lifecycle |

Shared behavioral tests additionally cover live localized/accessibility labels,
user-data preservation, focused-editor dispatch, legacy callback aliases, blocked
commands, worker responsiveness/cancellation, operation correlation, preference
validation, plugin registration and font scaling. Static checks cover Python and
Designer font declarations, Python menu construction and translation-key validity.
They do not inspect screen readers, visual contrast, focus order, every dynamic
message or all callbacks' filesystem/network/system effects.
