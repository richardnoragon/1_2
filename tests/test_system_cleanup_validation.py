#!/usr/bin/env python3
"""
Test script to validate SystemCleanupGUI instantiation
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    
    print("✅ QApplication created")
    
    from src.utilities.system.system_cleanup import SystemCleanupGUI
    print("✅ SystemCleanupGUI imported successfully")
    print("Class type:", type(SystemCleanupGUI))
    
    print("🔍 Creating instance...")
    instance = SystemCleanupGUI()
    print("✅ Instance created successfully")
    print("Instance type:", type(instance))
    
    print("🔍 Testing validation methods...")
    print("Has hide method:", hasattr(instance, 'hide'))
    print("Has close method:", hasattr(instance, 'close'))
    
    if hasattr(instance, 'hide'):
        instance.hide()
        print("✅ Hide method called")
    
    if hasattr(instance, 'close'):
        instance.close()
        print("✅ Close method called")
    
    app.quit()
    print("✅ Validation test completed successfully")
    
except Exception as e:
    print("❌ Validation test failed:", str(e))
    import traceback
    traceback.print_exc()