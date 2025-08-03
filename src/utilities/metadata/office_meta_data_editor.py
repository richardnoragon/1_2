import os
import sys
from typing import Optional
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from gui.common.base_window import BaseWindow
from gui.common.dialogs import (
    show_error_dialog, show_info_dialog, get_open_file_name
)
import docx


class OfficeMetaDataEditorGUI(BaseWindow):
    """A class that handles office meta data editor GUI and inherits
    from BaseWindow.
    """
    
    def __init__(self) -> None:
        """Initialize the Office metadata editor GUI."""
        super().__init__()
        # load the GUI's UI definition from the XML file
        uic.loadUi('office_meta_data_editor.ui', self)
        
        # Initialize instance variable for current file
        self.current_file: Optional[str] = None
        
        # create a model for the listview
        self.model = QStandardItemModel()
        self.select_ListView.setModel(self.model)
        
        # create models for metadata views
        self.title_model = QStandardItemModel()
        self.author_model = QStandardItemModel()
        self.created_model = QStandardItemModel()
        self.modified_model = QStandardItemModel()
        
        self.title_ListView.setModel(self.title_model)
        self.author_ListView.setModel(self.author_model)
        self.created_ListView.setModel(self.created_model)
        self.modified_ListView.setModel(self.modified_model)
        
        # connect the menu actions
        self.actionSelect_Files.triggered.connect(self.select)
        self.actionExit.triggered.connect(self.close)
        
        # connect the apply changes button
        self.apply_changes_button.clicked.connect(self.set_meta_data)
        
        self.show()

    def select(self) -> None:
        """Select an office document and load its metadata.
        
        Opens a file dialog to select a Word document and loads its metadata
        into the appropriate fields for editing.
        """
        try:
            file_name = get_open_file_name(
                self,
                'Select Office Document',
                '',
                "Office Documents (*.docx *.doc *.xlsx *.xls *.pptx *.ppt)"
            )
            
            if file_name:
                self.current_file = str(file_name)  # Convert Path to string
                self.model.clear()
                self.model.appendRow(QStandardItem(self.current_file))
                
                document = docx.Document(
                    str(file_name))  # Convert Path to string
                
                # Clear previous models
                self.title_model.clear()
                self.author_model.clear()
                self.created_model.clear()
                self.modified_model.clear()
                
                # Add metadata to models
                self.title_model.appendRow(QStandardItem(
                    str(document.core_properties.title or "")))
                self.author_model.appendRow(QStandardItem(
                    str(document.core_properties.author or "")))
                self.created_model.appendRow(QStandardItem(
                    str(document.core_properties.created or "")))
                self.modified_model.appendRow(QStandardItem(
                    str(document.core_properties.modified or "")))
                
        except Exception as e:
            show_error_dialog(self, "Error", f"Error opening file: {str(e)}")

    def set_meta_data(self) -> None:
        """Save the edited metadata back to the office document.
        
        Updates the document's core properties with the values from the
        GUI fields and saves the changes to the file.
        """
        try:
            if not self.current_file:
                show_error_dialog(
                    self, "Warning", "Please select a file first.")
                return
                
            document = docx.Document(
                str(self.current_file))  # Convert Path to string
            
            # Get text from the first item in each model
            title = (self.title_model.item(0).text()
                     if self.title_model.item(0) else "")
            author = (self.author_model.item(0).text()
                      if self.author_model.item(0) else "")
            
            # Update document properties
            document.core_properties.title = title
            document.core_properties.author = author
            
            # Save the changes
            document.save(str(self.current_file))  # Convert Path to string
            show_info_dialog(self, "Success",
                           "Metadata updated successfully!")
            
        except Exception as e:
            show_error_dialog(self, "Error",
                            f"Error updating metadata: {str(e)}")


def main() -> None:
    """Main function to run the Office metadata editor application."""
    app = QApplication(sys.argv)
    OfficeMetaDataEditorGUI()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
