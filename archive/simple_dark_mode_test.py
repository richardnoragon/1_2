#!/usr/bin/env python3
"""
Simple Dark Mode Test
"""

import sys

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QColor
    from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QLabel,
                                 QMainWindow, QPushButton, QVBoxLayout,
                                 QWidget)
except ImportError:
    print("PyQt5 not available")
    sys.exit(1)

# Simple theme classes
class LightColors:
    BACKGROUND = "#ECF0F1"
    WINDOW_BACKGROUND = "#FFFFFF"
    TEXT_PRIMARY = "#2C3E50"
    BUTTON_PRIMARY = "#3498DB"
    BUTTON_PRIMARY_HOVER = "#2980B9"

class DarkColors:
    BACKGROUND = "#2C3E50"
    WINDOW_BACKGROUND = "#34495E"
    TEXT_PRIMARY = "#ECF0F1"
    BUTTON_PRIMARY = "#5DADE2"
    BUTTON_PRIMARY_HOVER = "#7FB3D3"

class SimpleThemeManager:
    current_theme = "light"
    
    @classmethod
    def set_theme(cls, theme_name):
        cls.current_theme = theme_name
    
    @classmethod
    def get_colors(cls):
        return DarkColors if cls.current_theme == "dark" else LightColors
    
    @classmethod
    def apply_main_window_style(cls, window):
        colors = cls.get_colors()
        style = f"""
        QMainWindow {{
            background-color: {colors.WINDOW_BACKGROUND};
            color: {colors.TEXT_PRIMARY};
        }}
        """
        window.setStyleSheet(style)
    
    @classmethod
    def apply_button_style(cls, button):
        colors = cls.get_colors()
        style = f"""
        QPushButton {{
            background-color: {colors.BUTTON_PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {colors.BUTTON_PRIMARY_HOVER};
        }}
        """
        button.setStyleSheet(style)
    
    @classmethod
    def apply_label_style(cls, label):
        colors = cls.get_colors()
        style = f"""
        QLabel {{
            color: {colors.TEXT_PRIMARY};
            font-size: 12px;
        }}
        """
        label.setStyleSheet(style)

class DarkModeTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dark Mode Test - RFU File Explorer")
        self.setGeometry(200, 200, 500, 300)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        self.title_label = QLabel("RFU File Explorer - Dark Mode Test")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)
        
        # Theme selector
        theme_frame = QFrame()
        theme_layout = QVBoxLayout(theme_frame)
        
        theme_label = QLabel("Select Theme:")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_frame)
        
        # Sample content
        self.content_label = QLabel("This is sample content that should change colors with the theme.")
        layout.addWidget(self.content_label)
        
        # Test button
        self.test_button = QPushButton("Test Button")
        self.test_button.clicked.connect(lambda: print("Button clicked!"))
        layout.addWidget(self.test_button)
        
        # Status
        self.status_label = QLabel("Theme: Light Mode")
        layout.addWidget(self.status_label)
        
        # Apply initial theme
        self.apply_theme("light")
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        self.apply_theme(theme_name)
        self.status_label.setText(f"Theme: {theme_name.title()} Mode")
        print(f"✓ Changed to {theme_name} theme")
    
    def apply_theme(self, theme_name):
        """Apply theme to all widgets."""
        try:
            # Set the theme
            SimpleThemeManager.set_theme(theme_name)
            colors = SimpleThemeManager.get_colors()
            
            print(f"Applying {theme_name} theme:")
            print(f"  Background: {colors.WINDOW_BACKGROUND}")
            print(f"  Text: {colors.TEXT_PRIMARY}")
            
            # Apply to main window
            SimpleThemeManager.apply_main_window_style(self)
            
            # Apply to widgets
            SimpleThemeManager.apply_label_style(self.title_label)
            SimpleThemeManager.apply_label_style(self.content_label)
            SimpleThemeManager.apply_label_style(self.status_label)
            SimpleThemeManager.apply_button_style(self.test_button)
            
            # Style the combo box
            combo_style = f"""
            QComboBox {{
                background-color: {colors.WINDOW_BACKGROUND};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid #ccc;
                padding: 4px;
                border-radius: 4px;
            }}
            """
            self.theme_combo.setStyleSheet(combo_style)
            
            print(f"✓ {theme_name.title()} theme applied successfully")
            
        except Exception as e:
            print(f"✗ Error applying theme: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    print("=== RFU Dark Mode Test ===")
    print("Testing theme switching functionality...")
    
    window = DarkModeTestWindow()
    window.show()
    
    print("\nWindow shown. Use the dropdown to test theme switching.")
    print("You should see:")
    print("  - Light theme: white background, dark text")
    print("  - Dark theme: dark background, light text")
    print("\nClose window to exit.")
    
    sys.exit(app.exec_())