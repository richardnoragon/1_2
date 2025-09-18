#!/usr/bin/env python3
"""
Simple launcher for RFU from the rfu directory
"""
import sys
import os
from pathlib import Path

# Get the workspace root (two levels up from this script)
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

# Now we can import and run the main application
if __name__ == "__main__":
    try:
        # Import the main function from the workspace root main.py
        sys.path.insert(0, str(workspace_root))
        
        # Read and execute the main.py from workspace root
        main_py_path = workspace_root / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r', encoding='utf-8') as f:
                main_code = f.read()
            
            # Change working directory to workspace root
            original_cwd = os.getcwd()
            os.chdir(workspace_root)
            
            try:
                # Execute the main.py code
                exec(main_code)
            finally:
                # Restore original working directory
                os.chdir(original_cwd)
        else:
            print("Error: main.py not found in workspace root")
            print(f"Looking for: {main_py_path}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error launching application: {e}")
        print("\nAlternative: Run from workspace root:")
        print("cd c:\\Users\\HP1\\1_2\\1_2")
        print("python main.py")
        sys.exit(1)