#!/usr/bin/env python3
"""
Folder Refactoring Script: 1_1 to pdf_utilities
This script handles the systematic renaming of the 1_1 folder to pdf_utilities
and updates all references throughout the project.
"""

import os
import shutil
import sys
from pathlib import Path


def rename_folder():
    """Rename the 1_1 folder to pdf_utilities"""
    source_folder = Path("1_1")
    target_folder = Path("pdf_utilities")
    
    if not source_folder.exists():
        print(f"❌ Source folder {source_folder} does not exist!")
        return False
    
    if target_folder.exists():
        print(f"⚠️  Target folder {target_folder} already exists!")
        response = input("Do you want to remove it and continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Refactoring cancelled.")
            return False
        shutil.rmtree(target_folder)
        print(f"🗑️  Removed existing {target_folder}")
    
    try:
        shutil.move(str(source_folder), str(target_folder))
        print(f"✅ Successfully renamed {source_folder} to {target_folder}")
        return True
    except Exception as e:
        print(f"❌ Error renaming folder: {e}")
        return False


def update_markdown_files():
    """Update all markdown files to replace 1_1 references with pdf_utilities"""
    markdown_files = [
        "README.md",
        "PDF_TOOLS_USER_GUIDE.md", 
        "PDF_TOOLS_TROUBLESHOOTING.md",
        "INTEGRATION_SUMMARY.md",
        "integrate_pdf_utilities.md",
        "file_inventory_analysis.md",
        "configuration_logging_analysis.md"
    ]
    
    updated_files = []
    
    for file_path in markdown_files:
        if not Path(file_path).exists():
            print(f"⚠️  File {file_path} not found, skipping...")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count replacements
            original_count = content.count('1_1')
            
            # Replace all instances of 1_1 with pdf_utilities
            updated_content = content.replace('1_1', 'pdf_utilities')
            
            if original_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"✅ Updated {file_path}: {original_count} replacements")
                updated_files.append((file_path, original_count))
            else:
                print(f"ℹ️  No changes needed in {file_path}")
                
        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
    
    return updated_files


def verify_python_files():
    """Verify that Python files have been updated correctly"""
    python_files = [
        "rfuhub.py",
        "integration_test.py",
        "pdf_utilities/log_config.py"
    ]
    
    issues = []
    
    for file_path in python_files:
        if not Path(file_path).exists():
            issues.append(f"❌ File {file_path} not found")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for remaining 1_1 references
            remaining_refs = content.count('1_1')
            if remaining_refs > 0:
                issues.append(f"⚠️  {file_path} still contains {remaining_refs} '1_1' references")
            else:
                print(f"✅ {file_path} - no remaining '1_1' references")
                
        except Exception as e:
            issues.append(f"❌ Error checking {file_path}: {e}")
    
    return issues


def main():
    """Main refactoring process"""
    print("🔄 Starting PDF Utilities Folder Refactoring")
    print("=" * 50)
    
    # Step 1: Rename the folder
    print("\n📁 Step 1: Renaming folder...")
    if not rename_folder():
        print("❌ Folder rename failed. Stopping refactoring.")
        return False
    
    # Step 2: Update markdown files
    print("\n📝 Step 2: Updating documentation files...")
    updated_files = update_markdown_files()
    
    # Step 3: Verify Python files
    print("\n🐍 Step 3: Verifying Python files...")
    issues = verify_python_files()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 REFACTORING SUMMARY")
    print("=" * 50)
    
    print(f"✅ Folder renamed: 1_1 → pdf_utilities")
    print(f"📝 Documentation files updated: {len(updated_files)}")
    
    if updated_files:
        print("\nUpdated files:")
        for file_path, count in updated_files:
            print(f"  • {file_path}: {count} replacements")
    
    if issues:
        print(f"\n⚠️  Issues found: {len(issues)}")
        for issue in issues:
            print(f"  • {issue}")
        return False
    else:
        print("\n🎉 Refactoring completed successfully!")
        print("\nNext steps:")
        print("1. Test the integration by running the main application")
        print("2. Verify PDF Tools button works correctly")
        print("3. Check that all PDF utilities are accessible")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)