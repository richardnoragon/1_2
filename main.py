#!/usr/bin/env python3
"""
Richard's File Utilities - Main Entry Point

This is the main entry point for the Richard's File Utilities application.
It provides a comprehensive GUI interface for accessing all file utility tools.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the enhanced PDF tools widget
try:
    from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget
    ENHANCED_PDF_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced PDF Tools not available: {e}")
    ENHANCED_PDF_TOOLS_AVAILABLE = False

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, 
        QWidget, QHBoxLayout, QGridLayout, QScrollArea, QFrame,
        QTabWidget, QGroupBox, QMessageBox
    )
    from PyQt5.QtCore import Qt, pyqtSlot
    from PyQt5.QtGui import QFont, QIcon
    
    class RFUMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Richard's File Utilities")
            self.setGeometry(200, 200, 900, 700)
            
            # Store references to opened windows
            self.opened_windows = {}
            
            self.init_ui()
        
        def init_ui(self):
            """Initialize the user interface."""
            # Create central widget and main layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            
            # Add title
            title_label = QLabel("Richard's File Utilities")
            title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            title_label.setStyleSheet("""
                font-size: 28px; 
                font-weight: bold; 
                padding: 20px;
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
                border-radius: 10px;
                margin: 10px;
            """)
            main_layout.addWidget(title_label)
            
            # Create tab widget for different tool categories
            tab_widget = QTabWidget()
            main_layout.addWidget(tab_widget)
            
            # File Management Tools
            file_mgmt_tab = self.create_tool_category_tab([
                ("File Finder", "Search and find files based on various criteria", self.open_file_finder),
                ("Catalog Files", "Create and manage file catalogs", self.open_catalog),
                ("Rename Files", "Batch rename files and folders", self.open_rename),
                ("Organize Files", "Automatically organize files by type/date", self.open_organize),
            ])
            tab_widget.addTab(file_mgmt_tab, "File Management")
            
            # File Operations Tools
            file_ops_tab = self.create_tool_category_tab([
                ("Copy/Move/Sync/Delete", "Advanced file operations", self.open_cmsd),
                ("Compress/Decompress", "Archive and extract files", self.open_compress),
                ("Split/Join Files", "Split large files or join parts", self.open_file_splitter),
                ("Synchronize", "Synchronize directories", self.open_sync),
            ])
            tab_widget.addTab(file_ops_tab, "File Operations")
            
            # Analysis Tools
            analysis_tab = self.create_tool_category_tab([
                ("Size Analyzer", "Analyze disk space usage", self.open_size_analyzer),
                ("Duplicate Finder", "Find and remove duplicate files", self.open_duplicate_finder),
                ("File Checksum", "Calculate and verify checksums", self.open_checksum),
                ("Empty Folders", "Find and clean empty folders", self.open_empty_folders),
            ])
            tab_widget.addTab(analysis_tab, "Analysis")
            
            # Security Tools
            security_tab = self.create_tool_category_tab([
                ("Encrypt/Decrypt", "Secure file encryption and decryption", self.open_encrypt_decrypt),
                ("Secure Delete", "Permanently delete sensitive files", self.open_secure_delete),
                ("Permissions Editor", "Manage file and folder permissions", self.open_permissions),
            ])
            tab_widget.addTab(security_tab, "Security")
            
            # Metadata Tools
            metadata_tab = self.create_tool_category_tab([
                ("Edit Image Metadata", "View and edit image metadata", self.open_image_metadata),
                ("Office Metadata Editor", "Edit document metadata", self.open_office_metadata),
                ("File Touch", "Modify file timestamps", self.open_file_touch),
            ])
            tab_widget.addTab(metadata_tab, "Metadata")
            
            # Enhanced PDF Tools with Comprehensive Tabbed Interface
            if ENHANCED_PDF_TOOLS_AVAILABLE:
                pdf_tab = self.create_enhanced_pdf_tools_tab()
            else:
                # Fallback to simple PDF tools if enhanced version not available
                pdf_tab = self.create_tool_category_tab([
                    ("PDF Utilities", "Comprehensive PDF tools", self.open_pdf_tools),
                    ("Extract Links", "Extract links from PDF files", self.open_pdf_links),
                    ("Page Administration", "Manage PDF pages", self.open_pdf_pages),
                ])
            
            # Network Tools
            network_tab = self.create_tool_category_tab([
                ("Network Connectivity", "Check network connectivity and diagnostics", self.open_network_connectivity),
                ("Network Scanner", "Scan network for devices and services", self.open_network_scanner),
            ])
            tab_widget.addTab(network_tab, "Network Tools")
            
            # Privacy Tools
            privacy_tab = self.create_tool_category_tab([
                ("Privacy Cleaner", "Clean privacy-sensitive data", self.open_privacy_cleaner),
                ("Data Anonymizer", "Anonymize sensitive file data", self.open_data_anonymizer),
            ])
            tab_widget.addTab(privacy_tab, "Privacy Tools")
            
            # System Tools  
            system_tab = self.create_tool_category_tab([
                ("System Diagnostics", "Run system diagnostics and monitoring", self.open_system_diagnostics),
                ("System Cleanup", "Clean system temporary files", self.open_system_cleanup),
                ("Software Maintenance", "Maintain and update software", self.open_software_maintenance),
            ])
            tab_widget.addTab(system_tab, "System Tools")
            
            tab_widget.addTab(pdf_tab, "PDF Tools")
            
            # Add status bar
            self.statusBar().showMessage("Ready - Select a tool to begin")
        
        def create_tool_category_tab(self, tools):
            """Create a tab with tools for a specific category."""
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(5)
            
            # Create scroll area for tools
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameStyle(QFrame.NoFrame)
            scroll_widget = QWidget()
            scroll_layout = QGridLayout(scroll_widget)
            scroll_layout.setSpacing(10)
            scroll_layout.setContentsMargins(5, 5, 5, 5)
            
            # Add tools in a grid layout
            row, col = 0, 0
            for tool_name, description, callback in tools:
                tool_frame = self.create_tool_button(tool_name, description, callback)
                scroll_layout.addWidget(tool_frame, row, col)
                
                col += 1
                if col >= 2:  # 2 columns
                    col = 0
                    row += 1
            
            # Add stretch to push tools to the top
            scroll_layout.setRowStretch(row + 1, 1)
            
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)
            
            return tab_widget
        
        def create_tool_button(self, name, description, callback):
            """Create a styled button for a tool."""
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    margin: 5px;
                }
                QFrame:hover {
                    background-color: #e9ecef;
                    border-color: #3498db;
                }
            """)
            
            layout = QVBoxLayout(frame)
            
            # Tool name button
            button = QPushButton(name)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    color: #2c3e50;
                    border: none;
                    padding: 10px;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #3498db;
                }
                QPushButton:pressed {
                    color: #2980b9;
                }
            """)
            button.clicked.connect(callback)
            layout.addWidget(button)
            
            # Description
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("""
                font-size: 11px;
                color: #6c757d;
                padding: 0 10px 10px 10px;
            """)
            layout.addWidget(desc_label)
            
            frame.setMaximumHeight(120)
            frame.setMinimumHeight(100)
            
            return frame
        
        def create_enhanced_pdf_tools_tab(self):
            """Create enhanced PDF tools tab with comprehensive tabbed sub-interface"""
            try:
                # Create the enhanced PDF tools widget
                enhanced_pdf_widget = EnhancedPDFToolsWidget(self)
                
                # Connect signals for integration with main hub
                enhanced_pdf_widget.tool_operation_started.connect(self.on_pdf_operation_started)
                enhanced_pdf_widget.tool_operation_completed.connect(self.on_pdf_operation_completed)
                enhanced_pdf_widget.file_selected.connect(self.on_pdf_file_selected)
                
                # Store reference for later use
                self.enhanced_pdf_widget = enhanced_pdf_widget
                
                return enhanced_pdf_widget
                
            except Exception as e:
                print(f"Error creating enhanced PDF tools tab: {e}")
                # Fallback to simple tab
                return self.create_tool_category_tab([
                    ("PDF Utilities", "Comprehensive PDF tools", self.open_pdf_tools),
                    ("Extract Links", "Extract links from PDF files", self.open_pdf_links),
                    ("Page Administration", "Manage PDF pages", self.open_pdf_pages),
                ])
        
        def on_pdf_operation_started(self, tool_name: str, operation: str):
            """Handle PDF operation started signal"""
            self.statusBar().showMessage(f"PDF Operation: {tool_name} - {operation} started...")
            
        def on_pdf_operation_completed(self, tool_name: str, operation: str, success: bool):
            """Handle PDF operation completed signal"""
            if success:
                self.statusBar().showMessage(f"PDF Operation: {tool_name} - {operation} completed successfully")
            else:
                self.statusBar().showMessage(f"PDF Operation: {tool_name} - {operation} failed")
                
        def on_pdf_file_selected(self, file_path: str):
            """Handle PDF file selected signal"""
            self.statusBar().showMessage(f"PDF File selected: {os.path.basename(file_path)}")
            
        
        # Tool launcher methods
        def open_file_finder(self):
            """Open File Finder tool."""
            self.launch_tool("File Finder", "src.rfu.tools.file_management.file_finder", "FileFinderGUI")
        
        def open_catalog(self):
            """Open Catalog tool."""
            self.launch_tool("Catalog", "src.rfu.tools.file_management.catalog", "CatalogWindow")
        
        def open_rename(self):
            """Open Rename tool."""
            self.launch_tool("Rename", "src.rfu.tools.file_management.rename", "RenameWindow")
            
        def open_organize(self):
            """Open Organize tool."""
            self.launch_tool("Organize", "src.rfu.tools.file_management.organize", "OrganizeWindow")
            
        def open_cmsd(self):
            """Open Copy/Move/Sync/Delete tool."""
            self.launch_tool("CMSD", "src.rfu.tools.file_operations.cmsd", "CopyMoveSyncDeleteWindow")
            
        def open_compress(self):
            """Open Compress/Decompress tool."""
            self.launch_tool("Compress", "src.rfu.tools.file_operations.compress_decompress", "CompressDecompressApp")
            
        def open_file_splitter(self):
            """Open File Splitter tool."""
            self.launch_tool("File Splitter", "src.rfu.tools.file_operations.file_splitter_joiner", "FileSplitJoinGUI")
            
        def open_sync(self):
            """Open Sync tool."""
            self.launch_tool("Sync", "src.rfu.tools.file_operations.sync", "SyncWindow")
            
        def open_size_analyzer(self):
            """Open Size Analyzer tool."""
            self.launch_tool("Size Analyzer", "src.utilities.analysis.size_analyzer", "SizeAnalyzerGUI")
            
        def open_duplicate_finder(self):
            """Open Duplicate Finder tool."""
            self.launch_tool("Duplicate Finder", "src.utilities.analysis.find_duplicate_files", "DuplicateFinderApp")
            
        def open_checksum(self):
            """Open Checksum tool."""
            self.launch_tool("Checksum", "src.utilities.analysis.check_sum", "ChecksumGUI")
            
        def open_empty_folders(self):
            """Open Empty Folders tool."""
            self.launch_tool("Empty Folders", "src.rfu.tools.analysis.empty_folders", "EmptyFoldersGUI")
            
        def open_encrypt_decrypt(self):
            """Open Encrypt/Decrypt tool."""
            self.launch_tool("Encrypt/Decrypt", "src.utilities.security.en_and_decrypt", "EnAndDecryptGUI")
            
        def open_secure_delete(self):
            """Open Secure Delete tool."""
            self.launch_tool("Secure Delete", "src.utilities.security.secure_delete", "SecureDeleteGUI")
            
        def open_permissions(self):
            """Open Permissions Editor tool."""
            self.launch_tool("Permissions", "src.utilities.system.permissions_editor", "PermissionsEditorGUI")
            
        def open_image_metadata(self):
            """Open Image Metadata Editor tool."""
            self.launch_tool("Image Metadata", "src.rfu.tools.metadata.edit_image_metadata", "ImageMetadataEditorGUI")
            
        def open_office_metadata(self):
            """Open Office Metadata Editor tool."""
            self.launch_tool("Office Metadata", "src.rfu.tools.metadata.office_meta_data_editor", "OfficeMetaDataEditorGUI")
            
        def open_file_touch(self):
            """Open File Touch tool."""
            self.launch_tool("File Touch", "src.rfu.tools.metadata.file_touch", "FileTouchGUI")
            
        def open_pdf_tools(self):
            """Open PDF Tools."""
            self.launch_tool("PDF Tools", "pdf_utilities.main", "PDFUtilitiesGUI")
            
        def open_pdf_links(self):
            """Open PDF Links Extractor."""
            self.launch_tool("PDF Links", "pdf_utilities.extract_links", "ExtractLinksGUI")
            
        def open_pdf_pages(self):
            """Open PDF Page Administration."""
            self.launch_tool("PDF Pages", "pdf_utilities.page_administration", "PageAdminGUI")
        
        # Network Tools
        def open_network_connectivity(self):
            """Open Network Connectivity tool."""
            self.launch_tool("Network Connectivity", "src.utilities.network.network_connectivity", "NetworkConnectivityGUI")
        
        def open_network_scanner(self):
            """Open Network Scanner tool."""
            self.launch_tool("Network Scanner", "src.utilities.network.network_scanner", "NetworkScannerGUI")
        
        # Privacy Tools
        def open_privacy_cleaner(self):
            """Open Privacy Cleaner tool."""
            self.launch_tool("Privacy Cleaner", "src.utilities.privacy.privacy_tools", "PrivacyCleanerGUI")
        
        def open_data_anonymizer(self):
            """Open Data Anonymizer tool."""
            self.launch_tool("Data Anonymizer", "src.utilities.privacy.data_anonymizer", "DataAnonymizerGUI")
        
        # System Tools
        def open_system_diagnostics(self):
            """Open System Diagnostics tool."""
            self.launch_tool("System Diagnostics", "src.utilities.system.diagnostics_monitoring", "SystemDiagnosticsGUI")
        
        def open_system_cleanup(self):
            """Open System Cleanup tool."""
            self.launch_tool("System Cleanup", "src.utilities.system.system_cleanup", "SystemCleanupGUI")
        
        def open_software_maintenance(self):
            """Open Software Maintenance tool."""
            self.launch_tool("Software Maintenance", "src.utilities.system.software_maintenance", "SoftwareMaintenanceGUI")
        

        def _import_direct(self, module_name, class_name):
            """Strategy 1: Direct module import."""
            try:
                module = __import__(module_name, fromlist=[class_name])
                return getattr(module, class_name)
            except (ImportError, AttributeError):
                return None

        def _import_absolute(self, module_name, class_name):
            """Strategy 2: Absolute path import with explicit path resolution."""
            try:
                # Convert module path to absolute import
                if module_name.startswith('src.'):
                    # Remove 'src.' prefix since we already added src to path
                    clean_module = module_name[4:]
                else:
                    clean_module = module_name
                    
                module = __import__(clean_module, fromlist=[class_name])
                return getattr(module, class_name)
            except (ImportError, AttributeError):
                return None

        def _import_dynamic(self, module_name, class_name):
            """Strategy 3: Dynamic import using importlib."""
            try:
                import importlib
                
                # Try different module path variations
                module_variations = [
                    module_name,
                    module_name.replace('src.', ''),
                    f"src.{module_name}" if not module_name.startswith('src.') else module_name
                ]
                
                for module_path in module_variations:
                    try:
                        module = importlib.import_module(module_path)
                        if hasattr(module, class_name):
                            return getattr(module, class_name)
                    except ImportError:
                        continue
                return None
            except Exception:
                return None

        def _import_legacy(self, module_name, class_name):
            """Strategy 4: Legacy compatibility import."""
            try:
                # Try legacy paths
                legacy_paths = [
                    f"src.legacy.file_utilities_1.{module_name}",
                    f"legacy.file_utilities_1.{module_name}",
                    module_name.split('.')[-1]  # Just the final module name
                ]
                
                for legacy_path in legacy_paths:
                    try:
                        module = __import__(legacy_path, fromlist=[class_name])
                        if hasattr(module, class_name):
                            return getattr(module, class_name)
                    except (ImportError, AttributeError):
                        continue
                return None
            except Exception:
                return None

        def _validate_tool_class(self, tool_class, tool_name):
            """Validate that a tool class can be instantiated."""
            try:
                # Quick instantiation test without showing
                test_instance = tool_class()
                if hasattr(test_instance, 'hide'):
                    test_instance.hide()
                if hasattr(test_instance, 'close'):
                    test_instance.close()
                return True
            except Exception as e:
                print(f"Tool validation failed for {tool_name}: {e}")
                return False

        def _launch_validated_tool(self, tool_name, tool_class):
            """Launch a validated tool class."""
            try:
                # Validate before launching
                if not self._validate_tool_class(tool_class, tool_name):
                    self._handle_validation_failure(tool_name)
                    return
                    
                # Create and show the tool
                window = tool_class()
                self.opened_windows[tool_name] = window
                window.show()
                self.statusBar().showMessage(f"{tool_name} opened successfully")
                
            except Exception as e:
                self._handle_instantiation_error(tool_name, e)

        def _handle_import_failure(self, tool_name, module_name, class_name, last_error):
            """Handle import failure with detailed diagnostics."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Import Error - {tool_name}")
            msg.setIcon(QMessageBox.Critical)
            
            error_text = f"Failed to import {tool_name}:\n\n"
            error_text += f"Module: {module_name}\n"
            error_text += f"Class: {class_name}\n"
            error_text += f"Last Error: {str(last_error)}\n\n"
            
            # Add diagnostic information
            error_text += "🔍 Diagnostic Information:\n"
            
            # Check if module file exists
            module_path = module_name.replace('.', os.sep) + '.py'
            if os.path.exists(module_path):
                error_text += f"✓ Module file exists: {module_path}\n"
            else:
                error_text += f"✗ Module file not found: {module_path}\n"
            
            # Check Python path
            error_text += f"✓ Python path includes: {sys.path[:3]}...\n"
            
            # Add solution suggestions
            error_text += "\n🔧 Suggested Solutions:\n"
            error_text += "• Check if all required dependencies are installed\n"
            error_text += "• Verify the module file exists and is accessible\n"
            error_text += "• Run the automated tool corrector\n"
            error_text += "• Check the import validation utility\n"
            
            msg.setText(error_text)
            msg.exec_()
            self.statusBar().showMessage(f"Import failed for {tool_name}")

        def _handle_validation_failure(self, tool_name):
            """Handle tool validation failure."""
            from PyQt5.QtWidgets import QMessageBox
            
            QMessageBox.warning(
                self,
                f"Validation Error - {tool_name}",
                f"The {tool_name} tool failed validation checks.\n\n"
                f"This usually indicates missing dependencies or "
                f"configuration issues.\n\n"
                f"Please run the diagnostic tools to identify the problem."
            )

        def _handle_instantiation_error(self, tool_name, error):
            """Handle tool instantiation error."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Instantiation Error - {tool_name}")
            msg.setIcon(QMessageBox.Critical)
            
            error_text = f"Failed to create {tool_name} window:\n\n{str(error)}\n\n"
            
            # Provide specific guidance based on error type
            if "not defined" in str(error) or "NameError" in str(error):
                error_text += "🔧 This appears to be a missing import issue.\n"
                error_text += "The tool is missing required widget imports.\n\n"
                error_text += "Solutions:\n"
                error_text += "• Check PyQt5 installation\n"
                error_text += "• Verify all imports in the tool file\n"
                error_text += "• Run the automated tool corrector\n"
            elif "QApplication" in str(error):
                error_text += "🔧 QApplication initialization issue.\n"
                error_text += "The tool may have application lifecycle problems.\n"
            else:
                error_text += "🔧 General instantiation error.\n"
                error_text += "Check the tool's __init__ method for issues.\n"
            
            msg.setText(error_text)
            msg.exec_()
            self.statusBar().showMessage(f"{tool_name} instantiation failed")

        def _handle_unexpected_error(self, tool_name, error):
            """Handle unexpected errors during tool launch."""
            from PyQt5.QtWidgets import QMessageBox
            
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred while launching {tool_name}:\n\n"
                f"{str(error)}\n\n"
                f"Please report this issue with the error details."
            )
            self.statusBar().showMessage(f"Unexpected error opening {tool_name}")

        def launch_tool(self, tool_name, module_name, class_name):
            """Enhanced tool launcher with comprehensive error handling and multiple import strategies."""
            try:
                # Check if tool is already open
                if tool_name in self.opened_windows:
                    window = self.opened_windows[tool_name]
                    if window and hasattr(window, 'show'):
                        window.show()
                        window.raise_()
                        window.activateWindow()
                        self.statusBar().showMessage(f"{tool_name} window activated")
                        return
                
                # Multiple import strategies with fallbacks
                import_strategies = [
                    # Strategy 1: Direct module import
                    lambda: self._import_direct(module_name, class_name),
                    # Strategy 2: Absolute path import
                    lambda: self._import_absolute(module_name, class_name),
                    # Strategy 3: Dynamic import with importlib
                    lambda: self._import_dynamic(module_name, class_name),
                    # Strategy 4: Legacy compatibility import
                    lambda: self._import_legacy(module_name, class_name)
                ]
                
                tool_class = None
                last_error = None
                
                self.statusBar().showMessage(f"Loading {tool_name}...")
                
                for i, strategy in enumerate(import_strategies, 1):
                    try:
                        tool_class = strategy()
                        if tool_class:
                            self.statusBar().showMessage(f"Loaded {tool_name} using strategy {i}")
                            break
                    except Exception as e:
                        last_error = e
                        continue
                
                if tool_class is None:
                    self._handle_import_failure(tool_name, module_name, class_name, last_error)
                    return
                    
                # Launch the validated tool
                self._launch_validated_tool(tool_name, tool_class)
                
            except Exception as e:
                self._handle_unexpected_error(tool_name, e)
                
        def validate_tool_before_launch(self, module_name, class_name):
            """Validate tool dependencies before launch."""
            validation_result = {
                "success": True,
                "errors": [],
                "warnings": []
            }
            
            try:
                # Test import
                try:
                    module = __import__(module_name)
                except ImportError as e:
                    validation_result["success"] = False
                    validation_result["errors"].append(f"Import failed: {str(e)}")
                    return validation_result
                
                # Test class existence
                if not hasattr(module, class_name):
                    validation_result["success"] = False
                    validation_result["errors"].append(f"Class '{class_name}' not found in module")
                    return validation_result
                
                # Test basic instantiation (without showing)
                try:
                    tool_class = getattr(module, class_name)
                    # Quick instantiation test
                    test_instance = tool_class()
                    if hasattr(test_instance, 'hide'):
                        test_instance.hide()
                    if hasattr(test_instance, 'close'):
                        test_instance.close()
                except Exception as e:
                    validation_result["success"] = False
                    validation_result["errors"].append(f"Instantiation failed: {str(e)}")
                    return validation_result
                    
            except Exception as e:
                validation_result["success"] = False
                validation_result["errors"].append(f"Validation error: {str(e)}")
            
            return validation_result
            
        def show_enhanced_error_dialog(self, tool_name, module_name, validation_result):
            """Show enhanced error dialog with specific guidance."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Tool Launch Error - {tool_name}")
            msg.setIcon(QMessageBox.Warning)
            
            error_text = f"Could not launch {tool_name}:\n\n"
            for error in validation_result["errors"]:
                error_text += f"• {error}\n"
            
            # Add specific guidance based on error type
            if "Import failed" in str(validation_result["errors"]):
                error_text += "\n🔧 Suggested Solutions:\n"
                error_text += f"• Check if {module_name}.py exists in the current directory\n"
                error_text += "• Verify all required dependencies are installed\n"
                error_text += "• Run the automated tool corrector to fix missing tools\n"
            elif "not found" in str(validation_result["errors"]):
                error_text += "\n🔧 Suggested Solutions:\n"
                error_text += f"• Check class name in {module_name}.py\n"
                error_text += "• Run the comprehensive test suite for validation\n"
            elif "Instantiation failed" in str(validation_result["errors"]):
                error_text += "\n🔧 Suggested Solutions:\n"
                error_text += "• Check for missing PyQt5 widget imports\n"
                error_text += "• Verify all dependencies are properly imported\n"
                error_text += "• Check the tool's __init__ method for errors\n"
            
            msg.setText(error_text)
            msg.setInformativeText(f"Module: {module_name}\nTool Status: Needs attention")
            msg.exec_()
            self.statusBar().showMessage(f"Failed to open {tool_name} - See error details")
            
        def show_enhanced_placeholder_window(self, tool_name, module_name, import_error):
            """Show enhanced placeholder with specific error information."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"{tool_name} - Tool Not Available")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"The {tool_name} tool is currently not available.")
            
            info_text = f"Module: {module_name}\n"
            if import_error:
                info_text += f"Error: {str(import_error)}\n"
            info_text += "\n🔧 Quick Fix Options:\n"
            info_text += "• Run: python automated_tool_corrector.py --mode=single --tool=" + module_name + "\n"
            info_text += "• Run: python comprehensive_test_suite.py\n"
            info_text += "• Check the tool integration documentation\n"
            
            msg.setInformativeText(info_text)
            msg.exec_()
            self.statusBar().showMessage(f"{tool_name} not available - Use automated corrector")
            
        def show_instantiation_error_dialog(self, tool_name, error):
            """Show specific error dialog for instantiation failures."""
            from PyQt5.QtWidgets import QMessageBox
            
            msg = QMessageBox(self)
            msg.setWindowTitle(f"Tool Instantiation Error - {tool_name}")
            msg.setIcon(QMessageBox.Critical)
            
            error_text = f"Failed to create {tool_name} window:\n\n{str(error)}\n\n"
            
            # Provide specific guidance based on error type
            if "not defined" in str(error):
                error_text += "🔧 This appears to be a missing import issue.\n"
                error_text += "The tool is missing required PyQt5 widget imports.\n\n"
                error_text += "Quick Fix:\n"
                error_text += "• Run the automated tool corrector to fix imports\n"
                error_text += "• Check the tool's import statements\n"
            elif "QApplication" in str(error):
                error_text += "🔧 This is a QApplication initialization issue.\n"
                error_text += "The tool may be trying to create widgets before QApplication is ready.\n"
            else:
                error_text += "🔧 General instantiation error.\n"
                error_text += "Check the tool's __init__ method for issues.\n"
            
            msg.setText(error_text)
            msg.exec_()
            self.statusBar().showMessage(f"{tool_name} instantiation failed")
            
        def show_generic_error_dialog(self, tool_name, error):
            """Show generic error dialog for unexpected errors."""
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"An unexpected error occurred while launching {tool_name}:\n\n{str(error)}\n\n"
                f"Please report this issue with the error details."
            )
            self.statusBar().showMessage(f"Unexpected error opening {tool_name}")
        
        def show_placeholder_window(self, tool_name, module_name):
            """Show a placeholder window for tools that aren't implemented yet."""
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle(f"{tool_name} - Not Available")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"The {tool_name} tool is currently being integrated.")
            msg.setInformativeText(
                f"Module: {module_name}\n\n"
                f"This tool will be available in a future update. "
                f"The integration is in progress."
            )
            msg.exec_()
    
    def main():
        """Main entry point for the application."""
        print("Starting Richard's File Utilities...")
        
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Richard's File Utilities")
        app.setApplicationVersion("3.0.0")
        app.setOrganizationName("Richard's File Utilities")
        
        # Create and show main window
        window = RFUMainWindow()
        window.show()
        
        print("Application window displayed. Use the tabs to access different tools.")
        return app.exec_()
        
    if __name__ == '__main__':
        sys.exit(main())
        
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure PyQt5 is properly installed.")
    print("To install PyQt5, run: pip install PyQt5")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
    
    def main():
        """Main entry point for the application."""
        print("Starting Richard's File Utilities...")
        
        app = QApplication(sys.argv)
        window = RFUMainWindow()
        window.show()
        
        print("Application window displayed. Close the window to exit.")
        return app.exec_()
        
    if __name__ == '__main__':
        sys.exit(main())
        
except ImportError as e:
    print(f"Error importing main application: {e}")
    print("Please ensure PyQt5 is properly installed.")
    print("To install PyQt5, run: pip install PyQt5")
    sys.exit(1)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)