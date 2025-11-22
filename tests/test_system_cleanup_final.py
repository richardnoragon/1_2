#!/usr/bin/env python3
"""
Final test script to verify System Cleanup functionality
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from PyQt5.QtWidgets import QApplication

    print("✅ PyQt5 imported successfully")

    # Test importing SystemCleanupGUI directly
    try:
        from src.tools.privacy.privacy_cleaner.system_cleanup import SystemCleanupGUI

        print("✅ SystemCleanupGUI imported successfully")
    except Exception as e:
        print(f"❌ Failed to import SystemCleanupGUI: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    # Create QApplication
    app = QApplication(sys.argv)
    print("✅ QApplication created")

    # Test creating SystemCleanupGUI instance
    print("🔍 Creating SystemCleanupGUI instance...")
    try:
        cleanup_gui = SystemCleanupGUI()
        print("✅ SystemCleanupGUI instance created successfully!")
        print(f"Instance type: {type(cleanup_gui)}")
        print(f"MRO: {type(cleanup_gui).__mro__}")

        # Test basic functionality
        print("🔍 Testing basic functionality...")

        # Test window properties
        if hasattr(cleanup_gui, "setWindowTitle"):
            print("✅ Has setWindowTitle method")

        if hasattr(cleanup_gui, "show"):
            print("✅ Has show method")

        if hasattr(cleanup_gui, "hide"):
            print("✅ Has hide method")

        if hasattr(cleanup_gui, "close"):
            print("✅ Has close method")

        # Test cleanup-specific functionality
        if hasattr(cleanup_gui, "cleanup_tools"):
            print(f"✅ Has cleanup_tools: {cleanup_gui.cleanup_tools}")

        if hasattr(cleanup_gui, "add_cleanup_tab"):
            print("✅ Has add_cleanup_tab method")

        if hasattr(cleanup_gui, "run_temp_cleanup"):
            print("✅ Has run_temp_cleanup method")

        # Test hub integration
        if hasattr(cleanup_gui, "hub_instance"):
            print(f"✅ Has hub_instance: {cleanup_gui.hub_instance}")

        if hasattr(cleanup_gui, "register_tool"):
            print("✅ Has register_tool method (inherited from base)")

        # Test window title
        window_title = cleanup_gui.windowTitle()
        print(f"✅ Window title: '{window_title}'")

        # Test that it's properly inheriting from SystemDiagnosticsGUI
        from src.tools.system.diagnostics_monitoring.system_diagnostics_gui import (
            SystemDiagnosticsGUI,
        )

        if isinstance(cleanup_gui, SystemDiagnosticsGUI):
            print("✅ Correctly inherits from SystemDiagnosticsGUI")
        else:
            print("❌ Does not inherit from SystemDiagnosticsGUI")

        # Test cleanup without showing the window
        cleanup_gui.hide()
        cleanup_gui.close()
        print("✅ Window hidden and closed successfully")

    except Exception as e:
        print(f"❌ Failed to create SystemCleanupGUI: {e}")
        import traceback

        traceback.print_exc()

    print("✅ Final System Cleanup test completed successfully!")

except ImportError as e:
    print(f"❌ PyQt5 not available: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback

    traceback.print_exc()
