# Port Scanner Guide

**Version:** 1.2.0  
**Last Updated:** 2025-07-26  
**Tool Version:** Network Connectivity Toolkit v1.2.0+

## Overview

The Port Scanner is a comprehensive network security analysis tool that performs TCP and UDP port scanning, service detection, banner grabbing, and vulnerability assessment. It helps network administrators and security professionals identify open services, assess network security posture, and detect potential vulnerabilities.

## 🚀 Getting Started

### Quick Launch
1. **From GUI Hub:** Click the "Port Scanner" card
2. **From Command Line:** `python -m network_connectivity.tools.port_scanner`
3. **From RFU:** Navigate to Network Tools → Port Scanner

### First-Time Setup
1. **Enter Target:** Specify IP address, hostname, or network range
2. **Select Scan Type:** Choose from Quick, Full, or Custom scan
3. **Configure Options:** Set scan parameters and preferences
4. **Start Scan:** Begin the port scanning process

### Security Notice
⚠️ **Important:** Only scan networks and systems you own or have explicit permission to test. Unauthorized port scanning may violate laws and network policies.

## 🔧 Interface Overview

### Main Dashboard
- **Target Configuration:** Input fields for scan targets
- **Scan Type Selection:** Predefined and custom scan options
- **Progress Indicators:** Real-time scan progress and status
- **Results Display:** Detailed scan results and analysis
- **Export Options:** Save results in various formats

### Target Configuration Panel
- **Single Host:** IP address or hostname
- **IP Range:** CIDR notation or range specification
- **Host List:** Multiple targets from file or manual entry
- **Exclusions:** Hosts to skip during scanning

### Scan Configuration
- **Port Selection:** Individual ports, ranges, or predefined sets
- **Scan Techniques:** TCP SYN, TCP Connect, UDP, etc.
- **Timing Options:** Scan speed and stealth settings
- **Advanced Options:** Service detection, OS fingerprinting

## 📊 Scan Types and Techniques

### Predefined Scan Types

#### Quick Scan
- **Ports:** Top 100 most common ports
- **Technique:** TCP SYN scan
- **Speed:** Fast (high scan rate)
- **Use Case:** Rapid network assessment

```python
# Example: Quick scan
from network_connectivity.tools.port_scanner import PortScanner

scanner = PortScanner()
results = scanner.quick_scan("192.168.1.1")
```

#### Full Scan
- **Ports:** All 65,535 TCP ports
- **Technique:** TCP SYN scan with service detection
- **Speed:** Comprehensive (slower but thorough)
- **Use Case:** Complete security assessment

#### Custom Scan
- **Ports:** User-defined port selection
- **Technique:** Configurable scan methods
- **Speed:** User-controlled timing
- **Use Case:** Targeted analysis

### Scan Techniques

#### TCP Scanning
1. **TCP SYN Scan (Stealth Scan)**
   - Sends SYN packets without completing handshake
   - Fast and stealthy
   - Requires raw socket privileges
   - Default technique for most scans

2. **TCP Connect Scan**
   - Completes full TCP handshake
   - More reliable but slower
   - Works without special privileges
   - Generates more log entries

3. **TCP ACK Scan**
   - Sends ACK packets to determine firewall rules
   - Used for firewall detection
   - Doesn't determine open/closed ports
   - Useful for mapping firewall rules

#### UDP Scanning
- **UDP Scan**
  - Sends UDP packets to target ports
  - Slower than TCP scanning
  - Less reliable due to UDP nature
  - Important for discovering UDP services

#### Advanced Techniques
- **TCP FIN Scan:** Sends FIN packets to evade detection
- **TCP Null Scan:** Sends packets with no flags set
- **TCP Xmas Scan:** Sends packets with FIN, PSH, and URG flags

### Port Selection Options

#### Predefined Port Sets
```yaml
port_scanner:
  port_sets:
    common_ports: [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5432, 5900]
    web_ports: [80, 443, 8080, 8443, 8000, 8888]
    database_ports: [1433, 1521, 3306, 5432, 27017]
    remote_access_ports: [22, 23, 3389, 5900, 5901]
```

#### Custom Port Ranges
- **Single Port:** `80`
- **Port Range:** `80-443`
- **Multiple Ranges:** `80-443,8000-8080`
- **Mixed Format:** `22,80-443,8080`

## 🔍 Service Detection and Analysis

### Service Detection
Automatically identifies services running on open ports:
- **Service Name:** HTTP, SSH, FTP, etc.
- **Version Information:** Software version when available
- **Service Banner:** Raw service response
- **Confidence Level:** Detection accuracy rating

### Banner Grabbing
Captures service banners and responses:
```python
# Example: Service detection with banner grabbing
scanner = PortScanner()
results = scanner.scan_with_service_detection(
    target="192.168.1.1",
    ports="22,80,443",
    grab_banners=True
)

for port, info in results.items():
    print(f"Port {port}: {info['service']} - {info['banner']}")
```

### Operating System Detection
Attempts to identify target operating system:
- **OS Family:** Windows, Linux, macOS, etc.
- **Version Information:** Specific OS version when detectable
- **Confidence Score:** Reliability of OS detection
- **Fingerprint Details:** Technical detection details

## 🛡️ Security Features

### Stealth Scanning Options
```yaml
port_scanner:
  stealth:
    scan_delay: 100  # milliseconds between probes
    randomize_order: true  # randomize port scan order
    source_port_randomization: true
    decoy_scanning: false  # use decoy IP addresses
    fragment_packets: false  # fragment scan packets
```

### Rate Limiting and Timing
- **Scan Rate Control:** Limit packets per second
- **Adaptive Timing:** Adjust based on network conditions
- **Timeout Configuration:** Set connection timeouts
- **Retry Logic:** Configure retry attempts

### Target Validation
- **IP Address Validation:** Verify valid IP addresses
- **Hostname Resolution:** DNS lookup verification
- **Network Reachability:** Ping test before scanning
- **Permission Checking:** Validate scan authorization

## 📈 Results Analysis and Reporting

### Scan Results Structure
```json
{
  "scan_info": {
    "target": "192.168.1.1",
    "scan_type": "tcp_syn",
    "start_time": "2025-01-26T10:00:00Z",
    "end_time": "2025-01-26T10:05:30Z",
    "total_ports": 1000,
    "scan_duration": 330
  },
  "host_info": {
    "hostname": "router.local",
    "os_detection": {
      "os_family": "Linux",
      "confidence": 85
    }
  },
  "ports": {
    "22": {
      "state": "open",
      "service": "ssh",
      "version": "OpenSSH 8.2",
      "banner": "SSH-2.0-OpenSSH_8.2p1"
    },
    "80": {
      "state": "open",
      "service": "http",
      "version": "Apache 2.4.41",
      "banner": "Apache/2.4.41 (Ubuntu)"
    }
  }
}
```

### Port States
- **Open:** Port is accepting connections
- **Closed:** Port is not accepting connections
- **Filtered:** Port is blocked by firewall
- **Open|Filtered:** Cannot determine if open or filtered
- **Closed|Filtered:** Cannot determine if closed or filtered

### Security Assessment
Automatic security analysis of scan results:
- **Risk Assessment:** High, medium, low risk services
- **Vulnerability Indicators:** Known vulnerable services
- **Security Recommendations:** Suggested security improvements
- **Compliance Checking:** Security standard compliance

## 📊 Reporting and Export

### Report Formats
- **HTML:** Interactive web-based reports with charts
- **PDF:** Professional formatted reports
- **CSV:** Spreadsheet-compatible data export
- **JSON:** Structured data for programmatic processing
- **XML:** Structured markup for system integration

### Report Content Options
```yaml
port_scanner:
  reporting:
    include_closed_ports: false
    include_filtered_ports: true
    include_service_details: true
    include_banners: true
    include_os_detection: true
    include_security_assessment: true
    include_recommendations: true
```

### Automated Reporting
```python
# Example: Generate comprehensive report
scanner = PortScanner()
results = scanner.scan("192.168.1.0/24", ports="1-1000")

report = scanner.generate_report(
    results=results,
    format="html",
    include_charts=True,
    include_security_analysis=True,
    output_file="network_scan_report.html"
)
```

## ⚙️ Configuration Options

### Basic Configuration
```yaml
port_scanner:
  default_scan_type: "tcp_syn"
  scan_timeout: 3000  # milliseconds
  max_threads: 50
  enable_service_detection: true
  enable_os_detection: false
  save_scan_results: true
```

### Advanced Configuration
```yaml
port_scanner:
  advanced:
    enable_vulnerability_scan: false
    scan_delay: 0  # milliseconds
    randomize_scan_order: false
    enable_banner_grabbing: true
    max_retries: 3
    adaptive_timing: true
    stealth_mode: false
```

### Performance Tuning
```yaml
port_scanner:
  performance:
    thread_pool_size: 100
    connection_timeout: 5000
    read_timeout: 3000
    max_concurrent_hosts: 10
    memory_limit_mb: 256
```

## 🔧 Advanced Features

### Vulnerability Scanning
When enabled, performs basic vulnerability assessment:
- **Known Vulnerabilities:** Check for known service vulnerabilities
- **Default Credentials:** Test for default username/password combinations
- **SSL/TLS Analysis:** Analyze SSL/TLS configuration
- **Web Application Testing:** Basic web vulnerability checks

### Firewall Detection
Analyze firewall behavior and rules:
- **Firewall Presence:** Detect if firewall is active
- **Rule Analysis:** Understand filtering rules
- **Bypass Techniques:** Attempt firewall evasion
- **Policy Assessment:** Evaluate firewall effectiveness

### Network Mapping
Build comprehensive network topology:
- **Host Discovery:** Identify active hosts
- **Service Mapping:** Map services to hosts
- **Relationship Analysis:** Understand network relationships
- **Topology Visualization:** Generate network diagrams

## 🛠️ Troubleshooting

### Common Issues

#### "Permission Denied" Errors
**Causes:**
- Insufficient privileges for raw sockets
- Firewall blocking scan attempts
- Network policy restrictions

**Solutions:**
1. Run with administrator/root privileges
2. Use TCP Connect scan instead of SYN scan
3. Configure firewall exceptions
4. Check network access policies

#### Slow Scan Performance
**Causes:**
- Network latency or congestion
- Too many concurrent threads
- Target host rate limiting

**Solutions:**
1. Reduce thread count
2. Increase scan delays
3. Use adaptive timing
4. Scan smaller port ranges

#### Inaccurate Results
**Causes:**
- Firewall interference
- Network address translation (NAT)
- Load balancers or proxies

**Solutions:**
1. Try different scan techniques
2. Adjust timeout values
3. Use multiple scan methods
4. Verify network topology

#### Service Detection Failures
**Causes:**
- Custom or modified services
- Service banner suppression
- Network filtering

**Solutions:**
1. Enable banner grabbing
2. Try manual service identification
3. Use multiple detection methods
4. Check for service customization

### Performance Optimization

#### Scan Speed Optimization
```yaml
port_scanner:
  optimization:
    max_threads: 100  # Increase for faster scans
    scan_delay: 0  # Remove delays for speed
    timeout: 1000  # Reduce timeout for faster results
    adaptive_timing: true  # Adjust based on network
```

#### Memory Management
```yaml
port_scanner:
  memory:
    result_caching: true
    max_cached_results: 1000
    cleanup_interval: 3600  # seconds
    memory_limit_mb: 512
```

## 📚 Integration Examples

### Python API Usage
```python
from network_connectivity.tools.port_scanner import PortScanner
from datetime import datetime

# Create scanner instance
scanner = PortScanner()

# Configure scan options
scanner.configure(
    scan_type="tcp_syn",
    threads=50,
    timeout=3000,
    enable_service_detection=True
)

# Scan single host
results = scanner.scan(
    target="192.168.1.1",
    ports="1-1000"
)

# Scan network range
network_results = scanner.scan_network(
    network="192.168.1.0/24",
    ports="22,80,443"
)

# Generate security report
security_report = scanner.analyze_security(results)
print(f"Security Score: {security_report['score']}/100")

# Export results
scanner.export_results(
    results=results,
    format="json",
    filename=f"scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
)
```

### Command Line Usage
```bash
# Quick scan of single host
python -m network_connectivity.tools.port_scanner --target 192.168.1.1 --quick

# Full scan with service detection
python -m network_connectivity.tools.port_scanner \
  --target 192.168.1.1 \
  --ports 1-65535 \
  --service-detection \
  --output full_scan.json

# Network range scan
python -m network_connectivity.tools.port_scanner \
  --target 192.168.1.0/24 \
  --ports 22,80,443 \
  --threads 100 \
  --format html \
  --output network_scan.html

# Stealth scan with delays
python -m network_connectivity.tools.port_scanner \
  --target example.com \
  --ports 1-1000 \
  --stealth \
  --delay 100 \
  --randomize
```

## 🔗 Related Documentation

### User Guides
- **[Quick Start Guide](../user_guide/quick_start.md)** - Getting started quickly
- **[Master User Guide](../user_guide/master_user_guide.md)** - Comprehensive user documentation
- **[Security Guide](../user_guide/security_guide.md)** - Security best practices

### Technical Documentation
- **[API Reference](../api/port_scanner_api.md)** - Programming interface
- **[Architecture](../technical/architecture.md)** - System design
- **[Security Documentation](../technical/security.md)** - Security features

### Support Resources
- **[Troubleshooting](../troubleshooting/troubleshooting_guide.md)** - Problem resolution
- **[FAQ](../troubleshooting/faq.md)** - Common questions
- **[Legal Considerations](../reference/legal_considerations.md)** - Usage guidelines

---

**Security Notice:** Always ensure you have proper authorization before scanning networks. Check the **[Legal Considerations](../reference/legal_considerations.md)** guide for important usage guidelines.