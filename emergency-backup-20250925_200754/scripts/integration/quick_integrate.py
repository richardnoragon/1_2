#!/usr/bin/env python3
"""
Quick Tool Integration Script

This script quickly integrates multiple tools by copying them,
fixing imports, and handling UI files.
"""

import os
import shutil
import re
from pathlib import Path


def integrate_tools():
    """Integrate multiple tools quickly."""
    print("🚀 Quick Tool Integration")
    print("=" * 40)
    
    root_dir = Path(__file__).parent
    legacy_dir = root_dir / "src" / "legacy" / "file_utilities_1"
    
    # Tools to integrate (prioritized list)
    priority_tools = [
        "catalog.py",
        "compress_decompress.py", 
        "empty_folders.py",
        "organize.py",
        "file_touch.py"
    ]
    
    successful = []
    failed = []
    
    for tool_name in priority_tools:
        print(f"\n🔧 Integrating {tool_name}...")
        
        tool_path = legacy_dir / tool_name
        if not tool_path.exists():
            print(f"❌ {tool_name} not found in legacy directory")
            failed.append(tool_name)
            continue
        
        try:
            # Copy Python file
            dest_py = root_dir / tool_name
            if not dest_py.exists():
                shutil.copy2(tool_path, dest_py)
                print(f"📄 Copied {tool_name}")
            
            # Copy UI file if exists
            ui_path = tool_path.with_suffix('.ui')
            if ui_path.exists():
                dest_ui = root_dir / ui_path.name
                if not dest_ui.exists():
                    shutil.copy2(ui_path, dest_ui)
                    print(f"🎨 Copied {ui_path.name}")
            
            # Fix imports
            fix_tool_imports(dest_py)
            
            successful.append(tool_name)
            print(f"✅ {tool_name} integrated successfully")
            
        except Exception as e:
            print(f"❌ Failed to integrate {tool_name}: {e}")
            failed.append(tool_name)
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Integration Summary")
    print(f"✅ Successful: {len(successful)}")
    for tool in successful:
        print(f"   - {tool}")
    
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for tool in failed:
            print(f"   - {tool}")


def fix_tool_imports(file_path):
    """Fix imports in a tool file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Import fixes
        fixes = [
            (r'from gui\.common\.base_window import BaseWindow', 
             'from gui.common.base_window_simple import BaseWindow'),
            (r'from gui\.common\.dialogs import ([^\\n]+)', 
             r'from gui.common.dialogs_simple import \1'),
            (r'from gui\.common\.widgets import ([^\\n]+)', 
             r'from gui.common.widgets_simple import \1'),
        ]
        
        modified = False
        for pattern, replacement in fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"🔧 Fixed imports in {file_path.name}")
    
    except Exception as e:
        print(f"❌ Error fixing imports: {e}")


if __name__ == '__main__':
    integrate_tools()
