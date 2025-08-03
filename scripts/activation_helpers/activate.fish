#!/usr/bin/env fish
# Fish shell activation script for Python virtual environment
# This script activates the virtual environment and sets up the Fish shell environment

# Get the directory where this script is located
set -l script_dir (dirname (status --current-filename))
set -l project_root (dirname (dirname $script_dir))
set -l venv_path "$project_root/venv"

# Check if virtual environment exists
if not test -d "$venv_path"
    echo "❌ Virtual environment not found at: $venv_path"
    echo "Please run the setup script first: python scripts/setup_venv.py"
    exit 1
end

# Check if virtual environment is already active
if set -q VIRTUAL_ENV
    echo "⚠️  A virtual environment is already active: $VIRTUAL_ENV"
    echo "Deactivating current environment first..."
    deactivate
end

# Set virtual environment variables
set -gx VIRTUAL_ENV "$venv_path"
set -gx VIRTUAL_ENV_PROMPT "(venv) "

# Add virtual environment bin directory to PATH
set -gx PATH "$venv_path/bin" $PATH

# Set up Python path
set -gx PYTHONHOME ""

# Create deactivate function
function deactivate -d "Exit the virtual environment"
    # Reset PATH
    if set -q _OLD_VIRTUAL_PATH
        set -gx PATH $_OLD_VIRTUAL_PATH
        set -e _OLD_VIRTUAL_PATH
    end
    
    # Reset PYTHONHOME
    if set -q _OLD_VIRTUAL_PYTHONHOME
        set -gx PYTHONHOME $_OLD_VIRTUAL_PYTHONHOME
        set -e _OLD_VIRTUAL_PYTHONHOME
    end
    
    # Reset prompt
    if set -q _OLD_VIRTUAL_PROMPT
        functions -e fish_prompt
        set -gx fish_prompt $_OLD_VIRTUAL_PROMPT
        functions -c _old_fish_prompt fish_prompt
        functions -e _old_fish_prompt
        set -e _OLD_VIRTUAL_PROMPT
    end
    
    # Clean up environment variables
    set -e VIRTUAL_ENV
    set -e VIRTUAL_ENV_PROMPT
    
    # Remove deactivate function
    functions -e deactivate
    
    echo "🔄 Virtual environment deactivated"
end

# Save current PATH
set -gx _OLD_VIRTUAL_PATH $PATH

# Save current PYTHONHOME
if set -q PYTHONHOME
    set -gx _OLD_VIRTUAL_PYTHONHOME $PYTHONHOME
end

# Modify fish prompt to show virtual environment
if functions -q fish_prompt
    # Save current prompt function
    functions -c fish_prompt _old_fish_prompt
    set -gx _OLD_VIRTUAL_PROMPT "$fish_prompt"
    
    function fish_prompt
        # Display virtual environment name
        if set -q VIRTUAL_ENV_PROMPT
            printf '%s%s' $VIRTUAL_ENV_PROMPT (_old_fish_prompt)
        else
            _old_fish_prompt
        end
    end
else
    # Create a simple prompt if none exists
    function fish_prompt
        if set -q VIRTUAL_ENV_PROMPT
            printf '%s%s@%s %s%s$ ' $VIRTUAL_ENV_PROMPT (whoami) (hostname) (set_color $fish_color_cwd) (prompt_pwd) (set_color normal)
        else
            printf '%s@%s %s%s$ ' (whoami) (hostname) (set_color $fish_color_cwd) (prompt_pwd) (set_color normal)
        end
    end
end

# Display activation message
echo "✅ Virtual environment activated!"
echo "🐍 Python: $venv_path/bin/python"
echo "📦 Pip: $venv_path/bin/pip"
echo "💡 To deactivate, run: deactivate"

# Verify activation
if test -x "$venv_path/bin/python"
    set python_version (eval "$venv_path/bin/python --version 2>&1")
    echo "🔍 Python version: $python_version"
else
    echo "⚠️  Warning: Python executable not found in virtual environment"
end