"""
Database models and data classes for Richard's File Utilities.

This module defines data models for all database tables to ensure
type safety and consistent data handling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import json


@dataclass
class AppSetting:
    """Model for application settings."""
    id: Optional[int] = None
    section: str = ""
    key: str = ""
    value: str = ""
    value_type: str = "string"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'section': self.section,
            'key': self.key,
            'value': self.value,
            'value_type': self.value_type,
            'created_at': (self.created_at.isoformat()
                           if self.created_at else None),
            'updated_at': (self.updated_at.isoformat()
                           if self.updated_at else None)
        }


@dataclass
class FileHistory:
    """Model for file history tracking."""
    id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    directory_path: str = ""
    access_count: int = 1
    last_accessed: Optional[datetime] = None
    first_accessed: Optional[datetime] = None
    tool_name: Optional[str] = None
    operation_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'file_path': self.file_path,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'directory_path': self.directory_path,
            'access_count': self.access_count,
            'last_accessed': (self.last_accessed.isoformat()
                              if self.last_accessed else None),
            'first_accessed': (self.first_accessed.isoformat()
                               if self.first_accessed else None),
            'tool_name': self.tool_name,
            'operation_type': self.operation_type,
            'metadata': json.dumps(self.metadata) if self.metadata else None
        }


@dataclass
class DirectoryHistory:
    """Model for directory history tracking."""
    id: Optional[int] = None
    directory_path: str = ""
    access_count: int = 1
    last_accessed: Optional[datetime] = None
    first_accessed: Optional[datetime] = None
    is_favorite: bool = False
    tool_name: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'directory_path': self.directory_path,
            'access_count': self.access_count,
            'last_accessed': (self.last_accessed.isoformat()
                              if self.last_accessed else None),
            'first_accessed': (self.first_accessed.isoformat()
                               if self.first_accessed else None),
            'is_favorite': self.is_favorite,
            'tool_name': self.tool_name,
            'metadata': json.dumps(self.metadata) if self.metadata else None
        }


@dataclass
class AppLog:
    """Model for application logging."""
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    level: str = ""
    logger_name: str = ""
    message: str = ""
    module: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    tool_name: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'timestamp': (self.timestamp.isoformat()
                          if self.timestamp else None),
            'level': self.level,
            'logger_name': self.logger_name,
            'message': self.message,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'tool_name': self.tool_name,
            'session_id': self.session_id,
            'metadata': json.dumps(self.metadata) if self.metadata else None
        }


@dataclass
class ToolUsage:
    """Model for tool usage statistics."""
    id: Optional[int] = None
    tool_name: str = ""
    operation_type: Optional[str] = None
    usage_count: int = 1
    last_used: Optional[datetime] = None
    first_used: Optional[datetime] = None
    success_count: int = 0
    error_count: int = 0
    total_execution_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'tool_name': self.tool_name,
            'operation_type': self.operation_type,
            'usage_count': self.usage_count,
            'last_used': (self.last_used.isoformat()
                          if self.last_used else None),
            'first_used': (self.first_used.isoformat()
                           if self.first_used else None),
            'success_count': self.success_count,
            'error_count': self.error_count,
            'total_execution_time_ms': self.total_execution_time_ms,
            'metadata': json.dumps(self.metadata) if self.metadata else None
        }


@dataclass
class UserPreference:
    """Model for user preferences."""
    id: Optional[int] = None
    user_id: str = "default"
    preference_category: str = ""
    preference_key: str = ""
    preference_value: str = ""
    value_type: str = "string"
    is_encrypted: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'user_id': self.user_id,
            'preference_category': self.preference_category,
            'preference_key': self.preference_key,
            'preference_value': self.preference_value,
            'value_type': self.value_type,
            'is_encrypted': self.is_encrypted,
            'created_at': (self.created_at.isoformat()
                           if self.created_at else None),
            'updated_at': (self.updated_at.isoformat()
                           if self.updated_at else None)
        }
