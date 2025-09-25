"""
Theme Access Controller for RFU Hub

Provides comprehensive access control and audit logging for theme operations:
- User permission validation and enforcement
- Operation audit logging and tracking
- Security policy enforcement
- Access attempt monitoring and rate limiting
"""

import logging
import sqlite3
import datetime
import os
from typing import Dict, Any, List
from enum import Enum


class Permission(Enum):
    """Theme operation permissions."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    BACKUP = "backup"
    RESTORE = "restore"


class OperationType(Enum):
    """Types of theme operations."""

    LOAD_THEME = "load_theme"
    SAVE_THEME = "save_theme"
    DELETE_THEME = "delete_theme"
    CREATE_BACKUP = "create_backup"
    RESTORE_BACKUP = "restore_backup"
    ROTATE_KEYS = "rotate_keys"
    VIEW_LOGS = "view_logs"
    MODIFY_PERMISSIONS = "modify_permissions"


class AccessResult:
    """Result of an access control check."""

    def __init__(
        self,
        allowed: bool,
        reason: str = None,
        user_id: str = None,
        operation: str = None,
    ):
        self.allowed = allowed
        self.reason = reason
        self.user_id = user_id
        self.operation = operation
        self.timestamp = datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert access result to dictionary."""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "user_id": self.user_id,
            "operation": self.operation,
            "timestamp": self.timestamp,
        }


class ThemeAccessController:
    """
    Access control and audit logging system for theme operations.

    This class manages user permissions, logs all theme operations,
    and enforces security policies.
    """

    def __init__(self, database_path: str = "data/theme_security.db"):
        """
        Initialize the Theme Access Controller.

        Args:
            database_path: Path to the security database
        """
        self.logger = logging.getLogger("RFU.ThemeAccessController")
        self.database_path = database_path

        # Ensure database directory exists
        os.makedirs(os.path.dirname(database_path), exist_ok=True)

        # Initialize database
        self._init_database()

        # Access control configuration
        self.config = {
            "max_failed_attempts": 3,
            "lockout_duration": 300,  # 5 minutes in seconds
            "session_timeout": 3600,  # 1 hour in seconds
            "require_authentication": True,
            "audit_retention_days": 365,
            "rate_limit_window": 60,  # 1 minute
            "rate_limit_max_requests": 10,
        }

        # Default permissions for user roles
        self.default_permissions = {
            "admin": [
                Permission.READ,
                Permission.WRITE,
                Permission.DELETE,
                Permission.ADMIN,
                Permission.BACKUP,
                Permission.RESTORE,
            ],
            "user": [Permission.READ, Permission.WRITE],
            "guest": [Permission.READ],
            "backup_operator": [
                Permission.READ,
                Permission.BACKUP,
                Permission.RESTORE,
            ],
        }

        self.logger.info("Theme Access Controller initialized")

    def _init_database(self):
        """Initialize the security database tables."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Create user permissions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS theme_permissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        permission TEXT NOT NULL,
                        resource TEXT,
                        granted_by TEXT,
                        granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        active BOOLEAN DEFAULT 1,
                        UNIQUE(user_id, permission, resource)
                    )
                """
                )

                # Create access log table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS theme_access_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        resource TEXT,
                        success BOOLEAN NOT NULL,
                        reason TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        session_id TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create user sessions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS theme_user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_id TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        active BOOLEAN DEFAULT 1
                    )
                """
                )

                # Create failed attempts table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS theme_failed_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        ip_address TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.commit()
                self.logger.info("Security database initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize security database: {e}")
            raise

    def check_permission(
        self, user_id: str, permission: Permission, resource: str = None
    ) -> AccessResult:
        """
        Check if a user has permission for an operation.

        Args:
            user_id: User identifier
            permission: Required permission
            resource: Optional resource identifier

        Returns:
            AccessResult indicating if access is allowed
        """
        try:
            # Check if user is locked out
            if self._is_user_locked_out(user_id):
                return AccessResult(
                    allowed=False,
                    reason="User account is temporarily locked due to failed attempts",
                    user_id=user_id,
                )

            # Check rate limiting
            if self._is_rate_limited(user_id):
                return AccessResult(
                    allowed=False,
                    reason="Rate limit exceeded",
                    user_id=user_id,
                )

            # Check user permissions in database
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Check for specific permission
                query = """
                    SELECT COUNT(*) FROM theme_permissions 
                    WHERE user_id = ? AND permission = ? AND active = 1
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                """
                params = [user_id, permission.value]

                if resource:
                    query += " AND (resource IS NULL OR resource = ?)"
                    params.append(resource)

                cursor.execute(query, params)
                has_permission = cursor.fetchone()[0] > 0

                if has_permission:
                    return AccessResult(
                        allowed=True,
                        reason="Permission granted",
                        user_id=user_id,
                    )

                # Check for admin permission (admin can do everything)
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM theme_permissions 
                    WHERE user_id = ? AND permission = ? AND active = 1
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                """,
                    [user_id, Permission.ADMIN.value],
                )

                is_admin = cursor.fetchone()[0] > 0

                if is_admin:
                    return AccessResult(
                        allowed=True,
                        reason="Admin permission granted",
                        user_id=user_id,
                    )

                return AccessResult(
                    allowed=False,
                    reason=f"Permission {permission.value} not granted",
                    user_id=user_id,
                )

        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return AccessResult(
                allowed=False,
                reason=f"Permission check error: {e}",
                user_id=user_id,
            )

    def log_access(
        self,
        user_id: str,
        operation: OperationType,
        resource: str = None,
        success: bool = True,
        reason: str = None,
        session_id: str = None,
    ) -> bool:
        """
        Log a theme access operation.

        Args:
            user_id: User identifier
            operation: Type of operation
            resource: Optional resource identifier
            success: Whether the operation succeeded
            reason: Optional reason for failure
            session_id: Optional session identifier

        Returns:
            True if logging was successful
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO theme_access_log 
                    (user_id, operation, resource, success, reason, session_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    [
                        user_id,
                        operation.value,
                        resource,
                        success,
                        reason,
                        session_id,
                    ],
                )

                conn.commit()

                # If operation failed, record failed attempt
                if not success:
                    self._record_failed_attempt(user_id, operation.value)

                self.logger.debug(
                    f"Logged access: user={user_id}, operation={operation.value}, "
                    f"success={success}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to log access: {e}")
            return False

    def grant_permission(
        self,
        user_id: str,
        permission: Permission,
        resource: str = None,
        granted_by: str = None,
        expires_at: datetime.datetime = None,
    ) -> bool:
        """
        Grant a permission to a user.

        Args:
            user_id: User identifier
            permission: Permission to grant
            resource: Optional resource identifier
            granted_by: User who granted the permission
            expires_at: Optional expiration time

        Returns:
            True if permission was granted successfully
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Use INSERT OR REPLACE to handle duplicates
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO theme_permissions
                    (user_id, permission, resource, granted_by, expires_at, active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """,
                    [
                        user_id,
                        permission.value,
                        resource,
                        granted_by,
                        expires_at.isoformat() if expires_at else None,
                    ],
                )

                conn.commit()

                self.logger.info(
                    f"Granted permission {permission.value} to user {user_id}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to grant permission: {e}")
            return False

    def revoke_permission(
        self, user_id: str, permission: Permission, resource: str = None
    ) -> bool:
        """
        Revoke a permission from a user.

        Args:
            user_id: User identifier
            permission: Permission to revoke
            resource: Optional resource identifier

        Returns:
            True if permission was revoked successfully
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                query = """
                    UPDATE theme_permissions 
                    SET active = 0 
                    WHERE user_id = ? AND permission = ?
                """
                params = [user_id, permission.value]

                if resource:
                    query += " AND resource = ?"
                    params.append(resource)

                cursor.execute(query, params)
                conn.commit()

                self.logger.info(
                    f"Revoked permission {permission.value} from user {user_id}"
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to revoke permission: {e}")
            return False

    def create_user_role(
        self, user_id: str, role: str, granted_by: str = None
    ) -> bool:
        """
        Assign a predefined role to a user.

        Args:
            user_id: User identifier
            role: Role name ('admin', 'user', 'guest', 'backup_operator')
            granted_by: User who assigned the role

        Returns:
            True if role was assigned successfully
        """
        try:
            if role not in self.default_permissions:
                self.logger.error(f"Unknown role: {role}")
                return False

            # Grant all permissions for the role
            success = True
            for permission in self.default_permissions[role]:
                if not self.grant_permission(
                    user_id, permission, granted_by=granted_by
                ):
                    success = False

            if success:
                self.logger.info(f"Assigned role {role} to user {user_id}")

            return success

        except Exception as e:
            self.logger.error(f"Failed to create user role: {e}")
            return False

    def get_user_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all active permissions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of permission dictionaries
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT permission, resource, granted_by, granted_at, expires_at
                    FROM theme_permissions
                    WHERE user_id = ? AND active = 1
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                    ORDER BY granted_at DESC
                """,
                    [user_id],
                )

                permissions = []
                for row in cursor.fetchall():
                    permissions.append(
                        {
                            "permission": row[0],
                            "resource": row[1],
                            "granted_by": row[2],
                            "granted_at": row[3],
                            "expires_at": row[4],
                        }
                    )

                return permissions

        except Exception as e:
            self.logger.error(f"Failed to get user permissions: {e}")
            return []

    def get_access_log(
        self, user_id: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get access log entries.

        Args:
            user_id: Optional user filter
            limit: Maximum number of entries to return

        Returns:
            List of access log dictionaries
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                if user_id:
                    cursor.execute(
                        """
                        SELECT user_id, operation, resource, success, reason, 
                               ip_address, session_id, timestamp
                        FROM theme_access_log
                        WHERE user_id = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """,
                        [user_id, limit],
                    )
                else:
                    cursor.execute(
                        """
                        SELECT user_id, operation, resource, success, reason,
                               ip_address, session_id, timestamp
                        FROM theme_access_log
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """,
                        [limit],
                    )

                logs = []
                for row in cursor.fetchall():
                    logs.append(
                        {
                            "user_id": row[0],
                            "operation": row[1],
                            "resource": row[2],
                            "success": bool(row[3]),
                            "reason": row[4],
                            "ip_address": row[5],
                            "session_id": row[6],
                            "timestamp": row[7],
                        }
                    )

                return logs

        except Exception as e:
            self.logger.error(f"Failed to get access log: {e}")
            return []

    def _is_user_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Count failed attempts in the lockout window
                lockout_start = datetime.datetime.now() - datetime.timedelta(
                    seconds=self.config["lockout_duration"]
                )

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM theme_failed_attempts
                    WHERE user_id = ? AND timestamp > ?
                """,
                    [user_id, lockout_start.isoformat()],
                )

                failed_count = cursor.fetchone()[0]
                return failed_count >= self.config["max_failed_attempts"]

        except Exception as e:
            self.logger.error(f"Failed to check lockout status: {e}")
            return False

    def _is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Count requests in the rate limit window
                window_start = datetime.datetime.now() - datetime.timedelta(
                    seconds=self.config["rate_limit_window"]
                )

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM theme_access_log
                    WHERE user_id = ? AND timestamp > ?
                """,
                    [user_id, window_start.isoformat()],
                )

                request_count = cursor.fetchone()[0]
                return request_count >= self.config["rate_limit_max_requests"]

        except Exception as e:
            self.logger.error(f"Failed to check rate limit: {e}")
            return False

    def _record_failed_attempt(self, user_id: str, operation: str) -> None:
        """Record a failed access attempt."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO theme_failed_attempts (user_id, operation)
                    VALUES (?, ?)
                """,
                    [user_id, operation],
                )

                conn.commit()

        except Exception as e:
            self.logger.error(f"Failed to record failed attempt: {e}")

    def cleanup_old_logs(self, retention_days: int = None) -> int:
        """
        Clean up old access logs.

        Args:
            retention_days: Number of days to retain logs

        Returns:
            Number of deleted log entries
        """
        try:
            if retention_days is None:
                retention_days = self.config["audit_retention_days"]

            cutoff_date = datetime.datetime.now() - datetime.timedelta(
                days=retention_days
            )

            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()

                # Delete old access logs
                cursor.execute(
                    """
                    DELETE FROM theme_access_log
                    WHERE timestamp < ?
                """,
                    [cutoff_date.isoformat()],
                )

                deleted_count = cursor.rowcount

                # Delete old failed attempts
                cursor.execute(
                    """
                    DELETE FROM theme_failed_attempts
                    WHERE timestamp < ?
                """,
                    [cutoff_date.isoformat()],
                )

                conn.commit()

                self.logger.info(f"Cleaned up {deleted_count} old log entries")
                return deleted_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")
            return 0
