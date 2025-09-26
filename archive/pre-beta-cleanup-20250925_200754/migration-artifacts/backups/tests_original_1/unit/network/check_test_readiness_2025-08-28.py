#!/usr/bin/env python3
"""
Simple test runner to verify target module availability
"""
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    from src.utilities.network.gui import NetworkWorkerThread, NetworkToolsWindow
    print("✓ Target module imported successfully")
    print("✓ NetworkWorkerThread available")
    print("✓ NetworkToolsWindow available")
    TARGET_AVAILABLE = True
except Exception as e:
    print(f"✗ Import failed: {e}")
    TARGET_AVAILABLE = False

try:
    import PyQt5
    print("✓ PyQt5 available")
    PYQT5_AVAILABLE = True
except Exception as e:
    print(f"✗ PyQt5 not available: {e}")
    PYQT5_AVAILABLE = False

print(f"\nTest readiness:")
print(f"  Target module: {'✓' if TARGET_AVAILABLE else '✗'}")
print(f"  PyQt5 framework: {'✓' if PYQT5_AVAILABLE else '✗'}")
print(f"  Overall ready: {'✓' if TARGET_AVAILABLE and PYQT5_AVAILABLE else '✗'}")