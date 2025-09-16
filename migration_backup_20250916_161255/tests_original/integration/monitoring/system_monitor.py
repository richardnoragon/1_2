#!/usr/bin/env python3
"""
Monitoring and Alerting System for RFU Integration Testing
Phase 1: Foundation Setup - Comprehensive System Monitoring

This script provides real-time monitoring of test environments, performance metrics,
and automated alerting for critical issues.
"""

import json
import logging
import os
import queue
import smtplib
import sqlite3
import sys
import threading
import time
from datetime import datetime, timedelta
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil
import requests
import yaml


class SystemMonitor:
    """Comprehensive system monitoring for RFU integration testing."""
    
    def __init__(self, config_path: str = None):
        self.base_path = Path(__file__).parent.parent
        self.config_path = config_path or self.base_path / "configs" / "monitoring_config.yaml"
        self.monitoring_data_path = self.base_path / "monitoring"
        self.monitoring_data_path.mkdir(exist_ok=True)
        
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.metrics_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        self.running = False
        
        # Monitoring threads
        self.monitor_thread = None
        self.alert_thread = None
        
        # Thresholds and settings
        self.thresholds = self.config.get('thresholds', {})
        self.alert_settings = self.config.get('alerting', {})
        
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            'monitoring': {
                'interval': 60,
                'metrics': ['cpu', 'memory', 'disk', 'network', 'database'],
                'environments': ['dev', 'staging', 'prod-like']
            },
            'thresholds': {
                'cpu_percent': 80,
                'memory_percent': 85,
                'disk_percent': 90,
                'response_time_ms': 5000,
                'error_rate_percent': 5
            },
            'alerting': {
                'enabled': True,
                'email': {
                    'enabled': False,
                    'smtp_server': 'localhost',
                    'smtp_port': 587,
                    'recipients': []
                },
                'webhook': {
                    'enabled': False,
                    'url': '',
                    'timeout': 30
                }
            },
            'retention': {
                'metrics_days': 30,
                'alerts_days': 90
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Set up comprehensive logging for monitoring."""
        logger = logging.getLogger("SystemMonitor")
        logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # File handler
        log_file = self.base_path / "logs" / "system_monitor.log"
        log_file.parent.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def start_monitoring(self):
        """Start the monitoring system."""
        self.logger.info("Starting system monitoring...")
        
        self.running = True
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        # Start alerting thread
        self.alert_thread = threading.Thread(target=self._alerting_loop, daemon=True)
        self.alert_thread.start()
        
        self.logger.info("System monitoring started successfully")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.logger.info("Stopping system monitoring...")
        
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        if self.alert_thread and self.alert_thread.is_alive():
            self.alert_thread.join(timeout=5)
        
        self.logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        interval = self.config.get('monitoring', {}).get('interval', 60)
        
        while self.running:
            try:
                timestamp = datetime.now()
                
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                
                # Collect environment metrics
                env_metrics = self._collect_environment_metrics()
                
                # Collect database metrics
                db_metrics = self._collect_database_metrics()
                
                # Combine all metrics
                all_metrics = {
                    'timestamp': timestamp.isoformat(),
                    'system': system_metrics,
                    'environments': env_metrics,
                    'databases': db_metrics
                }
                
                # Store metrics
                self._store_metrics(all_metrics)
                
                # Check thresholds and generate alerts
                self._check_thresholds(all_metrics)
                
                # Log summary
                self.logger.debug(f"Collected metrics at {timestamp}")
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            # Wait for next interval
            time.sleep(interval)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except (PermissionError, OSError):
                    continue
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': load_avg
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': disk_usage,
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': {
                    'count': process_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def _collect_environment_metrics(self) -> Dict[str, Any]:
        """Collect environment-specific metrics."""
        environments = self.config.get('monitoring', {}).get('environments', [])
        env_metrics = {}
        
        for env_name in environments:
            try:
                env_path = self.base_path / "data" / env_name
                
                if not env_path.exists():
                    env_metrics[env_name] = {'status': 'not_created'}
                    continue
                
                # File count and disk usage
                file_count = 0
                total_size = 0
                
                for root, dirs, files in os.walk(env_path):
                    file_count += len(files)
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                        except (OSError, IOError):
                            continue
                
                # Check if environment is healthy
                status_file = self.base_path / "artifacts" / env_name / "environment_status.json"
                env_status = 'unknown'
                
                if status_file.exists():
                    with open(status_file, 'r') as f:
                        status_data = json.load(f)
                        env_status = status_data.get('status', 'unknown')
                
                env_metrics[env_name] = {
                    'status': env_status,
                    'file_count': file_count,
                    'size_bytes': total_size,
                    'size_mb': round(total_size / (1024**2), 2),
                    'path_exists': True
                }
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics for environment {env_name}: {e}")
                env_metrics[env_name] = {'status': 'error', 'error': str(e)}
        
        return env_metrics
    
    def _collect_database_metrics(self) -> Dict[str, Any]:
        """Collect database metrics for all environments."""
        environments = self.config.get('monitoring', {}).get('environments', [])
        db_metrics = {}
        
        for env_name in environments:
            try:
                db_path = self.base_path.parent / f"tests/integration/data/test_{env_name}.db"
                
                if not db_path.exists():
                    db_metrics[env_name] = {'status': 'not_found'}
                    continue
                
                # Database size
                db_size = os.path.getsize(db_path)
                
                # Connect and get table statistics
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Get table counts
                tables = {}
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = [row[0] for row in cursor.fetchall()]
                
                for table_name in table_names:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        tables[table_name] = count
                    except sqlite3.Error:
                        tables[table_name] = -1
                
                # Database integrity check
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                integrity_ok = integrity_result == "ok"
                
                # Page count and page size
                cursor.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                
                cursor.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                
                conn.close()
                
                db_metrics[env_name] = {
                    'status': 'healthy' if integrity_ok else 'corrupted',
                    'size_bytes': db_size,
                    'size_mb': round(db_size / (1024**2), 2),
                    'tables': tables,
                    'total_records': sum(count for count in tables.values() if count >= 0),
                    'integrity_ok': integrity_ok,
                    'page_count': page_count,
                    'page_size': page_size
                }
                
            except Exception as e:
                self.logger.error(f"Error collecting database metrics for {env_name}: {e}")
                db_metrics[env_name] = {'status': 'error', 'error': str(e)}
        
        return db_metrics
    
    def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics to file for historical analysis."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        metrics_file = self.monitoring_data_path / f"metrics_{timestamp}.json"
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Also store in a rolling log file
        daily_log = self.monitoring_data_path / f"metrics_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(daily_log, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
        
        # Cleanup old metrics based on retention policy
        self._cleanup_old_metrics()
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics files based on retention policy."""
        retention_days = self.config.get('retention', {}).get('metrics_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for metrics_file in self.monitoring_data_path.glob("metrics_*.json"):
            try:
                # Extract date from filename
                date_str = metrics_file.stem.split('_')[1]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date < cutoff_date:
                    metrics_file.unlink()
                    self.logger.debug(f"Cleaned up old metrics file: {metrics_file}")
                    
            except (ValueError, IndexError):
                # Skip files that don't match the expected format
                continue
    
    def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check metrics against thresholds and generate alerts."""
        alerts = []
        
        # Check system thresholds
        system_metrics = metrics.get('system', {})
        
        # CPU threshold
        cpu_percent = system_metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent > self.thresholds.get('cpu_percent', 80):
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'metric': 'cpu_percent',
                'value': cpu_percent,
                'threshold': self.thresholds.get('cpu_percent'),
                'message': f"High CPU usage: {cpu_percent}%"
            })
        
        # Memory threshold
        memory_percent = system_metrics.get('memory', {}).get('percent', 0)
        if memory_percent > self.thresholds.get('memory_percent', 85):
            alerts.append({
                'type': 'system',
                'severity': 'warning',
                'metric': 'memory_percent',
                'value': memory_percent,
                'threshold': self.thresholds.get('memory_percent'),
                'message': f"High memory usage: {memory_percent}%"
            })
        
        # Disk threshold
        for device, disk_info in system_metrics.get('disk', {}).items():
            disk_percent = disk_info.get('percent', 0)
            if disk_percent > self.thresholds.get('disk_percent', 90):
                alerts.append({
                    'type': 'system',
                    'severity': 'critical',
                    'metric': 'disk_percent',
                    'value': disk_percent,
                    'threshold': self.thresholds.get('disk_percent'),
                    'message': f"High disk usage on {device}: {disk_percent}%"
                })
        
        # Check environment thresholds
        env_metrics = metrics.get('environments', {})
        for env_name, env_data in env_metrics.items():
            if env_data.get('status') == 'error':
                alerts.append({
                    'type': 'environment',
                    'severity': 'critical',
                    'metric': 'environment_status',
                    'environment': env_name,
                    'message': f"Environment {env_name} has errors: {env_data.get('error', 'Unknown error')}"
                })
        
        # Check database thresholds
        db_metrics = metrics.get('databases', {})
        for env_name, db_data in db_metrics.items():
            if not db_data.get('integrity_ok', True):
                alerts.append({
                    'type': 'database',
                    'severity': 'critical',
                    'metric': 'database_integrity',
                    'environment': env_name,
                    'message': f"Database integrity check failed for {env_name}"
                })
        
        # Queue alerts for processing
        for alert in alerts:
            alert['timestamp'] = datetime.now().isoformat()
            self.alert_queue.put(alert)
    
    def _alerting_loop(self):
        """Process alerts and send notifications."""
        while self.running:
            try:
                # Get alert from queue (blocking with timeout)
                alert = self.alert_queue.get(timeout=1)
                
                # Process the alert
                self._process_alert(alert)
                
                # Mark task as done
                self.alert_queue.task_done()
                
            except queue.Empty:
                # No alerts to process
                continue
            except Exception as e:
                self.logger.error(f"Error in alerting loop: {e}")
    
    def _process_alert(self, alert: Dict[str, Any]):
        """Process and send an alert."""
        self.logger.warning(f"ALERT: {alert['message']}")
        
        # Store alert
        self._store_alert(alert)
        
        # Send notifications
        if self.alert_settings.get('enabled', True):
            self._send_alert_notifications(alert)
    
    def _store_alert(self, alert: Dict[str, Any]):
        """Store alert for historical tracking."""
        alerts_dir = self.monitoring_data_path / "alerts"
        alerts_dir.mkdir(exist_ok=True)
        
        # Store in daily alert log
        daily_alerts = alerts_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(daily_alerts, 'a') as f:
            f.write(json.dumps(alert) + '\n')
    
    def _send_alert_notifications(self, alert: Dict[str, Any]):
        """Send alert notifications via configured channels."""
        # Email notifications
        if self.alert_settings.get('email', {}).get('enabled', False):
            try:
                self._send_email_alert(alert)
            except Exception as e:
                self.logger.error(f"Failed to send email alert: {e}")
        
        # Webhook notifications
        if self.alert_settings.get('webhook', {}).get('enabled', False):
            try:
                self._send_webhook_alert(alert)
            except Exception as e:
                self.logger.error(f"Failed to send webhook alert: {e}")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send alert via email."""
        email_config = self.alert_settings.get('email', {})
        
        smtp_server = email_config.get('smtp_server', 'localhost')
        smtp_port = email_config.get('smtp_port', 587)
        username = email_config.get('username')
        password = email_config.get('password')
        recipients = email_config.get('recipients', [])
        
        if not recipients:
            return
        
        # Create message
        subject = f"RFU Monitoring Alert: {alert['severity'].upper()} - {alert['metric']}"
        
        body = f"""
RFU Integration Testing Monitoring Alert

Alert Details:
- Type: {alert['type']}
- Severity: {alert['severity']}
- Metric: {alert['metric']}
- Message: {alert['message']}
- Timestamp: {alert['timestamp']}

Environment: {alert.get('environment', 'System')}
Value: {alert.get('value', 'N/A')}
Threshold: {alert.get('threshold', 'N/A')}

This is an automated alert from the RFU Integration Testing monitoring system.
        """
        
        msg = MimeMultipart()
        msg['From'] = email_config.get('from_address', 'rfu-monitoring@localhost')
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MimeText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        if username and password:
            server.starttls()
            server.login(username, password)
        
        server.send_message(msg)
        server.quit()
        
        self.logger.info(f"Email alert sent to {len(recipients)} recipients")
    
    def _send_webhook_alert(self, alert: Dict[str, Any]):
        """Send alert via webhook."""
        webhook_config = self.alert_settings.get('webhook', {})
        
        webhook_url = webhook_config.get('url')
        timeout = webhook_config.get('timeout', 30)
        
        if not webhook_url:
            return
        
        # Prepare payload
        payload = {
            'alert': alert,
            'source': 'rfu-integration-testing',
            'timestamp': alert['timestamp']
        }
        
        # Send webhook
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
        response.raise_for_status()
        
        self.logger.info(f"Webhook alert sent to {webhook_url}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics on demand."""
        timestamp = datetime.now()
        
        return {
            'timestamp': timestamp.isoformat(),
            'system': self._collect_system_metrics(),
            'environments': self._collect_environment_metrics(),
            'databases': self._collect_database_metrics()
        }
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = []
        
        # Read from daily log files
        for log_file in self.monitoring_data_path.glob("metrics_*.jsonl"):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        metrics = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(metrics['timestamp'])
                        
                        if timestamp >= cutoff_time:
                            history.append(metrics)
            except (json.JSONDecodeError, ValueError, KeyError):
                continue
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        return history
    
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = []
        
        alerts_dir = self.monitoring_data_path / "alerts"
        if not alerts_dir.exists():
            return alerts
        
        # Read from daily alert files
        for alert_file in alerts_dir.glob("alerts_*.jsonl"):
            try:
                with open(alert_file, 'r') as f:
                    for line in f:
                        alert = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(alert['timestamp'])
                        
                        if timestamp >= cutoff_time:
                            alerts.append(alert)
            except (json.JSONDecodeError, ValueError, KeyError):
                continue
        
        # Sort by timestamp
        alerts.sort(key=lambda x: x['timestamp'])
        
        return alerts

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RFU Integration Test System Monitor')
    parser.add_argument('action', choices=['start', 'status', 'history', 'alerts'],
                       help='Action to perform')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--hours', type=int, default=24,
                       help='Hours of history to show (for history/alerts commands)')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (for start command)')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = SystemMonitor(args.config)
    
    if args.action == 'start':
        monitor.start_monitoring()
        
        if args.daemon:
            # Run as daemon
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\nShutting down monitor...")
                monitor.stop_monitoring()
        else:
            # Run for a short time and show current status
            time.sleep(5)
            metrics = monitor.get_current_metrics()
            print(json.dumps(metrics, indent=2))
            monitor.stop_monitoring()
    
    elif args.action == 'status':
        metrics = monitor.get_current_metrics()
        print("Current System Status:")
        print("=" * 50)
        
        # System metrics
        system = metrics['system']
        print(f"CPU: {system['cpu']['percent']:.1f}%")
        print(f"Memory: {system['memory']['percent']:.1f}%")
        print(f"Processes: {system['processes']['count']}")
        
        # Environment status
        print("\nEnvironments:")
        for env_name, env_data in metrics['environments'].items():
            status = env_data.get('status', 'unknown')
            size_mb = env_data.get('size_mb', 0)
            print(f"  {env_name}: {status} ({size_mb:.1f} MB)")
        
        # Database status
        print("\nDatabases:")
        for env_name, db_data in metrics['databases'].items():
            status = db_data.get('status', 'unknown')
            size_mb = db_data.get('size_mb', 0)
            print(f"  {env_name}: {status} ({size_mb:.1f} MB)")
    
    elif args.action == 'history':
        history = monitor.get_metrics_history(args.hours)
        print(f"Metrics History (last {args.hours} hours):")
        print("=" * 50)
        
        for metrics in history[-10:]:  # Show last 10 entries
            timestamp = metrics['timestamp']
            cpu = metrics['system']['cpu']['percent']
            memory = metrics['system']['memory']['percent']
            print(f"{timestamp}: CPU={cpu:.1f}%, Memory={memory:.1f}%")
    
    elif args.action == 'alerts':
        alerts = monitor.get_alert_history(args.hours)
        print(f"Alert History (last {args.hours} hours):")
        print("=" * 50)
        
        if not alerts:
            print("No alerts in the specified time period.")
        else:
            for alert in alerts:
                timestamp = alert['timestamp']
                severity = alert['severity']
                message = alert['message']
                print(f"{timestamp} [{severity.upper()}]: {message}")

if __name__ == "__main__":
    main()