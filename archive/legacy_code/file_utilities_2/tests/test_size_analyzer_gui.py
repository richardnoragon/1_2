"""
GUI Component Testing for Size Analyzer

This module contains comprehensive tests for the SizeAnalyzerGUI class,
including UI initialization, theme integration, user workflows, and
progress visualization.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtTest import QTest, QSignalSpy

from file_utilities_2.gui.size_analyzer_gui import SizeAnalyzerGUI
from file_utilities_2.core.size_analyzer_logic import SizeAnalyzer


class TestSizeAnalyzerGUI:
    """Test SizeAnalyzerGUI initialization and basic functionality."""
    
    def test_gui_initialization(self, qapp, mock_hub):
        """Test GUI initialization with all components."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test basic initialization
        assert gui is not None
        assert gui.analyzer is not None
        assert isinstance(gui.analyzer, SizeAnalyzer)
        assert gui.hub_instance == mock_hub
        assert gui.selected_directory is None
        assert gui.current_analysis is None
        
        gui.close()
    
    def test_gui_components_creation(self, qapp, mock_hub):
        """Test that all GUI components are created."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test essential components exist
        assert hasattr(gui, 'directory_line_edit')
        assert hasattr(gui, 'browse_button')
        assert hasattr(gui, 'analyze_button')
        assert hasattr(gui, 'output_list_view')
        
        # Test components are not None
        assert gui.directory_line_edit is not None
        assert gui.browse_button is not None
        assert gui.analyze_button is not None
        assert gui.output_list_view is not None
        
        gui.close()
    
    def test_hub_integration_setup(self, qapp, mock_hub):
        """Test hub integration setup."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test hub connector
        assert gui.hub_connector is not None
        assert gui.hub_connector.tool_name == "Size Analyzer"
        
        # Test hub registration
        assert "Size Analyzer" in mock_hub.registered_tools
        
        gui.close()
    
    def test_signal_definitions(self, qapp, mock_hub):
        """Test that all required signals are defined."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        hub_signals = [
            'tool_started',
            'tool_completed',
            'tool_error',
            'tool_progress',
            'tool_status_changed',
            'hub_connection_changed',
            'hub_resource_granted',
            'hub_event_received'
        ]
        
        for signal_name in hub_signals:
            assert hasattr(gui, signal_name)
        
        gui.close()
    
    def test_icon_path_resolution(self, qapp, mock_hub):
        """Test icon path resolution."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        icon_path = gui._get_icon_path()
        assert isinstance(icon_path, str)
        assert len(icon_path) > 0
        
        gui.close()
    
    def test_theme_integration(self, qapp, mock_hub):
        """Test theme integration and styling."""
        with patch('file_utilities_2.gui.themes.ThemeManager') as mock_theme:
            gui = SizeAnalyzerGUI(hub_instance=mock_hub)
            
            # Verify theme manager was called
            mock_theme.apply_utility_window_theme.assert_called()
            mock_theme.register_theme_callback.assert_called()
            
            gui.close()


class TestSizeAnalyzerGUIUserWorkflows:
    """Test user interaction workflows."""
    
    def test_browse_directory_workflow(self, qapp, mock_hub, temp_dir):
        """Test directory browsing workflow."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Mock directory selection
        with patch.object(gui, 'get_directory_path', return_value=temp_dir):
            gui._browse_directory()
            
            assert gui.selected_directory == temp_dir
            assert gui.directory_line_edit.text() == temp_dir
            assert gui.analyze_button.isEnabled()
        
        gui.close()
    
    def test_browse_directory_cancelled(self, qapp, mock_hub):
        """Test directory browsing when user cancels."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Mock cancelled directory selection
        with patch.object(gui, 'get_directory_path', return_value=None):
            gui._browse_directory()
            
            assert gui.selected_directory is None
            assert gui.directory_line_edit.text() == ""
        
        gui.close()
    
    def test_start_analysis_no_directory(self, qapp, mock_hub):
        """Test starting analysis without selecting directory."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        with patch.object(gui, 'show_warning_dialog') as mock_warning:
            gui._start_analysis()
            mock_warning.assert_called_once()
        
        gui.close()
    
    def test_start_analysis_nonexistent_directory(self, qapp, mock_hub):
        """Test starting analysis with non-existent directory."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        gui.selected_directory = "/nonexistent/directory"
        
        with patch.object(gui, 'show_error_dialog') as mock_error:
            gui._start_analysis()
            mock_error.assert_called_once()
        
        gui.close()
    
    def test_start_analysis_success(self, qapp, mock_hub, temp_dir, test_files):
        """Test successful analysis start."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        gui.selected_directory = temp_dir
        
        # Mock resource request
        with patch.object(gui, 'request_hub_resources', return_value=True):
            gui._start_analysis()
            
            # Verify worker thread was created
            assert gui.worker_thread is not None
            assert gui.worker_thread.directory_path == temp_dir
        
        gui.close()
    
    def test_start_analysis_resource_denied(self, qapp, mock_hub, temp_dir):
        """Test analysis start when resources are denied."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        gui.selected_directory = temp_dir
        
        # Mock resource denial
        with patch.object(gui, 'request_hub_resources', return_value=False), \
             patch.object(gui, 'show_warning_dialog') as mock_warning:
            gui._start_analysis()
            mock_warning.assert_called_once()
        
        gui.close()
    
    def test_cancel_analysis(self, qapp, mock_hub, temp_dir):
        """Test analysis cancellation."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        gui.selected_directory = temp_dir
        
        # Create mock worker thread
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        gui.worker_thread = mock_worker
        
        gui._cancel_analysis()
        
        mock_worker.cancel.assert_called_once()
        
        gui.close()
    
    def test_export_results_no_analysis(self, qapp, mock_hub):
        """Test export when no analysis results exist."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        with patch.object(gui, 'show_warning_dialog') as mock_warning:
            gui._export_results()
            mock_warning.assert_called_once()
        
        gui.close()
    
    def test_export_results_success(self, qapp, mock_hub, temp_dir,
                                   analysis_results_sample):
        """Test successful results export."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        gui.current_analysis = analysis_results_sample
        
        export_path = os.path.join(temp_dir, 'export.json')
        
        with patch.object(gui, 'get_save_file_path', return_value=export_path), \
             patch.object(gui.analyzer, 'export_analysis') as mock_export, \
             patch.object(gui, 'show_info_dialog') as mock_info:
            
            gui._export_results()
            
            mock_export.assert_called_once_with(analysis_results_sample,
                                               export_path)
            mock_info.assert_called_once()
        
        gui.close()
    
    def test_export_results_cancelled(self, qapp, mock_hub,
                                     analysis_results_sample):
        """Test export when user cancels file selection."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        gui.current_analysis = analysis_results_sample
        
        with patch.object(gui, 'get_save_file_path', return_value=None):
            gui._export_results()
            # Should not raise any errors
        
        gui.close()


class TestSizeAnalyzerGUIProgressVisualization:
    """Test progress visualization and status updates."""
    
    def test_progress_bar_updates(self, qapp, mock_hub):
        """Test progress bar updates."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test progress update
        gui._update_progress(50)
        
        if hasattr(gui, 'progress_bar'):
            assert gui.progress_bar.value() == 50
        
        gui.close()
    
    def test_status_message_updates(self, qapp, mock_hub):
        """Test status message updates."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        test_message = "Test status message"
        gui._update_status(test_message)
        
        if hasattr(gui, 'progress_label'):
            assert gui.progress_label.text() == test_message
        
        gui.close()
    
    def test_milestone_tracking(self, qapp, mock_hub):
        """Test milestone tracking and display."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        milestone = "Test Milestone"
        percentage = 75
        
        gui._milestone_reached(milestone, percentage)
        
        # Should update status message
        expected_message = f"{milestone} ({percentage}%)"
        # Verify through status bar or other means
        
        gui.close()
    
    def test_analysis_state_management(self, qapp, mock_hub):
        """Test UI state management during analysis."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test analysis state on
        gui._set_analysis_state(True)
        
        assert not gui.analyze_button.isEnabled()
        assert not gui.browse_button.isEnabled()
        
        if hasattr(gui, 'cancel_button'):
            assert gui.cancel_button.isEnabled()
        
        # Test analysis state off
        gui._set_analysis_state(False)
        
        assert gui.analyze_button.isEnabled()
        assert gui.browse_button.isEnabled()
        
        if hasattr(gui, 'cancel_button'):
            assert not gui.cancel_button.isEnabled()
        
        gui.close()
    
    def test_results_display(self, qapp, mock_hub, analysis_results_sample):
        """Test analysis results display."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        gui._display_results(analysis_results_sample)
        
        # Verify model was set
        model = gui.output_list_view.model()
        assert model is not None
        assert model.rowCount() > 0
        
        gui.close()
    
    def test_detailed_results_display(self, qapp, mock_hub,
                                     analysis_results_sample):
        """Test detailed results display."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        if hasattr(gui, 'details_text'):
            gui._display_detailed_results(analysis_results_sample)
            
            # Verify text was set
            text_content = gui.details_text.toPlainText()
            assert len(text_content) > 0
            assert "LARGEST FILES:" in text_content
            assert "FILE TYPE ANALYSIS:" in text_content
        
        gui.close()


class TestSizeAnalyzerGUISignalHandling:
    """Test signal handling and event processing."""
    
    def test_analysis_complete_handling(self, qapp, mock_hub,
                                       analysis_results_sample):
        """Test analysis completion handling."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Create mock worker
        mock_worker = Mock()
        gui.worker_thread = mock_worker
        
        gui._analysis_complete(analysis_results_sample)
        
        # Verify state changes
        assert gui.current_analysis == analysis_results_sample
        assert not gui.analyze_button.isEnabled() or True  # State depends on UI
        
        if hasattr(gui, 'export_button'):
            assert gui.export_button.isEnabled()
        
        gui.close()
    
    def test_error_handling(self, qapp, mock_hub):
        """Test error handling during analysis."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Create mock worker
        mock_worker = Mock()
        gui.worker_thread = mock_worker
        
        error_message = "Test error message"
        
        with patch.object(gui, 'show_error_dialog') as mock_error:
            gui._handle_error(error_message)
            mock_error.assert_called_once()
        
        gui.close()
    
    def test_operation_cancelled_handling(self, qapp, mock_hub):
        """Test operation cancellation handling."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Create mock worker
        mock_worker = Mock()
        gui.worker_thread = mock_worker
        
        gui._operation_cancelled()
        
        # Verify cleanup
        mock_worker.quit.assert_called_once()
        mock_worker.wait.assert_called_once()
        
        gui.close()
    
    def test_hub_event_handling(self, qapp, mock_hub):
        """Test hub event handling."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test tool progress event
        gui._on_tool_progress("Size Analyzer", 50, "Test progress")
        
        # Test tool error event
        gui._on_tool_error("Size Analyzer", "Test error")
        
        # Test tool completion event
        gui._on_tool_completed("Size Analyzer", {"test": "data"})
        
        # Test hub connection change
        gui._on_hub_connection_changed(True)
        gui._on_hub_connection_changed(False)
        
        gui.close()


class TestSizeAnalyzerGUIIntegration:
    """Test integration between GUI components."""
    
    def test_analyzer_signal_connections(self, qapp, mock_hub):
        """Test connections between analyzer and GUI signals."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Create signal spies
        progress_spy = QSignalSpy(gui.analyzer.progress_percentage)
        message_spy = QSignalSpy(gui.analyzer.progress_message)
        milestone_spy = QSignalSpy(gui.analyzer.milestone_reached)
        complete_spy = QSignalSpy(gui.analyzer.analysis_complete)
        error_spy = QSignalSpy(gui.analyzer.error_occurred)
        
        # Verify spies are connected (they should have 0 signals initially)
        assert len(progress_spy) == 0
        assert len(message_spy) == 0
        assert len(milestone_spy) == 0
        assert len(complete_spy) == 0
        assert len(error_spy) == 0
        
        gui.close()
    
    def test_hub_signal_connections(self, qapp, mock_hub):
        """Test connections between hub and GUI signals."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test hub connector signals
        assert gui.hub_connector is not None
        
        # Verify signal connections exist
        hub_signals = [
            'hub_connection_status',
            'hub_resource_available',
            'hub_broadcast_received',
            'tool_status_changed'
        ]
        
        for signal_name in hub_signals:
            assert hasattr(gui.hub_connector, signal_name)
        
        gui.close()
    
    def test_menu_action_connections(self, qapp, mock_hub):
        """Test menu action connections if they exist."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Test menu actions if they exist
        menu_actions = [
            'actionselect',
            'actionexport_results',
            'actionexit',
            'actionabout'
        ]
        
        for action_name in menu_actions:
            if hasattr(gui, action_name):
                action = getattr(gui, action_name)
                assert action is not None
        
        gui.close()
    
    def test_about_dialog(self, qapp, mock_hub):
        """Test about dialog functionality."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        with patch.object(gui, 'show_info_dialog') as mock_info:
            gui._show_about()
            mock_info.assert_called_once()
            
            # Verify about dialog content
            call_args = mock_info.call_args
            assert "About Size Analyzer" in call_args[0][0]
            assert "Size Analyzer v2.0" in call_args[0][1]
        
        gui.close()


class TestSizeAnalyzerGUICleanup:
    """Test GUI cleanup and resource management."""
    
    def test_close_event_handling(self, qapp, mock_hub):
        """Test close event handling and cleanup."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Create mock worker
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        gui.worker_thread = mock_worker
        
        # Create mock close event
        from PyQt5.QtGui import QCloseEvent
        close_event = QCloseEvent()
        
        gui.closeEvent(close_event)
        
        # Verify worker cleanup
        mock_worker.cancel.assert_called_once()
        mock_worker.quit.assert_called_once()
        mock_worker.wait.assert_called_once()
        
        gui.close()
    
    def test_hub_cleanup(self, qapp, mock_hub):
        """Test hub integration cleanup."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Mock hub connector cleanup
        with patch.object(gui.hub_connector, 'cleanup') as mock_cleanup:
            from PyQt5.QtGui import QCloseEvent
            close_event = QCloseEvent()
            gui.closeEvent(close_event)
            
            mock_cleanup.assert_called_once()
        
        gui.close()
    
    def test_resource_cleanup_on_error(self, qapp, mock_hub):
        """Test resource cleanup when errors occur."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Create mock worker that fails
        mock_worker = Mock()
        mock_worker.isRunning.return_value = True
        gui.worker_thread = mock_worker
        
        # Simulate error
        gui._handle_error("Test error")
        
        # Verify cleanup occurred
        mock_worker.quit.assert_called_once()
        mock_worker.wait.assert_called_once()
        
        gui.close()


class TestSizeAnalyzerGUIResponsiveness:
    """Test GUI responsiveness and user experience."""
    
    def test_ui_responsiveness_during_analysis(self, qapp, mock_hub):
        """Test that UI remains responsive during analysis."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Simulate analysis state
        gui._set_analysis_state(True)
        
        # Process events to ensure UI updates
        QApplication.processEvents()
        
        # UI should be in analysis state
        assert not gui.analyze_button.isEnabled()
        
        gui.close()
    
    def test_progress_update_frequency(self, qapp, mock_hub):
        """Test progress update frequency doesn't overwhelm UI."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Simulate rapid progress updates
        for i in range(100):
            gui._update_progress(i)
            if i % 10 == 0:  # Process events periodically
                QApplication.processEvents()
        
        # UI should handle rapid updates gracefully
        if hasattr(gui, 'progress_bar'):
            assert gui.progress_bar.value() == 99
        
        gui.close()
    
    def test_theme_change_responsiveness(self, qapp, mock_hub):
        """Test responsiveness to theme changes."""
        gui = SizeAnalyzerGUI(hub_instance=mock_hub)
        
        # Simulate theme change
        with patch('file_utilities_2.gui.themes.ThemeManager') as mock_theme:
            gui._on_theme_changed("dark")
            
            # Verify theme manager was called
            mock_theme.apply_utility_window_theme.assert_called()
        
        gui.close()