# Cross-Platform Test Environment Setup Instructions

**Project:** Richard's File Utilities (RFU)  
**Purpose:** Reproducible test environment setup for cross-platform testing  
**Platforms:** Windows 10/11, macOS 10.15+, Linux  
**Created:** September 5, 2025  

---

## Executive Summary

This document provides step-by-step instructions for setting up reproducible test environments on all supported platforms. Following these instructions ensures consistent testing conditions and reliable cross-platform test results.

### Setup Overview

| Platform | Setup Time | Prerequisites | Special Requirements |
|----------|------------|---------------|---------------------|
| **Windows** | 30-45 minutes | Admin access | Long path support, network shares |
| **macOS** | 20-30 minutes | Admin access | Full Disk Access, case-sensitive volume |
| **Linux** | 15-25 minutes | sudo access | Multiple filesystems, mount points |

---

## 1. Windows Test Environment Setup

### 1.1 Prerequisites and System Requirements

**System Requirements:**

- Windows 10 version 1607+ or Windows 11
- 8GB RAM minimum, 16GB recommended
- 50GB free disk space for testing
- Administrator account access
- Internet connection for downloads

**Required Software:**

```powershell
# Check Windows version (must be 1607+ for long path support)
winver

# Check PowerShell version (5.1+ required)
$PSVersionTable.PSVersion

# Verify .NET Framework 4.7.2+ installed
Get-ItemProperty "HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" -Name Release
```

### 1.2 Python Environment Setup

**Step 1: Install Python**

```powershell
# Download and install Python 3.11 (recommended) from python.org
# Ensure "Add to PATH" is checked during installation

# Verify installation
python --version
pip --version

# Install additional Python versions for testing (optional)
# Download Python 3.9, 3.10, 3.12 from python.org
```

**Step 2: Create Virtual Environment**

```powershell
# Navigate to RFU project directory
cd C:\path\to\rfu

# Create virtual environment
python -m venv rfu_test_env

# Activate virtual environment
rfu_test_env\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r tests\pre_beta\requirements-test.txt

# Verify PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### 1.3 Windows-Specific Configuration

**Step 3: Enable Long Path Support**

```powershell
# Method 1: Group Policy (requires Windows Pro/Enterprise)
# Run as Administrator:
gpedit.msc
# Navigate: Computer Configuration → Administrative Templates → System → Filesystem
# Enable: "Enable Win32 long paths"

# Method 2: Registry Edit (works on all Windows editions)
# Run as Administrator:
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1

# Verify long path support
python tests\pre_beta\scripts\verify_windows_long_path_support.py
```

**Step 4: Configure Test Directories**

```powershell
# Create test directory structure
mkdir C:\RFUTests
mkdir C:\RFUTests\LongPaths
mkdir C:\RFUTests\ReservedNames
mkdir C:\RFUTests\UNCTests
mkdir C:\RFUTests\CaseTests

# Create long path test structure
# This will create paths exceeding 260 characters
python tests\pre_beta\scripts\create_windows_long_path_structure.py

# Set up local network share for UNC testing
net share RFUTestShare=C:\RFUTests\UNCTests /grant:everyone,full

# Verify UNC access
dir \\localhost\RFUTestShare
```

**Step 5: Configure Windows Defender (Optional)**

```powershell
# Add test directories to Windows Defender exclusions (for performance)
# Run as Administrator:
Add-MpPreference -ExclusionPath "C:\RFUTests"
Add-MpPreference -ExclusionPath "C:\path\to\rfu\tests"

# Verify exclusions
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### 1.4 Windows Test Environment Validation

**Step 6: Validate Windows Environment**

```powershell
# Run Windows environment validation script
python tests\pre_beta\scripts\validate_windows_test_environment.py

# Expected output:
# ✓ Python 3.11 installed and accessible
# ✓ PyQt5 5.15.11 installed and functional
# ✓ Long path support enabled
# ✓ Network share accessible
# ✓ Test directories created
# ✓ Required dependencies installed
# ✓ Windows Defender exclusions configured
```

---

## 2. macOS Test Environment Setup

### 2.1 Prerequisites and System Requirements

**System Requirements:**

- macOS 10.15 (Catalina) or later
- 8GB RAM minimum, 16GB recommended
- 50GB free disk space for testing
- Administrator account access
- Internet connection for downloads

**Required Software:**

```bash
# Check macOS version
sw_vers

# Install Xcode Command Line Tools
xcode-select --install

# Verify installation
xcode-select -p
# Should output: /Applications/Xcode.app/Contents/Developer
# or: /Library/Developer/CommandLineTools
```

### 2.2 Package Manager and Python Setup

**Step 1: Install Homebrew**

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add Homebrew to PATH (for Apple Silicon Macs)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# Verify Homebrew installation
brew --version
```

**Step 2: Install Python Versions**

```bash
# Install multiple Python versions for testing
brew install python@3.9 python@3.10 python@3.11 python@3.12

# Verify installations
python3.11 --version
python3.10 --version

# Set Python 3.11 as default for testing
brew link --force python@3.11
```

**Step 3: Create Virtual Environment**

```bash
# Navigate to RFU project directory
cd /path/to/rfu

# Create virtual environment with Python 3.11
python3.11 -m venv rfu_test_env

# Activate virtual environment
source rfu_test_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r tests/pre_beta/requirements-test.txt

# Verify PyQt5 installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### 2.3 macOS-Specific Configuration

**Step 4: Configure Full Disk Access**

```bash
# Request Full Disk Access for Terminal (required for comprehensive testing)
# Manual step: System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add Terminal.app and any IDE you're using (VS Code, PyCharm)

# Verify Full Disk Access
python tests/pre_beta/scripts/verify_macos_full_disk_access.py
```

**Step 5: Create Case-Sensitive APFS Volume (Optional)**

```bash
# Create case-sensitive APFS volume for edge case testing
# This creates a 1GB case-sensitive volume mounted at /Volumes/RFU-Test-CaseSensitive
sudo diskutil apfs addVolume disk1 APFS "RFU-Test-CaseSensitive" -c

# Verify case-sensitive volume
touch /Volumes/RFU-Test-CaseSensitive/TestFile.txt
touch /Volumes/RFU-Test-CaseSensitive/testfile.txt
ls -la /Volumes/RFU-Test-CaseSensitive/
# Should show both files (different files on case-sensitive volume)
```

**Step 6: Configure Test Directories**

```bash
# Create test directory structure
mkdir -p ~/RFUTests/{UnicodeTests,ExtendedAttributes,SymlinkTests,BundleTests}

# Create Unicode NFD test files
python tests/pre_beta/scripts/create_macos_unicode_test_files.py

# Create files with extended attributes
xattr -w com.apple.FinderInfo "test metadata" ~/RFUTests/ExtendedAttributes/test_file.txt
xattr -w com.apple.quarantine "test quarantine" ~/RFUTests/ExtendedAttributes/quarantined_file.txt

# Create symlink test structures
python tests/pre_beta/scripts/create_macos_symlink_structures.py

# Verify extended attributes
xattr -l ~/RFUTests/ExtendedAttributes/test_file.txt
```

### 2.4 macOS Test Environment Validation

**Step 7: Validate macOS Environment**

```bash
# Run macOS environment validation script
python tests/pre_beta/scripts/validate_macos_test_environment.py

# Expected output:
# ✓ macOS 10.15+ detected
# ✓ Python 3.11 installed and accessible
# ✓ PyQt5 5.15.11 installed and functional
# ✓ Full Disk Access granted
# ✓ Unicode NFD test files created
# ✓ Extended attributes working
# ✓ Case-sensitive volume available (if created)
# ✓ Symlink structures created
```

---

## 3. Linux Test Environment Setup

### 3.1 Prerequisites and System Requirements

**Supported Distributions:**

- Ubuntu 20.04 LTS, 22.04 LTS
- CentOS 8, RHEL 8
- Fedora 35, 36, 37
- Debian 11, 12

**System Requirements:**

- 4GB RAM minimum, 8GB recommended
- 30GB free disk space for testing
- sudo access
- Internet connection for package downloads

### 3.2 Distribution-Specific Setup

#### 3.2.1 Ubuntu/Debian Setup

**Step 1: System Updates and Prerequisites**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install development tools
sudo apt install -y build-essential python3-dev python3-venv python3-pip git

# Install PyQt5 system dependencies
sudo apt install -y python3-pyqt5 python3-pyqt5-dev python3-pyqt5.qtsql

# Install additional tools for testing
sudo apt install -y xvfb  # For headless GUI testing
sudo apt install -y tree  # For directory structure visualization
```

**Step 2: Python Environment Setup**

```bash
# Install multiple Python versions (using deadsnakes PPA for Ubuntu)
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev
sudo apt install -y python3.10 python3.10-venv python3.10-dev
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Create virtual environment with Python 3.11
cd /path/to/rfu
python3.11 -m venv rfu_test_env
source rfu_test_env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r tests/pre_beta/requirements-test.txt

# Verify installation
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

#### 3.2.2 CentOS/RHEL Setup

**Step 1: Enable Additional Repositories**

```bash
# Enable EPEL repository
sudo dnf install -y epel-release

# Install development tools
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3-devel python3-pip python3-virtualenv git

# Install PyQt5 dependencies
sudo dnf install -y python3-qt5 python3-qt5-devel
```

#### 3.2.3 Fedora Setup

**Step 1: Install Development Tools**

```bash
# Install development tools and Python
sudo dnf install -y @development-tools python3-devel python3-pip python3-virtualenv git

# Install PyQt5
sudo dnf install -y python3-qt5 python3-qt5-devel

# Install additional testing tools
sudo dnf install -y xorg-x11-server-Xvfb tree
```

### 3.3 Linux-Specific Configuration

**Step 3: Configure Multiple Filesystems for Testing**

```bash
# Create test directory structure
sudo mkdir -p /mnt/rfu_tests/{ext4_test,xfs_test,btrfs_test}

# Create filesystem images for cross-device testing (requires sudo)
sudo dd if=/dev/zero of=/tmp/ext4_test.img bs=1M count=100
sudo dd if=/dev/zero of=/tmp/xfs_test.img bs=1M count=100

# Format filesystem images
sudo mkfs.ext4 /tmp/ext4_test.img
sudo mkfs.xfs /tmp/xfs_test.img

# Mount test filesystems
sudo mount -o loop /tmp/ext4_test.img /mnt/rfu_tests/ext4_test
sudo mount -o loop /tmp/xfs_test.img /mnt/rfu_tests/xfs_test

# Verify mounts
df -h | grep rfu_tests
mount | grep rfu_tests
```

**Step 4: Configure Test Permissions and Users**

```bash
# Create test user accounts for permission testing
sudo useradd -m rfutest1
sudo useradd -m rfutest2

# Set up test directories with various permissions
mkdir -p ~/RFUTests/{PermissionTests,SymlinkTests,CaseTests,CrossDeviceTests}

# Create files with different permissions
touch ~/RFUTests/PermissionTests/readable_file.txt
chmod 644 ~/RFUTests/PermissionTests/readable_file.txt

touch ~/RFUTests/PermissionTests/owner_only_file.txt  
chmod 600 ~/RFUTests/PermissionTests/owner_only_file.txt

touch ~/RFUTests/PermissionTests/no_read_file.txt
chmod 200 ~/RFUTests/PermissionTests/no_read_file.txt

# Create directories with special permissions
mkdir ~/RFUTests/PermissionTests/sticky_dir
chmod 1755 ~/RFUTests/PermissionTests/sticky_dir
```

**Step 5: Configure Symlink Test Structure**

```bash
# Create symlink test scenarios
cd ~/RFUTests/SymlinkTests

# Create target files and directories
mkdir targets
echo "Target file content" > targets/target_file.txt
echo "Another target" > targets/another_target.txt

# Create various symlink types
ln -s targets/target_file.txt simple_symlink.txt
ln -s ../targets/target_file.txt relative_symlink.txt
ln -s /home/$USER/RFUTests/SymlinkTests/targets/target_file.txt absolute_symlink.txt

# Create broken symlink
ln -s nonexistent_file.txt broken_symlink.txt

# Create circular symlinks
ln -s circular_b.txt circular_a.txt
ln -s circular_a.txt circular_b.txt

# Create directory symlink
ln -s targets symlink_to_directory

# Verify symlink structure
ls -la
```

**Step 6: Configure Case-Sensitive Test Data**

```bash
# Create case-sensitive test files (different files with different cases)
cd ~/RFUTests/CaseTests

# Create files that would conflict on Windows/macOS
echo "Upper case file" > FILE.TXT
echo "Lower case file" > file.txt
echo "Mixed case file" > File.txt

echo "Upper document" > DOCUMENT.PDF
echo "Lower document" > document.pdf

# Create directories with case differences
mkdir FOLDER folder Folder

# Verify all files exist separately
ls -la
# Should show all files as separate entries
```

### 3.4 Linux Test Environment Validation

**Step 7: Validate Linux Environment**

```bash
# Run Linux environment validation script
python tests/pre_beta/scripts/validate_linux_test_environment.py

# Expected output:
# ✓ Linux distribution detected: Ubuntu 22.04
# ✓ Python 3.11 installed and accessible
# ✓ PyQt5 5.15.11 installed and functional
# ✓ Multiple filesystems available for cross-device testing
# ✓ Permission test files created with correct permissions
# ✓ Symlink test structures created
# ✓ Case-sensitive test files created
# ✓ sudo access available
# ✓ Required system utilities available
```

---

## 4. Cross-Platform Environment Validation

### 4.1 Unified Environment Validation Script

**Step 8: Run Cross-Platform Validation**

```bash
# Run comprehensive environment validation
python tests/pre_beta/scripts/validate_cross_platform_environment.py --platform auto

# This script will:
# 1. Detect current platform
# 2. Validate platform-specific requirements
# 3. Test filesystem capabilities
# 4. Verify dependency installation
# 5. Check performance baseline feasibility
# 6. Validate test data integrity

# Expected output example:
# Platform Detection: linux (Ubuntu 22.04)
# Python Version: 3.11.5
# PyQt5 Version: 5.15.11
# Filesystem: ext4 (case-sensitive)
# Long Path Support: N/A (Unix-like)
# Unicode Support: Full NFD/NFC
# Extended Attributes: Supported
# Symlink Support: Full
# Network Paths: NFS/CIFS available
# Cross-Device Detection: Multiple mount points available
# Performance Baseline: Hardware suitable for baseline testing
# Test Data: All platform-specific test data created
# Environment Status: READY FOR TESTING ✓
```

### 4.2 Environment Configuration Export

**Step 9: Export Environment Configuration**

```bash
# Export environment configuration for reproducibility
python tests/pre_beta/scripts/export_environment_config.py --output-file environment_config.json

# This creates a configuration file that can be used to reproduce the environment
# The file includes:
# - Platform information
# - Python version and dependencies
# - Filesystem configuration
# - Test data locations
# - Performance baseline information
# - Special feature availability (long paths, xattr, etc.)
```

---

## 5. Automated Setup Scripts

### 5.1 One-Command Setup Scripts

#### 5.1.1 Windows Automated Setup

```powershell
# Windows one-command setup (run as Administrator)
# File: tests/pre_beta/scripts/setup_windows_environment.ps1

param(
    [string]$PythonVersion = "3.11",
    [switch]$EnableLongPaths,
    [switch]$ConfigureDefender,
    [switch]$CreateNetworkShare
)

# This script will:
# 1. Validate system requirements
# 2. Install Python if not present
# 3. Create virtual environment
# 4. Install dependencies
# 5. Enable long path support (if requested)
# 6. Configure Windows Defender exclusions (if requested)
# 7. Create network share (if requested)
# 8. Generate test data
# 9. Validate environment

# Usage:
# .\setup_windows_environment.ps1 -EnableLongPaths -ConfigureDefender -CreateNetworkShare
```

#### 5.1.2 macOS Automated Setup

```bash
#!/bin/bash
# macOS one-command setup
# File: tests/pre_beta/scripts/setup_macos_environment.sh

# This script will:
# 1. Install Xcode Command Line Tools if needed
# 2. Install Homebrew if needed
# 3. Install Python versions
# 4. Create virtual environment
# 5. Install dependencies
# 6. Create case-sensitive volume (optional)
# 7. Generate Unicode test data
# 8. Create extended attribute test files
# 9. Validate environment

# Usage:
# chmod +x tests/pre_beta/scripts/setup_macos_environment.sh
# ./tests/pre_beta/scripts/setup_macos_environment.sh --create-case-sensitive-volume
```

#### 5.1.3 Linux Automated Setup

```bash
#!/bin/bash
# Linux automated setup (works on Ubuntu, CentOS, Fedora)
# File: tests/pre_beta/scripts/setup_linux_environment.sh

# This script will:
# 1. Detect Linux distribution
# 2. Install distribution-appropriate packages
# 3. Install Python versions
# 4. Create virtual environment
# 5. Install dependencies
# 6. Create multiple filesystem test environment
# 7. Generate permission test data
# 8. Create symlink test structures
# 9. Validate environment

# Usage:
# chmod +x tests/pre_beta/scripts/setup_linux_environment.sh
# ./tests/pre_beta/scripts/setup_linux_environment.sh --create-test-filesystems
```

---

## 6. Docker-Based Testing Environment

### 6.1 Containerized Testing Setup

#### 6.1.1 Linux Docker Environment

```dockerfile
# File: tests/pre_beta/docker/Dockerfile.ubuntu
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3.11-dev \
    python3-pip git build-essential \
    python3-pyqt5 python3-pyqt5-dev \
    xvfb tree \
    && apt-get clean

# Create test user
RUN useradd -m -s /bin/bash rfutest
USER rfutest
WORKDIR /home/rfutest

# Copy RFU source code
COPY --chown=rfutest:rfutest . /home/rfutest/rfu

# Set up Python environment
RUN cd rfu && \
    python3.11 -m venv rfu_test_env && \
    . rfu_test_env/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r tests/pre_beta/requirements-test.txt

# Create test environment
RUN cd rfu && \
    . rfu_test_env/bin/activate && \
    python tests/pre_beta/scripts/create_linux_test_environment.py

# Set display for GUI testing
ENV DISPLAY=:99

# Entry point for testing
ENTRYPOINT ["bash", "-c", "cd rfu && . rfu_test_env/bin/activate && Xvfb :99 -screen 0 1024x768x24 & sleep 2 && exec \"$@\"", "--"]
```

**Docker Usage:**

```bash
# Build Linux test environment
docker build -f tests/pre_beta/docker/Dockerfile.ubuntu -t rfu-test-linux .

# Run Linux tests in container
docker run --rm -v $(pwd)/tests/results:/home/rfutest/rfu/tests/results rfu-test-linux \
    python -m pytest tests/pre_beta/cross_platform/linux/ -v

# Run interactive container for debugging
docker run -it --rm rfu-test-linux bash
```

### 6.2 Multi-Platform Docker Compose

```yaml
# File: tests/pre_beta/docker/docker-compose.yml
version: '3.8'

services:
  ubuntu-20-04:
    build:
      context: .
      dockerfile: tests/pre_beta/docker/Dockerfile.ubuntu20
    volumes:
      - ./tests/results:/app/tests/results
    environment:
      - DISPLAY=:99
    command: python -m pytest tests/pre_beta/cross_platform/linux/ -v
    
  ubuntu-22-04:
    build:
      context: .
      dockerfile: tests/pre_beta/docker/Dockerfile.ubuntu22
    volumes:
      - ./tests/results:/app/tests/results
    environment:
      - DISPLAY=:99
    command: python -m pytest tests/pre_beta/cross_platform/linux/ -v

  centos-8:
    build:
      context: .
      dockerfile: tests/pre_beta/docker/Dockerfile.centos8
    volumes:
      - ./tests/results:/app/tests/results
    command: python -m pytest tests/pre_beta/cross_platform/linux/ -v
```

**Usage:**

```bash
# Run tests on all Linux distributions
docker-compose -f tests/pre_beta/docker/docker-compose.yml up --abort-on-container-exit

# Run specific distribution
docker-compose -f tests/pre_beta/docker/docker-compose.yml up ubuntu-22-04
```

---

## 7. Cloud-Based Testing Environment

### 7.1 GitHub Actions Environment

#### 7.1.1 GitHub Actions Matrix Testing

```yaml
# File: .github/workflows/cross-platform-testing.yml
name: Cross-Platform Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
        python-version: ['3.9', '3.10', '3.11', '3.12']
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r tests/pre_beta/requirements-test.txt
    
    - name: Set up platform-specific test environment
      run: |
        python tests/pre_beta/scripts/setup_platform_environment.py --platform auto
    
    - name: Run platform-specific tests
      run: |
        python tests/pre_beta/scripts/run_platform_tests.py --category critical
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.os }}-py${{ matrix.python-version }}
        path: tests/results/
```

### 7.2 Cloud VM Testing Setup

#### 7.2.1 AWS EC2 Testing Environment

```bash
# AWS EC2 instances for comprehensive testing
# Windows Server 2019/2022 for Windows testing
# macOS instances (when available) for macOS testing  
# Ubuntu/Amazon Linux for Linux testing

# Example Ubuntu setup on EC2
aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type t3.medium \
    --key-name rfu-testing-key \
    --security-groups rfu-testing-sg \
    --user-data file://tests/pre_beta/cloud/aws-ubuntu-setup.sh

# User data script sets up complete testing environment automatically
```

---

## 8. Environment Troubleshooting

### 8.1 Common Setup Issues and Solutions

#### 8.1.1 Windows Setup Issues

**Issue: Long Path Support Not Working**

```powershell
# Verify current setting
reg query "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled

# If value is 0, enable long paths
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1

# Reboot may be required
# Test with:
python -c "import os; print(os.path.supports_long_paths)"
```

**Issue: PyQt5 Installation Fails**

```powershell
# Install Visual C++ Redistributable
# Download from Microsoft website and install

# Alternative: Install PyQt5 from conda-forge
conda install -c conda-forge pyqt=5.15.11
```

#### 8.1.2 macOS Setup Issues

**Issue: Full Disk Access Not Working**

```bash
# Verify Full Disk Access status
python -c "
import os
try:
    os.listdir('/Library/Application Support')
    print('Full Disk Access: OK')
except PermissionError:
    print('Full Disk Access: DENIED - Grant in System Preferences')
"

# Guide user to grant access:
# System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add Terminal.app and any IDE being used
```

**Issue: Case-Sensitive Volume Creation Fails**

```bash
# Check available disk space
diskutil info disk1

# Alternative: Create disk image instead
hdiutil create -size 1g -fs "Case-sensitive APFS" -volname "RFU-Test-CS" ~/Desktop/rfu-test-cs.dmg
hdiutil attach ~/Desktop/rfu-test-cs.dmg
```

#### 8.1.3 Linux Setup Issues

**Issue: PyQt5 GUI Tests Fail (Headless Environment)**

```bash
# Install and configure virtual display
sudo apt install -y xvfb

# Set up virtual display for GUI testing
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 &

# Verify GUI testing works
python -c "
from PyQt5.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)
print('GUI testing: OK')
"
```

**Issue: Cross-Device Testing Setup Fails**

```bash
# Check available disk space
df -h

# Alternative: Use tmpfs for testing
sudo mkdir /mnt/tmpfs_test
sudo mount -t tmpfs -o size=100M tmpfs /mnt/tmpfs_test

# Verify cross-device detection
python -c "
import os
print('Temp filesystem:', os.path.ismount('/mnt/tmpfs_test'))
"
```

---

## 9. Environment Maintenance and Updates

### 9.1 Regular Maintenance Procedures

#### 9.1.1 Weekly Environment Maintenance

```bash
# Update system packages (run weekly)
# Windows:
# Check for Windows Updates in Settings

# macOS:
brew update && brew upgrade
# Check for macOS updates in System Preferences

# Linux (Ubuntu):
sudo apt update && sudo apt upgrade -y

# Update Python dependencies
pip install --upgrade -r requirements.txt
pip install --upgrade -r tests/pre_beta/requirements-test.txt

# Validate environment still working
python tests/pre_beta/scripts/validate_cross_platform_environment.py
```

#### 9.1.2 Environment Reset Procedures

```bash
# Reset test environment to clean state
python tests/pre_beta/scripts/reset_test_environment.py --platform auto --confirm

# This script will:
# 1. Remove all generated test data
# 2. Reset file permissions to defaults
# 3. Cleanup temporary files and directories
# 4. Reset configuration to defaults
# 5. Validate clean environment state
```

### 9.2 Environment Backup and Restore

#### 9.2.1 Environment Configuration Backup

```bash
# Backup current environment configuration
python tests/pre_beta/scripts/backup_environment_config.py --output tests/environments/backup/

# Restore environment from backup
python tests/pre_beta/scripts/restore_environment_config.py --input tests/environments/backup/environment_config_20250905.json
```

This comprehensive setup guide ensures reproducible test environments across all supported platforms, enabling consistent and reliable cross-platform testing for RFU.
