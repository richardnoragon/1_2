#!/usr/bin/env python3
"""
Test script for dark mode functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QApplication, QComboBox, QLabel, QMainWindow,
                                 QPushButton, QVBoxLayout, QWidget)

    # Import our theme system
    try:
        from gui.themes import Colors, ThemeManager
        THEME_AVAILABLE = True
        print("✓ Theme system imported successfully")
    except ImportError as e:
        print(f"✗ Theme system import failed: {e}")
        THEME_AVAILABLE = False
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Dark Mode Test")
            self.setGeometry(100, 100, 600, 400)
            
            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Add some test widgets
            self.label = QLabel("This is a test label")
            layout.addWidget(self.label)
            
            self.combo = QComboBox()
            self.combo.addItems(["Option 1", "Option 2", "Option 3"])
            layout.addWidget(self.combo)
            
            # Theme selector
            theme_combo = QComboBox()
            theme_combo.addItems(["light", "dark"])
            theme_combo.currentTextChanged.connect(self.change_theme)
            layout.addWidget(theme_combo)
            
            self.button = QPushButton("Test Button")
            layout.addWidget(self.button)
            
            # Apply initial theme
            if THEME_AVAILABLE:
                self.apply_theme("light")
        
        def change_theme(self, theme_name):
            """Change the application theme."""
            if THEME_AVAILABLE:
                print(f"Changing theme to: {theme_name}")
                self.apply_theme(theme_name)
            else:
                print("Theme system not available")
        
        def apply_theme(self, theme_name):
            """Apply theme to all widgets."""
            if not THEME_AVAILABLE:
                return
            
            try:
                # Set the theme
                ThemeManager.set_theme(theme_name)
                print(f"Theme set to: {theme_name}")
                print(f"Background color: {Colors.BACKGROUND}")
                print(f"Text color: {Colors.TEXT_PRIMARY}")
                
                # Apply theme to main window
                ThemeManager.apply_main_window_theme(self)
                
                # Apply theme to widgets
                ThemeManager.apply_theme_to_widget(self.label, "label")
                ThemeManager.apply_theme_to_widget(self.combo, "combo")
                ThemeManager.apply_theme_to_widget(self.button, "button_primary")
                
                print(f"✓ Applied {theme_name} theme to all widgets")
                
            except Exception as e:
                print(f"✗ Error applying theme: {e}")
                import traceback
                traceback.print_exc()
    
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        
        print("Testing dark mode functionality...")
        
        # Test theme system
        if THEME_AVAILABLE:
            print("\n=== Theme System Test ===")
            print(f"Initial theme: {Colors.get_theme()}")
            
            # Test light theme
            Colors.set_theme('light')
            print(f"Light theme - Background: {Colors.BACKGROUND}, Text: {Colors.TEXT_PRIMARY}")
            
            # Test dark theme
            Colors.set_theme('dark')
            print(f"Dark theme - Background: {Colors.BACKGROUND}, Text: {Colors.TEXT_PRIMARY}")
            
            print("✓ Theme system working correctly")
        
        # Create and show test window
        window = TestWindow()
        window.show()
        
        print("\nTest window created. Try changing the theme using the dropdown.")
        print("Close the window to exit.")
        
        sys.exit(app.exec_())

except ImportError as e:
    print(f"✗ PyQt5 import failed: {e}")
    print("Please ensure PyQt5 is installed: pip install PyQt5")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()