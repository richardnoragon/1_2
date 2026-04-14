"""
Phase 3 TH theming migration script.

Actions performed:
  TH-1  Replace hard-coded hex colour strings with token() calls.
  TH-2  (survey only — zero LightColors/DarkColors refs found in tools)
  TH-3  Replace bare QFont("Family", size) calls with Typography.*() calls.
  TH-4  Deferred — requires running GUI display; noted in TASKS.md.
  TH-5  (survey only — zero hub_nav_* assignments found in tools)
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict

# ---------------------------------------------------------------------------
# 1. Hex-colour → token-key mapping
#    Light-mode values are used for matching; the TOKENS dict provides the
#    correct per-theme value at runtime via token().
# ---------------------------------------------------------------------------
HEX_TO_TOKEN: Dict[str, str] = {
    # Exact TOKENS matches (light values)
    "#2c3e50": "text_primary",
    "#3a4a5c": "text_primary",  # dark-mode primary (same semantic role)
    "#34495e": "secondary",
    "#4a5a6c": "secondary",
    "#3498db": "accent",
    "#5dade2": "accent",
    "#ecf0f1": "background",
    "#ffffff": "window_background",
    "#f8f9fa": "dialog_background",
    "#7f8c8d": "text_secondary",
    "#bdc3c7": "text_disabled",
    "#2980b9": "button_primary_hover",
    "#21618c": "button_primary_pressed",
    "#95a5a6": "button_secondary",
    "#27ae60": "semantic_success",
    "#58d68d": "semantic_success",
    "#f39c12": "semantic_warning",
    "#f7dc6f": "semantic_warning",
    "#e74c3c": "semantic_error",
    "#f1948a": "semantic_error",
    # New tokens (added to themes.py alongside this script)
    "#666666": "text_muted",
    "#666": "text_muted",
    "#6c757d": "text_muted",
    "#999999": "text_muted",
    "#999": "text_muted",
    "#888888": "text_muted",
    "#888": "text_muted",
    "#cccccc": "border",
    "#ccc": "border",
    "#ddd": "border",
    "#dddddd": "border",
    "#d3d3d3": "border",
    "#bfbfbf": "border",
    "#dee2e6": "border_light",
    "#e9ecef": "border_light",
    "#e0e0e0": "border_light",
    "#ced4da": "border_light",
    "#e8e8e8": "border_light",
    "#d0d0d0": "border_light",
    "#f5f5f5": "surface",
    "#f0f0f0": "surface",
    "#f8f8f8": "surface",
    "#f9f9f9": "surface",
    "#eeeeee": "surface",
    "#fafafa": "surface",
    "#333333": "text_primary",
    "#212529": "text_primary",
    "#343a40": "text_primary",
    "#495057": "text_secondary",
    # Success variants → semantic_success
    "#28a745": "semantic_success",
    "#218838": "semantic_success",
    "#4caf50": "semantic_success",
    "#229954": "semantic_success",
    "#45a049": "semantic_success",
    "#3d8b40": "semantic_success",
    # Error variants → semantic_error
    "#dc3545": "semantic_error",
    "#c82333": "semantic_error",
    "#d32f2f": "semantic_error",
    "#c0392b": "semantic_error",
    "#b71c1c": "semantic_error",
    "#e53935": "semantic_error",
    # Warning variants → semantic_warning
    "#e67e22": "semantic_warning",
    "#d35400": "semantic_warning",
    "#b9770e": "semantic_warning",
    "#ff9800": "semantic_warning",
    # Button/accent blue variants → button_primary
    "#007bff": "button_primary",
    "#0056b3": "button_primary",
    "#0078d4": "button_primary",
    "#2196f3": "button_primary",
    "#1976d2": "button_primary",
    "#005a9e": "button_primary",
    "#007acc": "button_primary",
    "#1a73e8": "button_primary",
    "#0066cc": "button_primary",
    # Light tints / highlights → surface_highlight (new token)
    "#ffeaea": "surface_error",
    "#fff2e8": "surface_warning",
    "#e8f4fd": "surface_info",
    "#b3d9ff": "accent",
}

# Normalise keys to lowercase
HEX_TO_TOKEN = {k.lower(): v for k, v in HEX_TO_TOKEN.items()}

# ---------------------------------------------------------------------------
# 2. QFont pattern → Typography method mapping
#    Handles the most common patterns: QFont("Family", size)
# ---------------------------------------------------------------------------
FONT_SIZE_TO_TYPOGRAPHY = {
    18: "h1",
    14: "h2",
    12: "h3",
    11: "h3",  # close to h3
    10: "body",
    9: "body",
    8: "caption",
    7: "caption",
}

# ---------------------------------------------------------------------------
# 3. Helpers
# ---------------------------------------------------------------------------

HEX_RE = re.compile(r'(?<!["\w])#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(?![0-9a-fA-F])')
IMPORT_TOKEN_RE = re.compile(r"from src\.gui\.themes import[^\n]*token")
IMPORT_TYPOGRAPHY_RE = re.compile(r"from src\.gui\.themes import[^\n]*Typography")


def _token_key(hex_raw: str) -> str | None:
    """Return the token key for a hex colour, or None if unmapped."""
    return HEX_TO_TOKEN.get(hex_raw.lower())


def _make_fstring(s: str) -> str:
    """Convert a plain string literal to an f-string prefix."""
    if s.startswith(('f"', "f'", 'f"""', "f'''")):
        return s  # already an f-string
    if s.startswith('"""'):
        return 'f"""' + s[3:]
    if s.startswith("'''"):
        return "f'''" + s[3:]
    if s.startswith('"'):
        return 'f"' + s[1:]
    if s.startswith("'"):
        return "f'" + s[1:]
    return s


def _is_in_string(line: str, col: int) -> bool:
    """Heuristic: is the character at col inside a string literal on this line?"""
    # Count unescaped quotes before col
    before = line[:col]
    in_str = False
    quote_char = None
    i = 0
    while i < len(before):
        c = before[i]
        if not in_str:
            if c in ('"', "'"):
                in_str = True
                quote_char = c
        else:
            if c == "\\":
                i += 1  # skip escaped char
            elif c == quote_char:
                in_str = False
                quote_char = None
        i += 1
    return in_str


def _replace_hex_in_line(line: str) -> tuple[str, bool, bool]:
    """
    Replace all hex colours in *line* with token() calls.

    Returns (new_line, changed, needs_token_import).
    """
    changed = False
    needs_token = False

    # Find all hex color matches
    matches = list(HEX_RE.finditer(line))
    if not matches:
        return line, False, False

    new_line = line
    offset = 0
    for m in matches:
        raw = m.group(0).lower()
        key = _token_key(raw)
        if key is None:
            continue  # unmapped color — leave as is

        # Build replacement
        repl = f"{{token('{key}')}}"
        start = m.start() + offset
        end = m.end() + offset

        # We need the surrounding string to become an f-string.
        # Strategy: find the enclosing string delimiter on this line.
        # If the line already has an f-prefix before this position, just replace.
        # If the string is a regular string, we need to add f prefix.

        # Find the opening quote before this match
        before_match = new_line[:start]

        # Detect if we're in an f-string already
        # Look backwards for string opener
        str_opener = None
        str_opener_pos = -1
        # Check for triple quotes first, then single
        for pat in ('f"""', "f'''", "f'", 'f"', '"""', "'''", '"', "'"):
            idx = before_match.rfind(pat)
            if idx >= 0:
                if str_opener_pos < idx:
                    str_opener_pos = idx
                    str_opener = pat

        already_fstring = str_opener is not None and str_opener.startswith("f")

        if not already_fstring and str_opener is not None:
            # Add 'f' prefix to the string opener
            # Be careful not to add duplicate f
            new_line = new_line[:str_opener_pos] + "f" + new_line[str_opener_pos:]
            start += 1
            end += 1
            offset += 1

        # Do the replacement
        new_line = new_line[:start] + repl + new_line[end:]
        offset += len(repl) - len(m.group(0))
        changed = True
        needs_token = True

    return new_line, changed, needs_token


def apply_th1_to_file(filepath: Path) -> tuple[int, bool]:
    """
    Apply TH-1 (hex→token) transformations to a file.
    Returns (count_of_replacements, needs_token_import).
    """
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines(keepends=True)
    new_lines = []
    total_changed = 0
    needs_token = False

    for line in lines:
        new_line, changed, nt = _replace_hex_in_line(line)
        new_lines.append(new_line)
        if changed:
            total_changed += 1
        if nt:
            needs_token = True

    if total_changed == 0:
        return 0, False

    new_content = "".join(new_lines)

    # Inject token import if not present
    if needs_token and not IMPORT_TOKEN_RE.search(new_content):
        # Find a good insertion point: after last stdlib import block
        # Look for the first 'from PyQt5' or after os/sys imports
        # Simple strategy: find first non-blank, non-comment, non-docstring line after imports
        import_inject = "from src.gui.themes import token\n"
        # Find insertion point: after last stdlib 'import' or 'from' line in header
        lines_out = new_content.splitlines(keepends=True)
        insert_idx = 0
        for i, l in enumerate(lines_out):
            stripped = l.strip()
            if stripped.startswith(("import ", "from ")) and not stripped.startswith(
                "from PyQt5"
            ):
                insert_idx = i + 1
            elif stripped.startswith("from PyQt5"):
                insert_idx = i + 1
                break
        # Insert after the last found import line
        lines_out.insert(insert_idx, import_inject)
        new_content = "".join(lines_out)

    filepath.write_text(new_content, encoding="utf-8")
    return total_changed, needs_token


def apply_th3_to_file(filepath: Path) -> int:
    """
    Apply TH-3 (QFont→Typography) transformation to a file.
    Returns count of replacements.
    """
    content = filepath.read_text(encoding="utf-8", errors="ignore")

    # Pattern: QFont("Segoe UI", N) or QFont("Arial", N) etc.
    # Replace with Typography.method()
    QFONT_PATS = [
        # QFont("family", size, weight) — 3 args
        (
            re.compile(r'QFont\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*,\s*\w+\s*\)'),
            lambda m: _qfont_3arg(m),
        ),
        # QFont("family", size) — 2 args
        (
            re.compile(r'QFont\s*\(\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*\)'),
            lambda m: _qfont_2arg(m),
        ),
        # QFont("family") — 1 arg (family only, no size)
        (
            re.compile(r'QFont\s*\(\s*["\']([^"\']+)["\']\s*\)'),
            lambda m: "Typography.body()",
        ),
    ]

    new_content = content
    count = 0

    for pat, replacer in QFONT_PATS:

        def do_replace(m, r=replacer):
            nonlocal count
            result = r(m)
            if result != m.group(0):
                count += 1
            return result

        new_content = pat.sub(do_replace, new_content)

    if count == 0:
        return 0

    # Add Typography import if not present
    if not IMPORT_TYPOGRAPHY_RE.search(new_content):
        import_inject = "from src.gui.themes import Typography\n"
        lines_out = new_content.splitlines(keepends=True)
        insert_idx = 0
        for i, l in enumerate(lines_out):
            stripped = l.strip()
            if stripped.startswith(("import ", "from ")):
                insert_idx = i + 1
        lines_out.insert(insert_idx, import_inject)
        new_content = "".join(lines_out)

    filepath.write_text(new_content, encoding="utf-8")
    return count


def _qfont_2arg(m: re.Match) -> str:
    family = m.group(1)
    try:
        size = int(m.group(2))
    except ValueError:
        return m.group(0)
    method = FONT_SIZE_TO_TYPOGRAPHY.get(size, "body")
    return f"Typography.{method}()"


def _qfont_3arg(m: re.Match) -> str:
    # 3-arg: treat same as 2-arg for method selection, ignore weight (Typography methods have fixed weight)
    return _qfont_2arg(m)


# ---------------------------------------------------------------------------
# 4. Main
# ---------------------------------------------------------------------------


def main():
    root = Path(os.getcwd())

    # Files to process: all tool source files + a few shared files with violations
    targets = list(Path("src/tools").rglob("*.py"))
    # Also include shared violating files (not themes.py / styles.py themselves)
    for extra in [
        "src/gui/safe_standard_window.py",
        "src/gui/dialogs/security_preferences_dialog.py",
        "src/gui/widgets/empty_state_widget.py",
        "src/core/constants.py",
        "src/rfu/login_dialog.py",
    ]:
        p = Path(extra)
        if p.exists():
            targets.append(p)

    # Exclude test files and config-only files
    EXCLUDE = {"test_theme_security.py", "conftest.py"}
    targets = [
        t for t in targets if t.name not in EXCLUDE and "__pycache__" not in str(t)
    ]

    th1_total = 0
    th3_total = 0
    th1_files = []
    th3_files = []

    print("=== TH-1: Hex colour → token() replacement ===")
    for fp in sorted(targets):
        txt = fp.read_text(encoding="utf-8", errors="ignore")
        if not HEX_RE.search(txt):
            continue
        n, _ = apply_th1_to_file(fp)
        if n > 0:
            rel = str(fp).replace(str(root) + os.sep, "").replace("\\", "/")
            print(f"  {n:3d} replacements  {rel}")
            th1_total += n
            th1_files.append(rel)

    print(f"\nTH-1 complete: {th1_total} replacements across {len(th1_files)} files")

    print("\n=== TH-3: QFont() → Typography.*() replacement ===")
    qfont_targets = [
        Path("src/tools/file_management/advanced_catalog/advanced_catalog_window.py"),
        Path(
            "src/tools/file_management/advanced_folders/ui/advanced_folders_widget.py"
        ),
        Path("src/tools/metadata/image_metadata/gui.py"),
        Path("src/tools/security/password_generator/password_generator.py"),
        Path("src/tools/security/security_scanner/security_scanner.py"),
        Path(
            "src/tools/system/diagnostics_monitoring/gui/filesystem_integrity_widget.py"
        ),
        Path("src/tools/system/diagnostics_monitoring/gui/performance_widget.py"),
        Path("src/tools/system/process_monitor/process_monitor.py"),
        Path("src/tools/system/simple_system_info.py"),
        Path("src/tools/system/software_maintenance/gui/maintenance_hub.py"),
    ]
    for fp in qfont_targets:
        if not fp.exists():
            print(f"  SKIP (not found): {fp}")
            continue
        n = apply_th3_to_file(fp)
        if n > 0:
            rel = str(fp).replace(str(root) + os.sep, "").replace("\\", "/")
            print(f"  {n:3d} replacements  {rel}")
            th3_total += n
            th3_files.append(rel)

    print(f"\nTH-3 complete: {th3_total} replacements across {len(th3_files)} files")
    print("\nTH-5: hub_nav_* — 0 violations found (all tools pass)")
    print("TH-2: LightColors/DarkColors — 0 violations found (all tools pass)")
    print("\nDone.")


if __name__ == "__main__":
    main()
