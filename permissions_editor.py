import os
import stat
import sys
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
                             QLabel, QCheckBox)

from gui.standard_window import StandardWindow
from gui.themes import ThemeManager
from gui.common.dialogs import get_open_file_name, get_existing_directory


class PermissionsEditorGUI(StandardWindow):
    """File permissions editor with standardized styling."""

    def __init__(self) -> None:
        super().__init__("File Permissions Editor")
        self.current_file: Optional[str] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the user interface with standardized styling."""
        # Create header
        header = self.create_header("File Permissions Editor")
        self.main_layout.addWidget(header)

        # Create file selection group
        file_group = self.create_group_box("File Selection")
        file_layout = QVBoxLayout()

        # File path display
        file_layout.addWidget(QLabel("Selected File:"))
        self.file_label = QLabel("No file selected")
        ThemeManager.style_label(self.file_label)

        # Buttons
        button_layout = QHBoxLayout()
        select_file_btn = self.create_button("Select File",
                                             self.select_file)
        select_dir_btn = self.create_button("Select Directory",
                                            self.select_directory)

        button_layout.addWidget(select_file_btn)
        button_layout.addWidget(select_dir_btn)

        file_layout.addWidget(self.file_label)
        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        self.main_layout.addWidget(file_group)

        # Create permissions group
        perm_group = self.create_group_box("Permissions")
        perm_layout = QVBoxLayout()

        # Create checkboxes for permissions
        self.read_owner = self.create_checkbox("Read (Owner)")
        self.write_owner = self.create_checkbox("Write (Owner)")
        self.execute_owner = self.create_checkbox("Execute (Owner)")

        self.read_group = self.create_checkbox("Read (Group)")
        self.write_group = self.create_checkbox("Write (Group)")
        self.execute_group = self.create_checkbox("Execute (Group)")

        self.read_other = self.create_checkbox("Read (Other)")
        self.write_other = self.create_checkbox("Write (Other)")
        self.execute_other = self.create_checkbox("Execute (Other)")

        # Add checkboxes to layout
        perm_layout.addWidget(self.read_owner)
        perm_layout.addWidget(self.write_owner)
        perm_layout.addWidget(self.execute_owner)
        perm_layout.addWidget(self.read_group)
        perm_layout.addWidget(self.write_group)
        perm_layout.addWidget(self.execute_group)
        perm_layout.addWidget(self.read_other)
        perm_layout.addWidget(self.write_other)
        perm_layout.addWidget(self.execute_other)

        perm_group.setLayout(perm_layout)
        self.main_layout.addWidget(perm_group)

        # Create action buttons
        action_group = self.create_group_box("Actions")
        action_layout = QHBoxLayout()

        load_btn = self.create_button("Load Permissions",
                                      self.load_permissions)
        apply_btn = self.create_button("Apply Permissions",
                                       self.apply_permissions)

        action_layout.addWidget(load_btn)
        action_layout.addWidget(apply_btn)

        action_group.setLayout(action_layout)
        self.main_layout.addWidget(action_group)

    def create_checkbox(self, text: str) -> QCheckBox:
        """Create a standardized checkbox."""
        checkbox = QCheckBox(text)
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {ThemeManager.TEXT_PRIMARY};
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {ThemeManager.TEXT_DISABLED};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {ThemeManager.ACCENT};
                border: 1px solid {ThemeManager.ACCENT};
            }}
        """)
        return checkbox

    def create_label(self, text: str) -> QLabel:
        """Create a standardized label."""
        label = QLabel(text)
        ThemeManager.style_label(label)
        return label

    def select_file(self) -> None:
        """Select a single file for permission editing."""
        file_path = get_open_file_name(self, "Select File")
        if file_path:
            self.current_file = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.load_permissions(file_path)

    def select_directory(self) -> None:
        """Select a directory for permission editing."""
        directory = get_existing_directory(self, "Select Directory")
        if directory:
            self.current_file = directory
            self.file_label.setText(os.path.basename(directory))
            self.load_permissions(directory)

    def load_permissions(self, path: str) -> None:
        """Load and display permissions for the selected file/directory.

        Args:
            path: Path to the file or directory
        """
        try:
            file_stat = os.stat(path)
            mode = file_stat.st_mode

            # Update checkboxes based on permissions
            self.read_owner.setChecked(bool(mode & stat.S_IRUSR))
            self.write_owner.setChecked(bool(mode & stat.S_IWUSR))
            self.execute_owner.setChecked(bool(mode & stat.S_IXUSR))

            self.read_group.setChecked(bool(mode & stat.S_IRGRP))
            self.write_group.setChecked(bool(mode & stat.S_IWGRP))
            self.execute_group.setChecked(bool(mode & stat.S_IXGRP))

            self.read_other.setChecked(bool(mode & stat.S_IROTH))
            self.write_other.setChecked(bool(mode & stat.S_IWOTH))
            self.execute_other.setChecked(bool(mode & stat.S_IXOTH))

            self.show_status_message(f"Loaded permissions for {os.path.basename(path)}")
        except Exception as e:
            self.show_error_dialog("Error", f"Could not load permissions: {str(e)}")

    def apply_permissions(self) -> None:
        """Apply the selected permissions to the current file/directory."""
        if not self.current_file:
            self.show_error_dialog("Error", "Please select a file or directory first")
            return

        try:
            # Calculate new permissions
            new_mode = 0

            if self.read_owner.isChecked():
                new_mode |= stat.S_IRUSR
            if self.write_owner.isChecked():
                new_mode |= stat.S_IWUSR
            if self.execute_owner.isChecked():
                new_mode |= stat.S_IXUSR

            if self.read_group.isChecked():
                new_mode |= stat.S_IRGRP
            if self.write_group.isChecked():
                new_mode |= stat.S_IWGRP
            if self.execute_group.isChecked():
                new_mode |= stat.S_IXGRP

            if self.read_other.isChecked():
                new_mode |= stat.S_IROTH
            if self.write_other.isChecked():
                new_mode |= stat.S_IWOTH
            if self.execute_other.isChecked():
                new_mode |= stat.S_IXOTH

            # Apply permissions
            os.chmod(self.current_file, new_mode)
            self.show_status_message("Permissions applied successfully")

        except Exception as e:
            self.show_error_dialog("Error", f"Could not apply permissions: {str(e)}")


def main() -> None:
    """Main function to run the permissions editor GUI."""
    app = QApplication(sys.argv)
    window = PermissionsEditorGUI()
    window.show()
    sys.exit(app.exec_())
