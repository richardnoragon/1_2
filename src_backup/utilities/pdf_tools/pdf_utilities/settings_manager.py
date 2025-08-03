import json
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox, QFileDialog
from config_manager import ConfigManager
from log_config import setup_logger

logger = setup_logger(__name__)


class SettingsManagerUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(SettingsManagerUI, self).__init__()
        self.config_manager = ConfigManager()
        
        # Load UI
        uic.loadUi('settings_manager.ui', self)
        
        # Connect signals
        self.settingsTree.itemClicked.connect(self.on_item_selected)
        self.saveButton.clicked.connect(self.save_setting)
        self.exportButton.clicked.connect(self.export_settings)
        self.importButton.clicked.connect(self.import_settings)
        
        # Populate settings tree
        self.refresh_settings_tree()
        
        self.show()
    
    def refresh_settings_tree(self):
        """Refresh the settings tree with current configuration"""
        try:
            self.settingsTree.clear()
            
            # Add all module settings to tree
            for module, settings in self.config_manager.config.items():
                module_item = QTreeWidgetItem([module])
                self.settingsTree.addTopLevelItem(module_item)
                
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        setting_item = QTreeWidgetItem([key, str(value)])
                        module_item.addChild(setting_item)
            
            self.settingsTree.expandAll()
            logger.debug("Settings tree refreshed successfully")
            
        except Exception as e:
            logger.error("Failed to refresh settings tree: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh settings: {str(e)}"
            )
    
    def on_item_selected(self, item, column):
        """Handle tree item selection"""
        try:
            parent = item.parent()
            
            if parent:  # This is a setting item
                self.moduleEdit.setText(parent.text(0))
                self.keyEdit.setText(item.text(0))
                self.valueEdit.setText(item.text(1))
            else:  # This is a module item
                self.moduleEdit.setText(item.text(0))
                self.keyEdit.clear()
                self.valueEdit.clear()
                
        except Exception as e:
            logger.error("Error handling item selection: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Error handling selection: {str(e)}"
            )
    
    def save_setting(self):
        """Save the current setting"""
        try:
            module = self.moduleEdit.text()
            key = self.keyEdit.text()
            value = self.valueEdit.text()
            
            if not all([module, key, value]):
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please fill in all fields"
                )
                return
            
            # Try to convert string value to appropriate type
            try:
                # Try to parse as JSON first (for lists, dicts, numbers, bools)
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # If not valid JSON, keep as string
                parsed_value = value
            
            self.config_manager.set_setting(module, key, parsed_value)
            self.refresh_settings_tree()
            QMessageBox.information(
                self,
                "Success",
                "Setting saved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to save setting: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save setting: {str(e)}"
            )
    
    def export_settings(self):
        """Export settings to a JSON file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Settings",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.config_manager.config, f, indent=4)
                QMessageBox.information(
                    self,
                    "Success",
                    "Settings exported successfully"
                )
                logger.info("Settings exported to %s", file_path)
                
        except Exception as e:
            logger.error("Failed to export settings: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export settings: {str(e)}"
            )
    
    def import_settings(self):
        """Import settings from a JSON file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Settings",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_config = json.load(f)
                
                # Confirm import
                reply = QMessageBox.question(
                    self,
                    "Confirm Import",
                    "This will replace all current settings. Continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.config_manager.config = new_config
                    self.config_manager.save_config()
                    self.refresh_settings_tree()
                    QMessageBox.information(
                        self,
                        "Success",
                        "Settings imported successfully"
                    )
                    logger.info("Settings imported from %s", file_path)
                
        except Exception as e:
            logger.error("Failed to import settings: %s", str(e))
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to import settings: {str(e)}"
            )
