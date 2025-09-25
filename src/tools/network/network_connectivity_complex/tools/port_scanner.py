"""Port Scanner tool for comprehensive network port scanning and security analysis."""

import socket
import struct
import threading
import time
import json
import csv
import ipaddress
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from ..core.network_base import (
    NetworkToolBase,
    NetworkOperationResult,
    NetworkAlertLevel,
)
from ..core.security_validator import (
    SecurityValidator,
    SecurityLevel,
    ValidationResult,
)
from ..core.platform_network import PlatformNetworkDetector


class ScanType(Enum):
    """Port scan types."""

    TCP_CONNECT = "tcp_connect"
    TCP_SYN = "tcp_syn"
    TCP_FIN = "tcp_fin"
    TCP_NULL = "tcp_null"
    TCP_XMAS = "tcp_xmas"
    UDP = "udp"


class PortState(Enum):
    """Port states."""

    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    OPEN_FILTERED = "open|filtered"
    CLOSED_FILTERED = "closed|filtered"
    UNKNOWN = "unknown"


class ScanPolicy(Enum):
    """Scanning policies for compliance and stealth."""

    AGGRESSIVE = "aggressive"
    NORMAL = "normal"
    POLITE = "polite"
    STEALTH = "stealth"


@dataclass
class PortInfo:
    """Information about a scanned port."""

    port: int
    protocol: str
    state: PortState
    service: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None
    response_time: Optional[float] = None
    confidence: float = 0.0
    extra_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_info is None:
            self.extra_info = {}


@dataclass
class ScanTarget:
    """Scan target specification."""

    host: str
    ports: List[int]
    scan_type: ScanType
    timeout: float = 3.0
    resolved_ip: Optional[str] = None


@dataclass
class ScanResult:
    """Complete scan result for a target."""

    target: str
    scan_type: ScanType
    start_time: datetime
    end_time: Optional[datetime]
    ports: List[PortInfo]
    total_ports: int
    open_ports: int
    closed_ports: int
    filtered_ports: int
    scan_duration: Optional[float] = None
    error_message: Optional[str] = None
    vulnerabilities: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.vulnerabilities is None:
            self.vulnerabilities = []
        if self.end_time and self.scan_duration is None:
            self.scan_duration = (
                self.end_time - self.start_time
            ).total_seconds()


@dataclass
class VulnerabilityInfo:
    """Vulnerability information."""

    cve_id: Optional[str]
    severity: str
    description: str
    service: str
    port: int
    recommendation: str
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []


class ServiceDetector:
    """Service detection and banner grabbing engine."""

    def __init__(self):
        """Initialize service detector."""
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.PortScanner.ServiceDetector"
        )

        # Common service signatures
        self.service_signatures = {
            21: {"service": "ftp", "banner_regex": r"220.*FTP"},
            22: {"service": "ssh", "banner_regex": r"SSH-[\d\.]+-(.+)"},
            23: {"service": "telnet", "banner_regex": r".*login:.*"},
            25: {"service": "smtp", "banner_regex": r"220.*SMTP"},
            53: {"service": "dns", "banner_regex": None},
            80: {"service": "http", "banner_regex": r"Server: (.+)"},
            110: {"service": "pop3", "banner_regex": r"\+OK.*POP3"},
            135: {"service": "msrpc", "banner_regex": None},
            139: {"service": "netbios-ssn", "banner_regex": None},
            143: {"service": "imap", "banner_regex": r"\* OK.*IMAP"},
            443: {"service": "https", "banner_regex": r"Server: (.+)"},
            445: {"service": "microsoft-ds", "banner_regex": None},
            993: {"service": "imaps", "banner_regex": None},
            995: {"service": "pop3s", "banner_regex": None},
            1433: {"service": "ms-sql-s", "banner_regex": None},
            1521: {"service": "oracle", "banner_regex": None},
            3306: {"service": "mysql", "banner_regex": None},
            3389: {"service": "ms-wbt-server", "banner_regex": None},
            5432: {"service": "postgresql", "banner_regex": None},
            5900: {"service": "vnc", "banner_regex": r"RFB (\d+\.\d+)"},
            6379: {"service": "redis", "banner_regex": None},
            8080: {"service": "http-proxy", "banner_regex": r"Server: (.+)"},
        }

    def detect_service(
        self, host: str, port: int, timeout: float = 3.0
    ) -> PortInfo:
        """Detect service running on a port.

        Args:
            host: Target host
            port: Target port
            timeout: Connection timeout

        Returns:
            PortInfo with service detection results
        """
        port_info = PortInfo(
            port=port, protocol="tcp", state=PortState.OPEN, confidence=0.0
        )

        try:
            # Get basic service info from port number
            if port in self.service_signatures:
                port_info.service = self.service_signatures[port]["service"]
                port_info.confidence = 0.5

            # Attempt banner grabbing
            banner = self._grab_banner(host, port, timeout)
            if banner:
                port_info.banner = banner
                port_info.confidence = 0.8

                # Analyze banner for service/version info
                service_info = self._analyze_banner(port, banner)
                if service_info:
                    port_info.service = service_info.get(
                        "service", port_info.service
                    )
                    port_info.version = service_info.get("version")
                    port_info.confidence = 0.9

            # Special handling for HTTP services
            if port in [80, 443, 8080, 8443] or (
                port_info.service and "http" in port_info.service
            ):
                http_info = self._probe_http_service(host, port, timeout)
                if http_info:
                    port_info.service = http_info.get(
                        "service", port_info.service
                    )
                    port_info.version = http_info.get(
                        "version", port_info.version
                    )
                    port_info.extra_info.update(http_info.get("extra", {}))
                    port_info.confidence = max(port_info.confidence, 0.8)

        except Exception as e:
            self.logger.debug(
                f"Service detection error for {host}:{port}: {e}"
            )

        return port_info

    def _grab_banner(
        self, host: str, port: int, timeout: float
    ) -> Optional[str]:
        """Grab banner from a service."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Send a generic probe
            try:
                sock.send(b"\r\n")
            except:
                pass

            # Try to receive banner
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            sock.close()

            return banner if banner else None

        except Exception:
            return None

    def _analyze_banner(
        self, port: int, banner: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze banner to extract service information."""
        if not banner:
            return None

        service_info = {}

        # Check against known signatures
        if port in self.service_signatures:
            sig = self.service_signatures[port]
            if sig["banner_regex"]:
                match = re.search(sig["banner_regex"], banner, re.IGNORECASE)
                if match:
                    service_info["service"] = sig["service"]
                    if match.groups():
                        service_info["version"] = match.group(1)

        # Generic patterns
        patterns = [
            (r"SSH-([\d\.]+-\S+)", "ssh"),
            (r"220.*FTP.*", "ftp"),
            (r"220.*SMTP.*", "smtp"),
            (r"\+OK.*POP3.*", "pop3"),
            (r"\* OK.*IMAP.*", "imap"),
            (r"HTTP/[\d\.]+ \d+", "http"),
            (r"Server: (.+)", "http"),
            (r"Apache/([\d\.]+)", "apache"),
            (r"nginx/([\d\.]+)", "nginx"),
            (r"Microsoft-IIS/([\d\.]+)", "iis"),
        ]

        for pattern, service in patterns:
            match = re.search(pattern, banner, re.IGNORECASE)
            if match:
                service_info["service"] = service
                if match.groups():
                    service_info["version"] = match.group(1)
                break

        return service_info if service_info else None

    def _probe_http_service(
        self, host: str, port: int, timeout: float
    ) -> Optional[Dict[str, Any]]:
        """Probe HTTP service for detailed information."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Send HTTP GET request
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: NetworkConnectivity-Scanner/1.0\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())

            # Receive response
            response = b""
            while True:
                try:
                    data = sock.recv(4096)
                    if not data:
                        break
                    response += data
                    if len(response) > 8192:  # Limit response size
                        break
                except socket.timeout:
                    break

            sock.close()

            if response:
                return self._parse_http_response(
                    response.decode("utf-8", errors="ignore")
                )

        except Exception:
            pass

        return None

    def _parse_http_response(self, response: str) -> Dict[str, Any]:
        """Parse HTTP response for service information."""
        info = {"service": "http", "extra": {}}

        lines = response.split("\n")
        if not lines:
            return info

        # Parse status line
        status_line = lines[0].strip()
        if status_line.startswith("HTTP/"):
            parts = status_line.split(" ", 2)
            if len(parts) >= 2:
                info["extra"]["status_code"] = parts[1]
                info["extra"]["http_version"] = parts[0]

        # Parse headers
        headers = {}
        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
            elif line.strip() == "":
                break

        # Extract useful information
        if "server" in headers:
            server = headers["server"]
            info["version"] = server
            info["extra"]["server"] = server

            # Try to identify specific server software
            if "apache" in server.lower():
                info["service"] = "apache"
            elif "nginx" in server.lower():
                info["service"] = "nginx"
            elif "iis" in server.lower():
                info["service"] = "iis"

        if "x-powered-by" in headers:
            info["extra"]["powered_by"] = headers["x-powered-by"]

        if "content-type" in headers:
            info["extra"]["content_type"] = headers["content-type"]

        return info


class VulnerabilityAssessment:
    """Vulnerability assessment engine with CVE integration."""

    def __init__(self):
        """Initialize vulnerability assessment."""
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.PortScanner.VulnerabilityAssessment"
        )

        # Common vulnerability patterns
        self.vulnerability_patterns = {
            "ftp": [
                {
                    "pattern": r"vsftpd 2\.3\.4",
                    "cve": "CVE-2011-2523",
                    "severity": "critical",
                    "description": "vsftpd 2.3.4 backdoor vulnerability",
                    "recommendation": "Upgrade vsftpd to latest version",
                }
            ],
            "ssh": [
                {
                    "pattern": r"OpenSSH_[1-6]\.",
                    "cve": "CVE-2016-0777",
                    "severity": "medium",
                    "description": "OpenSSH client information leak",
                    "recommendation": "Upgrade OpenSSH to version 7.0 or later",
                }
            ],
            "http": [
                {
                    "pattern": r"Apache/2\.2\.",
                    "cve": "CVE-2017-15710",
                    "severity": "medium",
                    "description": "Apache HTTP Server out-of-bounds read",
                    "recommendation": "Upgrade Apache to latest version",
                }
            ],
        }

        # Common insecure configurations
        self.insecure_configs = [
            {
                "service": "ftp",
                "port": 21,
                "check": "anonymous_login",
                "severity": "medium",
                "description": "Anonymous FTP access enabled",
                "recommendation": "Disable anonymous FTP access",
            },
            {
                "service": "telnet",
                "port": 23,
                "check": "unencrypted",
                "severity": "high",
                "description": "Unencrypted Telnet service",
                "recommendation": "Replace Telnet with SSH",
            },
            {
                "service": "http",
                "port": 80,
                "check": "unencrypted_web",
                "severity": "medium",
                "description": "Unencrypted HTTP service",
                "recommendation": "Implement HTTPS with proper certificates",
            },
        ]

    def assess_vulnerabilities(
        self, scan_result: ScanResult
    ) -> List[VulnerabilityInfo]:
        """Assess vulnerabilities in scan results."""
        vulnerabilities = []

        for port_info in scan_result.ports:
            if port_info.state == PortState.OPEN:
                # Check for known vulnerabilities
                vulns = self._check_service_vulnerabilities(port_info)
                vulnerabilities.extend(vulns)

                # Check for insecure configurations
                config_vulns = self._check_insecure_configurations(port_info)
                vulnerabilities.extend(config_vulns)

        return vulnerabilities

    def _check_service_vulnerabilities(
        self, port_info: PortInfo
    ) -> List[VulnerabilityInfo]:
        """Check for known service vulnerabilities."""
        vulnerabilities = []

        if not port_info.service or not port_info.banner:
            return vulnerabilities

        service = port_info.service.lower()
        if service in self.vulnerability_patterns:
            for vuln_pattern in self.vulnerability_patterns[service]:
                if re.search(
                    vuln_pattern["pattern"], port_info.banner, re.IGNORECASE
                ):
                    vulnerability = VulnerabilityInfo(
                        cve_id=vuln_pattern.get("cve"),
                        severity=vuln_pattern["severity"],
                        description=vuln_pattern["description"],
                        service=port_info.service,
                        port=port_info.port,
                        recommendation=vuln_pattern["recommendation"],
                    )
                    vulnerabilities.append(vulnerability)

        return vulnerabilities

    def _check_insecure_configurations(
        self, port_info: PortInfo
    ) -> List[VulnerabilityInfo]:
        """Check for insecure service configurations."""
        vulnerabilities = []

        for config in self.insecure_configs:
            if port_info.port == config["port"] or (
                port_info.service
                and config["service"].lower() in port_info.service.lower()
            ):

                vulnerability = VulnerabilityInfo(
                    cve_id=None,
                    severity=config["severity"],
                    description=config["description"],
                    service=port_info.service or config["service"],
                    port=port_info.port,
                    recommendation=config["recommendation"],
                )
                vulnerabilities.append(vulnerability)

        return vulnerabilities


class ScanEngine:
    """Core scanning engine with multiple scanning techniques."""

    def __init__(self, security_validator: SecurityValidator):
        """Initialize scan engine."""
        self.security_validator = security_validator
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.PortScanner.ScanEngine"
        )

        # Scanning state
        self._stop_event = threading.Event()
        self._scan_stats = {
            "ports_scanned": 0,
            "ports_open": 0,
            "ports_closed": 0,
            "ports_filtered": 0,
            "scan_errors": 0,
        }

    def scan_target(
        self,
        target: ScanTarget,
        scan_policy: ScanPolicy = ScanPolicy.NORMAL,
        max_threads: int = 50,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> ScanResult:
        """Scan a target with specified parameters."""
        start_time = datetime.now()
        self._reset_stats()

        # Validate target
        validation_result = self.security_validator.validate_scan_target(
            target.host, target.ports
        )

        if validation_result.result == ValidationResult.BLOCKED:
            return ScanResult(
                target=target.host,
                scan_type=target.scan_type,
                start_time=start_time,
                end_time=datetime.now(),
                ports=[],
                total_ports=0,
                open_ports=0,
                closed_ports=0,
                filtered_ports=0,
                error_message=f"Target blocked by security policy: {validation_result.message}",
            )

        # Resolve hostname if needed
        try:
            resolved_ip = socket.gethostbyname(target.host)
            target.resolved_ip = resolved_ip
        except socket.gaierror as e:
            return ScanResult(
                target=target.host,
                scan_type=target.scan_type,
                start_time=start_time,
                end_time=datetime.now(),
                ports=[],
                total_ports=0,
                open_ports=0,
                closed_ports=0,
                filtered_ports=0,
                error_message=f"Failed to resolve hostname: {e}",
            )

        # Apply scan policy timing
        timing_config = self._get_timing_config(scan_policy)
        max_threads = min(max_threads, timing_config["max_threads"])

        # Perform scan
        scanned_ports = []
        total_ports = len(target.ports)

        try:
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                # Submit scan tasks
                future_to_port = {}
                for port in target.ports:
                    if self._stop_event.is_set():
                        break

                    future = executor.submit(
                        self._scan_port,
                        target.resolved_ip,
                        port,
                        target.scan_type,
                        target.timeout,
                        timing_config,
                    )
                    future_to_port[future] = port

                # Collect results
                completed = 0
                for future in as_completed(future_to_port):
                    if self._stop_event.is_set():
                        break

                    port = future_to_port[future]
                    try:
                        port_info = future.result()
                        if port_info:
                            scanned_ports.append(port_info)
                            self._update_stats(port_info.state)
                    except Exception as e:
                        self.logger.error(f"Error scanning port {port}: {e}")
                        self._scan_stats["scan_errors"] += 1

                    completed += 1
                    if progress_callback:
                        progress_callback(
                            completed, total_ports, f"Scanned port {port}"
                        )

        except Exception as e:
            self.logger.error(f"Scan execution error: {e}")

        end_time = datetime.now()

        # Create scan result
        scan_result = ScanResult(
            target=target.host,
            scan_type=target.scan_type,
            start_time=start_time,
            end_time=end_time,
            ports=scanned_ports,
            total_ports=total_ports,
            open_ports=self._scan_stats["ports_open"],
            closed_ports=self._scan_stats["ports_closed"],
            filtered_ports=self._scan_stats["ports_filtered"],
        )

        return scan_result

    def _scan_port(
        self,
        host: str,
        port: int,
        scan_type: ScanType,
        timeout: float,
        timing_config: Dict[str, Any],
    ) -> Optional[PortInfo]:
        """Scan a single port."""
        if self._stop_event.is_set():
            return None

        # Apply scan delay
        if timing_config.get("scan_delay", 0) > 0:
            time.sleep(timing_config["scan_delay"] / 1000.0)

        start_time = time.time()

        try:
            if scan_type == ScanType.TCP_CONNECT:
                state = self._tcp_connect_scan(host, port, timeout)
            elif scan_type == ScanType.UDP:
                state = self._udp_scan(host, port, timeout)
            else:
                # For other scan types, fallback to TCP connect
                state = self._tcp_connect_scan(host, port, timeout)

            response_time = (time.time() - start_time) * 1000  # Convert to ms

            return PortInfo(
                port=port,
                protocol="tcp" if scan_type != ScanType.UDP else "udp",
                state=state,
                response_time=response_time,
            )

        except Exception as e:
            self.logger.debug(f"Port scan error {host}:{port}: {e}")
            return None

    def _tcp_connect_scan(
        self, host: str, port: int, timeout: float
    ) -> PortState:
        """Perform TCP connect scan."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return PortState.OPEN
            else:
                return PortState.CLOSED

        except socket.timeout:
            return PortState.FILTERED
        except Exception:
            return PortState.FILTERED

    def _udp_scan(self, host: str, port: int, timeout: float) -> PortState:
        """Perform UDP scan."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)

            # Send UDP packet
            sock.sendto(b"", (host, port))

            try:
                # Try to receive response
                sock.recvfrom(1024)
                return PortState.OPEN
            except socket.timeout:
                # No response - could be open or filtered
                return PortState.OPEN_FILTERED
            except ConnectionRefusedError:
                return PortState.CLOSED

        except Exception:
            return PortState.FILTERED
        finally:
            try:
                sock.close()
            except:
                pass

    def _get_timing_config(self, scan_policy: ScanPolicy) -> Dict[str, Any]:
        """Get timing configuration for scan policy."""
        configs = {
            ScanPolicy.AGGRESSIVE: {
                "max_threads": 200,
                "scan_delay": 0,
                "timeout_multiplier": 0.5,
            },
            ScanPolicy.NORMAL: {
                "max_threads": 50,
                "scan_delay": 0,
                "timeout_multiplier": 1.0,
            },
            ScanPolicy.POLITE: {
                "max_threads": 10,
                "scan_delay": 100,
                "timeout_multiplier": 1.5,
            },
            ScanPolicy.STEALTH: {
                "max_threads": 5,
                "scan_delay": 1000,
                "timeout_multiplier": 2.0,
            },
        }

        return configs.get(scan_policy, configs[ScanPolicy.NORMAL])

    def _reset_stats(self):
        """Reset scan statistics."""
        self._scan_stats = {
            "ports_scanned": 0,
            "ports_open": 0,
            "ports_closed": 0,
            "ports_filtered": 0,
            "scan_errors": 0,
        }

    def _update_stats(self, port_state: PortState):
        """Update scan statistics."""
        self._scan_stats["ports_scanned"] += 1

        if port_state == PortState.OPEN:
            self._scan_stats["ports_open"] += 1
        elif port_state == PortState.CLOSED:
            self._scan_stats["ports_closed"] += 1
        elif port_state in [
            PortState.FILTERED,
            PortState.OPEN_FILTERED,
            PortState.CLOSED_FILTERED,
        ]:
            self._scan_stats["ports_filtered"] += 1

    def stop_scan(self):
        """Stop the current scan."""
        self._stop_event.set()


class ScanResultManager:
    """Manages scan results storage, analysis, and historical data."""

    def __init__(self, max_results: int = 1000):
        """Initialize scan result manager."""
        self.max_results = max_results
        self.scan_results: List[ScanResult] = []
        self._lock = threading.Lock()
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.PortScanner.ScanResultManager"
        )

    def add_result(self, scan_result: ScanResult):
        """Add a scan result to storage."""
        with self._lock:
            self.scan_results.append(scan_result)

            # Limit stored results
            if len(self.scan_results) > self.max_results:
                self.scan_results = self.scan_results[-self.max_results :]

    def get_results(
        self,
        target: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        scan_type: Optional[ScanType] = None,
    ) -> List[ScanResult]:
        """Get scan results with optional filtering."""
        with self._lock:
            results = self.scan_results.copy()

        # Apply filters
        if target:
            results = [r for r in results if r.target == target]

        if start_time:
            results = [r for r in results if r.start_time >= start_time]

        if end_time:
            results = [r for r in results if r.start_time <= end_time]

        if scan_type:
            results = [r for r in results if r.scan_type == scan_type]

        return results

    def get_statistics(
        self, target: Optional[str] = None, hours: int = 24
    ) -> Dict[str, Any]:
        """Get scan statistics."""
        start_time = datetime.now() - timedelta(hours=hours)
        results = self.get_results(target=target, start_time=start_time)

        if not results:
            return {
                "total_scans": 0,
                "total_targets": 0,
                "total_ports_scanned": 0,
                "total_open_ports": 0,
                "avg_scan_duration": 0.0,
                "most_common_services": [],
                "vulnerability_count": 0,
            }

        # Calculate statistics
        total_scans = len(results)
        unique_targets = len(set(r.target for r in results))
        total_ports_scanned = sum(r.total_ports for r in results)
        total_open_ports = sum(r.open_ports for r in results)

        # Average scan duration
        durations = [r.scan_duration for r in results if r.scan_duration]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        # Most common services
        service_counts = {}
        vulnerability_count = 0

        for result in results:
            vulnerability_count += len(result.vulnerabilities)
            for port in result.ports:
                if port.state == PortState.OPEN and port.service:
                    service = port.service
                    service_counts[service] = (
                        service_counts.get(service, 0) + 1
                    )

        most_common_services = sorted(
            service_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "total_scans": total_scans,
            "total_targets": unique_targets,
            "total_ports_scanned": total_ports_scanned,
            "total_open_ports": total_open_ports,
            "avg_scan_duration": avg_duration,
            "most_common_services": most_common_services,
            "vulnerability_count": vulnerability_count,
        }

    def clear_results(self):
        """Clear all stored results."""
        with self._lock:
            self.scan_results.clear()


class ReportGenerator:
    """Generates comprehensive scan reports in various formats."""

    def __init__(self, result_manager: ScanResultManager):
        """Initialize report generator."""
        self.result_manager = result_manager
        self.logger = logging.getLogger(
            "RFU.NetworkConnectivity.PortScanner.ReportGenerator"
        )

    def generate_json_report(
        self,
        file_path: Path,
        target: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        include_statistics: bool = True,
    ) -> bool:
        """Generate JSON report."""
        try:
            results = self.result_manager.get_results(
                target=target, start_time=start_time, end_time=end_time
            )

            # Convert results to serializable format
            report_data = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "generator": "NetworkConnectivity PortScanner",
                    "version": "1.0",
                    "filters": {
                        "target": target,
                        "start_time": (
                            start_time.isoformat() if start_time else None
                        ),
                        "end_time": end_time.isoformat() if end_time else None,
                    },
                },
                "scan_results": [],
            }

            for result in results:
                result_dict = asdict(result)
                result_dict["start_time"] = result.start_time.isoformat()
                if result.end_time:
                    result_dict["end_time"] = result.end_time.isoformat()

                # Convert vulnerabilities
                if result.vulnerabilities:
                    result_dict["vulnerabilities"] = [
                        asdict(vuln) for vuln in result.vulnerabilities
                    ]

                report_data["scan_results"].append(result_dict)

            # Add statistics if requested
            if include_statistics:
                hours = 24
                if start_time and end_time:
                    hours = int((end_time - start_time).total_seconds() / 3600)

                report_data["statistics"] = self.result_manager.get_statistics(
                    target=target, hours=hours
                )

            # Write report
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(f"Failed to generate JSON report: {e}")
            return False

    def generate_csv_report(
        self,
        file_path: Path,
        target: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> bool:
        """Generate CSV report."""
        try:
            results = self.result_manager.get_results(
                target=target, start_time=start_time, end_time=end_time
            )

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "target",
                    "scan_time",
                    "scan_type",
                    "port",
                    "protocol",
                    "state",
                    "service",
                    "version",
                    "banner",
                    "response_time",
                    "vulnerabilities",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for result in results:
                    for port in result.ports:
                        # Format vulnerabilities
                        vulns = []
                        for vuln in result.vulnerabilities:
                            if vuln.port == port.port:
                                vulns.append(
                                    f"{vuln.severity}: {vuln.description}"
                                )

                        row = {
                            "target": result.target,
                            "scan_time": result.start_time.isoformat(),
                            "scan_type": result.scan_type.value,
                            "port": port.port,
                            "protocol": port.protocol,
                            "state": port.state.value,
                            "service": port.service or "",
                            "version": port.version or "",
                            "banner": port.banner or "",
                            "response_time": port.response_time or "",
                            "vulnerabilities": "; ".join(vulns),
                        }
                        writer.writerow(row)

            return True

        except Exception as e:
            self.logger.error(f"Failed to generate CSV report: {e}")
            return False


class PortScanner(NetworkToolBase):
    """Main port scanner tool with comprehensive scanning and analysis capabilities."""

    def __init__(self):
        """Initialize port scanner."""
        super().__init__("PortScanner")

        # Core components
        self.security_validator = SecurityValidator()
        self.scan_engine = ScanEngine(self.security_validator)
        self.service_detector = ServiceDetector()
        self.vulnerability_assessment = VulnerabilityAssessment()
        self.result_manager = ScanResultManager()
        self.report_generator = ReportGenerator(self.result_manager)

        # Platform detection
        self.platform_detector = PlatformNetworkDetector()

        # Scanning state
        self._current_scan: Optional[ScanResult] = None
        self._scan_thread: Optional[threading.Thread] = None
        self._scan_active = False

        # Load configuration
        self._load_configuration()

    def _load_configuration(self):
        """Load tool configuration."""
        # Get security level
        security_level_str = self.get_tool_config("security_level", "moderate")
        try:
            security_level = SecurityLevel(security_level_str)
            self.security_validator.security_level = security_level
        except ValueError:
            self.logger.warning(
                f"Invalid security level: {security_level_str}"
            )

        # Load scan settings
        self.default_timeout = (
            self.get_tool_config("scan_timeout", 3000) / 1000.0
        )
        self.max_threads = self.get_tool_config("max_threads", 50)
        self.enable_service_detection = self.get_tool_config(
            "enable_service_detection", True
        )
        self.enable_vulnerability_scan = self.get_tool_config(
            "enable_vulnerability_scan", False
        )
        self.save_scan_results = self.get_tool_config(
            "save_scan_results", True
        )

        # Load port lists
        self.common_ports = self.get_tool_config(
            "common_ports",
            [
                21,
                22,
                23,
                25,
                53,
                80,
                110,
                135,
                139,
                143,
                443,
                993,
                995,
                1723,
                3306,
                3389,
                5432,
                5900,
            ],
        )

    def execute_operation(self, **kwargs) -> NetworkOperationResult:
        """Execute port scanning operation."""
        operation_type = kwargs.get("operation_type", "scan_target")

        try:
            if operation_type == "scan_target":
                return self._scan_target_operation(**kwargs)
            elif operation_type == "get_results":
                return self._get_results_operation(**kwargs)
            elif operation_type == "generate_report":
                return self._generate_report_operation(**kwargs)
            elif operation_type == "get_statistics":
                return self._get_statistics_operation(**kwargs)
            elif operation_type == "stop_scan":
                return self._stop_scan_operation()
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")

        except Exception as e:
            return NetworkOperationResult(
                success=False,
                operation_type=operation_type,
                data={},
                error_message=str(e),
            )

    def _scan_target_operation(self, **kwargs) -> NetworkOperationResult:
        """Perform target scan operation."""
        target = kwargs.get("target")
        if not target:
            raise ValueError("Target is required for scan operation")

        # Parse ports
        ports = self._parse_ports(kwargs.get("ports", "common"))

        # Get scan parameters
        scan_type_str = kwargs.get("scan_type", "tcp_connect")
        try:
            scan_type = ScanType(scan_type_str)
        except ValueError:
            raise ValueError(f"Invalid scan type: {scan_type_str}")

        timeout = kwargs.get("timeout", self.default_timeout)
        max_threads = kwargs.get("max_threads", self.max_threads)

        scan_policy_str = kwargs.get("scan_policy", "normal")
        try:
            scan_policy = ScanPolicy(scan_policy_str)
        except ValueError:
            scan_policy = ScanPolicy.NORMAL

        # Create scan target
        scan_target = ScanTarget(
            host=target, ports=ports, scan_type=scan_type, timeout=timeout
        )

        # Perform scan
        scan_result = self.scan_engine.scan_target(
            scan_target,
            scan_policy,
            max_threads,
            lambda current, total, msg: self.progress_updated.emit(
                current, total, msg
            ),
        )

        # Enhance with service detection if enabled
        if kwargs.get(
            "enable_service_detection", self.enable_service_detection
        ):
            self._enhance_with_service_detection(scan_result)

        # Perform vulnerability assessment if enabled
        if kwargs.get(
            "enable_vulnerability_scan", self.enable_vulnerability_scan
        ):
            vulnerabilities = (
                self.vulnerability_assessment.assess_vulnerabilities(
                    scan_result
                )
            )
            scan_result.vulnerabilities = [
                asdict(vuln) for vuln in vulnerabilities
            ]

        # Store result if enabled
        if self.save_scan_results:
            self.result_manager.add_result(scan_result)

        # Store current scan
        self._current_scan = scan_result

        return NetworkOperationResult(
            success=True,
            operation_type="scan_target",
            data={
                "target": target,
                "ports_scanned": scan_result.total_ports,
                "open_ports": scan_result.open_ports,
                "closed_ports": scan_result.closed_ports,
                "filtered_ports": scan_result.filtered_ports,
                "scan_duration": scan_result.scan_duration,
                "vulnerabilities_found": len(scan_result.vulnerabilities),
                "scan_result": asdict(scan_result),
            },
        )

    def _enhance_with_service_detection(self, scan_result: ScanResult):
        """Enhance scan result with service detection."""
        for port_info in scan_result.ports:
            if port_info.state == PortState.OPEN:
                try:
                    enhanced_info = self.service_detector.detect_service(
                        scan_result.target,
                        port_info.port,
                        self.default_timeout,
                    )

                    # Update port info with service detection results
                    port_info.service = enhanced_info.service
                    port_info.version = enhanced_info.version
                    port_info.banner = enhanced_info.banner
                    port_info.confidence = enhanced_info.confidence
                    port_info.extra_info.update(enhanced_info.extra_info)

                except Exception as e:
                    self.logger.debug(
                        f"Service detection failed for {port_info.port}: {e}"
                    )

    def _parse_ports(self, ports_spec: Union[str, List[int]]) -> List[int]:
        """Parse port specification into list of ports."""
        if isinstance(ports_spec, list):
            return ports_spec

        if isinstance(ports_spec, str):
            if ports_spec.lower() == "common":
                return self.common_ports
            elif ports_spec.lower() == "all":
                return list(range(1, 65536))
            elif "-" in ports_spec:
                # Port range
                try:
                    start, end = map(int, ports_spec.split("-"))
                    return list(range(start, end + 1))
                except ValueError:
                    raise ValueError(f"Invalid port range: {ports_spec}")
            else:
                # Single port or comma-separated list
                try:
                    return [int(p.strip()) for p in ports_spec.split(",")]
                except ValueError:
                    raise ValueError(
                        f"Invalid port specification: {ports_spec}"
                    )

        raise ValueError(
            f"Invalid port specification type: {type(ports_spec)}"
        )

    def _get_results_operation(self, **kwargs) -> NetworkOperationResult:
        """Get scan results operation."""
        target = kwargs.get("target")
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        scan_type_str = kwargs.get("scan_type")

        scan_type = None
        if scan_type_str:
            try:
                scan_type = ScanType(scan_type_str)
            except ValueError:
                pass

        results = self.result_manager.get_results(
            target=target,
            start_time=start_time,
            end_time=end_time,
            scan_type=scan_type,
        )

        # Convert results to serializable format
        results_data = []
        for result in results:
            result_dict = asdict(result)
            result_dict["start_time"] = result.start_time.isoformat()
            if result.end_time:
                result_dict["end_time"] = result.end_time.isoformat()
            results_data.append(result_dict)

        return NetworkOperationResult(
            success=True,
            operation_type="get_results",
            data={"results": results_data, "count": len(results)},
        )

    def _generate_report_operation(self, **kwargs) -> NetworkOperationResult:
        """Generate report operation."""
        file_path = Path(kwargs.get("file_path", "scan_report.json"))
        report_format = kwargs.get("format", "json").lower()
        target = kwargs.get("target")
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")

        if report_format == "json":
            success = self.report_generator.generate_json_report(
                file_path, target, start_time, end_time
            )
        elif report_format == "csv":
            success = self.report_generator.generate_csv_report(
                file_path, target, start_time, end_time
            )
        else:
            raise ValueError(f"Unsupported report format: {report_format}")

        return NetworkOperationResult(
            success=success,
            operation_type="generate_report",
            data={
                "file_path": str(file_path),
                "format": report_format,
                "generated": success,
            },
        )

    def _get_statistics_operation(self, **kwargs) -> NetworkOperationResult:
        """Get scan statistics operation."""
        target = kwargs.get("target")
        hours = kwargs.get("hours", 24)

        statistics = self.result_manager.get_statistics(
            target=target, hours=hours
        )

        return NetworkOperationResult(
            success=True,
            operation_type="get_statistics",
            data={"statistics": statistics, "target": target, "hours": hours},
        )

    def _stop_scan_operation(self) -> NetworkOperationResult:
        """Stop current scan operation."""
        self.scan_engine.stop_scan()

        return NetworkOperationResult(
            success=True,
            operation_type="stop_scan",
            data={"scan_stopped": True},
        )

    def get_supported_protocols(self) -> List[str]:
        """Get list of supported protocols."""
        return ["TCP", "UDP"]

    def validate_parameters(self, **kwargs) -> bool:
        """Validate operation parameters."""
        operation_type = kwargs.get("operation_type")

        if not operation_type:
            return False

        valid_operations = [
            "scan_target",
            "get_results",
            "generate_report",
            "get_statistics",
            "stop_scan",
        ]

        if operation_type not in valid_operations:
            return False

        # Validate target for scan operations
        if operation_type == "scan_target":
            target = kwargs.get("target")
            if not target:
                return False

            # Validate scan type
            scan_type = kwargs.get("scan_type", "tcp_connect")
            try:
                ScanType(scan_type)
            except ValueError:
                return False

        return True

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        return {
            "is_scanning": self._scan_active,
            "current_scan": (
                asdict(self._current_scan) if self._current_scan else None
            ),
            "total_scans_performed": len(self.result_manager.scan_results),
            "security_level": self.security_validator.security_level.value,
            "platform_supported": self.platform_detector.is_supported(),
            "service_detection_enabled": self.enable_service_detection,
            "vulnerability_scan_enabled": self.enable_vulnerability_scan,
            "max_threads": self.max_threads,
            "default_timeout": self.default_timeout,
        }

    def scan_target(
        self,
        target: str,
        ports: Union[str, List[int]] = "common",
        scan_type: str = "tcp_connect",
        timeout: float = None,
        max_threads: int = None,
        scan_policy: str = "normal",
        enable_service_detection: bool = None,
        enable_vulnerability_scan: bool = None,
    ) -> ScanResult:
        """Convenience method to scan a target.

        Args:
            target: Target host or IP
            ports: Ports to scan ('common', 'all', range, or list)
            scan_type: Type of scan to perform
            timeout: Scan timeout
            max_threads: Maximum concurrent threads
            scan_policy: Scanning policy
            enable_service_detection: Enable service detection
            enable_vulnerability_scan: Enable vulnerability scanning

        Returns:
            ScanResult with scan results
        """
        operation_result = self.execute_operation(
            operation_type="scan_target",
            target=target,
            ports=ports,
            scan_type=scan_type,
            timeout=timeout or self.default_timeout,
            max_threads=max_threads or self.max_threads,
            scan_policy=scan_policy,
            enable_service_detection=(
                enable_service_detection
                if enable_service_detection is not None
                else self.enable_service_detection
            ),
            enable_vulnerability_scan=(
                enable_vulnerability_scan
                if enable_vulnerability_scan is not None
                else self.enable_vulnerability_scan
            ),
        )

        if operation_result.success:
            return self._current_scan
        else:
            raise RuntimeError(
                f"Scan failed: {operation_result.error_message}"
            )

    def get_scan_results(
        self, target: Optional[str] = None, hours: int = 24
    ) -> List[ScanResult]:
        """Get recent scan results.

        Args:
            target: Filter by target
            hours: Hours of results to retrieve

        Returns:
            List of scan results
        """
        start_time = datetime.now() - timedelta(hours=hours)
        return self.result_manager.get_results(
            target=target, start_time=start_time
        )

    def generate_report(
        self,
        file_path: str,
        format_type: str = "json",
        target: Optional[str] = None,
        hours: int = 24,
    ) -> bool:
        """Generate scan report.

        Args:
            file_path: Output file path
            format_type: Report format ('json' or 'csv')
            target: Filter by target
            hours: Hours of data to include

        Returns:
            True if report generated successfully
        """
        start_time = datetime.now() - timedelta(hours=hours)

        operation_result = self.execute_operation(
            operation_type="generate_report",
            file_path=file_path,
            format=format_type,
            target=target,
            start_time=start_time,
        )

        return operation_result.success
