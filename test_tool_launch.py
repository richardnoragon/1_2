#!/usr/bin/env python3
"""
Test launching a discovered tool
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Test launching a simple tool (File Checksum)
    print("Testing Tool Launch...")
    print("=" * 30)
    
    tool_data = {
        'name': 'check_sum',
        'display_name': 'File Checksum',
        'module_path': 'src.tools.analysis.check_sum',
        'class_name': 'ChecksumGUI',
        'category': 'Analysis'
    }
    
    print(f"Attempting to launch: {tool_data['display_name']}")
    print(f"Module: {tool_data['module_path']}")
    print(f"Class: {tool_data['class_name']}")
    
    # Try to import and launch
    try:
        module = __import__(tool_data['module_path'], fromlist=[tool_data['class_name']])
        tool_class = getattr(module, tool_data['class_name'])
        print(f"✓ Successfully imported {tool_data['class_name']}")
        
        # Create instance
        tool_instance = tool_class()
        print(f"✓ Successfully created instance of {tool_data['class_name']}")
        
        print(f"✓ Tool '{tool_data['display_name']}' can be launched successfully!")
        
        # Check if it has a show method
        if hasattr(tool_instance, 'show'):
            print("✓ Tool has 'show' method")
        elif hasattr(tool_instance, 'exec_'):
            print("✓ Tool has 'exec_' method") 
        else:
            print("? Tool launch method unknown")
            
    except ImportError as e:
        print(f"✗ Import failed: {e}")
    except AttributeError as e:
        print(f"✗ Class not found: {e}")
    except Exception as e:
        print(f"✗ Launch failed: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"✗ Test failed: {e}")
    import traceback
    traceback.print_exc()