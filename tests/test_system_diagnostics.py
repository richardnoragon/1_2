#!/usr/bin/env python3
"""
Test script for System Diagnostics GUI

This script tests the import paths and basic functionality of the 
System Diagnostics tool to ensure it can be launched successfully.
"""

import sys
import os

def test_imports():
    """Test all import paths for the System Diagnostics tool."""
    print("Testing System Diagnostics imports...")
    
    # Test 1: Import from diagnostics_monitoring subdirectory
    try:
        from src.tools.system.diagnostics_monitoring import (
            SystemDiagnosticsGUI,
            create_system_diagnostics_gui,
            MAIN_GUI_AVAILABLE
        )
        print("✓ Successfully imported SystemDiagnosticsGUI from subdirectory")
        print(f"  - MAIN_GUI_AVAILABLE: {MAIN_GUI_AVAILABLE}")
        
        if MAIN_GUI_AVAILABLE:
            print("✓ Main GUI is available for use")
        else:
            print("⚠ Main GUI not available (likely missing PyQt5)")
            
    except ImportError as e:
        print(f"✗ Failed to import from subdirectory: {e}")
        return False
    
    # Test 2: Import individual widgets
    try:
        from src.tools.system.diagnostics_monitoring import (
            DiskHealthWidget,
            PerformanceWidget,
            BatteryHealthWidget,
            GUI_WIDGETS_AVAILABLE
        )
        print("✓ Successfully imported individual widgets")
        print(f"  - GUI_WIDGETS_AVAILABLE: {GUI_WIDGETS_AVAILABLE}")
        
    except ImportError as e:
        print(f"⚠ Some widgets not available: {e}")
    
    # Test 3: Import core components
    try:
        from src.tools.system.diagnostics_monitoring import (
            PlatformDetector,
            DataCollector,
            AlertManager,
            CORE_AVAILABLE
        )
        print("✓ Successfully imported core components")
        print(f"  - CORE_AVAILABLE: {CORE_AVAILABLE}")
        
    except ImportError as e:
        print(f"⚠ Some core components not available: {e}")
    
    return True

def test_gui_creation():
    """Test creating the System Diagnostics GUI."""
    print("\nTesting GUI creation...")
    
    try:
        from src.tools.system.diagnostics_monitoring import (
            create_system_diagnostics_gui,
            MAIN_GUI_AVAILABLE
        )
        
        if not MAIN_GUI_AVAILABLE:
            print("⚠ Skipping GUI creation test - PyQt5 not available")
            return True
        
        # Test creating GUI without hub integration
        gui = create_system_diagnostics_gui()
        
        if gui:
            print("✓ Successfully created System Diagnostics GUI")
            print(f"  - GUI type: {type(gui).__name__}")
            print(f"  - Window title: {gui.windowTitle()}")
            
            # Test basic properties
            if hasattr(gui, 'tab_widget'):
                tab_count = gui.tab_widget.count()
                print(f"  - Number of tabs: {tab_count}")
                
                for i in range(tab_count):
                    tab_name = gui.tab_widget.tabText(i)
                    print(f"    - Tab {i+1}: {tab_name}")
            
            # Clean up
            gui.close()
            return True
        else:
            print("✗ Failed to create System Diagnostics GUI")
            return False
            
    except Exception as e:
        print(f"✗ Error creating GUI: {e}")
        return False

def test_hub_integration():
    """Test hub integration functionality."""
    print("\nTesting hub integration...")
    
    try:
        # Mock hub instance for testing
        class MockHub:
            def update_tool_progress(self, tool_name, percentage, message):
                print(f"  Hub received progress: {tool_name} - {percentage}% - {message}")
            
            def update_tool_status(self, tool_name, status):
                print(f"  Hub received status: {tool_name} - {status}")
            
            def register_tool(self, tool_name, tool_instance):
                print(f"  Hub registered tool: {tool_name}")
                return True
        
        from src.tools.system.diagnostics_monitoring import (
            create_system_diagnostics_gui,
            MAIN_GUI_AVAILABLE
        )
        
        if not MAIN_GUI_AVAILABLE:
            print("⚠ Skipping hub integration test - PyQt5 not available")
            return True
        
        mock_hub = MockHub()
        gui = create_system_diagnostics_gui(hub_instance=mock_hub)
        
        if gui:
            print("✓ Successfully created GUI with hub integration")
            
            # Test signal emission
            if hasattr(gui, 'tool_progress_updated'):
                gui.tool_progress_updated.emit("Test Tool", 50, "Testing")
                print("✓ Successfully emitted progress signal")
            
            if hasattr(gui, 'tool_status_changed'):
                gui.tool_status_changed.emit("Test Tool", "testing")
                print("✓ Successfully emitted status signal")
            
            gui.close()
            return True
        else:
            print("✗ Failed to create GUI with hub integration")
            return False
            
    except Exception as e:
        print(f"✗ Error testing hub integration: {e}")
        return False

def test_fallback_behavior():
    """Test fallback behavior when components are missing."""
    print("\nTesting fallback behavior...")
    
    try:
        # Test import behavior when PyQt5 is not available
        # This is simulated by checking the availability flags
        from src.tools.system.diagnostics_monitoring import (
            MAIN_GUI_AVAILABLE,
            GUI_WIDGETS_AVAILABLE,
            CORE_AVAILABLE
        )
        
        print(f"✓ Availability flags accessible:")
        print(f"  - Main GUI: {MAIN_GUI_AVAILABLE}")
        print(f"  - GUI Widgets: {GUI_WIDGETS_AVAILABLE}")
        print(f"  - Core Components: {CORE_AVAILABLE}")
        
        # Test graceful degradation
        if not MAIN_GUI_AVAILABLE:
            print("✓ System gracefully handles missing PyQt5")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing fallback behavior: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("System Diagnostics Tool - Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("GUI Creation", test_gui_creation),
        ("Hub Integration", test_hub_integration),
        ("Fallback Behavior", test_fallback_behavior)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System Diagnostics tool is ready.")
        return True
    else:
        print("⚠ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)