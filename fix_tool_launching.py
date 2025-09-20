#!/usr/bin/env python3
"""
Fix Tool Launching Issues - Comprehensive Solution
This script implements fixes for the multi-pane file explorer tool launching problems.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging for the fix process
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ToolLaunchingFix')

def patch_multi_pane_explorer():
    """Apply comprehensive fixes to the multi-pane explorer tool launching system."""
    
    # Path to the multi-pane explorer file
    explorer_file = Path(__file__).parent / "src" / "file_explorer" / "multi_pane_explorer.py"
    
    if not explorer_file.exists():
        logger.error(f"Multi-pane explorer file not found: {explorer_file}")
        return False
    
    logger.info("Starting comprehensive tool launching fixes...")
    
    # Read the current file
    with open(explorer_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply fixes
    fixed_content = apply_all_fixes(content)
    
    # Create backup
    backup_file = explorer_file.with_suffix('.py.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f"Created backup: {backup_file}")
    
    # Write fixed content
    with open(explorer_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    logger.info("Tool launching fixes applied successfully!")
    return True

def apply_all_fixes(content: str) -> str:
    """Apply all necessary fixes to the multi-pane explorer content."""
    
    # Fix 1: Enhanced tool discovery with better error handling
    content = fix_tool_discovery(content)
    
    # Fix 2: Improved event handling for tool activation
    content = fix_event_handling(content)
    
    # Fix 3: Enhanced import path resolution
    content = fix_import_paths(content)
    
    # Fix 4: Better error reporting for users
    content = fix_error_reporting(content)
    
    # Fix 5: Fallback tool system improvements
    content = fix_fallback_tools(content)
    
    return content

def fix_tool_discovery(content: str) -> str:
    """Fix the tool discovery mechanism with enhanced error handling."""
    
    # Replace the _discover_tools_from_directory method
    old_method = '''    def _discover_tools_from_directory(self):
        """Discover tools from the src/tools directory structure."""
        tools_dir = Path(__file__).parent.parent / "tools"
        discovered_tools = {}
        
        try:
            if not tools_dir.exists():
                self.logger.warning(f"Tools directory not found: {tools_dir}")
                return {}'''
    
    new_method = '''    def _discover_tools_from_directory(self):
        """Discover tools from the src/tools directory structure with enhanced error handling."""
        # Try multiple possible tool directory locations
        possible_dirs = [
            Path(__file__).parent.parent / "tools",
            Path(__file__).parent.parent / "utilities", 
            Path(__file__).parent.parent.parent / "src" / "tools",
            Path(__file__).parent.parent.parent / "src" / "utilities",
            Path(__file__).parent.parent.parent / "utilities",
        ]
        
        tools_dir = None
        for dir_path in possible_dirs:
            if dir_path.exists():
                tools_dir = dir_path
                self.logger.info(f"Found tools directory: {tools_dir}")
                break
        
        discovered_tools = {}
        
        try:
            if not tools_dir:
                self.logger.warning("No tools directory found, using fallback tools")
                return self._get_hardcoded_fallback_tools()'''
    
    content = content.replace(old_method, new_method)
    
    # Add the hardcoded fallback tools method
    fallback_method = '''
    def _get_hardcoded_fallback_tools(self):
        """Get hardcoded fallback tools when discovery fails."""
        return {
            "File Management": [
                {
                    'name': 'file_finder',
                    'display_name': 'File Finder', 
                    'module_path': 'src.utilities.file_management.file_finder',
                    'class_name': 'FileFinderGUI',
                    'icon': '🔍'
                },
                {
                    'name': 'catalog',
                    'display_name': 'File Catalog',
                    'module_path': 'src.utilities.file_management.catalog_window',
                    'class_name': 'CatalogWindow', 
                    'icon': '📋'
                }
            ],
            "Analysis": [
                {
                    'name': 'size_analyzer',
                    'display_name': 'Size Analyzer',
                    'module_path': 'src.utilities.analysis.size_analyzer',
                    'class_name': 'SizeAnalyzerGUI',
                    'icon': '📊'
                },
                {
                    'name': 'duplicate_finder',
                    'display_name': 'Duplicate Finder',
                    'module_path': 'src.utilities.analysis.duplicate_finder_app',
                    'class_name': 'DuplicateFinderApp',
                    'icon': '🔍'
                }
            ],
            "Security": [
                {
                    'name': 'encrypt_decrypt',
                    'display_name': 'Encrypt/Decrypt',
                    'module_path': 'src.utilities.security.en_and_decrypt',
                    'class_name': 'EnAndDecryptGUI',
                    'icon': '🔒'
                },
                {
                    'name': 'secure_delete',
                    'display_name': 'Secure Delete',
                    'module_path': 'src.utilities.security.secure_delete',
                    'class_name': 'SecureDeleteGUI',
                    'icon': '🗑️'
                }
            ]
        }
'''
    
    # Insert the method after the class definition
    class_def_pos = content.find("class MultiPaneFileExplorer(QMainWindow):")
    if class_def_pos != -1:
        # Find the end of the class
        next_class_pos = content.find("\nclass ", class_def_pos + 1)
        if next_class_pos == -1:
            next_class_pos = len(content)
        
        # Insert before the last method
        last_method_pos = content.rfind("\n    def ", class_def_pos, next_class_pos)
        if last_method_pos != -1:
            content = content[:last_method_pos] + fallback_method + content[last_method_pos:]
    
    return content

def fix_event_handling(content: str) -> str:
    """Fix event handling for tool activation."""
    
    # Fix the _on_discovered_tool_activated method
    old_handler = '''    def _on_discovered_tool_activated(self, item, column):
        """Handle activation of discovered tools."""
        try:
            if item.parent():  # Only handle leaf items (actual tools)
                tool_data = item.data(0, Qt.UserRole)
                if isinstance(tool_data, dict):
                    self._launch_discovered_tool(tool_data)
        except Exception as e:
            self.logger.error(f"Error activating discovered tool: {e}")'''
    
    new_handler = '''    def _on_discovered_tool_activated(self, item, column):
        """Handle activation of discovered tools with enhanced error handling."""
        try:
            if not item:
                self.logger.warning("No item selected for tool activation")
                return
                
            if item.parent():  # Only handle leaf items (actual tools)
                tool_data = item.data(0, Qt.UserRole)
                self.logger.info(f"Tool activation requested: {tool_data}")
                
                if isinstance(tool_data, dict):
                    self._launch_discovered_tool(tool_data)
                else:
                    # Try alternative data extraction
                    tool_name = item.text(0)
                    if tool_name:
                        self.logger.info(f"Attempting to launch tool by name: {tool_name}")
                        self._launch_tool_by_name(tool_name)
                    else:
                        self.logger.warning("No tool data or name found for activation")
            else:
                # Handle category expansion/collapse
                if item.isExpanded():
                    item.setExpanded(False)
                else:
                    item.setExpanded(True)
                    
        except Exception as e:
            self.logger.error(f"Error activating discovered tool: {e}")
            self._show_user_error("Tool Launch Error", 
                                f"Failed to activate tool: {e}")'''
    
    content = content.replace(old_handler, new_handler)
    
    return content

def fix_import_paths(content: str) -> str:
    """Fix import path resolution for tools."""
    
    # Enhanced _launch_discovered_tool method
    old_launch_method = '''    def _launch_discovered_tool(self, tool_data):
        """Launch a discovered tool using its metadata."""
        try:
            tool_name = tool_data['display_name']
            module_path = tool_data['module_path']
            class_name = tool_data['class_name']
            
            self.logger.info(f"Launching tool: {tool_name} ({module_path}.{class_name})")
            
            # Import and launch the tool
            try:
                module = __import__(module_path, fromlist=[class_name])
                tool_class = getattr(module, class_name)
                tool_instance = tool_class()
                
                # Show the tool window
                if hasattr(tool_instance, 'show'):
                    tool_instance.show()
                elif hasattr(tool_instance, 'exec_'):
                    tool_instance.exec_()
                
                self.statusBar().showMessage(f"{tool_name} launched successfully", 3000)
                self.logger.info(f"Successfully launched tool: {tool_name}")
                
            except ImportError as e:
                self.logger.error(f"Failed to import {module_path}: {e}")
                QMessageBox.warning(
                    self,
                    "Tool Launch Error",
                    f"Could not import {tool_name}:\\n\\n{e}\\n\\n"
                    f"Module: {module_path}\\nClass: {class_name}"
                )
            except AttributeError as e:
                self.logger.error(f"Class {class_name} not found in {module_path}: {e}")
                QMessageBox.warning(
                    self,
                    "Tool Launch Error", 
                    f"Class '{class_name}' not found in {tool_name}:\\n\\n{e}"
                )
            except Exception as e:
                self.logger.error(f"Error launching {tool_name}: {e}")
                QMessageBox.warning(
                    self,
                    "Tool Launch Error",
                    f"Could not launch {tool_name}:\\n\\n{e}"
                )
                
        except Exception as e:
            self.logger.error(f"Error in _launch_discovered_tool: {e}")'''
    
    new_launch_method = '''    def _launch_discovered_tool(self, tool_data):
        """Launch a discovered tool using its metadata with enhanced path resolution."""
        try:
            tool_name = tool_data['display_name']
            module_path = tool_data['module_path']
            class_name = tool_data['class_name']
            
            self.logger.info(f"Launching tool: {tool_name} ({module_path}.{class_name})")
            
            # Try multiple import strategies
            import_strategies = [
                # Strategy 1: Direct import
                lambda: __import__(module_path, fromlist=[class_name]),
                # Strategy 2: Try without 'src' prefix
                lambda: __import__(module_path.replace('src.', ''), fromlist=[class_name]),
                # Strategy 3: Try with different path variations
                lambda: self._try_alternative_imports(module_path, class_name),
                # Strategy 4: Try legacy paths
                lambda: self._try_legacy_imports(tool_name, class_name)
            ]
            
            tool_instance = None
            last_error = None
            
            for strategy in import_strategies:
                try:
                    self.logger.debug(f"Trying import strategy for {tool_name}")
                    module = strategy()
                    if module:
                        tool_class = getattr(module, class_name)
                        tool_instance = tool_class()
                        break
                except Exception as e:
                    last_error = e
                    self.logger.debug(f"Import strategy failed: {e}")
                    continue
            
            if tool_instance:
                # Show the tool window
                if hasattr(tool_instance, 'show'):
                    tool_instance.show()
                elif hasattr(tool_instance, 'exec_'):
                    tool_instance.exec_()
                else:
                    self.logger.warning(f"Tool {tool_name} has no show() or exec_() method")
                
                self.statusBar().showMessage(f"{tool_name} launched successfully", 3000)
                self.logger.info(f"Successfully launched tool: {tool_name}")
                
                # Track successful launch
                if hasattr(self, 'db_manager') and self.db_manager:
                    try:
                        self._track_tool_usage(tool_name)
                    except Exception:
                        pass  # Don't fail on tracking errors
                        
            else:
                self.logger.error(f"All import strategies failed for {tool_name}: {last_error}")
                self._show_user_error("Tool Launch Error",
                    f"Could not launch {tool_name}.\\n\\n"
                    f"Please ensure the tool is properly installed.\\n\\n"
                    f"Details: {last_error}")
                
        except Exception as e:
            self.logger.error(f"Error in _launch_discovered_tool: {e}")
            self._show_user_error("Tool Launch Error", 
                f"Unexpected error launching tool: {e}")'''
    
    content = content.replace(old_launch_method, new_launch_method)
    
    # Add helper methods for import strategies
    helper_methods = '''
    def _try_alternative_imports(self, module_path, class_name):
        """Try alternative import paths for tools."""
        alternatives = [
            module_path.replace('src.utilities.', 'utilities.'),
            module_path.replace('src.tools.', 'tools.'),
            module_path.replace('src.', ''),
            module_path.replace('.', '/') + '.py'
        ]
        
        for alt_path in alternatives:
            try:
                if alt_path.endswith('.py'):
                    # Direct file import approach
                    continue  # Skip for now, complex to implement
                module = __import__(alt_path, fromlist=[class_name])
                return module
            except ImportError:
                continue
        return None
    
    def _try_legacy_imports(self, tool_name, class_name):
        """Try legacy import paths based on tool name."""
        legacy_mappings = {
            'File Finder': 'src.utilities.file_management.file_finder',
            'Size Analyzer': 'src.utilities.analysis.size_analyzer', 
            'Duplicate Finder': 'src.utilities.analysis.duplicate_finder_app',
            'Encrypt/Decrypt': 'src.utilities.security.en_and_decrypt',
            'Secure Delete': 'src.utilities.security.secure_delete',
            'File Catalog': 'src.utilities.file_management.catalog_window'
        }
        
        if tool_name in legacy_mappings:
            try:
                module_path = legacy_mappings[tool_name]
                return __import__(module_path, fromlist=[class_name])
            except ImportError:
                pass
        return None
    
    def _launch_tool_by_name(self, tool_name):
        """Launch tool by name using fallback mapping."""
        # Remove emoji and clean up tool name
        clean_name = tool_name
        if ' ' in clean_name:
            clean_name = clean_name.split(' ', 1)[1] if clean_name[0] in '🔍📋📊🔒🗑️' else clean_name
        
        # Direct method mapping
        method_mappings = {
            'File Finder': self.launch_file_finder,
            'Size Analyzer': self.launch_size_analyzer,
            'Duplicate Finder': self.launch_duplicate_finder,
            'Encrypt/Decrypt': self.launch_encrypt_decrypt,
            'Secure Delete': self.launch_secure_delete,
            'File Catalog': self.launch_catalog
        }
        
        if clean_name in method_mappings:
            try:
                method_mappings[clean_name]()
                return True
            except Exception as e:
                self.logger.error(f"Error calling method for {clean_name}: {e}")
        
        self.logger.warning(f"No launch method found for tool: {clean_name}")
        return False
        
    def _track_tool_usage(self, tool_name):
        """Track tool usage in database if available."""
        try:
            if hasattr(self, 'db_manager') and self.db_manager:
                query = """
                    INSERT INTO tool_usage (tool_name, launch_time, session_id) 
                    VALUES (?, datetime('now'), ?)
                """
                session_id = getattr(self, 'session_id', 'unknown')
                self.db_manager.execute_update(query, (tool_name, session_id))
        except Exception as e:
            self.logger.debug(f"Failed to track tool usage: {e}")
'''
    
    # Insert helper methods
    insert_pos = content.find("    def _on_discovered_tool_activated")
    if insert_pos != -1:
        content = content[:insert_pos] + helper_methods + content[insert_pos:]
    
    return content

def fix_error_reporting(content: str) -> str:
    """Fix error reporting to provide better user feedback."""
    
    # Add user error reporting method
    error_method = '''
    def _show_user_error(self, title, message):
        """Show user-friendly error dialog."""
        try:
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            
            # Also update status bar
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(f"Error: {title}", 5000)
                
        except Exception as e:
            self.logger.error(f"Failed to show error dialog: {e}")
            print(f"ERROR: {title} - {message}")
'''
    
    # Insert the method
    insert_pos = content.find("    def _on_discovered_tool_activated")
    if insert_pos != -1:
        content = content[:insert_pos] + error_method + content[insert_pos:]
    
    return content

def fix_fallback_tools(content: str) -> str:
    """Improve the fallback tools system."""
    
    # Enhanced create_enhanced_tools_widget method
    old_widget_method = '''    def create_enhanced_tools_widget(self):
        """Create enhanced tools widget with automatic tool discovery."""
        tools_tree = QTreeWidget()
        tools_tree.setHeaderLabels(["RFU Tools"])
        
        # Discover tools from src/tools directory
        discovered_tools = self._discover_tools_from_directory()
        
        if not discovered_tools:
            # Fallback to basic tools if discovery fails
            self.logger.warning("Tool discovery failed, using fallback tools")
            return self._create_fallback_tools_widget()'''
    
    new_widget_method = '''    def create_enhanced_tools_widget(self):
        """Create enhanced tools widget with automatic tool discovery and robust fallbacks."""
        tools_tree = QTreeWidget()
        tools_tree.setHeaderLabels(["RFU Tools"])
        tools_tree.setToolTip("Double-click tools to launch them")
        
        # Enhanced styling for better visibility
        tools_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #ccc;
                font-size: 12px;
            }
            QTreeWidget::item {
                padding: 3px;
                border-bottom: 1px solid #eee;
            }
            QTreeWidget::item:hover {
                background-color: #e3f2fd;
            }
            QTreeWidget::item:selected {
                background-color: #2196f3;
                color: white;
            }
        """)
        
        # Discover tools from src/tools directory
        discovered_tools = self._discover_tools_from_directory()
        
        if not discovered_tools:
            # Fallback to basic tools if discovery fails
            self.logger.warning("Tool discovery failed, using fallback tools")
            discovered_tools = self._get_hardcoded_fallback_tools()'''
    
    content = content.replace(old_widget_method, new_widget_method)
    
    # Enhance the tree creation part
    old_tree_creation = '''        # Create categorized tree structure
        for category, tools in discovered_tools.items():
            if not tools:  # Skip empty categories
                continue
                
            category_item = QTreeWidgetItem([category])
            category_item.setExpanded(True)
            
            for tool_info in tools:
                tool_name = tool_info.get('display_name', tool_info['name'])
                icon = tool_info.get('icon', '🔧')
                module_path = tool_info['module_path']
                class_name = tool_info['class_name']
                
                tool_item = QTreeWidgetItem([f"{icon} {tool_name}"])
                # Store tool launch information
                tool_item.setData(0, Qt.UserRole, {
                    'name': tool_name,
                    'module_path': module_path,
                    'class_name': class_name,
                    'category': category
                })
                category_item.addChild(tool_item)
            
            tools_tree.addTopLevelItem(category_item)
        
        tools_tree.itemDoubleClicked.connect(self._on_discovered_tool_activated)
        return tools_tree'''
    
    new_tree_creation = '''        # Create categorized tree structure with enhanced error handling
        tools_added = 0
        for category, tools in discovered_tools.items():
            if not tools:  # Skip empty categories
                continue
                
            category_item = QTreeWidgetItem([f"📁 {category}"])
            category_item.setExpanded(True)
            category_item.setToolTip(f"Category: {category}")
            
            category_tools_added = 0
            for tool_info in tools:
                try:
                    tool_name = tool_info.get('display_name', tool_info.get('name', 'Unknown Tool'))
                    icon = tool_info.get('icon', '🔧')
                    module_path = tool_info.get('module_path', '')
                    class_name = tool_info.get('class_name', '')
                    
                    tool_item = QTreeWidgetItem([f"{icon} {tool_name}"])
                    tool_item.setToolTip(f"Double-click to launch {tool_name}")
                    
                    # Store tool launch information
                    tool_item.setData(0, Qt.UserRole, {
                        'name': tool_name,
                        'display_name': tool_name,
                        'module_path': module_path,
                        'class_name': class_name,
                        'category': category
                    })
                    category_item.addChild(tool_item)
                    category_tools_added += 1
                    
                except Exception as e:
                    self.logger.warning(f"Error adding tool {tool_info}: {e}")
                    continue
            
            if category_tools_added > 0:
                tools_tree.addTopLevelItem(category_item)
                tools_added += category_tools_added
        
        # Ensure we have at least some tools visible
        if tools_added == 0:
            self.logger.warning("No tools were successfully added, creating minimal fallback")
            self._create_minimal_tool_fallback(tools_tree)
        
        # Connect events with error handling
        try:
            tools_tree.itemDoubleClicked.connect(self._on_discovered_tool_activated)
            self.logger.info(f"Tools widget created with {tools_added} tools")
        except Exception as e:
            self.logger.error(f"Error connecting tool activation signal: {e}")
        
        return tools_tree'''
    
    content = content.replace(old_tree_creation, new_tree_creation)
    
    # Add minimal fallback method
    minimal_fallback = '''
    def _create_minimal_tool_fallback(self, tools_tree):
        """Create minimal tool fallback when all else fails."""
        try:
            emergency_item = QTreeWidgetItem(["⚠️ Emergency Tools"])
            emergency_item.setExpanded(True)
            
            # Add basic system tools that should always work
            basic_tools = [
                ("📁 File Explorer", lambda: self._open_file_explorer()),
                ("🏠 Home Directory", lambda: self._navigate_to_home()),
                ("💻 System Info", lambda: self._show_system_info())
            ]
            
            for tool_name, callback in basic_tools:
                tool_item = QTreeWidgetItem([tool_name])
                tool_item.setData(0, Qt.UserRole, callback)
                tool_item.setToolTip(f"Click to {tool_name}")
                emergency_item.addChild(tool_item)
            
            tools_tree.addTopLevelItem(emergency_item)
            self.logger.info("Created minimal emergency tools fallback")
            
        except Exception as e:
            self.logger.error(f"Failed to create minimal fallback: {e}")
    
    def _navigate_to_home(self):
        """Navigate active pane to home directory."""
        try:
            if self.panes and self.active_pane_index < len(self.panes):
                active_pane = self.panes[self.active_pane_index]
                home_path = Path.home()
                self._navigate_to_path(active_pane, home_path)
            self.statusBar().showMessage("Navigated to home directory", 2000)
        except Exception as e:
            self.logger.error(f"Error navigating to home: {e}")
    
    def _show_system_info(self):
        """Show basic system information."""
        try:
            import platform
            info = f"System: {platform.system()}\\n"
            info += f"Version: {platform.version()}\\n"
            info += f"Machine: {platform.machine()}\\n"
            info += f"Python: {platform.python_version()}"
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "System Information", info)
        except Exception as e:
            self.logger.error(f"Error showing system info: {e}")
'''
    
    # Insert minimal fallback methods
    insert_pos = content.find("    def _show_user_error")
    if insert_pos != -1:
        content = content[:insert_pos] + minimal_fallback + content[insert_pos:]
    
    return content

def main():
    """Main function to apply the tool launching fixes."""
    try:
        success = patch_multi_pane_explorer()
        if success:
            print("✅ Tool launching fixes applied successfully!")
            print("\nFixes applied:")
            print("1. Enhanced tool discovery with better error handling")
            print("2. Improved event handling for tool activation") 
            print("3. Enhanced import path resolution with fallback strategies")
            print("4. Better error reporting for users")
            print("5. Improved fallback tool system")
            print("\nPlease restart your application to test the fixes.")
        else:
            print("❌ Failed to apply fixes. Please check the file paths.")
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()