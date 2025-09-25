#!/bin/bash
# Richard's File Utilities - Virtual Environment Setup
# Activate the virtual environment for this project (Unix/Linux/macOS)

echo "Activating Richard's File Utilities Python Environment..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

echo ""
echo "Environment activated! Python executable: $SCRIPT_DIR/venv/bin/python"
echo "To run the main application: python main.py"
echo "To run tests: python -m pytest"
echo "To deactivate: deactivate"
echo ""