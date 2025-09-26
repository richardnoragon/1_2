# Usage Examples

**Version:** 1.2.0  
**Last Updated:** 2025-07-26  
**Compatibility:** Network Connectivity Toolkit v1.2.0+

## Overview

This document provides comprehensive real-world usage examples for the Network Connectivity Toolkit. These examples demonstrate practical scenarios and common use cases for network administrators, security professionals, and power users.

## 🏢 Enterprise Network Monitoring

### Scenario: Corporate Network Health Monitoring

Monitor bandwidth usage across multiple network segments and generate daily reports.

```python
from network_connectivity.tools.bandwidth_monitor import BandwidthMonitor
from network_connectivity.core.config_service import get_config_service
from network_connectivity.core.logging_service import get_logging_service
from datetime import datetime, timedelta
import schedule
import time

class EnterpriseNetworkMonitor:
    def __init__(self):
        self.config = get_config_service()
        self.logger = get_logging_service().get_logger('EnterpriseMonitor')
        self.monitors = {}
        
        # Configure enterprise settings
        self.config.set_setting('network_connectivity', 'general', {
            'default_timeout': 3000,
            'enable_logging': True,
            'log_level': 'INFO'
        })
        
    def setup_monitoring(self):
        """Setup monitoring for multiple network interfaces."""
        interfaces = ['eth0', 'eth1', 'wlan0']  # Primary, backup, wireless
        
        for interface in interfaces:
            monitor = BandwidthMonitor()
            
            # Configure interface-specific settings
            monitor.set_tool_config('monitoring_interval', 5000)  # 5 seconds
            monitor.set_tool_config('data_retention_hours', 168)  # 1 week
            monitor.set_tool_config('enable_alerts', True)
            
            # Setup alerts for business hours (9 AM - 6 PM)
            monitor.configure_alert(
                alert_type="speed_threshold",
                threshold=80,  # 80% of expected bandwidth
                direction="both",
                schedule="business_hours"
            )
            
            # Setup usage quota alerts
            monitor.configure_alert(
                alert_type="usage_quota",
                daily_limit_gb=100,
                warning_threshold=0.8
            )
            
            self.monitors[interface] = monitor
            self.logger.info(f"Configured monitoring for {interface}")
    
    def start_monitoring(self):
        """Start monitoring all interfaces."""
        for interface, monitor in self.monitors.items():
            try:
                if monitor.start_monitoring(interface=interface, interval=5000):
                    self.logger.info(f"Started monitoring {interface}")
                else:
                    self.logger.error(f"Failed to start monitoring {interface}")
            except Exception as e:
                self.logger.error(f"Error starting {interface}: {e}")
    
    def generate_daily_report(self):
        """Generate daily network usage report."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        report_data = {
            'report_date': end_time.strftime('%Y-%m-%d'),
            'interfaces': {}
        }
        
        for interface, monitor in self.monitors.items():
            try:
                # Get usage statistics
                stats = monitor.get_usage_statistics(start_time, end_time)
                
                # Get current health status
                health = monitor.get_health_status()
                
                report_data['interfaces'][interface] = {
                    'total_download_gb': stats.get('total_download_bytes', 0) / (1024**3),
                    'total_upload_gb': stats.get('total_upload_bytes', 0) / (1024**3),
                    'peak_download_mbps': stats.get('peak_download_speed', 0),
                    'peak_upload_mbps': stats.get('peak_upload_speed', 0),
                    'average_download_mbps': stats.get('avg_download_speed', 0),
                    'average_upload_mbps': stats.get('avg_upload_speed', 0),
                    'uptime_percentage': health.get('uptime_percentage', 0),
                    'alert_count': stats.get('alert_count', 0)
                }
                
                # Export detailed data
                monitor.export_data(
                    start_time=start_time,
                    end_time=end_time,
                    format="csv",
                    filename=f"bandwidth_{interface}_{end_time.strftime('%Y%m%d')}.csv"
                )
                
            except Exception as e:
                self.logger.error(f"Error generating report for {interface}: {e}")
                report_data['interfaces'][interface] = {'error': str(e)}
        
        # Generate summary report
        self._generate_summary_report(report_data)
        
        return report_data
    
    def _generate_summary_report(self, data):
        """Generate HTML summary report."""
        html_content = f"""
        <html>
        <head><title>Daily Network Report - {data['report_date']}</title></head>
        <body>
        <h1>Network Usage Report - {data['report_date']}</h1>
        <table border="1">
        <tr><th>Interface</th><th>Download (GB)</th><th>Upload (GB)</th><th>Peak Speed (Mbps)</th><th>Alerts</th></tr>
        """
        
        for interface, stats in data['interfaces'].items():
            if 'error' not in stats:
                html_content += f"""
                <tr>
                <td>{interface}</td>
                <td>{stats['total_download_gb']:.2f}</td>
                <td>{stats['total_upload_gb']:.2f}</td>
                <td>{stats['peak_download_mbps']:.1f}</td>
                <td>{stats['alert_count']}</td>
                </tr>
                """
        
        html_content += """
        </table>
        </body>
        </html>
        """
        
        with open(f"network_report_{data['report_date']}.html", 'w') as f:
            f.write(html_content)

# Usage
monitor = EnterpriseNetworkMonitor()
monitor.setup_monitoring()
monitor.start_monitoring()

# Schedule daily reports
schedule.every().day.at("06:00").do(monitor.generate_daily_report)

# Keep monitoring running
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🔒 Security Assessment Automation

### Scenario: Automated Network Security Scanning

Perform regular security assessments of network infrastructure.

```python
from network_connectivity.tools.port_scanner import PortScanner
from network_connectivity.tools.wifi_analyzer import WiFiAnalyzer
from network_connectivity.core.logging_service import get_logging_service
from datetime import datetime
import json

class SecurityAssessment:
    def __init__(self):
        self.port_scanner = PortScanner()
        self.wifi_analyzer = WiFiAnalyzer()
        self.logger = get_logging_service().get_logger('SecurityAssessment')
        
        # Configure security scanning
        self.port_scanner.configure(
            scan_type="tcp_syn",
            threads=25,  # Conservative for production
            timeout=5000,
            enable_service_detection=True,
            stealth_mode=True
        )
    
    def scan_network_infrastructure(self, network_range="192.168.1.0/24"):
        """Comprehensive infrastructure security scan."""
        self.logger.info(f"Starting security assessment of {network_range}")
        
        assessment_results = {
            'timestamp': datetime.now().isoformat(),
            'network_range': network_range,
            'infrastructure_scan': {},
            'wireless_analysis': {},
            'security_summary': {}
        }
        
        # 1. Infrastructure Port Scanning
        self.logger.info("Scanning network infrastructure...")
        
        # Scan critical infrastructure ports
        critical_ports = "22,23,25,53,80,135,139,443,445,993,995,3389,5900"
        
        try:
            infrastructure_results = self.port_scanner.scan_network(
                network=network_range,
                ports=critical_ports
            )
            
            assessment_results['infrastructure_scan'] = infrastructure_results
            
            # Analyze for security issues
            security_issues = self._analyze_infrastructure_security(infrastructure_results)
            assessment_results['security_summary']['infrastructure_issues'] = security_issues
            
        except Exception as e:
            self.logger.error(f"Infrastructure scan failed: {e}")
            assessment_results['infrastructure_scan'] = {'error': str(e)}
        
        # 2. Wireless Security Analysis
        self.logger.info("Analyzing wireless security...")
        
        try:
            self.wifi_analyzer.start_scanning(
                scan_interval=10000,
                enable_security_analysis=True
            )
            
            # Scan for 2 minutes to get comprehensive results
            time.sleep(120)
            
            networks = self.wifi_analyzer.get_networks()
            wireless_analysis = self._analyze_wireless_security(networks)
            
            assessment_results['wireless_analysis'] = wireless_analysis
            
            self.wifi_analyzer.stop_scanning()
            
        except Exception as e:
            self.logger.error(f"Wireless analysis failed: {e}")
            assessment_results['wireless_analysis'] = {'error': str(e)}
        
        # 3. Generate Security Report
        self._generate_security_report(assessment_results)
        
        return assessment_results
    
    def _analyze_infrastructure_security(self, scan_results):
        """Analyze infrastructure scan for security issues."""
        issues = []
        
        for host, host_data in scan_results.get('hosts', {}).items():
            host_issues = []
            
            for port, port_data in host_data.get('ports', {}).items():
                if port_data['state'] == 'open':
                    service = port_data.get('service', 'unknown')
                    
                    # Check for high-risk services
                    if port in ['23', '135', '139', '445']:  # Telnet, RPC, NetBIOS
                        host_issues.append({
                            'severity': 'high',
                            'port': port,
                            'service': service,
                            'issue': 'High-risk service exposed',
                            'recommendation': 'Consider disabling or restricting access'
                        })
                    
                    # Check for unencrypted services
                    if port in ['21', '23', '25', '80', '110']:  # FTP, Telnet, SMTP, HTTP, POP3
                        host_issues.append({
                            'severity': 'medium',
                            'port': port,
                            'service': service,
                            'issue': 'Unencrypted service',
                            'recommendation': 'Use encrypted alternative (HTTPS, FTPS, etc.)'
                        })
                    
                    # Check for default configurations
                    if 'default' in port_data.get('banner', '').lower():
                        host_issues.append({
                            'severity': 'medium',
                            'port': port,
                            'service': service,
                            'issue': 'Possible default configuration',
                            'recommendation': 'Review and harden service configuration'
                        })
            
            if host_issues:
                issues.append({
                    'host': host,
                    'issues': host_issues,
                    'risk_score': self._calculate_risk_score(host_issues)
                })
        
        return issues
    
    def _analyze_wireless_security(self, networks):
        """Analyze wireless networks for security issues."""
        analysis = {
            'total_networks': len(networks),
            'security_breakdown': {},
            'security_issues': [],
            'recommendations': []
        }
        
        security_types = {}
        
        for network in networks:
            security_type = network.get('security_type', 'Unknown')
            security_types[security_type] = security_types.get(security_type, 0) + 1
            
            # Assess individual network security
            security_assessment = self.wifi_analyzer.assess_security(network)
            
            if security_assessment['score'] < 50:
                analysis['security_issues'].append({
                    'ssid': network['ssid'],
                    'security_type': security_type,
                    'signal_strength': network['signal_strength'],
                    'security_score': security_assessment['score'],
                    'issues': security_assessment.get('issues', [])
                })
        
        analysis['security_breakdown'] = security_types
        
        # Generate recommendations
        if 'Open' in security_types:
            analysis['recommendations'].append(
                "Open networks detected - consider securing with WPA3"
            )
        
        if 'WEP' in security_types:
            analysis['recommendations'].append(
                "WEP networks detected - upgrade to WPA2/WPA3 immediately"
            )
        
        return analysis
    
    def _calculate_risk_score(self, issues):
        """Calculate risk score based on security issues."""
        score = 0
        for issue in issues:
            if issue['severity'] == 'high':
                score += 10
            elif issue['severity'] == 'medium':
                score += 5
            elif issue['severity'] == 'low':
                score += 1
        return min(score, 100)  # Cap at 100
    
    def _generate_security_report(self, results):
        """Generate comprehensive security report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON report for programmatic processing
        with open(f'security_assessment_{timestamp}.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # HTML report for human review
        html_report = self._create_html_security_report(results)
        with open(f'security_report_{timestamp}.html', 'w') as f:
            f.write(html_report)
        
        self.logger.info(f"Security assessment completed - reports saved with timestamp {timestamp}")
    
    def _create_html_security_report(self, results):
        """Create HTML security report."""
        # Implementation would create a comprehensive HTML report
        # This is a simplified version
        return f"""
        <html>
        <head><title>Security Assessment Report</title></head>
        <body>
        <h1>Network Security Assessment</h1>
        <p>Assessment Date: {results['timestamp']}</p>
        <p>Network Range: {results['network_range']}</p>
        
        <h2>Infrastructure Security</h2>
        <p>Hosts Scanned: {len(results.get('infrastructure_scan', {}).get('hosts', {}))}</p>
        
        <h2>Wireless Security</h2>
        <p>Networks Found: {results.get('wireless_analysis', {}).get('total_networks', 0)}</p>
        
        <h2>Security Issues</h2>
        <p>Review the JSON report for detailed security findings.</p>
        </body>
        </html>
        """

# Usage
assessment = SecurityAssessment()
results = assessment.scan_network_infrastructure("192.168.1.0/24")
```

## 🏠 Home Network Optimization

### Scenario: Home Wi-Fi Network Optimization

Optimize home Wi-Fi network for best performance and coverage.

```python
from network_connectivity.tools.wifi_analyzer import WiFiAnalyzer
from network_connectivity.tools.bandwidth_monitor import BandwidthMonitor
import time
from datetime import datetime, timedelta

class HomeNetworkOptimizer:
    def __init__(self):
        self.wifi_analyzer = WiFiAnalyzer()
        self.bandwidth_monitor = BandwidthMonitor()
        
    def analyze_wifi_environment(self):
        """Comprehensive Wi-Fi environment analysis."""
        print("🔍 Analyzing Wi-Fi environment...")
        
        # Start Wi-Fi scanning
        self.wifi_analyzer.start_scanning(
            scan_interval=15000,  # 15 seconds
            enable_security_analysis=True,
            enable_channel_analysis=True
        )
        
        # Collect data for 3 minutes
        print("📡 Collecting Wi-Fi data (3 minutes)...")
        time.sleep(180)
        
        # Get analysis results
        networks = self.wifi_analyzer.get_networks()
        
        print(f"\n📊 Found {len(networks)} Wi-Fi networks")
        print("\n🏠 Your Networks:")
        
        # Identify your networks (strongest signals typically)
        your_networks = [n for n in networks if n['signal_strength'] > -50]
        
        for network in your_networks:
            print(f"  • {network['ssid']}: {network['signal_strength']} dBm, "
                  f"Channel {network['channel']}, {network['security_type']}")
        
        # Analyze 2.4GHz band
        print("\n📶 2.4GHz Channel Analysis:")
        channel_analysis_24 = self.wifi_analyzer.analyze_channels("2.4GHz")
        self._print_channel_analysis(channel_analysis_24, "2.4GHz")
        
        # Analyze 5GHz band
        print("\n📶 5GHz Channel Analysis:")
        channel_analysis_5 = self.wifi_analyzer.analyze_channels("5GHz")
        self._print_channel_analysis(channel_analysis_5, "5GHz")
        
        # Get recommendations
        recommendations_24 = self.wifi_analyzer.get_channel_recommendations("2.4GHz")
        recommendations_5 = self.wifi_analyzer.get_channel_recommendations("5GHz")
        
        print(f"\n💡 Recommended Channels:")
        print(f"  • 2.4GHz: {recommendations_24}")
        print(f"  • 5GHz: {recommendations_5}")
        
        self.wifi_analyzer.stop_scanning()
        
        return {
            'networks': networks,
            'channel_analysis_24': channel_analysis_24,
            'channel_analysis_5': channel_analysis_5,
            'recommendations': {
                '2.4GHz': recommendations_24,
                '5GHz': recommendations_5
            }
        }
    
    def _print_channel_analysis(self, analysis, band):
        """Print channel analysis results."""
        for channel, data in analysis.get('channels', {}).items():
            utilization = data.get('utilization', 0)
            network_count = data.get('network_count', 0)
            
            status = "🟢 Good"
            if utilization > 70:
                status = "🔴 Congested"
            elif utilization > 40:
                status = "🟡 Busy"
            
            print(f"  Channel {channel}: {utilization:.1f}% utilization, "
                  f"{network_count} networks {status}")
    
    def test_internet_speed(self):
        """Test internet connection speed."""
        print("\n🚀 Testing Internet Speed...")
        
        # Start bandwidth monitoring
        self.bandwidth_monitor.start_monitoring(interface="auto", interval=1000)
        
        print("📊 Monitoring for 30 seconds...")
        time.sleep(30)
        
        # Get speed data
        current_data = self.bandwidth_monitor.get_current_data()
        
        print(f"\n📈 Speed Test Results:")
        print(f"  • Download: {current_data.get('download_speed', 0):.1f} Mbps")
        print(f"  • Upload: {current_data.get('upload_speed', 0):.1f} Mbps")
        
        self.bandwidth_monitor.stop_monitoring()
        
        return current_data
    
    def generate_optimization_report(self):
        """Generate comprehensive optimization report."""
        print("\n🔧 Generating Network Optimization Report...")
        
        # Analyze Wi-Fi environment
        wifi_analysis = self.analyze_wifi_environment()
        
        # Test internet speed
        speed_test = self.test_internet_speed()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(wifi_analysis, speed_test)
        
        # Create report
        report = {
            'timestamp': datetime.now().isoformat(),
            'wifi_analysis': wifi_analysis,
            'speed_test': speed_test,
            'recommendations': recommendations
        }
        
        # Save report
        filename = f"home_network_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            import json
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved as: {filename}")
        
        # Print summary
        self._print_optimization_summary(recommendations)
        
        return report
    
    def _generate_recommendations(self, wifi_analysis, speed_test):
        """Generate optimization recommendations."""
        recommendations = []
        
        # Channel recommendations
        if wifi_analysis['recommendations']['2.4GHz']:
            recommendations.append({
                'category': 'Wi-Fi Channels',
                'priority': 'High',
                'action': f"Change 2.4GHz channel to {wifi_analysis['recommendations']['2.4GHz'][0]}",
                'reason': 'Reduce interference and improve performance'
            })
        
        if wifi_analysis['recommendations']['5GHz']:
            recommendations.append({
                'category': 'Wi-Fi Channels',
                'priority': 'High',
                'action': f"Use 5GHz channel {wifi_analysis['recommendations']['5GHz'][0]}",
                'reason': 'Better performance and less congestion'
            })
        
        # Speed recommendations
        download_speed = speed_test.get('download_speed', 0)
        if download_speed < 25:
            recommendations.append({
                'category': 'Internet Speed',
                'priority': 'Medium',
                'action': 'Consider upgrading internet plan',
                'reason': f'Current speed ({download_speed:.1f} Mbps) may be insufficient for modern usage'
            })
        
        # Security recommendations
        networks = wifi_analysis['networks']
        open_networks = [n for n in networks if n.get('security_type') == 'Open']
        if open_networks:
            recommendations.append({
                'category': 'Security',
                'priority': 'High',
                'action': 'Secure open networks with WPA3',
                'reason': f'Found {len(open_networks)} unsecured networks'
            })
        
        return recommendations
    
    def _print_optimization_summary(self, recommendations):
        """Print optimization summary."""
        print("\n🎯 Optimization Recommendations:")
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
            print(f"\n{i}. {priority_icon} {rec['category']} ({rec['priority']} Priority)")
            print(f"   Action: {rec['action']}")
            print(f"   Reason: {rec['reason']}")

# Usage
optimizer = HomeNetworkOptimizer()
report = optimizer.generate_optimization_report()
```

## 🔄 Automated Network Monitoring

### Scenario: Continuous Network Health Monitoring

Set up continuous monitoring with automated alerting and reporting.

```python
from network_connectivity.tools.bandwidth_monitor import BandwidthMonitor
from network_connectivity.tools.port_scanner import PortScanner
from network_connectivity.core.notification_service import get_notification_service
from network_connectivity.core.logging_service import get_logging_service
import threading
import time
from datetime import datetime, timedelta

class ContinuousNetworkMonitor:
    def __init__(self):
        self.bandwidth_monitor = BandwidthMonitor()
        self.port_scanner = PortScanner()
        self.notification_service = get_notification_service()
        self.logger = get_logging_service().get_logger('ContinuousMonitor')
        
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Configure notifications
        self.notification_service.configure_email({
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password',
            'from_address': 'your-email@gmail.com',
            'to_addresses': ['admin@company.com']
        })
    
    def start_monitoring(self, config):
        """Start continuous network monitoring."""
        self.monitoring_active = True
        self.config = config
        
        # Start bandwidth monitoring
        self.bandwidth_monitor.start_monitoring(
            interface=config.get('interface', 'auto'),
            interval=config.get('bandwidth_interval', 5000)
        )
        
        # Configure bandwidth alerts
        self.bandwidth_monitor.configure_alert(
            alert_type="speed_threshold",
            threshold=config.get('speed_threshold', 50),
            direction="download",
            callback=self._handle_bandwidth_alert
        )
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Continuous network monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
        self.bandwidth_monitor.stop_monitoring()
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("Continuous network monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        last_connectivity_check = datetime.now()
        last_security_scan = datetime.now()
        last_report = datetime.now()
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                # Connectivity check every 5 minutes
                if (current_time - last_connectivity_check).total_seconds() > 300:
                    self._check_connectivity()
                    last_connectivity_check = current_time
                
                # Security scan every hour
                if (current_time - last_security_scan).total_seconds() > 3600:
                    self._perform_security_scan()
                    last_security_scan = current_time
                
                # Generate report every 24 hours
                if (current_time - last_report).total_seconds() > 86400:
                    self._generate_daily_report()
                    last_report = current_time
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _check_connectivity(self):
        """Check connectivity to critical services."""
        critical_hosts = self.config.get('critical_hosts', [
            '8.8.8.8',  # Google DNS
            '1.1.1.1',  # Cloudflare DNS
            'google.com',
            'github.com'
        ])
        
        connectivity_issues = []
        
        for host in critical_hosts:
            try:
                # Quick connectivity test
                result = self.port_scanner.scan(
                    target=host,
                    ports="80,443",
                    scan_type="tcp_connect",
                    timeout=5000
                )
                
                if not any(port_data['state'] == 'open' 
                          for port_data in result.get('ports', {}).values()):
                    connectivity_issues.append(host)
                    
            except Exception as e:
                connectivity_issues.append(f"{host} (error: {e})")
        
        if connectivity_issues:
            self._send_alert(
                "Connectivity Issues Detected",
                f"Cannot reach: {', '.join(connectivity_issues)}",
                level="warning"
            )
    
    def _perform_security_scan(self):
        """Perform periodic security scan."""
        gateway_ip = self.config.get('gateway_ip', '192.168.1.1')
        
        try:
            # Scan gateway for security issues
            scan_result = self.port_scanner.scan(
                target=gateway_ip,
                ports="21,22,23,25,53,80,135,139,443,445,993,995,3389,5900",
                scan_type="tcp_syn",
                enable_service_detection=True
            )
            
            # Analyze for security concerns
            security_analysis = self.port_scanner.analyze_security(scan_result)
            
            if security_analysis['score'] < 70:
                self._send_alert(
                    "Security Concern Detected",
                    f"Gateway security score: {security_analysis['score']}/100. "
                    f"Issues: {', '.join(security_analysis.get('issues', []))}",
                    level="warning"
                )
                
        except Exception as e:
            self.logger.error(f"Security scan failed: {e}")
    
    def _generate_daily_report(self):
        """Generate daily monitoring report."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        # Get bandwidth statistics
        bandwidth_stats = self.bandwidth_monitor.get_usage_statistics(start_time, end_time)
        
        # Get health status
        health_status = self.bandwidth_monitor.get_health_status()
        
        report_content = f"""
        Daily Network Monitoring Report
        Date: {end_time.strftime('%Y-%m-%d')}
        
        Bandwidth Usage:
        - Total Download: {bandwidth_stats.get('total_download_bytes', 0) / (1024**3):.2f} GB
        - Total Upload: {bandwidth_stats.get('total_upload_bytes', 0) / (1024**3):.2f} GB
        - Peak Download Speed: {bandwidth_stats.get('peak_download_speed', 0):.1f} Mbps
        - Peak Upload Speed: {bandwidth_stats.get('peak_upload_speed', 0):.1f} Mbps
        - Average Download Speed: {bandwidth_stats.get('avg_download_speed', 0):.1f} Mbps
        - Average Upload Speed: {bandwidth_stats.get('avg_upload_speed', 0):.1f} Mbps
        
        System Health:
        - Uptime: {health_status.get('uptime_percentage', 0):.1f}%
        - Alerts Generated: {bandwidth_stats.get('alert_count', 0)}
        - Last Error: {health_status.get('last_error', 'None')}
        """
        
        # Send report via email
        self.notification_service.send_notification(
            title="Daily Network Report",
            message=report_content,
            level="info",
            method="email"
        )
        
        # Export detailed data
        self.bandwidth_monitor.export_data(
            start_time=start_time,
            end_time=end_time,
            format="csv",
            filename=f"daily_bandwidth_{end_time.strftime('%Y%m%d')}.csv"
        )
    
    def _handle_bandwidth_alert(self, alert_data):
        """Handle bandwidth threshold alerts."""
        self._send_alert(
            "Bandwidth Alert",
            f"Speed dropped below threshold: {alert_data['current_speed']:.1f} Mbps "
            f"(threshold: {alert_data['threshold']:.1f} Mbps)",
            level="warning"
        )
    
    def _send_alert(self, title, message, level="info"):
        """Send alert notification."""
        self.notification_service.send_notification(