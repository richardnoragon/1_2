#!/usr/bin/env python3
"""
Simplified Rename Files Tool for Richard's File Utilities

Relocated under file_operations.rename to align with the
centralized file operations architecture.
"""
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind
from src.gui import menu_surfaces
from src.rfu import font_tokens

import json
import os
import sys

try:
    from PyQt5.QtWidgets import (
        QAction,
        QApplication,
        QButtonGroup,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QRadioButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    from src.gui.components.buttons import PrimaryButton, SecondaryButton
    from src.gui.components.inputs import TextInput
    from src.gui.themes import token
except ImportError:
    print("PyQt5 not available. Please install PyQt5.")
    sys.exit(1)

# Import StandardWindow for menu integration
try:
    from src.gui.standard_window import StandardWindow
except ImportError:
    # Fallback for standalone execution

    class StandardWindow(QMainWindow):
        """Fallback StandardWindow when the main one isn't available."""

        def __init__(
            self, title="Rename Files", window_type="file_operations", **kwargs
        ):
            super().__init__(**kwargs)
            self.setWindowTitle(title)
            self.window_type = window_type

            # Create central widget and main layout
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)

        def ensure_exit_action_reference(self):
            """Minimal exit action helper for standalone fallback."""
            menubar = self.menuBar() if hasattr(self, "menuBar") else None
            if menubar is None:
                return None

            exit_action = self._find_existing_exit_action(menubar)
            if exit_action is None:
                exit_action = self._create_exit_action(menubar)

            if exit_action is None:
                return None

            if not hasattr(self, "actionExit"):
                setattr(self, "actionExit", exit_action)
            if not hasattr(self, "actionexit"):
                setattr(self, "actionexit", exit_action)
            return exit_action

        def _find_existing_exit_action(self, menubar):
            for action in menubar.actions():
                menu = action.menu()
                if menu is None:
                    continue
                for child in menu.actions():
                    normalized = self._normalize_action_text(child.text())
                    if normalized in {"exit", "quit"}:
                        return child
            return None

        def _create_exit_action(self, menubar):
            file_menu = menu_surfaces.add_menu(menubar, '&File')
            exit_action = _ui_widget(QAction, 'Legacy.s2eb7984c42b97146', 'setText', self)
            exit_action.setShortcut("Ctrl+Q")
            _ui_bind(exit_action, 'setStatusTip', 'Legacy.sa7a8480fbc4288f1')
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            return exit_action

        @staticmethod
        def _normalize_action_text(label):
            return (label or "").replace("&", "").strip().lower()


NO_FILES_SELECTED_MESSAGE = "No files selected for renaming."


class RenameWindow(StandardWindow):
    """Simplified Rename Files GUI with essential functionality."""

    def __init__(self):
        super().__init__(
            title="Rename Files - Richard's File Utilities",
            window_type="file_operations",
        )
        self.current_directory = ""
        self.selected_files = []
        self._rename_undo = ()
        self.init_ui()
        self._setup_menu_callbacks()
        self.ensure_exit_action_reference()

    def _setup_menu_callbacks(self):
        """Setup tool-specific menu callbacks."""
        if hasattr(self, "menu_manager"):
            # Register tool-specific callbacks
            self.menu_manager.register_callback("new_rename", self.clear_selected_files)
            self.menu_manager.register_callback(
                "save_operation", self.save_rename_settings
            )
            self.menu_manager.register_callback(
                "load_operation", self.load_rename_settings
            )
            self.menu_manager.register_callback(
                "export_results", self.export_rename_results
            )

    def save_rename_settings(self):
        """Save current rename settings to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Rename Settings",
            "rename_settings.json",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                settings = {
                    "directory": self.current_directory,
                    "rename_mode": self._get_current_rename_mode(),
                    "prefix_text": self.prefix_edit.text(),
                    "suffix_text": self.suffix_edit.text(),
                    "find_text": self.find_edit.text(),
                    "replace_text": self.replace_edit.text(),
                    "start_number": self.start_number_edit.text(),
                    "number_format": self.number_format_edit.text(),
                }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)

                QMessageBox.information(
                    self, "Success", f"Settings saved to {file_path}"
                )
            except OSError as error:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to save settings: {error}",
                )

    def load_rename_settings(self):
        """Load rename settings from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Rename Settings",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                # Apply settings
                if "directory" in settings and settings["directory"]:
                    self.current_directory = settings["directory"]
                    self.directory_edit.setText(settings["directory"])
                    self.load_available_files()

                if "prefix_text" in settings:
                    self.prefix_edit.setText(settings["prefix_text"])
                if "suffix_text" in settings:
                    self.suffix_edit.setText(settings["suffix_text"])

                QMessageBox.information(
                    self, "Success", f"Settings loaded from {file_path}"
                )
            except (OSError, json.JSONDecodeError) as error:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to load settings: {error}",
                )

    def export_rename_results(self):
        """Export rename preview results."""
        if not self.selected_files:
            QMessageBox.information(
                self,
                "No Files",
                NO_FILES_SELECTED_MESSAGE,
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Rename Results",
            "rename_preview.txt",
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Rename Preview Results\n")
                    f.write(f"Directory: {self.current_directory}\n")
                    mode = self._get_current_rename_mode()
                    f.write(f"Rename Mode: {mode}\n")
                    f.write(f"Total Files: {len(self.selected_files)}\n\n")

                    for i, filename in enumerate(self.selected_files):
                        new_filename = self.get_new_filename(filename, i)
                        f.write(f"{filename} → {new_filename}\n")

                QMessageBox.information(
                    self, "Success", f"Results exported to {file_path}"
                )
            except OSError as error:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to export results: {error}",
                )

    def _get_current_rename_mode(self):
        """Get the currently selected rename mode."""
        if self.add_prefix_radio.isChecked():
            return "add_prefix"
        elif self.add_suffix_radio.isChecked():
            return "add_suffix"
        elif self.lowercase_radio.isChecked():
            return "lowercase"
        elif self.uppercase_radio.isChecked():
            return "uppercase"
        elif self.replace_radio.isChecked():
            return "replace_text"
        elif self.number_radio.isChecked():
            return "add_numbers"
        return "unknown"

    def show_preferences(self):
        """Show Rename tool preferences."""
        QMessageBox.information(
            self,
            "Rename Preferences",
            "Rename tool preferences:\n\n"
            "• Default rename patterns\n"
            "• Backup options\n"
            "• Confirmation settings\n"
            "• Undo functionality\n\n"
            "Advanced preferences coming soon!",
        )

    def refresh_view(self):
        """Refresh the current file lists."""
        if self.current_directory:
            self.load_available_files()
        else:
            QMessageBox.information(
                self, "Refresh", "Select a directory first to refresh."
            )

    def init_ui(self):
        """Initialize the user interface."""
        # Use the existing main layout from StandardWindow
        layout = self.main_layout

        # Create header
        header_label = _ui_widget(QLabel, 'Legacy.s5f55581f0c8d87a9', 'setText')
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

        # Create directory selection
        dir_group = _ui_widget(QGroupBox, 'Legacy.s30d2d5574cce5ea3', 'setTitle')
        dir_layout = QGridLayout(dir_group)

        dir_layout.addWidget(_ui_widget(QLabel, 'Legacy.s8b94846044eb0de0', 'setText'), 0, 0)
        self.directory_edit = TextInput("Directory", "Select a directory...")
        _ui_bind(self.directory_edit, 'setAccessibleName', 'Legacy.s72eeb3af14bc699d')
        dir_layout.addWidget(self.directory_edit, 0, 1)

        self.browse_button = _ui_widget(SecondaryButton, 'Legacy.s3227aa9666253f7a', 'setText')
        _ui_bind(self.browse_button, 'setAccessibleName', 'Legacy.s55a4a57a001cd95e')
        self.browse_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_button, 0, 2)

        layout.addWidget(dir_group)

        # Create file selection area
        files_group = _ui_widget(QGroupBox, 'Legacy.s1eef7fd26962e3d2', 'setTitle')
        files_layout = QVBoxLayout(files_group)

        # Available files list
        files_layout.addWidget(_ui_widget(QLabel, 'Legacy.s831847e031a26f24', 'setText'))
        self.available_files_list = QListWidget()
        _ui_bind(self.available_files_list, 'setAccessibleName', 'Legacy.sdd2881425094e81a')
        self.available_files_list.setMaximumHeight(150)
        files_layout.addWidget(self.available_files_list)

        # Selection buttons
        selection_layout = QHBoxLayout()

        self.add_button = _ui_widget(SecondaryButton, 'Legacy.sc78a147b59179b48', 'setText')
        _ui_bind(self.add_button, 'setAccessibleName', 'Legacy.sf57c0fa94afdcec4')
        self.add_button.clicked.connect(self.add_selected_files)
        selection_layout.addWidget(self.add_button)

        self.add_all_button = _ui_widget(SecondaryButton, 'Legacy.s8b5bded9faec1968', 'setText')
        _ui_bind(self.add_all_button, 'setAccessibleName', 'Legacy.sf89c3e74184515ac')
        self.add_all_button.clicked.connect(self.add_all_files)
        selection_layout.addWidget(self.add_all_button)

        self.remove_button = _ui_widget(SecondaryButton, 'Legacy.s0f8db0108fe749c5', 'setText')
        _ui_bind(self.remove_button, 'setAccessibleName', 'Legacy.sc9922ef399e6a233')
        self.remove_button.clicked.connect(self.remove_selected_files)
        selection_layout.addWidget(self.remove_button)

        self.clear_button = _ui_widget(SecondaryButton, 'Legacy.s9b563883720a6d60', 'setText')
        _ui_bind(self.clear_button, 'setAccessibleName', 'Legacy.s1561d4d08c3d2989')
        self.clear_button.clicked.connect(self.clear_selected_files)
        selection_layout.addWidget(self.clear_button)

        files_layout.addLayout(selection_layout)

        # Selected files list
        files_layout.addWidget(_ui_widget(QLabel, 'Legacy.s4ca844978c7dc9dd', 'setText'))
        self.selected_files_list = QListWidget()
        _ui_bind(self.selected_files_list, 'setAccessibleName', 'Legacy.s0e5c35ee8b676500')
        self.selected_files_list.setMaximumHeight(150)
        files_layout.addWidget(self.selected_files_list)

        layout.addWidget(files_group)

        # Create rename options
        options_group = _ui_widget(QGroupBox, 'Legacy.s39b10e9a29841c96', 'setTitle')
        options_layout = QGridLayout(options_group)

        # Create button group for radio buttons
        self.rename_mode_group = QButtonGroup()

        # Prefix/Suffix options
        self.add_prefix_radio = _ui_widget(QRadioButton, 'Legacy.s182a68245f9789e6', 'setText')
        _ui_bind(self.add_prefix_radio, 'setAccessibleName', 'Legacy.s240cbb1307347567')
        self.add_prefix_radio.setMinimumHeight(44)
        self.add_prefix_radio.setChecked(True)
        self.rename_mode_group.addButton(self.add_prefix_radio)
        options_layout.addWidget(self.add_prefix_radio, 0, 0)

        self.prefix_edit = TextInput("Prefix", "Enter prefix text...")
        _ui_bind(self.prefix_edit, 'setAccessibleName', 'Legacy.sd97d9b8988afe028')
        options_layout.addWidget(self.prefix_edit, 0, 1)

        self.add_suffix_radio = _ui_widget(QRadioButton, 'Legacy.s6ddf5c79ee1dfa9a', 'setText')
        _ui_bind(self.add_suffix_radio, 'setAccessibleName', 'Legacy.sd9787dc47c1a07e3')
        self.add_suffix_radio.setMinimumHeight(44)
        self.rename_mode_group.addButton(self.add_suffix_radio)
        options_layout.addWidget(self.add_suffix_radio, 1, 0)

        self.suffix_edit = TextInput("Suffix", "Enter suffix text...")
        _ui_bind(self.suffix_edit, 'setAccessibleName', 'Legacy.sb0fcda05d0078834')
        options_layout.addWidget(self.suffix_edit, 1, 1)

        # Case options
        self.lowercase_radio = _ui_widget(QRadioButton, 'Legacy.sfbb7deb2d599740d', 'setText')
        _ui_bind(self.lowercase_radio, 'setAccessibleName', 'Legacy.s00ae4f689e971322')
        self.lowercase_radio.setMinimumHeight(44)
        self.rename_mode_group.addButton(self.lowercase_radio)
        options_layout.addWidget(self.lowercase_radio, 2, 0)

        self.uppercase_radio = _ui_widget(QRadioButton, 'Legacy.s02ac8ba71d0c9a15', 'setText')
        _ui_bind(self.uppercase_radio, 'setAccessibleName', 'Legacy.s9059efb6621c59e0')
        self.uppercase_radio.setMinimumHeight(44)
        self.rename_mode_group.addButton(self.uppercase_radio)
        options_layout.addWidget(self.uppercase_radio, 2, 1)

        # Replace text
        self.replace_radio = _ui_widget(QRadioButton, 'Legacy.sd787ee0ab6591e53', 'setText')
        _ui_bind(self.replace_radio, 'setAccessibleName', 'Legacy.s9fe3082493dc6e19')
        self.replace_radio.setMinimumHeight(44)
        self.rename_mode_group.addButton(self.replace_radio)
        options_layout.addWidget(self.replace_radio, 3, 0)

        replace_layout = QHBoxLayout()
        self.find_edit = TextInput("Find", "Find...")
        _ui_bind(self.find_edit, 'setAccessibleName', 'Legacy.se0a02dca02f51360')
        _ui_bind(self.find_edit, 'setAccessibleDescription', 'Legacy.s0ccaa220495e6b18')
        replace_layout.addWidget(self.find_edit)

        replace_layout.addWidget(_ui_widget(QLabel, 'Legacy.s161660030aa6c9e3', 'setText'))

        self.replace_edit = TextInput("Replace", "Replace with...")
        _ui_bind(self.replace_edit, 'setAccessibleName', 'Legacy.s3ac0bda4a8d1cdfb')
        _ui_bind(self.replace_edit, 'setAccessibleDescription', 'Legacy.saf09041a90767dd7')
        replace_layout.addWidget(self.replace_edit)

        options_layout.addLayout(replace_layout, 3, 1)

        # Number sequence
        self.number_radio = _ui_widget(QRadioButton, 'Legacy.seb67640ea5cb60b8', 'setText')
        _ui_bind(self.number_radio, 'setAccessibleName', 'Legacy.sd5ae73aabca628a3')
        self.number_radio.setMinimumHeight(44)
        self.rename_mode_group.addButton(self.number_radio)
        options_layout.addWidget(self.number_radio, 4, 0)

        number_layout = QHBoxLayout()
        number_layout.addWidget(_ui_widget(QLabel, 'Legacy.s84cc09ea4cfa63fc', 'setText'))
        self.start_number_edit = TextInput("Start", "1")
        _ui_bind(self.start_number_edit, 'setAccessibleName', 'Legacy.sa5e94f21be45b535')
        self.start_number_edit.setMaximumWidth(60)
        number_layout.addWidget(self.start_number_edit)

        number_layout.addWidget(_ui_widget(QLabel, 'Legacy.s9a5649a42cb2fcef', 'setText'))
        self.number_format_edit = TextInput("Format", "_{:03d}")
        _ui_bind(self.number_format_edit, 'setAccessibleName', 'Legacy.scfbda029995b9209')
        number_layout.addWidget(self.number_format_edit)

        options_layout.addLayout(number_layout, 4, 1)

        layout.addWidget(options_group)

        # Create preview and action area
        action_group = _ui_widget(QGroupBox, 'Legacy.sfb9b8f6840f0f91f', 'setTitle')
        action_layout = QVBoxLayout(action_group)

        # Preview button
        self.preview_button = _ui_widget(SecondaryButton, 'Legacy.s7808a60612cdcbda', 'setText')
        _ui_bind(self.preview_button, 'setAccessibleName', 'Legacy.s378ddcdcf4bc1336')
        self.preview_button.clicked.connect(self.preview_changes)
        action_layout.addWidget(self.preview_button)

        # Preview text
        self.preview_text = QTextEdit()
        _ui_bind(self.preview_text, 'setAccessibleName', 'Legacy.s04da12d0c300cb4b')
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        action_layout.addWidget(self.preview_text)

        # Rename button
        self.rename_button = _ui_widget(PrimaryButton, 'Legacy.s2a7695ad787a136e', 'setText')
        _ui_bind(self.rename_button, 'setAccessibleName', 'Legacy.s996e6602d8ae5724')
        self.rename_button.clicked.connect(self.apply_rename)
        self.rename_button.setStyleSheet(
            """
            QPushButton {
                background-color: {token('semantic_error')};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;

            }
            QPushButton:hover {
                background-color: {token('semantic_error')};
            }
            QPushButton:disabled {
                background-color: {token('text_disabled')};
            }
        """
        )
        font_tokens.bind(self.rename_button, "font.body")
        action_layout.addWidget(self.rename_button)

        layout.addWidget(action_group)

    def browse_directory(self):
        """Open directory selection dialog."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.current_directory
        )
        if directory:
            self.current_directory = directory
            self.directory_edit.setText(directory)
            self.load_available_files()

    def load_available_files(self):
        """Load files from the selected directory."""
        self.available_files_list.clear()
        self.selected_files_list.clear()
        self.selected_files = []

        if not self.current_directory:
            return

        if not os.path.isdir(self.current_directory):
            QMessageBox.warning(
                self,
                "Directory Error",
                "The selected directory could not be found.\n"
                "Please verify it still exists before trying again.",
            )
            self.current_directory = ""
            self.directory_edit.clear()
            return

        try:
            for filename in sorted(os.listdir(self.current_directory)):
                file_path = os.path.join(self.current_directory, filename)
                if os.path.isfile(file_path):
                    item = QListWidgetItem(filename)
                    self.available_files_list.addItem(item)
        except OSError as error:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not load directory: {error}",
            )

    def add_selected_files(self):
        """Add selected files to rename list."""
        for item in self.available_files_list.selectedItems():
            filename = item.text()
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self.selected_files_list.addItem(QListWidgetItem(filename))

    def add_all_files(self):
        """Add all files to rename list."""
        for i in range(self.available_files_list.count()):
            filename = self.available_files_list.item(i).text()
            if filename not in self.selected_files:
                self.selected_files.append(filename)
                self.selected_files_list.addItem(QListWidgetItem(filename))

    def remove_selected_files(self):
        """Remove selected files from rename list."""
        for item in self.selected_files_list.selectedItems():
            filename = item.text()
            if filename in self.selected_files:
                self.selected_files.remove(filename)
                row = self.selected_files_list.row(item)
                self.selected_files_list.takeItem(row)

    def clear_selected_files(self):
        """Clear all selected files."""
        self.selected_files = []
        self.selected_files_list.clear()

    def get_new_filename(self, original_filename, index=0):
        """Generate new filename based on selected options."""
        name, ext = os.path.splitext(original_filename)

        if self.add_prefix_radio.isChecked():
            prefix = self.prefix_edit.text()
            return f"{prefix}{original_filename}"

        elif self.add_suffix_radio.isChecked():
            suffix = self.suffix_edit.text()
            return f"{name}{suffix}{ext}"

        elif self.lowercase_radio.isChecked():
            return original_filename.lower()

        elif self.uppercase_radio.isChecked():
            return original_filename.upper()

        elif self.replace_radio.isChecked():
            find_text = self.find_edit.text()
            replace_text = self.replace_edit.text()
            if find_text:
                return original_filename.replace(find_text, replace_text)

        elif self.number_radio.isChecked():
            try:
                start_num = int(self.start_number_edit.text())
                format_str = self.number_format_edit.text()
                number = start_num + index
                number_part = format_str.format(number)
                return f"{name}{number_part}{ext}"
            except (ValueError, KeyError):
                return original_filename

        return original_filename

    def preview_changes(self):
        """Preview the rename changes."""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", NO_FILES_SELECTED_MESSAGE)
            return

        preview_text = "Rename Preview:\n" + "=" * 50 + "\n"

        for i, filename in enumerate(self.selected_files):
            new_filename = self.get_new_filename(filename, i)
            preview_text += f"{filename} → {new_filename}\n"

        self.preview_text.setText(preview_text)

    def _rename_task(self):
        if not hasattr(self, '_background_rename'):
            from src.gui.background_task import BackgroundTask
            from PyQt5.QtWidgets import QAbstractButton, QLineEdit
            controls = self.findChildren(QAbstractButton) + self.findChildren(QLineEdit)
            self._background_rename = BackgroundTask(self, 'rename-files', self.main_layout, controls)
        return self._background_rename

    def apply_rename(self):
        """Validate the entire proposal before showing a safe-default confirmation."""
        if not self.selected_files:
            return
        from src.core.rename_operations import plan_renames
        directory = self.current_directory
        pairs = [(name, self.get_new_filename(name, index)) for index, name in enumerate(self.selected_files)]
        self._rename_task().start('preview', lambda: plan_renames(directory, pairs), self._confirm_rename_plan)

    def _confirm_rename_plan(self, plan):
        from src.gui.components import ConfirmationModal
        from PyQt5.QtWidgets import QDialog
        if not plan:
            return
        summary = '\n'.join(f"{item.source.name} → {item.target.name}" for item in plan[:100])
        self.preview_text.setPlainText(summary)
        if ConfirmationModal("Apply Rename", f"Files: {len(plan)}\n{summary}",
                             confirm_text="Rename", parent=self).exec_() != QDialog.Accepted:
            return
        from src.core.rename_operations import execute_renames
        task = self._rename_task()
        def completed(result):
            self._rename_undo, errors = result
            self.preview_text.setPlainText(f"Renamed: {len(self._rename_undo)}\n" + '\n'.join(errors))
            self.load_available_files()
        task.start('rename', lambda: execute_renames(plan, task.cancel), completed)

    def can_undo(self):
        return bool(self._rename_undo)

    def undo(self):
        if self._rename_undo:
            self._confirm_rename_plan(self._rename_undo)


def main():
    """Main function for standalone execution."""
    app = QApplication(sys.argv)
    window = RenameWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
