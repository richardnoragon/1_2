"""
Theme Backup Manager for RFU Hub

Provides comprehensive backup and versioning for theme data:
- Automatic backup creation with configurable intervals
- Version management with retention policies
- Backup verification and integrity checking
- Backup compression and storage optimization
"""

import logging
import os
import sqlite3
import datetime
import json
import gzip
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path


class BackupResult:
    """Result of a backup operation."""
    
    def __init__(self, success: bool, backup_id: str = None, 
                 file_path: str = None, error: str = None):
        self.success = success
        self.backup_id = backup_id
        self.file_path = file_path
        self.error = error
        self.timestamp = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert backup result to dictionary."""
        return {
            'success': self.success,
            'backup_id': self.backup_id,
            'file_path': self.file_path,
            'error': self.error,
            'timestamp': self.timestamp
        }


class BackupMetadata:
    """Metadata for a backup entry."""
    
    def __init__(self, backup_id: str, theme_name: str, user_id: str,
                 file_path: str, size: int, checksum: str):
        self.backup_id = backup_id
        self.theme_name = theme_name
        self.user_id = user_id
        self.file_path = file_path
        self.size = size
        self.checksum = checksum
        self.created_at = datetime.datetime.now()
        self.verified = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert backup metadata to dictionary."""
        return {
            'backup_id': self.backup_id,
            'theme_name': self.theme_name,
            'user_id': self.user_id,
            'file_path': self.file_path,
            'size': self.size,
            'checksum': self.checksum,
            'created_at': self.created_at.isoformat(),
            'verified': self.verified
        }


class ThemeBackupManager:
    """
    Comprehensive backup management system for theme data.
    
    This class handles automatic backups, version management,
    retention policies, and backup verification.
    """
    
    def __init__(self, backup_dir: str = "data/backups",
                 database_path: str = "data/theme_security.db"):
        """
        Initialize the Theme Backup Manager.
        
        Args:
            backup_dir: Directory for storing backups
            database_path: Path to the security database
        """
        self.logger = logging.getLogger('RFU.ThemeBackupManager')
        self.backup_dir = Path(backup_dir)
        self.database_path = database_path
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Backup configuration
        self.config = {
            'auto_backup_enabled': True,
            'backup_interval_hours': 24,
            'max_backups_per_theme': 10,
            'retention_days': 30,
            'compress_backups': True,
            'verify_backups': True,
            'backup_on_save': True,
            'backup_on_load': False,
            'cleanup_interval_hours': 168  # 1 week
        }
        
        self.logger.info("Theme Backup Manager initialized")
    
    def _init_database(self):
        """Initialize the backup database tables."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Create backups table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS theme_backups (
                        backup_id TEXT PRIMARY KEY,
                        theme_name TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        original_path TEXT,
                        size INTEGER NOT NULL,
                        checksum TEXT NOT NULL,
                        compressed BOOLEAN DEFAULT 0,
                        verified BOOLEAN DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        backup_type TEXT DEFAULT 'manual',
                        metadata TEXT
                    )
                ''')
                
                # Create backup verification log
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS theme_backup_verification (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        backup_id TEXT NOT NULL,
                        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        verification_success BOOLEAN NOT NULL,
                        error_message TEXT,
                        FOREIGN KEY (backup_id) REFERENCES theme_backups (backup_id)
                    )
                ''')
                
                conn.commit()
                self.logger.info("Backup database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize backup database: {e}")
            raise
    
    def create_backup(self, theme_name: str, theme_data: Dict[str, Any],
                     user_id: str = "default", backup_type: str = "manual") -> BackupResult:
        """
        Create a backup of theme data.
        
        Args:
            theme_name: Name of the theme
            theme_data: Theme data to backup
            user_id: User identifier
            backup_type: Type of backup ('manual', 'auto', 'pre_save')
            
        Returns:
            BackupResult with backup information
        """
        try:
            # Generate unique backup ID
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_id = f"{theme_name}_{user_id}_{timestamp}"
            
            # Create user backup directory
            user_backup_dir = self.backup_dir / user_id
            user_backup_dir.mkdir(exist_ok=True)
            
            # Determine file extension based on compression setting
            extension = ".json.gz" if self.config['compress_backups'] else ".json"
            backup_filename = f"{backup_id}{extension}"
            backup_path = user_backup_dir / backup_filename
            
            # Serialize theme data
            json_data = json.dumps(theme_data, indent=2, sort_keys=True)
            
            # Save backup file
            if self.config['compress_backups']:
                with gzip.open(backup_path, 'wt', encoding='utf-8') as f:
                    f.write(json_data)
            else:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(json_data)
            
            # Calculate file size and checksum
            file_size = backup_path.stat().st_size
            checksum = self._calculate_file_checksum(str(backup_path))
            
            # Store backup metadata in database
            success = self._store_backup_metadata(
                backup_id, theme_name, user_id, str(backup_path),
                file_size, checksum, backup_type
            )
            
            if not success:
                # Clean up file if database storage failed
                backup_path.unlink(missing_ok=True)
                return BackupResult(
                    success=False,
                    error="Failed to store backup metadata"
                )
            
            # Verify backup if enabled
            if self.config['verify_backups']:
                verification_success = self._verify_backup(backup_id)
                if not verification_success:
                    self.logger.warning(f"Backup verification failed: {backup_id}")
            
            # Clean up old backups for this theme
            self._cleanup_old_backups(theme_name, user_id)
            
            self.logger.info(f"Created backup: {backup_id}")
            return BackupResult(
                success=True,
                backup_id=backup_id,
                file_path=str(backup_path)
            )
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return BackupResult(
                success=False,
                error=str(e)
            )
    
    def restore_backup(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore theme data from a backup.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Restored theme data or None if failed
        """
        try:
            # Get backup metadata
            backup_metadata = self.get_backup_metadata(backup_id)
            if not backup_metadata:
                self.logger.error(f"Backup not found: {backup_id}")
                return None
            
            backup_path = backup_metadata['file_path']
            
            # Check if backup file exists
            if not os.path.exists(backup_path):
                self.logger.error(f"Backup file not found: {backup_path}")
                return None
            
            # Verify backup integrity
            if not self._verify_backup_file(backup_path, backup_metadata['checksum']):
                self.logger.error(f"Backup integrity check failed: {backup_id}")
                return None
            
            # Load backup data
            if backup_metadata.get('compressed', False):
                with gzip.open(backup_path, 'rt', encoding='utf-8') as f:
                    theme_data = json.load(f)
            else:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
            
            self.logger.info(f"Restored backup: {backup_id}")
            return theme_data
            
        except Exception as e:
            self.logger.error(f"Backup restoration failed: {e}")
            return None
    
    def list_backups(self, theme_name: str = None, user_id: str = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            theme_name: Optional theme filter
            user_id: Optional user filter
            limit: Maximum number of backups to return
            
        Returns:
            List of backup metadata dictionaries
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT backup_id, theme_name, user_id, file_path, size,
                           checksum, compressed, verified, created_at, backup_type
                    FROM theme_backups
                    WHERE 1=1
                '''
                params = []
                
                if theme_name:
                    query += ' AND theme_name = ?'
                    params.append(theme_name)
                
                if user_id:
                    query += ' AND user_id = ?'
                    params.append(user_id)
                
                query += ' ORDER BY created_at DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                
                backups = []
                for row in cursor.fetchall():
                    backups.append({
                        'backup_id': row[0],
                        'theme_name': row[1],
                        'user_id': row[2],
                        'file_path': row[3],
                        'size': row[4],
                        'checksum': row[5],
                        'compressed': bool(row[6]),
                        'verified': bool(row[7]),
                        'created_at': row[8],
                        'backup_type': row[9]
                    })
                
                return backups
                
        except Exception as e:
            self.logger.error(f"Failed to list backups: {e}")
            return []
    
    def get_backup_metadata(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific backup.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            Backup metadata dictionary or None if not found
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT backup_id, theme_name, user_id, file_path, size,
                           checksum, compressed, verified, created_at, backup_type,
                           metadata
                    FROM theme_backups
                    WHERE backup_id = ?
                ''', [backup_id])
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                metadata = {
                    'backup_id': row[0],
                    'theme_name': row[1],
                    'user_id': row[2],
                    'file_path': row[3],
                    'size': row[4],
                    'checksum': row[5],
                    'compressed': bool(row[6]),
                    'verified': bool(row[7]),
                    'created_at': row[8],
                    'backup_type': row[9]
                }
                
                # Parse additional metadata if present
                if row[10]:
                    try:
                        additional_metadata = json.loads(row[10])
                        metadata.update(additional_metadata)
                    except json.JSONDecodeError:
                        pass
                
                return metadata
                
        except Exception as e:
            self.logger.error(f"Failed to get backup metadata: {e}")
            return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup.
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            True if backup was deleted successfully
        """
        try:
            # Get backup metadata
            backup_metadata = self.get_backup_metadata(backup_id)
            if not backup_metadata:
                self.logger.warning(f"Backup not found for deletion: {backup_id}")
                return False
            
            # Delete backup file
            backup_path = backup_metadata['file_path']
            if os.path.exists(backup_path):
                os.unlink(backup_path)
            
            # Remove from database
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Delete verification records
                cursor.execute('''
                    DELETE FROM theme_backup_verification
                    WHERE backup_id = ?
                ''', [backup_id])
                
                # Delete backup record
                cursor.execute('''
                    DELETE FROM theme_backups
                    WHERE backup_id = ?
                ''', [backup_id])
                
                conn.commit()
            
            self.logger.info(f"Deleted backup: {backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete backup: {e}")
            return False
    
    def verify_all_backups(self) -> Dict[str, Any]:
        """
        Verify integrity of all backups.
        
        Returns:
            Dictionary with verification results
        """
        try:
            backups = self.list_backups(limit=1000)  # Get all backups
            
            results = {
                'total_backups': len(backups),
                'verified_count': 0,
                'failed_count': 0,
                'missing_files': 0,
                'failed_backups': [],
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            for backup in backups:
                backup_id = backup['backup_id']
                
                if not os.path.exists(backup['file_path']):
                    results['missing_files'] += 1
                    results['failed_backups'].append({
                        'backup_id': backup_id,
                        'error': 'File not found'
                    })
                    continue
                
                if self._verify_backup(backup_id):
                    results['verified_count'] += 1
                else:
                    results['failed_count'] += 1
                    results['failed_backups'].append({
                        'backup_id': backup_id,
                        'error': 'Verification failed'
                    })
            
            self.logger.info(
                f"Backup verification complete: {results['verified_count']}/"
                f"{results['total_backups']} verified"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }
    
    def _store_backup_metadata(self, backup_id: str, theme_name: str,
                              user_id: str, file_path: str, size: int,
                              checksum: str, backup_type: str) -> bool:
        """Store backup metadata in database."""
        try:
            # Calculate expiration date
            expires_at = datetime.datetime.now() + datetime.timedelta(
                days=self.config['retention_days']
            )
            
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO theme_backups
                    (backup_id, theme_name, user_id, file_path, size, checksum,
                     compressed, verified, expires_at, backup_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                ''', [
                    backup_id, theme_name, user_id, file_path, size, checksum,
                    self.config['compress_backups'], expires_at.isoformat(),
                    backup_type
                ])
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store backup metadata: {e}")
            return False
    
    def _verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity."""
        try:
            backup_metadata = self.get_backup_metadata(backup_id)
            if not backup_metadata:
                return False
            
            file_path = backup_metadata['file_path']
            expected_checksum = backup_metadata['checksum']
            
            # Verify file exists and checksum matches
            success = self._verify_backup_file(file_path, expected_checksum)
            
            # Log verification result
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO theme_backup_verification
                    (backup_id, verification_success, error_message)
                    VALUES (?, ?, ?)
                ''', [
                    backup_id, success,
                    None if success else "Checksum verification failed"
                ])
                
                # Update backup record
                cursor.execute('''
                    UPDATE theme_backups
                    SET verified = ?
                    WHERE backup_id = ?
                ''', [success, backup_id])
                
                conn.commit()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Backup verification failed: {e}")
            return False
    
    def _verify_backup_file(self, file_path: str, expected_checksum: str) -> bool:
        """Verify backup file checksum."""
        try:
            if not os.path.exists(file_path):
                return False
            
            actual_checksum = self._calculate_file_checksum(file_path)
            return actual_checksum == expected_checksum
            
        except Exception as e:
            self.logger.error(f"File verification failed: {e}")
            return False
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum for a file."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Checksum calculation failed: {e}")
            return ""
    
    def _cleanup_old_backups(self, theme_name: str, user_id: str) -> None:
        """Clean up old backups based on retention policy."""
        try:
            # Get backups for this theme and user
            backups = self.list_backups(theme_name=theme_name, user_id=user_id,
                                       limit=1000)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            # Keep only the configured number of backups
            max_backups = self.config['max_backups_per_theme']
            if len(backups) > max_backups:
                backups_to_delete = backups[max_backups:]
                
                for backup in backups_to_delete:
                    self.delete_backup(backup['backup_id'])
                    self.logger.info(f"Cleaned up old backup: {backup['backup_id']}")
            
            # Also clean up expired backups
            self._cleanup_expired_backups()
            
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
    
    def _cleanup_expired_backups(self) -> None:
        """Clean up expired backups."""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Find expired backups
                cursor.execute('''
                    SELECT backup_id FROM theme_backups
                    WHERE expires_at < CURRENT_TIMESTAMP
                ''')
                
                expired_backups = [row[0] for row in cursor.fetchall()]
                
                # Delete expired backups
                for backup_id in expired_backups:
                    self.delete_backup(backup_id)
                    
                if expired_backups:
                    self.logger.info(f"Cleaned up {len(expired_backups)} expired backups")
                    
        except Exception as e:
            self.logger.error(f"Expired backup cleanup failed: {e}")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """
        Get backup system statistics.
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Total backups
                cursor.execute('SELECT COUNT(*) FROM theme_backups')
                total_backups = cursor.fetchone()[0]
                
                # Verified backups
                cursor.execute('SELECT COUNT(*) FROM theme_backups WHERE verified = 1')
                verified_backups = cursor.fetchone()[0]
                
                # Total storage used
                cursor.execute('SELECT SUM(size) FROM theme_backups')
                total_size = cursor.fetchone()[0] or 0
                
                # Backups by type
                cursor.execute('''
                    SELECT backup_type, COUNT(*) FROM theme_backups
                    GROUP BY backup_type
                ''')
                backup_types = dict(cursor.fetchall())
                
                # Recent backup activity (last 7 days)
                week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
                cursor.execute('''
                    SELECT COUNT(*) FROM theme_backups
                    WHERE created_at > ?
                ''', [week_ago])
                recent_backups = cursor.fetchone()[0]
                
                return {
                    'total_backups': total_backups,
                    'verified_backups': verified_backups,
                    'verification_rate': verified_backups / total_backups if total_backups > 0 else 0,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2),
                    'backup_types': backup_types,
                    'recent_backups': recent_backups,
                    'compression_enabled': self.config['compress_backups'],
                    'retention_days': self.config['retention_days'],
                    'max_backups_per_theme': self.config['max_backups_per_theme'],
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get backup statistics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }