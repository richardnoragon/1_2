#!/usr/bin/env python3
"""
Enhanced Permissions Editor GUI for Richard's File Utilities
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.rfu import font_tokens
from src.gui.themes import token

import os
import stat
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from src.gui.components.buttons import PrimaryButton, SecondaryButton

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow

    STANDARD_WINDOW_AVAILABLE = True
except ImportError:
    # Fallback for standalone execution
    StandardWindow = QMainWindow
    STANDARD_WINDOW_AVAILABLE = False


class PermissionsEditorGUI(StandardWindow):
    """Enhanced Permissions Editor GUI."""

    def __init__(self):
        if STANDARD_WINDOW_AVAILABLE:
            super().__init__(
                title="Permissions Editor - Richard's File Utilities",
                window_type="utility",
            )
        else:
            super().__init__()
            _ui_bind(self, 'setWindowTitle', 'Legacy.s51cb73871bcb1066')
            self.setGeometry(100, 100, 800, 600)

        self.selected_path = None
        self._permission_undo = None
        self.init_ui()
        if STANDARD_WINDOW_AVAILABLE:
            self._setup_menu_callbacks()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_permissions", self.clear_selection)
            self.menu_manager.register_callback("help_permissions", self.show_help)

    def show_help(self):
        """Show comprehensive help for Permissions Editor."""
        help_text = """
        <h2>Permissions Editor - Comprehensive Guide</h2>

        <h3>🔐 Overview</h3>
        <p>The Permissions Editor allows you to view and modify file and directory
        permissions, controlling who can read, write, or execute files on your system.</p>

        <h3>🚀 Key Features</h3>
        <ul>
            <li><b>File Permissions</b>: View and modify individual file permissions</li>
            <li><b>Directory Permissions</b>: Manage folder access controls</li>
            <li><b>Batch Operations</b>: Apply permissions to multiple files</li>
            <li><b>Security Analysis</b>: Identify potential security issues</li>
            <li><b>Permission Templates</b>: Apply common permission patterns</li>
            <li><b>Inheritance Control</b>: Manage permission inheritance</li>
        </ul>

        <h3>📊 Permission Types</h3>
        <ul>
            <li><b>Read (r)</b>: Allows viewing file contents or listing directory</li>
            <li><b>Write (w)</b>: Allows modifying file contents or directory structure</li>
            <li><b>Execute (x)</b>: Allows running files or accessing directories</li>
        </ul>

        <h3>👥 Permission Categories</h3>
        <ul>
            <li><b>Owner</b>: The user who owns the file or directory</li>
            <li><b>Group</b>: Members of the file's assigned group</li>
            <li><b>Others</b>: All other users on the system</li>
        </ul>

        <h3>🔧 Common Permission Patterns</h3>
        <ul>
            <li><b>644 (rw-r--r--)</b>: Standard file permissions</li>
            <li><b>755 (rwxr-xr-x)</b>: Executable files and directories</li>
            <li><b>600 (rw-------)</b>: Private files (owner only)</li>
            <li><b>700 (rwx------)</b>: Private directories (owner only)</li>
            <li><b>666 (rw-rw-rw-)</b>: Shared files (read/write for all)</li>
        </ul>

        <h3>⚠️ Security Considerations</h3>
        <ul>
            <li><b>Least Privilege</b>: Grant only necessary permissions</li>
            <li><b>Sensitive Files</b>: Restrict access to confidential data</li>
            <li><b>System Files</b>: Never modify critical system file permissions</li>
            <li><b>Backup First</b>: Create backups before changing permissions</li>
        </ul>

        <h3>🛠️ Best Practices</h3>
        <ul>
            <li><b>Regular Audits</b>: Periodically review file permissions</li>
            <li><b>Group Management</b>: Use groups for easier permission management</li>
            <li><b>Documentation</b>: Document permission changes and reasons</li>
            <li><b>Testing</b>: Test permission changes in safe environments</li>
        </ul>

        <p><b>Note:</b> Modifying permissions requires appropriate system privileges.
        Some operations may require administrator rights.</p>
        """

        msg_box = QMessageBox()
        _ui_bind(msg_box, 'setWindowTitle', 'Legacy.s30b78498ece75c2a')
        msg_box.setTextFormat(1)  # Rich text format
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_preferences(self):
        """Show Permissions Editor preferences."""
        QMessageBox.information(
            self,
            "Permissions Editor Preferences",
            "Permissions Editor preferences:\n\n"
            "• Default permission templates\n"
            "• Security audit settings\n"
            "• Backup options before changes\n"
            "• Display format preferences\n"
            "• Warning and confirmation settings\n\n"
            "Advanced preferences coming soon!",
        )

    def refresh_view(self):
        """Refresh the current view."""
        if self.selected_path:
            self.load_permissions()
        else:
            self.clear_selection()

    def clear_selection(self):
        """Clear current selection and reset interface."""
        self.selected_path = None
        if hasattr(self, "file_label"):
            self.file_label.setText("No file/directory selected")
        if hasattr(self, "read_check"):
            self.read_check.setChecked(False)
            self.write_check.setChecked(False)
            self.execute_check.setChecked(False)
        if hasattr(self, "status_list"):
            self.status_list.clear()

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow or create new layout
        if STANDARD_WINDOW_AVAILABLE and hasattr(self, "main_layout"):
            layout = self.main_layout
        else:
            # Create central widget and layout for fallback mode
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

        # Add header
        header_label = _ui_widget(QLabel, 'Legacy.sbaf645edc7982895', 'setText')
        header_label.setStyleSheet(
            """
            QLabel {

                font-weight: bold;
                color: {token('text_primary')};
                padding: 10px;
                background-color: {token('background')};
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """
        )
        font_tokens.bind(header_label, "font.toolHeader")
        layout.addWidget(header_label)

        # File selection
        file_group = _ui_widget(QGroupBox, 'Legacy.s9eeccf894b023062', 'setTitle')
        file_layout = QVBoxLayout(file_group)

        # Selection buttons
        button_layout = QHBoxLayout()

        select_file_button = _ui_widget(PrimaryButton, 'Legacy.s79f376f90b59c3bc', 'setText')
        _ui_bind(select_file_button, 'setAccessibleName', 'Legacy.sd038b93bd43075ca')
        select_file_button.clicked.connect(self.select_file)
        button_layout.addWidget(select_file_button)

        select_dir_button = _ui_widget(SecondaryButton, 'Legacy.s220c3fe6289ca828', 'setText')
        _ui_bind(select_dir_button, 'setAccessibleName', 'Legacy.sd3ac21a50013290d')
        select_dir_button.clicked.connect(self.select_directory)
        button_layout.addWidget(select_dir_button)

        file_layout.addLayout(button_layout)

        self.file_label = _ui_widget(QLabel, 'Legacy.s2e38d8a5e309c8ef', 'setText')
        self.file_label.setStyleSheet(
            f"padding: 10px; background-color: {token('dialog_background')}; border-radius: 4px;"
        )
        file_layout.addWidget(self.file_label)

        layout.addWidget(file_group)

        # Permissions checkboxes
        perms_group = _ui_widget(QGroupBox, 'Legacy.sabccc78cc93c0793', 'setTitle')
        perms_layout = QVBoxLayout(perms_group)

        self.read_check = _ui_widget(QCheckBox, 'Legacy.s830f0bc8b0c60710', 'setText')
        _ui_bind(self.read_check, 'setAccessibleName', 'Legacy.s4aed314942ad3ce4')
        self.read_check.setMinimumHeight(44)
        self.write_check = _ui_widget(QCheckBox, 'Legacy.s6527699ac61adf67', 'setText')
        _ui_bind(self.write_check, 'setAccessibleName', 'Legacy.se87034f552476831')
        self.write_check.setMinimumHeight(44)
        self.execute_check = _ui_widget(QCheckBox, 'Legacy.s0187e10730b4399f', 'setText')
        _ui_bind(self.execute_check, 'setAccessibleName', 'Legacy.s1fc34fb727237c85')
        self.execute_check.setMinimumHeight(44)

        for checkbox in [
            self.read_check,
            self.write_check,
            self.execute_check,
        ]:
            checkbox.setStyleSheet("padding: 5px;")

        perms_layout.addWidget(self.read_check)
        perms_layout.addWidget(self.write_check)
        perms_layout.addWidget(self.execute_check)

        layout.addWidget(perms_group)

        # Control buttons
        control_layout = QHBoxLayout()

        load_button = _ui_widget(SecondaryButton, 'Legacy.s5d795f9575b5aa07', 'setText')
        _ui_bind(load_button, 'setAccessibleName', 'Legacy.s5998b8c5df4166b6')
        load_button.clicked.connect(self.load_permissions)
        control_layout.addWidget(load_button)

        apply_button = _ui_widget(PrimaryButton, 'Legacy.sd665c256868e1ed1', 'setText')
        _ui_bind(apply_button, 'setAccessibleName', 'Legacy.s2122f0e1db021d3a')
        apply_button.clicked.connect(self.apply_permissions)
        control_layout.addWidget(apply_button)

        clear_button = _ui_widget(SecondaryButton, 'Legacy.sc52ff5ea803d5775', 'setText')
        _ui_bind(clear_button, 'setAccessibleName', 'Legacy.sa95500ff1f838fe6')
        clear_button.clicked.connect(self.clear_selection)
        control_layout.addWidget(clear_button)

        layout.addLayout(control_layout)
        self.preview_only = _ui_widget(QCheckBox, 'Legacy.saa77a34e1ac919a9', 'setText')
        self.preview_only.setChecked(True)
        layout.addWidget(self.preview_only)
        if os.name == 'nt':
            self.read_check.setEnabled(False)
            self.execute_check.setEnabled(False)
            self.write_check.setText("Writable (Windows read-only flag)")
        from src.gui.background_task import BackgroundTask
        self._permission_task = BackgroundTask(self, 'permissions-editor', layout,
            [select_file_button, select_dir_button, load_button, apply_button, clear_button,
             self.read_check, self.write_check, self.execute_check, self.preview_only])

        # Status
        status_group = _ui_widget(QGroupBox, 'Legacy.sa5b5d494bffd8154', 'setTitle')
        status_layout = QVBoxLayout(status_group)

        self.status_list = QListWidget()
        _ui_bind(self.status_list, 'setAccessibleName', 'Legacy.s3f8647674d7b1bca')
        self.status_list.setMaximumHeight(150)
        status_layout.addWidget(self.status_list)

        layout.addWidget(status_group)

    def select_file(self):
        """Select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
            self.status_list.addItem(f"File selected: {os.path.basename(file_path)}")

    def select_directory(self):
        """Select a directory."""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.selected_path = dir_path
            self.file_label.setText(f"Selected: {dir_path}")
            self.status_list.addItem(
                f"Directory selected: {os.path.basename(dir_path)}"
            )

    def load_permissions(self):
        """Load current permissions."""
        if not self.selected_path:
            QMessageBox.warning(
                self, "Warning", "Please select a file/directory first."
            )
            return

        try:
            file_stat = os.stat(self.selected_path)
            mode = file_stat.st_mode

            self.read_check.setChecked(bool(mode & stat.S_IRUSR))
            self.write_check.setChecked(bool(mode & stat.S_IWUSR))
            self.execute_check.setChecked(bool(mode & stat.S_IXUSR))

            # Format permission string
            perm_str = stat.filemode(mode)
            self.status_list.addItem(
                f"Loaded permissions: {perm_str} for {os.path.basename(self.selected_path)}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load permissions: {e}")
            self.status_list.addItem(f"Error loading permissions: {e}")

    def apply_permissions(self):
        """Build a read-only plan off the UI thread before confirmation."""
        if not self.selected_path:
            return
        from src.core.permission_operations import plan_permissions
        mode = ((stat.S_IRUSR if self.read_check.isChecked() else 0)
                | (stat.S_IWUSR if self.write_check.isChecked() else 0)
                | (stat.S_IXUSR if self.execute_check.isChecked() else 0))
        path = self.selected_path
        self._permission_task.start('preview', lambda: plan_permissions(path, mode), self._review_permissions)

    def _review_permissions(self, plan):
        from src.gui.components import ConfirmationModal
        from PyQt5.QtWidgets import QDialog
        summary = f"{plan.path}\n{plan.before:04o} → {plan.after:04o}"
        if self.preview_only.isChecked():
            self.status_list.addItem("Preview only: " + summary)
            return
        if ConfirmationModal("Apply Permissions", summary, confirm_text="Apply", parent=self).exec_() == QDialog.Accepted:
            self._apply_permission_plan(plan)

    def _apply_permission_plan(self, plan):
        from src.core.permission_operations import apply_permissions
        def finished(reverse):
            self._permission_undo = reverse
            self.status_list.addItem(f"Permissions updated: {plan.path}")
        self._permission_task.start('apply', lambda: apply_permissions(plan), finished)

    def can_undo(self):
        return self._permission_undo is not None

    def undo(self):
        """Restore the previous mode only if the target remains unchanged."""
        if self._permission_undo is not None:
            self._review_permissions(self._permission_undo)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = PermissionsEditorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
