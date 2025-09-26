# Installation Guide

**Version:** 1.2.0  
**Last Updated:** 2025-07-26  
**Estimated Time:** 10-30 minutes

## Overview

This guide provides comprehensive installation instructions for the Network Connectivity Toolkit across all supported platforms. Choose the installation method that best fits your environment and requirements.

## 📋 System Requirements

### Minimum Requirements
- **Operating System:** Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **Memory:** 4GB RAM
- **Storage:** 500MB free space
- **Network:** Active network connection

### Recommended Requirements
- **Operating System:** Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python:** 3.9 or higher
- **Memory:** 8GB RAM or more
- **Storage:** 2GB free space
- **Network:** Gigabit ethernet or Wi-Fi 6

### Additional Requirements by Tool
- **Port Scanner:** Administrator/root privileges for some scan types
- **Wi-Fi Analyzer:** Wi-Fi adapter with monitor mode support (optional)
- **LAN File Transfer:** Network discovery requires multicast support
- **Bandwidth Monitor:** Network interface access permissions

## 🚀 Installation Methods

### Method 1: Integrated Installation (Recommended)

If you already have Richard's File Utilities (RFU) installed:

1. **Update RFU to latest version**
2. **Enable Network Connectivity module:**
   ```bash
   python -m rfu --enable-module network_connectivity
   ```
3. **Verify installation:**
   ```bash
   python -m rfu --list-modules
   ```

### Method 2: Standalone Installation

For standalone installation without RFU:

1. **Download the toolkit:**
   ```bash
   git clone https://github.com/your-repo/network-connectivity-toolkit.git
   cd network-connectivity-toolkit
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

### Method 3: Package Manager Installation

#### Using pip (when available):
```bash
pip install network-connectivity-toolkit
```

#### Using conda (when available):
```bash
conda install -c conda-forge network-connectivity-toolkit
```

## 🖥️ Platform-Specific Installation

### Windows Installation

#### Prerequisites
1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Install Git** (optional, for source installation)
3. **Install Visual C++ Build Tools** (for some dependencies)

#### Step-by-Step Installation
1. **Open Command Prompt as Administrator**
2. **Verify Python installation:**
   ```cmd
   python --version
   pip --version
   ```
3. **Install the toolkit:**
   ```cmd
   pip install network-connectivity-toolkit
   ```
4. **Install Windows-specific dependencies:**
   ```cmd
   pip install pywin32 wmi
   ```

#### Windows-Specific Notes
- **Firewall:** Windows Defender may prompt for network access permissions
- **UAC:** Some features require "Run as Administrator"
- **Antivirus:** Add toolkit directory to antivirus exclusions if needed

### macOS Installation

#### Prerequisites
1. **Install Homebrew** (recommended):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. **Install Python:**
   ```bash
   brew install python@3.9
   ```

#### Step-by-Step Installation
1. **Open Terminal**
2. **Verify Python installation:**
   ```bash
   python3 --version
   pip3 --version
   ```
3. **Install the toolkit:**
   ```bash
   pip3 install network-connectivity-toolkit
   ```
4. **Install macOS-specific dependencies:**
   ```bash
   pip3 install pyobjc-framework-SystemConfiguration
   ```

#### macOS-Specific Notes
- **Permissions:** Grant network access permissions when prompted
- **Gatekeeper:** May need to allow unsigned applications in Security preferences
- **Admin Rights:** Some network operations require sudo privileges

### Linux Installation

#### Ubuntu/Debian
1. **Update package list:**
   ```bash
   sudo apt update
   ```
2. **Install Python and dependencies:**
   ```bash
   sudo apt install python3 python3-pip python3-venv
   sudo apt install build-essential libssl-dev libffi-dev
   ```
3. **Install network tools:**
   ```bash
   sudo apt install net-tools wireless-tools
   ```
4. **Install the toolkit:**
   ```bash
   pip3 install network-connectivity-toolkit
   ```

#### CentOS/RHEL/Fedora
1. **Install Python and dependencies:**
   ```bash
   sudo dnf install python3 python3-pip python3-devel
   sudo dnf install gcc openssl-devel libffi-devel
   ```
2. **Install network tools:**
   ```bash
   sudo dnf install net-tools wireless-tools
   ```
3. **Install the toolkit:**
   ```bash
   pip3 install network-connectivity-toolkit
   ```

#### Arch Linux
1. **Install dependencies:**
   ```bash
   sudo pacman -S python python-pip base-devel
   sudo pacman -S net-tools wireless_tools
   ```
2. **Install the toolkit:**
   ```bash
   pip install network-connectivity-toolkit
   ```

## 🔧 Post-Installation Configuration

### Initial Setup
1. **Run initial configuration:**
   ```bash
   python -m network_connectivity --setup
   ```
2. **Test installation:**
   ```bash
   python -m network_connectivity --test
   ```
3. **Launch GUI:**
   ```bash
   python -m network_connectivity.gui.hub
   ```

### Configuration Files
The toolkit creates configuration files in:
- **Windows:** `%APPDATA%\NetworkConnectivity\`
- **macOS:** `~/Library/Application Support/NetworkConnectivity/`
- **Linux:** `~/.config/NetworkConnectivity/`

### Default Configuration
```yaml
network_connectivity:
  general:
    default_timeout: 5000
    enable_logging: true
    log_level: INFO
  bandwidth_monitor:
    monitoring_interval: 1000
    enable_alerts: true
  port_scanner:
    default_scan_type: tcp
    max_threads: 50
  wifi_analyzer:
    scan_interval: 30000
    enable_security_analysis: true
  lan_file_transfer:
    discovery_port: 8765
    encryption_enabled: true
```

## 🔐 Permissions and Security

### Required Permissions
- **Network Interface Access:** Reading network statistics
- **Socket Creation:** For port scanning and file transfer
- **Multicast Access:** For device discovery
- **File System Access:** For configuration and data storage

### Security Considerations
1. **Firewall Rules:** Configure firewall to allow toolkit network access
2. **User Permissions:** Some features require elevated privileges
3. **Network Security:** Ensure secure network environment for file transfers
4. **Data Privacy:** Configure data retention and encryption settings

### Setting Up Permissions

#### Windows
1. **Run as Administrator** for full functionality
2. **Configure Windows Firewall:**
   - Allow Python through firewall
   - Add specific ports if needed (8765, 8766 for file transfer)

#### macOS
1. **Grant network permissions** when prompted
2. **For advanced features:**
   ```bash
   sudo python -m network_connectivity --setup-permissions
   ```

#### Linux
1. **Add user to netdev group:**
   ```bash
   sudo usermod -a -G netdev $USER
   ```
2. **Set capabilities for network access:**
   ```bash
   sudo setcap cap_net_raw+ep $(which python3)
   ```

## ✅ Verification and Testing

### Basic Verification
```bash
# Check installation
python -m network_connectivity --version

# Test core functionality
python -m network_connectivity --test

# List available tools
python -m network_connectivity --list-tools
```

### Comprehensive Testing
```bash
# Run full test suite
python -m network_connectivity.tests --all

# Test specific components
python -m network_connectivity.tests --bandwidth-monitor
python -m network_connectivity.tests --port-scanner
python -m network_connectivity.tests --wifi-analyzer
python -m network_connectivity.tests --lan-file-transfer
```

### GUI Testing
1. **Launch the GUI:**
   ```bash
   python -m network_connectivity.gui.hub
   ```
2. **Verify all tool cards are visible**
3. **Test launching each tool**
4. **Check status indicators**

## 🔄 Updates and Maintenance

### Updating the Toolkit
```bash
# Update via pip
pip install --upgrade network-connectivity-toolkit

# Update via git (source installation)
git pull origin main
pip install -e .
```

### Backup Configuration
```bash
# Export current configuration
python -m network_connectivity --export-config backup.json

# Import configuration
python -m network_connectivity --import-config backup.json
```

## 🚨 Troubleshooting Installation

### Common Issues

#### "Python not found"
**Solution:** Install Python 3.8+ and ensure it's in your PATH

#### "Permission denied" errors
**Solution:** Run with administrator/sudo privileges or adjust permissions

#### "Module not found" errors
**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

#### Network interface detection issues
**Solution:** 
- Check network adapter drivers
- Verify network interfaces are active
- Run with elevated privileges

#### GUI doesn't start
**Solution:**
- Install GUI dependencies: `pip install PyQt5`
- Check display environment variables
- Verify graphics drivers

### Platform-Specific Issues

#### Windows
- **Antivirus blocking:** Add exclusions for toolkit directory
- **Windows Defender:** Allow network access when prompted
- **UAC prompts:** Run as administrator for full functionality

#### macOS
- **Gatekeeper warnings:** Allow in Security & Privacy settings
- **Network permissions:** Grant access when prompted
- **Homebrew issues:** Update Homebrew and reinstall dependencies

#### Linux
- **Missing dependencies:** Install development packages
- **Permission issues:** Add user to appropriate groups
- **Display issues:** Set DISPLAY environment variable

## 📞 Getting Help

### Documentation
- **[System Requirements](system_requirements.md)** - Detailed requirements
- **[Platform Setup](platform_setup.md)** - Platform-specific guides
- **[Troubleshooting](../troubleshooting/troubleshooting_guide.md)** - Problem resolution

### Support Resources
- **[FAQ](../troubleshooting/faq.md)** - Common questions
- **[Known Issues](../troubleshooting/known_issues.md)** - Current limitations
- **[Support Guide](../troubleshooting/support_guide.md)** - Getting help

### Community
- Report installation issues
- Share installation experiences
- Contribute to documentation improvements

---

**Installation complete!** Continue with the **[Quick Start Guide](../user_guide/quick_start.md)** to begin using the toolkit.