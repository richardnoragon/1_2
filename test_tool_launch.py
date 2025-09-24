#!/usr/bin/env python3
"""
Test script to verify tool launching works from multi-pane explorer
"""

import os
import sys

# Add path for imports
project_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_tool_imports():
    """Test that our four problem tools can be imported and instantiated."""
    tools_to_test = [
        ('File Checksum', 'src.tools.analysis.check_sum', 'ChecksumGUI'),
        ('Empty Folders', 'src.tools.analysis.empty_folders', 'EmptyFoldersGUI'),
        ('Duplicate Finder', 'src.tools.analysis.find_duplicate_files', 'DuplicateFinderApp'),
        ('Size Analyzer', 'src.tools.analysis.size_analyzer', 'SizeAnalyzerGUI')
    ]
    
    results = {}
    
    for tool_name, module_path, class_name in tools_to_test:
        try:
            print(f"Testing {tool_name}...")
            
            # Try to import the module
            module = __import__(module_path, fromlist=[class_name])
            tool_class = getattr(module, class_name)
            
            # Try to instantiate with parent parameter (enhanced)
            try:
                tool_instance = tool_class(parent=None)
                print(f"  ✅ Created with parent parameter")
            except TypeError:
                # Fall back to no parameters
                tool_instance = tool_class()
                print(f"  ✅ Created with default constructor")
            
            # Test window properties
            if hasattr(tool_instance, 'windowTitle'):
                title = tool_instance.windowTitle()
                print(f"  ℹ️  Window title: {title}")
            
            if hasattr(tool_instance, 'isVisible'):
                print(f"  ℹ️  Window visible: {tool_instance.isVisible()}")
            
            print(f"✅ {tool_name}: Import and instantiation successful")
            results[tool_name] = "SUCCESS"
            
            # Clean up
            if hasattr(tool_instance, 'close'):
                tool_instance.close()
            del tool_instance
            
        except Exception as e:
            print(f"❌ {tool_name}: Failed with error: {e}")
            print(f"  Error type: {type(e).__name__}")
            results[tool_name] = f"FAILED: {e}"
    
    return results

def test_enhanced_import_strategy():
    """Test the enhanced import strategy used in multi-pane explorer."""
    print("\\n" + "="*60)
    print("Testing Enhanced Import Strategy with Parent Widget")
    print("="*60)
    
    def _import_with_importlib(module_path, class_name):
        """Test importlib strategy."""
        try:
            import importlib
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                return module
        except ImportError:
            pass
        return None
    
    def _create_tool_instance_enhanced(tool_class, tool_name):
        """Test enhanced tool instantiation with multiple strategies."""
        creation_strategies = [
            # Strategy 1: Try with parent parameter
            lambda: tool_class(parent=None),
            # Strategy 2: Try with default constructor
            lambda: tool_class(),
            # Strategy 3: Try with window type parameter
            lambda: tool_class(window_type="utility") if _has_param(tool_class, 'window_type') else None,
            # Strategy 4: Try with minimal parameters
            lambda: tool_class(title=f"{tool_name} - Test") if _has_param(tool_class, 'title') else None
        ]
        
        for i, strategy in enumerate(creation_strategies, 1):
            try:
                print(f"    Trying creation strategy {i}...")
                tool_instance = strategy()
                if tool_instance:
                    print(f"    ✅ Strategy {i} successful!")
                    return tool_instance
            except Exception as e:
                print(f"    ❌ Strategy {i} failed: {e}")
                continue
        return None
    
    def _has_param(tool_class, param_name):
        """Check if constructor has specific parameter."""
        try:
            import inspect
            sig = inspect.signature(tool_class.__init__)
            return param_name in sig.parameters
        except Exception:
            return False
    
    # Test all four problem tools
    tools_to_test = [
        ("File Checksum", "src.tools.analysis.check_sum", "ChecksumGUI"),
        ("Empty Folders", "src.tools.analysis.empty_folders", "EmptyFoldersGUI"),
        ("Duplicate Finder", "src.tools.analysis.find_duplicate_files", "DuplicateFinderApp"),
        ("Size Analyzer", "src.tools.analysis.size_analyzer", "SizeAnalyzerGUI")
    ]
    
    success_count = 0
    
    for tool_name, module_path, class_name in tools_to_test:
        print(f"\\nTesting {tool_name} with enhanced strategy...")
        
        import_strategies = [
            lambda: __import__(module_path, fromlist=[class_name]),
            lambda: __import__(module_path.replace('src.', ''), fromlist=[class_name]),
            lambda: _import_with_importlib(module_path, class_name)
        ]
        
        tool_instance = None
        last_error = None
        
        for i, strategy in enumerate(import_strategies, 1):
            try:
                print(f"  Trying import strategy {i}...")
                module = strategy()
                if module:
                    tool_class = getattr(module, class_name)
                    tool_instance = _create_tool_instance_enhanced(tool_class, tool_name)
                    if tool_instance:
                        print(f"  ✅ Import strategy {i} successful!")
                        break
            except Exception as e:
                last_error = e
                print(f"  ❌ Import strategy {i} failed: {e}")
                continue
        
        if tool_instance:
            print(f"✅ {tool_name}: Enhanced strategy successful!")
            success_count += 1
            if hasattr(tool_instance, 'close'):
                tool_instance.close()
        else:
            print(f"❌ {tool_name}: All strategies failed. Last error: {last_error}")
    
    return success_count == len(tools_to_test)

if __name__ == "__main__":
    print("="*60)
    print("Tool Launch Test - Multi-Pane Explorer Integration")
    print("="*60)
    
    # Test basic imports
    results = test_tool_imports()
    
    # Test enhanced strategy
    enhanced_success = test_enhanced_import_strategy()
    
    # Summary
    print("\\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = sum(1 for result in results.values() if result == "SUCCESS")
    total_count = len(results)
    
    print(f"Basic Import Tests: {success_count}/{total_count} successful")
    
    for tool_name, result in results.items():
        status = "✅" if result == "SUCCESS" else "❌"
        print(f"  {status} {tool_name}: {result}")
    
    print(f"\\nEnhanced Strategy Test: {'✅ SUCCESS' if enhanced_success else '❌ FAILED'}")
    
    if success_count == total_count and enhanced_success:
        print("\\n🎉 ALL TESTS PASSED! Tools should work from multi-pane explorer.")
        sys.exit(0)
    else:
        print("\\n⚠️  Some tests failed. Multi-pane explorer may still have issues.")
        sys.exit(1)