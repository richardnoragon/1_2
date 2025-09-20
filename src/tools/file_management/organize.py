"""File organization tool with rule-based file sorting.

This module provides functionality to organize files based on
customizable rules such as file type, size, date, and naming patterns.
"""

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt5 import uic
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem,
                             QMessageBox, QPushButton, QVBoxLayout)

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution
    from PyQt5.QtWidgets import QMainWindow
    
    class StandardWindow(QMainWindow):
        """Fallback StandardWindow when the main one isn't available."""
        def __init__(self, title="Organize Files", window_type="file_operations", **kwargs):
            super().__init__()
            self.setWindowTitle(title)
            self.window_type = window_type

def get_existing_directory(parent, title):
    """Directory selection dialog."""
    from PyQt5.QtWidgets import QFileDialog
    return QFileDialog.getExistingDirectory(parent, title)

def show_error_dialog(parent, title, message):
    """Error dialog display."""
    QMessageBox.critical(parent, title, message)


@dataclass
class OrganizeRule:
    """Represents a file organization rule.
    
    Attributes:
        name: Name of the rule
        pattern: File pattern to match (e.g., "*.txt", "*.jpg")
        destination: Destination folder path
        enabled: Whether the rule is active
    """
    name: str
    pattern: str
    destination: str
    enabled: bool = True


class OrganizeWindow(StandardWindow):
    """Main window for file organization operations.
    
    This window provides a graphical interface for organizing files
    based on customizable rules and patterns.
    
    Features:
    - Directory selection and recursive scanning
    - Rule-based file organization
    - Customizable file patterns
    - Preview before organization
    - Undo functionality
    
    Attributes:
        _current_dir: Path to currently selected directory
        _rules: List of organization rules
        _list_model: Model for file list view
        _organized_files: List of files that were moved
    """
    # Default paths
    _ICON_PATH = os.path.join(os.path.dirname(__file__), "icons")
    _ICON_NAME = "organize.png"
    _UI_FILE = "organize.ui"

    def __init__(self) -> None:
        """Initialize the OrganizeWindow.
        
        Sets up:
        - UI components and layout
        - Data models and internal state
        - Signal connections
        - Default organization rules
        """
        try:
            super().__init__(
                title="Organize Files - Richard's File Utilities",
                window_type="file_operations"
            )
        except TypeError:
            # Fallback for QMainWindow
            super().__init__()
            self.setWindowTitle("Organize Files - Richard's File Utilities")
        self._init_models()
        self._setup_ui()
        self._setup_icons()
        self._connect_signals()
        self._set_initial_state()
        self._load_default_rules()
        self._setup_menu_callbacks()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, 'menu_manager'):
            # Register tool-specific callbacks
            self.menu_manager.register_callback('new_organize', self.clear_organization)
            self.menu_manager.register_callback('save_operation', self.save_organize_settings)
            self.menu_manager.register_callback('load_operation', self.load_organize_settings)
            self.menu_manager.register_callback('export_results', self.export_organize_results)

    def clear_organization(self):
        """Clear current organization state."""
        self._current_dir = ""
        self._organized_files.clear()
        self._list_model.clear()
        if hasattr(self, 'directory_label'):
            self.directory_label.setText("No folder selected")
        if hasattr(self, 'status_label'):
            self.status_label.setText("Select a folder to begin")
        if hasattr(self, 'organizePushButton'):
            self.organizePushButton.setEnabled(False)

    def save_organize_settings(self):
        """Save current organize settings to file."""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Organize Settings", "organize_settings.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                settings = {
                    'directory': self._current_dir,
                    'rules': [
                        {
                            'name': rule.name,
                            'pattern': rule.pattern,
                            'destination': rule.destination,
                            'enabled': rule.enabled
                        }
                        for rule in self._rules
                    ]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2)
                    
                QMessageBox.information(self, "Success", f"Settings saved to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save settings: {e}")

    def load_organize_settings(self):
        """Load organize settings from file."""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Organize Settings", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Apply settings
                if 'directory' in settings and settings['directory']:
                    self._current_dir = settings['directory']
                    if hasattr(self, 'directory_label'):
                        self.directory_label.setText(settings['directory'])
                    self._update_file_list()
                    
                if 'rules' in settings:
                    self._rules = [
                        OrganizeRule(
                            name=rule['name'],
                            pattern=rule['pattern'],
                            destination=rule['destination'],
                            enabled=rule.get('enabled', True)
                        )
                        for rule in settings['rules']
                    ]
                    
                QMessageBox.information(self, "Success", f"Settings loaded from {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load settings: {e}")

    def export_organize_results(self):
        """Export organize preview results."""
        if not self._current_dir:
            QMessageBox.information(self, "No Directory", "No directory selected for organizing.")
            return
            
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Organize Results", "organize_preview.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Organize Preview Results\n")
                    f.write(f"Directory: {self._current_dir}\n")
                    f.write(f"Total Rules: {len(self._rules)}\n\n")
                    
                    f.write("Organization Rules:\n")
                    for rule in self._rules:
                        status = "✓" if rule.enabled else "✗"
                        f.write(f"{status} {rule.name}: {rule.pattern} → {rule.destination}\n")
                    
                    f.write(f"\nFiles organized: {len(self._organized_files)}\n")
                    for original, new in self._organized_files:
                        f.write(f"{original} → {new}\n")
                        
                QMessageBox.information(self, "Success", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export results: {e}")

    def _init_models(self) -> None:
        """Initialize data models and internal state."""
        self._current_dir = ""
        self._rules: List[OrganizeRule] = []
        self._list_model = QStandardItemModel()
        self._organized_files: List[Tuple[str, str]] = []
        
        if hasattr(self, 'listListView'):
            self.listListView.setModel(self._list_model)

    def _setup_ui(self) -> None:
        """Initialize and load the UI file."""
        try:
            ui_file = Path(__file__).parent / self._UI_FILE
            if not ui_file.exists():
                raise FileNotFoundError(f"UI file not found: {ui_file}")
                
            uic.loadUi(str(ui_file), self)
            
        except (FileNotFoundError, ValueError) as e:
            show_error_dialog(self, "UI Error", str(e))
            sys.exit(1)

    def _connect_signals(self) -> None:
        """Connect UI signals to their respective slots."""
        if hasattr(self, 'selectFolderButton'):
            self.selectFolderButton.clicked.connect(self._load_directory)
        if hasattr(self, 'organizePushButton'):
            self.organizePushButton.clicked.connect(self._organize_files)
        if hasattr(self, 'rulesButton'):
            self.rulesButton.clicked.connect(self._show_rules_dialog)
            
        # Connect menu actions
        if hasattr(self, 'actionexit'):
            self.actionexit.triggered.connect(self.close)
        if hasattr(self, 'actionselect'):
            self.actionselect.triggered.connect(self._load_directory)

    def _set_initial_state(self) -> None:
        """Set the initial state of UI elements."""
        if hasattr(self, 'organizePushButton'):
            self.organizePushButton.setEnabled(False)
        if hasattr(self, 'status_label'):
            self.status_label.setText("Select a folder to begin")

    def _setup_icons(self) -> None:
        """Load application icons."""
        icon_file = Path(self._ICON_PATH) / self._ICON_NAME
        if icon_file.exists():
            self.setWindowIcon(QIcon(str(icon_file)))

    def _load_default_rules(self) -> None:
        """Load default organization rules."""
        self._rules = [
            OrganizeRule("Documents", "*.pdf;*.doc;*.docx;*.txt", "Documents"),
            OrganizeRule("Images", "*.jpg;*.jpeg;*.png;*.gif;*.bmp", "Images"),
            OrganizeRule("Videos", "*.mp4;*.avi;*.mkv;*.mov;*.wmv", "Videos"),
            OrganizeRule("Audio", "*.mp3;*.wav;*.flac;*.aac", "Audio"),
            OrganizeRule(
                "Archives", "*.zip;*.rar;*.7z;*.tar;*.gz", "Archives"
            ),
        ]

    def _load_directory(self) -> None:
        """Load directory and display files in the list view."""
        directory = get_existing_directory(
            self, "Select Directory to Organize"
        )
        if directory:
            self._current_dir = directory
            if hasattr(self, 'directory_label'):
                self.directory_label.setText(directory)
            self._update_file_list()
            if hasattr(self, 'organizePushButton'):
                self.organizePushButton.setEnabled(True)
            if hasattr(self, 'status_label'):
                self.status_label.setText("Ready to organize files")

    def _update_file_list(self) -> None:
        """Update the list view with files from the selected directory."""
        self._list_model.clear()
        
        if not self._current_dir:
            return
            
        try:
            files = self._get_file_list()
            for file_path in sorted(files):
                self._add_file_to_list(file_path)
                
        except OSError as e:
            show_error_dialog(
                self,
                "Error",
                f"Could not read directory: {str(e)}"
            )

    def _get_file_list(self) -> List[str]:
        """Get list of files from the current directory.
        
        Returns:
            List[str]: List of full file paths
        """
        files = []
        base_path = Path(self._current_dir)
        
        recursive = False
        if hasattr(self, 'recursiveCheckBox'):
            recursive = self.recursiveCheckBox.isChecked()
            
        if recursive:
            for path in base_path.rglob('*'):
                if path.is_file():
                    files.append(str(path))
        else:
            for path in base_path.iterdir():
                if path.is_file():
                    files.append(str(path))
                    
        return files

    def _add_file_to_list(self, file_path: str) -> None:
        """Add a file entry to the list model.
        
        Args:
            file_path: Full path to the file
        """
        item = QStandardItem(os.path.basename(file_path))
        item.setData(file_path)  # Store full path in item data
        self._list_model.appendRow(item)

    def _organize_files(self) -> None:
        """Organize files based on the current rules."""
        if not self._current_dir:
            return
            
        try:
            organized_count = 0
            self._organized_files.clear()
            
            files = self._get_file_list()
            for file_path in files:
                if self._organize_single_file(file_path):
                    organized_count += 1
            
            self._update_file_list()  # Refresh the list
            
            QMessageBox.information(
                self,
                "Organization Complete",
                f"Organized {organized_count} files based on rules."
            )
            
            if hasattr(self, 'status_label'):
                self.status_label.setText(
                    f"Organized {organized_count} files"
                )
                
        except Exception as e:
            show_error_dialog(
                self,
                "Error",
                f"Failed to organize files: {str(e)}"
            )

    def _organize_single_file(self, file_path: str) -> bool:
        """Organize a single file based on rules.
        
        Args:
            file_path: Path to the file to organize
            
        Returns:
            bool: True if file was moved, False otherwise
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return False
            
        for rule in self._rules:
            if not rule.enabled:
                continue
                
            patterns = [p.strip() for p in rule.pattern.split(';')]
            for pattern in patterns:
                if file_path_obj.match(pattern):
                    return self._move_file_to_destination(
                        file_path, rule.destination
                    )
                    
        return False

    def _move_file_to_destination(
        self, file_path: str, destination: str
    ) -> bool:
        """Move a file to its destination folder.
        
        Args:
            file_path: Source file path
            destination: Destination folder name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            source_path = Path(file_path)
            dest_dir = Path(self._current_dir) / destination
            
            # Create destination directory if it doesn't exist
            dest_dir.mkdir(exist_ok=True)
            
            # Build destination path
            dest_path = dest_dir / source_path.name
            
            # Handle duplicate filenames
            counter = 1
            while dest_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            
            # Store for potential undo
            self._organized_files.append((str(source_path), str(dest_path)))
            
            return True
            
        except Exception as e:
            print(f"Error moving file {file_path}: {e}")
            return False

    def _show_rules_dialog(self) -> None:
        """Show the rules management dialog."""
        dialog = RulesDialog(self._rules, self)
        if dialog.exec_():
            self._rules = dialog.get_rules()

    def _undo_last_organization(self) -> None:
        """Undo the last organization operation."""
        try:
            moved_count = 0
            for original_path, new_path in reversed(self._organized_files):
                if Path(new_path).exists():
                    shutil.move(new_path, original_path)
                    moved_count += 1
            
            self._organized_files.clear()
            self._update_file_list()
            
            QMessageBox.information(
                self,
                "Undo Complete",
                f"Restored {moved_count} files to original locations."
            )
            
        except Exception as e:
            show_error_dialog(
                self,
                "Error",
                f"Failed to undo organization: {str(e)}"
            )


class RulesDialog(QDialog):
    """Dialog for managing organization rules."""
    
    def __init__(self, rules: List[OrganizeRule], parent=None) -> None:
        """Initialize the rules dialog.
        
        Args:
            rules: Current list of organization rules
            parent: Parent widget
        """
        super().__init__(parent)
        self._rules = rules.copy()
        self._init_ui()
        
    def _init_ui(self) -> None:
        """Initialize the dialog UI."""
        self.setWindowTitle("Manage Organization Rules")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout()
        
        # Rules list
        self.rules_list = QListWidget()
        self._populate_rules_list()
        layout.addWidget(QLabel("Organization Rules:"))
        layout.addWidget(self.rules_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Rule")
        add_button.clicked.connect(self._add_rule)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit Rule")
        edit_button.clicked.connect(self._edit_rule)
        button_layout.addWidget(edit_button)
        
        remove_button = QPushButton("Remove Rule")
        remove_button.clicked.connect(self._remove_rule)
        button_layout.addWidget(remove_button)
        
        layout.addLayout(button_layout)
        
        # OK/Cancel buttons
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
    
    def _populate_rules_list(self) -> None:
        """Populate the rules list widget."""
        self.rules_list.clear()
        for rule in self._rules:
            status = "✓" if rule.enabled else "✗"
            item_text = f"{status} {rule.name}: {rule.pattern} → {rule.destination}"
            self.rules_list.addItem(QListWidgetItem(item_text))
    
    def _add_rule(self) -> None:
        """Add a new organization rule."""
        dialog = RuleEditDialog(self)
        if dialog.exec_():
            new_rule = dialog.get_rule()
            self._rules.append(new_rule)
            self._populate_rules_list()
    
    def _edit_rule(self) -> None:
        """Edit the selected rule."""
        current_row = self.rules_list.currentRow()
        if 0 <= current_row < len(self._rules):
            dialog = RuleEditDialog(self, self._rules[current_row])
            if dialog.exec_():
                self._rules[current_row] = dialog.get_rule()
                self._populate_rules_list()
    
    def _remove_rule(self) -> None:
        """Remove the selected rule."""
        current_row = self.rules_list.currentRow()
        if 0 <= current_row < len(self._rules):
            del self._rules[current_row]
            self._populate_rules_list()
    
    def get_rules(self) -> List[OrganizeRule]:
        """Get the current list of rules.
        
        Returns:
            List[OrganizeRule]: Current organization rules
        """
        return self._rules


class RuleEditDialog(QDialog):
    """Dialog for editing individual organization rules."""
    
    def __init__(
        self, parent=None, rule: Optional[OrganizeRule] = None
    ) -> None:
        """Initialize the rule edit dialog.
        
        Args:
            parent: Parent widget
            rule: Rule to edit (None for new rule)
        """
        super().__init__(parent)
        self._rule = rule
        self._init_ui()
        
    def _init_ui(self) -> None:
        """Initialize the dialog UI."""
        self.setWindowTitle("Edit Rule")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        # Rule name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Rule Name:"))
        self.name_edit = QLineEdit()
        if self._rule:
            self.name_edit.setText(self._rule.name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # File pattern
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("File Pattern:"))
        self.pattern_edit = QLineEdit()
        if self._rule:
            self.pattern_edit.setText(self._rule.pattern)
        pattern_layout.addWidget(self.pattern_edit)
        layout.addLayout(pattern_layout)
        
        # Destination folder
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel("Destination:"))
        self.dest_edit = QLineEdit()
        if self._rule:
            self.dest_edit.setText(self._rule.destination)
        dest_layout.addWidget(self.dest_edit)
        layout.addLayout(dest_layout)
        
        # OK/Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_rule(self) -> OrganizeRule:
        """Get the edited rule.
        
        Returns:
            OrganizeRule: The edited rule
        """
        return OrganizeRule(
            name=self.name_edit.text(),
            pattern=self.pattern_edit.text(),
            destination=self.dest_edit.text()
        )


def main() -> None:
    """Main entry point for the organize application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    _ = OrganizeWindow()  # Keep reference to prevent garbage collection
    sys.exit(app.exec_())


# Compatibility alias for main.py
OrganizeGUI = OrganizeWindow


if __name__ == "__main__":
    main()

