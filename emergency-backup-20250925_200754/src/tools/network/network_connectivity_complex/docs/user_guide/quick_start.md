# Quick Start Guide

**Version:** 1.2.0  
**Estimated Time:** 15 minutes  
**Prerequisites:** Basic computer knowledge

## Welcome to Network Connectivity Toolkit

This guide will get you up and running with the Network Connectivity Toolkit in just a few minutes. You'll learn how to install, configure, and use the essential features.

## 🚀 Installation

### System Requirements
- **Operating System:** Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **Memory:** 4GB RAM minimum, 8GB recommended
- **Storage:** 500MB free space
- **Network:** Active network connection for monitoring

### Quick Installation

1. **Download the toolkit** (if not already installed)
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Verify installation:**
   ```bash
   python -m network_connectivity --version
   ```

## 🎯 First Launch

### Starting the GUI
```bash
python -m network_connectivity.gui.hub
```

Or from the main RFU interface:
1. Open Richard's File Utilities
2. Navigate to **Network Tools**
3. Click **Network Connectivity Hub**

### What You'll See
- **Overview Tab:** Main dashboard with tool cards
- **Tool Cards:** Bandwidth Monitor, Port Scanner, Wi-Fi Analyzer, LAN File Transfer
- **Status Bar:** Real-time status indicators for each tool

## 🔧 Essential Tools Overview

### 1. Bandwidth Monitor
**Purpose:** Monitor real-time network speed and usage

**Quick Start:**
1. Click **Bandwidth Monitor** card
2. Select your network interface
3. Click **Start Monitoring**
4. View real-time charts and statistics

**Key Features:**
- Real-time upload/download speed monitoring
- Historical data with customizable time ranges
- Bandwidth usage alerts and notifications
- Data export capabilities

### 2. Port Scanner
**Purpose:** Scan network ports for security analysis

**Quick Start:**
1. Click **Port Scanner** card
2. Enter target IP address or hostname
3. Select scan type (Quick, Full, or Custom)
4. Click **Start Scan**

**Key Features:**
- TCP and UDP port scanning
- Service detection and banner grabbing
- Vulnerability assessment
- Detailed reporting and export

### 3. Wi-Fi Analyzer
**Purpose:** Analyze wireless networks and signal strength

**Quick Start:**
1. Click **Wi-Fi Analyzer** card
2. Click **Start Scanning**
3. View detected networks and signal strengths
4. Analyze channel utilization and interference

**Key Features:**
- Real-time Wi-Fi network discovery
- Signal strength monitoring and history
- Channel analysis and optimization recommendations
- Security assessment of detected networks

### 4. LAN File Transfer
**Purpose:** Secure file sharing between local network devices

**Quick Start:**
1. Click **LAN File Transfer** card
2. Enable **Device Discovery**
3. Select files to share or browse available devices
4. Initiate secure file transfers

**Key Features:**
- Automatic device discovery on local network
- Encrypted file transfers with authentication
- Resume interrupted transfers
- Transfer history and management

## 📊 Your First Network Analysis

Let's perform a complete network analysis in 5 minutes:

### Step 1: Check Your Connection Speed (2 minutes)
1. Launch **Bandwidth Monitor**
2. Select your primary network interface
3. Start monitoring and observe for 1-2 minutes
4. Note your baseline upload/download speeds

### Step 2: Scan Your Network (2 minutes)
1. Open **Port Scanner**
2. Enter your router's IP (usually 192.168.1.1 or 192.168.0.1)
3. Run a **Quick Scan**
4. Review open ports and services

### Step 3: Analyze Wi-Fi Environment (1 minute)
1. Launch **Wi-Fi Analyzer**
2. Start scanning for networks
3. Identify your network and check signal strength
4. Note any channel congestion

## ⚙️ Basic Configuration

### Setting Up Alerts
1. Go to **Settings** → **Notifications**
2. Enable bandwidth alerts
3. Set threshold (e.g., 80% of your connection speed)
4. Choose notification method (popup, email, sound)

### Configuring Data Retention
1. Open **Settings** → **Data Management**
2. Set retention period (default: 30 days)
3. Configure automatic data export
4. Set storage location for reports

### Security Settings
1. Navigate to **Settings** → **Security**
2. Enable encryption for file transfers
3. Set authentication requirements
4. Configure trusted device list

## 🎨 Customizing the Interface

### Theme and Appearance
- **Dark/Light Mode:** Settings → Appearance → Theme
- **Chart Colors:** Settings → Visualization → Color Scheme
- **Layout:** Drag and resize tool windows as needed

### Dashboard Layout
- **Tool Cards:** Rearrange on overview page
- **Status Indicators:** Customize in status bar settings
- **Quick Access:** Pin frequently used tools

## 📈 Understanding the Data

### Bandwidth Monitor Metrics
- **Download Speed:** Data received from internet
- **Upload Speed:** Data sent to internet
- **Total Usage:** Cumulative data transfer
- **Peak Times:** Highest usage periods

### Port Scanner Results
- **Open Ports:** Accessible network services
- **Filtered Ports:** Blocked by firewall
- **Service Detection:** Identified running services
- **Security Score:** Overall security assessment

### Wi-Fi Analyzer Data
- **Signal Strength (dBm):** Higher values = stronger signal
- **Channel Utilization:** Percentage of channel usage
- **Security Type:** WPA3, WPA2, WEP, or Open
- **Interference Level:** Competing signals on same channel

## 🚨 Common First-Time Issues

### "No Network Interfaces Found"
**Solution:** Run as administrator/sudo or check network adapter drivers

### "Permission Denied" for Port Scanning
**Solution:** Some scans require elevated privileges - run as administrator

### "Wi-Fi Adapter Not Detected"
**Solution:** Ensure Wi-Fi is enabled and drivers are installed

### Slow Performance
**Solution:** Close unnecessary applications and check system resources

## 🔄 Next Steps

### Learn More
- **[Master User Guide](master_user_guide.md)** - Complete feature documentation
- **[Configuration Guide](configuration_guide.md)** - Advanced configuration options
- **[Tool-Specific Guides](../tools/)** - Detailed tool documentation

### Advanced Features
- **Automation:** Set up scheduled scans and monitoring
- **Integration:** Connect with external systems via API
- **Reporting:** Generate automated network reports
- **Alerting:** Configure advanced notification rules

### Best Practices
- **Regular Monitoring:** Set up continuous bandwidth monitoring
- **Security Scans:** Perform weekly port scans of your network
- **Wi-Fi Optimization:** Monthly channel analysis and optimization
- **Data Backup:** Regular export of historical data

## 💡 Tips for Success

1. **Start Simple:** Begin with basic monitoring before advanced features
2. **Regular Updates:** Keep the toolkit updated for latest features
3. **Documentation:** Bookmark relevant guides for quick reference
4. **Community:** Join user forums for tips and troubleshooting
5. **Backup Settings:** Export your configuration regularly

## 🆘 Getting Help

### Quick Help
- **F1 Key:** Context-sensitive help in any tool
- **Tooltips:** Hover over interface elements for explanations
- **Status Messages:** Check status bar for current operation info

### Documentation
- **[FAQ](../troubleshooting/faq.md)** - Common questions and answers
- **[Troubleshooting Guide](../troubleshooting/troubleshooting_guide.md)** - Problem resolution
- **[Support Guide](../troubleshooting/support_guide.md)** - Getting additional help

### Emergency Contacts
- **Critical Issues:** Check known issues list first
- **Bug Reports:** Use built-in reporting tool
- **Feature Requests:** Submit through feedback system

---

**Congratulations!** You're now ready to use the Network Connectivity Toolkit effectively. 

**Next recommended reading:** [Master User Guide](master_user_guide.md) for comprehensive feature coverage.