# Cross-platform virtual environment activation
# This script detects the platform and runs the appropriate activation script

import os
import platform
import subprocess


def get_script_dir():
    """Get the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))


def activate_environment():
    """Activate the virtual environment based on the current platform."""
    script_dir = get_script_dir()
    system = platform.system().lower()
    
    print("Activating Richard's File Utilities Python Environment...")
    print(f"Platform detected: {platform.system()}")
    
    if system == "windows":
        # Try PowerShell first, then fall back to batch
        ps_script = os.path.join(script_dir, "activate_env.ps1")
        bat_script = os.path.join(script_dir, "activate_env.bat")
        
        if os.path.exists(ps_script):
            print("Using PowerShell activation script...")
            subprocess.run([
                "powershell", "-ExecutionPolicy", "Bypass", "-File", ps_script
            ], check=False)
        elif os.path.exists(bat_script):
            print("Using batch activation script...")
            subprocess.run([bat_script], check=False)
        else:
            print("No Windows activation script found. "
                  "Using direct activation...")
            activate_direct(script_dir, "Scripts")
    
    elif system in ["linux", "darwin"]:  # Linux or macOS
        sh_script = os.path.join(script_dir, "activate_env.sh")
        
        if os.path.exists(sh_script):
            print("Using shell activation script...")
            subprocess.run(["bash", sh_script], check=False)
        else:
            print("No Unix activation script found. "
                  "Using direct activation...")
            activate_direct(script_dir, "bin")
    
    else:
        print(f"Unsupported platform: {system}")
        print("Attempting direct activation...")
        # Try both Windows and Unix paths
        for bin_dir in ["Scripts", "bin"]:
            if activate_direct(script_dir, bin_dir):
                break


def activate_direct(script_dir, bin_dir):
    """Directly activate the virtual environment."""
    venv_dir = os.path.join(script_dir, "venv")
    python_exe = os.path.join(venv_dir, bin_dir, "python")
    
    if os.path.exists(python_exe):
        print(f"Environment found at: {venv_dir}")
        print(f"Python executable: {python_exe}")
        print("To run the main application: python main.py")
        print("To run tests: python -m pytest")
        return True
    return False


if __name__ == "__main__":
    activate_environment()