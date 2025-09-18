#!/usr/bin/env python3
# Simple Import Validation Test
# Tests basic imports after reorganization

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'scripts', 'maintenance'))

print("ENTERPRISE IMPORT VALIDATION TEST")
print("=" * 50)

# Test 1: Core constants
try:
    from src.core.constants import APP_NAME
    print(f"[PASS] Core constants: {APP_NAME}")
except ImportError as e:
    print(f"[FAIL] Core constants: {e}")

# Test 2: Database manager (relocated)
try:
    from scripts.maintenance.standalone_database_manager import get_database_manager
    print("[PASS] Database manager import")
except ImportError as e:
    print(f"[FAIL] Database manager: {e}")

# Test 3: GUI components
try:
    from src.gui.menu_manager import MenuManager
    print("[PASS] Menu manager import")
except ImportError as e:
    print(f"[FAIL] Menu manager: {e}")

# Test 4: Tools structure
try:
    from src.tools.analysis.size_analyzer import SizeAnalyzerGUI
    print("[PASS] Size analyzer tool")
except ImportError as e:
    print(f"[WARN] Size analyzer: {e}")

# Test 5: Application startup
try:
    from PyQt5.QtWidgets import QApplication
    print("[PASS] PyQt5 available")
except ImportError:
    print("[WARN] PyQt5 not available")

print("\nValidation complete. Check [PASS] status for working imports.")