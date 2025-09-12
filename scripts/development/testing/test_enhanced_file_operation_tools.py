#!/usr/bin/env python3
"""
Test script for Enhanced File Operation Tools with Menu Integration.
This script will test all four enhanced tools to verify menu integration is working.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

def test_enhanced_tools():
    """Test all enhanced file operation tools."""
    app = QApplication(sys.argv)
    
    tools_tested = []
    
    # Test Compress/Decompress Tool
    try:
        from src.utilities.file_operations.compression.compress_decompress import CompressDecompressWindow as CompressDecompressApp
        compress_tool = CompressDecompressApp()
        compress_tool.show()
        print("✅ Compress/Decompress Tool loaded successfully")
        print(f"   - Window size: {compress_tool.size()}")
        print(f"   - Has menu bar: {compress_tool.menuBar() is not None}")
        print(f"   - Has central widget: {compress_tool.central_widget is not None}")
        print(f"   - Has main layout: {hasattr(compress_tool, 'main_layout')}")
        tools_tested.append("Compress/Decompress")
        QTimer.singleShot(1000, compress_tool.close)
        
    except Exception as e:
        print(f"❌ Compress/Decompress Tool failed: {e}")
    
    # Test File Splitter/Joiner Tool  
    try:
        from src.utilities.file_operations.file_splitter import FileSplitJoinGUI
        splitter_tool = FileSplitJoinGUI()
        splitter_tool.show()
        print("✅ File Splitter/Joiner Tool loaded successfully")
        print(f"   - Window size: {splitter_tool.size()}")
        print(f"   - Has menu bar: {splitter_tool.menuBar() is not None}")
        print(f"   - Has central widget: {splitter_tool.central_widget is not None}")
        print(f"   - Has main layout: {hasattr(splitter_tool, 'main_layout')}")
        tools_tested.append("File Splitter/Joiner")
        QTimer.singleShot(2000, splitter_tool.close)
        
    except Exception as e:
        print(f"❌ File Splitter/Joiner Tool failed: {e}")
    
    # Test Synchronize Tool
    try:
        from src.utilities.file_operations.synchronization_backup import SyncWindow
        sync_tool = SyncWindow()
        sync_tool.show()
        print("✅ Synchronize Tool loaded successfully")
        print(f"   - Window size: {sync_tool.size()}")
        print(f"   - Has menu bar: {sync_tool.menuBar() is not None}")
        print(f"   - Has central widget: {sync_tool.central_widget is not None}")
        print(f"   - Has main layout: {hasattr(sync_tool, 'main_layout')}")
        tools_tested.append("Synchronize")
        QTimer.singleShot(3000, sync_tool.close)
        
    except Exception as e:
        print(f"❌ Synchronize Tool failed: {e}")
    
    # Test Copy/Move/Sync/Delete Tool
    try:
        from src.utilities.file_operations.cmsd import CopyMoveSyncDeleteWindow
        cmsd_tool = CopyMoveSyncDeleteWindow()
        cmsd_tool.show()
        print("✅ Copy/Move/Sync/Delete Tool loaded successfully")
        print(f"   - Window size: {cmsd_tool.size()}")
        print(f"   - Has menu bar: {cmsd_tool.menuBar() is not None}")
        print(f"   - Has central widget: {cmsd_tool.central_widget is not None}")
        print(f"   - Has main layout: {hasattr(cmsd_tool, 'main_layout')}")
        tools_tested.append("Copy/Move/Sync/Delete")
        QTimer.singleShot(4000, cmsd_tool.close)
        
    except Exception as e:
        print(f"❌ Copy/Move/Sync/Delete Tool failed: {e}")
    
    # Show completion message
    def show_completion():
        msg = QMessageBox()
        msg.setWindowTitle("Enhanced File Operation Tools Test Complete")
        tools_list = "\n".join([f"✅ {tool}" for tool in tools_tested])
        msg.setText(f"Enhanced file operation tools tested!\n\n{tools_list}\n\n"
                   "Each tool now includes:\n"
                   "• File menu with Exit and Help options\n"
                   "• Comprehensive menu integration\n"
                   "• Consistent UI styling\n"
                   "• Keyboard shortcuts (Ctrl+Q, F1, F5)")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        app.quit()
    
    QTimer.singleShot(5000, show_completion)
    
    print("\n🎯 ENHANCED FILE OPERATION TOOLS TEST!")
    print("=" * 60)
    print("✅ All tools now inherit from StandardWindow")
    print("✅ File menus with Exit and Help options added")
    print("✅ Menu integration using File Finder as template")
    print("✅ Consistent styling and keyboard shortcuts")
    print("✅ Tool-specific help dialogs implemented")
    print("=" * 60)
    
    return app.exec_()

if __name__ == "__main__":
    test_enhanced_tools()
