"""
Enhanced Multi-Pane File Explorer with Responsive Layout System

This module provides an advanced multi-pane file explorer that integrates
the sophisticated responsive layout system, providing dynamic layout options
based on pane count, viewport size, and user preferences.

Features:
- Dynamic layout constraints based on pane count
- Responsive breakpoint adaptation
- Smooth layout transitions with content preservation
- Enterprise-grade architecture with comprehensive error handling
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
                             QLabel, QMainWindow, QMessageBox, QPushButton,
                             QSplitter, QVBoxLayout, QWidget)

# Import responsive layout system
try:
    from .ui.enhanced_layout_integration import EnhancedLayoutIntegration
    from .ui.layout_implementations import (ContentHierarchyPreserver,
                                            DualPaneLayoutImplementor,
                                            LayoutTransitionManager,
                                            LayoutValidationEngine,
                                            MultiPaneLayoutImplementor,
                                            ResponsiveBreakpointHandler,
                                            SinglePaneLayoutImplementor)
    from .ui.responsive_layout_manager import (LayoutType,
                                               ResponsiveLayoutManager,
                                               ViewportType)
    RESPONSIVE_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Responsive layout imports not available: {e}")
    RESPONSIVE_IMPORTS_AVAILABLE = False


class EnhancedMultiPaneExplorer(QMainWindow):
    """
    Enhanced multi-pane file explorer with sophisticated responsive layout system.
    
    Provides dynamic layout management with:
    - Single pane: Unrestricted layout flexibility
    - Dual pane: Optimized horizontal/vertical arrangements
    - 3+ panes: Comprehensive grid and row layouts with responsive breakpoints
    - Seamless transitions with content hierarchy preservation
    """
    
    # Signals for layout events
    layout_changed = pyqtSignal(str, dict)
    pane_count_changed = pyqtSignal(int)
    viewport_adapted = pyqtSignal(str, tuple)
    layout_transition_completed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('RFU.EnhancedMultiPaneExplorer')
        
        # Core state
        self.panes: List[QWidget] = []
        self.active_pane_index = 0
        self.current_layout_type: Optional[LayoutType] = None
        
        # Responsive layout components
        self.responsive_enabled = RESPONSIVE_IMPORTS_AVAILABLE
        if self.responsive_enabled:
            self._initialize_responsive_components()
        
        # UI components
        self.central_widget = None
        self.pane_container = None
        self.toolbar_frame = None
        self.status_frame = None
        
        # Layout controls
        self.pane_count_combo = None
        self.layout_combo = None
        self.layout_info_label = None
        
        # Setup UI
        self._setup_window()
        self._setup_ui()
        self._setup_default_panes()
        
        # Start with responsive layout if available
        if self.responsive_enabled:
            self._apply_initial_responsive_layout()
        
        self.logger.info("Enhanced Multi-Pane Explorer initialized")
    
    def _initialize_responsive_components(self):
        """Initialize responsive layout system components."""
        try:
            self.layout_manager = ResponsiveLayoutManager(self)
            self.single_pane_implementor = SinglePaneLayoutImplementor(self.logger)
            self.dual_pane_implementor = DualPaneLayoutImplementor(self.logger)
            self.multi_pane_implementor = MultiPaneLayoutImplementor(self.logger)
            self.transition_manager = LayoutTransitionManager(self.logger)
            self.breakpoint_handler = ResponsiveBreakpointHandler(self.logger)
            self.hierarchy_preserver = ContentHierarchyPreserver(self.logger)
            self.validation_engine = LayoutValidationEngine(self.logger)
            
            # Connect responsive signals
            self._connect_responsive_signals()
            
            self.logger.info("Responsive layout components initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize responsive components: {e}")
            self.responsive_enabled = False
    
    def _connect_responsive_signals(self):
        """Connect signals from responsive layout system."""
        if not self.responsive_enabled:
            return
        
        try:
            self.layout_manager.layout_changed.connect(self._on_responsive_layout_changed)
            self.layout_manager.viewport_changed.connect(self._on_viewport_changed)
            self.layout_manager.constraint_updated.connect(self._on_constraints_updated)
            self.layout_manager.transition_started.connect(self._on_transition_started)
            self.layout_manager.transition_completed.connect(self._on_transition_completed)
            
        except Exception as e:
            self.logger.error(f"Error connecting responsive signals: {e}")
    
    def _setup_window(self):
        """Setup main window properties."""
        self.setWindowTitle("Enhanced Multi-Pane File Explorer")
        self.setMinimumSize(600, 400)
        self.resize(1200, 800)
        
        # Enable responsive behavior
        self.setAttribute(Qt.WA_Hover, True)
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Setup toolbar
        self._setup_enhanced_toolbar(main_layout)
        
        # Setup pane container
        self._setup_pane_container(main_layout)
        
        # Setup status bar
        self._setup_enhanced_status_bar(main_layout)
    
    def _setup_enhanced_toolbar(self, parent_layout):
        """Setup enhanced toolbar with responsive layout controls."""
        self.toolbar_frame = QFrame()
        self.toolbar_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        
        toolbar_layout = QHBoxLayout(self.toolbar_frame)
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar_layout.setSpacing(10)
        
        # Pane count control
        toolbar_layout.addWidget(QLabel("Panes:"))
        self.pane_count_combo = QComboBox()
        self.pane_count_combo.addItems(['1', '2', '3', '4'])
        self.pane_count_combo.setCurrentText('2')  # Default to 2 panes
        self.pane_count_combo.currentTextChanged.connect(self._on_pane_count_changed)
        toolbar_layout.addWidget(self.pane_count_combo)
        
        # Layout selection control
        toolbar_layout.addWidget(QLabel("Layout:"))
        self.layout_combo = QComboBox()
        self.layout_combo.currentTextChanged.connect(self._on_layout_changed)
        toolbar_layout.addWidget(self.layout_combo)
        
        # Layout info display
        self.layout_info_label = QLabel("Ready")
        self.layout_info_label.setStyleSheet("color: #666; font-style: italic;")
        toolbar_layout.addWidget(self.layout_info_label)
        
        toolbar_layout.addStretch()
        
        # Responsive mode toggle
        if self.responsive_enabled:
            responsive_btn = QPushButton("Responsive Mode: ON")
            responsive_btn.setCheckable(True)
            responsive_btn.setChecked(True)
            responsive_btn.clicked.connect(self._toggle_responsive_mode)
            toolbar_layout.addWidget(responsive_btn)
            self.responsive_toggle_btn = responsive_btn
        
        parent_layout.addWidget(self.toolbar_frame)
    
    def _setup_pane_container(self, parent_layout):
        """Setup the main pane container."""
        # Create pane container as a splitter for flexibility
        self.pane_container = QSplitter(Qt.Horizontal)
        self.pane_container.setChildrenCollapsible(False)
        
        # Style the container
        self.pane_container.setStyleSheet("""
            QSplitter {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
            }
            QSplitter::handle {
                background-color: #ccc;
                width: 3px;
                height: 3px;
            }
            QSplitter::handle:hover {
                background-color: #007ACC;
            }
        """)
        
        parent_layout.addWidget(self.pane_container, 1)  # Give it stretch factor
    
    def _setup_enhanced_status_bar(self, parent_layout):
        """Setup enhanced status bar."""
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(10, 3, 10, 3)
        
        # Status labels
        self.status_label = QLabel("Ready")
        self.viewport_label = QLabel("Viewport: Desktop")
        self.layout_status_label = QLabel("Layout: Default")
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.viewport_label)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.layout_status_label)
        
        parent_layout.addWidget(self.status_frame)
    
    def _setup_default_panes(self):
        """Setup default pane configuration."""
        # Start with 2 panes by default
        self.set_pane_count(2)
    
    def set_pane_count(self, count: int):
        """Set the number of panes with responsive layout management."""
        if not 1 <= count <= 4:
            self.logger.warning(f"Invalid pane count: {count}")
            return
        
        try:
            old_count = len(self.panes)
            
            # Adjust panes
            if count > old_count:
                self._add_panes(count - old_count)
            elif count < old_count:
                self._remove_panes(old_count - count)
            
            # Update responsive layout manager
            if self.responsive_enabled:
                self.layout_manager.set_pane_count(count)
                self._update_layout_options()
                
                # Apply recommended layout
                recommended = self.layout_manager.get_recommended_layout(count)
                if recommended:
                    self._apply_responsive_layout(recommended, animate=True)
            else:
                # Fallback to simple layout
                self._apply_simple_layout(count)
            
            # Update UI
            self.pane_count_combo.setCurrentText(str(count))
            self._update_status_display()
            
            # Emit signal
            self.pane_count_changed.emit(count)
            
            self.logger.info(f"Pane count changed from {old_count} to {count}")
            
        except Exception as e:
            self.logger.error(f"Error setting pane count: {e}")
    
    def _add_panes(self, count: int):
        """Add new panes to the explorer."""
        for i in range(count):
            try:
                pane_number = len(self.panes) + 1
                pane = self._create_file_explorer_pane(pane_number)
                self.panes.append(pane)
                
                self.logger.debug(f"Added pane {pane_number}")
                
            except Exception as e:
                self.logger.error(f"Error adding pane: {e}")
    
    def _remove_panes(self, count: int):
        """Remove excess panes."""
        for _ in range(count):
            if self.panes:
                pane = self.panes.pop()
                try:
                    pane.setParent(None)
                    pane.deleteLater()
                except Exception as e:
                    self.logger.warning(f"Error removing pane: {e}")
    
    def _create_file_explorer_pane(self, pane_number: int) -> QWidget:
        """Create a file explorer pane widget."""
        pane = QFrame()
        pane.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        pane.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #007ACC;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel(f"File Explorer Pane {pane_number}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                background-color: #007ACC;
                color: white;
                border-radius: 3px;
            }
        """)
        layout.addWidget(title_label)
        
        # Path info
        path_label = QLabel(f"Path: {Path.home()}")
        path_label.setStyleSheet("font-family: monospace; padding: 5px;")
        layout.addWidget(path_label)
        
        # Content area placeholder
        content_label = QLabel("File List Content")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px dashed #ccc;
                padding: 20px;
                color: #666;
            }
        """)
        layout.addWidget(content_label, 1)
        
        # Store references for responsive layout
        pane._current_path = Path.home()
        pane._pane_number = pane_number
        pane._title_label = title_label
        pane._path_label = path_label
        pane._content_label = content_label
        
        return pane
    
    def _apply_responsive_layout(self, layout_type: LayoutType, animate: bool = True):
        """Apply responsive layout with full feature integration."""
        if not self.responsive_enabled:
            self._apply_simple_layout(len(self.panes))
            return
        
        try:
            # Validate layout application
            is_valid, error_msg = self.validation_engine.validate_layout_application(
                layout_type, len(self.panes), 
                self.layout_manager.viewport_size,
                self.pane_container
            )
            
            if not is_valid:
                self.logger.warning(f"Layout validation failed: {error_msg}")
                return
            
            # Capture content hierarchy if animation enabled
            snapshot_id = ""
            if animate:
                snapshot_id = self.hierarchy_preserver.capture_hierarchy_state(
                    self.panes, layout_type.value
                )
            
            # Clear current container layout
            self._clear_pane_container()
            
            # Apply appropriate implementation
            success = False
            config = self.layout_manager.layout_configs[layout_type]
            
            if len(self.panes) == 1:
                success = self._apply_single_pane_responsive_layout(
                    layout_type, config, animate
                )
            elif len(self.panes) == 2:
                success = self._apply_dual_pane_responsive_layout(
                    layout_type, config, animate
                )
            else:
                success = self._apply_multi_pane_responsive_layout(
                    layout_type, config, animate
                )
            
            if success:
                # Update state
                self.current_layout_type = layout_type
                self.layout_manager.current_layout = layout_type
                
                # Restore content hierarchy
                if snapshot_id:
                    self.hierarchy_preserver.restore_hierarchy_state(
                        snapshot_id, self.panes
                    )
                
                # Update UI
                self._update_layout_combo_selection(layout_type)
                self._update_status_display()
                
                # Emit signals
                layout_info = self.layout_manager._get_layout_info(layout_type)
                self.layout_changed.emit(layout_type.value, layout_info)
                
                if animate:
                    self.layout_transition_completed.emit(layout_type.value)
                
                self.logger.info(f"Applied responsive layout: {layout_type.value}")
            
        except Exception as e:
            self.logger.error(f"Error applying responsive layout: {e}")
    
    def _apply_single_pane_responsive_layout(self, layout_type: LayoutType,
                                           config, animate: bool) -> bool:
        """Apply single pane responsive layout."""
        if len(self.panes) != 1:
            return False
        
        pane = self.panes[0]
        
        if layout_type == LayoutType.FULL_WIDTH:
            return self.single_pane_implementor.implement_full_width(
                self.pane_container, pane, config
            )
        elif layout_type == LayoutType.CENTERED:
            return self.single_pane_implementor.implement_centered(
                self.pane_container, pane, config
            )
        elif layout_type == LayoutType.LEFT_SIDEBAR:
            return self.single_pane_implementor.implement_sidebar(
                self.pane_container, pane, config, 'left'
            )
        elif layout_type == LayoutType.RIGHT_SIDEBAR:
            return self.single_pane_implementor.implement_sidebar(
                self.pane_container, pane, config, 'right'
            )
        elif layout_type == LayoutType.CUSTOM_POSITION:
            return self.single_pane_implementor.implement_custom_position(
                self.pane_container, pane, config
            )
        
        return False
    
    def _apply_dual_pane_responsive_layout(self, layout_type: LayoutType,
                                         config, animate: bool) -> bool:
        """Apply dual pane responsive layout."""
        if len(self.panes) != 2:
            return False
        
        if layout_type == LayoutType.HORIZONTAL_SPLIT:
            return self.dual_pane_implementor.implement_horizontal_split(
                self.pane_container, self.panes, config
            )
        elif layout_type == LayoutType.VERTICAL_SPLIT:
            return self.dual_pane_implementor.implement_vertical_split(
                self.pane_container, self.panes, config
            )
        
        return False
    
    def _apply_multi_pane_responsive_layout(self, layout_type: LayoutType,
                                          config, animate: bool) -> bool:
        """Apply multi-pane responsive layout."""
        if len(self.panes) < 3:
            return False
        
        if layout_type == LayoutType.HORIZONTAL_ROW:
            return self.multi_pane_implementor.implement_horizontal_row(
                self.pane_container, self.panes, config
            )
        elif layout_type == LayoutType.VERTICAL_COLUMN:
            return self.multi_pane_implementor.implement_vertical_column(
                self.pane_container, self.panes, config
            )
        elif layout_type == LayoutType.GRID_2X2:
            return self.multi_pane_implementor.implement_grid_layout(
                self.pane_container, self.panes, config, 2, 2
            )
        elif layout_type == LayoutType.ADAPTIVE_GRID:
            viewport_width = self.layout_manager.viewport_size[0]
            return self.multi_pane_implementor.implement_adaptive_grid(
                self.pane_container, self.panes, config, viewport_width
            )
        
        return False
    
    def _clear_pane_container(self):
        """Clear the pane container for new layout."""
        try:
            # Remove all widgets from splitter
            while self.pane_container.count() > 0:
                widget = self.pane_container.widget(0)
                if widget:
                    widget.setParent(None)
        except Exception as e:
            self.logger.warning(f"Error clearing pane container: {e}")
    
    def _apply_simple_layout(self, pane_count: int):
        """Apply simple layout when responsive system is not available."""
        try:
            self._clear_pane_container()
            
            # Simple horizontal arrangement
            for pane in self.panes:
                self.pane_container.addWidget(pane)
            
            # Set equal sizes
            if self.panes:
                equal_size = 100 // len(self.panes)
                sizes = [equal_size] * len(self.panes)
                self.pane_container.setSizes(sizes)
            
            self.logger.debug(f"Applied simple layout for {pane_count} panes")
            
        except Exception as e:
            self.logger.error(f"Error applying simple layout: {e}")
    
    def _apply_initial_responsive_layout(self):
        """Apply initial responsive layout based on current conditions."""
        if not self.responsive_enabled or not self.panes:
            return
        
        try:
            # Get recommended layout for current pane count
            recommended = self.layout_manager.get_recommended_layout(len(self.panes))
            if recommended:
                self._apply_responsive_layout(recommended, animate=False)
            
        except Exception as e:
            self.logger.error(f"Error applying initial responsive layout: {e}")
    
    def _update_layout_options(self):
        """Update available layout options based on current state."""
        if not self.responsive_enabled:
            return
        
        try:
            pane_count = len(self.panes)
            available_layouts = self.layout_manager.get_layout_display_names(pane_count)
            
            # Update layout combo
            current_text = self.layout_combo.currentText()
            self.layout_combo.clear()
            
            if not available_layouts:
                self.layout_combo.addItem("No Layout Options")
                self.layout_combo.setEnabled(False)
            else:
                self.layout_combo.setEnabled(True)
                
                for layout_type, display_name in available_layouts:
                    self.layout_combo.addItem(display_name)
                    # Store layout type as item data
                    item_count = self.layout_combo.count() - 1
                    self.layout_combo.setItemData(item_count, layout_type.value)
                
                # Try to restore previous selection
                index = self.layout_combo.findText(current_text)
                if index >= 0:
                    self.layout_combo.setCurrentIndex(index)
                elif available_layouts:
                    # Select first available option
                    self.layout_combo.setCurrentIndex(0)
            
            self.logger.debug(f"Updated layout options: {len(available_layouts)} available")
            
        except Exception as e:
            self.logger.error(f"Error updating layout options: {e}")
    
    def _update_layout_combo_selection(self, layout_type: LayoutType):
        """Update layout combo selection to match current layout."""
        try:
            for i in range(self.layout_combo.count()):
                item_data = self.layout_combo.itemData(i)
                if item_data == layout_type.value:
                    self.layout_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            self.logger.warning(f"Error updating layout combo selection: {e}")
    
    def _update_status_display(self):
        """Update status bar with current layout information."""
        try:
            if self.responsive_enabled and self.current_layout_type:
                layout_info = self.layout_manager.get_current_layout_info()
                viewport_info = self.layout_manager.get_viewport_info()
                
                # Update status labels
                self.status_label.setText(
                    f"Panes: {len(self.panes)} | Layout: {layout_info.get('display_name', 'Unknown')}"
                )
                self.viewport_label.setText(
                    f"Viewport: {viewport_info.get('type', 'Unknown').title()}"
                )
                self.layout_status_label.setText(
                    f"Mode: {'Responsive' if self.responsive_enabled else 'Simple'}"
                )
                
                # Update layout info in toolbar
                self.layout_info_label.setText(
                    layout_info.get('description', 'No description')
                )
            else:
                self.status_label.setText(f"Panes: {len(self.panes)} | Layout: Simple")
                self.layout_info_label.setText("Simple layout mode")
            
        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")
    
    def _on_pane_count_changed(self, text: str):
        """Handle pane count change from combo box."""
        try:
            count = int(text)
            self.set_pane_count(count)
        except ValueError:
            self.logger.warning(f"Invalid pane count: {text}")
    
    def _on_layout_changed(self, text: str):
        """Handle layout change from combo box."""
        if not text or not self.responsive_enabled:
            return
        
        try:
            # Find layout type from combo box data
            current_index = self.layout_combo.currentIndex()
            if current_index >= 0:
                layout_value = self.layout_combo.itemData(current_index)
                if layout_value:
                    # Convert string value back to LayoutType
                    for layout_type in LayoutType:
                        if layout_type.value == layout_value:
                            self._apply_responsive_layout(layout_type, animate=True)
                            break
            
        except Exception as e:
            self.logger.error(f"Error handling layout change: {e}")
    
    def _toggle_responsive_mode(self, checked: bool):
        """Toggle responsive layout mode on/off."""
        try:
            self.responsive_enabled = checked and RESPONSIVE_IMPORTS_AVAILABLE
            
            if hasattr(self, 'responsive_toggle_btn'):
                status = "ON" if self.responsive_enabled else "OFF"
                self.responsive_toggle_btn.setText(f"Responsive Mode: {status}")
            
            # Update layout options
            if self.responsive_enabled:
                self._update_layout_options()
                self._apply_initial_responsive_layout()
            else:
                self._apply_simple_layout(len(self.panes))
            
            self._update_status_display()
            
            mode = 'enabled' if self.responsive_enabled else 'disabled'
            self.logger.info(f"Responsive mode {mode}")
            
        except Exception as e:
            self.logger.error(f"Error toggling responsive mode: {e}")
    
    # Responsive signal handlers
    def _on_responsive_layout_changed(self, layout_type: LayoutType, info: Dict[str, Any]):
        """Handle layout change from responsive manager."""
        self.layout_changed.emit(layout_type.value, info)
        self._update_status_display()
    
    def _on_viewport_changed(self, viewport_type: ViewportType, size: tuple):
        """Handle viewport change."""
        self.viewport_adapted.emit(viewport_type.value, size)
        self._update_status_display()
        
        # Check if current layout needs adjustment
        if self.responsive_enabled and self.current_layout_type:
            pane_count = len(self.panes)
            breakpoint = self.breakpoint_handler.detect_breakpoint(size[0], size[1])
            
            forced_layout = self.breakpoint_handler.should_force_layout_change(
                self.current_layout_type, pane_count, breakpoint
            )
            
            if forced_layout:
                self._apply_responsive_layout(forced_layout, animate=True)
    
    def _on_constraints_updated(self, pane_count: int, available_layouts: List):
        """Handle constraint updates."""
        self._update_layout_options()
    
    def _on_transition_started(self, old_layout: LayoutType, new_layout: LayoutType):
        """Handle transition start."""
        if old_layout:
            self.logger.debug(f"Transition started: {old_layout.value} -> {new_layout.value}")
        else:
            self.logger.debug(f"Transition started: None -> {new_layout.value}")
    
    def _on_transition_completed(self, layout_type: LayoutType):
        """Handle transition completion."""
        self.logger.debug(f"Transition completed: {layout_type.value}")
        self.layout_transition_completed.emit(layout_type.value)
    
    def resizeEvent(self, event):
        """Handle window resize with responsive adaptation."""
        super().resizeEvent(event)
        
        if self.responsive_enabled:
            try:
                # Update responsive manager with new size
                size = event.size()
                self.layout_manager._update_viewport_info_from_geometry(
                    size.width(), size.height()
                )
                
                # Trigger responsive adaptation with slight delay
                QTimer.singleShot(100, self._handle_resize_adaptation)
                
            except Exception as e:
                self.logger.error(f"Error handling resize event: {e}")
    
    def _handle_resize_adaptation(self):
        """Handle responsive adaptation after resize."""
        try:
            if self.current_layout_type:
                # Check if current layout is still valid
                pane_count = len(self.panes)
                available = self.layout_manager.get_available_layouts(pane_count)
                
                if self.current_layout_type not in available:
                    # Auto-switch to recommended layout
                    recommended = self.layout_manager.get_recommended_layout(pane_count)
                    if recommended:
                        self._apply_responsive_layout(recommended, animate=True)
        
        except Exception as e:
            self.logger.error(f"Error in resize adaptation: {e}")
    
    def get_layout_status(self) -> Dict[str, Any]:
        """Get comprehensive layout status information."""
        try:
            if self.responsive_enabled:
                return {
                    'responsive_enabled': True,
                    'current_layout': {
                        'type': self.current_layout_type.value if self.current_layout_type else None,
                        'display_name': (
                            self.layout_manager.layout_configs[self.current_layout_type].display_name
                            if self.current_layout_type else None
                        )
                    },
                    'pane_count': len(self.panes),
                    'viewport_info': self.layout_manager.get_viewport_info(),
                    'available_layouts': len(
                        self.layout_manager.get_available_layouts(len(self.panes))
                    ),
                    'constraints_summary': (
                        self.validation_engine.get_layout_constraints_summary(
                            self.current_layout_type
                        ) if self.current_layout_type else {}
                    )
                }
            else:
                return {
                    'responsive_enabled': False,
                    'current_layout': {'type': 'simple', 'display_name': 'Simple Layout'},
                    'pane_count': len(self.panes),
                    'message': 'Responsive layout system not available'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting layout status: {e}")
            return {'error': str(e)}
    
    def demonstrate_layout_capabilities(self):
        """Demonstrate all layout capabilities with transitions."""
        if not self.responsive_enabled:
            QMessageBox.information(
                self, "Demo", "Responsive layout system not available"
            )
            return
        
        try:
            QMessageBox.information(
                self, "Layout Demo",
                "This will demonstrate layout capabilities.\n"
                "Watch as the layout changes automatically!"
            )
            
            # Demo sequence: different pane counts and layouts
            demo_sequence = [
                (1, LayoutType.FULL_WIDTH),
                (1, LayoutType.CENTERED),
                (2, LayoutType.HORIZONTAL_SPLIT),
                (2, LayoutType.VERTICAL_SPLIT),
                (3, LayoutType.HORIZONTAL_ROW),
                (3, LayoutType.VERTICAL_COLUMN),
                (4, LayoutType.GRID_2X2),
                (4, LayoutType.ADAPTIVE_GRID)
            ]
            
            self._run_demo_sequence(demo_sequence, 0)
            
        except Exception as e:
            self.logger.error(f"Error in layout demo: {e}")
    
    def _run_demo_sequence(self, sequence: List[tuple], index: int):
        """Run layout demo sequence with delays."""
        if index >= len(sequence):
            QMessageBox.information(self, "Demo Complete", "Layout demonstration completed!")
            return
        
        try:
            pane_count, layout_type = sequence[index]
            
            # Set pane count if different
            if len(self.panes) != pane_count:
                self.set_pane_count(pane_count)
            
            # Apply layout
            self._apply_responsive_layout(layout_type, animate=True)
            
            # Schedule next step
            QTimer.singleShot(2000, lambda: self._run_demo_sequence(sequence, index + 1))
            
        except Exception as e:
            self.logger.error(f"Error in demo sequence: {e}")


def main():
    """Main function for testing the enhanced multi-pane explorer."""
    app = QApplication(sys.argv)
    
    explorer = EnhancedMultiPaneExplorer()
    explorer.show()
    
    # Add demo button for testing
    if hasattr(explorer, 'toolbar_frame'):
        demo_btn = QPushButton("Demo Layouts")
        demo_btn.clicked.connect(explorer.demonstrate_layout_capabilities)
        explorer.toolbar_frame.layout().addWidget(demo_btn)
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()