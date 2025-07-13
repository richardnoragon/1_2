import os
import sys
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import uic
from gui.common.base_window import BaseWindow
from gui.common.dialogs import show_error_dialog, show_info_dialog, get_open_file_names

from core.error_handler import error_handler


class FilePermissionsGUI(BaseWindow):
    """A class that handles file permissions g u i and inherits from BaseWindow."""
    def __init__(self):
        """init."""
        super().__init__()
        uic.loadUi('permissions_editor.ui', self)
        
        # Setup model and list view
        self.model = QStandardItemModel()
        self.select_ListView.setModel(self.model)
        self.select_ListView.setAcceptDrops(True)
        self.select_ListView.setDragEnabled(True)
        
        # Connect signals
        self.select_button.clicked.connect(self.select_files)
        self.apply_permissions_button.clicked.connect(self.set_permissions)
        self.action_Exit.triggered.connect(self.close)  # Connect Exit action
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Add tooltips
        self.apply_permissions_button.setToolTip("Apply the selected permissions to all files in the list")
        self.select_ListView.setToolTip("Drag and drop files here or use the Select Files button")
        
        self.show()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """dragenterevent.
        Args:
            event (QDragEnterEvent): Description of event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """dropevent.
        Args:
            event (QDropEvent): Description of event"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.add_files(files)
        
    def select_files(self):
        """selectfiles."""
        files = get_open_file_names(
            self,
            "Select Files",
            "",
            "All Files (*.*)"
        )
        if files:
            self.add_files(files)
            
    def add_files(self, files):
        """addfiles.
        Args:
            files (Any): Description of files"""
        for file in files:
            if not self.model.findItems(file):
                item = QStandardItem(file)
                self.model.appendRow(item)
                self.update_file_permissions(file)
                
    def update_file_permissions(self, file):
        """updatefilepermissions.
        Args:
            file (Any): Description of file"""
        try:
            self.read_checkBox.setChecked(os.access(file, os.R_OK))
            self.write_checkBox.setChecked(os.access(file, os.W_OK))
            self.execute_checkBox.setChecked(os.access(file, os.X_OK))
        except Exception as e:
            show_error_dialog(self, "Error", f"Could not read permissions for {file}: {str(e)}")

    def set_permissions(self):
        """setpermissions."""
        if self.model.rowCount() == 0:
            show_info_dialog(self, "No Files", "Please add files to modify their permissions")
            return
            
        permissions = 0
        if self.read_checkBox.isChecked():
            permissions |= os.R_OK
        if self.write_checkBox.isChecked():
            permissions |= os.W_OK
        if self.execute_checkBox.isChecked():
            permissions |= os.X_OK
            
        success_count = 0
        failed_files = []
        
        for row in range(self.model.rowCount()):
            file_path = self.model.item(row).text()
            try:
                current_mode = os.stat(file_path).st_mode
                # Preserve other bits, only modify user permission bits
                new_mode = (current_mode & 0o777777) | permissions
                os.chmod(file_path, new_mode)
                success_count += 1
            except Exception as e:
                failed_files.append(f"{file_path}: {str(e)}")
                
        # Show results
        if failed_files:
            show_error_dialog(
                self,
                "Permissions Update Result",
                f"Successfully updated {success_count} file(s).\n\nFailed to update:\n" + "\n".join(failed_files)
            )
        else:
            show_info_dialog(
                self,
                "Success",
                f"Successfully updated permissions for {success_count} file(s)"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern style
    gui = FilePermissionsGUI()
    sys.exit(app.exec_())
