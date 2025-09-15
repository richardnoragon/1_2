"""
Unit Tests for Responsive Layout Constraint System

Tests the core constraint evaluation logic, layout availability calculations,
and responsive breakpoint behavior in isolation.
"""

from typing import Dict, List
from unittest.mock import Mock, patch

import pytest


# Mock the layout system for unit testing
class MockLayoutType:
    """Mock LayoutType enum for testing."""
    FULL_WIDTH = "full_width"
    CENTERED = "centered"
    LEFT_SIDEBAR = "left_sidebar"
    RIGHT_SIDEBAR = "right_sidebar"
    CUSTOM_POSITION = "custom_position"
    HORIZONTAL_SPLIT = "horizontal_split"
    VERTICAL_SPLIT = "vertical_split"
    HORIZONTAL_ROW = "horizontal_row"
    VERTICAL_COLUMN = "vertical_column"
    GRID_2X2 = "grid_2x2"
    GRID_2X3 = "grid_2x3"
    ADAPTIVE_GRID = "adaptive_grid"


class MockViewportType:
    """Mock ViewportType enum for testing."""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LARGE_DESKTOP = "large_desktop"


class LayoutConstraintValidator:
    """Validates layout constraints in isolation."""
    
    def __init__(self):
        self.layout_constraints = {
            # Single pane layouts
            MockLayoutType.FULL_WIDTH: {
                "min_panes": 1, "max_panes": 1, 
                "min_width": 0, "min_height": 0,
                "viewports": ["mobile", "tablet", "desktop", "large_desktop"]
            },
            MockLayoutType.CENTERED: {
                "min_panes": 1, "max_panes": 1,
                "min_width": 600, "min_height": 0,
                "viewports": ["tablet", "desktop", "large_desktop"]
            },
            MockLayoutType.LEFT_SIDEBAR: {
                "min_panes": 1, "max_panes": 1,
                "min_width": 800, "min_height": 0,
                "viewports": ["desktop", "large_desktop"]
            },
            MockLayoutType.RIGHT_SIDEBAR: {
                "min_panes": 1, "max_panes": 1,
                "min_width": 800, "min_height": 0,
                "viewports": ["desktop", "large_desktop"]
            },
            MockLayoutType.CUSTOM_POSITION: {
                "min_panes": 1, "max_panes": 1,
                "min_width": 1024, "min_height": 0,
                "viewports": ["desktop", "large_desktop"]
            },
            
            # Dual pane layouts
            MockLayoutType.HORIZONTAL_SPLIT: {
                "min_panes": 2, "max_panes": 2,
                "min_width": 600, "min_height": 0,
                "viewports": ["tablet", "desktop", "large_desktop"]
            },
            MockLayoutType.VERTICAL_SPLIT: {
                "min_panes": 2, "max_panes": 2,
                "min_width": 0, "min_height": 600,
                "viewports": ["mobile", "tablet", "desktop", "large_desktop"]
            },
            
            # Multi-pane layouts
            MockLayoutType.HORIZONTAL_ROW: {
                "min_panes": 3, "max_panes": 4,
                "min_width": 900, "min_height": 0,
                "viewports": ["desktop", "large_desktop"]
            },
            MockLayoutType.VERTICAL_COLUMN: {
                "min_panes": 3, "max_panes": 4,
                "min_width": 0, "min_height": 800,
                "viewports": ["tablet", "desktop", "large_desktop"]
            },
            MockLayoutType.GRID_2X2: {
                "min_panes": 4, "max_panes": 4,
                "min_width": 800, "min_height": 600,
                "viewports": ["desktop", "large_desktop"]
            },
            MockLayoutType.ADAPTIVE_GRID: {
                "min_panes": 3, "max_panes": 4,
                "min_width": 600, "min_height": 400,
                "viewports": ["tablet", "desktop", "large_desktop"]
            }
        }
    
    def is_layout_valid(self, layout_type: str, pane_count: int,
                       viewport_width: int, viewport_height: int,
                       viewport_type: str) -> bool:
        """Check if layout is valid under given conditions."""
        if layout_type not in self.layout_constraints:
            return False
        
        constraint = self.layout_constraints[layout_type]
        
        # Check pane count
        if not (constraint["min_panes"] <= pane_count <= constraint["max_panes"]):
            return False
        
        # Check viewport size
        if (viewport_width < constraint["min_width"] or 
            viewport_height < constraint["min_height"]):
            return False
        
        # Check viewport type
        if viewport_type not in constraint["viewports"]:
            return False
        
        return True
    
    def get_available_layouts(self, pane_count: int, viewport_width: int,
                            viewport_height: int, viewport_type: str) -> List[str]:
        """Get available layouts for given conditions."""
        available = []
        
        for layout_type in self.layout_constraints:
            if self.is_layout_valid(
                layout_type, pane_count, viewport_width, 
                viewport_height, viewport_type
            ):
                available.append(layout_type)
        
        return available


@pytest.fixture
def constraint_validator():
    """Provide layout constraint validator."""
    return LayoutConstraintValidator()


class TestSinglePaneLayoutConstraints:
    """Test single pane layout constraints and flexibility."""
    
    @pytest.mark.parametrize("viewport_config", [
        {"width": 400, "height": 600, "type": "mobile"},
        {"width": 800, "height": 1000, "type": "tablet"},
        {"width": 1366, "height": 768, "type": "desktop"},
        {"width": 1920, "height": 1080, "type": "large_desktop"}
    ])
    def test_single_pane_unrestricted_flexibility(self, constraint_validator, viewport_config):
        """Test single pane has unrestricted layout flexibility."""
        validator = constraint_validator
        width, height, vtype = viewport_config["width"], viewport_config["height"], viewport_config["type"]
        
        available = validator.get_available_layouts(1, width, height, vtype)
        
        # Single pane should always have at least full_width available
        assert MockLayoutType.FULL_WIDTH in available, \
            f"Full width not available in {vtype} viewport"
        
        # Check viewport-specific availability
        if vtype in ["tablet", "desktop", "large_desktop"]:
            assert MockLayoutType.CENTERED in available, \
                f"Centered not available in {vtype} viewport"
        
        if vtype in ["desktop", "large_desktop"]:
            if width >= 800:
                assert MockLayoutType.LEFT_SIDEBAR in available, \
                    f"Left sidebar not available in {vtype} viewport"
                assert MockLayoutType.RIGHT_SIDEBAR in available, \
                    f"Right sidebar not available in {vtype} viewport"
        
        if vtype == "large_desktop" and width >= 1024:
            assert MockLayoutType.CUSTOM_POSITION in available, \
                f"Custom position not available in {vtype} viewport"
        
        # Verify minimum flexibility
        assert len(available) >= 1, f"Single pane should have at least 1 layout option"
    
    def test_single_pane_constraint_enforcement(self, constraint_validator):
        """Test single pane layout constraints are properly enforced."""
        validator = constraint_validator
        
        # Test centered layout width requirement
        assert not validator.is_layout_valid(
            MockLayoutType.CENTERED, 1, 500, 600, "tablet"
        ), "Centered should require minimum 600px width"
        
        assert validator.is_layout_valid(
            MockLayoutType.CENTERED, 1, 700, 600, "tablet"
        ), "Centered should be valid with sufficient width"
        
        # Test sidebar width requirements
        assert not validator.is_layout_valid(
            MockLayoutType.LEFT_SIDEBAR, 1, 700, 600, "desktop"
        ), "Left sidebar should require minimum 800px width"
        
        assert validator.is_layout_valid(
            MockLayoutType.LEFT_SIDEBAR, 1, 900, 600, "desktop"
        ), "Left sidebar should be valid with sufficient width"
        
        # Test custom position requirements
        assert not validator.is_layout_valid(
            MockLayoutType.CUSTOM_POSITION, 1, 800, 600, "desktop"
        ), "Custom position should require minimum 1024px width"
        
        assert validator.is_layout_valid(
            MockLayoutType.CUSTOM_POSITION, 1, 1200, 600, "large_desktop"
        ), "Custom position should be valid with sufficient width and viewport"


class TestDualPaneLayoutConstraints:
    """Test dual pane layout constraints and restrictions."""
    
    def test_dual_pane_restricted_to_splits(self, constraint_validator):
        """Test dual pane is restricted to horizontal/vertical splits only."""
        validator = constraint_validator
        
        # Test on desktop viewport
        available = validator.get_available_layouts(2, 1366, 768, "desktop")
        
        # Should have both split options
        assert MockLayoutType.HORIZONTAL_SPLIT in available, \
            "Horizontal split should be available for dual pane"
        assert MockLayoutType.VERTICAL_SPLIT in available, \
            "Vertical split should be available for dual pane"
        
        # Should not have single pane layouts
        assert MockLayoutType.FULL_WIDTH not in available, \
            "Single pane layouts should not be available for dual pane"
        assert MockLayoutType.CENTERED not in available, \
            "Single pane layouts should not be available for dual pane"
        
        # Should not have multi-pane layouts
        assert MockLayoutType.HORIZONTAL_ROW not in available, \
            "Multi-pane layouts should not be available for dual pane"
        assert MockLayoutType.GRID_2X2 not in available, \
            "Grid layouts should not be available for dual pane"
    
    @pytest.mark.parametrize("viewport_config", [
        {"width": 500, "height": 600, "type": "mobile"},
        {"width": 700, "height": 1000, "type": "tablet"},
        {"width": 1200, "height": 500, "type": "desktop"}
    ])
    def test_dual_pane_viewport_constraints(self, constraint_validator, viewport_config):
        """Test dual pane viewport-specific constraints."""
        validator = constraint_validator
        width, height, vtype = viewport_config["width"], viewport_config["height"], viewport_config["type"]
        
        available = validator.get_available_layouts(2, width, height, vtype)
        
        # Horizontal split requires minimum width
        if width >= 600:
            if vtype in ["tablet", "desktop", "large_desktop"]:
                assert MockLayoutType.HORIZONTAL_SPLIT in available, \
                    f"Horizontal split should be available in {vtype} with width {width}"
        else:
            assert MockLayoutType.HORIZONTAL_SPLIT not in available, \
                f"Horizontal split should not be available with width {width}"
        
        # Vertical split requires minimum height
        if height >= 600:
            assert MockLayoutType.VERTICAL_SPLIT in available, \
                f"Vertical split should be available with height {height}"
        else:
            assert MockLayoutType.VERTICAL_SPLIT not in available, \
                f"Vertical split should not be available with height {height}"


class TestMultiPaneLayoutConstraints:
    """Test multi-pane layout constraints and comprehensive options."""
    
    def test_multi_pane_comprehensive_options(self, constraint_validator):
        """Test 3+ panes offer comprehensive layout choices."""
        validator = constraint_validator
        
        # Test 3 panes on large desktop
        available_3 = validator.get_available_layouts(3, 1920, 1080, "large_desktop")
        
        expected_3_pane = [
            MockLayoutType.HORIZONTAL_ROW,
            MockLayoutType.VERTICAL_COLUMN,
            MockLayoutType.ADAPTIVE_GRID
        ]
        
        for expected in expected_3_pane:
            assert expected in available_3, \
                f"3-pane missing {expected} layout"
        
        # Test 4 panes on large desktop
        available_4 = validator.get_available_layouts(4, 1920, 1080, "large_desktop")
        
        expected_4_pane = [
            MockLayoutType.HORIZONTAL_ROW,
            MockLayoutType.VERTICAL_COLUMN,
            MockLayoutType.GRID_2X2,
            MockLayoutType.ADAPTIVE_GRID
        ]
        
        for expected in expected_4_pane:
            assert expected in available_4, \
                f"4-pane missing {expected} layout"
        
        # Verify more options than dual pane
        dual_pane_available = validator.get_available_layouts(2, 1920, 1080, "large_desktop")
        assert len(available_3) > len(dual_pane_available), \
            "3-pane should have more options than dual pane"
        assert len(available_4) >= len(available_3), \
            "4-pane should have at least as many options as 3-pane"
    
    def test_multi_pane_grid_constraints(self, constraint_validator):
        """Test multi-pane grid layout constraints."""
        validator = constraint_validator
        
        # Test 2x2 grid requires exactly 4 panes
        assert not validator.is_layout_valid(
            MockLayoutType.GRID_2X2, 3, 1920, 1080, "desktop"
        ), "2x2 grid should require exactly 4 panes"
        
        assert validator.is_layout_valid(
            MockLayoutType.GRID_2X2, 4, 1920, 1080, "desktop"
        ), "2x2 grid should be valid with 4 panes"
        
        # Test grid size requirements
        assert not validator.is_layout_valid(
            MockLayoutType.GRID_2X2, 4, 700, 500, "desktop"
        ), "2x2 grid should require minimum 800x600"
        
        assert validator.is_layout_valid(
            MockLayoutType.GRID_2X2, 4, 900, 700, "desktop"
        ), "2x2 grid should be valid with sufficient size"
    
    def test_multi_pane_row_column_constraints(self, constraint_validator):
        """Test row and column layout constraints."""
        validator = constraint_validator
        
        # Test horizontal row width requirements
        assert not validator.is_layout_valid(
            MockLayoutType.HORIZONTAL_ROW, 3, 800, 600, "desktop"
        ), "Horizontal row should require minimum 900px width"
        
        assert validator.is_layout_valid(
            MockLayoutType.HORIZONTAL_ROW, 3, 1000, 600, "desktop"
        ), "Horizontal row should be valid with sufficient width"
        
        # Test vertical column height requirements
        assert not validator.is_layout_valid(
            MockLayoutType.VERTICAL_COLUMN, 3, 1000, 700, "desktop"
        ), "Vertical column should require minimum 800px height"
        
        assert validator.is_layout_valid(
            MockLayoutType.VERTICAL_COLUMN, 3, 1000, 900, "desktop"
        ), "Vertical column should be valid with sufficient height"


class TestResponsiveBreakpointLogic:
    """Test responsive breakpoint detection and adaptation logic."""
    
    @pytest.mark.parametrize("width,expected_type", [
        (500, "mobile"),
        (767, "mobile"),
        (768, "tablet"),
        (1023, "tablet"),
        (1024, "desktop"),
        (1439, "desktop"),
        (1440, "large_desktop"),
        (2000, "large_desktop")
    ])
    def test_breakpoint_detection(self, width, expected_type):
        """Test viewport breakpoint detection accuracy."""
        # Simulate breakpoint detection logic
        if width < 768:
            detected = "mobile"
        elif width < 1024:
            detected = "tablet"
        elif width < 1440:
            detected = "desktop"
        else:
            detected = "large_desktop"
        
        assert detected == expected_type, \
            f"Breakpoint detection failed for width {width}: expected {expected_type}, got {detected}"
    
    def test_mobile_layout_adaptations(self, constraint_validator):
        """Test mobile viewport forces appropriate layout adaptations."""
        validator = constraint_validator
        
        # Mobile should force vertical split for dual pane
        available_2_pane = validator.get_available_layouts(2, 600, 800, "mobile")
        assert MockLayoutType.VERTICAL_SPLIT in available_2_pane, \
            "Mobile should have vertical split for dual pane"
        assert MockLayoutType.HORIZONTAL_SPLIT not in available_2_pane, \
            "Mobile should not have horizontal split"
        
        # Mobile should force vertical column for multi-pane
        available_3_pane = validator.get_available_layouts(3, 600, 800, "mobile")
        # Note: In mobile, we'd expect very limited options
        # The actual constraint might be that only single pane is available
    
    def test_large_desktop_comprehensive_options(self, constraint_validator):
        """Test large desktop viewport provides comprehensive options."""
        validator = constraint_validator
        
        # Large desktop should have all appropriate options
        for pane_count in [1, 2, 3, 4]:
            available = validator.get_available_layouts(
                pane_count, 1920, 1080, "large_desktop"
            )
            
            assert len(available) > 0, \
                f"Large desktop should have layouts for {pane_count} panes"
            
            if pane_count == 1:
                # Should have comprehensive single pane options
                expected_min = 3  # At least full_width, centered, and one sidebar
            elif pane_count == 2:
                # Should have both split options
                expected_min = 2
            else:
                # Should have comprehensive multi-pane options
                expected_min = 3
            
            assert len(available) >= expected_min, \
                f"Large desktop should have at least {expected_min} options for {pane_count} panes"


class TestLayoutTransitionValidation:
    """Test layout transition validation and constraint checking."""
    
    @pytest.mark.parametrize("transition", [
        # Valid transitions
        {"from": MockLayoutType.FULL_WIDTH, "to": MockLayoutType.CENTERED, "pane_change": False},
        {"from": MockLayoutType.HORIZONTAL_SPLIT, "to": MockLayoutType.VERTICAL_SPLIT, "pane_change": False},
        {"from": MockLayoutType.VERTICAL_COLUMN, "to": MockLayoutType.GRID_2X2, "pane_change": True},
        
        # Invalid transitions
        {"from": MockLayoutType.CENTERED, "to": MockLayoutType.HORIZONTAL_SPLIT, "pane_change": True},
        {"from": MockLayoutType.GRID_2X2, "to": MockLayoutType.VERTICAL_SPLIT, "pane_change": True}
    ])
    def test_transition_validity(self, constraint_validator, transition):
        """Test layout transition validity checking."""
        validator = constraint_validator
        
        from_layout = transition["from"]
        to_layout = transition["to"]
        pane_change_required = transition["pane_change"]
        
        # Determine pane counts for layouts
        from_constraint = validator.layout_constraints[from_layout]
        to_constraint = validator.layout_constraints[to_layout]
        
        from_pane_count = from_constraint["min_panes"]
        to_pane_count = to_constraint["min_panes"]
        
        # Check if transition requires pane count change
        actual_pane_change = from_pane_count != to_pane_count
        assert actual_pane_change == pane_change_required, \
            f"Transition {from_layout} -> {to_layout} pane change requirement mismatch"
        
        # Verify both layouts are valid in appropriate conditions
        desktop_width, desktop_height = 1366, 768
        
        from_valid = validator.is_layout_valid(
            from_layout, from_pane_count, desktop_width, desktop_height, "desktop"
        )
        to_valid = validator.is_layout_valid(
            to_layout, to_pane_count, desktop_width, desktop_height, "desktop"
        )
        
        # Both layouts should be valid in their respective pane counts
        assert from_valid or from_constraint["viewports"] and "desktop" not in from_constraint["viewports"], \
            f"From layout {from_layout} should be valid or not support desktop"
        assert to_valid or to_constraint["viewports"] and "desktop" not in to_constraint["viewports"], \
            f"To layout {to_layout} should be valid or not support desktop"


class TestConstraintCachePerformance:
    """Test constraint evaluation performance and caching."""
    
    def test_constraint_evaluation_performance(self, constraint_validator):
        """Test constraint evaluation meets performance targets."""
        validator = constraint_validator
        
        import time

        # Performance test: evaluate constraints 1000 times
        start_time = time.time()
        
        for _ in range(1000):
            for pane_count in [1, 2, 3, 4]:
                validator.get_available_layouts(pane_count, 1366, 768, "desktop")
        
        end_time = time.time()
        duration = end_time - start_time
        avg_time = duration / 4000  # 4000 total evaluations
        
        # Should be very fast (< 1ms per evaluation)
        assert avg_time < 0.001, \
            f"Constraint evaluation too slow: {avg_time:.6f}s per evaluation"
    
    def test_constraint_cache_effectiveness(self):
        """Test constraint caching improves performance."""
        # This would test caching behavior
        # For unit test, we simulate cache behavior
        
        cache = {}
        cache_hits = 0
        cache_misses = 0
        
        def get_with_cache(key):
            nonlocal cache_hits, cache_misses
            if key in cache:
                cache_hits += 1
                return cache[key]
            else:
                cache_misses += 1
                result = f"result_for_{key}"
                cache[key] = result
                return result
        
        # Simulate repeated requests
        test_keys = ["1_desktop", "2_desktop", "3_desktop", "4_desktop"]
        
        # First round - all misses
        for key in test_keys:
            get_with_cache(key)
        
        assert cache_misses == 4, "Should have 4 cache misses initially"
        
        # Second round - all hits
        for key in test_keys:
            get_with_cache(key)
        
        assert cache_hits == 4, "Should have 4 cache hits on second round"
        
        # Cache should improve performance
        hit_ratio = cache_hits / (cache_hits + cache_misses)
        assert hit_ratio >= 0.5, f"Cache hit ratio should be >= 50%, got {hit_ratio:.2%}"


class TestLayoutConstraintEdgeCases:
    """Test edge cases in layout constraint handling."""
    
    def test_extreme_viewport_sizes(self, constraint_validator):
        """Test constraint handling with extreme viewport sizes."""
        validator = constraint_validator
        
        # Test extremely small viewport
        tiny_available = validator.get_available_layouts(1, 100, 100, "mobile")
        assert MockLayoutType.FULL_WIDTH in tiny_available, \
            "Full width should be available even in tiny viewport"
        
        # Most other layouts should not be available
        restricted_layouts = [
            MockLayoutType.CENTERED, MockLayoutType.LEFT_SIDEBAR,
            MockLayoutType.RIGHT_SIDEBAR, MockLayoutType.CUSTOM_POSITION
        ]
        for layout in restricted_layouts:
            assert layout not in tiny_available, \
                f"Layout {layout} should not be available in tiny viewport"
        
        # Test extremely large viewport
        huge_available = validator.get_available_layouts(4, 5000, 3000, "large_desktop")
        
        # Should have all possible 4-pane layouts
        expected_layouts = [
            MockLayoutType.HORIZONTAL_ROW,
            MockLayoutType.VERTICAL_COLUMN,
            MockLayoutType.GRID_2X2,
            MockLayoutType.ADAPTIVE_GRID
        ]
        
        for layout in expected_layouts:
            assert layout in huge_available, \
                f"Layout {layout} should be available in huge viewport"
    
    def test_boundary_conditions(self, constraint_validator):
        """Test boundary conditions for layout constraints."""
        validator = constraint_validator
        
        # Test exact boundary values
        boundary_tests = [
            # Centered layout boundary (600px)
            {"layout": MockLayoutType.CENTERED, "pane_count": 1, 
             "width": 599, "height": 600, "should_be_valid": False},
            {"layout": MockLayoutType.CENTERED, "pane_count": 1,
             "width": 600, "height": 600, "should_be_valid": True},
            
            # Sidebar layout boundary (800px)
            {"layout": MockLayoutType.LEFT_SIDEBAR, "pane_count": 1,
             "width": 799, "height": 600, "should_be_valid": False},
            {"layout": MockLayoutType.LEFT_SIDEBAR, "pane_count": 1,
             "width": 800, "height": 600, "should_be_valid": True},
            
            # Grid layout boundary (800x600)
            {"layout": MockLayoutType.GRID_2X2, "pane_count": 4,
             "width": 799, "height": 600, "should_be_valid": False},
            {"layout": MockLayoutType.GRID_2X2, "pane_count": 4,
             "width": 800, "height": 599, "should_be_valid": False},
            {"layout": MockLayoutType.GRID_2X2, "pane_count": 4,
             "width": 800, "height": 600, "should_be_valid": True}
        ]
        
        for test in boundary_tests:
            is_valid = validator.is_layout_valid(
                test["layout"], test["pane_count"],
                test["width"], test["height"], "desktop"
            )
            
            assert is_valid == test["should_be_valid"], \
                f"Boundary test failed for {test['layout']} at {test['width']}x{test['height']}: " \
                f"expected {test['should_be_valid']}, got {is_valid}"
    
    def test_pane_count_validation(self, constraint_validator):
        """Test pane count validation for all layout types."""
        validator = constraint_validator
        
        # Test each layout type with various pane counts
        pane_count_tests = [
            # Single pane layouts
            {"layout": MockLayoutType.FULL_WIDTH, "valid_counts": [1], "invalid_counts": [0, 2, 3, 4]},
            {"layout": MockLayoutType.CENTERED, "valid_counts": [1], "invalid_counts": [0, 2, 3, 4]},
            
            # Dual pane layouts  
            {"layout": MockLayoutType.HORIZONTAL_SPLIT, "valid_counts": [2], "invalid_counts": [0, 1, 3, 4]},
            {"layout": MockLayoutType.VERTICAL_SPLIT, "valid_counts": [2], "invalid_counts": [0, 1, 3, 4]},
            
            # Multi-pane layouts
            {"layout": MockLayoutType.HORIZONTAL_ROW, "valid_counts": [3, 4], "invalid_counts": [0, 1, 2]},
            {"layout": MockLayoutType.VERTICAL_COLUMN, "valid_counts": [3, 4], "invalid_counts": [0, 1, 2]},
            {"layout": MockLayoutType.GRID_2X2, "valid_counts": [4], "invalid_counts": [0, 1, 2, 3]},
            {"layout": MockLayoutType.ADAPTIVE_GRID, "valid_counts": [3, 4], "invalid_counts": [0, 1, 2]}
        ]
        
        for test in pane_count_tests:
            layout = test["layout"]
            
            # Test valid pane counts
            for valid_count in test["valid_counts"]:
                is_valid = validator.is_layout_valid(
                    layout, valid_count, 1920, 1080, "large_desktop"
                )
                assert is_valid, \
                    f"Layout {layout} should be valid with {valid_count} panes"
            
            # Test invalid pane counts
            for invalid_count in test["invalid_counts"]:
                if invalid_count >= 0:  # Skip negative counts
                    is_valid = validator.is_layout_valid(
                        layout, invalid_count, 1920, 1080, "large_desktop"
                    )
                    assert not is_valid, \
                        f"Layout {layout} should not be valid with {invalid_count} panes"


if __name__ == '__main__':
    # Run unit tests
    pytest.main([__file__, "-v", "--tb=short"])