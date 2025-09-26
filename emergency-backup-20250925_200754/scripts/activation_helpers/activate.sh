#!/bin/bash
# Unix Shell Script for Virtual Environment Activation
# ===================================================

echo ""
echo "🐍 Activating Python Virtual Environment..."
echo ""

# Get script directory and construct venv path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
VENV_PATH="$PROJECT_ROOT/venv"
ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"

# Check if virtual environment exists
if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python scripts/setup_venv.py"
    echo ""
    read -p "Press Enter to continue..."
    exit 1
fi

# Check if activate script is executable
if [ ! -x "$ACTIVATE_SCRIPT" ]; then
    echo "⚠️  Making activate script executable..."
    chmod +x "$ACTIVATE_SCRIPT"
fi

# Activate virtual environment
source "$ACTIVATE_SCRIPT"

# Check if activation was successful
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment!"
    echo ""
    read -p "Press Enter to continue..."
    exit 1
fi

echo "✅ Virtual environment activated successfully!"
echo ""
echo "📍 Environment: $VIRTUAL_ENV"
echo "🐍 Python: $VIRTUAL_ENV/bin/python"
echo "📦 Pip: $VIRTUAL_ENV/bin/pip"
echo ""
echo "💡 To deactivate, run: deactivate"
echo "💡 To verify environment, run: python scripts/verify_environment.py"
echo ""

# Check Python version
PYTHON_VERSION=$("$VIRTUAL_ENV/bin/python" --version 2>&1)
echo "🔍 Python Version: $PYTHON_VERSION"

# Check pip version
PIP_VERSION=$("$VIRTUAL_ENV/bin/pip" --version 2>&1)
echo "🔍 Pip Version: $PIP_VERSION"
echo ""

# Optional: Show installed packages count
PACKAGE_COUNT=$("$VIRTUAL_ENV/bin/pip" list --format=freeze 2>/dev/null | wc -l)
echo "📦 Installed packages: $PACKAGE_COUNT"
echo ""