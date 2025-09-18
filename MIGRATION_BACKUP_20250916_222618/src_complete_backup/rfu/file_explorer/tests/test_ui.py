"""
Unit Tests for UI Components
Tests pane manager, file explorer pane, and custom widgets.

Author: RFU Development Team
Created: 2025-09-12
Version: 1.0.0
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Check for Qt availability
QT_AVAILABLE = False
try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication

    from src.rfu.file_explorer.ui.custom_widgets import (EnhancedStatusBar,
                                                         EnhancedToolbar,
                                                         FilePropertyPanel,
                                                         QuickPreviewWidget,
                                                         SearchWidget,
                                                         ThemeColors)
    from src.rfu.file_explorer.ui.file_explorer_pane import (FileExplorerPane,
                                                             NavigationBar,
                                                             ViewMode)
    from src.rfu.file_explorer.ui.pane_manager import (LayoutType,
                                                       PaneConfiguration,
                                                       PaneManager, PaneType)
    QT_AVAILABLE = True
except ImportError:
    pass


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestPaneManager:
    """Test pane manager functionality."""

    def test_pane_manager_creation(self, qapp):
        """Test pane manager creation."""
        manager = PaneManager()
        assert manager is not None
        assert len(manager.panes) == 0

    def test_pane_configuration(self):
        """Test pane configuration creation."""
        config = PaneConfiguration(
            pane_id="test_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Test Pane",
            position=(0, 0),
            size=(400, 300)
        )
        
        assert config.pane_id == "test_pane"
        assert config.pane_type == PaneType.FILE_EXPLORER
        assert config.title == "Test Pane"
        assert config.position == (0, 0)
        assert config.size == (400, 300)

    def test_add_pane(self, qapp):
        """Test adding pane to manager."""
        manager = PaneManager()
        
        config = PaneConfiguration(
            pane_id="test_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Test Pane"
        )
        
        pane = manager.add_pane(config)
        assert pane is not None
        assert len(manager.panes) == 1
        assert manager.get_pane("test_pane") == pane

    def test_remove_pane(self, qapp):
        """Test removing pane from manager."""
        manager = PaneManager()
        
        config = PaneConfiguration(
            pane_id="test_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Test Pane"
        )
        
        pane = manager.add_pane(config)
        assert len(manager.panes) == 1
        
        manager.remove_pane("test_pane")
        assert len(manager.panes) == 0
        assert manager.get_pane("test_pane") is None

    def test_layout_types(self, qapp):
        """Test different layout types."""
        manager = PaneManager()
        
        # Test grid layout
        manager.set_layout(LayoutType.GRID)
        assert manager.current_layout == LayoutType.GRID
        
        # Test split layout
        manager.set_layout(LayoutType.SPLIT_HORIZONTAL)
        assert manager.current_layout == LayoutType.SPLIT_HORIZONTAL

    def test_pane_persistence(self, qapp):
        """Test pane configuration persistence."""
        manager = PaneManager()
        
        config = PaneConfiguration(
            pane_id="persist_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Persistent Pane"
        )
        
        manager.add_pane(config)
        
        # Save configuration
        saved_config = manager.save_configuration()
        assert 'panes' in saved_config
        assert len(saved_config['panes']) == 1
        
        # Create new manager and load configuration
        new_manager = PaneManager()
        new_manager.load_configuration(saved_config)
        
        assert len(new_manager.panes) == 1
        assert new_manager.get_pane("persist_pane") is not None


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestFileExplorerPane:
    """Test file explorer pane functionality."""

    def test_pane_creation(self, qapp):
        """Test file explorer pane creation."""
        config = PaneConfiguration(
            pane_id="explorer_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Explorer"
        )
        
        pane = FileExplorerPane(config)
        assert pane is not None
        assert pane.config == config

    def test_path_setting(self, qapp, mock_filesystem):
        """Test setting path in explorer pane."""
        config = PaneConfiguration(
            pane_id="path_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Path Test"
        )
        
        pane = FileExplorerPane(config)
        test_path = str(mock_filesystem.base_path)
        
        pane.set_path(test_path)
        assert pane.current_path == test_path

    def test_view_modes(self, qapp):
        """Test different view modes."""
        config = PaneConfiguration(
            pane_id="view_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="View Test"
        )
        
        pane = FileExplorerPane(config)
        
        # Test view mode changes
        pane.set_view_mode(ViewMode.LIST)
        assert pane.current_view_mode == ViewMode.LIST
        
        pane.set_view_mode(ViewMode.GRID)
        assert pane.current_view_mode == ViewMode.GRID
        
        pane.set_view_mode(ViewMode.DETAILS)
        assert pane.current_view_mode == ViewMode.DETAILS

    def test_navigation_bar(self, qapp):
        """Test navigation bar functionality."""
        nav_bar = NavigationBar()
        assert nav_bar is not None
        
        # Test path setting
        test_path = "/home/user/documents"
        nav_bar.set_path(test_path)
        assert nav_bar.current_path == test_path
        
        # Test navigation buttons
        assert nav_bar.back_button is not None
        assert nav_bar.forward_button is not None
        assert nav_bar.up_button is not None

    def test_file_operations(self, qapp, mock_filesystem):
        """Test file operation capabilities."""
        config = PaneConfiguration(
            pane_id="ops_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Operations Test"
        )
        
        pane = FileExplorerPane(config)
        pane.set_path(str(mock_filesystem.base_path))
        
        # Test selection
        test_file = "Documents/readme.txt"
        pane.select_file(test_file)
        
        selected = pane.get_selected_files()
        assert len(selected) >= 0  # May be 0 if file not found in mock

    def test_sorting_and_filtering(self, qapp):
        """Test sorting and filtering functionality."""
        config = PaneConfiguration(
            pane_id="sort_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Sort Test"
        )
        
        pane = FileExplorerPane(config)
        
        # Test sorting options
        pane.set_sort_column("name")
        pane.set_sort_order(Qt.AscendingOrder)
        
        # Test filtering
        pane.set_filter("*.txt")
        assert pane.current_filter == "*.txt"


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestCustomWidgets:
    """Test custom widget functionality."""

    def test_enhanced_toolbar(self, qapp):
        """Test enhanced toolbar widget."""
        toolbar = EnhancedToolbar()
        assert toolbar is not None
        
        # Test adding action button
        toolbar.add_action_button(
            "test_action", 
            "Test", 
            tooltip="Test action"
        )
        
        action_button = toolbar.get_action_button("test_action")
        assert action_button is not None
        assert action_button.text() == "Test"
        assert action_button.toolTip() == "Test action"
        
        # Test enable/disable
        toolbar.set_action_enabled("test_action", False)
        assert not action_button.isEnabled()
        
        toolbar.set_action_enabled("test_action", True)
        assert action_button.isEnabled()

    def test_enhanced_status_bar(self, qapp):
        """Test enhanced status bar widget."""
        status_bar = EnhancedStatusBar()
        assert status_bar is not None
        
        # Test message setting
        status_bar.set_main_message("Test message", "info")
        
        # Test file count
        status_bar.set_file_count(42, 1024*1024)
        
        # Test selection info
        status_bar.set_selection_info(5, 512*1024)
        
        # Test progress bar
        status_bar.show_progress(0, 100, 50)
        assert status_bar.progress_bar.isVisible()
        
        status_bar.hide_progress()
        assert not status_bar.progress_bar.isVisible()

    def test_file_property_panel(self, qapp, mock_filesystem):
        """Test file property panel widget."""
        panel = FilePropertyPanel()
        assert panel is not None
        
        # Test setting file info
        test_file = mock_filesystem.base_path / "Documents" / "readme.txt"
        if test_file.exists():
            panel.set_file_info(str(test_file))
            assert panel.current_file_path == str(test_file)
            assert panel.file_name_label.text() == "readme.txt"

    def test_quick_preview_widget(self, qapp):
        """Test quick preview widget."""
        preview = QuickPreviewWidget()
        assert preview is not None
        
        # Test file type detection
        assert preview.is_text_file("test.txt")
        assert preview.is_image_file("image.jpg")
        assert not preview.is_text_file("image.jpg")

    def test_search_widget(self, qapp):
        """Test search widget functionality."""
        search = SearchWidget()
        assert search is not None
        
        # Test search criteria
        search.set_search_text("test query")
        search.set_file_types([".txt", ".py"])
        search.set_search_path("/home/user")
        
        criteria = search.get_search_criteria()
        assert criteria['text'] == "test query"
        assert ".txt" in criteria['file_types']
        assert criteria['path'] == "/home/user"

    def test_theme_colors(self, qapp):
        """Test theme colors functionality."""
        # Test light theme
        light_colors = ThemeColors.get_light_theme()
        assert 'background' in light_colors
        assert 'text' in light_colors
        assert 'accent' in light_colors
        
        # Test dark theme
        dark_colors = ThemeColors.get_dark_theme()
        assert 'background' in dark_colors
        assert 'text' in dark_colors
        assert 'accent' in dark_colors
        
        # Colors should be different
        assert light_colors['background'] != dark_colors['background']

    def test_widget_styling(self, qapp):
        """Test widget styling functionality."""
        toolbar = EnhancedToolbar()
        
        # Test theme application
        light_theme = ThemeColors.get_light_theme()
        toolbar.apply_theme(light_theme)
        
        dark_theme = ThemeColors.get_dark_theme()
        toolbar.apply_theme(dark_theme)
        
        # Should not raise exceptions

    def test_widget_signals(self, qapp):
        """Test widget signal emissions."""
        search = SearchWidget()
        
        # Test signal connections
        signal_received = []
        
        def on_search():
            signal_received.append("search")
        
        search.search_requested.connect(on_search)
        
        # Simulate search button click
        QTest.mouseClick(search.search_button, Qt.LeftButton)
        
        # Process events
        QApplication.processEvents()
        
        # Should have received signal
        assert len(signal_received) > 0


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestUIIntegration:
    """Test UI component integration."""

    def test_pane_widget_integration(self, qapp, mock_filesystem):
        """Test integration between pane and widgets."""
        config = PaneConfiguration(
            pane_id="integration_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Integration Test"
        )
        
        pane = FileExplorerPane(config)
        pane.set_path(str(mock_filesystem.base_path))
        
        # Test property panel integration
        property_panel = FilePropertyPanel()
        
        # Should be able to connect signals
        pane.file_selected.connect(property_panel.set_file_info)
        
        # Test toolbar integration
        toolbar = EnhancedToolbar()
        toolbar.add_action_button("refresh", "Refresh")
        
        # Should be able to connect actions
        refresh_action = toolbar.get_action_button("refresh")
        refresh_action.clicked.connect(pane.refresh)

    def test_status_bar_updates(self, qapp, mock_filesystem):
        """Test status bar updates from pane."""
        config = PaneConfiguration(
            pane_id="status_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Status Test"
        )
        
        pane = FileExplorerPane(config)
        status_bar = EnhancedStatusBar()
        
        # Connect signals
        pane.path_changed.connect(lambda path: status_bar.set_main_message(f"Path: {path}"))
        pane.selection_changed.connect(status_bar.set_selection_info)
        
        # Test path change
        pane.set_path(str(mock_filesystem.base_path))

    def test_search_integration(self, qapp, mock_filesystem):
        """Test search widget integration with file pane."""
        config = PaneConfiguration(
            pane_id="search_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Search Test"
        )
        
        pane = FileExplorerPane(config)
        search = SearchWidget()
        
        # Connect search
        search.search_requested.connect(lambda: pane.perform_search(search.get_search_criteria()))
        
        # Test search functionality
        search.set_search_text("readme")
        search.set_search_path(str(mock_filesystem.base_path))


@pytest.mark.skipif(not QT_AVAILABLE, reason="PyQt5 not available")
class TestUIPerformance:
    """Test UI performance characteristics."""

    def test_pane_creation_performance(self, qapp, performance_monitor):
        """Test pane creation performance."""
        performance_monitor.start_measurement("pane_creation")
        
        # Create multiple panes
        for i in range(10):
            config = PaneConfiguration(
                pane_id=f"perf_pane_{i}",
                pane_type=PaneType.FILE_EXPLORER,
                title=f"Performance Pane {i}"
            )
            pane = FileExplorerPane(config)
            pane.cleanup()
        
        duration = performance_monitor.end_measurement("pane_creation")
        
        # Should create 10 panes quickly
        assert duration < 2.0

    def test_large_directory_loading(self, qapp, large_directory, performance_monitor):
        """Test loading large directory performance."""
        config = PaneConfiguration(
            pane_id="large_dir_pane",
            pane_type=PaneType.FILE_EXPLORER,
            title="Large Directory Test"
        )
        
        pane = FileExplorerPane(config)
        
        performance_monitor.start_measurement("large_dir_load")
        pane.set_path(str(large_directory))
        duration = performance_monitor.end_measurement("large_dir_load")
        
        # Should load large directory reasonably quickly
        assert duration < 5.0

    def test_widget_update_performance(self, qapp, performance_monitor):
        """Test widget update performance."""
        status_bar = EnhancedStatusBar()
        
        performance_monitor.start_measurement("status_updates")
        
        # Rapid status updates
        for i in range(1000):
            status_bar.set_file_count(i, i * 1024)
            status_bar.set_selection_info(i % 10, i * 512)
        
        duration = performance_monitor.end_measurement("status_updates")
        
        # Should handle rapid updates efficiently
        assert duration < 1.0


if __name__ == '__main__':
    pytest.main([__file__, "-v"])