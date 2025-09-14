#!/usr/bin/env python3
"""Test MultiPaneFileExplorer import and initialization."""

import os
import sys
from pathlib import Path

# Add the same paths as main.py
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_multi_pane_import():
    """Test importing and creating MultiPaneFileExplorer."""
    print("Testing MultiPaneFileExplorer import...")
    
    try:
        from src.rfu.file_explorer.multi_pane_explorer import \
            MultiPaneFileExplorer
        print("✅ Import successful!")
        
        print("Testing MultiPaneFileExplorer creation...")
        explorer = MultiPaneFileExplorer()
        print("✅ Creation successful!")
        
        print("MultiPaneFileExplorer is working correctly")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Creation Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_multi_pane_import()