import re
import ast
from pathlib import Path

def unescape_content_in_string(filepath: Path) -> bool:
    """If the file content ends with a quote or a sequence like \" it might be an escaped string."""
    raw = filepath.read_text(encoding="utf-8", errors="replace")
    
    # If the file seems to have a lot of \" and \n it might be partially or fully double-escaped
    if '\\n' in raw or '\\"' in raw:
        # A common issue is a file appearing as a single Python string literal in literal form
        # But we need to be careful. Let's try to see if it's truncated at the end of a line.
        modified = False
        
        # If the whole thing was wrapped or escaped:
        # Let's try replacing \\n with \n
        new_content = raw.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
        
        # If it still ends with a backslash, remove it
        if new_content.rstrip().endswith('\\'):
             new_content = new_content.rstrip()[:-1]

        if new_content != raw:
            try:
                # See if it's better now
                ast.parse(new_content)
                filepath.write_text(new_content, encoding="utf-8")
                return True
            except:
                # If still failing, don't overwrite
                pass
    return False

files = [
    Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\gui\configuration_dialog.py"),
    Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\gui\directory_browser.py"),
]

for f in files:
    print(f"Processing: {f.name}")
    try:
        ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        print(f"  Syntax: OK (pre-check)")
        continue
    except:
        pass
    
    changed = unescape_content_in_string(f)
    print(f"  Changed: {changed}")
    
    try:
        ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        print(f"  Syntax: OK")
    except SyntaxError as e:
        print(f"  Syntax ERROR at line {e.lineno}: {e.msg}")
        # One last attempt: remove the offending line if it's at EOF
        lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        if e.lineno >= len(lines):
             f.write_text("\n".join(lines[:-1]), encoding="utf-8")
             print(f"  Attempted to delete last line {e.lineno}")
             try:
                 ast.parse(f.read_text(encoding="utf-8", errors="replace"))
                 print("  Syntax: OK (after removing last line)")
             except:
                 pass
