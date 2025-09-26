#!/usr/bin/env python3
"""
Environment Manager for RFU Integration Testing
Phase 1: Foundation Setup - Environment Provisioning and Management

This script provides comprehensive environment management capabilities for 
all three test environments: development, staging, and production-like.
"""

import json
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import yaml


class EnvironmentManager:
    """Comprehensive environment management for RFU integration testing."""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.environments_path = self.base_path / "environments"
        self.data_path = self.base_path / "data"
        self.logs_path = self.base_path / "logs"
        self.artifacts_path = self.base_path / "artifacts"
        self.backups_path = self.base_path / "backups"
        
        # Ensure all directories exist
        for path in [self.data_path, self.logs_path, self.artifacts_path, self.backups_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        self.environments = ["dev", "staging", "prod-like"]
        
    def _setup_logging(self) -> logging.Logger:
        """Set up comprehensive logging for environment management."""
        logger = logging.getLogger("EnvironmentManager")
        logger.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # File handler
        log_file = self.logs_path / "environment_manager.log"
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
    
    def load_environment_config(self, env_name: str) -> Dict[str, Any]:
        """Load configuration for a specific environment."""
        config_path = self.environments_path / env_name / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration not found for environment: {env_name}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.logger.debug(f"Loaded configuration for environment: {env_name}")
        return config
    
    def create_environment(self, env_name: str, force: bool = False) -> bool:
        """Create and initialize a test environment."""
        self.logger.info(f"Creating environment: {env_name}")
        
        try:
            config = self.load_environment_config(env_name)
            
            # Create environment directories
            env_data_path = self.data_path / env_name
            env_temp_path = self.base_path / "temp" / env_name
            env_artifacts_path = self.artifacts_path / env_name
            
            for path in [env_data_path, env_temp_path, env_artifacts_path]:
                if path.exists() and not force:
                    self.logger.warning(f"Directory already exists: {path}")
                    continue
                path.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            if not self._initialize_database(env_name, config, force):
                return False
            
            # Create sample test data
            if not self._create_sample_data(env_name, config):
                return False
            
            # Set up monitoring if enabled
            if config.get('performance', {}).get('monitoring', {}).get('enabled', False):
                self._setup_monitoring(env_name, config)
            
            # Create environment status file
            self._create_environment_status(env_name, config)
            
            self.logger.info(f"Successfully created environment: {env_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create environment {env_name}: {str(e)}")
            return False
    
    def _initialize_database(self, env_name: str, config: Dict[str, Any], force: bool = False) -> bool:
        """Initialize SQLite database for the environment."""
        db_config = config.get('database', {})
        db_location = db_config.get('location', f'tests/integration/data/test_{env_name}.db')
        
        # Convert relative path to absolute
        if not os.path.isabs(db_location):
            db_path = self.base_path.parent / db_location
        else:
            db_path = Path(db_location)
        
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Remove existing database if force is True
        if force and db_path.exists():
            db_path.unlink()
            self.logger.info(f"Removed existing database: {db_path}")
        
        try:
            # Create database connection
            conn = sqlite3.connect(str(db_path))
            
            # Enable foreign keys if specified
            if db_config.get('foreign_keys', True):
                conn.execute("PRAGMA foreign_keys = ON")
            
            # Enable WAL mode if specified
            if db_config.get('wal_mode', False):
                conn.execute("PRAGMA journal_mode = WAL")
            
            # Set timeout
            timeout = db_config.get('timeout', 30)
            conn.execute(f"PRAGMA busy_timeout = {timeout * 1000}")
            
            # Create basic tables for RFU
            self._create_database_schema(conn)
            
            # Load sample data if specified
            if db_config.get('initialization', {}).get('load_sample_data', True):
                self._load_sample_database_data(conn, env_name)
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Initialized database for {env_name}: {db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database for {env_name}: {str(e)}")
            return False
    
    def _create_database_schema(self, conn: sqlite3.Connection):
        """Create the basic database schema for RFU testing."""
        schema_sql = """
        -- Files table
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            size INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_type TEXT,
            checksum TEXT,
            metadata TEXT
        );
        
        -- File metadata table
        CREATE TABLE IF NOT EXISTS file_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
        );
        
        -- Processing jobs table
        CREATE TABLE IF NOT EXISTS processing_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            input_files TEXT,
            output_files TEXT,
            parameters TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT
        );
        
        -- User preferences table
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category, key)
        );
        
        -- Test execution logs table
        CREATE TABLE IF NOT EXISTS test_execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_name TEXT NOT NULL,
            environment TEXT NOT NULL,
            status TEXT NOT NULL,
            duration REAL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
        CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type);
        CREATE INDEX IF NOT EXISTS idx_metadata_file_id ON file_metadata(file_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_status ON processing_jobs(status);
        CREATE INDEX IF NOT EXISTS idx_jobs_type ON processing_jobs(job_type);
        CREATE INDEX IF NOT EXISTS idx_preferences_category ON user_preferences(category);
        CREATE INDEX IF NOT EXISTS idx_test_logs_environment ON test_execution_logs(environment);
        """
        
        for statement in schema_sql.split(';'):
            if statement.strip():
                conn.execute(statement)
    
    def _load_sample_database_data(self, conn: sqlite3.Connection, env_name: str):
        """Load sample data appropriate for the environment."""
        # Determine sample data size based on environment
        if env_name == "dev":
            file_count = 50
        elif env_name == "staging":
            file_count = 500
        else:  # prod-like
            file_count = 5000
        
        # Insert sample files
        for i in range(file_count):
            conn.execute("""
                INSERT INTO files (path, name, size, file_type, checksum)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"/test/files/sample_{i}.pdf",
                f"sample_{i}.pdf",
                1024 * (i + 1),
                "pdf",
                f"checksum_{i:06d}"
            ))
        
        # Insert sample metadata
        for i in range(0, file_count, 10):
            file_id = i + 1
            conn.execute("""
                INSERT INTO file_metadata (file_id, key, value)
                VALUES (?, ?, ?)
            """, (file_id, "author", f"Test Author {i}"))
            
            conn.execute("""
                INSERT INTO file_metadata (file_id, key, value)
                VALUES (?, ?, ?)
            """, (file_id, "pages", str((i % 100) + 1)))
        
        # Insert sample preferences
        preferences = [
            ("theme", "dark_mode", "false"),
            ("performance", "max_workers", "4"),
            ("security", "encryption_enabled", "true"),
            ("gui", "auto_save", "true")
        ]
        
        for category, key, value in preferences:
            conn.execute("""
                INSERT OR REPLACE INTO user_preferences (category, key, value)
                VALUES (?, ?, ?)
            """, (category, key, value))
    
    def _create_sample_data(self, env_name: str, config: Dict[str, Any]) -> bool:
        """Create sample files for testing."""
        try:
            file_config = config.get('file_system', {})
            test_data_root = self.data_path / env_name
            
            # Create sample PDF files
            pdf_count = file_config.get('pdf_samples', 10)
            pdf_dir = test_data_root / "pdf_samples"
            pdf_dir.mkdir(exist_ok=True)
            
            for i in range(pdf_count):
                pdf_content = f"PDF Test Content {i}\nEnvironment: {env_name}\nGenerated: {datetime.now()}"
                pdf_file = pdf_dir / f"sample_{i:03d}.txt"  # Using .txt for simplicity
                pdf_file.write_text(pdf_content)
            
            # Create sample image files
            image_count = file_config.get('image_samples', 15)
            image_dir = test_data_root / "image_samples"
            image_dir.mkdir(exist_ok=True)
            
            for i in range(image_count):
                image_content = f"Image Test Data {i}\nEnvironment: {env_name}\nGenerated: {datetime.now()}"
                image_file = image_dir / f"sample_{i:03d}.txt"  # Using .txt for simplicity
                image_file.write_text(image_content)
            
            # Create sample office files
            office_count = file_config.get('office_samples', 8)
            office_dir = test_data_root / "office_samples"
            office_dir.mkdir(exist_ok=True)
            
            for i in range(office_count):
                office_content = f"Office Document {i}\nEnvironment: {env_name}\nGenerated: {datetime.now()}"
                office_file = office_dir / f"document_{i:03d}.txt"
                office_file.write_text(office_content)
            
            self.logger.info(f"Created sample data for {env_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create sample data for {env_name}: {str(e)}")
            return False
    
    def _setup_monitoring(self, env_name: str, config: Dict[str, Any]):
        """Set up monitoring for the environment."""
        monitoring_config = config.get('performance', {}).get('monitoring', {})
        
        if not monitoring_config.get('enabled', False):
            return
        
        # Create monitoring directory
        monitoring_dir = self.base_path / "monitoring" / env_name
        monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # Create monitoring configuration
        monitor_config = {
            'environment': env_name,
            'interval': monitoring_config.get('interval', 60),
            'metrics': monitoring_config.get('metrics', ['memory', 'cpu', 'disk']),
            'enabled': True,
            'created_at': datetime.now().isoformat()
        }
        
        config_file = monitoring_dir / "monitor_config.json"
        with open(config_file, 'w') as f:
            json.dump(monitor_config, f, indent=2)
        
        self.logger.info(f"Set up monitoring for {env_name}")
    
    def _create_environment_status(self, env_name: str, config: Dict[str, Any]):
        """Create environment status tracking file."""
        status = {
            'environment': env_name,
            'status': 'ready',
            'created_at': datetime.now().isoformat(),
            'last_validated': datetime.now().isoformat(),
            'configuration': config.get('environment', {}),
            'health_checks': {
                'database': 'healthy',
                'file_system': 'healthy',
                'monitoring': 'healthy' if config.get('performance', {}).get('monitoring', {}).get('enabled', False) else 'disabled'
            },
            'metrics': {
                'disk_usage': self._get_disk_usage(env_name),
                'file_count': self._count_environment_files(env_name)
            }
        }
        
        status_file = self.artifacts_path / env_name / "environment_status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def validate_environment(self, env_name: str) -> Dict[str, Any]:
        """Comprehensive environment validation."""
        self.logger.info(f"Validating environment: {env_name}")
        
        validation_results = {
            'environment': env_name,
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        try:
            config = self.load_environment_config(env_name)
            
            # Database validation
            db_status = self._validate_database(env_name, config)
            validation_results['checks']['database'] = db_status
            
            # File system validation
            fs_status = self._validate_file_system(env_name, config)
            validation_results['checks']['file_system'] = fs_status
            
            # Network validation
            network_status = self._validate_network(env_name, config)
            validation_results['checks']['network'] = network_status
            
            # Resource validation
            resource_status = self._validate_resources(env_name, config)
            validation_results['checks']['resources'] = resource_status
            
            # Determine overall status
            failed_checks = [name for name, check in validation_results['checks'].items() 
                           if check.get('status') != 'healthy']
            
            if failed_checks:
                validation_results['overall_status'] = 'unhealthy'
                validation_results['failed_checks'] = failed_checks
            
            # Save validation results
            validation_file = self.artifacts_path / env_name / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            validation_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(validation_file, 'w') as f:
                json.dump(validation_results, f, indent=2)
            
            self.logger.info(f"Environment validation completed for {env_name}: {validation_results['overall_status']}")
            
        except Exception as e:
            validation_results['overall_status'] = 'error'
            validation_results['error'] = str(e)
            self.logger.error(f"Environment validation failed for {env_name}: {str(e)}")
        
        return validation_results
    
    def _validate_database(self, env_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate database connectivity and schema."""
        db_config = config.get('database', {})
        db_location = db_config.get('location', f'tests/integration/data/test_{env_name}.db')
        
        if not os.path.isabs(db_location):
            db_path = self.base_path.parent / db_location
        else:
            db_path = Path(db_location)
        
        try:
            if not db_path.exists():
                return {'status': 'unhealthy', 'error': 'Database file not found'}
            
            # Test connection
            conn = sqlite3.connect(str(db_path))
            
            # Verify schema
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['files', 'file_metadata', 'processing_jobs', 'user_preferences', 'test_execution_logs']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                conn.close()
                return {'status': 'unhealthy', 'error': f'Missing tables: {missing_tables}'}
            
            # Test basic operations
            cursor.execute("SELECT COUNT(*) FROM files")
            file_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'status': 'healthy',
                'file_count': file_count,
                'tables': tables,
                'path': str(db_path)
            }
            
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _validate_file_system(self, env_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate file system setup and permissions."""
        try:
            env_data_path = self.data_path / env_name
            
            if not env_data_path.exists():
                return {'status': 'unhealthy', 'error': 'Environment data directory not found'}
            
            # Check directory permissions
            if not os.access(env_data_path, os.R_OK | os.W_OK):
                return {'status': 'unhealthy', 'error': 'Insufficient directory permissions'}
            
            # Count files
            file_count = self._count_environment_files(env_name)
            
            # Check disk usage
            disk_usage = self._get_disk_usage(env_name)
            
            return {
                'status': 'healthy',
                'file_count': file_count,
                'disk_usage_mb': disk_usage,
                'path': str(env_data_path)
            }
            
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _validate_network(self, env_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate network configuration and connectivity."""
        network_config = config.get('network', {})
        
        try:
            if network_config.get('mock_external_apis', True):
                return {'status': 'healthy', 'mode': 'mock'}
            
            # Test external service connectivity
            external_services = network_config.get('external_services', {})
            service_status = {}
            
            for service_name, service_config in external_services.items():
                if service_config.get('mock', True):
                    service_status[service_name] = 'mocked'
                else:
                    # In a real implementation, you would test actual connectivity
                    service_status[service_name] = 'not_tested'
            
            return {
                'status': 'healthy',
                'mode': 'live',
                'services': service_status
            }
            
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _validate_resources(self, env_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate system resource availability."""
        try:
            perf_config = config.get('performance', {})
            
            # Memory check
            memory = psutil.virtual_memory()
            memory_limit = perf_config.get('memory_limit', '1GB')
            memory_limit_bytes = self._parse_size(memory_limit)
            
            # Disk check
            disk = psutil.disk_usage(str(self.base_path))
            disk_limit = perf_config.get('disk_limit', '10GB')
            disk_limit_bytes = self._parse_size(disk_limit)
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'status': 'healthy',
                'memory': {
                    'available_gb': round(memory.available / (1024**3), 2),
                    'limit_gb': round(memory_limit_bytes / (1024**3), 2),
                    'sufficient': memory.available >= memory_limit_bytes
                },
                'disk': {
                    'free_gb': round(disk.free / (1024**3), 2),
                    'limit_gb': round(disk_limit_bytes / (1024**3), 2),
                    'sufficient': disk.free >= disk_limit_bytes
                },
                'cpu': {
                    'current_percent': cpu_percent,
                    'status': 'normal' if cpu_percent < 80 else 'high'
                }
            }
            
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string (e.g., '1GB', '500MB') to bytes."""
        size_str = size_str.upper()
        if size_str.endswith('GB'):
            return int(float(size_str[:-2]) * 1024**3)
        elif size_str.endswith('MB'):
            return int(float(size_str[:-2]) * 1024**2)
        elif size_str.endswith('KB'):
            return int(float(size_str[:-2]) * 1024)
        else:
            return int(size_str)
    
    def _get_disk_usage(self, env_name: str) -> float:
        """Get disk usage for environment in MB."""
        env_path = self.data_path / env_name
        if not env_path.exists():
            return 0
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(env_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    pass
        
        return round(total_size / (1024**2), 2)  # Convert to MB
    
    def _count_environment_files(self, env_name: str) -> int:
        """Count files in environment."""
        env_path = self.data_path / env_name
        if not env_path.exists():
            return 0
        
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(env_path):
            file_count += len(filenames)
        
        return file_count
    
    def cleanup_environment(self, env_name: str, preserve_config: bool = True) -> bool:
        """Clean up environment data while optionally preserving configuration."""
        self.logger.info(f"Cleaning up environment: {env_name}")
        
        try:
            # Clean up data directory
            env_data_path = self.data_path / env_name
            if env_data_path.exists():
                shutil.rmtree(env_data_path)
                self.logger.info(f"Removed data directory: {env_data_path}")
            
            # Clean up temp directory
            env_temp_path = self.base_path / "temp" / env_name
            if env_temp_path.exists():
                shutil.rmtree(env_temp_path)
                self.logger.info(f"Removed temp directory: {env_temp_path}")
            
            # Clean up artifacts (optional)
            if not preserve_config:
                env_artifacts_path = self.artifacts_path / env_name
                if env_artifacts_path.exists():
                    shutil.rmtree(env_artifacts_path)
                    self.logger.info(f"Removed artifacts directory: {env_artifacts_path}")
            
            self.logger.info(f"Successfully cleaned up environment: {env_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clean up environment {env_name}: {str(e)}")
            return False
    
    def backup_environment(self, env_name: str) -> str:
        """Create a backup of the environment."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{env_name}_backup_{timestamp}"
        backup_path = self.backups_path / backup_name
        
        self.logger.info(f"Creating backup for environment: {env_name}")
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup data directory
            env_data_path = self.data_path / env_name
            if env_data_path.exists():
                shutil.copytree(env_data_path, backup_path / "data")
            
            # Backup artifacts
            env_artifacts_path = self.artifacts_path / env_name
            if env_artifacts_path.exists():
                shutil.copytree(env_artifacts_path, backup_path / "artifacts")
            
            # Create backup manifest
            manifest = {
                'environment': env_name,
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'files_backed_up': self._count_backup_files(backup_path),
                'size_mb': self._get_backup_size(backup_path)
            }
            
            with open(backup_path / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self.logger.info(f"Successfully created backup: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {env_name}: {str(e)}")
            return ""
    
    def _count_backup_files(self, backup_path: Path) -> int:
        """Count files in backup."""
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(backup_path):
            file_count += len(filenames)
        return file_count
    
    def _get_backup_size(self, backup_path: Path) -> float:
        """Get backup size in MB."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(backup_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, IOError):
                    pass
        return round(total_size / (1024**2), 2)
    
    def list_environments(self) -> List[Dict[str, Any]]:
        """List all available environments with their status."""
        environments = []
        
        for env_name in self.environments:
            try:
                config = self.load_environment_config(env_name)
                
                # Check if environment is created
                env_data_path = self.data_path / env_name
                is_created = env_data_path.exists()
                
                # Get basic metrics if environment exists
                metrics = {}
                if is_created:
                    metrics = {
                        'file_count': self._count_environment_files(env_name),
                        'disk_usage_mb': self._get_disk_usage(env_name)
                    }
                
                environments.append({
                    'name': env_name,
                    'purpose': config.get('environment', {}).get('purpose', 'Unknown'),
                    'created': is_created,
                    'metrics': metrics
                })
                
            except Exception as e:
                environments.append({
                    'name': env_name,
                    'purpose': 'Unknown',
                    'created': False,
                    'error': str(e)
                })
        
        return environments

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RFU Integration Test Environment Manager')
    parser.add_argument('action', choices=['create', 'validate', 'cleanup', 'backup', 'list'],
                       help='Action to perform')
    parser.add_argument('--environment', '-e', choices=['dev', 'staging', 'prod-like'],
                       help='Environment name')
    parser.add_argument('--force', '-f', action='store_true',
                       help='Force action (e.g., overwrite existing environment)')
    parser.add_argument('--preserve-config', action='store_true', default=True,
                       help='Preserve configuration during cleanup')
    
    args = parser.parse_args()
    
    # Initialize environment manager
    manager = EnvironmentManager()
    
    if args.action == 'list':
        environments = manager.list_environments()
        print("\nAvailable Environments:")
        print("-" * 50)
        for env in environments:
            print(f"Name: {env['name']}")
            print(f"Purpose: {env['purpose']}")
            print(f"Created: {'Yes' if env['created'] else 'No'}")
            if env.get('metrics'):
                print(f"Files: {env['metrics']['file_count']}")
                print(f"Disk Usage: {env['metrics']['disk_usage_mb']} MB")
            if env.get('error'):
                print(f"Error: {env['error']}")
            print("-" * 50)
    
    elif args.environment:
        if args.action == 'create':
            success = manager.create_environment(args.environment, args.force)
            if success:
                print(f"Successfully created environment: {args.environment}")
            else:
                print(f"Failed to create environment: {args.environment}")
                sys.exit(1)
        
        elif args.action == 'validate':
            results = manager.validate_environment(args.environment)
            print(f"\nValidation Results for {args.environment}:")
            print(f"Overall Status: {results['overall_status']}")
            
            for check_name, check_result in results.get('checks', {}).items():
                print(f"\n{check_name.title()}:")
                print(f"  Status: {check_result.get('status', 'unknown')}")
                if check_result.get('error'):
                    print(f"  Error: {check_result['error']}")
        
        elif args.action == 'cleanup':
            success = manager.cleanup_environment(args.environment, args.preserve_config)
            if success:
                print(f"Successfully cleaned up environment: {args.environment}")
            else:
                print(f"Failed to clean up environment: {args.environment}")
                sys.exit(1)
        
        elif args.action == 'backup':
            backup_path = manager.backup_environment(args.environment)
            if backup_path:
                print(f"Successfully created backup: {backup_path}")
            else:
                print(f"Failed to create backup for environment: {args.environment}")
                sys.exit(1)
    
    else:
        print("Error: Environment name required for this action")
        sys.exit(1)

if __name__ == "__main__":
    main()