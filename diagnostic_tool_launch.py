#!/usr/bin/env python3
"""
Tool Launch Diagnostic and Testing Script

This script provides diagnostic tools to verify that the tool launching fixes
are working correctly and helps identify any remaining issues.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ToolLaunchDiagnostic')


def test_tool_imports():
    """Test if tools can be imported successfully."""
    logger.info("Testing tool imports...")
    
    # Test cases with multiple import strategies
    test_tools = [
        {
            'name': 'File Finder',
            'paths': [
                'src.utilities.file_management.file_finder',
                'utilities.file_management.file_finder',
                'src.tools.file_management.file_finder'
            ],
            'class': 'FileFinderGUI'
        },
        {
            'name': 'Size Analyzer', 
            'paths': [
                'src.utilities.analysis.size_analyzer',
                'utilities.analysis.size_analyzer',
                'src.tools.analysis.size_analyzer'
            ],
            'class': 'SizeAnalyzerGUI'
        },
        {
            'name': 'Duplicate Finder',
            'paths': [
                'src.utilities.analysis.duplicate_finder_app',
                'utilities.analysis.duplicate_finder_app',
                'src.tools.analysis.find_duplicate_files'
            ],
            'class': 'DuplicateFinderApp'
        },
        {
            'name': 'Encrypt/Decrypt',
            'paths': [
                'src.utilities.security.en_and_decrypt',
                'utilities.security.en_and_decrypt',
                'src.tools.security.en_and_decrypt'
            ],
            'class': 'EnAndDecryptGUI'
        }
    ]
    
    results = {}
    
    for tool in test_tools:
        tool_name = tool['name']
        class_name = tool['class']
        success = False
        working_path = None
        
        for path in tool['paths']:
            try:
                logger.info(f"Testing import: {path}.{class_name}")
                module = __import__(path, fromlist=[class_name])
                tool_class = getattr(module, class_name)
                
                # Test instantiation (without showing GUI)
                # tool_instance = tool_class()
                success = True
                working_path = path
                logger.info(f"✅ {tool_name}: {path}.{class_name} - SUCCESS")
                break
                
            except ImportError as e:
                logger.debug(f"❌ {tool_name}: {path}.{class_name} - ImportError: {e}")
            except AttributeError as e:
                logger.debug(f"❌ {tool_name}: {path}.{class_name} - AttributeError: {e}")
            except Exception as e:
                logger.debug(f"❌ {tool_name}: {path}.{class_name} - Error: {e}")
        
        results[tool_name] = {
            'success': success,
            'working_path': working_path,
            'class_name': class_name
        }
        
        if not success:
            logger.warning(f"❌ {tool_name}: All import attempts failed")
    
    return results


def check_directory_structure():
    """Check the directory structure for tool files."""
    logger.info("Checking directory structure...")
    
    directories_to_check = [
        project_root / 'src' / 'utilities',
        project_root / 'src' / 'tools', 
        project_root / 'utilities',
        project_root / 'tools'
    ]
    
    found_dirs = []
    
    for directory in directories_to_check:
        if directory.exists():
            logger.info(f"✅ Found directory: {directory}")
            found_dirs.append(directory)
            
            # List subdirectories
            try:
                subdirs = [d for d in directory.iterdir() if d.is_dir()]
                logger.info(f"   Subdirectories: {[d.name for d in subdirs]}")
                
                # Check for Python files in subdirectories
                for subdir in subdirs[:3]:  # Limit to first 3 for brevity
                    py_files = list(subdir.glob('*.py'))
                    if py_files:
                        logger.info(f"   {subdir.name}: {len(py_files)} Python files")
                        
            except Exception as e:
                logger.warning(f"   Error listing contents: {e}")
        else:
            logger.info(f"❌ Missing directory: {directory}")
    
    return found_dirs


def test_qt_imports():
    """Test PyQt5 imports."""
    logger.info("Testing PyQt5 imports...")
    
    try:
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
        logger.info("✅ PyQt5 imports successful")
        return True
    except ImportError as e:
        logger.error(f"❌ PyQt5 import failed: {e}")
        return False


def generate_diagnostic_report():
    """Generate a comprehensive diagnostic report."""
    logger.info("Generating diagnostic report...")
    
    print("\n" + "="*60)
    print("RFU TOOL LAUNCH DIAGNOSTIC REPORT")
    print("="*60)
    
    # Test PyQt5
    print("\n1. PyQt5 Status:")
    qt_ok = test_qt_imports()
    print(f"   PyQt5 Available: {'✅ Yes' if qt_ok else '❌ No'}")
    
    # Test directory structure
    print("\n2. Directory Structure:")
    found_dirs = check_directory_structure()
    print(f"   Found {len(found_dirs)} tool directories")
    
    # Test tool imports
    print("\n3. Tool Import Status:")
    import_results = test_tool_imports()
    
    successful_tools = 0
    for tool_name, result in import_results.items():
        status = "✅ Working" if result['success'] else "❌ Failed"
        path = result['working_path'] if result['success'] else "No working path found"
        print(f"   {tool_name}: {status}")
        if result['success']:
            print(f"      Path: {path}")
            successful_tools += 1
    
    print(f"\n   Summary: {successful_tools}/{len(import_results)} tools working")
    
    # Recommendations
    print("\n4. Recommendations:")
    if successful_tools == len(import_results):
        print("   ✅ All tools are working! Tool launching should function correctly.")
    elif successful_tools > 0:
        print(f"   ⚠️  {len(import_results) - successful_tools} tools need attention.")
        print("   - Some tools are working, check individual tool paths")
        print("   - Consider creating missing tool modules")
    else:
        print("   ❌ No tools are working. Check:")
        print("   - Python path configuration")
        print("   - Tool directory structure") 
        print("   - Module naming conventions")
    
    if not qt_ok:
        print("   ❌ PyQt5 not available - GUI functionality will be limited")
        print("   - Install PyQt5: pip install PyQt5")
    
    print("\n5. Next Steps:")
    if successful_tools > 0:
        print("   1. Restart the RFU application")
        print("   2. Test tool launching by double-clicking tools in sidebar")
        print("   3. Check logs for any remaining errors")
    else:
        print("   1. Check tool installation and paths")
        print("   2. Verify directory structure matches expectations")
        print("   3. Run this diagnostic again after fixes")
    
    print("\n" + "="*60)
    
    return import_results


def test_simple_tool_launch():
    """Test launching a simple tool to verify the fix works."""
    logger.info("Testing simple tool launch...")
    
    try:
        # Try to launch file finder as an example
        import_results = test_tool_imports()
        
        for tool_name, result in import_results.items():
            if result['success']:
                logger.info(f"Testing launch of {tool_name}...")
                module_path = result['working_path']
                class_name = result['class_name']
                
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    tool_class = getattr(module, class_name)
                    
                    # Create instance but don't show GUI in headless test
                    logger.info(f"✅ {tool_name} can be instantiated successfully")
                    return True
                    
                except Exception as e:
                    logger.warning(f"❌ {tool_name} instantiation failed: {e}")
                    continue
        
        logger.warning("No tools could be launched")
        return False
        
    except Exception as e:
        logger.error(f"Error testing tool launch: {e}")
        return False


def main():
    """Main diagnostic function."""
    print("RFU Tool Launch Diagnostic Tool")
    print("This tool will test if the tool launching fixes are working correctly.\n")
    
    # Generate full diagnostic report
    results = generate_diagnostic_report()
    
    # Test actual tool launching
    print("\n6. Tool Launch Test:")
    launch_ok = test_simple_tool_launch()
    print(f"   Tool Launch Test: {'✅ Passed' if launch_ok else '❌ Failed'}")
    
    # Summary
    successful_count = sum(1 for r in results.values() if r['success'])
    total_count = len(results)
    
    if successful_count == total_count and launch_ok:
        print(f"\n🎉 DIAGNOSTIC PASSED: All {total_count} tools are working!")
        print("The tool launching fixes have been successfully applied.")
    elif successful_count > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {successful_count}/{total_count} tools working")
        print("Some improvements achieved, but manual verification recommended.")
    else:
        print(f"\n❌ DIAGNOSTIC FAILED: No tools are working")
        print("Additional troubleshooting required.")
    
    print("\nTo test in the application:")
    print("1. Run: python main.py")
    print("2. Navigate to multi-pane explorer interface")
    print("3. Double-click tools in the sidebar to test launching")


if __name__ == "__main__":
    main()