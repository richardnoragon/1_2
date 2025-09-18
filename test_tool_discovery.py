#!/usr/bin/env python3
"""
Test script for tool discovery functionality
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test the tool discovery logic
def test_tool_discovery():
    """Test the tool discovery functionality independently."""
    print("Testing Tool Discovery System")
    print("=" * 50)
    
    # Mock the logger
    class MockLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def debug(self, msg): print(f"DEBUG: {msg}")
    
    # Create a test instance to access methods
    class ToolDiscoveryTester:
        def __init__(self):
            self.logger = MockLogger()
        
        def _discover_tools_from_directory(self):
            """Discover tools from the src/tools directory structure."""
            tools_dir = Path(__file__).parent / "src" / "tools"
            discovered_tools = {}
            
            try:
                if not tools_dir.exists():
                    self.logger.warning(f"Tools directory not found: {tools_dir}")
                    return {}
                
                # Category mapping for organization
                category_mapping = {
                    'file_management': 'File Management',
                    'analysis': 'Analysis',
                    'security': 'Security',
                    'pdf_tools': 'PDF Tools',
                    'network': 'Network',
                    'system': 'System',
                    'metadata': 'Metadata',
                    'file_operations': 'File Operations',
                    'privacy': 'Privacy'
                }
                
                # Icon mapping for different tool types
                icon_mapping = {
                    'file_management': '📁',
                    'analysis': '📊',
                    'security': '🔒',
                    'pdf_tools': '📄',
                    'network': '🌐',
                    'system': '⚙️',
                    'metadata': '🏷️',
                    'file_operations': '📋',
                    'privacy': '🛡️'
                }
                
                for category_dir in tools_dir.iterdir():
                    if category_dir.is_dir() and not category_dir.name.startswith('_'):
                        category_name = category_mapping.get(category_dir.name, category_dir.name.title())
                        category_icon = icon_mapping.get(category_dir.name, '🔧')
                        
                        tools_in_category = []
                        self._scan_directory_for_tools(category_dir, tools_in_category, category_icon)
                        
                        if tools_in_category:
                            discovered_tools[category_name] = tools_in_category
                
                self.logger.info(f"Discovered {sum(len(tools) for tools in discovered_tools.values())} tools in {len(discovered_tools)} categories")
                return discovered_tools
                
            except Exception as e:
                self.logger.error(f"Error discovering tools: {e}")
                return {}
        
        def _scan_directory_for_tools(self, directory, tools_list, default_icon):
            """Recursively scan directory for tool files."""
            try:
                # Look for Python files that could be tools
                for item in directory.iterdir():
                    if item.is_file() and item.suffix == '.py' and not item.name.startswith('_'):
                        tool_info = self._analyze_python_file_for_tool(item, default_icon)
                        if tool_info:
                            tools_list.append(tool_info)
                    elif item.is_dir() and not item.name.startswith('_'):
                        # Check subdirectories
                        self._scan_directory_for_tools(item, tools_list, default_icon)
                        
            except Exception as e:
                self.logger.warning(f"Error scanning directory {directory}: {e}")
        
        def _analyze_python_file_for_tool(self, file_path, default_icon):
            """Analyze a Python file to determine if it's a launchable tool."""
            try:
                # Create module path from file path
                relative_path = file_path.relative_to(Path(__file__).parent)
                module_path = str(relative_path.with_suffix('')).replace(os.sep, '.')
                
                # Try to extract class information
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for GUI classes (common patterns)
                import re
                gui_class_patterns = [
                    r'class\s+(\w*GUI)\s*\(',
                    r'class\s+(\w*App)\s*\(',
                    r'class\s+(\w*Window)\s*\(',
                    r'class\s+(\w*Tool)\s*\(',
                    r'class\s+(\w*Dialog)\s*\(',
                    r'class\s+(\w*Widget)\s*\('
                ]
                
                class_name = None
                for pattern in gui_class_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Prefer GUI classes over others
                        gui_matches = [m for m in matches if 'GUI' in m or 'App' in m or 'Window' in m]
                        if gui_matches:
                            class_name = gui_matches[0]
                            break
                        else:
                            class_name = matches[0]
                            break
                
                if not class_name:
                    return None
                
                # Create display name from file name
                display_name = self._create_display_name(file_path.stem)
                
                return {
                    'name': file_path.stem,
                    'display_name': display_name,
                    'module_path': module_path,
                    'class_name': class_name,
                    'file_path': str(file_path),
                    'icon': default_icon
                }
                
            except Exception as e:
                self.logger.warning(f"Error analyzing file {file_path}: {e}")
                return None
        
        def _create_display_name(self, file_name):
            """Create a user-friendly display name from a file name."""
            # Handle common naming patterns
            name_replacements = {
                'file_finder': 'File Finder',
                'size_analyzer': 'Size Analyzer',
                'find_duplicate_files': 'Duplicate Finder',
                'duplicate_finder': 'Duplicate Finder',
                'en_and_decrypt': 'Encrypt/Decrypt',
                'secure_delete': 'Secure Delete',
                'check_sum': 'File Checksum',
                'organize': 'File Organizer',
                'catalog': 'File Catalog',
                'rename': 'File Renamer'
            }
            
            if file_name in name_replacements:
                return name_replacements[file_name]
            
            # Convert snake_case to Title Case
            return ' '.join(word.capitalize() for word in file_name.split('_'))
    
    # Run the test
    tester = ToolDiscoveryTester()
    discovered_tools = tester._discover_tools_from_directory()
    
    print(f"\nDiscovered Tools Summary:")
    print("-" * 30)
    
    for category, tools in discovered_tools.items():
        print(f"\n{category} ({len(tools)} tools):")
        for tool in tools:
            print(f"  {tool['icon']} {tool['display_name']}")
            print(f"    Module: {tool['module_path']}")
            print(f"    Class: {tool['class_name']}")
            print(f"    File: {tool['file_path']}")
    
    if not discovered_tools:
        print("No tools discovered!")
    else:
        total_tools = sum(len(tools) for tools in discovered_tools.values())
        print(f"\nTotal: {total_tools} tools in {len(discovered_tools)} categories")

if __name__ == "__main__":
    test_tool_discovery()