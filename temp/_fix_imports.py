import sys


def fix_file(fp, old, new):
    with open(fp, encoding="utf-8", errors="replace") as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new, 1)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        return "FIXED"
    return "NOT_FOUND"


r = fix_file(
    "src/tools/security/security_scanner/security_scanner.py",
    "try:\n    from PyQt5.QtWidgets import (\nfrom src.gui.themes import token, Typography\n        QMainWindow,",
    "from src.gui.themes import token, Typography\ntry:\n    from PyQt5.QtWidgets import (\n        QMainWindow,",
)
print("security_scanner.py:", r)

r = fix_file(
    "src/tools/system/process_monitor/process_monitor.py",
    "try:\n    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal\nfrom src.gui.themes import token, Typography\n    from PyQt5.QtGui import QFont",
    "from src.gui.themes import token, Typography\ntry:\n    from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal\n    from PyQt5.QtGui import QFont",
)
print("process_monitor.py:", r)

r = fix_file(
    "src/gui/dialogs/security_preferences_dialog.py",
    "try:\n    from PyQt5.QtCore import QDateTime, Qt, QThread, QTimer, pyqtSignal\nfrom src.gui.themes import token\n    from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QPixmap",
    "from src.gui.themes import token\ntry:\n    from PyQt5.QtCore import QDateTime, Qt, QThread, QTimer, pyqtSignal\n    from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QPixmap",
)
print("security_preferences_dialog.py:", r)

# config_analyzer.py - remove stray import from __main__ block, add at top
fp = "src/tools/analysis/config/config_analyzer.py"
with open(fp, encoding="utf-8", errors="replace") as f:
    content = f.read()

stray = "\nfrom src.gui.themes import token\n"
main_block = 'if __name__ == "__main__":\n    import sys\nfrom src.gui.themes import token\n\n    if len(sys.argv) < 2:'
main_fixed = 'if __name__ == "__main__":\n    import sys\n\n    if len(sys.argv) < 2:'

if main_block in content:
    content = content.replace(main_block, main_fixed, 1)
    # Add proper import after yaml import
    content = content.replace(
        "import yaml\n\n\nclass ConfigType",
        "import yaml\n\nfrom src.gui.themes import token\n\n\nclass ConfigType",
        1,
    )
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)
    print("config_analyzer.py: FIXED")
elif "from src.gui.themes import token" in content:
    print("config_analyzer.py: import already in file (from prior run?)")
else:
    print("config_analyzer.py: pattern NOT_FOUND")
