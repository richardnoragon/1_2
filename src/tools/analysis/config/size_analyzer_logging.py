"""
Size Analyzer Logging Configuration

This module provides logging configuration specifically for the Size Analyzer tool,
integrating with the main logging system and providing categorized logging.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.logging_manager import LogManager

from .size_analyzer_config import SizeAnalyzerConfig


class SizeAnalyzerLogger:
    """
    Logging manager for Size Analyzer with categorized logging and
    integration with the main logging system.
    """
    
    def __init__(self, config: Optional[SizeAnalyzerConfig] = None):
        """Initialize the Size Analyzer logging manager."""
        self.config = config or SizeAnalyzerConfig()
        self.loggers: Dict[str, logging.Logger] = {}
        self.main_logger = LogManager.get_logger('SizeAnalyzer')
        
        # Initialize logging configuration
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration for Size Analyzer."""
        try:
            # Get logging configuration
            logging_config = self.config.get_all_settings().get('logging', {})
            
            if not logging_config.get('enable_tool_logging', True):
                return
            
            # Setup log directory
            log_dir = self._ensure_log_directory()
            
            # Setup main log file
            log_file = os.path.join(log_dir, 'size_analyzer.log')
            
            # Configure main logger
            self._configure_main_logger(log_file, logging_config)
            
            # Configure category loggers
            self._configure_category_loggers(log_dir, logging_config)
            
        except Exception as e:
            # Fall back to main logger
            self.main_logger.error(f"Error setting up Size Analyzer logging: {e}")
    
    def _ensure_log_directory(self) -> str:
        """Ensure the log directory exists and return its path."""
        log_dir = self.config.get_resource_path('log_directory')
        
        if not log_dir:
            # Fall back to default
            base_dir = Path(__file__).parent.parent.parent
            log_dir = str(base_dir / 'logs' / 'size_analyzer')
        
        # Create directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        return log_dir
    
    def _configure_main_logger(self, log_file: str, config: Dict[str, Any]):
        """Configure the main Size Analyzer logger."""
        try:
            # Get log level
            log_level = getattr(logging, config.get('log_level', 'INFO').upper())
            
            # Configure main logger
            self.main_logger.setLevel(log_level)
            
            # Remove existing handlers to avoid duplicates
            for handler in self.main_logger.handlers[:]:
                self.main_logger.removeHandler(handler)
            
            # Create file handler with rotation
            max_size = config.get('max_log_size_mb', 10) * 1024 * 1024
            backup_count = config.get('backup_count', 5)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count
            )
            file_handler.setLevel(log_level)
            
            # Set formatter
            log_format = config.get(
                'log_format',
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            formatter = logging.Formatter(log_format)
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.main_logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Error configuring main logger: {e}")
    
    def _configure_category_loggers(self, log_dir: str, config: Dict[str, Any]):
        """Configure category-specific loggers."""
        try:
            log_categories = config.get('log_categories', {})
            
            for category, level_name in log_categories.items():
                logger_name = f'SizeAnalyzer.{category}'
                logger = LogManager.get_logger(logger_name)
                
                # Set log level
                try:
                    log_level = getattr(logging, level_name.upper())
                    logger.setLevel(log_level)
                except AttributeError:
                    logger.setLevel(logging.INFO)
                
                # Create category-specific log file
                category_log_file = os.path.join(log_dir, f'{category}.log')
                
                # Create file handler
                file_handler = logging.handlers.RotatingFileHandler(
                    category_log_file,
                    maxBytes=5 * 1024 * 1024,  # 5MB
                    backupCount=3
                )
                file_handler.setLevel(log_level)
                
                # Set formatter
                formatter = logging.Formatter(
                    f'%(asctime)s - {category.upper()} - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)
                
                # Add handler
                logger.addHandler(file_handler)
                
                # Store logger reference
                self.loggers[category] = logger
                
        except Exception as e:
            self.main_logger.error(f"Error configuring category loggers: {e}")
    
    def get_logger(self, category: str = 'main') -> logging.Logger:
        """Get a logger for a specific category."""
        if category == 'main':
            return self.main_logger
        
        return self.loggers.get(category, self.main_logger)
    
    def log_core_logic(self, level: str, message: str, **kwargs):
        """Log core logic events."""
        logger = self.get_logger('core_logic')
        getattr(logger, level.lower(), logger.info)(message, **kwargs)
    
    def log_gui_event(self, level: str, message: str, **kwargs):
        """Log GUI events."""
        logger = self.get_logger('gui_events')
        getattr(logger, level.lower(), logger.info)(message, **kwargs)
    
    def log_hub_integration(self, level: str, message: str, **kwargs):
        """Log hub integration events."""
        logger = self.get_logger('hub_integration')
        getattr(logger, level.lower(), logger.info)(message, **kwargs)
    
    def log_performance(self, level: str, message: str, **kwargs):
        """Log performance metrics."""
        logger = self.get_logger('performance')
        getattr(logger, level.lower(), logger.debug)(message, **kwargs)
    
    def log_error(self, message: str, exception: Exception = None, **kwargs):
        """Log error events."""
        logger = self.get_logger('errors')
        if exception:
            logger.error(message, exc_info=exception, **kwargs)
        else:
            logger.error(message, **kwargs)
    
    def log_analysis_start(self, directory: str, settings: Dict[str, Any]):
        """Log analysis start event."""
        self.log_core_logic('info', f"Starting analysis of directory: {directory}")
        self.log_performance('debug', f"Analysis settings: {settings}")
    
    def log_analysis_progress(self, percentage: int, message: str):
        """Log analysis progress."""
        self.log_core_logic('debug', f"Analysis progress: {percentage}% - {message}")
    
    def log_analysis_complete(self, directory: str, results: Dict[str, Any]):
        """Log analysis completion."""
        file_count = results.get('file_count', 0)
        total_size = results.get('total_size', 0)
        
        self.log_core_logic(
            'info',
            f"Analysis complete for {directory}: {file_count} files, "
            f"{total_size} bytes"
        )
        
        # Log performance metrics if available
        if 'performance_metrics' in results:
            metrics = results['performance_metrics']
            self.log_performance(
                'info',
                f"Performance: {metrics.get('files_per_second', 0):.2f} files/sec, "
                f"{metrics.get('bytes_per_second', 0):.2f} bytes/sec"
            )
    
    def log_export_event(self, export_path: str, format_type: str, success: bool):
        """Log export events."""
        if success:
            self.log_core_logic(
                'info',
                f"Successfully exported results to {export_path} ({format_type})"
            )
        else:
            self.log_error(f"Failed to export results to {export_path}")
    
    def log_hub_event(self, event_type: str, data: Dict[str, Any]):
        """Log hub integration events."""
        self.log_hub_integration(
            'info',
            f"Hub event: {event_type} - {data}"
        )
    
    def log_configuration_change(self, setting: str, old_value: Any, new_value: Any):
        """Log configuration changes."""
        self.log_core_logic(
            'info',
            f"Configuration changed: {setting} from {old_value} to {new_value}"
        )
    
    def log_resource_usage(self, cpu_percent: float, memory_mb: float, 
                          disk_io: float):
        """Log resource usage metrics."""
        self.log_performance(
            'debug',
            f"Resource usage: CPU {cpu_percent:.1f}%, "
            f"Memory {memory_mb:.1f}MB, Disk I/O {disk_io:.1f}MB/s"
        )
    
    def cleanup(self):
        """Cleanup logging resources."""
        try:
            # Close all handlers
            for logger in self.loggers.values():
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)
            
            # Close main logger handlers
            for handler in self.main_logger.handlers[:]:
                handler.close()
                self.main_logger.removeHandler(handler)
                
        except Exception as e:
            print(f"Error during logging cleanup: {e}")


# Global logger instance
_size_analyzer_logger: Optional[SizeAnalyzerLogger] = None


def get_size_analyzer_logger(config: Optional[SizeAnalyzerConfig] = None) -> SizeAnalyzerLogger:
    """Get the global Size Analyzer logger instance."""
    global _size_analyzer_logger
    
    if _size_analyzer_logger is None:
        _size_analyzer_logger = SizeAnalyzerLogger(config)
    
    return _size_analyzer_logger


def cleanup_logging():
    """Cleanup the global logging instance."""
    global _size_analyzer_logger
    
    if _size_analyzer_logger:
        _size_analyzer_logger.cleanup()
        _size_analyzer_logger = None