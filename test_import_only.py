#!/usr/bin/env python3
"""
Test script to verify tool imports work without GUI initialization
"""

import os
import sys

# Add path for imports
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_module_imports():
    """Test that our four problem tool modules can be imported."""
    tools_to_test = [
        ('File Checksum', 'src.tools.analysis.check_sum'),
        ('Empty Folders', 'src.tools.analysis.empty_folders'),
        ('Duplicate Finder', 'src.tools.analysis.find_duplicate_files'),
        ('Size Analyzer', 'src.tools.analysis.size_analyzer')
    ]
    
    results = {}
    
    for tool_name, module_path in tools_to_test:
        try:
            print(f"Testing import of {tool_name}...")
            
            # Try to import the module
            module = __import__(module_path, fromlist=[''])
            
            # Check for expected classes
            expected_classes = {
                'check_sum': 'ChecksumGUI',
                'empty_folders': 'EmptyFoldersGUI', 
                'find_duplicate_files': 'DuplicateFinderApp',
                'size_analyzer': 'SizeAnalyzerGUI'
            }
            
            module_name = module_path.split('.')[-1]
            if module_name in expected_classes:
                class_name = expected_classes[module_name]
                if hasattr(module, class_name):
                    tool_class = getattr(module, class_name)
                    print(f"  ✅ Found class {class_name}")
                    print(f"  ℹ️  Class type: {type(tool_class)}")
                    
                    # Check constructor signature
                    import inspect
                    try:
                        sig = inspect.signature(tool_class.__init__)
                        params = list(sig.parameters.keys())
                        print(f"  ℹ️  Constructor params: {params}")
                        
                        # Check if parent parameter exists
                        if 'parent' in params:
                            print(f"  ✅ Supports parent parameter")
                        else:
                            print(f"  ⚠️  No parent parameter")
                            
                        results[tool_name] = "SUCCESS - Import OK"
                    except Exception as e:
                        print(f"  ⚠️  Could not inspect constructor: {e}")
                        results[tool_name] = f"PARTIAL - Import OK, inspection failed: {e}"
                else:
                    print(f"  ❌ Class {class_name} not found in module")
                    results[tool_name] = f"FAILED - Class {class_name} missing"
            else:
                print(f"  ⚠️  Unknown module {module_name}")
                results[tool_name] = "PARTIAL - Module imported but unknown structure"
            
        except Exception as e:
            print(f"❌ {tool_name}: Import failed with error: {e}")
            print(f"  Error type: {type(e).__name__}")
            results[tool_name] = f"FAILED: {e}"
    
    return results

def test_safe_standard_window():
    """Test that SafeStandardWindow can be imported."""
    print("\\n" + "="*60)
    print("Testing SafeStandardWindow Import")
    print("="*60)
    
    try:
        from src.gui.safe_standard_window import SafeStandardWindow
        print("✅ SafeStandardWindow imported successfully")
        
        # Check constructor signature
        import inspect
        sig = inspect.signature(SafeStandardWindow.__init__)
        params = list(sig.parameters.keys())
        print(f"ℹ️  Constructor params: {params}")
        
        return True
    except Exception as e:
        print(f"❌ SafeStandardWindow import failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Import-Only Test - Multi-Pane Explorer Integration")
    print("="*60)
    
    # Test basic imports
    results = test_module_imports()
    
    # Test SafeStandardWindow
    safe_window_success = test_safe_standard_window()
    
    # Summary
    print("\\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = sum(1 for result in results.values() if result.startswith("SUCCESS"))
    total_count = len(results)
    
    print(f"Module Import Tests: {success_count}/{total_count} successful")
    
    for tool_name, result in results.items():
        status = "✅" if result.startswith("SUCCESS") else "❌" if result.startswith("FAILED") else "⚠️"
        print(f"  {status} {tool_name}: {result}")
    
    print(f"\\nSafeStandardWindow Test: {'✅ SUCCESS' if safe_window_success else '❌ FAILED'}")
    
    if success_count == total_count and safe_window_success:
        print("\\n🎉 ALL IMPORTS SUCCESSFUL! Ready for integration testing.")
        sys.exit(0)
    else:
        print("\\n⚠️  Some imports failed. Check dependencies and paths.")
        sys.exit(1)