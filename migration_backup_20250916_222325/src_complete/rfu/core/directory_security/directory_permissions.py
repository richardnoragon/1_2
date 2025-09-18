"""
Directory Permission Manager for RFU Hub

Manages directory access permissions with role-based access control
and authorization for directory preferences.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

from ..database.database_manager import DatabaseManager


class PermissionLevel(Enum):
    """Directory permission levels"""
    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 3
    ADMIN = 4


class DirectoryRole(Enum):
    """Directory access roles"""
    GUEST = "guest"
    USER = "user"
    POWER_USER = "power_user"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class PermissionCheckResult:
    """Result of permission check operation"""
    authorized: bool
    permission_level: PermissionLevel
    reason: Optional[str] = None
    role: Optional[DirectoryRole] = None
    restrictions: Optional[List[str]] = None


@dataclass
class DirectoryPermission:
    """Directory permission entry"""
    user_id: str
    resource_path: str
    permission_level: PermissionLevel
    role: DirectoryRole
    granted_by: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    restrictions: Optional[Dict] = None


class DirectoryPermissionManager:
    """
    Manages directory access permissions with role-based access control
    and authorization for directory preferences.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize DirectoryPermissionManager
        
        Args:
            database_manager: Database manager instance
        """
        self.db_manager = database_manager
        self.logger = logging.getLogger('RFU.DirectoryPermissionManager')
        
        # Role hierarchy (higher roles inherit lower role permissions)
        self.role_hierarchy = {
            DirectoryRole.GUEST: 0,
            DirectoryRole.USER: 1,
            DirectoryRole.POWER_USER: 2,
            DirectoryRole.ADMIN: 3,
            DirectoryRole.SYSTEM: 4
        }
        
        # Default permissions for each role
        self.default_role_permissions = {
            DirectoryRole.GUEST: PermissionLevel.READ,
            DirectoryRole.USER: PermissionLevel.WRITE,
            DirectoryRole.POWER_USER: PermissionLevel.DELETE,
            DirectoryRole.ADMIN: PermissionLevel.ADMIN,
            DirectoryRole.SYSTEM: PermissionLevel.ADMIN
        }
        
        # Permission action mappings
        self.action_permissions = {
            'read': PermissionLevel.READ,
            'write': PermissionLevel.WRITE,
            'delete': PermissionLevel.DELETE,
            'admin': PermissionLevel.ADMIN
        }
        
        self.logger.info("DirectoryPermissionManager initialized successfully")
    
    def check_directory_permission(self, user_id: str, resource_path: str, 
                                  action: str) -> PermissionCheckResult:
        """
        Check if user has permission to perform action on directory resource
        
        Args:
            user_id: User identifier
            resource_path: Directory path or hash
            action: Action to perform ('read', 'write', 'delete', 'admin')
            
        Returns:
            PermissionCheckResult with authorization outcome
        """
        try:
            self.logger.debug(
                f"Checking permission for user {user_id[:8]}... "
                f"action {action}"
            )
            
            # Get required permission level for action
            required_permission = self.action_permissions.get(
                action.lower(), PermissionLevel.ADMIN
            )
            
            # Get user's role and permissions
            user_role = self._get_user_role(user_id)
            user_permissions = self._get_user_permissions(user_id, resource_path)
            
            # Check explicit permissions first
            if user_permissions:
                for permission in user_permissions:
                    if self._is_permission_valid(permission):
                        if permission.permission_level.value >= required_permission.value:
                            return PermissionCheckResult(
                                authorized=True,
                                permission_level=permission.permission_level,
                                role=permission.role,
                                restrictions=self._get_permission_restrictions(permission)
                            )
            
            # Check role-based permissions
            role_permission = self._check_role_permission(user_role, required_permission)
            if role_permission.authorized:
                return role_permission
            
            # Check if user is accessing their own data
            if self._is_user_own_data(user_id, resource_path):
                # Users can always read/write their own directory preferences
                if required_permission.value <= PermissionLevel.WRITE.value:
                    return PermissionCheckResult(
                        authorized=True,
                        permission_level=PermissionLevel.WRITE,
                        role=user_role,
                        reason="Own data access"
                    )
            
            # Default deny
            return PermissionCheckResult(
                authorized=False,
                permission_level=PermissionLevel.NONE,
                reason=f"Insufficient permissions for action: {action}",
                role=user_role
            )
            
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return PermissionCheckResult(
                authorized=False,
                permission_level=PermissionLevel.NONE,
                reason=f"Permission check error: {e}"
            )
    
    def grant_directory_permission(self, user_id: str, resource_path: str,
                                  permission_level: PermissionLevel,
                                  granted_by: str,
                                  expires_at: Optional[datetime] = None,
                                  restrictions: Optional[Dict] = None) -> bool:
        """
        Grant directory permission to user
        
        Args:
            user_id: User to grant permission to
            resource_path: Directory path or hash
            permission_level: Permission level to grant
            granted_by: User granting the permission
            expires_at: Optional expiration time
            restrictions: Optional permission restrictions
            
        Returns:
            True if permission granted successfully, False otherwise
        """
        try:
            # Check if granter has admin permissions
            granter_check = self.check_directory_permission(
                granted_by, resource_path, 'admin'
            )
            
            if not granter_check.authorized:
                self.logger.warning(
                    f"Permission grant denied: {granted_by} lacks admin rights"
                )
                return False
            
            # Get user's current role
            user_role = self._get_user_role(user_id)
            
            # Store permission in database
            success = self._store_permission(
                user_id=user_id,
                resource_path=resource_path,
                permission_level=permission_level,
                role=user_role,
                granted_by=granted_by,
                expires_at=expires_at,
                restrictions=restrictions
            )
            
            if success:
                self.logger.info(
                    f"Permission granted: {permission_level.name} to "
                    f"user {user_id[:8]}... by {granted_by[:8]}..."
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Permission grant failed: {e}")
            return False
    
    def revoke_directory_permission(self, user_id: str, resource_path: str,
                                   revoked_by: str) -> bool:
        """
        Revoke directory permission from user
        
        Args:
            user_id: User to revoke permission from
            resource_path: Directory path or hash
            revoked_by: User revoking the permission
            
        Returns:
            True if permission revoked successfully, False otherwise
        """
        try:
            # Check if revoker has admin permissions
            revoker_check = self.check_directory_permission(
                revoked_by, resource_path, 'admin'
            )
            
            if not revoker_check.authorized:
                self.logger.warning(
                    f"Permission revocation denied: {revoked_by} lacks admin rights"
                )
                return False
            
            # Remove permission from database
            success = self._remove_permission(user_id, resource_path)
            
            if success:
                self.logger.info(
                    f"Permission revoked from user {user_id[:8]}... "
                    f"by {revoked_by[:8]}..."
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Permission revocation failed: {e}")
            return False
    
    def set_user_role(self, user_id: str, role: DirectoryRole,
                     assigned_by: str) -> bool:
        """
        Set user's directory access role
        
        Args:
            user_id: User to assign role to
            role: Role to assign
            assigned_by: User assigning the role
            
        Returns:
            True if role assigned successfully, False otherwise
        """
        try:
            # Check if assigner has admin permissions
            if not self._is_system_admin(assigned_by):
                self.logger.warning(
                    f"Role assignment denied: {assigned_by} lacks admin rights"
                )
                return False
            
            # Store role in database
            success = self._store_user_role(user_id, role, assigned_by)
            
            if success:
                self.logger.info(
                    f"Role {role.value} assigned to user {user_id[:8]}... "
                    f"by {assigned_by[:8]}..."
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Role assignment failed: {e}")
            return False
    
    def get_user_permissions(self, user_id: str) -> List[DirectoryPermission]:
        """
        Get all permissions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of DirectoryPermission objects
        """
        try:
            return self._get_all_user_permissions(user_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get user permissions: {e}")
            return []
    
    def cleanup_expired_permissions(self) -> int:
        """
        Clean up expired permissions
        
        Returns:
            Number of permissions cleaned up
        """
        try:
            count = self._remove_expired_permissions()
            if count > 0:
                self.logger.info(f"Cleaned up {count} expired permissions")
            return count
            
        except Exception as e:
            self.logger.error(f"Permission cleanup failed: {e}")
            return 0
    
    def _get_user_role(self, user_id: str) -> DirectoryRole:
        """Get user's directory access role"""
        try:
            query = """
            SELECT role FROM directory_user_roles 
            WHERE user_id = ? AND active = 1
            """
            result = self.db_manager.fetch_one(query, (user_id,))
            
            if result:
                return DirectoryRole(result[0])
            else:
                # Default role for new users
                return DirectoryRole.USER
                
        except Exception:
            # Fallback to guest role on error
            return DirectoryRole.GUEST
    
    def _get_user_permissions(self, user_id: str, 
                             resource_path: str) -> List[DirectoryPermission]:
        """Get user's explicit permissions for resource"""
        try:
            query = """
            SELECT user_id, resource_path, permission_level, role, granted_by,
                   granted_at, expires_at, restrictions
            FROM directory_permissions 
            WHERE user_id = ? AND (resource_path = ? OR resource_path = '*')
            AND active = 1
            """
            results = self.db_manager.fetch_all(query, (user_id, resource_path))
            
            permissions = []
            for result in results:
                permission = DirectoryPermission(
                    user_id=result[0],
                    resource_path=result[1],
                    permission_level=PermissionLevel(result[2]),
                    role=DirectoryRole(result[3]),
                    granted_by=result[4],
                    granted_at=datetime.fromisoformat(result[5]),
                    expires_at=datetime.fromisoformat(result[6]) if result[6] else None,
                    restrictions=eval(result[7]) if result[7] else None
                )
                permissions.append(permission)
            
            return permissions
            
        except Exception as e:
            self.logger.error(f"Failed to get user permissions: {e}")
            return []
    
    def _check_role_permission(self, role: DirectoryRole,
                              required_permission: PermissionLevel) -> PermissionCheckResult:
        """Check if role has required permission level"""
        
        role_permission = self.default_role_permissions.get(
            role, PermissionLevel.NONE
        )
        
        if role_permission.value >= required_permission.value:
            return PermissionCheckResult(
                authorized=True,
                permission_level=role_permission,
                role=role,
                reason="Role-based access"
            )
        else:
            return PermissionCheckResult(
                authorized=False,
                permission_level=role_permission,
                role=role,
                reason=f"Role {role.value} insufficient for required permission"
            )
    
    def _is_permission_valid(self, permission: DirectoryPermission) -> bool:
        """Check if permission is still valid"""
        
        # Check if permission has expired
        if permission.expires_at and datetime.utcnow() > permission.expires_at:
            return False
        
        # Check restrictions
        if permission.restrictions:
            # Could implement time-based, IP-based, or other restrictions
            pass
        
        return True
    
    def _is_user_own_data(self, user_id: str, resource_path: str) -> bool:
        """Check if resource belongs to the user"""
        try:
            # Check if this is the user's own directory preference
            query = """
            SELECT COUNT(*) FROM secure_directories 
            WHERE user_id = ? AND path_hash = ?
            """
            result = self.db_manager.fetch_one(query, (user_id, resource_path))
            
            return result and result[0] > 0
            
        except Exception:
            return False
    
    def _is_system_admin(self, user_id: str) -> bool:
        """Check if user is a system administrator"""
        role = self._get_user_role(user_id)
        return role in [DirectoryRole.ADMIN, DirectoryRole.SYSTEM]
    
    def _store_permission(self, user_id: str, resource_path: str,
                         permission_level: PermissionLevel, role: DirectoryRole,
                         granted_by: str, expires_at: Optional[datetime],
                         restrictions: Optional[Dict]) -> bool:
        """Store permission in database"""
        try:
            query = """
            INSERT OR REPLACE INTO directory_permissions 
            (user_id, resource_path, permission_level, role, granted_by,
             granted_at, expires_at, restrictions, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """
            
            params = (
                user_id,
                resource_path,
                permission_level.value,
                role.value,
                granted_by,
                datetime.utcnow().isoformat(),
                expires_at.isoformat() if expires_at else None,
                str(restrictions) if restrictions else None
            )
            
            self.db_manager.execute_query(query, params)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store permission: {e}")
            return False
    
    def _remove_permission(self, user_id: str, resource_path: str) -> bool:
        """Remove permission from database"""
        try:
            query = """
            UPDATE directory_permissions 
            SET active = 0, revoked_at = ?
            WHERE user_id = ? AND resource_path = ?
            """
            
            self.db_manager.execute_query(
                query, 
                (datetime.utcnow().isoformat(), user_id, resource_path)
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove permission: {e}")
            return False
    
    def _store_user_role(self, user_id: str, role: DirectoryRole,
                        assigned_by: str) -> bool:
        """Store user role in database"""
        try:
            # Deactivate existing roles
            deactivate_query = """
            UPDATE directory_user_roles 
            SET active = 0 
            WHERE user_id = ?
            """
            self.db_manager.execute_query(deactivate_query, (user_id,))
            
            # Insert new role
            insert_query = """
            INSERT INTO directory_user_roles 
            (user_id, role, assigned_by, assigned_at, active)
            VALUES (?, ?, ?, ?, 1)
            """
            
            self.db_manager.execute_query(
                insert_query,
                (user_id, role.value, assigned_by, datetime.utcnow().isoformat())
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store user role: {e}")
            return False
    
    def _get_all_user_permissions(self, user_id: str) -> List[DirectoryPermission]:
        """Get all permissions for a user"""
        try:
            query = """
            SELECT user_id, resource_path, permission_level, role, granted_by,
                   granted_at, expires_at, restrictions
            FROM directory_permissions 
            WHERE user_id = ? AND active = 1
            ORDER BY granted_at DESC
            """
            results = self.db_manager.fetch_all(query, (user_id,))
            
            permissions = []
            for result in results:
                permission = DirectoryPermission(
                    user_id=result[0],
                    resource_path=result[1],
                    permission_level=PermissionLevel(result[2]),
                    role=DirectoryRole(result[3]),
                    granted_by=result[4],
                    granted_at=datetime.fromisoformat(result[5]),
                    expires_at=datetime.fromisoformat(result[6]) if result[6] else None,
                    restrictions=eval(result[7]) if result[7] else None
                )
                permissions.append(permission)
            
            return permissions
            
        except Exception as e:
            self.logger.error(f"Failed to get all user permissions: {e}")
            return []
    
    def _remove_expired_permissions(self) -> int:
        """Remove expired permissions"""
        try:
            query = """
            UPDATE directory_permissions 
            SET active = 0, revoked_at = ?
            WHERE expires_at < ? AND active = 1
            """
            
            now = datetime.utcnow().isoformat()
            result = self.db_manager.execute_query(query, (now, now))
            
            # Return number of affected rows
            return result.rowcount if hasattr(result, 'rowcount') else 0
            
        except Exception as e:
            self.logger.error(f"Failed to remove expired permissions: {e}")
            return 0
    
    def _get_permission_restrictions(self, 
                                   permission: DirectoryPermission) -> List[str]:
        """Get list of restrictions for permission"""
        restrictions = []
        
        if permission.expires_at:
            restrictions.append(f"Expires: {permission.expires_at}")
        
        if permission.restrictions:
            for key, value in permission.restrictions.items():
                restrictions.append(f"{key}: {value}")
        
        return restrictions