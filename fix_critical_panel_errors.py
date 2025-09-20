#!/usr/bin/env python3
"""
Critical Fix for Panel Creation Errors

This script fixes the specific errors causing the left panel to fail in the multi-pane explorer.
"""

import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('CriticalPanelFix')

def fix_tooltip_error():
    """Fix the setToolTip error that's causing panel creation to fail."""
    
    explorer_file = Path(__file__).parent / "src" / "file_explorer" / "multi_pane_explorer.py"
    
    if not explorer_file.exists():
        logger.error(f"Multi-pane explorer file not found: {explorer_file}")
        return False
    
    # Read current content
    with open(explorer_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the tooltip issue - find and replace problematic setToolTip calls
    fixes = [
        # Fix 1: Replace item.setToolTip(0, tooltip) calls with proper column parameter
        (
            'item.setToolTip(f"Double-click to launch {tool_name}")',
            'item.setToolTip(0, f"Double-click to launch {tool_name}")'
        ),
        (
            'item.setToolTip(f"Category: {category}")',
            'item.setToolTip(0, f"Category: {category}")'
        ),
        (
            'item.setToolTip(f"Click to {tool_name}")',
            'item.setToolTip(0, f"Click to {tool_name}")'
        ),
        # Fix 2: Add error handling around tooltip setting
        (
            'tool_item.setToolTip(f"Double-click to launch {tool_name}")',
            '''try:
                        tool_item.setToolTip(0, f"Double-click to launch {tool_name}")
                    except Exception as tooltip_error:
                        self.logger.debug(f"Tooltip error ignored: {tooltip_error}")'''
        ),
        # Fix 3: Fix category tooltip
        (
            'category_item.setToolTip(f"Category: {category}")',
            '''try:
                category_item.setToolTip(0, f"Category: {category}")
            except Exception as tooltip_error:
                self.logger.debug(f"Category tooltip error ignored: {tooltip_error}")'''
        )
    ]
    
    modified = False
    for old_text, new_text in fixes:
        if old_text in content:
            content = content.replace(old_text, new_text)
            modified = True
            logger.info(f"Fixed tooltip issue: {old_text[:50]}...")
    
    # Additional safety fix - wrap the entire tools tree creation in try-catch
    tools_tree_creation = '''        # Create categorized tree structure with enhanced error handling
        tools_added = 0
        for category, tools in discovered_tools.items():
            if not tools:  # Skip empty categories
                continue
                
            category_item = QTreeWidgetItem([f"📁 {category}"])
            category_item.setExpanded(True)
            try:
                category_item.setToolTip(0, f"Category: {category}")
            except Exception as tooltip_error:
                self.logger.debug(f"Category tooltip error ignored: {tooltip_error}")
            
            category_tools_added = 0
            for tool_info in tools:
                try:
                    tool_name = tool_info.get('display_name', tool_info.get('name', 'Unknown Tool'))
                    icon = tool_info.get('icon', '🔧')
                    module_path = tool_info.get('module_path', '')
                    class_name = tool_info.get('class_name', '')
                    
                    tool_item = QTreeWidgetItem([f"{icon} {tool_name}"])
                    try:
                        tool_item.setToolTip(0, f"Double-click to launch {tool_name}")
                    except Exception as tooltip_error:
                        self.logger.debug(f"Tool tooltip error ignored: {tooltip_error}")
                    
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
                tools_added += category_tools_added'''
    
    # Find and replace the problematic section
    old_pattern = '''        # Create categorized tree structure with enhanced error handling
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
                tools_added += category_tools_added'''
    
    if old_pattern in content:
        content = content.replace(old_pattern, tools_tree_creation)
        modified = True
        logger.info("Fixed tools tree creation with proper tooltip handling")
    
    if modified:
        # Create backup
        backup_file = explorer_file.with_suffix('.py.critical_backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            with open(explorer_file, 'r', encoding='utf-8') as original:
                f.write(original.read())
        
        # Write fixed content
        with open(explorer_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info("Critical panel fixes applied successfully!")
        return True
    else:
        logger.info("No critical fixes were needed")
        return False

def main():
    """Apply critical fixes for panel creation errors."""
    print("Applying critical fixes for panel creation errors...")
    
    success = fix_tooltip_error()
    
    if success:
        print("✅ Critical fixes applied successfully!")
        print("\nFixes applied:")
        print("1. Fixed setToolTip parameter errors")
        print("2. Added error handling around tooltip creation")
        print("3. Made tooltip creation more robust")
        print("\nPlease restart the application to test the fixes.")
    else:
        print("ℹ️ No critical fixes were needed.")
    
    print("\nTo test:")
    print("1. Run: python main.py")
    print("2. Choose 'Multi-Pane Explorer' interface")
    print("3. Check that the left panel loads without 'Error' messages")
    print("4. Try double-clicking tools in the sidebar")

if __name__ == "__main__":
    main()