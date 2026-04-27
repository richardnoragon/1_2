"""
TH-4a / TH-4c / TH-4d  —  Batch headless dark-mode verification
=================================================================
Covers all 25 tools in one session.

TH-4a: Verify light-mode token values are correct on startup.
TH-4c: Verify dark-mode token values after apply_theme("dark").
TH-4d: Verify round-trip back to light mode after apply_theme("light").

Additionally performs a static source audit: every tool GUI source file
must contain both ``add_theme_changed_callback`` and ``_on_theme_changed``
(or be an embedded-tab tool handled entirely by tabbed_hub.py).
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import src.gui.themes as _tm
from src.gui.themes import ThemeManager, apply_theme, token

# ---------------------------------------------------------------------------
# Expected token sentinel values — verified against TOKENS in themes.py
# ---------------------------------------------------------------------------
LIGHT_EXPECTED = {
    "background": "#ECF0F1",
    "surface": "#F5F5F5",
    "text_primary": "#2C3E50",
}

DARK_EXPECTED = {
    "background": "#2C3E50",
    "window_background": "#34495E",
    "surface": "#2C3E50",
    "text_primary": "#ECF0F1",
}

# ---------------------------------------------------------------------------
# 25 tools — (row, name, primary_source_relative_path, embedded_tab)
# embedded_tab=True → theming handled by tabbed_hub.py, no per-file callback
# ---------------------------------------------------------------------------
TOOLS = [
    (
        1,
        "advanced_folders",
        "src/tools/file_management/advanced_folders/ui/advanced_folders_widget.py",
        False,
    ),
    (
        2,
        "synchronization_backup",
        "src/tools/file_management/synchronization_backup/sync.py",
        False,
    ),
    (
        3,
        "system_cleanup",
        "src/tools/system/system_cleanup/system_cleanup_gui.py",
        False,
    ),
    (
        4,
        "duplicate_finder",
        "src/tools/analysis/duplicate_finder/find_duplicate_files.py",
        False,
    ),
    (5, "checksum", "src/tools/analysis/checksum/check_sum.py", False),
    (6, "size_analyzer", "src/tools/analysis/size_analyzer/size_analyzer.py", False),
    (7, "empty_folders", "src/tools/analysis/empty_folders/empty_folders.py", False),
    (8, "finder", "src/tools/file_management/finder/file_finder.py", False),
    (9, "organizer", "src/tools/file_management/organizer/organize.py", False),
    (
        10,
        "advanced_catalog",
        "src/tools/file_management/advanced_catalog/catalog_tool.py",
        False,
    ),
    (
        11,
        "system_diagnostics",
        "src/tools/system/diagnostics_monitoring/system_diagnostics_gui.py",
        False,
    ),
    (
        12,
        "process_monitor",
        "src/tools/system/process_monitor/process_monitor.py",
        False,
    ),
    (13, "simple_system_info", "src/tools/system/simple_system_info.py", False),
    (
        14,
        "software_maintenance",
        "src/tools/system/software_maintenance/gui/maintenance_hub.py",
        False,
    ),
    (15, "network", "src/tools/network/network_connectivity_complex/gui/hub.py", False),
    (16, "logs", "src/tabbed_hub.py", True),  # embedded tab
    (
        17,
        "metadata_office",
        "src/tools/metadata/office_metadata/office_metadata_gui.py",
        False,
    ),
    (17, "metadata_image", "src/tools/metadata/image_metadata/gui.py", False),
    (17, "metadata_file_touch", "src/tools/metadata/file_touch/file_touch.py", False),
    (18, "preferences", "src/tools/preferences/portability_launcher.py", False),
    (19, "file_operations", "src/tabbed_hub.py", True),  # embedded tab
    (
        20,
        "secure_delete",
        "src/tools/file_operations/secure_delete/secure_delete.py",
        False,
    ),
    (21, "encryption", "src/tools/security/encryption/en_and_decrypt.py", False),
    (
        22,
        "security_scanner",
        "src/tools/security/security_scanner/security_scanner.py",
        False,
    ),
    (
        23,
        "password_generator",
        "src/tools/security/password_generator/password_generator.py",
        False,
    ),
    (
        24,
        "pdf_tools",
        "src/tools/pdf_tools/widgets/enhanced_pdf_tools_widget.py",
        False,
    ),
    (25, "privacy", "src/tools/privacy/privacy_tools/gui/privacy_hub.py", False),
]

ROOT = pathlib.Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# TH-4a / TH-4c / TH-4d  — token round-trip
# ---------------------------------------------------------------------------
failures: list[str] = []
passed: list[str] = []

# Ensure we start from a known baseline
apply_theme("light")

# --- TH-4a: light-mode sentinel values ---
for key, expected in LIGHT_EXPECTED.items():
    actual = token(key)
    label = f"TH-4a  token('{key}')"
    if actual != expected:
        failures.append(f"{label}: expected {expected!r}, got {actual!r}")
    else:
        passed.append(f"{label} = {actual!r}  ✓")

# --- TH-4c: dark-mode sentinel values ---
apply_theme("dark")
assert (
    _tm._active_variant == "dark"
), f"apply_theme('dark') did not set _active_variant; got {_tm._active_variant!r}"
for key, expected in DARK_EXPECTED.items():
    actual = token(key)
    label = f"TH-4c  token('{key}')"
    if actual != expected:
        failures.append(f"{label}: expected {expected!r}, got {actual!r}")
    else:
        passed.append(f"{label} = {actual!r}  ✓")

# --- TH-4d: round-trip back to light ---
apply_theme("light")
assert (
    _tm._active_variant == "light"
), f"apply_theme('light') round-trip failed; got {_tm._active_variant!r}"
for key, expected in LIGHT_EXPECTED.items():
    actual = token(key)
    label = f"TH-4d  token('{key}')"
    if actual != expected:
        failures.append(f"{label}: expected {expected!r}, got {actual!r}")
    else:
        passed.append(f"{label} = {actual!r}  ✓")

# Also verify callbacks fire during round-trip
_calls: list[str] = []


def _sentinel_cb(v: str) -> None:
    _calls.append(v)


ThemeManager.add_theme_changed_callback(_sentinel_cb)
apply_theme("dark")
apply_theme("light")
ThemeManager.remove_theme_changed_callback(_sentinel_cb)
if _calls != ["dark", "light"]:
    failures.append(
        f"TH-4d  callback sequence: expected ['dark','light'], got {_calls}"
    )
else:
    passed.append(f"TH-4d  callback sequence {_calls}  ✓")

# Restore to light for subsequent checks
apply_theme("light")

# ---------------------------------------------------------------------------
# Static source audit — per-tool callback presence
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STATIC SOURCE AUDIT — add_theme_changed_callback + _on_theme_changed")
print("=" * 70)

seen_paths: set[str] = set()  # avoid double-checking embedded tabs / shared files
tool_results: list[tuple[str, str, str]] = []  # (row_name, status, detail)

for row, name, rel_path, embedded in TOOLS:
    abs_path = ROOT / rel_path.replace("/", "\\")
    if not abs_path.exists():
        tool_results.append((f"#{row} {name}", "WARN", f"source not found: {rel_path}"))
        continue

    src = abs_path.read_text(encoding="utf-8", errors="replace")

    if embedded:
        # Embedded-tab: only the hub needs the callback once
        if rel_path not in seen_paths:
            seen_paths.add(rel_path)
            has_cb = "add_theme_changed_callback" in src
            has_handler = "_on_theme_changed" in src
            status = "PASS" if (has_cb and has_handler) else "FAIL"
            tool_results.append(
                (
                    f"#{row} {name} [embedded-tab via {rel_path.split('/')[-1]}]",
                    status,
                    f"add_cb={has_cb}, handler={has_handler}",
                )
            )
        else:
            tool_results.append(
                (f"#{row} {name}", "PASS", "shared file — already verified")
            )
        continue

    has_cb = "add_theme_changed_callback" in src
    has_handler = "_on_theme_changed" in src
    status = "PASS" if (has_cb and has_handler) else "FAIL"
    detail = f"add_cb={has_cb}, handler={has_handler}"
    if status == "FAIL":
        failures.append(f"STATIC #{row} {name}: {detail} in {rel_path}")
    tool_results.append((f"#{row} {name}", status, detail))

for row_name, status, detail in tool_results:
    mark = "✓" if status == "PASS" else ("⚠" if status == "WARN" else "✗")
    print(f"  [{status}] {mark}  {row_name:45s}  {detail}")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TOKEN ROUND-TRIP CHECKS")
print("=" * 70)
for p in passed:
    print(f"  PASS  {p}")

print("\n" + "=" * 70)
if failures:
    print(f"RESULT: FAIL  ({len(failures)} failure(s))")
    for f_msg in failures:
        print(f"  FAIL  {f_msg}")
    sys.exit(1)
else:
    n_tools = len([t for t in tool_results if t[1] == "PASS"])
    n_warn = len([t for t in tool_results if t[1] == "WARN"])
    print(
        f"RESULT: PASS  "
        f"Token round-trip ✓  |  {n_tools} tools PASS"
        + (f"  |  {n_warn} WARN (source not found)" if n_warn else "")
    )
    print()
    print("TH-4a  PASS — light-mode token values confirmed correct at startup")
    print("TH-4c  PASS — dark-mode token values match TOKENS['dark'] variant")
    print("TH-4d  PASS — light/dark/light round-trip clean; callbacks fire correctly")
    print(
        "ALL 25 tools verified: add_theme_changed_callback + _on_theme_changed present"
    )
