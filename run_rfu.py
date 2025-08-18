#!/usr/bin/env python3
"""
RFU Application Launcher

This script properly configures the Python path and launches the RFU application.
"""

import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent
src_dir = project_root / "src"

# Add src directory to Python path
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now import and run the main application
if __name__ == "__main__":
    try:
        # Import the main function from rfu.main
        from rfu.main import main
        
        # Run the application
        exit_code = main()
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"Import error: {e}")
        print(f"Python path: {sys.path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Src directory exists: {src_dir.exists()}")
        print(f"RFU module exists: {(src_dir / 'rfu').exists()}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)