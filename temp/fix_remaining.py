import ast
from pathlib import Path

ROOT = Path("C:/Users/HP1/1_2/src")

def fix_bom(path: Path):
    content = path.read_bytes()
    if content.startswith(b"\xef\xbb\xbf"):
        path.write_bytes(content[3:])
        return True
    return False

def fix_line_continuation(path: Path):
    text = path.read_text(encoding="utf-8")
    # Replace backslash followed by spaces and newline with just newline or backslash newline
    # The error "unexpected character after line continuation character" usually means there is space after \
    new_text = ""
    lines = text.splitlines(keepends=True)
    fixed = False
    for line in lines:
        if "\\" in line:
            # Check for trailing whitespace after backslash
            stripped = line.rstrip()
            if stripped.endswith("\\") and len(line.rstrip("\r\n")) > len(stripped):
                 new_text += line.rstrip() + "\n"
                 fixed = True
                 continue
        new_text += line
    if fixed:
        path.write_text(new_text, encoding="utf-8")
    return fixed

# Fix __init__.py BOM
fix_bom(ROOT / "__init__.py")

# Fix line continuations
for rel in ["tools/file_management/advanced_folders/core/search_cache.py", 
            "tools/file_management/advanced_folders/gui/configuration_dialog.py",
            "tools/file_management/advanced_folders/gui/directory_browser.py"]:
    fix_line_continuation(ROOT / rel)

# Fix remaining try/except blocks (missing except)
def fix_missing_except(path: Path):
    text = path.read_text(encoding="utf-8")
    # Simplified: find the end of the try block and add except Exception: pass
    # Usually it's at the end of the file or before another block.
    # For these specific files, they likely have a try: with PyQt5 imports but no except.
    if "try:" in text and "except" not in text:
        # Very crude: append except at the end if the last line is indented
        lines = text.splitlines()
        if lines[-1].startswith("    "):
            lines.append("except ImportError:")
            lines.append("    pass")
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return True
    return False

# Manual check for password_generator and maintenance_hub
for rel in ["tools/security/password_generator/password_generator.py", "tools/system/software_maintenance/gui/maintenance_hub.py"]:
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    # Identify where the try: block is and where it ends.
    # In these files, they seem to have:
    # try:
    #     from PyQt5...
    #     from src.gui.themes import token
    # (no except)
    import re
    m = re.search(r'try:\n(\s+from .+\n)+', text)
    if m:
        end = m.end()
        # Check if except follows
        if not text[end:].strip().startswith("except"):
            new_text = text[:end] + "except ImportError:\n    pass\n" + text[end:]
            p.write_text(new_text, encoding="utf-8")

# Final check
print("=== FINAL RE-CHECK ===")
broken = []
for py in sorted(ROOT.rglob("*.py")):
    try:
        ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as e:
        broken.append(f"{py.relative_to(ROOT.parent)}:{e.lineno}: {e.msg}")
print(f"Count: {len(broken)}")
for b in broken:
    print(b)
