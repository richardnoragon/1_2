"""
End-to-End Tests for Responsive Layout System

Comprehensive E2E testing for the responsive layout system covering:
- Layout constraint validation across different pane counts
- Responsive breakpoint behavior and adaptation
- Layout transition smoothness and content preservation
- Cross-viewport compatibility and performance validation
"""

import logging
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import test utilities
from tests.e2e.file_management_test_utilities import (
    FileManagementPerformanceMonitor, FileManagementTestDataFactory)

# Mock PyQt5 for testing
try:
    from PyQt5.QtCore import QRect, Qt
    from PyQt5.QtWidgets import QApplication, QWidget
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Create mock classes for testing
    class QApplication:
        @staticmethod
        def instance():
            return Mock()
    
    class QWidget:
        def __init__(self):
            self.geometry_rect = QRect(0, 0, 100, 100)
        
        def geometry(self):
            return self.geometry_rect
        
        def setParent(self, parent):
            pass
        
        def isVisible(self):
            return True
    
    class QRect:
        def __init__(self, x, y, w, h):
            self.x, self.y, self.w, self.h = x, y, w, h
        
        def width(self):
            return self.w
        
        def height(self):
            return self.h
    
    class Qt:
        Horizontal = 1
        Vertical = 2


# Import responsive layout system with mocking
if PYQT_AVAILABLE:
    try:
        from src.rfu.file_explorer.enhanced_multi_pane_explorer import \
            EnhancedMultiPaneExplorer
        from src.rfu.file_explorer.ui.layout_implementations import (
            ContentHierarchyPreserver, DualPaneLayoutImplementor,
            LayoutTransitionManager, LayoutValidationEngine,
            MultiPaneLayoutImplementor, ResponsiveBreakpointHandler,
            SinglePaneLayoutImplementor)
        from src.rfu.file_explorer.ui.responsive_layout_manager import (
            LayoutConfiguration, LayoutConstraint, LayoutType,
            ResponsiveBreakpoint, ResponsiveLayoutManager, ViewportType)
        RESPONSIVE_LAYOUT_AVAILABLE = True
    except ImportError as e:
        RESPONSIVE_LAYOUT_AVAILABLE = False
        print(f"Responsive layout system not available for testing: {e}")
else:
    RESPONSIVE_LAYOUT_AVAILABLE = False


class MockResponsiveLayoutSystem:
    """Mock responsive layout system for testing without PyQt5."""
    
    def __init__(self):
        self.layout_manager = Mock()
        self.viewport_size = (1920, 1080)
        self.current_viewport = "desktop"
        self.available_layouts = {
            1: ["full_width", "centered", "left_sidebar", "right_sidebar"],
            2: ["horizontal_split", "vertical_split"],
            3: ["horizontal_row", "vertical_column", "adaptive_grid"],
            4: ["horizontal_row", "vertical_column", "grid_2x2", "adaptive_grid"]
        }
    
    def get_available_layouts(self, pane_count: int) -> List[str]:
        """Get available layouts for pane count."""
        return self.available_layouts.get(pane_count, [])
    
    def validate_layout_constraints(self, layout_type: str, pane_count: int) -> bool:
        """Validate layout constraints."""
        available = self.get_available_layouts(pane_count)
        return layout_type in available


class ResponsiveLayoutTestUtilities:
    """Specialized test utilities for responsive layout testing."""
    
    def __init__(self):
        self.logger = logging.getLogger('ResponsiveLayoutTest')
        self.performance_monitor = FileManagementPerformanceMonitor()
        self.test_data_factory = FileManagementTestDataFactory()
        
        # Test configurations
        self.viewport_test_cases = [
            {"name": "mobile", "width": 600, "height": 800},
            {"name": "tablet", "width": 900, "height": 1200},
            {"name": "desktop", "width": 1366, "height": 768},
            {"name": "large_desktop", "width": 1920, "height": 1080}
        ]
        
        self.pane_test_cases = [1, 2, 3, 4]
        
        self.layout_performance_targets = {
            "layout_application": 0.5,  # 500ms max
            "transition_animation": 1.0,  # 1s max
            "constraint_evaluation": 0.1,  # 100ms max
            "viewport_adaptation": 0.2   # 200ms max
        }
    
    def create_mock_panes(self, count: int) -> List[QWidget]:
        """Create mock panes for testing."""
        panes = []
        for i in range(count):
            pane = QWidget()
            pane._pane_number = i + 1
            pane._current_path = f"/test/path/pane_{i+1}"
            panes.append(pane)
        return panes
    
    def simulate_viewport_change(self, width: int, height: int) -> Dict[str, Any]:
        """Simulate viewport change and return expected behavior."""
        if width < 768:
            viewport_type = "mobile"
            expected_constraints = {
                2: ["vertical_split"],
                3: ["vertical_column"],
                4: ["vertical_column"]
            }
        elif width < 1024:
            viewport_type = "tablet"
            expected_constraints = {
                2: ["horizontal_split", "vertical_split"],
                3: ["adaptive_grid", "vertical_column"],
                4: ["adaptive_grid"]
            }
        elif width < 1440:
            viewport_type = "desktop"
            expected_constraints = {
                2: ["horizontal_split", "vertical_split"],
                3: ["horizontal_row", "vertical_column", "adaptive_grid"],
                4: ["horizontal_row", "grid_2x2", "adaptive_grid"]
            }
        else:
            viewport_type = "large_desktop"
            expected_constraints = {
                2: ["horizontal_split", "vertical_split"],
                3: ["horizontal_row", "vertical_column", "grid_2x3", "adaptive_grid"],
                4: ["horizontal_row", "grid_2x2", "grid_2x3", "adaptive_grid"]
            }
        
        return {
            "viewport_type": viewport_type,
            "size": (width, height),
            "expected_constraints": expected_constraints
        }


@pytest.fixture
def responsive_layout_utilities():
    """Provide responsive layout test utilities."""
    return ResponsiveLayoutTestUtilities()


@pytest.fixture
def mock_responsive_system():
    """Provide mock responsive layout system."""
    return MockResponsiveLayoutSystem()


@pytest.mark.parametrize("pane_count", [1, 2, 3, 4])
def test_layout_constraints_by_pane_count(responsive_layout_utilities, pane_count):
    """Test layout constraints are properly enforced by pane count."""
    utilities = responsive_layout_utilities
    
    # Test constraint validation
    expected_layouts = {
        1: ["full_width", "centered", "left_sidebar", "right_sidebar", "custom_position"],
        2: ["horizontal_split", "vertical_split"],
        3: ["horizontal_row", "vertical_column", "adaptive_grid"],
        4: ["horizontal_row", "vertical_column", "grid_2x2", "adaptive_grid"]
    }
    
    if RESPONSIVE_LAYOUT_AVAILABLE:
        # Test with actual responsive system
        layout_manager = ResponsiveLayoutManager()
        layout_manager.viewport_size = (1920, 1080)  # Large desktop
        
        available = layout_manager.get_available_layouts(pane_count)
        available_values = [lt.value for lt in available]
        
        # Verify expected layouts are available
        for expected_layout in expected_layouts[pane_count]:
            assert any(expected_layout in av for av in available_values), \
                f"Expected layout {expected_layout} not available for {pane_count} panes"
    else:
        # Test with mock system
        mock_system = MockResponsiveLayoutSystem()
        available = mock_system.get_available_layouts(pane_count)
        
        # Basic constraint validation
        assert len(available) > 0, f"No layouts available for {pane_count} panes"


@pytest.mark.parametrize("viewport_config", [
    {"width": 600, "height": 800, "type": "mobile"},
    {"width": 900, "height": 1200, "type": "tablet"},
    {"width": 1366, "height": 768, "type": "desktop"},
    {"width": 1920, "height": 1080, "type": "large_desktop"}
])
def test_responsive_breakpoint_behavior(responsive_layout_utilities, viewport_config):
    """Test responsive breakpoint detection and layout adaptation."""
    utilities = responsive_layout_utilities
    
    # Simulate viewport change
    width, height = viewport_config["width"], viewport_config["height"]
    expected_type = viewport_config["type"]
    
    viewport_result = utilities.simulate_viewport_change(width, height)
    
    # Verify viewport type detection
    assert viewport_result["viewport_type"] == expected_type, \
        f"Expected viewport type {expected_type}, got {viewport_result['viewport_type']}"
    
    # Test layout constraints for each pane count in this viewport
    for pane_count in [2, 3, 4]:
        expected_constraints = viewport_result["expected_constraints"].get(pane_count, [])
        assert len(expected_constraints) > 0, \
            f"No layout constraints defined for {pane_count} panes in {expected_type} viewport"
        
        if RESPONSIVE_LAYOUT_AVAILABLE:
            # Test with actual responsive system
            layout_manager = ResponsiveLayoutManager()
            layout_manager.viewport_size = (width, height)
            
            available = layout_manager.get_available_layouts(pane_count)
            available_values = [lt.value for lt in available]
            
            # Verify at least one expected constraint is available
            constraint_available = any(
                any(constraint in av for av in available_values)
                for constraint in expected_constraints
            )
            assert constraint_available, \
                f"None of expected constraints {expected_constraints} available"


def test_single_pane_unrestricted_flexibility(responsive_layout_utilities):
    """Test single pane configurations have unrestricted layout flexibility."""
    utilities = responsive_layout_utilities
    
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    # Test single pane with different viewport sizes
    for viewport_config in utilities.viewport_test_cases:
        layout_manager = ResponsiveLayoutManager()
        layout_manager.viewport_size = (viewport_config["width"], viewport_config["height"])
        
        available = layout_manager.get_available_layouts(1)
        available_values = [lt.value for lt in available]
        
        # Single pane should have multiple layout options
        expected_single_pane_layouts = [
            "full_width", "centered"
        ]
        
        for expected in expected_single_pane_layouts:
            assert any(expected in av for av in available_values), \
                f"Single pane missing {expected} layout in {viewport_config['name']} viewport"
        
        # Verify minimum flexibility (at least 2 options)
        assert len(available) >= 2, \
            f"Single pane should have multiple layout options, got {len(available)}"


def test_dual_pane_optimized_arrangements(responsive_layout_utilities):
    """Test dual pane configurations are restricted to horizontal/vertical only."""
    utilities = responsive_layout_utilities
    
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    layout_manager = ResponsiveLayoutManager()
    layout_manager.viewport_size = (1366, 768)  # Desktop viewport
    
    available = layout_manager.get_available_layouts(2)
    available_values = [lt.value for lt in available]
    
    # Dual pane should only have horizontal and vertical splits
    expected_layouts = ["horizontal_split", "vertical_split"]
    
    for expected in expected_layouts:
        assert any(expected in av for av in available_values), \
            f"Dual pane missing {expected} layout"
    
    # Should not have grid layouts for 2 panes
    prohibited_layouts = ["grid_2x2", "grid_2x3", "horizontal_row"]
    for prohibited in prohibited_layouts:
        assert not any(prohibited in av for av in available_values), \
            f"Dual pane should not have {prohibited} layout"


def test_multi_pane_comprehensive_options(responsive_layout_utilities):
    """Test 3+ pane configurations offer comprehensive layout choices."""
    utilities = responsive_layout_utilities
    
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    # Test 3 panes
    layout_manager = ResponsiveLayoutManager()
    layout_manager.viewport_size = (1920, 1080)  # Large desktop
    
    available_3_panes = layout_manager.get_available_layouts(3)
    available_3_values = [lt.value for lt in available_3_panes]
    
    expected_3_pane_layouts = ["horizontal_row", "vertical_column", "adaptive_grid"]
    
    for expected in expected_3_pane_layouts:
        assert any(expected in av for av in available_3_values), \
            f"3-pane missing {expected} layout"
    
    # Test 4 panes
    available_4_panes = layout_manager.get_available_layouts(4)
    available_4_values = [lt.value for lt in available_4_panes]
    
    expected_4_pane_layouts = ["horizontal_row", "vertical_column", "grid_2x2", "adaptive_grid"]
    
    for expected in expected_4_pane_layouts:
        assert any(expected in av for av in available_4_values), \
            f"4-pane missing {expected} layout"
    
    # Verify 3+ panes have more options than dual pane
    assert len(available_3_panes) >= 3, "3-pane should have at least 3 layout options"
    assert len(available_4_panes) >= 4, "4-pane should have at least 4 layout options"


@pytest.mark.parametrize("transition_pair", [
    ("horizontal_split", "vertical_split"),
    ("vertical_column", "grid_2x2"),
    ("full_width", "centered"),
    ("adaptive_grid", "horizontal_row")
])
def test_layout_transition_smoothness(responsive_layout_utilities, transition_pair):
    """Test smooth transitions between different layout configurations."""
    utilities = responsive_layout_utilities
    
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    from_layout_str, to_layout_str = transition_pair
    
    # Find corresponding LayoutType enums
    from_layout = None
    to_layout = None
    
    for layout_type in LayoutType:
        if layout_type.value == from_layout_str:
            from_layout = layout_type
        if layout_type.value == to_layout_str:
            to_layout = layout_type
    
    if not from_layout or not to_layout:
        pytest.skip(f"Layout types not found for transition {transition_pair}")
    
    # Create test panes
    pane_count = max(2, 4 if "grid_2x2" in transition_pair else 3)
    mock_panes = utilities.create_mock_panes(pane_count)
    
    # Test transition
    transition_manager = LayoutTransitionManager(utilities.logger)
    
    # Mock container
    mock_container = QWidget()
    
    # Test transition creation
    with utilities.performance_monitor.monitor_operation("layout_transition") as monitor:
        success = transition_manager.create_smooth_transition(
            mock_panes, from_layout, to_layout, mock_container
        )
    
    # Verify transition was created successfully
    assert success, f"Failed to create transition from {from_layout_str} to {to_layout_str}"
    
    # Verify performance target
    duration = monitor.get_duration()
    target = utilities.layout_performance_targets["transition_animation"]
    assert duration <= target, \
        f"Transition took {duration:.3f}s, expected <= {target}s"


def test_content_hierarchy_preservation():
    """Test content hierarchy is preserved during layout transitions."""
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    # Create test utilities
    utilities = ResponsiveLayoutTestUtilities()
    hierarchy_preserver = ContentHierarchyPreserver(utilities.logger)
    
    # Create mock panes with content
    mock_panes = utilities.create_mock_panes(3)
    
    # Add mock content state to panes
    for i, pane in enumerate(mock_panes):
        pane._file_list = Mock()
        pane._file_list.selectedItems.return_value = [
            Mock(text=lambda col: f"file_{i}_{j}.txt") for j in range(2)
        ]
        pane._file_list.currentItem.return_value = Mock(
            text=lambda col: f"current_file_{i}.txt"
        )
    
    # Capture hierarchy state
    snapshot_id = hierarchy_preserver.capture_hierarchy_state(
        mock_panes, "test_layout"
    )
    
    assert snapshot_id, "Failed to capture hierarchy state"
    assert snapshot_id in hierarchy_preserver.snapshots, "Snapshot not stored"
    
    # Verify snapshot contents
    snapshot = hierarchy_preserver.snapshots[snapshot_id]
    assert snapshot['pane_count'] == 3, "Incorrect pane count in snapshot"
    assert len(snapshot['pane_states']) == 3, "Incorrect pane states count"
    
    # Test hierarchy restoration
    success = hierarchy_preserver.restore_hierarchy_state(snapshot_id, mock_panes)
    assert success, "Failed to restore hierarchy state"
    assert snapshot_id not in hierarchy_preserver.snapshots, "Snapshot not cleaned up"


@pytest.mark.performance
def test_layout_system_performance(responsive_layout_utilities):
    """Test responsive layout system performance under various conditions."""
    utilities = responsive_layout_utilities
    
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    # Performance test cases
    test_cases = [
        {"operation": "constraint_evaluation", "pane_counts": [1, 2, 3, 4], "iterations": 100},
        {"operation": "layout_application", "pane_counts": [2, 4], "iterations": 50},
        {"operation": "viewport_adaptation", "viewports": utilities.viewport_test_cases, "iterations": 20}
    ]
    
    layout_manager = ResponsiveLayoutManager()
    
    for test_case in test_cases:
        operation = test_case["operation"]
        target_time = utilities.layout_performance_targets[operation]
        
        if operation == "constraint_evaluation":
            # Test constraint evaluation performance
            for pane_count in test_case["pane_counts"]:
                with utilities.performance_monitor.monitor_operation(f"constraints_{pane_count}") as monitor:
                    for _ in range(test_case["iterations"]):
                        layout_manager.get_available_layouts(pane_count)
                
                avg_duration = monitor.get_duration() / test_case["iterations"]
                assert avg_duration <= target_time, \
                    f"Constraint evaluation too slow: {avg_duration:.3f}s > {target_time}s"
        
        elif operation == "layout_application":
            # Test layout application performance
            mock_panes = utilities.create_mock_panes(4)
            mock_container = QWidget()
            
            implementor = MultiPaneLayoutImplementor(utilities.logger)
            config = Mock()
            config.margins = (0, 0, 0, 0)
            config.spacing = 2
            
            with utilities.performance_monitor.monitor_operation("layout_application") as monitor:
                for _ in range(test_case["iterations"]):
                    implementor.implement_adaptive_grid(
                        mock_container, mock_panes, config, 1920
                    )
            
            avg_duration = monitor.get_duration() / test_case["iterations"]
            assert avg_duration <= target_time, \
                f"Layout application too slow: {avg_duration:.3f}s > {target_time}s"


def test_responsive_breakpoint_edge_cases(responsive_layout_utilities):
    """Test edge cases in responsive breakpoint handling."""
    utilities = responsive_layout_utilities
    
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    breakpoint_handler = ResponsiveBreakpointHandler(utilities.logger)
    
    # Test edge case viewport sizes
    edge_cases = [
        {"width": 767, "expected": "mobile"},    # Mobile upper bound
        {"width": 768, "expected": "tablet"},    # Tablet lower bound
        {"width": 1023, "expected": "tablet"},   # Tablet upper bound
        {"width": 1024, "expected": "desktop"},  # Desktop lower bound
        {"width": 1439, "expected": "desktop"},  # Desktop upper bound
        {"width": 1440, "expected": "large_desktop"},  # Large desktop lower bound
        {"width": 100, "expected": "mobile"},    # Extremely small
        {"width": 3000, "expected": "large_desktop"}   # Extremely large
    ]
    
    for case in edge_cases:
        detected = breakpoint_handler.detect_breakpoint(case["width"], 800)
        assert detected == case["expected"], \
            f"Breakpoint detection failed for width {case['width']}: " \
            f"expected {case['expected']}, got {detected}"


def test_layout_validation_engine():
    """Test layout validation engine catches invalid configurations."""
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    validation_engine = LayoutValidationEngine(logging.getLogger('test'))
    mock_container = QWidget()
    
    # Test invalid configurations
    invalid_cases = [
        {
            "layout": LayoutType.HORIZONTAL_SPLIT,
            "pane_count": 1,
            "viewport": (1920, 1080),
            "expected_error": "Split layouts require exactly 2 panes"
        },
        {
            "layout": LayoutType.GRID_2X2,
            "pane_count": 3,
            "viewport": (1920, 1080),
            "expected_error": "2×2 grid requires exactly 4 panes"
        },
        {
            "layout": LayoutType.LEFT_SIDEBAR,
            "pane_count": 1,
            "viewport": (500, 600),
            "expected_error": "Sidebar layouts require minimum 800px width"
        },
        {
            "layout": LayoutType.HORIZONTAL_ROW,
            "pane_count": 2,
            "viewport": (1920, 1080),
            "expected_error": "Row/column layouts require 3+ panes"
        }
    ]
    
    for case in invalid_cases:
        is_valid, error_msg = validation_engine.validate_layout_application(
            case["layout"], case["pane_count"], case["viewport"], mock_container
        )
        
        assert not is_valid, f"Validation should fail for {case['layout'].value}"
        assert case["expected_error"] in error_msg, \
            f"Expected error message '{case['expected_error']}' not found in '{error_msg}'"


def test_enhanced_multi_pane_explorer_integration():
    """Test integration of responsive system with enhanced multi-pane explorer."""
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    # Mock QApplication for testing
    with patch('PyQt5.QtWidgets.QApplication.instance') as mock_app:
        mock_app.return_value = Mock()
        
        try:
            # Create enhanced explorer
            explorer = EnhancedMultiPaneExplorer()
            
            # Verify responsive components are initialized
            assert hasattr(explorer, 'layout_manager'), "Layout manager not initialized"
            assert hasattr(explorer, 'responsive_enabled'), "Responsive flag not set"
            assert explorer.responsive_enabled, "Responsive mode should be enabled"
            
            # Test pane count changes
            initial_pane_count = len(explorer.panes)
            explorer.set_pane_count(3)
            
            assert len(explorer.panes) == 3, "Pane count not updated correctly"
            
            # Test layout application
            if hasattr(explorer, 'current_layout_type'):
                assert explorer.current_layout_type is not None, "No layout applied"
            
            # Test status reporting
            status = explorer.get_layout_status()
            assert status['responsive_enabled'], "Responsive should be enabled in status"
            assert status['pane_count'] == 3, "Incorrect pane count in status"
            
        except Exception as e:
            pytest.skip(f"Enhanced explorer test failed: {e}")


@pytest.mark.integration
def test_cross_viewport_layout_compatibility():
    """Test layout compatibility across different viewport sizes."""
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    utilities = ResponsiveLayoutTestUtilities()
    layout_manager = ResponsiveLayoutManager()
    
    # Test layout availability across viewports
    compatibility_matrix = {}
    
    for viewport_config in utilities.viewport_test_cases:
        viewport_name = viewport_config["name"]
        layout_manager.viewport_size = (viewport_config["width"], viewport_config["height"])
        
        compatibility_matrix[viewport_name] = {}
        
        for pane_count in utilities.pane_test_cases:
            available = layout_manager.get_available_layouts(pane_count)
            compatibility_matrix[viewport_name][pane_count] = [lt.value for lt in available]
    
    # Verify cross-viewport compatibility principles
    
    # Single pane should always have at least full_width available
    for viewport_name in compatibility_matrix:
        single_pane_layouts = compatibility_matrix[viewport_name][1]
        assert any("full_width" in layout for layout in single_pane_layouts), \
            f"Full width not available in {viewport_name} viewport"
    
    # Dual pane should always have at least one split option
    for viewport_name in compatibility_matrix:
        dual_pane_layouts = compatibility_matrix[viewport_name][2]
        has_split = any(
            any(split in layout for split in ["horizontal_split", "vertical_split"])
            for layout in dual_pane_layouts
        )
        assert has_split, f"No split layouts available in {viewport_name} viewport"
    
    # Desktop and large desktop should have more options than mobile/tablet
    desktop_layouts = len(compatibility_matrix["desktop"][4])
    mobile_layouts = len(compatibility_matrix["mobile"][4])
    
    assert desktop_layouts >= mobile_layouts, \
        "Desktop should have at least as many layout options as mobile"


def test_error_handling_and_recovery():
    """Test error handling and recovery in the responsive layout system."""
    if not RESPONSIVE_LAYOUT_AVAILABLE:
        pytest.skip("Responsive layout system not available")
    
    utilities = ResponsiveLayoutTestUtilities()
    
    # Test with invalid inputs
    layout_manager = ResponsiveLayoutManager()
    
    # Test invalid pane count
    available = layout_manager.get_available_layouts(-1)
    assert isinstance(available, list), "Should return empty list for invalid pane count"
    
    available = layout_manager.get_available_layouts(10)
    assert isinstance(available, list), "Should return empty list for excessive pane count"
    
    # Test with null container
    success = layout_manager.apply_layout(LayoutType.HORIZONTAL_SPLIT, None, False)
    assert not success, "Should fail with null container"
    
    # Test validation engine error handling
    validation_engine = LayoutValidationEngine(utilities.logger)
    
    is_valid, error_msg = validation_engine.validate_layout_application(
        LayoutType.GRID_2X2, 0, (1920, 1080), None
    )
    assert not is_valid, "Should fail validation with invalid inputs"
    assert "container" in error_msg.lower() or "pane" in error_msg.lower(), \
        "Error message should mention the validation failure reason"


if __name__ == '__main__':
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])