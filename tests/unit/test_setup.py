"""
Test setup and configuration for metrics_service tests
Generated on: 2025-08-30
"""

import sys
import unittest.mock
from pathlib import Path
from unittest.mock import Mock

# Add the source directory to Python path
test_dir = Path(__file__).parent
src_dir = test_dir.parent.parent / "src"
sys.path.insert(0, str(src_dir))


class MockNetworkLoggingManager:
    """Mock logging manager for testing."""
    
    def get_tool_logger(self, name):
        """Return a mock logger."""
        logger = Mock()
        logger.debug = Mock()
        logger.info = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        logger.critical = Mock()
        return logger


def mock_get_network_logging_manager():
    """Mock function to get logging manager."""
    return MockNetworkLoggingManager()


# Apply the mock before importing metrics_service
module_path = 'src.tools.network.network_connectivity_complex.core.logging_integration'
sys.modules[module_path] = Mock()
logging_integration_mock = sys.modules[module_path]
logging_integration_mock.get_network_logging_manager = mock_get_network_logging_manager

# Also create the mock for direct import
with unittest.mock.patch.dict('sys.modules', {
    'logging_integration': Mock(
        get_network_logging_manager=mock_get_network_logging_manager
    )
}):
    pass