#!/usr/bin/env python3
"""
Debug script to test SystemCleanupGUI inheritance chain
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import QApplication
    print("✅ PyQt5 imported successfully")
    
    # Test importing SystemDiagnosticsGUI directly
    try:
        from utilities.system.diagnostics_monitoring.system_diagnostics_gui import SystemDiagnosticsGUI
        print("✅ SystemDiagnosticsGUI imported successfully")
        print(f"SystemDiagnosticsGUI type: {type(SystemDiagnosticsGUI)}")
        print(f"SystemDiagnosticsGUI MRO: {SystemDiagnosticsGUI.__mro__}")
    except Exception as e:
        print(f"❌ Failed to import SystemDiagnosticsGUI: {e}")
        import traceback
        traceback.print_exc()
        
    # Test importing SystemCleanupGUI
    try:
        from utilities.system.system_cleanup import SystemCleanupGUI
        print("✅ SystemCleanupGUI imported successfully")
        print(f"SystemCleanupGUI type: {type(SystemCleanupGUI)}")
        print(f"SystemCleanupGUI MRO: {SystemCleanupGUI.__mro__}")
        
        # Test creating QApplication
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        # Test instantiation
        print("🔍 Creating SystemCleanupGUI instance...")
        instance = SystemCleanupGUI()
        print("✅ SystemCleanupGUI instance created successfully!")
        print(f"Instance type: {type(instance)}")
        
    except Exception as e:
        print(f"❌ Failed with SystemCleanupGUI: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ PyQt5 not available: {e}")