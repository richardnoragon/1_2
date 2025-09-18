"""
Enhanced Layout Integration for Multi-Pane File Explorer

This module provides seamless integration between the responsive layout system
and the existing multi-pane file explorer, ensuring backward compatibility
while adding advanced responsive capabilities.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import (QComboBox, QHBoxLayout, QSplitter, QVBoxLayout,
                             QWidget)

from .responsive_layout_manager import (ContentHierarchyManager,
                                        LayoutImplementor, LayoutType,
                                        ResponsiveLayoutManager, ViewportType)


class EnhancedLayoutIntegration(QObject):
    """
    Integration layer between responsive layout system and multi-pane explorer.
    
    Provides backward compatibility while enabling advanced responsive features:
    - Seamless integration with existing pane management
    - Enhanced layout options based on pane count
    - Smooth transitions between layout modes
    - Content hierarchy preservation
    - Responsive breakpoint handling
    """
    
    # Signals for layout state changes
    layout_options_updated = pyqtSignal(list)  # Updated layout options
    layout_applied = pyqtSignal(str, dict)     # Layout applied successfully
    viewport_adapted = pyqtSignal(str, tuple)  # Viewport adaptation completed
    
    def __init__(self, main_explorer, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = logging.getLogger('RFU.EnhancedLayoutIntegration')
        self.main_explorer = main_explorer
        
        # Initialize responsive components
        self.layout_manager = ResponsiveLayoutManager(self)
        self.layout_implementor = LayoutImplementor(self.logger)
        self.hierarchy_manager = ContentHierarchyManager(self.logger)
        
        # Integration state
        self.is_responsive_mode = True
        self.legacy_layout_map = self._create_legacy_layout_mapping()
        
        # Connect signals
        self._connect_responsive_signals()
        
        # Override existing layout methods
        self._integrate_with_explorer()
        
        self.logger.info("Enhanced layout integration initialized")
    
    def _create_legacy_layout_mapping(self) -> Dict[str, LayoutType]:
        """Map legacy layout modes to new responsive layout types."""
        return {
            'horizontal': LayoutType.HORIZONTAL_SPLIT,
            'vertical': LayoutType.VERTICAL_SPLIT,
            'grid': LayoutType.ADAPTIVE_GRID,
            'single': LayoutType.FULL_WIDTH
        }
    
    def _connect_responsive_signals(self):
        """Connect responsive layout manager signals."""
        self.layout_manager.layout_changed.connect(self._on_layout_changed)
        self.layout_manager.viewport_changed.connect(self._on_viewport_changed)
        self.layout_manager.constraint_updated.connect(
            self._on_constraints_updated
        )
    
    def _integrate_with_explorer(self):
        """Integrate responsive system with existing explorer methods."""
        # Store original methods
        self.main_explorer._original_update_pane_layout = (
            self.main_explorer._update_pane_layout
        )
        self.main_explorer._original_validate_and_update_layout = (
            self.main_explorer._validate_and_update_layout
        )
        
        # Override with enhanced versions
        self.main_explorer._update_pane_layout = self._enhanced_update_pane_layout
        self.main_explorer._validate_and_update_layout = (
            self._enhanced_validate_and_update_layout
        )
        
        # Add new methods to explorer
        self.main_explorer.get_available_layout_options = (
            self.get_available_layout_options
        )
        self.main_explorer.apply_responsive_layout = self.apply_responsive_layout
        self.main_explorer.get_layout_recommendations = (
            self.get_layout_recommendations
        )
    
    def _enhanced_update_pane_layout(self):
        """Enhanced version of pane layout update with responsive features."""
        try:
            # Update responsive manager with current state
            self.layout_manager.set_pane_count(len(self.main_explorer.panes))
            self.layout_manager.container_widget = (
                self.main_explorer.pane_splitter
            )
            
            # Get current layout mode and map to responsive type
            current_mode = getattr(self.main_explorer, 'layout_mode', 'horizontal')
            responsive_layout = self.legacy_layout_map.get(
                current_mode, LayoutType.HORIZONTAL_SPLIT
            )
            
            # Apply responsive layout
            if self.is_responsive_mode:
                success = self._apply_responsive_layout_internal(
                    responsive_layout, self.main_explorer.panes
                )
                if success:
                    return
            
            # Fallback to original method
            self.main_explorer._original_update_pane_layout()
            
        except Exception as e:
            self.logger.error(f"Enhanced layout update failed: {e}")
            # Fallback to original implementation
            self.main_explorer._original_update_pane_layout()
    
    def _enhanced_validate_and_update_layout(self):
        """Enhanced layout validation with responsive constraints."""
        try:
            pane_count = getattr(self.main_explorer, 'pane_count', 2)
            current_mode = getattr(self.main_explorer, 'layout_mode', 'horizontal')
            
            # Get available layouts for current pane count
            available = self.get_available_layout_options(pane_count)
            
            # Check if current mode is available
            current_responsive = self.legacy_layout_map.get(current_mode)
            if current_responsive and current_responsive in [opt[0] for opt in available]:
                # Current layout is valid
                return
            
            # Switch to recommended layout
            if available:
                recommended = available[0][0]  # First available layout
                legacy_mode = self._responsive_to_legacy_mode(recommended)
                if legacy_mode:
                    self.main_explorer.layout_mode = legacy_mode
                    self.logger.info(
                        f"Layout auto-adjusted to {legacy_mode} for {pane_count} panes"
                    )
            
            # Update layout combo if it exists
            if hasattr(self.main_explorer, 'layout_combo'):
                self._update_legacy_layout_combo()
        
        except Exception as e:
            self.logger.error(f"Enhanced layout validation failed: {e}")
            # Fallback to original method
            self.main_explorer._original_validate_and_update_layout()
    
    def get_available_layout_options(
            self, pane_count: Optional[int] = None
    ) -> List[tuple]:
        """
        Get available layout options for current or specified pane count.
        
        Returns:
            List of (LayoutType, display_name) tuples
        """
        if pane_count is None:
            pane_count = len(getattr(self.main_explorer, 'panes', []))
        
        return self.layout_manager.get_layout_display_names(pane_count)
    
    def apply_responsive_layout(self, layout_type: LayoutType, 
                              animate: bool = True) -> bool:
        """Apply responsive layout with full integration."""
        try:
            panes = getattr(self.main_explorer, 'panes', [])
            if not panes:
                self.logger.warning("No panes available for layout application")
                return False
            
            return self._apply_responsive_layout_internal(
                layout_type, panes, animate
            )
            
        except Exception as e:
            self.logger.error(f"Failed to apply responsive layout: {e}")
            return False
    
    def _apply_responsive_layout_internal(
            self, layout_type: LayoutType, panes: List[QWidget],
            animate: bool = True
    ) -> bool:
        """Internal method to apply responsive layout."""
        try:
            container = self.main_explorer.pane_splitter
            if not container:
                self.logger.error("No pane splitter container available")
                return False
            
            # Capture content hierarchy
            snapshot_id = ""
            if animate and self.hierarchy_manager.hierarchy_enabled:
                snapshot_id = self.hierarchy_manager.capture_content_hierarchy(
                    panes, self.layout_manager.current_layout or layout_type
                )
            
            # Apply the layout through the manager
            success = self.layout_manager.apply_layout(
                layout_type, container, animate
            )
            
            if success:
                # Implement the actual layout
                config = self.layout_manager.layout_configs[layout_type]
                
                if len(panes) == 1:
                    self.layout_implementor.implement_single_pane_layout(
                        container, panes, layout_type, config
                    )
                elif len(panes) == 2:
                    self.layout_implementor.implement_dual_pane_layout(
                        container, panes, layout_type, config
                    )
                else:
                    self.layout_implementor.implement_multi_pane_layout(
                        container, panes, layout_type, config
                    )
                
                # Restore content hierarchy
                if snapshot_id:
                    self.hierarchy_manager.restore_content_hierarchy(
                        snapshot_id, panes, layout_type
                    )
                
                # Update legacy layout mode
                legacy_mode = self._responsive_to_legacy_mode(layout_type)
                if legacy_mode:
                    self.main_explorer.layout_mode = legacy_mode
            
            return success
            
        except Exception as e:
            self.logger.error(f"Internal layout application failed: {e}")
            return False
    
    def get_layout_recommendations(self, pane_count: int) -> Dict[str, Any]:
        """Get layout recommendations for the specified pane count."""
        try:
            available = self.layout_manager.get_available_layouts(pane_count)
            recommended = self.layout_manager.get_recommended_layout(pane_count)
            
            return {
                'pane_count': pane_count,
                'available_layouts': [
                    {
                        'type': lt.value,
                        'display_name': self.layout_manager.layout_configs[lt].display_name,
                        'description': self.layout_manager.layout_configs[lt].description
                    }
                    for lt in available
                ],
                'recommended': {
                    'type': recommended.value,
                    'display_name': self.layout_manager.layout_configs[recommended].display_name
                } if recommended else None,
                'viewport_info': self.layout_manager.get_viewport_info()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting layout recommendations: {e}")
            return {'error': str(e)}
    
    def _responsive_to_legacy_mode(self, layout_type: LayoutType) -> Optional[str]:
        """Convert responsive layout type to legacy mode string."""
        reverse_map = {
            LayoutType.FULL_WIDTH: 'single',
            LayoutType.CENTERED: 'single',
            LayoutType.LEFT_SIDEBAR: 'single',
            LayoutType.RIGHT_SIDEBAR: 'single',
            LayoutType.CUSTOM_POSITION: 'single',
            LayoutType.HORIZONTAL_SPLIT: 'horizontal',
            LayoutType.VERTICAL_SPLIT: 'vertical',
            LayoutType.HORIZONTAL_ROW: 'horizontal',
            LayoutType.VERTICAL_COLUMN: 'vertical',
            LayoutType.GRID_2X2: 'grid',
            LayoutType.GRID_2X3: 'grid',
            LayoutType.ADAPTIVE_GRID: 'grid'
        }
        return reverse_map.get(layout_type)
    
    def _update_legacy_layout_combo(self):
        """Update the legacy layout combo with enhanced options."""
        try:
            if not hasattr(self.main_explorer, 'layout_combo'):
                return
            
            layout_combo = self.main_explorer.layout_combo
            if not layout_combo:
                return
            
            # Get current responsive options
            pane_count = len(getattr(self.main_explorer, 'panes', []))
            available = self.get_available_layout_options(pane_count)
            
            # Update combo box
            current_text = layout_combo.currentText()
            layout_combo.clear()
            
            if not available:
                layout_combo.addItem("Single View")
                layout_combo.setEnabled(False)
                layout_combo.setToolTip("No layout options for single pane")
            else:
                layout_combo.setEnabled(True)
                layout_combo.setToolTip("Select responsive layout arrangement")
                
                for layout_type, display_name in available:
                    layout_combo.addItem(display_name)
                    layout_combo.setItemData(
                        layout_combo.count() - 1, layout_type.value
                    )
                
                # Try to restore previous selection
                index = layout_combo.findText(current_text)
                if index >= 0:
                    layout_combo.setCurrentIndex(index)
        
        except Exception as e:
            self.logger.error(f"Error updating legacy layout combo: {e}")
    
    def _on_layout_changed(self, layout_type: LayoutType, info: Dict[str, Any]):
        """Handle layout change from responsive manager."""
        self.layout_applied.emit(layout_type.value, info)
        self.logger.info(f"Responsive layout applied: {info['display_name']}")
    
    def _on_viewport_changed(self, viewport_type: ViewportType, size: tuple):
        """Handle viewport change from responsive manager."""
        self.viewport_adapted.emit(viewport_type.value, size)
        
        # Update layout options for new viewport
        pane_count = len(getattr(self.main_explorer, 'panes', []))
        self._update_layout_options_for_viewport(pane_count, viewport_type)
    
    def _on_constraints_updated(self, pane_count: int, available_layouts: List):
        """Handle constraint updates from responsive manager."""
        # Convert to display format
        options = [(lt, self.layout_manager.layout_configs[lt].display_name) 
                  for lt in available_layouts]
        self.layout_options_updated.emit(options)
        
        # Update legacy combo
        self._update_legacy_layout_combo()
    
    def _update_layout_options_for_viewport(self, pane_count: int, 
                                          viewport_type: ViewportType):
        """Update layout options when viewport changes."""
        try:
            # Get new available layouts
            available = self.layout_manager.get_available_layouts(
                pane_count, viewport_type
            )
            
            # Check if current layout is still valid
            current_layout = getattr(self.main_explorer, 'layout_mode', 'horizontal')
            current_responsive = self.legacy_layout_map.get(current_layout)
            
            if current_responsive and current_responsive not in available:
                # Auto-switch to recommended layout
                recommended = self.layout_manager.get_recommended_layout(pane_count)
                if recommended:
                    new_legacy_mode = self._responsive_to_legacy_mode(recommended)
                    if new_legacy_mode:
                        self.main_explorer.layout_mode = new_legacy_mode
                        self._enhanced_update_pane_layout()
            
            # Update UI options
            self._update_legacy_layout_combo()
            
        except Exception as e:
            self.logger.error(f"Error updating layout options for viewport: {e}")
    
    def enhance_pane_count_change(self, new_count: int):
        """Enhanced pane count change with responsive layout validation."""
        try:
            # Update responsive manager
            self.layout_manager.set_pane_count(new_count)
            
            # Get available layouts for new count
            available = self.layout_manager.get_available_layouts(new_count)
            
            # Validate current layout
            current_mode = getattr(self.main_explorer, 'layout_mode', 'horizontal')
            current_responsive = self.legacy_layout_map.get(current_mode)
            
            if current_responsive and current_responsive not in available:
                # Switch to recommended layout
                recommended = self.layout_manager.get_recommended_layout(new_count)
                if recommended:
                    new_legacy_mode = self._responsive_to_legacy_mode(recommended)
                    if new_legacy_mode:
                        self.main_explorer.layout_mode = new_legacy_mode
                        self.logger.info(
                            f"Auto-switched layout to {new_legacy_mode} for "
                            f"{new_count} panes"
                        )
            
            # Update UI
            self._update_legacy_layout_combo()
            
        except Exception as e:
            self.logger.error(f"Enhanced pane count change failed: {e}")
    
    def enhance_layout_mode_change(self, new_mode: str):
        """Enhanced layout mode change with responsive validation."""
        try:
            # Map to responsive layout type
            responsive_layout = self.legacy_layout_map.get(new_mode.lower())
            if not responsive_layout:
                self.logger.warning(f"Unknown layout mode: {new_mode}")
                return False
            
            # Check if layout is available
            pane_count = len(getattr(self.main_explorer, 'panes', []))
            available = self.layout_manager.get_available_layouts(pane_count)
            
            if responsive_layout not in available:
                self.logger.warning(
                    f"Layout {new_mode} not available for {pane_count} panes"
                )
                return False
            
            # Apply responsive layout
            return self.apply_responsive_layout(responsive_layout)
            
        except Exception as e:
            self.logger.error(f"Enhanced layout mode change failed: {e}")
            return False
    
    def apply_responsive_layout(self, layout_type: LayoutType, 
                              animate: bool = True) -> bool:
        """Apply responsive layout with full feature integration."""
        try:
            panes = getattr(self.main_explorer, 'panes', [])
            container = getattr(self.main_explorer, 'pane_splitter', None)
            
            if not panes or not container:
                self.logger.error("Missing panes or container for layout application")
                return False
            
            # Capture content hierarchy if animation is enabled
            snapshot_id = ""
            if animate and self.hierarchy_manager.hierarchy_enabled:
                current_layout = self.layout_manager.current_layout
                snapshot_id = self.hierarchy_manager.capture_content_hierarchy(
                    panes, current_layout or layout_type
                )
            
            # Clear existing splitter content
            self._clear_splitter_widgets(container)
            
            # Apply the responsive layout
            config = self.layout_manager.layout_configs[layout_type]
            success = False
            
            if len(panes) == 1:
                success = self.layout_implementor.implement_single_pane_layout(
                    container, panes, layout_type, config
                )
            elif len(panes) == 2:
                success = self.layout_implementor.implement_dual_pane_layout(
                    container, panes, layout_type, config
                )
            else:
                success = self.layout_implementor.implement_multi_pane_layout(
                    container, panes, layout_type, config
                )
            
            if success:
                # Update layout manager state
                self.layout_manager.current_layout = layout_type
                
                # Restore content hierarchy
                if snapshot_id:
                    self.hierarchy_manager.restore_content_hierarchy(
                        snapshot_id, panes, layout_type
                    )
                
                # Update legacy mode
                legacy_mode = self._responsive_to_legacy_mode(layout_type)
                if legacy_mode:
                    self.main_explorer.layout_mode = legacy_mode
                
                self.logger.info(f"Applied responsive layout: {layout_type.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Responsive layout application failed: {e}")
            return False
    
    def _clear_splitter_widgets(self, splitter):
        """Safely clear all widgets from splitter."""
        try:
            if hasattr(splitter, 'count'):
                # QSplitter
                for i in reversed(range(splitter.count())):
                    widget = splitter.widget(i)
                    if widget:
                        widget.setParent(None)
            elif hasattr(splitter, 'layout'):
                # QWidget with layout
                layout = splitter.layout()
                if layout:
                    while layout.count():
                        child = layout.takeAt(0)
                        if child.widget():
                            child.widget().setParent(None)
                            
        except Exception as e:
            self.logger.warning(f"Error clearing splitter widgets: {e}")
    
    def _responsive_to_legacy_mode(self, layout_type: LayoutType) -> Optional[str]:
        """Convert responsive layout type back to legacy mode."""
        reverse_map = {
            LayoutType.FULL_WIDTH: 'single',
            LayoutType.CENTERED: 'single',
            LayoutType.LEFT_SIDEBAR: 'single',
            LayoutType.RIGHT_SIDEBAR: 'single',
            LayoutType.CUSTOM_POSITION: 'single',
            LayoutType.HORIZONTAL_SPLIT: 'horizontal',
            LayoutType.VERTICAL_SPLIT: 'vertical',
            LayoutType.HORIZONTAL_ROW: 'horizontal',
            LayoutType.VERTICAL_COLUMN: 'vertical',
            LayoutType.GRID_2X2: 'grid',
            LayoutType.GRID_2X3: 'grid',
            LayoutType.ADAPTIVE_GRID: 'grid'
        }
        return reverse_map.get(layout_type)
    
    def get_current_responsive_layout(self) -> Optional[LayoutType]:
        """Get current layout as responsive layout type."""
        current_mode = getattr(self.main_explorer, 'layout_mode', 'horizontal')
        return self.legacy_layout_map.get(current_mode)
    
    def enable_responsive_mode(self, enabled: bool = True):
        """Enable or disable responsive layout mode."""
        self.is_responsive_mode = enabled
        self.hierarchy_manager.enable_hierarchy_preservation(enabled)
        
        status = 'enabled' if enabled else 'disabled'
        self.logger.info(f"Responsive layout mode {status}")
    
    def get_responsive_status(self) -> Dict[str, Any]:
        """Get comprehensive responsive layout system status."""
        try:
            current_layout = self.get_current_responsive_layout()
            pane_count = len(getattr(self.main_explorer, 'panes', []))
            
            return {
                'responsive_enabled': self.is_responsive_mode,
                'hierarchy_enabled': self.hierarchy_manager.hierarchy_enabled,
                'current_layout': {
                    'type': current_layout.value if current_layout else None,
                    'display_name': (
                        self.layout_manager.layout_configs[current_layout].display_name
                        if current_layout else None
                    )
                },
                'pane_count': pane_count,
                'viewport_info': self.layout_manager.get_viewport_info(),
                'available_layouts': len(
                    self.layout_manager.get_available_layouts(pane_count)
                ),
                'recommendations': self.get_layout_recommendations(pane_count)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting responsive status: {e}")
            return {'error': str(e)}
    
    def handle_window_resize(self, width: int, height: int):
        """Handle window resize events for responsive adaptation."""
        try:
            # Update viewport information
            self.layout_manager._update_viewport_info_from_geometry(width, height)
            
            # Check if layout needs adjustment
            current_layout = self.get_current_responsive_layout()
            if current_layout:
                pane_count = len(getattr(self.main_explorer, 'panes', []))
                available = self.layout_manager.get_available_layouts(pane_count)
                
                if current_layout not in available:
                    # Auto-switch to appropriate layout
                    recommended = self.layout_manager.get_recommended_layout(pane_count)
                    if recommended:
                        self.apply_responsive_layout(recommended, animate=True)
            
        except Exception as e:
            self.logger.error(f"Error handling window resize: {e}")


def create_enhanced_layout_integration(main_explorer) -> EnhancedLayoutIntegration:
    """
    Factory function to create enhanced layout integration.
    
    Args:
        main_explorer: Main multi-pane explorer instance
        
    Returns:
        Configured EnhancedLayoutIntegration instance
    """
    try:
        integration = EnhancedLayoutIntegration(main_explorer)
        
        # Override resize event in main explorer
        original_resize_event = main_explorer.resizeEvent
        
        def enhanced_resize_event(event):
            # Call original resize event
            original_resize_event(event)
            
            # Handle responsive layout adaptation
            size = event.size()
            integration.handle_window_resize(size.width(), size.height())
        
        main_explorer.resizeEvent = enhanced_resize_event
        
        return integration
        
    except Exception as e:
        logger = logging.getLogger('RFU.EnhancedLayoutIntegration')
        logger.error(f"Failed to create enhanced layout integration: {e}")
        raise