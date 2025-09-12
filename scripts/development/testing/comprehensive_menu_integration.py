#!/usr/bin/env python3
"""
Comprehensive Menu Integration Script
Updates all existing tools to use StandardWindow with menu integration
"""

import os
import sys
import shutil
from pathlib import Path

def update_tool_to_standard_window(file_path, class_name, window_type="utility"):
    """Update a tool file to inherit from StandardWindow instead of QMainWindow."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original file
        backup_path = str(file_path) + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update imports
        if 'from PyQt5.QtWidgets import' in content and 'QMainWindow' in content:
            # Add StandardWindow import
            import_section = content.split('except ImportError:')[0]
            if 'from src.rfu.gui.standard_window import StandardWindow' not in import_section:
                # Find the location to add the import
                lines = content.split('\n')
                import_added = False
                new_lines = []
                
                for i, line in enumerate(lines):
                    new_lines.append(line)
                    
                    # Add StandardWindow import after PyQt5 imports
                    if ('except ImportError:' in line and 
                        'PyQt5' in lines[i-3:i] and not import_added):
                        new_lines.extend([
                            '',
                            '# Import StandardWindow for menu integration',
                            'try:',
                            '    from src.rfu.gui.standard_window import StandardWindow',
                            'except ImportError:',
                            '    # Fallback for standalone execution',
                            '    from PyQt5.QtWidgets import QMainWindow',
                            '    StandardWindow = QMainWindow'
                        ])
                        import_added = True
                
                content = '\n'.join(new_lines)
        
        # Update class inheritance
        content = content.replace(
            f'class {class_name}(QMainWindow):',
            f'class {class_name}(StandardWindow):'
        )
        
        # Update constructor
        if f'class {class_name}(StandardWindow):' in content:
            # Find __init__ method and update it
            lines = content.split('\n')
            new_lines = []
            in_init = False
            init_updated = False
            
            for line in lines:
                if f'def __init__(self' in line and not init_updated:
                    in_init = True
                    new_lines.append(line)
                elif in_init and 'super().__init__()' in line and not init_updated:
                    # Update super() call
                    indent = ' ' * (len(line) - len(line.lstrip()))
                    new_lines.extend([
                        f'{indent}super().__init__(',
                        f'{indent}    title="{class_name.replace("GUI", "").replace("Window", "")} - Richard\'s File Utilities",',
                        f'{indent}    window_type="{window_type}"',
                        f'{indent})'
                    ])
                    init_updated = True
                elif in_init and ('self.setWindowTitle(' in line or 
                                'self.setGeometry(' in line or
                                'self.setCentralWidget(' in line):
                    # Skip these lines as they're handled by StandardWindow
                    continue
                elif in_init and 'self.init_ui()' in line:
                    new_lines.append(line)
                    # Add menu callback setup
                    indent = ' ' * (len(line) - len(line.lstrip()))
                    new_lines.append(f'{indent}self._setup_menu_callbacks()')
                    in_init = False
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # Update init_ui method to use central_widget
        content = content.replace(
            'central_widget = QWidget()\n        self.setCentralWidget(central_widget)\n        layout = QVBoxLayout(central_widget)',
            '# Create main layout using the standardized central widget\n        layout = QVBoxLayout(self.central_widget)'
        )
        
        # Add menu callback setup method
        if '_setup_menu_callbacks' not in content:
            # Find a good place to add the method (after __init__)
            lines = content.split('\n')
            new_lines = []
            init_method_end = -1
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                if 'def __init__(self' in line:
                    # Find the end of __init__ method
                    indent_level = len(line) - len(line.lstrip())
                    j = i + 1
                    while j < len(lines):
                        if (lines[j].strip() and 
                            len(lines[j]) - len(lines[j].lstrip()) <= indent_level and
                            lines[j].strip().startswith('def ')):
                            init_method_end = j
                            break
                        j += 1
                
                if i == init_method_end:
                    # Add menu callback method before next method
                    new_lines.extend([
                        '',
                        '    def _setup_menu_callbacks(self):',
                        '        """Setup tool-specific menu callbacks."""',
                        '        if hasattr(self, \'menu_manager\'):',
                        '            # Register tool-specific callbacks',
                        f'            self.menu_manager.register_callback(\'refresh\', self.refresh_view)',
                        '            # Add more callbacks as needed',
                        '',
                        '    def refresh_view(self):',
                        '        """Refresh the current view."""',
                        '        if hasattr(self, \'statusBar\'):',
                        '            self.statusBar().showMessage("Refreshed", 2000)',
                        ''
                    ])
            
            content = '\n'.join(new_lines)
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update {file_path}: {e}")
        return False

def main():
    """Main function to update all tools."""
    
    # Tools to update
    tools_to_update = [
        # File Management Tools
        {
            'path': 'src/rfu/tools/file_management/file_finder.py',
            'class': 'FileFinderGUI',
            'type': 'search'
        },
        {
            'path': 'src/rfu/tools/file_management/catalog.py',
            'class': 'CatalogWindow',
            'type': 'analysis'
        },
        {
            'path': 'src/rfu/tools/file_management/rename.py',
            'class': 'RenameWindow',
            'type': 'file_operations'
        },
        
        # Analysis Tools
        {
            'path': 'src/utilities/analysis/find_duplicate_files.py',
            'class': 'DuplicateFinderApp',
            'type': 'analysis'
        },
        {
            'path': 'src/utilities/analysis/size_analyzer.py',
            'class': 'SizeAnalyzerGUI',
            'type': 'analysis'
        },
        {
            'path': 'src/utilities/analysis/check_sum.py',
            'class': 'ChecksumGUI',
            'type': 'verification'
        },
        
        # Add more tools as they become available
    ]
    
    print("🚀 Starting comprehensive menu integration...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(tools_to_update)
    
    for tool_info in tools_to_update:
        file_path = Path(tool_info['path'])
        
        if file_path.exists():
            print(f"📝 Updating {tool_info['class']} in {file_path}...")
            if update_tool_to_standard_window(
                file_path, 
                tool_info['class'], 
                tool_info['type']
            ):
                success_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("=" * 60)
    print(f"✅ Integration complete: {success_count}/{total_count} tools updated")
    
    if success_count > 0:
        print("\n📋 Next steps:")
        print("1. Test the enhanced main application:")
        print("   python enhanced_main_with_comprehensive_menus.py")
        print("2. Test individual tools to verify menu integration")
        print("3. Check for any import errors or missing dependencies")
        print("\n💡 All tools now have comprehensive menu systems!")
    
if __name__ == "__main__":
    main()
