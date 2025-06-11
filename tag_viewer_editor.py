import mutagen
import mutagen.id3
import mutagen.flac
import mutagen.mp3
import mutagen.mp4
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5 import uic

class TagViewerEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI
        uic.loadUi('tag_viewer_editor.ui', self)
        
        # Initialize the metadata model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Tag', 'Value'])
        self.metadataTable.setModel(self.model)
        self.metadataTable.horizontalHeader().setStretchLastSection(True)
        
        # Connect signals
        self.actionOpen.triggered.connect(self.browse_file)
        self.actionExit.triggered.connect(self.close)
        self.browseButton.clicked.connect(self.browse_file)
        self.updateButton.clicked.connect(self.update_tag)
        self.metadataTable.clicked.connect(self.on_table_click)
        
        # Initialize current file
        self.current_file = None
        self.current_tags = None
        
        self.show()
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio/Video File",
            "",
            "Audio/Video Files (*.mp3 *.flac *.m4a *.mp4 *.aac);;All Files (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.filePathEdit.setText(file_path)
            self.load_metadata()
    
    def load_metadata(self):
        try:
            self.current_tags = mutagen.File(self.current_file, easy=True)
            if self.current_tags is None:
                QMessageBox.warning(self, "Error", "File format not supported or file does not exist.")
                return
            
            # Clear the model
            self.model.removeRows(0, self.model.rowCount())
            
            # Add metadata to the table
            for key, value in self.current_tags.items():
                self.model.appendRow([
                    QStandardItem(str(key)),
                    QStandardItem(str(value))
                ])
                
            self.statusbar.showMessage("Metadata loaded successfully")
        except mutagen.MutagenError as e:
            QMessageBox.critical(self, "Error", f"Could not load metadata: {str(e)}")
    
    def update_tag(self):
        if not self.current_file or not self.current_tags:
            QMessageBox.warning(self, "Warning", "Please open a file first")
            return
        
        key = self.keyEdit.text().strip()
        value = self.valueEdit.text().strip()
        
        if not key or not value:
            QMessageBox.warning(self, "Warning", "Please enter both tag name and value")
            return
            
        try:
            self.current_tags[key] = value
            self.current_tags.save()
            self.load_metadata()  # Reload to show changes
            self.keyEdit.clear()
            self.valueEdit.clear()
            self.statusbar.showMessage("Tag updated successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not update tag: {str(e)}")
    
    def on_table_click(self, index):
        if index.isValid():
            key = self.model.item(index.row(), 0).text()
            value = self.model.item(index.row(), 1).text()
            self.keyEdit.setText(key)
            self.valueEdit.setText(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TagViewerEditor()
    sys.exit(app.exec_())
