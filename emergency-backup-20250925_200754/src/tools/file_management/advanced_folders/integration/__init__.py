"""Advanced Folders Backend-UI Integration Package.

Enterprise-grade integration layer between backend services and UI components.
Implements signal-based communication, data binding, and real-time updates.

This package provides:
- Backend service abstraction
- Real-time data synchronization
- Signal-based UI updates
- Performance optimization
- Error handling and recovery
"""

from .backend_integration import BackendIntegrationManager
from .realtime_search import RealtimeSearchManager
from .ui_data_bridge import UIDataBridge

__version__ = "1.0.0"
__author__ = "RFU Development Team"

__all__ = [
    "BackendIntegrationManager",
    "RealtimeSearchManager",
    "UIDataBridge",
]
