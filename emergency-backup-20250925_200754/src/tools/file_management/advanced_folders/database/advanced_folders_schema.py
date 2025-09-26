"""
Advanced Folders Database Schema Extension for RFU.

This module extends the existing RFU database schema with tables
specifically designed for the Advanced Folders feature, following
enterprise-grade database design patterns.
"""

import logging
import sqlite3
from typing import Any, Dict

logger = logging.getLogger("RFU.AdvancedFolders.Schema")


class AdvancedFoldersSchema:
    """Advanced Folders database schema manager."""

    @staticmethod
    def create_advanced_folders_schema(conn: sqlite3.Connection) -> None:
        """
        Create the complete Advanced Folders database schema.

        Implements enterprise-grade schema design with:
        - Proper normalization and foreign key relationships
        - Comprehensive indexing strategy
        - Performance-optimized data types
        - Audit logging capabilities
        """

        # Folder Configurations Table - Core folder definition
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS folder_configurations (
                folder_id TEXT PRIMARY KEY,
                folder_name TEXT NOT NULL CHECK(length(folder_name) > 0),
                description TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'system',
                last_scan_at TIMESTAMP,
                scan_status TEXT DEFAULT 'pending'
                    CHECK(scan_status IN (
                        'pending', 'scanning', 'completed', 'error')),
                total_files INTEGER DEFAULT 0,
                total_size_bytes INTEGER DEFAULT 0,
                configuration_version INTEGER DEFAULT 1,
                metadata_json TEXT DEFAULT '{}',
                UNIQUE(folder_name)
            )
        """
        )

        # Search Parameters Table - Flexible search configuration
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS search_parameters (
                parameter_id TEXT PRIMARY KEY,
                folder_id TEXT NOT NULL,
                parameter_type TEXT NOT NULL
                    CHECK(parameter_type IN (
                        'directory', 'file_pattern', 'content_search',
                        'date_range', 'size_range', 'file_type', 'exclusion')),
                parameter_key TEXT NOT NULL,
                parameter_value TEXT NOT NULL,
                parameter_operator TEXT DEFAULT 'equals'
                    CHECK(parameter_operator IN (
                        'equals', 'contains', 'starts_with', 'ends_with',
                        'regex', 'greater_than', 'less_than', 'between',
                        'in', 'not_in')),
                is_enabled BOOLEAN DEFAULT TRUE,
                priority_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (folder_id)
                    REFERENCES folder_configurations(folder_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """
        )

        # File Metadata Index - High-performance file metadata storage
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_metadata_index (
                file_id TEXT PRIMARY KEY,
                folder_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_extension TEXT,
                directory_path TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                created_date TIMESTAMP,
                modified_date TIMESTAMP,
                accessed_date TIMESTAMP,
                file_hash TEXT,
                mime_type TEXT,
                file_permissions TEXT,
                is_hidden BOOLEAN DEFAULT FALSE,
                is_system BOOLEAN DEFAULT FALSE,
                content_summary TEXT,
                metadata_extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scan_session_id TEXT,
                FOREIGN KEY (folder_id)
                    REFERENCES folder_configurations(folder_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                UNIQUE(folder_id, file_path)
            )
        """
        )

        # File Metadata Extended - Additional metadata for advanced features
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS file_metadata_extended (
                file_id TEXT PRIMARY KEY,
                file_path_hash TEXT NOT NULL UNIQUE,
                content_preview TEXT,
                extracted_text TEXT,
                image_dimensions TEXT,
                audio_duration INTEGER,
                video_duration INTEGER,
                document_pages INTEGER,
                document_author TEXT,
                document_title TEXT,
                document_subject TEXT,
                document_keywords TEXT,
                custom_tags TEXT,
                user_rating INTEGER DEFAULT 0
                    CHECK(user_rating BETWEEN 0 AND 5),
                last_opened_at TIMESTAMP,
                open_count INTEGER DEFAULT 0,
                metadata_json TEXT DEFAULT '{}',
                extraction_version INTEGER DEFAULT 1,
                extraction_errors TEXT,
                FOREIGN KEY (file_id)
                    REFERENCES file_metadata_index(file_id)
                    ON DELETE CASCADE ON UPDATE CASCADE
            )
        """
        )

        # Search Results Cache - Performance optimization
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS search_results_cache (
                cache_id TEXT PRIMARY KEY,
                folder_id TEXT NOT NULL,
                search_hash TEXT NOT NULL,
                search_parameters_json TEXT NOT NULL,
                result_count INTEGER DEFAULT 0,
                cached_results_json TEXT,
                cache_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                cache_expires_at TIMESTAMP,
                last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1,
                result_size_bytes INTEGER DEFAULT 0,
                FOREIGN KEY (folder_id)
                    REFERENCES folder_configurations(folder_id)
                    ON DELETE CASCADE ON UPDATE CASCADE,
                UNIQUE(folder_id, search_hash)
            )
        """
        )

        # Performance Metrics - System performance monitoring
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id TEXT PRIMARY KEY,
                folder_id TEXT,
                operation_type TEXT NOT NULL
                    CHECK(operation_type IN (
                        'scan', 'search', 'index', 'cache', 'cleanup')),
                execution_time_ms INTEGER NOT NULL,
                files_processed INTEGER DEFAULT 0,
                bytes_processed INTEGER DEFAULT 0,
                memory_usage_mb INTEGER DEFAULT 0,
                cpu_usage_percent REAL DEFAULT 0.0,
                disk_io_operations INTEGER DEFAULT 0,
                operation_status TEXT DEFAULT 'completed'
                    CHECK(operation_status IN (
                        'started', 'completed', 'failed', 'cancelled')),
                error_message TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                metadata_json TEXT DEFAULT '{}',
                FOREIGN KEY (folder_id)
                    REFERENCES folder_configurations(folder_id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            )
        """
        )

        # UI Preferences - User interface customization
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ui_preferences (
                preference_id TEXT PRIMARY KEY,
                user_id TEXT DEFAULT 'default',
                component_name TEXT NOT NULL,
                preference_category TEXT NOT NULL,
                preference_data_json TEXT NOT NULL DEFAULT '{}',
                is_global BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, component_name, preference_category)
            )
        """
        )

        # Folder Configuration Audit - Security and compliance
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS folder_configuration_audit (
                audit_id TEXT PRIMARY KEY,
                folder_id TEXT,
                operation_type TEXT NOT NULL
                    CHECK(operation_type IN (
                        'create', 'update', 'delete', 'scan',
                        'search', 'export', 'import')),
                old_values_json TEXT,
                new_values_json TEXT,
                user_id TEXT DEFAULT 'system',
                ip_address TEXT,
                user_agent TEXT,
                performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                operation_status TEXT DEFAULT 'success'
                    CHECK(operation_status IN (
                        'success', 'failed', 'partial')),
                error_details TEXT,
                FOREIGN KEY (folder_id)
                    REFERENCES folder_configurations(folder_id)
                    ON DELETE SET NULL ON UPDATE CASCADE
            )
        """
        )

        logger.info("Advanced Folders schema created successfully")

    @staticmethod
    def create_advanced_folders_indexes(conn: sqlite3.Connection) -> None:
        """
        Create optimized indexes for Advanced Folders tables.

        Implements comprehensive indexing strategy for:
        - Primary query patterns
        - Join optimization
        - Sort operations
        - Range queries
        """

        indexes = [
            # Folder Configurations Indexes
            """CREATE INDEX IF NOT EXISTS idx_folder_config_name
               ON folder_configurations(folder_name)""",
            """CREATE INDEX IF NOT EXISTS idx_folder_config_active
               ON folder_configurations(is_active, created_at)""",
            """CREATE INDEX IF NOT EXISTS idx_folder_config_scan_status
               ON folder_configurations(scan_status, last_scan_at)""",
            # Search Parameters Indexes
            """CREATE INDEX IF NOT EXISTS idx_search_params_folder
               ON search_parameters(folder_id, is_enabled)""",
            """CREATE INDEX IF NOT EXISTS idx_search_params_type
               ON search_parameters(parameter_type, parameter_key)""",
            """CREATE INDEX IF NOT EXISTS idx_search_params_priority
               ON search_parameters(folder_id, priority_order)""",
            # File Metadata Index - Critical for performance
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_folder
               ON file_metadata_index(folder_id, file_name)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_path
               ON file_metadata_index(file_path)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_ext
               ON file_metadata_index(file_extension, file_size)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_modified
               ON file_metadata_index(modified_date DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_size
               ON file_metadata_index(file_size DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_hash
               ON file_metadata_index(file_hash)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_mime
               ON file_metadata_index(mime_type)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_scan
               ON file_metadata_index(scan_session_id)""",
            # Composite indexes for common queries
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_folder_type
               ON file_metadata_index(folder_id, file_extension,
                                      modified_date DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_file_metadata_folder_size
               ON file_metadata_index(folder_id, file_size DESC,
                                      file_name)""",
            # File Metadata Extended Indexes
            """CREATE INDEX IF NOT EXISTS idx_file_ext_hash
               ON file_metadata_extended(file_path_hash)""",
            """CREATE INDEX IF NOT EXISTS idx_file_ext_rating
               ON file_metadata_extended(user_rating DESC,
                                        last_opened_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_file_ext_opens
               ON file_metadata_extended(open_count DESC)""",
            # Search Cache Indexes
            """CREATE INDEX IF NOT EXISTS idx_search_cache_folder
               ON search_results_cache(folder_id, cache_created_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_search_cache_hash
               ON search_results_cache(search_hash)""",
            """CREATE INDEX IF NOT EXISTS idx_search_cache_expires
               ON search_results_cache(cache_expires_at)""",
            """CREATE INDEX IF NOT EXISTS idx_search_cache_access
               ON search_results_cache(last_accessed_at DESC,
                                      access_count DESC)""",
            # Performance Metrics Indexes
            """CREATE INDEX IF NOT EXISTS idx_perf_metrics_folder
               ON performance_metrics(folder_id, recorded_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_perf_metrics_operation
               ON performance_metrics(operation_type, recorded_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_perf_metrics_execution_time
               ON performance_metrics(execution_time_ms DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_perf_metrics_session
               ON performance_metrics(session_id)""",
            # UI Preferences Indexes
            """CREATE INDEX IF NOT EXISTS idx_ui_pref_user
               ON ui_preferences(user_id, component_name)""",
            """CREATE INDEX IF NOT EXISTS idx_ui_pref_component
               ON ui_preferences(component_name, preference_category)""",
            # Audit Log Indexes
            """CREATE INDEX IF NOT EXISTS idx_audit_folder
               ON folder_configuration_audit(folder_id, performed_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_audit_operation
               ON folder_configuration_audit(operation_type,
                                             performed_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_audit_user
               ON folder_configuration_audit(user_id, performed_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_audit_session
               ON folder_configuration_audit(session_id)""",
            """CREATE INDEX IF NOT EXISTS idx_audit_status
               ON folder_configuration_audit(operation_status,
                                             performed_at DESC)""",
        ]

        for index_sql in indexes:
            try:
                conn.execute(index_sql)
                index_name = index_sql.split()[4]  # Extract index name
                logger.debug(f"Created index: {index_name}")
            except Exception as e:
                logger.error(f"Failed to create index {index_sql}: {e}")

        logger.info("Advanced Folders indexes created successfully")

    @staticmethod
    def create_advanced_folders_indexes(conn: sqlite3.Connection) -> None:
        """
        Create optimized indexes for Advanced Folders tables.

        Implements comprehensive indexing strategy for:
        - Primary query patterns
        - Join optimization
        - Sort operations
        - Range queries
        """

        indexes = [
            # Folder Configurations Indexes
            "CREATE INDEX IF NOT EXISTS idx_folder_config_name ON folder_configurations(folder_name)",
            "CREATE INDEX IF NOT EXISTS idx_folder_config_active ON folder_configurations(is_active, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_folder_config_scan_status ON folder_configurations(scan_status, last_scan_at)",
            # Search Parameters Indexes
            "CREATE INDEX IF NOT EXISTS idx_search_params_folder ON search_parameters(folder_id, is_enabled)",
            "CREATE INDEX IF NOT EXISTS idx_search_params_type ON search_parameters(parameter_type, parameter_key)",
            "CREATE INDEX IF NOT EXISTS idx_search_params_priority ON search_parameters(folder_id, priority_order)",
            # File Metadata Index - Critical for performance
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_folder ON file_metadata_index(folder_id, file_name)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_path ON file_metadata_index(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_ext ON file_metadata_index(file_extension, file_size)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_modified ON file_metadata_index(modified_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_size ON file_metadata_index(file_size DESC)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_hash ON file_metadata_index(file_hash)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_mime ON file_metadata_index(mime_type)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_scan ON file_metadata_index(scan_session_id)",
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_folder_type ON file_metadata_index(folder_id, file_extension, modified_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_file_metadata_folder_size ON file_metadata_index(folder_id, file_size DESC, file_name)",
            # File Metadata Extended Indexes
            "CREATE INDEX IF NOT EXISTS idx_file_ext_hash ON file_metadata_extended(file_path_hash)",
            "CREATE INDEX IF NOT EXISTS idx_file_ext_rating ON file_metadata_extended(user_rating DESC, last_opened_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_file_ext_opens ON file_metadata_extended(open_count DESC)",
            # Search Cache Indexes
            "CREATE INDEX IF NOT EXISTS idx_search_cache_folder ON search_results_cache(folder_id, cache_created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_hash ON search_results_cache(search_hash)",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_expires ON search_results_cache(cache_expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_search_cache_access ON search_results_cache(last_accessed_at DESC, access_count DESC)",
            # Performance Metrics Indexes
            "CREATE INDEX IF NOT EXISTS idx_perf_metrics_folder ON performance_metrics(folder_id, recorded_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_perf_metrics_operation ON performance_metrics(operation_type, recorded_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_perf_metrics_execution_time ON performance_metrics(execution_time_ms DESC)",
            "CREATE INDEX IF NOT EXISTS idx_perf_metrics_session ON performance_metrics(session_id)",
            # UI Preferences Indexes
            "CREATE INDEX IF NOT EXISTS idx_ui_pref_user ON ui_preferences(user_id, component_name)",
            "CREATE INDEX IF NOT EXISTS idx_ui_pref_component ON ui_preferences(component_name, preference_category)",
            # Audit Log Indexes
            "CREATE INDEX IF NOT EXISTS idx_audit_folder ON folder_configuration_audit(folder_id, performed_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_operation ON folder_configuration_audit(operation_type, performed_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON folder_configuration_audit(user_id, performed_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_session ON folder_configuration_audit(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_status ON folder_configuration_audit(operation_status, performed_at DESC)",
        ]

        for index_sql in indexes:
            try:
                conn.execute(index_sql)
                logger.debug(f"Created index: {index_sql.split()[-1]}")
            except Exception as e:
                logger.error(f"Failed to create index {index_sql}: {e}")

        logger.info("Advanced Folders indexes created successfully")

    @staticmethod
    def create_advanced_folders_triggers(conn: sqlite3.Connection) -> None:
        """
        Create database triggers for automation and data integrity.

        Implements automated maintenance for:
        - Timestamp updates
        - Cache invalidation
        - Audit logging
        - Data cleanup
        """

        triggers = [
            # Auto-update timestamp on folder configuration changes
            """
            CREATE TRIGGER IF NOT EXISTS trg_folder_config_updated
            AFTER UPDATE ON folder_configurations
            FOR EACH ROW
            WHEN NEW.updated_at = OLD.updated_at
            BEGIN
                UPDATE folder_configurations 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE folder_id = NEW.folder_id;
            END
            """,
            # Auto-update timestamp on search parameters changes
            """
            CREATE TRIGGER IF NOT EXISTS trg_search_params_updated
            AFTER UPDATE ON search_parameters
            FOR EACH ROW
            WHEN NEW.updated_at = OLD.updated_at
            BEGIN
                UPDATE search_parameters 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE parameter_id = NEW.parameter_id;
            END
            """,
            # Invalidate cache when search parameters change
            """
            CREATE TRIGGER IF NOT EXISTS trg_invalidate_cache_on_params_change
            AFTER UPDATE ON search_parameters
            FOR EACH ROW
            BEGIN
                DELETE FROM search_results_cache 
                WHERE folder_id = NEW.folder_id;
            END
            """,
            # Update folder file statistics when files are added/removed
            """
            CREATE TRIGGER IF NOT EXISTS trg_update_folder_stats_insert
            AFTER INSERT ON file_metadata_index
            FOR EACH ROW
            BEGIN
                UPDATE folder_configurations 
                SET total_files = total_files + 1,
                    total_size_bytes = total_size_bytes + COALESCE(NEW.file_size, 0),
                    updated_at = CURRENT_TIMESTAMP
                WHERE folder_id = NEW.folder_id;
            END
            """,
            """
            CREATE TRIGGER IF NOT EXISTS trg_update_folder_stats_delete
            AFTER DELETE ON file_metadata_index
            FOR EACH ROW
            BEGIN
                UPDATE folder_configurations 
                SET total_files = total_files - 1,
                    total_size_bytes = total_size_bytes - COALESCE(OLD.file_size, 0),
                    updated_at = CURRENT_TIMESTAMP
                WHERE folder_id = OLD.folder_id;
            END
            """,
            # Auto-generate file_path_hash for extended metadata
            """
            CREATE TRIGGER IF NOT EXISTS trg_generate_file_path_hash
            BEFORE INSERT ON file_metadata_extended
            FOR EACH ROW
            WHEN NEW.file_path_hash IS NULL OR NEW.file_path_hash = ''
            BEGIN
                UPDATE file_metadata_extended 
                SET file_path_hash = hex(randomblob(16))
                WHERE file_id = NEW.file_id;
            END
            """,
            # Auto-expire old cache entries
            """
            CREATE TRIGGER IF NOT EXISTS trg_cleanup_expired_cache
            BEFORE INSERT ON search_results_cache
            FOR EACH ROW
            BEGIN
                DELETE FROM search_results_cache 
                WHERE cache_expires_at < CURRENT_TIMESTAMP;
            END
            """,
            # Update UI preferences timestamp
            """
            CREATE TRIGGER IF NOT EXISTS trg_ui_prefs_updated
            AFTER UPDATE ON ui_preferences
            FOR EACH ROW
            WHEN NEW.updated_at = OLD.updated_at
            BEGIN
                UPDATE ui_preferences 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE preference_id = NEW.preference_id;
            END
            """,
        ]

        for trigger_sql in triggers:
            try:
                conn.execute(trigger_sql)
                trigger_name = trigger_sql.split("\n")[1].strip().split()[-1]
                logger.debug(f"Created trigger: {trigger_name}")
            except Exception as e:
                logger.error(f"Failed to create trigger: {e}")

        logger.info("Advanced Folders triggers created successfully")

    @staticmethod
    def get_schema_info() -> Dict[str, Any]:
        """
        Get comprehensive schema information.

        Returns:
            Dictionary containing schema metadata and statistics
        """
        return {
            "schema_version": "1.0.0",
            "tables": [
                "folder_configurations",
                "search_parameters",
                "file_metadata_index",
                "file_metadata_extended",
                "search_results_cache",
                "performance_metrics",
                "ui_preferences",
                "folder_configuration_audit",
            ],
            "primary_indexes": 24,
            "triggers": 8,
            "foreign_keys": 7,
            "check_constraints": 15,
            "unique_constraints": 8,
        }
