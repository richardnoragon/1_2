#!/usr/bin/env python3
"""
Automated Tool Integration Script for Richard's File Utilities

This script automatically integrates legacy tools into the main application by:
1. Scanning for available tools
2. Copying them to the root directory
3. Fixing import statements
4. Installing missing dependencies
5. Creating class aliases for compatibility
6. Testing imports
"""

import os
import sys
import shutil
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class ToolIntegrator:
    """Automated tool integration class."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.src_dir = self.root_dir / "src"
        self.legacy_dir = self.src_dir / "legacy" / "file_utilities_1"
        self.utilities_dir = self.src_dir / "utilities"
        
        # Track integrated tools
        self.integrated_tools = []
        self.failed_tools = []
        self.dependencies_installed = set()
        
        # Common import fixes
        self.import_fixes = {
            'from gui.common.base_window import BaseWindow': 
                'from gui.common.base_window_simple import BaseWindow',
            'from gui.common.dialogs import': 
                'from gui.common.dialogs_simple import',
            'from gui.common.widgets import': 
                'from gui.common.widgets_simple import',
            'from log_manager import': 
                'from log_manager import',
            'from config_manager import': 
                'from config_manager import',
        }
        
        # Common dependencies that might be needed
        self.common_dependencies = [
            'python-docx', 'PyPDF2', 'chardet', 'mutagen', 'Pillow',
            'openpyxl', 'pandas', 'numpy', 'cryptography'
        ]
    
    def scan_available_tools(self) -> List[Path]:
        """Scan for available Python tools in legacy and utilities directories."""
        tools = []
        
        print("Scanning for available tools...")
        
        # Scan legacy directory
        if self.legacy_dir.exists():
            for file_path in self.legacy_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    tools.append(file_path)
                    print(f"  Found legacy tool: {file_path.name}")
        
        # Scan utilities subdirectories
        if self.utilities_dir.exists():
            for subdir in self.utilities_dir.iterdir():
                if subdir.is_dir():
                    for file_path in subdir.glob("**/*.py"):
                        if (file_path.name != "__init__.py" and 
                            "gui" in file_path.name.lower() and
                            file_path.name not in [f.name for f in tools]):
                            tools.append(file_path)
                            print(f"  Found utility tool: {file_path.name}")
        
        print(f"Total tools found: {len(tools)}")
        return tools
    
    def extract_class_names(self, file_path: Path) -> List[str]:
        """Extract class names from a Python file."""
        class_names = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Find class definitions
            class_pattern = r'class\s+(\w+)\s*\([^)]*\):'
            matches = re.findall(class_pattern, content)
            
            # Filter for likely GUI classes
            for match in matches:
                if any(keyword in match.lower() for keyword in 
                      ['window', 'gui', 'dialog', 'widget', 'app']):
                    class_names.append(match)
            
        except Exception as e:
            print(f"    Error extracting classes from {file_path.name}: {e}")
        
        return class_names
    
    def fix_imports(self, content: str) -> str:
        """Fix import statements in tool content."""
        for old_import, new_import in self.import_fixes.items():
            content = content.replace(old_import, new_import)
        
        # Fix relative imports
        content = re.sub(r'from\s+\.([^.\s]+)\s+import', r'from \1 import', content)
        
        return content
    
    def install_dependencies(self, file_path: Path) -> bool:
        """Install dependencies found in the file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract import statements
            import_pattern = r'import\s+(\w+)|from\s+(\w+)\s+import'
            matches = re.findall(import_pattern, content)
            
            dependencies_to_install = []
            for match in matches:
                module = match[0] or match[1]
                if module in ['docx', 'PyPDF2', 'chardet', 'mutagen', 'PIL',
                             'openpyxl', 'pandas', 'numpy', 'cryptography']:
                    dep_name = {
                        'docx': 'python-docx',
                        'PIL': 'Pillow'
                    }.get(module, module)
                    
                    if dep_name not in self.dependencies_installed:
                        dependencies_to_install.append(dep_name)
            
            # Install dependencies
            for dep in dependencies_to_install:
                print(f"    Installing dependency: {dep}")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', dep
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.dependencies_installed.add(dep)
                    print(f"    ✅ {dep} installed successfully")
                else:
                    print(f"    ❌ Failed to install {dep}: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"    Error installing dependencies: {e}")
            return False
    
    def integrate_tool(self, tool_path: Path) -> bool:
        """Integrate a single tool."""
        tool_name = tool_path.stem
        target_path = self.root_dir / f"{tool_name}.py"
        
        print(f"\nIntegrating tool: {tool_name}")
        
        try:
            # Copy the tool file
            print(f"  Copying {tool_path} to {target_path}")
            shutil.copy2(tool_path, target_path)
            
            # Read and fix the content
            with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Fix imports
            print("  Fixing imports...")
            fixed_content = self.fix_imports(content)
            
            # Extract class names
            class_names = self.extract_class_names(target_path)
            print(f"  Found classes: {class_names}")
            
            # Add compatibility aliases
            if class_names:
                aliases = []
                for class_name in class_names:
                    if 'Window' in class_name and 'GUI' not in class_name:
                        aliases.append(f"{class_name.replace('Window', 'GUI')} = {class_name}")
                    elif 'App' in class_name and 'GUI' not in class_name:
                        aliases.append(f"{class_name.replace('App', 'GUI')} = {class_name}")
                
                if aliases:
                    fixed_content += "\n\n# Compatibility aliases\n"
                    fixed_content += "\n".join(aliases)
                    print(f"  Added aliases: {aliases}")
            
            # Write fixed content
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Install dependencies
            print("  Installing dependencies...")
            if not self.install_dependencies(target_path):
                print("  ⚠️  Some dependencies failed to install")
            
            # Test import
            print("  Testing import...")
            if self.test_import(tool_name, class_names):
                print(f"  ✅ {tool_name} integrated successfully!")
                self.integrated_tools.append((tool_name, class_names))
                return True
            else:
                print(f"  ❌ {tool_name} import test failed")
                self.failed_tools.append(tool_name)
                return False
                
        except Exception as e:
            print(f"  ❌ Error integrating {tool_name}: {e}")
            self.failed_tools.append(tool_name)
            return False
    
    def test_import(self, tool_name: str, class_names: List[str]) -> bool:
        """Test if a tool can be imported successfully."""
        try:
            # Test basic module import
            exec(f"import {tool_name}")
            
            # Test class imports if available
            if class_names:
                for class_name in class_names:
                    try:
                        exec(f"from {tool_name} import {class_name}")
                    except ImportError:
                        continue
            
            return True
            
        except Exception as e:
            print(f"    Import test error: {e}")
            return False
    
    def update_main_py(self) -> None:
        """Update main.py with the correct class names for integrated tools."""
        print("\nUpdating main.py with integrated tools...")
        
        main_py_path = self.root_dir / "main.py"
        if not main_py_path.exists():
            print("  ❌ main.py not found")
            return
        
        with open(main_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update tool launcher methods with correct class names
        for tool_name, class_names in self.integrated_tools:
            if class_names:
                primary_class = class_names[0]
                
                # Find and update the launch_tool call for this tool
                pattern = rf'(self\.launch_tool\([^,]+,\s*["\']){tool_name}(["\'],\s*["\'])\w+(["\'])'
                replacement = rf'\g<1>{tool_name}\g<2>{primary_class}\g<3>'
                content = re.sub(pattern, replacement, content)
        
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("  ✅ main.py updated")
    
    def generate_report(self) -> None:
        """Generate integration report."""
        print("\n" + "="*60)
        print("TOOL INTEGRATION REPORT")
        print("="*60)
        
        print(f"\n✅ Successfully Integrated Tools ({len(self.integrated_tools)}):")
        for tool_name, class_names in self.integrated_tools:
            print(f"  • {tool_name}: {', '.join(class_names)}")
        
        if self.failed_tools:
            print(f"\n❌ Failed to Integrate ({len(self.failed_tools)}):")
            for tool_name in self.failed_tools:
                print(f"  • {tool_name}")
        
        print(f"\n📦 Dependencies Installed ({len(self.dependencies_installed)}):")
        for dep in sorted(self.dependencies_installed):
            print(f"  • {dep}")
        
        print(f"\n🎯 Integration Success Rate: {len(self.integrated_tools)}/{len(self.integrated_tools) + len(self.failed_tools)} ({len(self.integrated_tools)/(len(self.integrated_tools) + len(self.failed_tools))*100:.1f}%)")
        
        print("\n" + "="*60)
    
    def run_integration(self) -> None:
        """Run the complete integration process."""
        print("🚀 Starting Automated Tool Integration")
        print("="*50)
        
        # Scan for tools
        tools = self.scan_available_tools()
        
        if not tools:
            print("❌ No tools found to integrate")
            return
        
        # Integrate each tool
        for tool_path in tools:
            self.integrate_tool(tool_path)
        
        # Update main.py
        self.update_main_py()
        
        # Generate report
        self.generate_report()
        
        print("\n🎉 Integration process completed!")


def main():
    """Main function."""
    integrator = ToolIntegrator()
    integrator.run_integration()


if __name__ == '__main__':
    main()
