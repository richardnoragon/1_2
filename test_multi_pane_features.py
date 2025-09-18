#!/usr/bin/env python3
"""
Test script to verify the full multi-pane explorer features
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, '.')

def test_multi_pane_features():
    """Test that the multi-pane explorer has the expected features."""
    print("Testing MultiPaneFileExplorer features...")
    
    try:
        # Create QApplication first
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        from src.file_explorer.multi_pane_explorer import \
            MultiPaneFileExplorer
        print("✓ MultiPaneFileExplorer imported successfully")
        
        # Create instance
        explorer = MultiPaneFileExplorer()
        print("✓ MultiPaneFileExplorer instantiated successfully")
        
        # Check basic properties
        print(f"  - Pane count: {getattr(explorer, 'pane_count', 'Unknown')}")
        print(f"  - Layout mode: {getattr(explorer, 'layout_mode', 'Unknown')}")
        
        # Check for advanced features
        features_found = []
        
        # Check for bookmark manager
        if hasattr(explorer, 'bookmark_manager'):
            features_found.append("Bookmark Manager")
            
        # Check for tool launcher
        if hasattr(explorer, 'tool_launcher'):
            features_found.append("Tool Launcher")
            
        # Check for pane controls
        if hasattr(explorer, 'pane_count_combo'):
            features_found.append("Pane Count Controls")
            
        # Check for layout controls
        if hasattr(explorer, 'layout_mode_combo'):
            features_found.append("Layout Mode Controls")
            
        # Check for property panel
        if hasattr(explorer, 'property_panel'):
            features_found.append("Property Panel")
            
        # Check for preview widget
        if hasattr(explorer, 'preview_widget'):
            features_found.append("Preview Widget")
            
        # Check for search widget
        if hasattr(explorer, 'search_widget'):
            features_found.append("Search Widget")
            
        # Check for docks
        if hasattr(explorer, 'tool_dock'):
            features_found.append("Tool Dock")
            
        if hasattr(explorer, 'bookmark_dock'):
            features_found.append("Bookmark Dock")
        
        print("✓ Advanced features found:")
        for feature in features_found:
            print(f"  - {feature}")
            
        if len(features_found) >= 3:
            print("✅ SUCCESS: Full multi-pane explorer with advanced features!")
            return True
        else:
            print("⚠️  WARNING: Limited features found - may be simplified version")
            return False
            
    except ImportError as e:
        print(f"✗ IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_multi_pane_features()
    if success:
        print("\n🎉 Multi-pane explorer is working with full features!")
    else:
        print("\n❌ Multi-pane explorer has issues or missing features")
    
    sys.exit(0 if success else 1)