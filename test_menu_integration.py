#!/usr/bin/env python3
"""
Test script for comprehensive menu bar system integration
Tests all four tools: Compress/Decompress, Office Metadata Editor, def test_image_metadata():
    """Test Image Metadata Editor tool menu integration."""
    print("🖼️ Testing Image Metadata Editor Tool...")
    try:
        from src.utilities.metadata.image_metadata import ImageMetadataEditorGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)h, Image Metadata Editor
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt

def test_compress_decompress():
    """Test Compress/Decompress tool menu integration."""
    print("🔧 Testing Compress/Decompress Tool...")
    try:
        from src.utilities.file_operations.compression import CompressDecompressApp
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        tool = CompressDecompressApp()
        
        # Test menu manager existence
        assert hasattr(tool, 'menu_manager'), "Menu manager not found"
        print("✅ Menu manager initialized")
        
        # Test menu callbacks
        callbacks_to_test = [
            'new_compression', 'save_file', 'open_file', 'export_data',
            'import_data', 'print_document', 'cut', 'copy', 'paste',
            'select_all', 'find', 'zoom_in', 'zoom_out', 'zoom_reset',
            'show_options', 'verify_archive', 'batch_operations', 'help_compression'
        ]
        
        for callback in callbacks_to_test:
            assert callback in tool.menu_manager.callbacks, f"Callback {callback} not registered"
        
        print(f"✅ All {len(callbacks_to_test)} menu callbacks registered")
        
        # Test specific methods exist
        methods_to_test = [
            'new_compression_session', 'save_compression_settings', 
            'load_compression_settings', 'verify_archive', 'show_help'
        ]
        
        for method in methods_to_test:
            assert hasattr(tool, method), f"Method {method} not found"
        
        print(f"✅ All {len(methods_to_test)} menu methods implemented")
        
        tool.close()
        print("✅ Compress/Decompress tool test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Compress/Decompress tool test failed: {str(e)}\n")
        return False

def test_office_metadata_editor():
    """Test Office Metadata Editor menu integration."""
    print("📄 Testing Office Metadata Editor...")
    try:
        from src.utilities.metadata.office_meta_data_editor import OfficeMetaDataEditorGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        tool = OfficeMetaDataEditorGUI()
        
        # Test menu manager existence
        assert hasattr(tool, 'menu_manager'), "Menu manager not found"
        print("✅ Menu manager initialized")
        
        # Test menu callbacks
        callbacks_to_test = [
            'new_metadata_session', 'save_file', 'open_file', 'export_data',
            'import_data', 'print_document', 'cut', 'copy', 'paste',
            'select_all', 'find', 'zoom_in', 'zoom_out', 'zoom_reset',
            'show_options', 'batch_processing', 'document_analysis', 'help_metadata'
        ]
        
        for callback in callbacks_to_test:
            assert callback in tool.menu_manager.callbacks, f"Callback {callback} not registered"
        
        print(f"✅ All {len(callbacks_to_test)} menu callbacks registered")
        
        # Test specific methods exist
        methods_to_test = [
            'new_metadata_session', 'save_metadata_settings', 
            'load_metadata_settings', 'analyze_documents', 'show_help'
        ]
        
        for method in methods_to_test:
            assert hasattr(tool, method), f"Method {method} not found"
        
        print(f"✅ All {len(methods_to_test)} menu methods implemented")
        
        tool.close()
        print("✅ Office Metadata Editor test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Office Metadata Editor test failed: {str(e)}\n")
        return False

def test_file_touch():
    """Test File Touch tool menu integration."""
    print("🕒 Testing File Touch Tool...")
    try:
        from src.utilities.file_operations.file_touch import FileTouchWindow
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        tool = FileTouchWindow()
        
        # Test menu manager existence
        assert hasattr(tool, 'menu_manager'), "Menu manager not found"
        print("✅ Menu manager initialized")
        
        # Test menu callbacks
        callbacks_to_test = [
            'new_touch_session', 'save_file', 'open_file', 'export_data',
            'import_data', 'print_document', 'cut', 'copy', 'paste',
            'select_all', 'find', 'zoom_in', 'zoom_out', 'zoom_reset',
            'show_options', 'timestamp_presets', 'batch_operations', 'help_touch'
        ]
        
        for callback in callbacks_to_test:
            assert callback in tool.menu_manager.callbacks, f"Callback {callback} not registered"
        
        print(f"✅ All {len(callbacks_to_test)} menu callbacks registered")
        
        # Test specific methods exist
        methods_to_test = [
            'new_touch_session', 'save_touch_settings', 
            'load_touch_settings', 'show_timestamp_presets', 'show_help'
        ]
        
        for method in methods_to_test:
            assert hasattr(tool, method), f"Method {method} not found"
        
        print(f"✅ All {len(methods_to_test)} menu methods implemented")
        
        tool.close()
        print("✅ File Touch tool test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ File Touch tool test failed: {str(e)}\n")
        return False

def test_image_metadata_editor():
    """Test Image Metadata Editor menu integration."""
    print("🖼️ Testing Image Metadata Editor...")
    try:
        from src.utilities.metadata.image_metadata import ImageMetadataEditorGUI
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        tool = ImageMetadataEditorGUI()
        
        # Test menu manager existence
        assert hasattr(tool, 'menu_manager'), "Menu manager not found"
        print("✅ Menu manager initialized")
        
        # Test menu callbacks
        callbacks_to_test = [
            'new_image_session', 'save_file', 'open_file', 'export_data',
            'import_data', 'print_document', 'cut', 'copy', 'paste',
            'select_all', 'find', 'zoom_in', 'zoom_out', 'zoom_reset',
            'show_options', 'batch_processing', 'metadata_analysis', 'help_image'
        ]
        
        for callback in callbacks_to_test:
            assert callback in tool.menu_manager.callbacks, f"Callback {callback} not registered"
        
        print(f"✅ All {len(callbacks_to_test)} menu callbacks registered")
        
        # Test specific methods exist
        methods_to_test = [
            'new_image_session', 'save_image_settings',
            'load_image_settings', 'analyze_images', 'show_help'
        ]
        
        for method in methods_to_test:
            assert hasattr(tool, method), f"Method {method} not found"
        
        print(f"✅ All {len(methods_to_test)} menu methods implemented")
        
        tool.close()
        print("✅ Image Metadata Editor test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Image Metadata Editor test failed: {str(e)}\n")
        return False

def test_menu_structure():
    """Test that all tools have consistent menu structure."""
    print("📋 Testing Menu Structure Consistency...")
    try:
        # Import menu manager to verify structure
        from gui.menu_manager import MenuManager
        from PyQt5.QtWidgets import QMainWindow
        
        # Create a test window
        test_window = QMainWindow()
        menu_manager = MenuManager(test_window)
        
        # Test menu creation
        menubar = menu_manager.create_standard_menubar("utility")
        assert menubar is not None, "Menu bar creation failed"
        
        # Test that all standard menus exist
        menu_actions = [action.text() for action in menubar.actions()]
        expected_menus = ['&File', '&Edit', '&View', '&Tools', '&Help']
        
        for menu in expected_menus:
            assert menu in menu_actions, f"Menu {menu} not found"
        
        print(f"✅ All {len(expected_menus)} standard menus present")
        
        # Test callback registration
        test_callback = lambda: None
        menu_manager.register_callback('test_action', test_callback)
        assert 'test_action' in menu_manager.callbacks, "Callback registration failed"
        
        print("✅ Callback registration working")
        
        test_window.close()
        print("✅ Menu structure consistency test completed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ Menu structure test failed: {str(e)}\n")
        return False

def create_demo_launcher():
    """Create a demo launcher to test all tools interactively."""
    print("🚀 Creating Demo Launcher...")
    
    class DemoLauncher(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Menu Integration Demo Launcher")
            self.setGeometry(100, 100, 400, 300)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Header
            header = QLabel("Menu Bar Integration Demo")
            header.setAlignment(Qt.AlignCenter)
            header.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 20px;
                    background-color: #ecf0f1;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
            """)
            layout.addWidget(header)
            
            # Tool buttons
            compress_btn = QPushButton("Launch Compress/Decompress Tool")
            compress_btn.clicked.connect(self.launch_compress_decompress)
            layout.addWidget(compress_btn)
            
            metadata_btn = QPushButton("Launch Office Metadata Editor")
            metadata_btn.clicked.connect(self.launch_metadata_editor)
            layout.addWidget(metadata_btn)
            
            touch_btn = QPushButton("Launch File Touch Tool")
            touch_btn.clicked.connect(self.launch_file_touch)
            layout.addWidget(touch_btn)
            
            image_btn = QPushButton("Launch Image Metadata Editor")
            image_btn.clicked.connect(self.launch_image_metadata_editor)
            layout.addWidget(image_btn)
            
            # Info label
            info = QLabel("Each tool now includes comprehensive menu bars with:\n"
                         "• File, Edit, View, Tools, Help menus\n"
                         "• Keyboard shortcuts (Ctrl+N, Ctrl+S, F1, etc.)\n"
                         "• Tool-specific menu options\n"
                         "• Consistent styling and behavior")
            info.setWordWrap(True)
            info.setStyleSheet("padding: 10px; color: #666;")
            layout.addWidget(info)
            
        def launch_compress_decompress(self):
            try:
                from src.utilities.file_operations.compression import CompressDecompressApp
                self.compress_tool = CompressDecompressApp()
                self.compress_tool.show()
            except Exception as e:
                print(f"Error launching Compress/Decompress: {e}")
                
        def launch_metadata_editor(self):
            try:
                from src.utilities.metadata.office_meta_data_editor import OfficeMetaDataEditorGUI
                self.metadata_tool = OfficeMetaDataEditorGUI()
                self.metadata_tool.show()
            except Exception as e:
                print(f"Error launching Office Metadata Editor: {e}")
                
        def launch_file_touch(self):
            try:
                from src.utilities.file_operations.file_touch import FileTouchWindow
                self.touch_tool = FileTouchWindow()
                self.touch_tool.show()
            except Exception as e:
                print(f"Error launching File Touch: {e}")
                
        def launch_image_metadata_editor(self):
            try:
                from src.utilities.metadata.image_metadata import ImageMetadataEditorGUI
                self.image_tool = ImageMetadataEditorGUI()
                self.image_tool.show()
            except Exception as e:
                print(f"Error launching Image Metadata Editor: {e}")
    
    return DemoLauncher()

def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 COMPREHENSIVE MENU BAR INTEGRATION TEST")
    print("=" * 60)
    print()
    
    # Initialize QApplication
    app = QApplication(sys.argv)
    
    # Run tests
    tests = [
        test_menu_structure,
        test_compress_decompress,
        test_office_metadata_editor,
        test_file_touch,
        test_image_metadata_editor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Menu integration is working correctly.")
        
        # Launch demo
        print("\n🚀 Launching interactive demo...")
        demo = create_demo_launcher()
        demo.show()
        
        print("\nDemo launcher created. You can now test each tool interactively.")
        print("Each tool should have comprehensive menu bars with all functionality.")
        
        return app.exec_()
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())