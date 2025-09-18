#!/usr/bin/env python3
"""
Comprehensive test suite for Multi-Pane Explorer
Test file: test_multi_pane_explorer_repaired.py
Created: September 18, 2025

This test suite validates all functionality of the repaired multi_pane_explorer.py
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the classes to test
try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    from src.file_explorer.multi_pane_explorer import (ERROR_MESSAGES,
                                                       KEYBOARD_SHORTCUTS,
                                                       LAYOUT_ERROR_MESSAGES,
                                                       TOOL_NAMES,
                                                       WIDGET_DELETED_ERROR,
                                                       MultiPaneFileExplorer)
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    MultiPaneFileExplorer = None


class TestConstants:
    """Test the constants defined in the repaired file."""
    
    def test_tool_names_constants(self):
        """Test that tool name constants are properly defined."""
        assert 'FILE_FINDER' in TOOL_NAMES
        assert 'SIZE_ANALYZER' in TOOL_NAMES
        assert 'DUPLICATE_FINDER' in TOOL_NAMES
        assert 'ENCRYPT_DECRYPT' in TOOL_NAMES
        assert 'SECURE_DELETE' in TOOL_NAMES
        assert 'DISK_USAGE' in TOOL_NAMES
        
        # Test actual values
        assert TOOL_NAMES['FILE_FINDER'] == "File Finder"
        assert TOOL_NAMES['SIZE_ANALYZER'] == "Size Analyzer"
        assert TOOL_NAMES['DUPLICATE_FINDER'] == "Duplicate Finder"
    
    def test_error_messages_constants(self):
        """Test that error message constants are properly defined."""
        assert 'FILE_OPEN_ERROR' in ERROR_MESSAGES
        assert 'COPY_ERROR' in ERROR_MESSAGES
        assert 'MOVE_ERROR' in ERROR_MESSAGES
        assert 'COMPARE_ERROR' in ERROR_MESSAGES
        assert 'NAVIGATION_ERROR' in ERROR_MESSAGES
        
        # Test actual values
        assert ERROR_MESSAGES['FILE_OPEN_ERROR'] == "File Open Error"
        assert ERROR_MESSAGES['COPY_ERROR'] == "Copy Error"
        assert ERROR_MESSAGES['MOVE_ERROR'] == "Move Error"
    
    def test_keyboard_shortcuts_constants(self):
        """Test that keyboard shortcut constants are properly defined."""
        assert 'SEARCH' in KEYBOARD_SHORTCUTS
        assert 'REFRESH' in KEYBOARD_SHORTCUTS
        assert 'HELP' in KEYBOARD_SHORTCUTS
        
        assert KEYBOARD_SHORTCUTS['SEARCH'] == "Ctrl+F"
        assert KEYBOARD_SHORTCUTS['REFRESH'] == "F5"
        assert KEYBOARD_SHORTCUTS['HELP'] == "F1"
    
    def test_widget_constants(self):
        """Test widget lifecycle constants."""
        assert WIDGET_DELETED_ERROR == "wrapped C/C++ object"
        assert 'NO_SPLITTER' in LAYOUT_ERROR_MESSAGES
        assert LAYOUT_ERROR_MESSAGES['NO_SPLITTER'] == "Cannot create layout: pane_splitter is None"


@pytest.mark.skipif(not PYQT_AVAILABLE, reason="PyQt5 not available")
class TestMultiPaneFileExplorer:
    """Test suite for MultiPaneFileExplorer class."""
    
    @pytest.fixture(scope="class")
    def app(self):
        """Create QApplication for testing."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        # Don't quit here as it might be used by other tests
    
    @pytest.fixture
    def explorer(self, app):
        """Create MultiPaneFileExplorer instance for testing."""
        with patch.multiple(
            'src.file_explorer.multi_pane_explorer',
            get_log_manager=MagicMock(),
            get_config_manager=MagicMock(),
            get_database_manager=MagicMock()
        ):
            explorer = MultiPaneFileExplorer()
            yield explorer
            explorer.close()
    
    def test_initialization(self, explorer):
        """Test that MultiPaneFileExplorer initializes correctly."""
        assert explorer is not None
        assert hasattr(explorer, 'panes')
        assert hasattr(explorer, 'active_pane_index')
        assert hasattr(explorer, 'pane_count')
        assert hasattr(explorer, 'layout_mode')
        
        # Test default values
        assert explorer.pane_count == 2
        assert explorer.layout_mode == 'horizontal'
        assert explorer.active_pane_index == 0
    
    def test_pane_count_validation(self, explorer):
        """Test pane count validation."""
        # Valid pane counts
        assert explorer.set_pane_count(1) is None  # Should not raise
        assert explorer.set_pane_count(2) is None
        assert explorer.set_pane_count(3) is None
        assert explorer.set_pane_count(4) is None
        
        # Invalid pane counts should be ignored
        original_count = explorer.pane_count
        explorer.set_pane_count(0)
        assert explorer.pane_count == original_count
        
        explorer.set_pane_count(5)
        assert explorer.pane_count == original_count
    
    def test_layout_mode_validation(self, explorer):
        """Test layout mode validation."""
        # Test valid layout modes for different pane counts
        explorer.set_pane_count(2)
        available_layouts = explorer.available_layouts[2]
        
        for layout in available_layouts:
            explorer.layout_mode = layout
            explorer._validate_and_update_layout()
            assert explorer.layout_mode in available_layouts
    
    def test_tool_launch_methods(self, explorer):
        """Test that tool launch methods use constants correctly."""
        with patch.object(explorer, '_launch_tool') as mock_launch:
            # Test file finder
            explorer.launch_file_finder()
            mock_launch.assert_called_with(
                TOOL_NAMES['FILE_FINDER'],
                "src.tools.file_management.file_finder",
                "FileFinderGUI"
            )
            
            # Test size analyzer
            explorer.launch_size_analyzer()
            mock_launch.assert_called_with(
                TOOL_NAMES['SIZE_ANALYZER'],
                "src.tools.analysis.size_analyzer",
                "SizeAnalyzerGUI"
            )
            
            # Test duplicate finder
            explorer.launch_duplicate_finder()
            mock_launch.assert_called_with(
                TOOL_NAMES['DUPLICATE_FINDER'],
                "src.tools.analysis.find_duplicate_files",
                "DuplicateFinderApp"
            )
    
    def test_viewport_detection(self, explorer):
        """Test responsive viewport detection."""
        # Test desktop viewport
        explorer.screen_size = (1920, 1080)
        explorer._detect_viewport()
        assert not explorer.is_mobile_viewport
        
        # Test mobile viewport
        explorer.screen_size = (800, 600)
        explorer._detect_viewport()
        assert explorer.is_mobile_viewport
    
    def test_configuration_loading(self, explorer):
        """Test configuration loading with proper exception handling."""
        # Mock config manager
        mock_config = MagicMock()
        mock_config.get_section.return_value = {
            'pane_count': 3,
            'layout_mode': 'vertical'
        }
        explorer.config_manager = mock_config
        
        explorer.load_configuration()
        
        # Should load configuration successfully
        mock_config.get_section.assert_called_with('file_explorer')
    
    def test_exception_handling_in_config_loading(self, explorer):
        """Test that configuration loading handles exceptions properly."""
        # Mock config manager that raises exception
        mock_config = MagicMock()
        mock_config.get_section.side_effect = AttributeError("Test error")
        explorer.config_manager = mock_config
        
        # Should not raise exception, should handle gracefully
        try:
            explorer.load_configuration()
        except (AttributeError, KeyError, TypeError):
            pytest.fail("Exception not handled properly in load_configuration")


class TestFallbackFunctions:
    """Test the fallback functions defined in the imports section."""
    
    def test_fallback_functions_exist(self):
        """Test that fallback functions are properly defined."""
        from src.file_explorer.multi_pane_explorer import (
            is_widget_valid, register_widget, safe_destroy_widget,
            safe_widget_operation)

        # Test that functions exist and are callable
        assert callable(register_widget)
        assert callable(safe_destroy_widget)
        assert callable(is_widget_valid)
        assert callable(safe_widget_operation)
        
        # Test return values
        assert register_widget("test") == ""
        assert safe_destroy_widget("test") is True
        assert is_widget_valid("test") is True
        assert safe_widget_operation("test") is True


class TestCodeQuality:
    """Test code quality improvements."""
    
    def test_no_bare_except_clauses(self):
        """Test that there are no bare except clauses in the code."""
        # Read the source file
        source_path = Path(__file__).parent.parent.parent / "src" / "file_explorer" / "multi_pane_explorer.py"
        
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for bare except clauses
        lines = content.split('\n')
        bare_except_lines = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped == "except:" or stripped.startswith("except:"):
                bare_except_lines.append(i)
        
        assert len(bare_except_lines) == 0, f"Found bare except clauses at lines: {bare_except_lines}"
    
    def test_no_lambda_assignments(self):
        """Test that there are no lambda assignments in the code."""
        source_path = Path(__file__).parent.parent.parent / "src" / "file_explorer" / "multi_pane_explorer.py"
        
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for lambda assignments
        lines = content.split('\n')
        lambda_assignments = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if "= lambda" in stripped:
                lambda_assignments.append(i)
        
        assert len(lambda_assignments) == 0, f"Found lambda assignments at lines: {lambda_assignments}"
    
    def test_line_length_compliance(self):
        """Test that most lines comply with 79 character limit."""
        source_path = Path(__file__).parent.parent.parent / "src" / "file_explorer" / "multi_pane_explorer.py"
        
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        long_lines = []
        for i, line in enumerate(lines, 1):
            # Exclude comment lines and strings that might legitimately be long
            if len(line.rstrip()) > 79 and not line.strip().startswith('#'):
                long_lines.append((i, len(line.rstrip())))
        
        # Allow some long lines but they should be minimal
        assert len(long_lines) < 50, f"Too many long lines found: {len(long_lines)}"


def test_import_success():
    """Test that the module can be imported without errors."""
    try:
        import src.file_explorer.multi_pane_explorer
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import multi_pane_explorer: {e}")
    except SyntaxError as e:
        pytest.fail(f"Syntax error in multi_pane_explorer: {e}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])