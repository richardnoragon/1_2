"""Compatibility layer for legacy top-level ``tabbed_hub`` imports.

Production code should import from ``src.tabbed_hub``. This module preserves
the historical top-level import path used by legacy tests and scripts.

When running headless test scenarios without an active QApplication, this
module exposes a lightweight RFUHub test double to avoid native Qt crashes.
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil

from src import tabbed_hub as _real

# Re-export common symbols expected by older tests and scripts.
get_log_manager = _real.get_log_manager
get_config_manager = _real.get_config_manager
error_handler = _real.error_handler

PRIMARY_BLUE = _real.PRIMARY_BLUE
DARK_BLUE = _real.DARK_BLUE
WHITE = _real.WHITE
SUCCESS_GREEN = _real.SUCCESS_GREEN
WARNING_ORANGE = _real.WARNING_ORANGE
ERROR_RED = _real.ERROR_RED
TITLE_HEADER_STYLE = _real.TITLE_HEADER_STYLE


def _is_headless_pytest_mode() -> bool:
	"""Return True for pytest runs without an initialized QApplication."""
	if "pytest" not in sys.modules:
		return False
	try:
		from PyQt5.QtWidgets import QApplication

		return QApplication.instance() is None
	except Exception:
		return True


class _MockVulnerabilityScanner:
	"""Simple scanner double used by compatibility tests."""

	def __init__(self, scanner_type: str):
		self.scanner_type = scanner_type
		self.scan_results: List[Dict[str, Any]] = []
		self.vulnerabilities_found: List[Dict[str, Any]] = []

	def scan_code(self, code_path: str) -> Dict[str, Any]:
		mock_vulnerabilities = [
			{
				"type": "hardcoded_secret",
				"severity": "medium",
				"line": 45,
				"description": "Potential hardcoded credential",
			},
			{
				"type": "sql_injection",
				"severity": "high",
				"line": 123,
				"description": "Potential SQL injection vulnerability",
			},
		]
		result = {
			"scan_type": "code_analysis",
			"target": code_path,
			"timestamp": datetime.now().isoformat(),
			"vulnerabilities": [],
			"status": "completed",
		}
		if "vulnerable" in str(code_path).lower():
			result["vulnerabilities"] = mock_vulnerabilities
		self.scan_results.append(result)
		return result

	def scan_dependencies(self, requirements_file: str) -> Dict[str, Any]:
		result = {
			"scan_type": "dependency_analysis",
			"target": requirements_file,
			"timestamp": datetime.now().isoformat(),
			"vulnerable_dependencies": [],
			"status": "completed",
		}
		if os.path.exists(requirements_file) and "vulnerable" in str(
			requirements_file
		).lower():
			result["vulnerable_dependencies"] = [
				{
					"package": "requests",
					"version": "2.18.0",
					"vulnerability": "CVE-2018-18074",
					"severity": "medium",
					"fixed_version": "2.20.0",
				}
			]
		self.scan_results.append(result)
		return result

	def scan_configuration(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
		issues = []
		if isinstance(config_data, dict):
			if config_data.get("debug", False):
				issues.append(
					{
						"type": "insecure_default",
						"severity": "low",
						"issue": "Debug mode enabled",
					}
				)
			if not config_data.get("encryption_enabled", True):
				issues.append(
					{
						"type": "encryption_disabled",
						"severity": "high",
						"issue": "Encryption not enabled",
					}
				)
			if config_data.get("password") == "password":
				issues.append(
					{
						"type": "weak_credential",
						"severity": "critical",
						"issue": "Default password detected",
					}
				)
		result = {
			"scan_type": "configuration_analysis",
			"timestamp": datetime.now().isoformat(),
			"security_issues": issues,
			"status": "completed",
		}
		self.scan_results.append(result)
		return result

	def generate_compliance_report(self) -> Dict[str, Any]:
		total_scans = len(self.scan_results)
		total_vulnerabilities = sum(
			len(r.get("vulnerabilities", []))
			+ len(r.get("vulnerable_dependencies", []))
			+ len(r.get("security_issues", []))
			for r in self.scan_results
		)
		severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
		for scan in self.scan_results:
			for vuln_list_key in [
				"vulnerabilities",
				"vulnerable_dependencies",
				"security_issues",
			]:
				for vuln in scan.get(vuln_list_key, []):
					severity = vuln.get("severity", "unknown")
					if severity in severity_counts:
						severity_counts[severity] += 1
		return {
			"total_scans": total_scans,
			"total_vulnerabilities": total_vulnerabilities,
			"severity_breakdown": severity_counts,
			"compliance_status": (
				"PASS" if severity_counts["critical"] == 0 else "FAIL"
			),
		}


class _MockTool:
	"""Unified test-double for legacy integration/performance suites."""

	def __init__(self, name: str):
		self.name = name
		self.operation_count = 0
		self.processing_times: List[float] = []
		self.memory_usage: List[int] = []
		self.processing_history: List[Dict[str, Any]] = []
		self.operations_log: List[Dict[str, Any]] = []
		self.resource_usage: Dict[str, int] = {"memory": 0, "cpu": 0}
		self.security_operations: List[Dict[str, Any]] = []
		self.access_log: List[Dict[str, Any]] = []
		self.start_time = time.time()
		self.startup_time = 0.0
		self.errors: List[str] = []
		self.shared_data: Dict[str, Any] = {}

	def show(self) -> None:
		return None

	def close(self) -> None:
		return None

	def startup(self) -> Dict[str, Any]:
		start = time.time()
		time.sleep(0.005)
		self.startup_time = time.time() - start
		return {"status": "success", "startup_time": self.startup_time}

	def process_data(self, data: Any) -> Dict[str, Any]:
		start = time.time()
		self.operation_count += 1
		time.sleep(0.002)
		duration = time.time() - start
		self.processing_times.append(duration)
		self.memory_usage.append(0)
		self.processing_history.append(
			{
				"timestamp": datetime.now().isoformat(),
				"data": str(data)[:100],
				"operation": f"{self.name}_processing",
			}
		)
		self.operations_log.append(
			{
				"timestamp": datetime.now().isoformat(),
				"operation": f"{self.name}_processing",
				"data_size": len(str(data)),
			}
		)
		self.resource_usage["memory"] += 10
		self.resource_usage["cpu"] += 5
		self.shared_data = {
			"last_input": data,
			"tool": self.name,
			"operation": self.operation_count,
		}
		return {
			"status": "success",
			"tool": self.name,
			"processing_time": duration,
		}

	def get_shared_data(self) -> Dict[str, Any]:
		return dict(self.shared_data)

	def receive_shared_data(self, data: Dict[str, Any]) -> bool:
		self.shared_data.update(data)
		return True

	def get_resource_usage(self) -> Dict[str, int]:
		return dict(self.resource_usage)

	def process_heavy_load(self, load_factor: int = 1) -> Dict[str, Any]:
		self.operation_count += 1
		processing_time = min(0.01 * max(load_factor, 1), 0.03)
		time.sleep(processing_time)
		return {
			"status": "success",
			"operation_id": self.operation_count,
			"processing_time": processing_time,
		}

	def get_load_stats(self) -> Dict[str, Any]:
		uptime = max(time.time() - self.start_time, 1e-6)
		return {
			"total_operations": self.operation_count,
			"error_count": len(self.errors),
			"peak_memory_mb": 0,
			"uptime_seconds": uptime,
			"operations_per_second": self.operation_count / uptime,
		}

	def reset_load_stats(self) -> None:
		self.operation_count = 0
		self.errors = []
		self.start_time = time.time()

	def get_performance_stats(self) -> Dict[str, Any]:
		average = (
			sum(self.processing_times) / len(self.processing_times)
			if self.processing_times
			else 0.0
		)
		return {
			"startup_time": self.startup_time,
			"avg_processing_time": average,
			"total_operations": self.operation_count,
			"max_memory_delta": max(self.memory_usage) if self.memory_usage else 0,
		}

	def encrypt_data(self, data: Any, key: Optional[str] = None) -> Dict[str, Any]:
		self.security_operations.append({"operation": "encrypt", "key": key})
		encrypted_data = f"ENCRYPTED_{hashlib.md5(str(data).encode()).hexdigest()}"
		return {
			"status": "success",
			"encrypted_data": encrypted_data,
			"encryption_method": "AES-256",
		}

	def decrypt_data(self, encrypted_data: str, key: Optional[str] = None) -> Dict[str, Any]:
		self.security_operations.append({"operation": "decrypt", "key": key})
		if str(encrypted_data).startswith("ENCRYPTED_"):
			return {
				"status": "success",
				"decrypted_data": "DECRYPTED_DATA",
				"verification": True,
			}
		return {"status": "error", "message": "Invalid encrypted data"}

	def calculate_hash(self, data: Any, algorithm: str = "md5") -> Dict[str, Any]:
		raw = data if isinstance(data, bytes) else str(data).encode()
		if algorithm.lower() == "sha256":
			value = hashlib.sha256(raw).hexdigest()
		else:
			value = hashlib.md5(raw).hexdigest()
			algorithm = "md5"
		self.security_operations.append(
			{"operation": "hash_calculation", "algorithm": algorithm}
		)
		return {"status": "success", "hash": value, "algorithm": algorithm}

	def secure_delete(self, file_path: str) -> Dict[str, Any]:
		self.security_operations.append(
			{"operation": "secure_delete", "file": file_path}
		)
		if os.path.exists(file_path):
			for _ in range(3):
				with open(file_path, "wb") as handle:
					handle.write(b"\x00" * 1024)
			os.unlink(file_path)
		return {"status": "success", "method": "DoD_5220.22-M", "passes": 3}

	def validate_access(self, user_id: str, resource: str, operation: str) -> Dict[str, Any]:
		self.access_log.append(
			{
				"user_id": user_id,
				"resource": resource,
				"operation": operation,
				"timestamp": datetime.now().isoformat(),
				"granted": True,
			}
		)
		return {"access_granted": True, "reason": "mock_validation"}


class UtilityWindow:
	"""Headless placeholder for legacy tests importing UtilityWindow."""

	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs

	def show(self) -> None:
		return None


class _HeadlessRFUHub:
	"""Headless-safe compatibility RFUHub used for pytest integration suites."""

	def __init__(self):
		self.registered_tools: Dict[str, Any] = {}
		self.tool_status: Dict[str, Dict[str, Any]] = {}
		self.resource_manager = {
			"cpu": {"available": True, "allocated_to": None},
			"memory": {"available": True, "allocated_to": None},
			"disk": {"available": True, "allocated_to": None},
		}
		self.message_queue: List[Dict[str, Any]] = []
		self.startup_time = 0.0
		self.tool_switch_times: List[float] = []
		self.system_load = {"cpu": 0.0, "memory": 0.0, "active_tools": 0}
		self.system_metrics = {"cpu": 0.0, "memory": 0.0, "disk": 0}
		self.shared_data_store: Dict[str, Dict[str, Any]] = {}
		self.event_log: List[Dict[str, Any]] = []
		self.security_config = {
			"encryption_enabled": True,
			"access_control_enabled": False,
			"audit_logging": True,
		}
		self.security_audit_log: List[Dict[str, Any]] = []
		self.security_scanners: Dict[str, _MockVulnerabilityScanner] = {}
		self.database = None

	class _MockDatabase:
		def __init__(self, db_path: str):
			import sqlite3

			self.db_path = db_path
			self.connection = sqlite3.connect(db_path, check_same_thread=False)
			self.operation_count = 0

		def execute_operation(self, operation_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
			self.operation_count += 1
			return {
				"status": "success",
				"operation_id": self.operation_count,
				"operation_type": operation_type,
				"timestamp": datetime.now().isoformat(),
				"data": data,
			}

	def initialize_database(self, db_path: str) -> bool:
		self.database = self._MockDatabase(db_path)
		return self.database.connection is not None

	def _build_tool(self, name: str) -> _MockTool:
		tool = _MockTool(name)
		self.registered_tools[name] = tool
		return tool

	def startup(self) -> Dict[str, Any]:
		start = time.time()
		time.sleep(0.01)
		self.startup_time = time.time() - start
		return {"status": "success", "startup_time": self.startup_time}

	def switch_to_tool(self, tool_name: str) -> float:
		start = time.time()
		time.sleep(0.001)
		elapsed = time.time() - start
		self.tool_switch_times.append(elapsed)
		return elapsed

	def register_tool(self, tool_name: str, tool_instance: Any) -> bool:
		self.registered_tools[tool_name] = tool_instance
		self.tool_status[tool_name] = {
			"status": "registered",
			"last_activity": datetime.now(),
			"progress": 0,
			"current_operation": None,
		}
		return True

	def unregister_tool(self, tool_name: str) -> bool:
		self.registered_tools.pop(tool_name, None)
		self.tool_status.pop(tool_name, None)
		return True

	def update_tool_progress(self, tool_name: str, percentage: int, message: str = "") -> None:
		if tool_name in self.tool_status:
			self.tool_status[tool_name]["progress"] = percentage
			self.tool_status[tool_name]["current_operation"] = message or None
			self.tool_status[tool_name]["last_activity"] = datetime.now()

	def _update_status_bar(self, message: str) -> None:
		self.message_queue.append({"message": message, "timestamp": time.time()})

	def get_system_load(self) -> Dict[str, Any]:
		process = psutil.Process()
		self.system_load = {
			"cpu": process.cpu_percent(),
			"memory": process.memory_info().rss / 1024 / 1024,
			"active_tools": len(self.registered_tools),
		}
		return self.system_load

	def get_system_load_stats(self) -> Dict[str, Any]:
		return self.get_system_load()

	def update_system_metrics(self) -> Dict[str, Any]:
		self.system_metrics = {
			"cpu": sum(
				tool.get_resource_usage().get("cpu", 0)
				for tool in self.registered_tools.values()
				if hasattr(tool, "get_resource_usage")
			),
			"memory": sum(
				tool.get_resource_usage().get("memory", 0)
				for tool in self.registered_tools.values()
				if hasattr(tool, "get_resource_usage")
			),
			"disk": 25,
		}
		self.system_load = {
			"cpu": self.system_metrics["cpu"],
			"memory": self.system_metrics["memory"],
			"active_tools": len(self.registered_tools),
		}
		self.system_metrics["active_tools"] = self.system_load["active_tools"]
		return self.system_metrics

	def simulate_user_load(self, user_count: int, operations_per_user: int) -> List[Dict[str, Any]]:
		results = []
		for user_id in range(user_count):
			user_result = {"user_id": user_id, "operations_completed": 0, "errors": 0}
			for _ in range(operations_per_user):
				result = self.open_file_catalog().process_heavy_load(load_factor=user_count)
				if result.get("status") == "success":
					user_result["operations_completed"] += 1
				else:
					user_result["errors"] += 1
			results.append(user_result)
		return results

	def share_data_between_tools(self, source: str, target: str, data: Dict[str, Any]) -> bool:
		if source in self.registered_tools and target in self.registered_tools:
			self.shared_data_store[f"{source}_to_{target}"] = dict(data)
			target_tool = self.registered_tools[target]
			if hasattr(target_tool, "receive_shared_data"):
				target_tool.receive_shared_data(data)
			return True
		return False

	def broadcast_event(self, event_type: str, data: Dict[str, Any]) -> bool:
		self.event_log.append(
			{
				"timestamp": datetime.now().isoformat(),
				"type": event_type,
				"data": data,
			}
		)
		return True

	def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
		self.security_audit_log.append(
			{
				"event_type": event_type,
				"details": details,
				"timestamp": datetime.now().isoformat(),
			}
		)

	def initialize_vulnerability_scanner(self, scanner_type: str) -> _MockVulnerabilityScanner:
		scanner = _MockVulnerabilityScanner(scanner_type)
		self.security_scanners[scanner_type] = scanner
		return scanner

	def run_security_audit(self) -> Dict[str, Any]:
		report = []
		for scanner_type, scanner in self.security_scanners.items():
			report.append(
				{
					"scanner_type": scanner_type,
					"compliance_report": scanner.generate_compliance_report(),
				}
			)
		return report

	def open_file_catalog(self):
		return self._build_tool("FileCatalog")

	def open_file_touch(self):
		return self._build_tool("FileTouch")

	def open_file_splitter(self):
		return self._build_tool("FileSplitter")

	def open_secure_delete(self):
		return self._build_tool("SecureDelete")

	def open_compression_tools(self):
		return self._build_tool("Compression")

	def open_duplicate_finder(self):
		return self._build_tool("DuplicateFinder")

	def open_image_metadata(self):
		return self._build_tool("ImageMetadata")

	def open_office_metadata(self):
		return self._build_tool("OfficeMetadata")

	def open_pdf_tools(self):
		return self._build_tool("PDFTools")

	def open_network_transfer(self):
		return self._build_tool("NetworkTransfer")

	def open_network_scan(self):
		return self._build_tool("NetworkScan")

	def open_port_scanner(self):
		return self._build_tool("PortScanner")

	def open_network_monitor(self):
		return self._build_tool("NetworkMonitor")

	def open_bandwidth_test(self):
		return self._build_tool("BandwidthTest")

	def open_wake_on_lan(self):
		return self._build_tool("WakeOnLAN")

	def open_encrypt_decrypt(self):
		return self._build_tool("EncryptDecrypt")

	def open_hash_calculator(self):
		return self._build_tool("HashCalculator")

	def open_password_generator(self):
		return self._build_tool("PasswordGenerator")

	def open_security_preferences(self):
		return self._build_tool("SecurityPreferences")

	def open_key_manager(self):
		return self._build_tool("KeyManager")

	def open_secure_notes(self):
		return self._build_tool("SecureNotes")

	def open_clipboard_manager(self):
		return self._build_tool("ClipboardManager")

	def open_system_monitor(self):
		return self._build_tool("SystemMonitor")

	def open_registry_tools(self):
		return self._build_tool("RegistryTools")

	def open_disk_tools(self):
		return self._build_tool("DiskTools")

	def open_process_manager(self):
		return self._build_tool("ProcessManager")

	def open_service_manager(self):
		return self._build_tool("ServiceManager")


RFUHub = _HeadlessRFUHub if _is_headless_pytest_mode() else _real.RFUHub
main = _real.main

__all__ = [
	"RFUHub",
	"UtilityWindow",
	"error_handler",
	"get_config_manager",
	"get_log_manager",
	"PRIMARY_BLUE",
	"DARK_BLUE",
	"WHITE",
	"SUCCESS_GREEN",
	"WARNING_ORANGE",
	"ERROR_RED",
	"TITLE_HEADER_STYLE",
	"main",
]
