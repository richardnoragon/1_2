"""
Image Metadata Editor GUI Module

Modern GUI for Image Metadata Editor with comprehensive hub integration.
Inherits from StandardWindow and provides consistent styling and functionality.
"""

import os
import sys
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QLabel, QGroupBox, QProgressBar, QListWidget,
    QAbstractItemView, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi

# Import file_utilities_2 components
from .standard_window import StandardWindow
from .themes import ThemeManager, Colors, Fonts, Spacing
from ..integration.hub_connector import HubConnector
from ..core.image_metadata_logic import ImageMetadataLogic, ImageMetadataWorker


class ImageMetadataEditor(StandardWindow):
    """
    Modern image metadata editor with comprehensive hub integration.
    
    Inherits from StandardWindow and provides:
    - Modern PyQt5 interface with progress visualization
    - Integration with ThemeManager for consistent styling
    - Connection to core logic via signals/slots
    - Hub communication and coordination
    - Batch processing capabilities
    """
    
    def __init__(self, hub_instance=None):
        """Initialize the image metadata editor."""
        super().__init__(
            title="Image Metadata Editor",
            icon_path=self._get_icon_path()
        )
        
        # Initialize hub integration
        self.hub_connector = HubConnector("Image Metadata Editor", hub_instance)
        self.hub_connector.register_with_hub()
        
        # Initialize core logic with hub integration
        self.metadata_logic = ImageMetadataLogic(self.hub_connector)
        
        # Setup UI components
        self._setup_ui()
        self._connect_signals()
        self._apply_theme()
        
        # Initialize state
        self.current_file = None
        self.current_metadata = {}
        self.batch_mode = False
        self.worker_thread = None
        
        # Report tool startup
        self.hub_connector.report_status_to_hub("started", {
            "tool_version": "2.0.0",
            "startup_time": self.hub_connector._get_current_time()
        })
    
    def _get_icon_path(self):
        """Get icon path for the application."""
        return os.path.join(os.path.dirname(__file__), 'icons', 'image_metadata.png')
    
    def _setup_ui(self):
        """Setup UI components with modern styling."""
        # Create main layout
        main_widget = self.centralWidget()
        if main_widget is None:
            from PyQt5.QtWidgets import QWidget
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(Spacing.WINDOW_MARGIN, Spacing.WINDOW_MARGIN,
                                  Spacing.WINDOW_MARGIN, Spacing.WINDOW_MARGIN)
        layout.setSpacing(Spacing.LARGE_SPACING)
        
        # File selection group
        self._create_file_selection_ui(layout)
        
        # Metadata display group
        self._create_metadata_display_ui(layout)
        
        # Progress tracking UI
        self._create_progress_ui(layout)
        
        # Batch processing UI
        self._create_batch_ui(layout)
        
        # Action buttons
        self._create_action_buttons_ui(layout)
    
    def _create_file_selection_ui(self, parent_layout):
        """Create file selection UI components."""
        file_group = self.create_group_box("File Selection")
        file_layout = QHBoxLayout()
        
        # File path display
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select an image file...")
        self.file_path_edit.setReadOnly(True)
        ThemeManager.style_input_field(self.file_path_edit)
        
        # Browse button
        self.browse_button = self.create_button("Browse...", self._browse_file)
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.browse_button)
        file_group.setLayout(file_layout)
        parent_layout.addWidget(file_group)
    
    def _create_metadata_display_ui(self, parent_layout):
        """Create metadata display UI components."""
        metadata_group = self.create_group_box("Image Metadata")
        metadata_layout = QVBoxLayout()
        
        # Metadata tree widget
        self.metadata_tree = QTreeWidget()
        self.metadata_tree.setHeaderLabels([
            "IFD/Group", "Tag Name", "Value", "Type", "Editable"
        ])
        self.metadata_tree.setAlternatingRowColors(True)
        self.metadata_tree.setSortingEnabled(True)
        self.metadata_tree.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed
        )
        
        # Connect signals
        self.metadata_tree.itemChanged.connect(self._on_metadata_changed)
        self.metadata_tree.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Apply theme styling
        ThemeManager.style_input_field(self.metadata_tree)
        
        metadata_layout.addWidget(self.metadata_tree)
        metadata_group.setLayout(metadata_layout)
        parent_layout.addWidget(metadata_group)
    
    def _create_progress_ui(self, parent_layout):
        """Create progress tracking UI components."""
        self.progress_group = self.create_group_box("Operation Progress")
        self.progress_group.setVisible(False)
        
        progress_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = self.create_progress_bar()
        
        # Progress message label
        self.progress_message = QLabel("Ready")
        ThemeManager.style_label(self.progress_message)
        
        # Time estimate label
        self.time_estimate_label = QLabel("")
        ThemeManager.style_label(self.time_estimate_label)
        
        # Cancel button
        self.cancel_button = self.create_button(
            "Cancel", self._cancel_operation, primary=False
        )
        self.cancel_button.setVisible(False)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_message)
        progress_layout.addWidget(self.time_estimate_label)
        progress_layout.addWidget(self.cancel_button)
        
        self.progress_group.setLayout(progress_layout)
        parent_layout.addWidget(self.progress_group)
    
    def _create_batch_ui(self, parent_layout):
        """Create batch processing UI components."""
        self.batch_group = self.create_group_box("Batch Operations")
        self.batch_group.setVisible(False)  # Hidden by default
        
        batch_layout = QVBoxLayout()
        
        # Batch file list
        self.batch_list = QListWidget()
        ThemeManager.style_input_field(self.batch_list)
        
        # Batch control buttons
        batch_buttons_layout = QHBoxLayout()
        
        self.add_files_btn = self.create_button(
            "Add Files", self._add_batch_files, primary=False
        )
        self.remove_files_btn = self.create_button(
            "Remove Selected", self._remove_batch_files, primary=False
        )
        self.process_batch_btn = self.create_button(
            "Process Batch", self._process_batch, primary=True
        )
        
        batch_buttons_layout.addWidget(self.add_files_btn)
        batch_buttons_layout.addWidget(self.remove_files_btn)
        batch_buttons_layout.addWidget(self.process_batch_btn)
        
        batch_layout.addWidget(self.batch_list)
        batch_layout.addLayout(batch_buttons_layout)
        
        self.batch_group.setLayout(batch_layout)
        parent_layout.addWidget(self.batch_group)
    
    def _create_action_buttons_ui(self, parent_layout):
        """Create action buttons UI."""
        buttons_layout = QHBoxLayout()
        
        # Add spacer to push buttons to the right
        buttons_layout.addStretch()
        
        # Reload button
        self.reload_button = self.create_button(
            "Reload", self._reload_metadata, primary=False
        )
        self.reload_button.setEnabled(False)
        
        # Save button
        self.save_button = self.create_button(
            "Save Changes", self._save_changes, primary=True
        )
        self.save_button.setEnabled(False)
        
        # Export button
        self.export_button = self.create_button(
            "Export", self._export_metadata, primary=False
        )
        self.export_button.setEnabled(False)
        
        buttons_layout.addWidget(self.reload_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.export_button)
        
        parent_layout.addLayout(buttons_layout)
    
    def _connect_signals(self):
        """Connect signals from core logic to GUI."""
        # Connect metadata logic signals
        self.metadata_logic.progress_percentage.connect(self._update_progress)
        self.metadata_logic.progress_message.connect(self._update_progress_message)
        self.metadata_logic.milestone_reached.connect(self._on_milestone_reached)
        self.metadata_logic.metadata_loaded.connect(self._on_metadata_loaded)
        self.metadata_logic.metadata_saved.connect(self._on_metadata_saved)
        self.metadata_logic.error_occurred.connect(self._on_error_occurred)
        self.metadata_logic.operation_cancelled.connect(self._on_operation_cancelled)
        self.metadata_logic.finished.connect(self._on_operation_finished)
        
        # Connect hub signals
        self.hub_connector.hub_message_received.connect(self._handle_hub_message)
        self.hub_connector.tool_status_changed.connect(self._handle_status_change)
    
    def _apply_theme(self):
        """Apply comprehensive theme integration."""
        # Apply standard window theme
        ThemeManager.apply_utility_window_theme(self)
        
        # Register for theme changes
        ThemeManager.register_theme_callback(self._on_theme_changed)
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes."""
        self._apply_theme()
        self.show_status_message(f"Theme changed to: {theme_name}")
    
    def _browse_file(self):
        """Open file dialog and load selected image file."""
        file_path = self.get_file_path(
            "Select Image File",
            "Images (*.jpg *.jpeg *.tif *.tiff);;All Files (*.*)"
        )
        
        if file_path:
            self.current_file = file_path
            self.file_path_edit.setText(file_path)
            self._load_metadata(file_path)
    
    def _load_metadata(self, file_path: str):
        """Load metadata from the specified file."""
        # Show progress UI
        self._show_progress_ui()
        
        # Start worker thread for loading
        self.worker_thread = ImageMetadataWorker(
            self.metadata_logic, file_path, "load"
        )
        self.worker_thread.start()
    
    def _save_changes(self):
        """Save current metadata modifications."""
        if self.current_file and self.current_metadata:
            # Show progress UI
            self._show_progress_ui()
            
            # Start worker thread for saving
            self.worker_thread = ImageMetadataWorker(
                self.metadata_logic, self.current_file, "save",
                modified_data=self.current_metadata
            )
            self.worker_thread.start()
    
    def _reload_metadata(self):
        """Reload metadata from the current file."""
        if self.current_file:
            self._load_metadata(self.current_file)
    
    def _export_metadata(self):
        """Export metadata to a file."""
        if not self.current_metadata:
            self.show_warning_dialog("Warning", "No metadata to export.")
            return
        
        export_path = self.get_save_file_path(
            "Export Metadata",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if export_path:
            try:
                import json
                with open(export_path, 'w', encoding='utf-8') as f:
                    # Prepare metadata for export (remove non-serializable items)
                    export_data = self._prepare_metadata_for_export(self.current_metadata)
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self.show_info_dialog("Success", f"Metadata exported to {export_path}")
            except Exception as e:
                self.show_error_dialog("Export Error", f"Failed to export metadata: {e}")
    
    def _prepare_metadata_for_export(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for JSON export."""
        export_data = {}
        for ifd_name, tags in metadata.items():
            if ifd_name == 'file_info':
                export_data[ifd_name] = tags
                continue
            
            export_data[ifd_name] = {}
            for tag_code, tag_info in tags.items():
                export_data[ifd_name][str(tag_code)] = {
                    'name': tag_info['name'],
                    'value': tag_info['value'],
                    'type': str(tag_info['original_type'])
                }
        
        return export_data
    
    def _show_progress_ui(self):
        """Show progress UI elements."""
        self.progress_group.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_message.setVisible(True)
        self.time_estimate_label.setVisible(True)
        
        # Disable action buttons and show cancel
        self.browse_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.reload_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.cancel_button.setVisible(True)
    
    def _hide_progress_ui(self):
        """Hide progress UI elements."""
        self.progress_group.setVisible(False)
        self.cancel_button.setVisible(False)
        
        # Re-enable action buttons
        self.browse_button.setEnabled(True)
        if self.current_metadata:
            self.save_button.setEnabled(True)
            self.reload_button.setEnabled(True)
            self.export_button.setEnabled(True)
    
    def _cancel_operation(self):
        """Cancel the current operation."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
        
        self.metadata_logic.cancel_operation()
        self._hide_progress_ui()
    
    def _update_progress(self, percentage: int):
        """Update progress bar."""
        self.progress_bar.setValue(percentage)
    
    def _update_progress_message(self, message: str):
        """Update progress message."""
        self.progress_message.setText(message)
    
    def _on_milestone_reached(self, milestone: str, percentage: int):
        """Handle milestone updates."""
        self.show_status_message(f"{milestone} ({percentage}%)")
    
    def _on_metadata_loaded(self, metadata: Dict[str, Any]):
        """Handle metadata loading completion."""
        self.current_metadata = metadata
        self._populate_metadata_tree(metadata)
        self._hide_progress_ui()
        
        if metadata:
            self.show_status_message(f"Loaded metadata from {os.path.basename(self.current_file)}")
        else:
            self.show_status_message("No metadata found in image")
    
    def _on_metadata_saved(self, success: bool, message: str):
        """Handle metadata saving completion."""
        self._hide_progress_ui()
        
        if success:
            self.show_info_dialog("Success", message)
            self.show_status_message("Metadata saved successfully")
        else:
            self.show_error_dialog("Save Error", message)
    
    def _on_error_occurred(self, error_message: str):
        """Handle error messages."""
        self._hide_progress_ui()
        self.show_error_dialog("Error", error_message)
    
    def _on_operation_cancelled(self):
        """Handle operation cancellation."""
        self._hide_progress_ui()
        self.show_status_message("Operation cancelled")
    
    def _on_operation_finished(self):
        """Handle operation completion."""
        self._hide_progress_ui()
    
    def _populate_metadata_tree(self, metadata: Dict[str, Any]):
        """Populate metadata tree with enhanced display."""
        self.metadata_tree.clear()
        
        for ifd_name, tags in metadata.items():
            if ifd_name == 'file_info':
                continue  # Handle file info separately
            
            # Create IFD group item
            ifd_item = QTreeWidgetItem([ifd_name, "", "", "", ""])
            ifd_item.setExpanded(True)
            
            # Style IFD item
            font = ifd_item.font(0)
            font.setBold(True)
            ifd_item.setFont(0, font)
            
            self.metadata_tree.addTopLevelItem(ifd_item)
            
            # Add tag items
            for tag_code, tag_info in tags.items():
                tag_item = QTreeWidgetItem([
                    "",  # IFD column (empty for tags)
                    tag_info.get('name', f'Tag_{tag_code}'),
                    tag_info.get('value', ''),
                    str(tag_info.get('original_type', 'Unknown')),
                    "Yes" if tag_info.get('editable', True) else "No"
                ])
                
                # Store tag information
                tag_item.setData(0, Qt.UserRole, {
                    'ifd_name': ifd_name,
                    'tag_code': tag_code,
                    'tag_info': tag_info
                })
                
                # Configure editability
                if tag_info.get('editable', True):
                    tag_item.setFlags(tag_item.flags() | Qt.ItemIsEditable)
                else:
                    tag_item.setFlags(tag_item.flags() & ~Qt.ItemIsEditable)
                    # Style non-editable items
                    for col in range(tag_item.columnCount()):
                        tag_item.setForeground(col, QColor(Colors.TEXT_DISABLED))
                
                ifd_item.addChild(tag_item)
        
        # Resize columns to content
        for i in range(self.metadata_tree.columnCount()):
            self.metadata_tree.resizeColumnToContents(i)
    
    def _on_metadata_changed(self, item: QTreeWidgetItem, column: int):
        """Handle metadata tree item changes."""
        if column == 2 and item.data(0, Qt.UserRole):  # Value column
            tag_data = item.data(0, Qt.UserRole)
            ifd_name = tag_data['ifd_name']
            tag_code = tag_data['tag_code']
            new_value = item.text(column)
            
            # Update the metadata
            if (ifd_name in self.current_metadata and 
                tag_code in self.current_metadata[ifd_name]):
                self.current_metadata[ifd_name][tag_code]['value'] = new_value
                self.save_button.setEnabled(True)
    
    def _on_selection_changed(self):
        """Handle tree selection changes."""
        # Could add preview or detailed view here
        pass
    
    def _add_batch_files(self):
        """Add files to batch processing queue."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Image Files for Batch Processing",
            "",
            "Images (*.jpg *.jpeg *.tif *.tiff);;All Files (*.*)"
        )
        
        for file_path in files:
            self.batch_list.addItem(file_path)
        
        if files:
            self.batch_group.setVisible(True)
    
    def _remove_batch_files(self):
        """Remove selected files from batch queue."""
        for item in self.batch_list.selectedItems():
            self.batch_list.takeItem(self.batch_list.row(item))
        
        if self.batch_list.count() == 0:
            self.batch_group.setVisible(False)
    
    def _process_batch(self):
        """Process files in batch mode."""
        # Implementation for batch processing
        self.show_info_dialog("Batch Processing", "Batch processing not yet implemented")
    
    def _handle_hub_message(self, message):
        """Handle incoming hub messages."""
        # Implementation for hub message handling
        pass
    
    def _handle_status_change(self, tool_name: str, status: str):
        """Handle tool status changes."""
        # Implementation for status change handling
        pass
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Cancel any running operations
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
        
        # Cleanup hub integration
        self.hub_connector.cleanup()
        
        super().closeEvent(event)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = ImageMetadataEditor()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()