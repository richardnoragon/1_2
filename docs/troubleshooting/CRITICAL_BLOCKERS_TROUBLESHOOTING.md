# CRITICAL BLOCKERS TROUBLESHOOTING GUIDE

**Document:** Critical Test Execution Blockers Troubleshooting and Escalation Procedures  
**Generated:** September 2, 2025  
**Project:** Richard's File Utilities - Unit Testing Infrastructure  
**Scope:** Network Complex Module Imports & Cross-Platform Dependencies  

---

## EMERGENCY CONTACT INFORMATION

### Immediate Escalation Contacts

| Issue Type | Primary Contact | Secondary Contact | Response Time |
|------------|----------------|-------------------|---------------|
| **Critical Import Failures** | Technical Lead | Senior Developer | < 2 hours |
| **Infrastructure/CI-CD Issues** | DevOps Manager | Platform Engineer | < 4 hours |
| **Security Test Failures** | Security Manager | Security Engineer | < 1 hour |
| **Project Timeline Impact** | Project Manager | Development Manager | < 6 hours |

### Emergency Procedures
- **Severity 1 (Critical):** Call primary contact immediately + send email
- **Severity 2 (High):** Email primary contact + secondary contact  
- **Severity 3 (Medium):** Create ticket + email primary contact
- **Severity 4 (Low):** Create ticket for next business day

---

## NETWORK COMPLEX MODULE IMPORT RESOLUTION

### Problem: ModuleNotFoundError: No module named 'core.config_manager'

#### Symptoms
```python
ModuleNotFoundError: No module named 'core.config_manager'
ImportError: cannot import name 'ConfigManager' from 'core.config_manager'
AttributeError: module 'core' has no attribute 'config_manager'
```

#### Root Cause Analysis
- Python path resolution failure: core.config_manager not in sys.path
- Missing core directory structure with proper __init__.py files  
- Architecture mismatch: config_manager.py exists in root but not in core/
- Import hierarchy conflict in network module dependencies

#### Step-by-Step Resolution

**Step 1: Verify Directory Structure**
```powershell
# Windows
Test-Path "c:\Users\richardi\1_2\core"
Test-Path "c:\Users\richardi\1_2\core\__init__.py"  
Test-Path "c:\Users\richardi\1_2\core\config_manager.py"

# If missing, create structure:
New-Item -Path "c:\Users\richardi\1_2\core" -ItemType Directory -Force
New-Item -Path "c:\Users\richardi\1_2\core\__init__.py" -ItemType File -Force
Copy-Item "c:\Users\richardi\1_2\config_manager.py" "c:\Users\richardi\1_2\core\config_manager.py"
```

**Step 2: Configure Python Path**
```powershell
# Windows - Temporary
$env:PYTHONPATH = "c:\Users\richardi\1_2"

# Windows - Permanent
[Environment]::SetEnvironmentVariable("PYTHONPATH", "c:\Users\richardi\1_2", "User")

# Verify path configuration
python -c "import sys; print('\n'.join(sys.path))"
```

**Step 3: Test Import Resolution**
```python
# Test script: test_core_import.py
import sys
import os

# Add project root to path if not present
project_root = r"c:\Users\richardi\1_2"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.config_manager import ConfigManager
    config = ConfigManager()
    print("✅ SUCCESS: Core config_manager import and instantiation successful")
    print(f"Config sections: {list(config.get_all_settings().keys())}")
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print(f"Current sys.path: {sys.path}")
except Exception as e:
    print(f"❌ RUNTIME ERROR: {e}")
```

**Step 4: Validate Network Module Access**
```python
# Test network module integration
try:
    from src.utilities.network.network_connectivity_complex.integration.rfu_integration import RFUIntegration
    print("✅ SUCCESS: Network RFU integration import successful")
except ImportError as e:
    print(f"❌ NETWORK IMPORT ERROR: {e}")

try:
    from src.utilities.network.network_connectivity_complex.config.config_profiles import ConfigProfiles  
    print("✅ SUCCESS: Network config profiles import successful")
except ImportError as e:
    print(f"❌ CONFIG PROFILES ERROR: {e}")
```

#### Advanced Troubleshooting

**Issue:** Import works in some contexts but not others
**Solution:** Check for relative import conflicts
```python
# In network modules, ensure proper import syntax:
# CORRECT:
from core.config_manager import ConfigManager

# INCORRECT:
from ...core.config_manager import ConfigManager  # Relative import issues
import core.config_manager  # May cause circular import
```

**Issue:** ConfigManager instantiation fails
**Solution:** Verify config directory permissions and file access
```python
import os
from pathlib import Path

config_dir = Path('config')
print(f"Config dir exists: {config_dir.exists()}")
print(f"Config dir writable: {os.access(config_dir, os.W_OK) if config_dir.exists() else 'Directory missing'}")

# Create if missing:
config_dir.mkdir(exist_ok=True)
```

**Issue:** Network modules still cannot access configuration
**Solution:** Implement dependency injection pattern
```python
# In network modules, use dependency injection:
class NetworkComponent:
    def __init__(self, config_manager=None):
        if config_manager is None:
            from core.config_manager import ConfigManager
            config_manager = ConfigManager()
        self.config = config_manager
```

### Emergency Rollback Procedures

**If core directory creation breaks existing functionality:**
1. Backup current core directory: `Copy-Item "core" "core_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Recurse`
2. Remove problematic core directory: `Remove-Item "core" -Recurse -Force`
3. Restore original config_manager.py: `Copy-Item "config_manager_backup.py" "config_manager.py"`
4. Test existing functionality: `pytest tests/unit/test_basic_functionality.py`

---

## CROSS-PLATFORM DEPENDENCIES RESOLUTION

### Problem: Platform-Specific Test Failures

#### Common Symptoms by Platform

**macOS Issues:**
```
ImportError: No module named '_tkinter'
FileNotFoundError: [Errno 2] No such file or directory: 'mdfind'
AttributeError: 'MacOSBrowserDetector' object has no attribute 'system_profiler'
```

**Linux Issues:**
```
ModuleNotFoundError: No module named 'tkinter'
subprocess.CalledProcessError: Command 'locate' returned non-zero exit status 1
PermissionError: [Errno 13] Permission denied: '/etc/passwd'
```

**Windows Specific:**
```
ImportError: DLL load failed while importing _tkinter: %1 is not a valid Win32 application
WinError 5: Access is denied (Registry access issues)
```

#### Platform-Specific Resolution Procedures

### macOS Resolution

**Step 1: Install Platform Dependencies**
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python GUI support
brew install python-tk

# Install browser detection utilities
brew install findutils coreutils

# Install Python packages
pip3 install matplotlib numpy>=1.21.0 pyqt5 pytest pytest-qt
```

**Step 2: Configure Environment**
```bash
# Set Python path
export PYTHONPATH="/path/to/1_2"

# Add to shell profile for persistence
echo 'export PYTHONPATH="/path/to/1_2"' >> ~/.zshrc
source ~/.zshrc

# Verify GUI backend
python3 -c "import tkinter; print('✅ tkinter available')"
python3 -c "import matplotlib; matplotlib.use('TkAgg'); import matplotlib.pyplot as plt; print('✅ matplotlib GUI ready')"
```

**Step 3: Test Browser Detection**
```bash
# Test macOS browser detection utilities
which mdfind && echo "✅ mdfind available" || echo "❌ mdfind missing"
system_profiler SPApplicationsDataType | grep -i browser || echo "Browser detection may fail"

# Test Python browser detection
python3 -c "
from src.utilities.privacy.privacy_tools.core.browser_detector import BrowserDetector
detector = BrowserDetector()
browsers = detector.detect_browsers()
print(f'✅ Detected {len(browsers)} browsers')
"
```

### Linux Resolution

**Step 1: Install Platform Dependencies**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-tk python3-dev python3-pip
sudo apt-get install locate mlocate findutils

# CentOS/RHEL
sudo yum install tkinter python3-devel python3-pip
sudo yum install mlocate findutils

# Update locate database
sudo updatedb

# Install Python packages
pip3 install matplotlib numpy>=1.21.0 pyqt5 pytest pytest-qt
```

**Step 2: Configure Environment and Permissions**
```bash
# Set Python path
export PYTHONPATH="/path/to/1_2"

# Add to shell profile
echo 'export PYTHONPATH="/path/to/1_2"' >> ~/.bashrc
source ~/.bashrc

# Configure display for GUI testing (if needed)
export DISPLAY=:0.0

# Verify permissions for system access
ls -la /etc/passwd && echo "✅ System file access available" || echo "❌ Permission issues"
```

**Step 3: Test Cross-Platform Functionality**
```bash
# Test GUI components
python3 -c "
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for headless testing
import matplotlib.pyplot as plt
print('✅ matplotlib non-GUI backend ready')
"

# Test file operations
python3 -c "
import tempfile
import os
with tempfile.NamedTemporaryFile(delete=False) as f:
    f.write(b'test')
    temp_path = f.name
os.unlink(temp_path)
print('✅ File operations working')
"
```

### Windows Resolution

**Step 1: Install Dependencies with PowerShell**
```powershell
# Install Python packages
pip install matplotlib numpy>=1.21.0 pyqt5 pytest pytest-qt pytest-mock

# Verify installation
python -c "import matplotlib; import numpy; import PyQt5; print('✅ All packages installed')"

# Test GUI backend
python -c "
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
print('✅ Qt5 GUI backend ready')
"
```

**Step 2: Configure Registry Access (if needed)**
```powershell
# Test registry access for browser detection
python -c "
import winreg
try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'):
        print('✅ Registry access working')
except Exception as e:
    print(f'❌ Registry access failed: {e}')
"
```

### Cross-Platform Testing Validation

**Comprehensive Cross-Platform Test Script:**
```python
# cross_platform_validation.py
import sys
import platform
import subprocess
import importlib

def test_platform_specific():
    """Test platform-specific functionality."""
    system = platform.system()
    print(f"Testing on {system} {platform.release()}")
    
    # Test GUI components
    try:
        import tkinter
        print("✅ tkinter available")
    except ImportError:
        print("❌ tkinter missing - install python-tk")
    
    # Test visualization
    try:
        import matplotlib
        import numpy
        print("✅ matplotlib and numpy available")
    except ImportError:
        print("❌ visualization packages missing")
    
    # Test PyQt5
    try:
        import PyQt5
        print("✅ PyQt5 available")
    except ImportError:
        print("❌ PyQt5 missing")
    
    # Platform-specific tests
    if system == "Darwin":  # macOS
        try:
            subprocess.run(["mdfind", "-name", "test"], capture_output=True, check=True)
            print("✅ macOS browser detection utilities available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ macOS utilities missing - install findutils")
    
    elif system == "Linux":
        try:
            subprocess.run(["locate", "--version"], capture_output=True, check=True)
            print("✅ Linux file location utilities available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Linux utilities missing - install mlocate")
    
    elif system == "Windows":
        try:
            import winreg
            print("✅ Windows registry access available")
        except ImportError:
            print("❌ Windows registry access issues")

if __name__ == "__main__":
    test_platform_specific()
```

---

## AUTOMATED RESOLUTION SCRIPTS

### Core Module Setup Script
```powershell
# setup_core_module.ps1
param(
    [string]$ProjectRoot = "c:\Users\richardi\1_2"
)

Write-Host "Setting up core module architecture..." -ForegroundColor Green

# Create core directory structure
$coreDir = Join-Path $ProjectRoot "core"
New-Item -Path $coreDir -ItemType Directory -Force
Write-Host "✅ Created core directory: $coreDir"

# Create __init__.py
$initFile = Join-Path $coreDir "__init__.py"
Set-Content -Path $initFile -Value "# Core module for Richard's File Utilities"
Write-Host "✅ Created __init__.py: $initFile"

# Copy config_manager to core
$sourceConfig = Join-Path $ProjectRoot "config_manager.py"
$targetConfig = Join-Path $coreDir "config_manager.py"
if (Test-Path $sourceConfig) {
    Copy-Item $sourceConfig $targetConfig -Force
    Write-Host "✅ Copied config_manager.py to core directory"
} else {
    Write-Host "❌ Source config_manager.py not found: $sourceConfig" -ForegroundColor Red
    exit 1
}

# Set environment variable
$env:PYTHONPATH = $ProjectRoot
[Environment]::SetEnvironmentVariable("PYTHONPATH", $ProjectRoot, "User")
Write-Host "✅ Set PYTHONPATH to: $ProjectRoot"

# Test import
try {
    $result = python -c "from core.config_manager import ConfigManager; print('SUCCESS')" 2>&1
    if ($result -match "SUCCESS") {
        Write-Host "✅ Core module import test successful" -ForegroundColor Green
    } else {
        Write-Host "❌ Core module import test failed: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Core module import test error: $_" -ForegroundColor Red
}

Write-Host "Core module setup complete!" -ForegroundColor Green
```

### Cross-Platform Dependencies Installation Script
```bash
#!/bin/bash
# setup_cross_platform_deps.sh

echo "Setting up cross-platform dependencies..."

# Detect platform
case "$(uname -s)" in
    Darwin)
        echo "📱 macOS detected"
        # Install Homebrew if needed
        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install dependencies
        brew install python-tk findutils coreutils
        pip3 install matplotlib numpy pyqt5 pytest pytest-qt
        echo "✅ macOS dependencies installed"
        ;;
        
    Linux)
        echo "🐧 Linux detected"
        # Detect Linux distribution
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-tk python3-dev python3-pip locate mlocate findutils
        elif command -v yum &> /dev/null; then
            sudo yum install -y tkinter python3-devel python3-pip mlocate findutils
        fi
        
        pip3 install matplotlib numpy pyqt5 pytest pytest-qt
        sudo updatedb
        echo "✅ Linux dependencies installed"
        ;;
        
    MINGW*|CYGWIN*|MSYS*)
        echo "🪟 Windows (Git Bash) detected"
        pip install matplotlib numpy pyqt5 pytest pytest-qt
        echo "✅ Windows dependencies installed"
        ;;
        
    *)
        echo "❌ Unsupported platform: $(uname -s)"
        exit 1
        ;;
esac

# Set Python path
export PYTHONPATH="$(pwd)"
echo "✅ Set PYTHONPATH to: $(pwd)"

# Test imports
python3 -c "
import sys
try:
    import matplotlib
    import numpy  
    import PyQt5
    print('✅ All major dependencies available')
except ImportError as e:
    print(f'❌ Dependency missing: {e}')
    sys.exit(1)
"

echo "✅ Cross-platform dependencies setup complete!"
```

---

## MONITORING AND VALIDATION

### Continuous Monitoring Script
```python
# monitor_blockers.py
import subprocess
import sys
import time
from datetime import datetime

def check_core_module():
    """Check core module import status."""
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            "from core.config_manager import ConfigManager; print('OK')"
        ], capture_output=True, text=True, timeout=10)
        return result.returncode == 0 and "OK" in result.stdout
    except Exception:
        return False

def check_network_modules():
    """Check network module imports."""
    modules_to_test = [
        "src.utilities.network.network_connectivity_complex.integration.rfu_integration",
        "src.utilities.network.network_connectivity_complex.config.config_profiles",
        "src.utilities.network.network_connectivity_complex.config.config_integration"
    ]
    
    results = {}
    for module in modules_to_test:
        try:
            result = subprocess.run([
                sys.executable, "-c", f"import {module}; print('OK')"
            ], capture_output=True, text=True, timeout=10)
            results[module] = result.returncode == 0 and "OK" in result.stdout
        except Exception:
            results[module] = False
    
    return results

def check_cross_platform_deps():
    """Check cross-platform dependencies."""
    deps = ["matplotlib", "numpy", "PyQt5", "pytest"]
    results = {}
    
    for dep in deps:
        try:
            result = subprocess.run([
                sys.executable, "-c", f"import {dep}; print('OK')"
            ], capture_output=True, text=True, timeout=10)
            results[dep] = result.returncode == 0 and "OK" in result.stdout
        except Exception:
            results[dep] = False
    
    return results

def generate_status_report():
    """Generate comprehensive status report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n🔍 BLOCKER RESOLUTION STATUS REPORT - {timestamp}")
    print("=" * 60)
    
    # Core module status
    core_status = check_core_module()
    print(f"Core Module Import: {'✅ WORKING' if core_status else '❌ FAILED'}")
    
    # Network modules status  
    network_results = check_network_modules()
    print(f"\nNetwork Modules Import:")
    for module, status in network_results.items():
        short_name = module.split('.')[-1]
        print(f"  {short_name}: {'✅ WORKING' if status else '❌ FAILED'}")
    
    # Cross-platform dependencies
    deps_results = check_cross_platform_deps()
    print(f"\nCross-Platform Dependencies:")
    for dep, status in deps_results.items():
        print(f"  {dep}: {'✅ WORKING' if status else '❌ FAILED'}")
    
    # Overall status
    core_ok = core_status
    network_ok = all(network_results.values())
    deps_ok = all(deps_results.values())
    
    overall_status = "🟢 RESOLVED" if (core_ok and network_ok and deps_ok) else "🔴 BLOCKERS REMAIN"
    print(f"\nOverall Status: {overall_status}")
    
    if not (core_ok and network_ok and deps_ok):
        print("\n⚠️  ESCALATION REQUIRED - Contact Technical Lead")
    
    return core_ok and network_ok and deps_ok

if __name__ == "__main__":
    generate_status_report()
```

---

## ESCALATION MATRIX

### When to Escalate

| Situation | Severity | Contact | Timeline |
|-----------|----------|---------|----------|
| **Core module import fails after following all procedures** | Critical | Technical Lead | Immediate |
| **Network modules still cannot access config after 4 hours** | Critical | Senior Developer | < 2 hours |
| **Cross-platform dependencies fail on multiple platforms** | High | DevOps Manager | < 4 hours |
| **Security tests continue to fail after environment setup** | Critical | Security Manager | < 1 hour |
| **Timeline impact > 2 days** | High | Project Manager | < 6 hours |
| **Rollback procedures fail** | Critical | Technical Lead + DevOps Manager | Immediate |

### Escalation Communication Template

**Subject:** CRITICAL: [Brief Description] - Richard's File Utilities Testing Blockers

**Priority:** [Critical/High/Medium]

**Issue Summary:**
- Problem: [Brief description]
- Impact: [Specific impact on testing/timeline] 
- Attempted Resolution: [What was tried]
- Current Status: [Current state]

**Environment Details:**
- Platform: [Windows/macOS/Linux]
- Python Version: [Version]
- Project Path: [Path]
- Error Messages: [Exact error text]

**Immediate Needs:**
- [ ] Technical guidance
- [ ] Infrastructure support
- [ ] Timeline adjustment
- [ ] Resource allocation

**Next Steps:**
[What will be attempted next]

**Requested Response Time:** [Based on severity]

---

**Document Status:** ✅ **ACTIVE TROUBLESHOOTING GUIDE**  
**Last Updated:** September 2, 2025  
**Version:** 1.0  
**Owner:** Technical Lead + DevOps Manager  
**Review Frequency:** Weekly during active resolution  
**Distribution:** Development Team, QA Team, DevOps Team