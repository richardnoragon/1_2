import os
import sys
import shutil
from datetime import datetime
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic

from gui.common.base_window import BaseWindow
from gui.common.dialogs import show_error_dialog, get_existing_directory

# Get the directory containing the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class SyncWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    preview = pyqtSignal(str, str, str)  # action, source, target

    def __init__(self, source_files, target_files, source_dir, target_dir,
                 options):
        super().__init__()
        self.source_files = source_files
        self.target_files = target_files
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.options = options
        self.running = True

    def backup_file(self, file_path):
        if not self.options['backup']:
            return
        backup_path = f"{file_path}.bak"
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            base_name = os.path.basename(backup_path)
            self.status.emit(f"Backup created: {base_name}")

    def should_copy_file(self, src_path, tgt_path):
        if not os.path.exists(tgt_path):
            return True, "new"
            
        src_time = os.path.getmtime(src_path)
        tgt_time = os.path.getmtime(tgt_path)
        
        if src_time == tgt_time:
            return False, "identical"
            
        if self.options['conflict_resolution'] == 'newest':
            is_newer = src_time > tgt_time
            return is_newer, "newer" if is_newer else "older"
        elif self.options['conflict_resolution'] == 'source':
            return True, "source wins"
        elif self.options['conflict_resolution'] == 'target':
            return False, "target wins"
        
        return False, "skipped"

    def run(self):
        try:
            if self.options['sync_mode'] == 'mirror':
                self.mirror_sync()
            elif self.options['sync_mode'] == 'update':
                self.update_sync()
            else:  # two-way sync
                self.two_way_sync()

            if not self.options['dry_run']:
                self.status.emit("Synchronization complete!")
            else:
                self.status.emit("Dry run complete - no files were modified")
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def mirror_sync(self):
        total_files = len(self.source_files)
        for idx, file in enumerate(self.source_files):
            if not self.running:
                return
                
            source_path = os.path.join(self.source_dir, file)
            target_path = os.path.join(self.target_dir, file)
            
            should_copy, reason = self.should_copy_file(source_path, target_path)
            
            if should_copy:
                self.preview.emit("COPY", source_path, target_path)
                if not self.options['dry_run']:
                    self.backup_file(target_path)
                    shutil.copy2(source_path, target_path)
                    self.status.emit(f"Copied: {file}")
            
            # Remove files in target that don't exist in source
            for file in self.target_files:
                if file not in self.source_files:
                    target_path = os.path.join(self.target_dir, file)
                    self.preview.emit("DELETE", "", target_path)
                    if not self.options['dry_run']:
                        os.remove(target_path)
                        self.status.emit(f"Deleted: {file}")
            
            self.progress.emit(int((idx + 1) * 100 / total_files))

    def update_sync(self):
        total_files = len(self.source_files)
        for idx, file in enumerate(self.source_files):
            if not self.running:
                return
                
            source_path = os.path.join(self.source_dir, file)
            target_path = os.path.join(self.target_dir, file)
            
            should_copy, reason = self.should_copy_file(source_path, target_path)
            
            if should_copy and (not self.options['skip_newer'] or reason == "new"):
                self.preview.emit("COPY", source_path, target_path)
                if not self.options['dry_run']:
                    self.backup_file(target_path)
                    shutil.copy2(source_path, target_path)
                    self.status.emit(f"Copied: {file}")
            
            self.progress.emit(int((idx + 1) * 100 / total_files))

    def two_way_sync(self):
        all_files = set(self.source_files) | set(self.target_files)
        total_files = len(all_files)
        
        for idx, file in enumerate(all_files):
            if not self.running:
                return
                
            source_path = os.path.join(self.source_dir, file)
            target_path = os.path.join(self.target_dir, file)
            
            # File exists only in source
            if file in self.source_files and file not in self.target_files:
                self.preview.emit("COPY", source_path, target_path)
                if not self.options['dry_run']:
                    shutil.copy2(source_path, target_path)
                    self.status.emit(f"Copied to target: {file}")
            
            # File exists only in target
            elif file in self.target_files and file not in self.source_files:
                self.preview.emit("COPY", target_path, source_path)
                if not self.options['dry_run']:
                    shutil.copy2(target_path, source_path)
                    self.status.emit(f"Copied to source: {file}")
            
            # File exists in both
            else:
                source_time = os.path.getmtime(source_path)
                target_time = os.path.getmtime(target_path)
                
                if source_time > target_time:
                    self.preview.emit("COPY", source_path, target_path)
                    if not self.options['dry_run']:
                        self.backup_file(target_path)
                        shutil.copy2(source_path, target_path)
                        self.status.emit(f"Updated target: {file}")
                elif target_time > source_time:
                    self.preview.emit("COPY", target_path, source_path)
                    if not self.options['dry_run']:
                        self.backup_file(source_path)
                        shutil.copy2(target_path, source_path)
                        self.status.emit(f"Updated source: {file}")
            
            self.progress.emit(int((idx + 1) * 100 / total_files))

    def stop(self):
        self.running = False


class SyncGUI(BaseWindow):
    def __init__(self):
        super().__init__()
        ui_file = os.path.join(SCRIPT_DIR, 'sync.ui')
        uic.loadUi(ui_file, self)

        # Initialize models
        self.left_model = QStandardItemModel()
        self.right_model = QStandardItemModel()
        self.left_listView.setModel(self.left_model)
        self.right_listView.setModel(self.right_model)

        # Setup menu actions
        self.actionExit = self.menuExit.addAction("Exit")
        self.actionExit.setShortcut("Ctrl+Q")
        self.actionExit.triggered.connect(self.close)

        # Connect buttons with shorter line lengths
        self.select_left_pushButton.clicked.connect(
            lambda: self.select_directory('left'))
        self.select_right_pushButton.clicked.connect(
            lambda: self.select_directory('right'))
        self.compare_pushButton.clicked.connect(self.compare_directories)
        self.sync_pushButton.clicked.connect(self.sync_directories)

        # Initialize variables
        self.left_dir = ""
        self.right_dir = ""
        self.sync_worker = None

        # Initial state
        self.sync_pushButton.setEnabled(False)
        self.compare_pushButton.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.show()

    def select_directory(self, side):
        directory = get_existing_directory(self, "Select Directory")
        if directory:
            if side == 'left':
                self.left_dir = directory
                self.left_directory_label.setText(directory)
                self.update_file_list(self.left_model, directory)
            else:
                self.right_dir = directory
                self.right_directory_label.setText(directory)
                self.update_file_list(self.right_model, directory)

            # Enable compare if both directories are selected
            both_dirs = bool(self.left_dir and self.right_dir)
            self.compare_pushButton.setEnabled(both_dirs)

    def update_file_list(self, model, directory):
        model.clear()
        try:
            files = sorted(os.listdir(directory))
            for file in files:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    item = QStandardItem(file)
                    item.setToolTip(self.get_file_info(file_path))
                    model.appendRow(item)
        except OSError as e:
            msg = f"Could not read directory: {str(e)}"
            show_error_dialog(
                message=msg,
                title="Error",
                parent=self
            )

    def get_file_info(self, file_path):
        try:
            stats = os.stat(file_path)
            modified = datetime.fromtimestamp(
                stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            size = self.format_size(stats.st_size)
            return f"Size: {size}\nModified: {modified}"
        except OSError:
            return "Could not read file info"

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def compare_directories(self):
        if not (self.left_dir and self.right_dir):
            return

        try:
            left_files = set(os.listdir(self.left_dir))
            right_files = set(os.listdir(self.right_dir))
            
            # Reset models
            self.left_model.clear()
            self.right_model.clear()

            # Process all files
            all_files = sorted(left_files.union(right_files))
            for file in all_files:
                left_path = os.path.join(self.left_dir, file)
                right_path = os.path.join(self.right_dir, file)

                # Add to left list
                self._add_list_item(
                    file, left_path, right_path,
                    file in left_files, file in right_files,
                    self.left_model, is_left=True
                )

                # Add to right list
                self._add_list_item(
                    file, right_path, left_path,
                    file in right_files, file in left_files,
                    self.right_model, is_left=False
                )

            self.sync_pushButton.setEnabled(True)
            self.status_label.setText("Comparison complete - Ready to sync")
        except OSError as e:
            msg = f"Error comparing directories: {str(e)}"
            show_error_dialog(
                message=msg,
                title="Error",
                parent=self
            )

    def _add_list_item(self, file, path1, path2, in_first, in_second,
                      model, is_left):
        if not in_first:
            return

        item = QStandardItem(file)
        if not in_second:
            # Blue for new files
            item.setForeground(QColor("#2196F3"))
            item.setToolTip("New file")
        elif os.path.exists(path1) and os.path.exists(path2):
            time1 = os.path.getmtime(path1)
            time2 = os.path.getmtime(path2)
            if time1 > time2:
                # Green for newer files
                item.setForeground(QColor("#4CAF50"))
                item.setToolTip("Newer version")
            elif time1 < time2:
                # Orange for older files
                item.setForeground(QColor("#FF5722"))
                item.setToolTip("Older version")
        model.appendRow(item)

    def get_sync_options(self):
        # Get sync mode
        if self.mirror_radio.isChecked():
            sync_mode = 'mirror'
        elif self.update_radio.isChecked():
            sync_mode = 'update'
        else:
            sync_mode = 'two-way'
            
        # Get conflict resolution
        if self.source_radio.isChecked():
            conflict_resolution = 'source'
        elif self.target_radio.isChecked():
            conflict_resolution = 'target'
        else:
            conflict_resolution = 'newest'
            
        return {
            'sync_mode': sync_mode,
            'conflict_resolution': conflict_resolution,
            'backup': self.backup_checkbox.isChecked(),
            'dry_run': self.dry_run_checkbox.isChecked(),
            'skip_newer': self.skip_newer_checkbox.isChecked()
        }

    def sync_directories(self):
        if not (self.left_dir and self.right_dir):
            return

        options = self.get_sync_options()
        message = ["Please confirm the following sync operation:\n"]
        
        if options['sync_mode'] == 'mirror':
            message.append(
                "- Mirror Mode: Target will be made identical to source")
        elif options['sync_mode'] == 'update':
            message.append("- Update Mode: Only copy newer files to target")
        else:
            message.append(
                "- Two-Way Sync: Both directories will be synchronized")
            
        message.append(
            f"- Conflict Resolution: {options['conflict_resolution'].title()}")
        
        if options['backup']:
            message.append("- Backup files will be created before overwriting")
        if options['dry_run']:
            message.append("- DRY RUN: No files will be modified")
        if options['skip_newer']:
            message.append("- Existing newer files will be skipped")
            
        message.append("\nContinue with these settings?")

        reply = QMessageBox.question(
            self,
            "Confirm Sync",
            "\n".join(message),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                left_files = [
                    f for f in os.listdir(self.left_dir)
                    if os.path.isfile(os.path.join(self.left_dir, f))
                ]
                right_files = [
                    f for f in os.listdir(self.right_dir)
                    if os.path.isfile(os.path.join(self.right_dir, f))
                ]

                self.sync_worker = SyncWorker(
                    left_files,
                    right_files,
                    self.left_dir,
                    self.right_dir,
                    options
                )
                                            
                self.sync_worker.progress.connect(self.progress_bar.setValue)
                self.sync_worker.status.connect(self.status_label.setText)
                self.sync_worker.error.connect(self.handle_error)
                self.sync_worker.finished.connect(self.sync_finished)
                self.sync_worker.preview.connect(self.show_preview)

                # Disable UI elements during sync
                self.sync_pushButton.setEnabled(False)
                self.compare_pushButton.setEnabled(False)
                self.select_left_pushButton.setEnabled(False)
                self.select_right_pushButton.setEnabled(False)
                
                # Disable options during sync
                self.sync_mode_group.setEnabled(False)
                self.conflict_group.setEnabled(False)
                self.additional_options_group.setEnabled(False)

                self.sync_worker.start()

            except OSError as e:
                msg = f"Error starting sync: {str(e)}"
                show_error_dialog(
                    message=msg,
                    title="Error",
                    parent=self
                )

    def show_preview(self, action, source, target):
        if action == "COPY":
            msg = (f"Would copy: {os.path.basename(source)} -> "
                  f"{os.path.basename(target)}")
            self.status_label.setText(msg)
        elif action == "DELETE":
            msg = f"Would delete: {os.path.basename(target)}"
            self.status_label.setText(msg)

    def sync_finished(self):
        # Re-enable all UI elements
        self.sync_pushButton.setEnabled(True)
        self.compare_pushButton.setEnabled(True)
        self.select_left_pushButton.setEnabled(True)
        self.select_right_pushButton.setEnabled(True)
        
        # Re-enable options
        self.sync_mode_group.setEnabled(True)
        self.conflict_group.setEnabled(True)
        self.additional_options_group.setEnabled(True)
        
        self.compare_directories()  # Refresh the comparison

    def handle_error(self, error_msg):
        show_error_dialog(
            message=f"Sync error: {error_msg}",
            title="Error",
            parent=self
        )
        self.sync_finished()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    window = SyncGUI()
    window.show()  # Make sure window stays alive
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
