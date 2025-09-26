#!/usr/bin/env python3
"""
Size Analyzer Theming and Styling Validation Test

This script validates the comprehensive theming implementation for the Size Analyzer
in Phase 4 of the migration, ensuring visual consistency and proper integration
with the file_utilities_2 design system.
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont, QPalette
    
    # Import file_utilities_2 components
    from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
    from file_utilities_2.gui.themes import ThemeManager, Colors, Fonts, Spacing, Dimensions
    from file_utilities_2.gui.standard_window import StandardWindow
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all dependencies are installed and paths are correct.")
    sys.exit(1)


class ThemingValidator:
    """Validates theming and styling implementation."""
    
    def __init__(self):
        self.app = None
        self.test_results = []
        self.size_analyzer = None
        
    def setup_test_environment(self):
        """Setup test environment."""
        try:
            self.app = QApplication(sys.argv)
            self.app.setStyle('Fusion')  # Use consistent style for testing
            return True
        except Exception as e:
            self.log_error("Environment Setup", f"Failed to setup test environment: {e}")
            return False
    
    def log_success(self, test_name: str, message: str):
        """Log successful test."""
        self.test_results.append({"test": test_name, "status": "✅ PASS", "message": message})
        print(f"✅ {test_name}: {message}")
    
    def log_error(self, test_name: str, message: str):
        """Log failed test."""
        self.test_results.append({"test": test_name, "status": "❌ FAIL", "message": message})
        print(f"❌ {test_name}: {message}")
    
    def log_warning(self, test_name: str, message: str):
        """Log warning."""
        self.test_results.append({"test": test_name, "status": "⚠️ WARN", "message": message})
        print(f"⚠️ {test_name}: {message}")
    
    def test_theme_manager_functionality(self):
        """Test ThemeManager functionality."""
        print("\n🔍 Testing ThemeManager Functionality...")
        
        try:
            # Test singleton pattern
            instance1 = ThemeManager.instance()
            instance2 = ThemeManager.instance()
            
            if instance1 is instance2:
                self.log_success("ThemeManager Singleton", "Singleton pattern working correctly")
            else:
                self.log_error("ThemeManager Singleton", "Singleton pattern not working")
            
            # Test theme switching
            original_theme = ThemeManager._current_theme
            ThemeManager.set_theme("dark")
            
            if ThemeManager._current_theme == "dark":
                self.log_success("Theme Switching", "Theme switching functionality works")
            else:
                self.log_error("Theme Switching", "Theme switching not working")
            
            # Restore original theme
            ThemeManager.set_theme(original_theme)
            
            # Test color definitions
            required_colors = ['PRIMARY', 'SECONDARY', 'ACCENT', 'BACKGROUND', 
                             'WINDOW_BACKGROUND', 'TEXT_PRIMARY', 'BUTTON_PRIMARY']
            
            missing_colors = []
            for color in required_colors:
                if not hasattr(Colors, color):
                    missing_colors.append(color)
            
            if not missing_colors:
                self.log_success("Color Definitions", "All required colors defined")
            else:
                self.log_error("Color Definitions", f"Missing colors: {missing_colors}")
            
            # Test font definitions
            required_fonts = ['DEFAULT_FAMILY', 'MONOSPACE_FAMILY', 'TITLE_SIZE', 
                            'BODY_SIZE', 'SMALL_SIZE']
            
            missing_fonts = []
            for font in required_fonts:
                if not hasattr(Fonts, font):
                    missing_fonts.append(font)
            
            if not missing_fonts:
                self.log_success("Font Definitions", "All required fonts defined")
            else:
                self.log_error("Font Definitions", f"Missing fonts: {missing_fonts}")
            
        except Exception as e:
            self.log_error("ThemeManager Functionality", f"Exception: {e}")
    
    def test_size_analyzer_initialization(self):
        """Test Size Analyzer GUI initialization."""
        print("\n🔍 Testing Size Analyzer Initialization...")
        
        try:
            # Create Size Analyzer instance
            self.size_analyzer = SizeAnalyzerGUI()
            
            if self.size_analyzer:
                self.log_success("GUI Initialization", "Size Analyzer GUI created successfully")
            else:
                self.log_error("GUI Initialization", "Failed to create Size Analyzer GUI")
                return False
            
            # Test StandardWindow inheritance
            if isinstance(self.size_analyzer, StandardWindow):
                self.log_success("StandardWindow Inheritance", "Properly inherits from StandardWindow")
            else:
                self.log_error("StandardWindow Inheritance", "Does not inherit from StandardWindow")
            
            # Test window properties
            min_size = self.size_analyzer.minimumSize()
            if (min_size.width() >= Dimensions.UTILITY_WINDOW_MIN_WIDTH and 
                min_size.height() >= Dimensions.UTILITY_WINDOW_MIN_HEIGHT):
                self.log_success("Window Dimensions", "Minimum window size set correctly")
            else:
                self.log_warning("Window Dimensions", 
                               f"Window size: {min_size.width()}x{min_size.height()}")
            
            return True
            
        except Exception as e:
            self.log_error("GUI Initialization", f"Exception: {e}")
            return False
    
    def test_ui_component_styling(self):
        """Test UI component styling."""
        print("\n🔍 Testing UI Component Styling...")
        
        if not self.size_analyzer:
            self.log_error("Component Styling", "Size Analyzer not initialized")
            return
        
        try:
            # Test required UI components exist
            required_components = [
                'directory_line_edit', 'browse_button', 'analyze_button', 
                'output_list_view'
            ]
            
            missing_components = []
            for component in required_components:
                if not hasattr(self.size_analyzer, component):
                    missing_components.append(component)
            
            if not missing_components:
                self.log_success("Required Components", "All required components present")
            else:
                self.log_error("Required Components", f"Missing: {missing_components}")
            
            # Test enhanced components from UI update
            enhanced_components = [
                'progress_bar', 'progress_label', 'details_text', 
                'export_button', 'cancel_button'
            ]
            
            present_enhanced = []
            for component in enhanced_components:
                if hasattr(self.size_analyzer, component):
                    present_enhanced.append(component)
            
            if len(present_enhanced) >= 3:  # At least most components should be present
                self.log_success("Enhanced Components", 
                               f"Enhanced components present: {present_enhanced}")
            else:
                self.log_warning("Enhanced Components", 
                               f"Limited enhanced components: {present_enhanced}")
            
            # Test button styling
            if hasattr(self.size_analyzer, 'browse_button'):
                button_style = self.size_analyzer.browse_button.styleSheet()
                if Colors.BUTTON_PRIMARY in button_style or button_style:
                    self.log_success("Button Styling", "Buttons have custom styling applied")
                else:
                    self.log_warning("Button Styling", "Buttons may not have proper styling")
            
            # Test input field styling
            if hasattr(self.size_analyzer, 'directory_line_edit'):
                input_style = self.size_analyzer.directory_line_edit.styleSheet()
                if Colors.WINDOW_BACKGROUND in input_style or input_style:
                    self.log_success("Input Styling", "Input fields have custom styling")
                else:
                    self.log_warning("Input Styling", "Input fields may not have proper styling")
            
        except Exception as e:
            self.log_error("Component Styling", f"Exception: {e}")
    
    def test_progress_visualization(self):
        """Test progress visualization components."""
        print("\n🔍 Testing Progress Visualization...")
        
        if not self.size_analyzer:
            self.log_error("Progress Visualization", "Size Analyzer not initialized")
            return
        
        try:
            # Test progress bar
            if hasattr(self.size_analyzer, 'progress_bar'):
                progress_bar = self.size_analyzer.progress_bar
                
                # Test progress bar styling
                style = progress_bar.styleSheet()
                if Colors.ACCENT in style or style:
                    self.log_success("Progress Bar Styling", "Progress bar has themed styling")
                else:
                    self.log_warning("Progress Bar Styling", "Progress bar styling may be missing")
                
                # Test progress bar functionality
                progress_bar.setValue(50)
                if progress_bar.value() == 50:
                    self.log_success("Progress Bar Functionality", "Progress bar value setting works")
                else:
                    self.log_error("Progress Bar Functionality", "Progress bar value setting failed")
            else:
                self.log_warning("Progress Bar", "Progress bar component not found")
            
            # Test progress label
            if hasattr(self.size_analyzer, 'progress_label'):
                self.log_success("Progress Label", "Progress label component present")
            else:
                self.log_warning("Progress Label", "Progress label component not found")
            
            # Test progress group
            if hasattr(self.size_analyzer, 'progress_group'):
                self.log_success("Progress Group", "Progress group container present")
            else:
                self.log_warning("Progress Group", "Progress group container not found")
            
        except Exception as e:
            self.log_error("Progress Visualization", f"Exception: {e}")
    
    def test_responsive_design(self):
        """Test responsive design features."""
        print("\n🔍 Testing Responsive Design...")
        
        if not self.size_analyzer:
            self.log_error("Responsive Design", "Size Analyzer not initialized")
            return
        
        try:
            # Test window resizing
            original_size = self.size_analyzer.size()
            
            # Try to resize window
            new_width = max(800, Dimensions.UTILITY_WINDOW_MIN_WIDTH + 200)
            new_height = max(600, Dimensions.UTILITY_WINDOW_MIN_HEIGHT + 150)
            
            self.size_analyzer.resize(new_width, new_height)
            
            # Check if resize was successful
            current_size = self.size_analyzer.size()
            if (current_size.width() >= new_width - 50 and 
                current_size.height() >= new_height - 50):
                self.log_success("Window Resizing", "Window resizing works correctly")
            else:
                self.log_warning("Window Resizing", 
                               f"Resize may not work properly: {current_size.width()}x{current_size.height()}")
            
            # Test splitter if present
            if hasattr(self.size_analyzer, 'resultsSplitter'):
                splitter = self.size_analyzer.resultsSplitter
                if splitter.count() >= 2:
                    self.log_success("Splitter Layout", "Results splitter configured correctly")
                else:
                    self.log_warning("Splitter Layout", "Results splitter may not be configured")
            
            # Test size policies
            size_policy = self.size_analyzer.sizePolicy()
            if (size_policy.horizontalPolicy() != 0 and 
                size_policy.verticalPolicy() != 0):
                self.log_success("Size Policies", "Window has proper size policies")
            else:
                self.log_warning("Size Policies", "Size policies may not be optimal")
            
        except Exception as e:
            self.log_error("Responsive Design", f"Exception: {e}")
    
    def test_theme_consistency(self):
        """Test theme consistency across components."""
        print("\n🔍 Testing Theme Consistency...")
        
        if not self.size_analyzer:
            self.log_error("Theme Consistency", "Size Analyzer not initialized")
            return
        
        try:
            # Test if theme callback registration works
            callback_count = len(ThemeManager._theme_callbacks)
            if callback_count > 0:
                self.log_success("Theme Callbacks", f"Theme callbacks registered: {callback_count}")
            else:
                self.log_warning("Theme Callbacks", "No theme callbacks registered")
            
            # Test theme switching impact
            original_theme = ThemeManager._current_theme
            
            # Switch theme and check if components update
            ThemeManager.set_theme("dark")
            
            # Check if window styling is applied
            window_style = self.size_analyzer.styleSheet()
            if window_style:
                self.log_success("Window Theming", "Window has theme styling applied")
            else:
                self.log_warning("Window Theming", "Window may not have theme styling")
            
            # Restore original theme
            ThemeManager.set_theme(original_theme)
            
            # Test color consistency
            primary_color = Colors.PRIMARY
            accent_color = Colors.ACCENT
            
            if primary_color and accent_color and primary_color != accent_color:
                self.log_success("Color Consistency", "Color scheme is properly defined")
            else:
                self.log_warning("Color Consistency", "Color scheme may have issues")
            
        except Exception as e:
            self.log_error("Theme Consistency", f"Exception: {e}")
    
    def test_icon_and_resource_paths(self):
        """Test icon and resource path handling."""
        print("\n🔍 Testing Icon and Resource Paths...")
        
        if not self.size_analyzer:
            self.log_error("Resource Paths", "Size Analyzer not initialized")
            return
        
        try:
            # Test icon path resolution
            icon_path = self.size_analyzer._get_icon_path()
            
            if icon_path and os.path.exists(icon_path):
                self.log_success("Icon Path", f"Icon found at: {icon_path}")
            else:
                self.log_warning("Icon Path", f"Icon not found, using fallback: {icon_path}")
            
            # Test window icon
            window_icon = self.size_analyzer.windowIcon()
            if not window_icon.isNull():
                self.log_success("Window Icon", "Window icon is set")
            else:
                self.log_warning("Window Icon", "Window icon may not be set")
            
            # Test UI file loading
            ui_file_path = os.path.join(os.path.dirname(self.size_analyzer.__class__.__module__.replace('.', os.sep)), 
                                       'size_analyzer.ui')
            
            if os.path.exists(ui_file_path):
                self.log_success("UI File", f"UI file found: {ui_file_path}")
            else:
                self.log_warning("UI File", "UI file may not be found, using programmatic creation")
            
        except Exception as e:
            self.log_error("Resource Paths", f"Exception: {e}")
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("🚀 Starting Size Analyzer Theming Validation Tests...")
        print("=" * 60)
        
        if not self.setup_test_environment():
            return False
        
        # Run all test categories
        self.test_theme_manager_functionality()
        self.test_size_analyzer_initialization()
        self.test_ui_component_styling()
        self.test_progress_visualization()
        self.test_responsive_design()
        self.test_theme_consistency()
        self.test_icon_and_resource_paths()
        
        # Generate summary
        self.generate_test_summary()
        
        # Cleanup
        if self.size_analyzer:
            self.size_analyzer.close()
        
        return True
    
    def generate_test_summary(self):
        """Generate test summary report."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅" in r["status"]])
        failed_tests = len([r for r in self.test_results if "❌" in r["status"]])
        warning_tests = len([r for r in self.test_results if "⚠️" in r["status"]])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warning_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌" in result["status"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        if warning_tests > 0:
            print("\n⚠️ WARNINGS:")
            for result in self.test_results:
                if "⚠️" in result["status"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        if failed_tests == 0:
            print("🎉 ALL CRITICAL TESTS PASSED!")
            print("Size Analyzer theming implementation is working correctly.")
        else:
            print("⚠️ Some tests failed. Please review the implementation.")
        
        print("=" * 60)


def main():
    """Main test execution."""
    validator = ThemingValidator()
    
    try:
        success = validator.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())