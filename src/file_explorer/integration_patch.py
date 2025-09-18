"""
Integration patch for multi_pane_explorer.py

This patch integrates the enhanced widget lifecycle manager and configuration manager
into the existing multi-pane explorer to resolve Qt widget deletion errors.

Key changes:
1. Replace direct widget manipulation with lifecycle-managed operations
2. Integrate enhanced configuration manager for QByteArray serialization
3. Add defensive programming for widget operations
4. Implement proper cleanup procedures

Author: RFU Development Team
Version: 2.0.0 (Enhanced Integration)
"""

# Enhanced configuration management
from src.file_explorer.core.enhanced_config_manager import \
    get_enhanced_config_manager
# Widget lifecycle management integration
from src.file_explorer.ui.widget_lifecycle_manager import (
    get_widget_lifecycle_manager, is_widget_valid, register_widget,
    safe_destroy_widget, safe_widget_operation)

# Add these imports to the top of multi_pane_explorer.py

def enhanced_remove_panes(self, count: int):
    """
    Enhanced pane removal with proper widget lifecycle management.
    
    This replaces the existing _remove_panes method.
    """
    try:
        for _ in range(count):
            if self.panes:
                pane = self.panes.pop()
                
                # Check if pane widget is still valid before operations
                pane_id = getattr(pane, '_lifecycle_id', None)
                
                if pane_id and is_widget_valid(pane_id):
                    # Use safe widget operation to set parent
                    def safe_set_parent(widget):
                        try:
                            widget.setParent(None)
                            return True
                        except RuntimeError as e:
                            if "wrapped C/C++ object" in str(e):
                                self.logger.warning(f"Widget already deleted: {e}")
                                return False
                            raise
                    
                    success = safe_widget_operation(pane_id, safe_set_parent)
                    if not success:
                        self.logger.warning(f"Failed to safely remove pane, widget may be deleted")
                    
                    # Destroy the widget through lifecycle manager
                    safe_destroy_widget(pane_id)
                else:
                    # Fallback for widgets not managed by lifecycle manager
                    try:
                        pane.setParent(None)
                        pane.deleteLater()
                    except RuntimeError as e:
                        if "wrapped C/C++ object" in str(e):
                            self.logger.warning(f"Widget already deleted during removal: {e}")
                        else:
                            raise
                            
        self.logger.debug(f"Successfully removed {count} panes")
        
    except Exception as e:
        self.logger.error(f"Error during pane removal: {e}")


def enhanced_update_pane_layout(self):
    """
    Enhanced pane layout update with safe widget operations.
    
    This replaces the existing _update_pane_layout method.
    """
    try:
        # Clear current splitter with safe operations
        widgets_to_remove = []
        for i in reversed(range(self.pane_splitter.count())):
            widget = self.pane_splitter.widget(i)
            if widget:
                widgets_to_remove.append(widget)
        
        # Safely remove widgets from splitter
        for widget in widgets_to_remove:
            try:
                widget.setParent(None)
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    self.logger.warning(f"Widget already deleted during layout update: {e}")
                else:
                    raise
        
        # Validate panes before adding to layout
        valid_panes = []
        for pane in self.panes:
            pane_id = getattr(pane, '_lifecycle_id', None)
            if pane_id and is_widget_valid(pane_id):
                valid_panes.append(pane)
            elif pane_id is None:
                # Pane not managed by lifecycle manager, check directly
                try:
                    # Test if widget is still valid by accessing a property
                    _ = pane.isVisible()
                    valid_panes.append(pane)
                except RuntimeError as e:
                    if "wrapped C/C++ object" in str(e):
                        self.logger.warning(f"Skipping deleted pane widget: {e}")
                        continue
                    raise
            else:
                self.logger.warning(f"Skipping invalid pane widget")
        
        # Update panes list to only include valid panes
        self.panes = valid_panes
        
        # Add valid panes based on layout mode and count
        if len(self.panes) == 1:
            self._safe_add_widget_to_splitter(self.panes[0])
        elif len(self.panes) == 2:
            for pane in self.panes:
                self._safe_add_widget_to_splitter(pane)
        elif len(self.panes) >= 3:
            # For 3+ panes, create nested splitters
            if self.layout_mode == 'horizontal':
                for pane in self.panes:
                    self._safe_add_widget_to_splitter(pane)
            else:  # vertical or grid
                # Implement grid layout for 4 panes
                self._enhanced_create_grid_layout()
        
        # Set equal sizes if we have valid panes
        if self.panes:
            sizes = [100] * len(self.panes)
            self.pane_splitter.setSizes(sizes)
            
        self.logger.debug(f"Successfully updated layout for {len(self.panes)} panes")
        
    except Exception as e:
        self.logger.error(f"Error during pane layout update: {e}")


def safe_add_widget_to_splitter(self, widget):
    """
    Safely add widget to splitter with validation.
    
    Args:
        widget: Widget to add to splitter
    """
    try:
        # Validate widget before adding
        widget_id = getattr(widget, '_lifecycle_id', None)
        
        if widget_id and is_widget_valid(widget_id):
            # Use safe widget operation
            def add_to_splitter(w):
                self.pane_splitter.addWidget(w)
                return True
            
            success = safe_widget_operation(widget_id, add_to_splitter)
            if not success:
                self.logger.warning("Failed to add widget to splitter through lifecycle manager")
        else:
            # Fallback for non-managed widgets
            try:
                # Test widget validity
                _ = widget.isVisible()
                self.pane_splitter.addWidget(widget)
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    self.logger.warning(f"Cannot add deleted widget to splitter: {e}")
                else:
                    raise
                    
    except Exception as e:
        self.logger.error(f"Error adding widget to splitter: {e}")


def enhanced_create_grid_layout(self):
    """
    Enhanced grid layout creation with safe widget operations.
    
    This replaces the existing _create_grid_layout method.
    """
    try:
        if len(self.panes) >= 4:
            # Validate all panes before creating grid
            valid_panes = []
            for pane in self.panes[:4]:  # Only use first 4 panes for grid
                pane_id = getattr(pane, '_lifecycle_id', None)
                if pane_id and is_widget_valid(pane_id):
                    valid_panes.append(pane)
                elif pane_id is None:
                    try:
                        _ = pane.isVisible()
                        valid_panes.append(pane)
                    except RuntimeError as e:
                        if "wrapped C/C++ object" not in str(e):
                            raise
                        self.logger.warning(f"Skipping deleted pane in grid layout: {e}")
            
            if len(valid_panes) >= 4:
                # Create 2x2 grid using nested splitters
                from PyQt5.QtCore import Qt
                from PyQt5.QtWidgets import QSplitter
                
                top_splitter = QSplitter(Qt.Horizontal)
                bottom_splitter = QSplitter(Qt.Horizontal)
                
                # Register splitters with lifecycle manager
                top_splitter_id = register_widget(top_splitter, "TopSplitter")
                bottom_splitter_id = register_widget(bottom_splitter, "BottomSplitter")
                
                # Safely add widgets to splitters
                try:
                    top_splitter.addWidget(valid_panes[0])
                    top_splitter.addWidget(valid_panes[1])
                    bottom_splitter.addWidget(valid_panes[2])
                    bottom_splitter.addWidget(valid_panes[3])
                    
                    self.pane_splitter.setOrientation(Qt.Vertical)
                    self.pane_splitter.addWidget(top_splitter)
                    self.pane_splitter.addWidget(bottom_splitter)
                    
                    self.logger.debug("Successfully created grid layout")
                    
                except RuntimeError as e:
                    if "wrapped C/C++ object" in str(e):
                        self.logger.warning(f"Widget deletion during grid creation: {e}")
                        # Clean up partially created splitters
                        safe_destroy_widget(top_splitter_id)
                        safe_destroy_widget(bottom_splitter_id)
                    else:
                        raise
            else:
                self.logger.warning(f"Insufficient valid panes for grid layout: {len(valid_panes)}")
                
    except Exception as e:
        self.logger.error(f"Error creating grid layout: {e}")


def enhanced_save_configuration(self):
    """
    Enhanced configuration saving with Qt object serialization support.
    
    This replaces the existing save_configuration method.
    """
    try:
        # Use enhanced config manager instead of regular config manager
        enhanced_config = get_enhanced_config_manager()
        
        # Save configuration with proper Qt object handling
        enhanced_config.set_setting('file_explorer', 'geometry', self.saveGeometry())
        enhanced_config.set_setting('file_explorer', 'pane_count', self.pane_count)
        enhanced_config.set_setting('file_explorer', 'layout_mode', self.layout_mode)
        
        # Save window state if available
        if hasattr(self, 'saveState'):
            enhanced_config.set_setting('file_explorer', 'window_state', self.saveState())
        
        # Save splitter state
        if hasattr(self, 'pane_splitter') and self.pane_splitter:
            try:
                splitter_state = self.pane_splitter.saveState()
                enhanced_config.set_setting('file_explorer', 'splitter_state', splitter_state)
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    self.logger.warning(f"Cannot save splitter state, widget deleted: {e}")
                else:
                    raise
        
        success = enhanced_config.save_config()
        if success:
            self.logger.debug("Configuration saved successfully")
        else:
            self.logger.warning("Configuration save failed")
            
    except Exception as e:
        self.logger.error(f"Error saving configuration: {e}")


def enhanced_cleanup(self):
    """
    Enhanced cleanup method for proper resource management.
    
    Add this method to the MultiPaneFileExplorer class.
    """
    try:
        self.logger.info("Starting enhanced cleanup")
        
        # Save configuration before cleanup
        try:
            self.enhanced_save_configuration()
        except Exception as e:
            self.logger.warning(f"Failed to save configuration during cleanup: {e}")
        
        # Clean up panes with lifecycle manager
        panes_to_cleanup = list(self.panes)
        for pane in panes_to_cleanup:
            pane_id = getattr(pane, '_lifecycle_id', None)
            if pane_id:
                safe_destroy_widget(pane_id)
            else:
                try:
                    pane.setParent(None)
                    pane.deleteLater()
                except RuntimeError as e:
                    if "wrapped C/C++ object" not in str(e):
                        raise
                    self.logger.warning(f"Widget already deleted during cleanup: {e}")
        
        self.panes.clear()
        
        # Clean up splitter
        if hasattr(self, 'pane_splitter') and self.pane_splitter:
            try:
                self.pane_splitter.setParent(None)
                self.pane_splitter.deleteLater()
            except RuntimeError as e:
                if "wrapped C/C++ object" not in str(e):
                    raise
                self.logger.warning(f"Splitter already deleted during cleanup: {e}")
        
        self.logger.info("Enhanced cleanup completed")
        
    except Exception as e:
        self.logger.error(f"Error during enhanced cleanup: {e}")


# Instructions for integration:
"""
To integrate these enhancements into multi_pane_explorer.py:

1. Add the imports at the top of the file
2. Replace the existing methods with their enhanced versions:
   - _remove_panes -> enhanced_remove_panes
   - _update_pane_layout -> enhanced_update_pane_layout
   - _create_grid_layout -> enhanced_create_grid_layout
   - save_configuration -> enhanced_save_configuration
   
3. Add the new methods:
   - _safe_add_widget_to_splitter -> safe_add_widget_to_splitter
   - enhanced_cleanup (add to __del__ or close methods)

4. Update pane creation to register widgets with lifecycle manager:
   In _create_pane method, add:
   pane._lifecycle_id = register_widget(pane, f"Pane_{len(self.panes)}")

5. Update config manager initialization:
   Replace: self.config_manager = get_config_manager()
   With: self.config_manager = get_enhanced_config_manager()
"""