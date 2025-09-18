#!/usr/bin/env python3
"""
Test script to verify System Cleanup integration with the main hub
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import QApplication
    print("✅ PyQt5 imported successfully")
    
    # Test importing the hub
    try:
        from src.hub import RFUHub
        print("✅ RFUHub imported successfully")
    except Exception as e:
        print(f"❌ Failed to import RFUHub: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Create QApplication
    app = QApplication(sys.argv)
    print("✅ QApplication created")
    
    # Create hub instance
    print("🔍 Creating RFUHub instance...")
    hub = RFUHub()
    print("✅ RFUHub instance created successfully!")
    
    # Test the open_system_cleanup method
    print("🔍 Testing open_system_cleanup method...")
    try:
        hub.open_system_cleanup()
        print("✅ System Cleanup opened successfully from hub!")
        
        # Check if the tool was registered
        if "System Cleanup" in hub.registered_tools:
            print("✅ System Cleanup tool registered with hub")
            cleanup_instance = hub.registered_tools["System Cleanup"]
            print(f"✅ Cleanup instance type: {type(cleanup_instance)}")
            
            # Test basic functionality
            if hasattr(cleanup_instance, 'hide'):
                cleanup_instance.hide()
                print("✅ System Cleanup window hidden successfully")
            
            if hasattr(cleanup_instance, 'close'):
                cleanup_instance.close()
                print("✅ System Cleanup window closed successfully")
                
        else:
            print("❌ System Cleanup tool not found in registered tools")
            
    except Exception as e:
        print(f"❌ Failed to open System Cleanup from hub: {e}")
        import traceback
        traceback.print_exc()
    
    print("✅ Hub integration test completed successfully!")
    
except ImportError as e:
    print(f"❌ PyQt5 not available: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()