#!/usr/bin/env python3
"""
RFU Hub Launcher - Runs the consolidated hub with proper path setup

This launcher ensures that the hub can find all its dependencies
regardless of where it's run from.
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the RFU Hub with proper path setup."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Add the src directory to Python path
    src_dir = script_dir / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
    
    # Add the current directory to Python path for relative imports
    sys.path.insert(0, str(script_dir))
    
    try:
        # Import and run the hub
        from src.hub import main as hub_main
        hub_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Trying alternative import path...")
        try:
            # Try importing from the rfu directory directly
            sys.path.insert(0, str(script_dir / "src" / "rfu"))
            import hub
            hub.main()
        except ImportError as e2:
            print(f"Alternative import failed: {e2}")
            print("\nAvailable options:")
            print("1. Run from workspace root: python launch_hub.py")
            print("2. Run main application: python main.py")
            print("3. Check that all dependencies are installed")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())