"""
Directory Audit Logger for RFU Hub

Implements comprehensive audit logging with anonymization and
compliance features for directory security operations.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import logging
import json
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

from ..database.database_manager import DatabaseManager


class AuditEventType(Enum):
    """Types of audit events"""

    DIRECTORY_ACCESS = "directory_access"
    DIRECTORY_STORE = "directory_store"
    DIRECTORY_RETRIEVE = "directory_retrieve"
    DIRECTORY_DELETE = "directory_delete"
    DIRECTORY_LIST = "directory_list"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_REVOKE = "permission_revoke"
    ROLE_ASSIGNMENT = "role_assignment"
    SECURITY_VIOLATION = "security_violation"
    ACCESS_DENIED = "access_denied"
    ENCRYPTION_EVENT = "encryption_event"
    PII_DETECTION = "pii_detection"
    SYSTEM_EVENT = "system_event"


class AuditSeverity(Enum):
    """Audit event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event record"""

    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: str
    resource_id: Optional[str]
    action: str
    success: bool
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    anonymized_data: Optional[Dict[str, Any]] = None


class DirectoryAuditLogger:
    """
    Implements comprehensive audit logging with anonymization and
    compliance features for directory security operations.
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize DirectoryAuditLogger

        Args:
            database_manager: Database manager instance
        """
        self.db_manager = database_manager
        self.logger = logging.getLogger("RFU.DirectoryAuditLogger")

        # Audit configuration
        self.max_detail_length = 10000
        self.anonymize_sensitive_data = True
        self.retention_days = 365

        # PII patterns for anonymization
        self.pii_patterns = self._load_pii_anonymization_patterns()

        self.logger.info("DirectoryAuditLogger initialized successfully")

    def log_directory_operation(
        self,
        user_id: str,
        resource_id: str,
        operation: str,
        success: bool,
        details: Dict[str, Any],
        severity: AuditSeverity = AuditSeverity.INFO,
    ) -> str:
        """
        Log directory operation

        Args:
            user_id: User performing operation
            resource_id: Resource identifier (path hash)
            operation: Operation performed
            success: Whether operation succeeded
            details: Operation details
            severity: Event severity

        Returns:
            Event ID of logged event
        """
        try:
            event_type = self._determine_event_type(operation)

            audit_event = self._create_audit_event(
                event_type=event_type,
                severity=severity,
                user_id=user_id,
                resource_id=resource_id,
                action=operation,
                success=success,
                details=details,
            )

            # Store in database
            event_id = self._store_audit_event(audit_event)

            # Log to system logger based on severity
            self._log_to_system(audit_event)

            return event_id

        except Exception as e:
            self.logger.error(f"Failed to log directory operation: {e}")
            return ""

    def log_access_denied(
        self, user_id: str, resource_id: str, action: str, reason: str
    ) -> str:
        """
        Log access denied event

        Args:
            user_id: User denied access
            resource_id: Resource identifier
            action: Action that was denied
            reason: Reason for denial

        Returns:
            Event ID of logged event
        """
        try:
            details = {
                "action": action,
                "reason": reason,
                "access_time": datetime.now(timezone.utc).isoformat(),
            }

            audit_event = self._create_audit_event(
                event_type=AuditEventType.ACCESS_DENIED,
                severity=AuditSeverity.WARNING,
                user_id=user_id,
                resource_id=resource_id,
                action=f"access_denied_{action}",
                success=False,
                details=details,
            )

            event_id = self._store_audit_event(audit_event)
            self._log_to_system(audit_event)

            return event_id

        except Exception as e:
            self.logger.error(f"Failed to log access denied: {e}")
            return ""

    def log_security_violation(
        self, user_id: str, violation_type: str, details: Dict[str, Any]
    ) -> str:
        """
        Log security violation event

        Args:
            user_id: User associated with violation
            violation_type: Type of security violation
            details: Violation details

        Returns:
            Event ID of logged event
        """
        try:
            audit_event = self._create_audit_event(
                event_type=AuditEventType.SECURITY_VIOLATION,
                severity=AuditSeverity.ERROR,
                user_id=user_id,
                resource_id=None,
                action=f"security_violation_{violation_type}",
                success=False,
                details=details,
            )

            event_id = self._store_audit_event(audit_event)
            self._log_to_system(audit_event)

            # Also log to security-specific logger
            security_logger = logging.getLogger("RFU.Security")
            security_logger.error(
                f"Security violation by user {user_id[:8]}...: "
                f"{violation_type} - {details}"
            )

            return event_id

        except Exception as e:
            self.logger.error(f"Failed to log security violation: {e}")
            return ""

    def log_permission_change(
        self,
        user_id: str,
        target_user: str,
        action: str,
        permission_details: Dict[str, Any],
        success: bool,
    ) -> str:
        """
        Log permission change event

        Args:
            user_id: User making the change
            target_user: User whose permissions are being changed
            action: Permission action (grant/revoke)
            permission_details: Permission details
            success: Whether change succeeded

        Returns:
            Event ID of logged event
        """
        try:
            details = {
                "target_user": self._anonymize_user_id(target_user),
                "permission_details": permission_details,
                "change_time": datetime.now(timezone.utc).isoformat(),
            }

            event_type = (
                AuditEventType.PERMISSION_GRANT
                if action == "grant"
                else AuditEventType.PERMISSION_REVOKE
            )

            audit_event = self._create_audit_event(
                event_type=event_type,
                severity=AuditSeverity.INFO,
                user_id=user_id,
                resource_id=None,
                action=f"permission_{action}",
                success=success,
                details=details,
            )

            event_id = self._store_audit_event(audit_event)
            self._log_to_system(audit_event)

            return event_id

        except Exception as e:
            self.logger.error(f"Failed to log permission change: {e}")
            return ""

    def log_pii_detection(
        self,
        user_id: str,
        resource_id: str,
        pii_indicators: List[str],
        sensitivity_level: int,
        anonymized_path: str,
    ) -> str:
        """
        Log PII detection event

        Args:
            user_id: User associated with PII detection
            resource_id: Resource identifier
            pii_indicators: List of PII indicators found
            sensitivity_level: Sensitivity level (1-5)
            anonymized_path: Anonymized version of path

        Returns:
            Event ID of logged event
        """
        try:
            details = {
                "pii_indicators": pii_indicators,
                "sensitivity_level": sensitivity_level,
                "anonymized_path": anonymized_path,
                "detection_time": datetime.now(timezone.utc).isoformat(),
            }

            severity = (
                AuditSeverity.CRITICAL
                if sensitivity_level >= 5
                else (
                    AuditSeverity.WARNING
                    if sensitivity_level >= 3
                    else AuditSeverity.INFO
                )
            )

            audit_event = self._create_audit_event(
                event_type=AuditEventType.PII_DETECTION,
                severity=severity,
                user_id=user_id,
                resource_id=resource_id,
                action="pii_detected",
                success=True,
                details=details,
            )

            event_id = self._store_audit_event(audit_event)
            self._log_to_system(audit_event)

            return event_id

        except Exception as e:
            self.logger.error(f"Failed to log PII detection: {e}")
            return ""

    def get_audit_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuditEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        """
        Retrieve audit events with filtering

        Args:
            user_id: Optional user filter
            event_type: Optional event type filter
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of events to return

        Returns:
            List of AuditEvent objects
        """
        try:
            query_parts = ["SELECT * FROM directory_audit_log WHERE 1=1"]
            params = []

            if user_id:
                query_parts.append("AND user_id = ?")
                params.append(user_id)

            if event_type:
                query_parts.append("AND event_type = ?")
                params.append(event_type.value)

            if start_time:
                query_parts.append("AND timestamp >= ?")
                params.append(start_time.isoformat())

            if end_time:
                query_parts.append("AND timestamp <= ?")
                params.append(end_time.isoformat())

            query_parts.append("ORDER BY timestamp DESC LIMIT ?")
            params.append(limit)

            query = " ".join(query_parts)
            results = self.db_manager.fetch_all(query, params)

            events = []
            for result in results:
                event = self._parse_audit_event_from_db(result)
                if event:
                    events.append(event)

            return events

        except Exception as e:
            self.logger.error(f"Failed to retrieve audit events: {e}")
            return []

    def generate_audit_report(
        self,
        start_time: datetime,
        end_time: datetime,
        include_pii_events: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate audit report for time period

        Args:
            start_time: Report start time
            end_time: Report end time
            include_pii_events: Whether to include PII-related events

        Returns:
            Audit report dictionary
        """
        try:
            events = self.get_audit_events(
                start_time=start_time, end_time=end_time, limit=10000
            )

            # Generate report statistics
            report = {
                "report_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                },
                "total_events": len(events),
                "event_types": {},
                "severity_distribution": {},
                "success_rate": 0,
                "security_violations": 0,
                "access_denials": 0,
                "unique_users": set(),
                "top_operations": {},
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Analyze events
            successful_events = 0
            for event in events:
                # Event type distribution
                event_type = event.event_type.value
                report["event_types"][event_type] = (
                    report["event_types"].get(event_type, 0) + 1
                )

                # Severity distribution
                severity = event.severity.value
                report["severity_distribution"][severity] = (
                    report["severity_distribution"].get(severity, 0) + 1
                )

                # Success tracking
                if event.success:
                    successful_events += 1

                # Security events
                if event.event_type == AuditEventType.SECURITY_VIOLATION:
                    report["security_violations"] += 1
                elif event.event_type == AuditEventType.ACCESS_DENIED:
                    report["access_denials"] += 1

                # User tracking
                report["unique_users"].add(
                    self._anonymize_user_id(event.user_id)
                )

                # Operation tracking
                action = event.action
                report["top_operations"][action] = (
                    report["top_operations"].get(action, 0) + 1
                )

            # Calculate success rate
            if len(events) > 0:
                report["success_rate"] = (
                    successful_events / len(events)
                ) * 100

            # Convert unique users set to count
            report["unique_users"] = len(report["unique_users"])

            # Sort top operations
            report["top_operations"] = dict(
                sorted(
                    report["top_operations"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]
            )

            # Add PII events summary if requested
            if include_pii_events:
                pii_events = [
                    e
                    for e in events
                    if e.event_type == AuditEventType.PII_DETECTION
                ]
                report["pii_events"] = {
                    "total": len(pii_events),
                    "high_sensitivity": len(
                        [
                            e
                            for e in pii_events
                            if e.details.get("sensitivity_level", 0) >= 4
                        ]
                    ),
                }

            return report

        except Exception as e:
            self.logger.error(f"Failed to generate audit report: {e}")
            return {"error": str(e)}

    def cleanup_old_events(self, retention_days: Optional[int] = None) -> int:
        """
        Clean up old audit events based on retention policy

        Args:
            retention_days: Optional override for retention period

        Returns:
            Number of events cleaned up
        """
        try:
            days = retention_days or self.retention_days
            cutoff_time = datetime.now(timezone.utc) - datetime.timedelta(
                days=days
            )

            query = "DELETE FROM directory_audit_log WHERE timestamp < ?"
            result = self.db_manager.execute_query(
                query, (cutoff_time.isoformat(),)
            )

            count = result.rowcount if hasattr(result, "rowcount") else 0

            if count > 0:
                self.logger.info(f"Cleaned up {count} old audit events")

            return count

        except Exception as e:
            self.logger.error(f"Failed to cleanup old events: {e}")
            return 0

    def _create_audit_event(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        user_id: str,
        resource_id: Optional[str],
        action: str,
        success: bool,
        details: Dict[str, Any],
    ) -> AuditEvent:
        """Create audit event object"""

        # Generate unique event ID
        event_id = self._generate_event_id()

        # Anonymize sensitive data in details
        anonymized_details = self._anonymize_details(details)

        # Create anonymized data summary
        anonymized_data = {
            "user_hash": self._anonymize_user_id(user_id),
            "resource_hash": resource_id[:8] + "..." if resource_id else None,
            "timestamp_hash": hashlib.md5(
                datetime.now(timezone.utc).isoformat().encode()
            ).hexdigest()[:8],
        }

        return AuditEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource_id=resource_id,
            action=action,
            success=success,
            details=anonymized_details,
            timestamp=datetime.now(timezone.utc),
            anonymized_data=anonymized_data,
        )

    def _store_audit_event(self, event: AuditEvent) -> str:
        """Store audit event in database"""
        try:
            query = """
            INSERT INTO directory_audit_log 
            (event_id, event_type, severity, user_id, resource_id, action,
             success, details, timestamp, anonymized_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                event.event_id,
                event.event_type.value,
                event.severity.value,
                event.user_id,
                event.resource_id,
                event.action,
                event.success,
                json.dumps(event.details),
                event.timestamp.isoformat(),
                json.dumps(event.anonymized_data),
            )

            self.db_manager.execute_query(query, params)
            return event.event_id

        except Exception as e:
            self.logger.error(f"Failed to store audit event: {e}")
            return ""

    def _determine_event_type(self, operation: str) -> AuditEventType:
        """Determine audit event type from operation"""

        operation_mapping = {
            "store": AuditEventType.DIRECTORY_STORE,
            "retrieve": AuditEventType.DIRECTORY_RETRIEVE,
            "delete": AuditEventType.DIRECTORY_DELETE,
            "list": AuditEventType.DIRECTORY_LIST,
            "access": AuditEventType.DIRECTORY_ACCESS,
        }

        return operation_mapping.get(operation, AuditEventType.SYSTEM_EVENT)

    def _anonymize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data in event details"""

        if not self.anonymize_sensitive_data:
            return details

        anonymized = {}

        for key, value in details.items():
            if isinstance(value, str):
                # Apply PII anonymization patterns
                anonymized_value = value
                for pattern, replacement in self.pii_patterns.items():
                    anonymized_value = anonymized_value.replace(
                        pattern, replacement
                    )
                anonymized[key] = anonymized_value
            elif isinstance(value, dict):
                anonymized[key] = self._anonymize_details(value)
            else:
                anonymized[key] = value

        return anonymized

    def _anonymize_user_id(self, user_id: str) -> str:
        """Anonymize user ID for reporting"""
        return hashlib.md5(user_id.encode()).hexdigest()[:8]

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        import secrets

        return f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{secrets.token_hex(8)}"

    def _log_to_system(self, event: AuditEvent) -> None:
        """Log event to system logger"""

        log_message = (
            f"AUDIT: {event.event_type.value} by user {event.user_id[:8]}... "
            f"- {event.action} - {'SUCCESS' if event.success else 'FAILED'}"
        )

        if event.severity == AuditSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif event.severity == AuditSeverity.ERROR:
            self.logger.error(log_message)
        elif event.severity == AuditSeverity.WARNING:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _parse_audit_event_from_db(
        self, db_result: tuple
    ) -> Optional[AuditEvent]:
        """Parse audit event from database result"""
        try:
            return AuditEvent(
                event_id=db_result[0],
                event_type=AuditEventType(db_result[1]),
                severity=AuditSeverity(db_result[2]),
                user_id=db_result[3],
                resource_id=db_result[4],
                action=db_result[5],
                success=bool(db_result[6]),
                details=json.loads(db_result[7]),
                timestamp=datetime.fromisoformat(db_result[8]),
                anonymized_data=(
                    json.loads(db_result[9]) if db_result[9] else None
                ),
            )

        except Exception as e:
            self.logger.error(f"Failed to parse audit event: {e}")
            return None

    def _load_pii_anonymization_patterns(self) -> Dict[str, str]:
        """Load PII anonymization patterns"""
        return {
            "username": "[USER]",
            "email": "[EMAIL]",
            "phone": "[PHONE]",
            "ssn": "[SSN]",
            "credit_card": "[CARD]",
            "ip_address": "[IP]",
            "path": "[PATH]",
        }
