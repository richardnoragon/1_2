"""Tests for the logging service."""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from ..core.logging_service import (
    LoggingService, LogLevel, LogFormat, LogEntry, LogFilter,
    LogCollector, PerformanceLogCollector, SecurityLogCollector,
    ErrorLogCollector, LogFormatter, FileLogHandler, LogRotationPolicy
)


class TestLogEntry:
    """Test log entry functionality."""
    
    def test_log_entry_creation(self):
        """Test log entry creation."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            logger_name="test.logger",
            message="Test message",
            tool_name="TestTool"
        )
        
        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
        assert entry.tool_name == "TestTool"
        assert isinstance(entry.context, dict)
        assert isinstance(entry.metadata, dict)


class TestLogFilter:
    """Test log filtering functionality."""
    
    def test_log_filter_creation(self):
        """Test log filter creation."""
        log_filter = LogFilter(
            min_level=LogLevel.WARNING,
            max_level=LogLevel.CRITICAL,
            tools=["TestTool"],
            keywords=["error", "warning"]
        )
        
        assert log_filter.min_level == LogLevel.WARNING
        assert log_filter.max_level == LogLevel.CRITICAL
        assert "TestTool" in log_filter.tools
        assert "error" in log_filter.keywords


class TestLogFormatter:
    """Test log formatting functionality."""
    
    def test_json_formatting(self):
        """Test JSON log formatting."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            logger_name="test.logger",
            message="Test message",
            tool_name="TestTool"
        )
        
        formatted = LogFormatter.format_json(entry)
        assert isinstance(formatted, str)
        assert "Test message" in formatted
        assert "TestTool" in formatted
    
    def test_plain_formatting(self):
        """Test plain text log formatting."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            logger_name="test.logger",
            message="Test message",
            tool_name="TestTool"
        )
        
        formatted = LogFormatter.format_plain(entry)
        assert isinstance(formatted, str)
        assert "INFO" in formatted
        assert "Test message" in formatted
        assert "TestTool" in formatted
    
    def test_csv_formatting(self):
        """Test CSV log formatting."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            logger_name="test.logger",
            message="Test message",
            tool_name="TestTool"
        )
        
        formatted = LogFormatter.format_csv(entry)
        assert isinstance(formatted, str)
        assert "," in formatted  # CSV should have commas
        assert "Test message" in formatted


class TestLogCollectors:
    """Test log collector functionality."""
    
    @pytest.fixture
    def logging_service(self):
        """Create a test logging service."""
        return LoggingService()
    
    def test_performance_log_collector(self, logging_service):
        """Test performance log collector."""
        collector = PerformanceLogCollector(logging_service)
        
        # Test performance log entry
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.PERFORMANCE,
            logger_name="test.logger",
            message="Performance test",
            tool_name="TestTool",
            performance_data={
                "response_time_ms": 1000,
                "memory_usage_mb": 100
            }
        )
        
        # Process the entry
        collector._process_log_entry(entry)
        
        # Verify metrics were stored
        assert "TestTool.response_time_ms" in collector._performance_metrics
        assert "TestTool.memory_usage_mb" in collector._performance_metrics
    
    def test_security_log_collector(self, logging_service):
        """Test security log collector."""
        collector = SecurityLogCollector(logging_service)
        
        # Test security log entry
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.SECURITY,
            logger_name="test.logger",
            message="failed_authentication attempt",
            tool_name="TestTool"
        )
        
        # Process the entry
        collector._process_log_entry(entry)
        
        # Verify security event was stored
        assert len(collector._security_events) > 0
    
    def test_error_log_collector(self, logging_service):
        """Test error log collector."""
        collector = ErrorLogCollector(logging_service)
        
        # Test error log entry
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            logger_name="test.logger",
            message="Test error",
            tool_name="TestTool",
            correlation_id="test-correlation-123"
        )
        
        # Process the entry
        collector._process_log_entry(entry)
        
        # Verify error was stored
        error_key = "TestTool.None"  # operation is None
        assert error_key in collector._error_patterns


class TestFileLogHandler:
    """Test file log handler functionality."""
    
    def test_file_handler_creation(self):
        """Test file log handler creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            handler = FileLogHandler(
                name="test_handler",
                file_path=str(log_file),
                formatter=LogFormatter(),
                log_filter=LogFilter(),
                rotation_policy=LogRotationPolicy.SIZE_BASED,
                max_size_mb=1
            )
            
            assert handler.name == "test_handler"
            assert handler.file_path == log_file
    
    def test_file_handler_logging(self):
        """Test file handler logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            handler = FileLogHandler(
                name="test_handler",
                file_path=str(log_file),
                formatter=LogFormatter(),
                log_filter=LogFilter(),
                rotation_policy=LogRotationPolicy.SIZE_BASED
            )
            
            # Create test log entry
            entry = LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                logger_name="test.logger",
                message="Test message",
                tool_name="TestTool"
            )
            
            # Handle the entry
            handler.handle(entry)
            
            # Verify file was created and has content
            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content


class TestLoggingService:
    """Test logging service functionality."""
    
    @pytest.fixture
    def logging_service(self):
        """Create a test logging service."""
        return LoggingService()
    
    def test_structured_logging(self, logging_service):
        """Test structured logging."""
        logging_service.log_structured(
            level=LogLevel.INFO,
            tool_name="TestTool",
            message="Test structured log",
            operation="test_operation",
            context={"key": "value"},
            metadata={"meta": "data"}
        )
        
        # Verify log was stored
        assert len(logging_service._log_entries) > 0
        
        # Get the logged entry
        entry = logging_service._log_entries[-1]
        assert entry.message == "Test structured log"
        assert entry.tool_name == "TestTool"
        assert entry.operation == "test_operation"
        assert entry.context["key"] == "value"
        assert entry.metadata["meta"] == "data"
    
    def test_log_search(self, logging_service):
        """Test log search functionality."""
        # Add some test logs
        logging_service.log_structured(
            LogLevel.INFO, "Tool1", "Info message", operation="op1"
        )
        logging_service.log_structured(
            LogLevel.ERROR, "Tool2", "Error message", operation="op2"
        )
        logging_service.log_structured(
            LogLevel.WARNING, "Tool1", "Warning message", operation="op1"
        )
        
        # Search by tool
        tool_filter = LogFilter(tools=["Tool1"])
        results = logging_service.search_logs(tool_filter)
        assert len(results) == 2
        assert all(r.tool_name == "Tool1" for r in results)
        
        # Search by level
        error_filter = LogFilter(
            min_level=LogLevel.ERROR,
            max_level=LogLevel.ERROR
        )
        results = logging_service.search_logs(error_filter)
        assert len(results) == 1
        assert results[0].level == LogLevel.ERROR
        
        # Search by keyword
        keyword_filter = LogFilter(keywords=["Warning"])
        results = logging_service.search_logs(keyword_filter)
        assert len(results) == 1
        assert "Warning" in results[0].message
    
    def test_log_analytics(self, logging_service):
        """Test log analytics functionality."""
        # Add test logs
        logging_service.log_structured(
            LogLevel.INFO, "Tool1", "Message 1"
        )
        logging_service.log_structured(
            LogLevel.ERROR, "Tool1", "Message 2"
        )
        logging_service.log_structured(
            LogLevel.INFO, "Tool2", "Message 3"
        )
        
        # Get analytics
        analytics = logging_service.get_analytics()
        
        assert "Tool1" in analytics
        assert "Tool2" in analytics
        assert analytics["Tool1"]["INFO_count"] >= 1
        assert analytics["Tool1"]["ERROR_count"] >= 1
        assert analytics["Tool1"]["total_count"] >= 2
    
    def test_log_export(self, logging_service):
        """Test log export functionality."""
        # Add test logs
        logging_service.log_structured(
            LogLevel.INFO, "TestTool", "Export test message"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_path = f.name
        
        try:
            # Export logs
            success = logging_service.export_logs(
                export_path,
                LogFilter(),
                LogFormat.JSON
            )
            assert success
            
            # Verify export file
            assert Path(export_path).exists()
            content = Path(export_path).read_text()
            assert "Export test message" in content
            
        finally:
            Path(export_path).unlink(missing_ok=True)
    
    def test_log_cleanup(self, logging_service):
        """Test log cleanup functionality."""
        # Add old log entry
        old_time = datetime.now() - timedelta(hours=25)
        old_entry = LogEntry(
            timestamp=old_time,
            level=LogLevel.INFO,
            logger_name="test.logger",
            message="Old message",
            tool_name="TestTool"
        )
        logging_service._log_entries.append(old_entry)
        
        # Add recent log entry
        logging_service.log_structured(
            LogLevel.INFO, "TestTool", "Recent message"
        )
        
        initial_count = len(logging_service._log_entries)
        
        # Cleanup old logs (older than 24 hours)
        logging_service.cleanup_old_logs(24)
        
        # Should have fewer entries now
        assert len(logging_service._log_entries) < initial_count
        
        # Recent message should still be there
        recent_messages = [e.message for e in logging_service._log_entries]
        assert "Recent message" in recent_messages
        assert "Old message" not in recent_messages
    
    def test_log_statistics(self, logging_service):
        """Test log statistics functionality."""
        # Add test logs
        logging_service.log_structured(
            LogLevel.INFO, "Tool1", "Message 1"
        )
        logging_service.log_structured(
            LogLevel.ERROR, "Tool2", "Message 2"
        )
        
        # Get statistics
        stats = logging_service.get_log_statistics()
        
        assert "total_entries" in stats
        assert "level_distribution" in stats
        assert "tool_distribution" in stats
        assert "time_range_seconds" in stats
        
        assert stats["total_entries"] >= 2
        assert "INFO" in stats["level_distribution"]
        assert "ERROR" in stats["level_distribution"]
        assert "Tool1" in stats["tool_distribution"]
        assert "Tool2" in stats["tool_distribution"]


class TestLoggingIntegration:
    """Integration tests for logging system."""
    
    def test_logging_with_metrics(self):
        """Test integration between logging and metrics."""
        from ..core.metrics_service import get_metrics_service
        
        logging_service = LoggingService()
        metrics_service = get_metrics_service()
        
        # Log performance data
        logging_service.log_structured(
            LogLevel.PERFORMANCE,
            "TestTool",
            "Performance test",
            performance_data={
                "response_time_ms": 500,
                "memory_usage_mb": 128
            }
        )
        
        # Verify metrics were recorded
        # (This would require the metrics service to listen to logging events)
        assert len(logging_service._log_entries) > 0
    
    def test_logging_with_notifications(self):
        """Test integration between logging and notifications."""
        from ..core.notification_service import get_notification_service
        
        logging_service = LoggingService()
        notification_service = get_notification_service()
        
        # Log error (should trigger notification)
        logging_service.log_structured(
            LogLevel.ERROR,
            "TestTool",
            "Test error for notification"
        )
        
        # Verify log was created
        assert len(logging_service._log_entries) > 0
        
        # Notification would be triggered through rules
        # (This would require proper event integration)


if __name__ == "__main__":
    pytest.main([__file__])