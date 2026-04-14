import ast  # syntax check script
import os
import sys

os.chdir(r"C:\Users\HP1\1_2")

files = [
    "src/tools/network/gui.py",
    "src/tools/pdf_tools/dialogs/parameter_dialogs.py",
    "src/tools/pdf_tools/dialogs/security_parameter_dialogs.py",
    "src/tools/analysis/empty_folders/empty_folders.py",
    "src/tools/file_management/advanced_catalog/catalog/catalog.py",
    "src/tools/analysis/config/config_analyzer.py",
    "src/tools/security/security_scanner/security_scanner.py",
    "src/tools/system/process_monitor/process_monitor.py",
    "src/gui/dialogs/security_preferences_dialog.py",
]

all_ok = True
for f in files:
    with open(f, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    try:
        ast.parse(src)
        print(f"OK: {f}")
    except SyntaxError as e:
        print(f"ERR L{e.lineno}: {f} -- {e.msg}")
        all_ok = False

if all_ok:
    print("\nAll 9 files: syntax OK")
else:
    print("\nSome files still have syntax errors")
    sys.exit(1)
