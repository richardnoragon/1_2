"""
File Splitter Hub Integration

This module provides comprehensive hub connectivity and communication
for the file splitter tool, enabling centralized monitoring, progress
reporting, and resource management.
"""

from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from file_utilities_2.integration.hub_connector import HubIntegratedTool
from file_utilities_2.core.file_splitter_logic import FileSplitterLogic
from file_utilities_2.core.file_splitter_config import FileSplitterConfig
from file_utilities_2.core.file_splitter_logging import get_file_splitter_logger


class FileSplitterHubConnector(HubIntegratedTool):
    """
    Hub integration for file splitter tool.
    
    Provides comprehensive hub connectivity including progress reporting,
    error tracking, resource monitoring, and lifecycle management.
    """
    
    # Additional signals for file splitter specific events
    split_operation_started = pyqtSignal(str, dict)  # file_path, details
    split_operation_completed = pyqtSignal(str, dict)  # file_path, results
    join_operation_started = pyqtSignal(str, dict)  # chunk_path, details
    join_operation_completed = pyqtSignal(str, dict)  # output_path, results
    
    def __init__(self):
        """Initialize file splitter hub connector."""
        super().__init__("file_splitter")
        
        # Initialize components
        self.config = FileSplitterConfig()
        self.logger = get_file_splitter_logger()
        self.splitter_logic = FileSplitterLogic(self.config, self.logger)
        
        # Connect signals
        self._connect_signals()
        
        # Register with hub
        self.register_with_hub()
        
        self.logger.info("FileSplitterHubConnector initialized successfully")
    
    def _connect_signals(self):
        """Connect splitter signals to hub reporting."""
        # Connect core logic signals
        self.splitter_logic.progress_updated.connect(self._report_progress)
        self.splitter_logic.operation_complete.connect(self._report_completion)
        self.splitter_logic.error_occurred.connect(self._report_error)
        self.splitter_logic.finished.connect(self._report_finished)
        
        # Set hub connector in logic
        self.splitter_logic.set_hub_connector(self.hub_connector)
    
    def _report_progress(self, current: int, total: int, message: str):
        """
        Report progress to hub.
        
        Args:
            current: Current progress value
            total: Total progress value
            message: Progress message
        """
        percentage = int((current / total) * 100) if total > 0 else 0
        self.report_tool_progress(percentage, message)
        
        # Report detailed progress
        self.hub_connector.report_status_to_hub(
            "processing",
            {
                'current': current,
                'total': total,
                'percentage': percentage,
                'message': message,
                'tool': 'file_splitter'
            }
        )
    
    def _report_completion(self, message: str):
        """
        Report successful completion to hub.
        
        Args:
            message: Completion message
        """
        self.report_tool_completed({"completion_message": message})
        
        # Determine operation type and emit specific signal
        if "split" in message.lower():
            self.split_operation_completed.emit("", {"message": message})
        elif "join" in message.lower():
            self.join_operation_completed.emit("", {"message": message})
    
    def _report_error(self, error_message: str):
        """
        Report error to hub.
        
        Args:
            error_message: Error message
        """
        self.report_tool_error(error_message)
        
        # Log error details
        self.logger.error(f"File splitter error reported to hub: {error_message}")
    
    def _report_finished(self):
        """Report operation finished to hub."""
        self.hub_connector.report_status_to_hub(
            "idle",
            {
                'message': 'Operation finished',
                'tool': 'file_splitter'
            }
        )
    
    def start_split_operation(self, 
                            input_filepath: str, 
                            output_dir: str, 
                            split_mode: str,
                            value: float, 
                            unit_multiplier: int = 1) -> bool:
        """
        Start file split operation with hub integration.
        
        Args:
            input_filepath: Path to file to split
            output_dir: Output directory for chunks
            split_mode: Split mode ('size' or 'parts')
            value: Split value
            unit_multiplier: Unit multiplier for size mode
            
        Returns:
            True if operation started successfully
        """
        try:
            # Report operation start
            operation_details = {
                'input_file': input_filepath,
                'output_dir': output_dir,
                'split_mode': split_mode,
                'value': value,
                'unit_multiplier': unit_multiplier
            }
            
            self.report_tool_started(operation_details)
            self.split_operation_started.emit(input_filepath, operation_details)
            
            # Start the operation
            self.splitter_logic.split_file(
                input_filepath, output_dir, split_mode, value, unit_multiplier
            )
            
            self.logger.info(f"Split operation started via hub: {input_filepath}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to start split operation: {e}"
            self._report_error(error_msg)
            return False
    
    def start_join_operation(self, 
                           first_chunk_path: str, 
                           output_filepath: str) -> bool:
        """
        Start file join operation with hub integration.
        
        Args:
            first_chunk_path: Path to first chunk file
            output_filepath: Output file path
            
        Returns:
            True if operation started successfully
        """
        try:
            # Report operation start
            operation_details = {
                'first_chunk': first_chunk_path,
                'output_file': output_filepath
            }
            
            self.report_tool_started(operation_details)
            self.join_operation_started.emit(first_chunk_path, operation_details)
            
            # Start the operation
            self.splitter_logic.join_files(first_chunk_path, output_filepath)
            
            self.logger.info(f"Join operation started via hub: {first_chunk_path}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to start join operation: {e}"
            self._report_error(error_msg)
            return False
    
    def stop_operation(self) -> bool:
        """
        Stop current operation.
        
        Returns:
            True if stop command sent successfully
        """
        try:
            self.splitter_logic.stop()
            
            self.hub_connector.report_status_to_hub(
                "stopped",
                {
                    'message': 'Operation stopped by user',
                    'tool': 'file_splitter'
                }
            )
            
            self.logger.info("Operation stop requested via hub")
            return True
            
        except Exception as e:
            error_msg = f"Failed to stop operation: {e}"
            self._report_error(error_msg)
            return False
    
    def get_operation_status(self) -> Dict[str, Any]:
        """
        Get current operation status.
        
        Returns:
            Dictionary with current status information
        """
        return {
            'tool_name': self.tool_name,
            'is_running': self.splitter_logic._is_running,
            'operation_stats': self.splitter_logic.operation_stats.copy(),
            'config_summary': self.config.get_config_summary(),
            'hub_connected': self.hub_connector.is_connected if self.hub_connector else False
        }
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """
        Update configuration via hub.
        
        Args:
            config_updates: Configuration updates
            
        Returns:
            True if configuration updated successfully
        """
        try:
            self.config.update(config_updates, save=True)
            
            self.hub_connector.report_status_to_hub(
                "config_updated",
                {
                    'message': 'Configuration updated',
                    'updates': config_updates,
                    'tool': 'file_splitter'
                }
            )
            
            self.logger.info(f"Configuration updated via hub: {config_updates}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to update configuration: {e}"
            self._report_error(error_msg)
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for hub monitoring.
        
        Returns:
            Dictionary with performance metrics
        """
        stats = self.splitter_logic.operation_stats
        
        return {
            'tool_name': self.tool_name,
            'bytes_processed': stats.get('bytes_processed', 0),
            'chunks_processed': stats.get('chunks_processed', 0),
            'errors_count': stats.get('errors_count', 0),
            'operation_type': stats.get('operation_type'),
            'start_time': stats.get('start_time'),
            'end_time': stats.get('end_time'),
            'input_file_size': stats.get('input_file_size', 0),
            'output_files_count': stats.get('output_files_count', 0)
        }
    
    def handle_hub_command(self, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle commands from hub.
        
        Args:
            command: Command to execute
            parameters: Command parameters
            
        Returns:
            Command execution result
        """
        try:
            if command == "split_file":
                success = self.start_split_operation(
                    parameters.get('input_filepath'),
                    parameters.get('output_dir'),
                    parameters.get('split_mode'),
                    parameters.get('value'),
                    parameters.get('unit_multiplier', 1)
                )
                return {'success': success, 'command': command}
                
            elif command == "join_files":
                success = self.start_join_operation(
                    parameters.get('first_chunk_path'),
                    parameters.get('output_filepath')
                )
                return {'success': success, 'command': command}
                
            elif command == "stop_operation":
                success = self.stop_operation()
                return {'success': success, 'command': command}
                
            elif command == "get_status":
                status = self.get_operation_status()
                return {'success': True, 'command': command, 'status': status}
                
            elif command == "get_metrics":
                metrics = self.get_performance_metrics()
                return {'success': True, 'command': command, 'metrics': metrics}
                
            elif command == "update_config":
                success = self.update_configuration(parameters.get('config', {}))
                return {'success': success, 'command': command}
                
            else:
                return {
                    'success': False, 
                    'command': command, 
                    'error': f'Unknown command: {command}'
                }
                
        except Exception as e:
            self.logger.error(f"Error handling hub command '{command}': {e}")
            return {
                'success': False, 
                'command': command, 
                'error': str(e)
            }
    
    def cleanup_hub_integration(self):
        """Cleanup hub integration resources."""
        try:
            # Stop any running operations
            if self.splitter_logic._is_running:
                self.splitter_logic.stop()
            
            # Cleanup parent hub integration
            super().cleanup_hub_integration()
            
            self.logger.info("FileSplitterHubConnector cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during hub integration cleanup: {e}")


# Factory function for creating hub connector
def create_file_splitter_hub_connector() -> FileSplitterHubConnector:
    """
    Factory function to create file splitter hub connector.
    
    Returns:
        Configured FileSplitterHubConnector instance
    """
    return FileSplitterHubConnector()


# Hub registration function
def register_file_splitter_with_hub(hub_instance) -> FileSplitterHubConnector:
    """
    Register file splitter with hub instance.
    
    Args:
        hub_instance: Hub instance to register with
        
    Returns:
        Configured and registered FileSplitterHubConnector
    """
    connector = create_file_splitter_hub_connector()
    connector.hub_connector.register_with_hub(hub_instance)
    return connector