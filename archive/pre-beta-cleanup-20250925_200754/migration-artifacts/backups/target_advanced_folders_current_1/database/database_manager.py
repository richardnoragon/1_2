"""
Advanced Folders Database Integration Manager.

This module integrates Advanced Folders with the existing RFU database
system, extending the DatabaseManager with Advanced Folders-specific
functionality while maintaining compatibility.
"""

import logging
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..database.advanced_folders_schema import AdvancedFoldersSchema
from ..models.folder_models import (FileMetadata, FolderConfiguration,
                                    ParameterOperator, ParameterType,
                                    ScanStatus, SearchParameter)

logger = logging.getLogger('RFU.AdvancedFolders.DatabaseManager')


class AdvancedFoldersDBManager:
    """
    Database manager for Advanced Folders functionality.
    
    Extends the existing RFU database with Advanced Folders tables
    and provides CRUD operations for folder configurations and metadata.
    """
    
    def __init__(self, rfu_database_manager=None):
        """
        Initialize the Advanced Folders database manager.
        
        Args:
            rfu_database_manager: Existing RFU DatabaseManager instance
        """
        self.rfu_db = rfu_database_manager
        self.logger = logging.getLogger('RFU.AdvancedFolders.DB')
        self.session_id = str(uuid.uuid4())
        
        # Initialize schema if database manager is available
        if self.rfu_db:
            self._initialize_advanced_folders_schema()
        else:
            self.logger.warning("No RFU database manager provided")
    
    def _initialize_advanced_folders_schema(self) -> None:
        """Initialize Advanced Folders schema in the RFU database."""
        try:
            with self.rfu_db.get_connection() as conn:
                # Create Advanced Folders tables
                AdvancedFoldersSchema.create_advanced_folders_schema(conn)
                
                # Create indexes for performance
                AdvancedFoldersSchema.create_advanced_folders_indexes(conn)
                
                # Create triggers for automation
                AdvancedFoldersSchema.create_advanced_folders_triggers(conn)
                
                conn.commit()
                
            self.logger.info("Advanced Folders schema initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Advanced Folders schema: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from RFU database manager."""
        if self.rfu_db:
            with self.rfu_db.get_connection() as conn:
                yield conn
        else:
            raise RuntimeError("No database manager available")
    
    def create_folder_configuration(self, config: FolderConfiguration) -> bool:
        """
        Create a new folder configuration in the database.
        
        Args:
            config: FolderConfiguration instance to create
            
        Returns:
            bool: True if creation was successful
        """
        try:
            with self.get_connection() as conn:
                # Insert folder configuration
                conn.execute("""
                    INSERT INTO folder_configurations (
                        folder_id, folder_name, description, is_active,
                        created_at, updated_at, created_by, scan_status,
                        total_files, total_size_bytes, configuration_version,
                        metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    config.folder_id,
                    config.folder_name,
                    config.description,
                    config.is_active,
                    config.created_at.isoformat(),
                    config.updated_at.isoformat(),
                    config.created_by,
                    config.scan_status.value,
                    config.total_files,
                    config.total_size_bytes,
                    config.configuration_version,
                    str(config.metadata)
                ))
                
                # Insert search parameters
                for param in config.search_parameters:
                    self._insert_search_parameter(conn, config.folder_id, param)
                
                conn.commit()
                
            self.logger.info(f"Created folder configuration: {config.folder_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create folder configuration: {e}")
            return False
    
    def _insert_search_parameter(self, conn: sqlite3.Connection,
                                folder_id: str, param: SearchParameter) -> None:
        """Insert a search parameter into the database."""
        conn.execute("""
            INSERT INTO search_parameters (
                parameter_id, folder_id, parameter_type, parameter_key,
                parameter_value, parameter_operator, is_enabled,
                priority_order, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            param.parameter_id,
            folder_id,
            param.parameter_type.value,
            param.parameter_key,
            param.parameter_value,
            param.parameter_operator.value,
            param.is_enabled,
            param.priority_order,
            param.created_at.isoformat(),
            param.updated_at.isoformat()
        ))
    
    def get_folder_configuration(self, folder_id: str) -> Optional[FolderConfiguration]:
        """
        Get a folder configuration by ID.
        
        Args:
            folder_id: ID of the configuration to retrieve
            
        Returns:
            FolderConfiguration instance or None if not found
        """
        try:
            with self.get_connection() as conn:
                # Get folder configuration
                cursor = conn.execute("""
                    SELECT folder_id, folder_name, description, is_active,
                           created_at, updated_at, created_by, last_scan_at,
                           scan_status, total_files, total_size_bytes,
                           configuration_version, metadata_json
                    FROM folder_configurations
                    WHERE folder_id = ?
                """, (folder_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                # Create configuration object
                config_data = {
                    'folder_id': row[0],
                    'folder_name': row[1],
                    'description': row[2] or '',
                    'is_active': bool(row[3]),
                    'created_at': datetime.fromisoformat(row[4]),
                    'updated_at': datetime.fromisoformat(row[5]),
                    'created_by': row[6],
                    'last_scan_at': (datetime.fromisoformat(row[7])
                                   if row[7] else None),
                    'scan_status': ScanStatus(row[8]),
                    'total_files': row[9],
                    'total_size_bytes': row[10],
                    'configuration_version': row[11],
                    'metadata': eval(row[12]) if row[12] else {}
                }
                
                config = FolderConfiguration(**config_data)
                
                # Get search parameters
                config.search_parameters = self._get_search_parameters(
                    conn, folder_id)
                
                return config
                
        except Exception as e:
            self.logger.error(f"Failed to get folder configuration: {e}")
            return None
    
    def _get_search_parameters(self, conn: sqlite3.Connection,
                              folder_id: str) -> List[SearchParameter]:
        """Get search parameters for a folder configuration."""
        cursor = conn.execute("""
            SELECT parameter_id, parameter_type, parameter_key,
                   parameter_value, parameter_operator, is_enabled,
                   priority_order, created_at, updated_at
            FROM search_parameters
            WHERE folder_id = ?
            ORDER BY priority_order, created_at
        """, (folder_id,))
        
        parameters = []
        for row in cursor.fetchall():
            param_data = {
                'parameter_id': row[0],
                'parameter_type': ParameterType(row[1]),
                'parameter_key': row[2],
                'parameter_value': row[3],
                'parameter_operator': ParameterOperator(row[4]),
                'is_enabled': bool(row[5]),
                'priority_order': row[6],
                'created_at': datetime.fromisoformat(row[7]),
                'updated_at': datetime.fromisoformat(row[8])
            }
            parameters.append(SearchParameter(**param_data))
        
        return parameters
    
    def update_folder_configuration(self, config: FolderConfiguration) -> bool:
        """
        Update an existing folder configuration.
        
        Args:
            config: Updated FolderConfiguration instance
            
        Returns:
            bool: True if update was successful
        """
        try:
            with self.get_connection() as conn:
                # Update folder configuration
                config.updated_at = datetime.now()
                
                conn.execute("""
                    UPDATE folder_configurations
                    SET folder_name = ?, description = ?, is_active = ?,
                        updated_at = ?, scan_status = ?, total_files = ?,
                        total_size_bytes = ?, configuration_version = ?,
                        metadata_json = ?
                    WHERE folder_id = ?
                """, (
                    config.folder_name,
                    config.description,
                    config.is_active,
                    config.updated_at.isoformat(),
                    config.scan_status.value,
                    config.total_files,
                    config.total_size_bytes,
                    config.configuration_version,
                    str(config.metadata),
                    config.folder_id
                ))
                
                # Delete existing search parameters
                conn.execute("""
                    DELETE FROM search_parameters WHERE folder_id = ?
                """, (config.folder_id,))
                
                # Insert updated search parameters
                for param in config.search_parameters:
                    self._insert_search_parameter(conn, config.folder_id, param)
                
                conn.commit()
                
            self.logger.info(f"Updated folder configuration: {config.folder_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update folder configuration: {e}")
            return False
    
    def delete_folder_configuration(self, folder_id: str) -> bool:
        """
        Delete a folder configuration.
        
        Args:
            folder_id: ID of configuration to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            with self.get_connection() as conn:
                # Delete configuration (cascades to search parameters)
                cursor = conn.execute("""
                    DELETE FROM folder_configurations WHERE folder_id = ?
                """, (folder_id,))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted folder configuration: {folder_id}")
                    return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete folder configuration: {e}")
        
        return False
    
    def list_folder_configurations(self, active_only: bool = True) -> List[FolderConfiguration]:
        """
        List all folder configurations.
        
        Args:
            active_only: If True, only return active configurations
            
        Returns:
            List of FolderConfiguration instances
        """
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT folder_id FROM folder_configurations
                """
                if active_only:
                    query += " WHERE is_active = 1"
                query += " ORDER BY folder_name"
                
                cursor = conn.execute(query)
                folder_ids = [row[0] for row in cursor.fetchall()]
                
                # Get full configurations
                configurations = []
                for folder_id in folder_ids:
                    config = self.get_folder_configuration(folder_id)
                    if config:
                        configurations.append(config)
                
                return configurations
                
        except Exception as e:
            self.logger.error(f"Failed to list folder configurations: {e}")
            return []
    
    def insert_file_metadata(self, folder_id: str, 
                           metadata: FileMetadata) -> bool:
        """
        Insert file metadata into the index.
        
        Args:
            folder_id: ID of the folder configuration
            metadata: FileMetadata instance
            
        Returns:
            bool: True if insertion was successful
        """
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO file_metadata_index (
                        file_id, folder_id, file_path, file_name,
                        file_extension, directory_path, file_size,
                        created_date, modified_date, accessed_date,
                        file_hash, mime_type, file_permissions,
                        is_hidden, is_system, content_summary,
                        metadata_extracted_at, scan_session_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metadata.file_id,
                    folder_id,
                    metadata.file_path,
                    metadata.file_name,
                    metadata.file_extension,
                    metadata.directory_path,
                    metadata.file_size,
                    (metadata.created_date.isoformat()
                     if metadata.created_date else None),
                    (metadata.modified_date.isoformat()
                     if metadata.modified_date else None),
                    (metadata.accessed_date.isoformat()
                     if metadata.accessed_date else None),
                    metadata.file_hash,
                    metadata.mime_type,
                    metadata.file_permissions,
                    metadata.is_hidden,
                    metadata.is_system,
                    metadata.content_summary,
                    metadata.metadata_extracted_at.isoformat(),
                    metadata.scan_session_id
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to insert file metadata: {e}")
            return False
    
    def search_files(self, folder_id: str, 
                    search_criteria: Dict[str, Any] = None) -> List[FileMetadata]:
        """
        Search for files in a folder configuration.
        
        Args:
            folder_id: ID of the folder configuration
            search_criteria: Optional search criteria
            
        Returns:
            List of FileMetadata instances
        """
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT file_id, file_path, file_name, file_extension,
                           directory_path, file_size, created_date,
                           modified_date, accessed_date, file_hash,
                           mime_type, file_permissions, is_hidden,
                           is_system, content_summary, metadata_extracted_at,
                           scan_session_id
                    FROM file_metadata_index
                    WHERE folder_id = ?
                """
                params = [folder_id]
                
                # Add search criteria if provided
                if search_criteria:
                    if 'file_extension' in search_criteria:
                        query += " AND file_extension = ?"
                        params.append(search_criteria['file_extension'])
                    
                    if 'min_size' in search_criteria:
                        query += " AND file_size >= ?"
                        params.append(search_criteria['min_size'])
                    
                    if 'max_size' in search_criteria:
                        query += " AND file_size <= ?"
                        params.append(search_criteria['max_size'])
                    
                    if 'name_pattern' in search_criteria:
                        query += " AND file_name LIKE ?"
                        params.append(f"%{search_criteria['name_pattern']}%")
                
                query += " ORDER BY modified_date DESC"
                
                cursor = conn.execute(query, params)
                
                files = []
                for row in cursor.fetchall():
                    metadata_data = {
                        'file_id': row[0],
                        'file_path': row[1],
                        'file_name': row[2],
                        'file_extension': row[3],
                        'directory_path': row[4],
                        'file_size': row[5],
                        'created_date': (datetime.fromisoformat(row[6])
                                       if row[6] else None),
                        'modified_date': (datetime.fromisoformat(row[7])
                                        if row[7] else None),
                        'accessed_date': (datetime.fromisoformat(row[8])
                                        if row[8] else None),
                        'file_hash': row[9],
                        'mime_type': row[10],
                        'file_permissions': row[11],
                        'is_hidden': bool(row[12]),
                        'is_system': bool(row[13]),
                        'content_summary': row[14],
                        'metadata_extracted_at': datetime.fromisoformat(row[15]),
                        'scan_session_id': row[16]
                    }
                    
                    files.append(FileMetadata(**metadata_data))
                
                return files
                
        except Exception as e:
            self.logger.error(f"Failed to search files: {e}")
            return []
    
    def get_performance_metrics(self, folder_id: str = None,
                              operation_type: str = None) -> List[Dict[str, Any]]:
        """
        Get performance metrics.
        
        Args:
            folder_id: Optional folder ID to filter by
            operation_type: Optional operation type to filter by
            
        Returns:
            List of performance metric dictionaries
        """
        try:
            with self.get_connection() as conn:
                query = """
                    SELECT metric_id, folder_id, operation_type,
                           execution_time_ms, files_processed,
                           bytes_processed, memory_usage_mb,
                           cpu_usage_percent, disk_io_operations,
                           operation_status, error_message,
                           recorded_at, session_id, metadata_json
                    FROM performance_metrics
                    WHERE 1=1
                """
                params = []
                
                if folder_id:
                    query += " AND folder_id = ?"
                    params.append(folder_id)
                
                if operation_type:
                    query += " AND operation_type = ?"
                    params.append(operation_type)
                
                query += " ORDER BY recorded_at DESC LIMIT 100"
                
                cursor = conn.execute(query, params)
                
                metrics = []
                for row in cursor.fetchall():
                    metric = {
                        'metric_id': row[0],
                        'folder_id': row[1],
                        'operation_type': row[2],
                        'execution_time_ms': row[3],
                        'files_processed': row[4],
                        'bytes_processed': row[5],
                        'memory_usage_mb': row[6],
                        'cpu_usage_percent': row[7],
                        'disk_io_operations': row[8],
                        'operation_status': row[9],
                        'error_message': row[10],
                        'recorded_at': datetime.fromisoformat(row[11]),
                        'session_id': row[12],
                        'metadata': eval(row[13]) if row[13] else {}
                    }
                    metrics.append(metric)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return []
    
    def record_performance_metric(self, folder_id: str, operation_type: str,
                                execution_time_ms: int, **kwargs) -> bool:
        """
        Record a performance metric.
        
        Args:
            folder_id: ID of folder configuration
            operation_type: Type of operation
            execution_time_ms: Execution time in milliseconds
            **kwargs: Additional metric data
            
        Returns:
            bool: True if recording was successful
        """
        try:
            with self.get_connection() as conn:
                metric_id = str(uuid.uuid4())
                
                conn.execute("""
                    INSERT INTO performance_metrics (
                        metric_id, folder_id, operation_type,
                        execution_time_ms, files_processed,
                        bytes_processed, memory_usage_mb,
                        cpu_usage_percent, disk_io_operations,
                        operation_status, error_message,
                        recorded_at, session_id, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric_id,
                    folder_id,
                    operation_type,
                    execution_time_ms,
                    kwargs.get('files_processed', 0),
                    kwargs.get('bytes_processed', 0),
                    kwargs.get('memory_usage_mb', 0),
                    kwargs.get('cpu_usage_percent', 0.0),
                    kwargs.get('disk_io_operations', 0),
                    kwargs.get('operation_status', 'completed'),
                    kwargs.get('error_message'),
                    datetime.now().isoformat(),
                    self.session_id,
                    str(kwargs.get('metadata', {}))
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to record performance metric: {e}")
            return False