"""Advanced corruption detection algorithms for filesystem integrity."""

import os
import hashlib
import struct
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum
from pathlib import Path

from ...core.platform_detector import get_platform_detector
from core.error_handler import error_handler


class CorruptionSeverity(Enum):
    """Corruption severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CorruptionType(Enum):
    """Types of corruption that can be detected."""
    CHECKSUM_MISMATCH = "checksum_mismatch"
    SIZE_ANOMALY = "size_anomaly"
    TIMESTAMP_ANOMALY = "timestamp_anomaly"
    PERMISSION_CORRUPTION = "permission_corruption"
    METADATA_CORRUPTION = "metadata_corruption"
    STRUCTURAL_DAMAGE = "structural_damage"
    INODE_CORRUPTION = "inode_corruption"
    DIRECTORY_CORRUPTION = "directory_corruption"
    SYMLINK_CORRUPTION = "symlink_corruption"
    FILESYSTEM_INCONSISTENCY = "filesystem_inconsistency"


class CorruptionDetector:
    """Advanced corruption detection for filesystem integrity.
    
    Provides comprehensive corruption detection including:
    - Checksum verification and validation
    - File size and timestamp anomaly detection
    - Metadata corruption analysis
    - Structural integrity checking
    - Cross-reference validation
    - Pattern-based corruption detection
    """
    
    def __init__(self):
        """Initialize the corruption detector."""
        self.platform_detector = get_platform_detector()
        
        # Detection thresholds
        self.thresholds = {
            'size_change_percent': 10.0,  # % change to flag as anomaly
            'timestamp_future_days': 30,   # Days in future to flag
            'timestamp_past_years': 50,    # Years in past to flag
            'checksum_retry_count': 3,     # Retries for checksum verification
            'metadata_consistency_checks': True,
            'structural_validation': True,
            'cross_reference_validation': True
        }
        
        # Known corruption patterns
        self.corruption_patterns = {
            'zero_byte_files': {
                'description': 'Files that should not be zero bytes',
                'extensions': ['.exe', '.dll', '.so', '.dylib', '.pdf', '.doc'],
                'severity': CorruptionSeverity.HIGH
            },
            'suspicious_sizes': {
                'description': 'Files with suspicious sizes',
                'patterns': [4096, 8192, 16384],  # Common block sizes
                'severity': CorruptionSeverity.MEDIUM
            },
            'invalid_timestamps': {
                'description': 'Files with invalid timestamps',
                'severity': CorruptionSeverity.MEDIUM
            },
            'permission_anomalies': {
                'description': 'Unusual permission patterns',
                'severity': CorruptionSeverity.LOW
            }
        }
        
        # File type signatures for validation
        self.file_signatures = {
            '.pdf': [b'%PDF'],
            '.exe': [b'MZ'],
            '.zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
            '.png': [b'\x89PNG\r\n\x1a\n'],
            '.jpg': [b'\xff\xd8\xff'],
            '.jpeg': [b'\xff\xd8\xff'],
            '.gif': [b'GIF87a', b'GIF89a'],
            '.mp3': [b'ID3', b'\xff\xfb'],
            '.mp4': [b'ftyp'],
            '.avi': [b'RIFF'],
            '.doc': [b'\xd0\xcf\x11\xe0'],
            '.docx': [b'PK\x03\x04']
        }
    
    def analyze_scan_results(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scan results for corruption.
        
        Args:
            scan_results: Results from filesystem scan
            
        Returns:
            Dict containing corruption analysis
        """
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'corruptions': [],
                'warnings': [],
                'statistics': {
                    'files_analyzed': 0,
                    'corruptions_found': 0,
                    'warnings_generated': 0,
                    'critical_issues': 0,
                    'high_severity': 0,
                    'medium_severity': 0,
                    'low_severity': 0
                },
                'summary': {
                    'overall_health': 'unknown',
                    'corruption_rate': 0.0,
                    'most_common_issue': None,
                    'recommendations': []
                }
            }
            
            # Analyze different aspects
            self._analyze_files(scan_results, analysis)
            self._analyze_directories(scan_results, analysis)
            self._analyze_checksums(scan_results, analysis)
            self._analyze_permissions(scan_results, analysis)
            self._analyze_timestamps(scan_results, analysis)
            self._analyze_symlinks(scan_results, analysis)
            self._analyze_structural_integrity(scan_results, analysis)
            
            # Generate summary
            self._generate_analysis_summary(analysis)
            
            return analysis
            
        except Exception as e:
            error_handler.handle_error(e, "CorruptionDetector.analyze_scan_results")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'corruptions': [],
                'statistics': {'files_analyzed': 0}
            }
    
    def _analyze_files(
        self, 
        scan_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Analyze regular files for corruption.
        
        Args:
            scan_results: Scan results to analyze
            analysis: Analysis results to update
        """
        files = scan_results.get('files', [])
        analysis['statistics']['files_analyzed'] = len(files)
        
        for file_info in files:
            try:
                file_path = file_info.get('path', '')
                
                # Check for zero-byte files that shouldn't be empty
                self._check_zero_byte_corruption(file_info, analysis)
                
                # Check file size anomalies
                self._check_size_anomalies(file_info, analysis)
                
                # Check file signature validation
                self._check_file_signature(file_info, analysis)
                
                # Check metadata consistency
                self._check_metadata_consistency(file_info, analysis)
                
            except Exception as e:
                self._add_corruption(
                    analysis,
                    CorruptionType.METADATA_CORRUPTION,
                    CorruptionSeverity.MEDIUM,
                    file_path,
                    f"Error analyzing file: {e}"
                )
    
    def _analyze_directories(
        self, 
        scan_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Analyze directories for corruption.
        
        Args:
            scan_results: Scan results to analyze
            analysis: Analysis results to update
        """
        directories = scan_results.get('directories', [])
        
        for dir_info in directories:
            try:
                dir_path = dir_info.get('path', '')
                
                # Check directory metadata
                self._check_directory_metadata(dir_info, analysis)
                
                # Check directory permissions
                self._check_directory_permissions(dir_info, analysis)
                
            except Exception as e:
                self._add_corruption(
                    analysis,
                    CorruptionType.DIRECTORY_CORRUPTION,
                    CorruptionSeverity.MEDIUM,
                    dir_path,
                    f"Error analyzing directory: {e}"
                )
    
    def _analyze_checksums(
        self, 
        scan_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Analyze checksums for corruption.
        
        Args:
            scan_results: Scan results to analyze
            analysis: Analysis results to update
        """
        checksums = scan_results.get('checksums', {})
        
        for file_path, checksum in checksums.items():
            try:
                # Verify checksum by recalculating
                if self._should_verify_checksum(file_path):
                    verified = self._verify_checksum(file_path, checksum)
                    if not verified:
                        self._add_corruption(
                            analysis,
                            CorruptionType.CHECKSUM_MISMATCH,
                            CorruptionSeverity.HIGH,
                            file_path,
                            "Checksum verification failed"
                        )
                
            except Exception as e:
                self._add_corruption(
                    analysis,
                    CorruptionType.CHECKSUM_MISMATCH,
                    CorruptionSeverity.MEDIUM,
                    file_path,
                    f"Error verifying checksum: {e}"
                )
    
    def _analyze_permissions(
        self, 
        scan_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Analyze file permissions for anomalies.
        
        Args:
            scan_results: Scan results to analyze
            analysis: Analysis results to update
        """
        permissions = scan_results.get('permissions', {})
        
        for file_path, perm_info in permissions.items():
            try:
                # Check for suspicious permission patterns
                self._check_permission_anomalies(file_path, perm_info, analysis)
                
            except Exception as e:
                self._add_corruption(
                    analysis,
                    CorruptionType.PERMISSION_CORRUPTION,
                    CorruptionSeverity.LOW,
                    file_path,
                    f"Error analyzing permissions: {e}"
                )
    
    def _analyze_timestamps(
        self, 
        scan_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Analyze file timestamps for anomalies.
        
        Args:
            scan_results: Scan results to analyze
            analysis: Analysis results to update
        """
        timestamps = scan_results.get('timestamps', {})
        
        for file_path, timestamp_info in timestamps.items():
            try:
                # Check for invalid timestamps
                self._check_timestamp_anomalies(file_path, timestamp_info, analysis)
                
            except Exception as e:
                self._add_corruption(
                    analysis,
                    CorruptionType.TIMESTAMP_ANOMALY,
                    CorruptionSeverity.LOW,
                    file_path,
                    f"Error analyzing timestamps: {e}"
                )
    
    def _analyze_symlinks(
        self, 
        scan_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Analyze symbolic links for corruption.
        
        Args:
            scan_results: Scan results to analyze
            analysis: Analysis results to update
        """
        symlinks = scan_results.get('symlinks', [])
        
        for link_info in symlinks:
            try:
                link_path = link_info.get('path', '')
                
                # Check for broken symlinks
                if not link_info.get('target_exists', True):
                    self._add_corruption(
                        analysis,
                        CorruptionType.SYMLINK_CORRUPTION,
                        CorruptionSeverity.MEDIUM,
                        link_path,
                        f"Broken symlink target: {link_info.get('target', 'unknown')}"
                    )
                
                # Check for circular references
                if 'target_error' in link_info:
                    self._add_corruption(
                        analysis,
                        CorruptionType.SYMLINK_CORRUPTION,
                        CorruptionSeverity.LOW,
                        link_path,
                        f"Symlink error: {link_info['target_error']}"
                    )
                
            except Exception as e:
                self._add_corruption(
                    analysis,
                    CorruptionType.SYMLINK_CORRUPTION,
                    CorruptionSeverity.LOW,
                    link_path,
                    f"Error analyzing symlink: {e}"
                )
    
    def _analyze_structural_integrity(
        self, 
        scan_results: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Analyze structural integrity of the filesystem.
        
        Args:
            scan_results: Scan results to analyze
            analysis: Analysis results to update
        """
        try:
            # Check for filesystem inconsistencies
            errors = scan_results.get('errors', [])
            
            # Categorize errors
            permission_errors = 0
            access_errors = 0
            other_errors = 0
            
            for error in errors:
                error_msg = error.get('error', '').lower()
                if 'permission' in error_msg:
                    permission_errors += 1
                elif 'access' in error_msg or 'not found' in error_msg:
                    access_errors += 1
                else:
                    other_errors += 1
            
            # Flag high error rates as potential corruption
            total_items = (len(scan_results.get('files', [])) + 
                          len(scan_results.get('directories', [])))
            
            if total_items > 0:
                error_rate = len(errors) / total_items
                if error_rate > 0.1:  # More than 10% errors
                    self._add_corruption(
                        analysis,
                        CorruptionType.FILESYSTEM_INCONSISTENCY,
                        CorruptionSeverity.HIGH,
                        'filesystem',
                        f"High error rate: {error_rate:.1%} ({len(errors)} errors)"
                    )
                elif error_rate > 0.05:  # More than 5% errors
                    self._add_corruption(
                        analysis,
                        CorruptionType.FILESYSTEM_INCONSISTENCY,
                        CorruptionSeverity.MEDIUM,
                        'filesystem',
                        f"Elevated error rate: {error_rate:.1%} ({len(errors)} errors)"
                    )
            
        except Exception as e:
            self._add_corruption(
                analysis,
                CorruptionType.STRUCTURAL_DAMAGE,
                CorruptionSeverity.MEDIUM,
                'filesystem',
                f"Error analyzing structural integrity: {e}"
            )
    
    def _check_zero_byte_corruption(
        self, 
        file_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check for zero-byte files that shouldn't be empty.
        
        Args:
            file_info: File information
            analysis: Analysis results to update
        """
        file_path = file_info.get('path', '')
        file_size = file_info.get('size', 0)
        
        if file_size == 0:
            # Check if this file type should not be zero bytes
            file_ext = Path(file_path).suffix.lower()
            pattern = self.corruption_patterns['zero_byte_files']
            
            if file_ext in pattern['extensions']:
                self._add_corruption(
                    analysis,
                    CorruptionType.SIZE_ANOMALY,
                    pattern['severity'],
                    file_path,
                    f"Zero-byte file of type {file_ext}"
                )
    
    def _check_size_anomalies(
        self, 
        file_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check for file size anomalies.
        
        Args:
            file_info: File information
            analysis: Analysis results to update
        """
        file_path = file_info.get('path', '')
        file_size = file_info.get('size', 0)
        
        # Check for suspicious sizes (exact block sizes)
        pattern = self.corruption_patterns['suspicious_sizes']
        if file_size in pattern['patterns'] and file_size > 0:
            # Additional check: verify this isn't a legitimate small file
            file_ext = Path(file_path).suffix.lower()
            if file_ext in ['.exe', '.dll', '.so', '.pdf', '.doc']:
                self._add_corruption(
                    analysis,
                    CorruptionType.SIZE_ANOMALY,
                    pattern['severity'],
                    file_path,
                    f"Suspicious file size: {file_size} bytes"
                )
    
    def _check_file_signature(
        self, 
        file_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check file signature validation.
        
        Args:
            file_info: File information
            analysis: Analysis results to update
        """
        file_path = file_info.get('path', '')
        file_ext = Path(file_path).suffix.lower()
        
        # Only check files with known signatures
        if file_ext in self.file_signatures:
            try:
                if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                    with open(file_path, 'rb') as f:
                        header = f.read(32)  # Read first 32 bytes
                    
                    # Check if header matches expected signatures
                    expected_sigs = self.file_signatures[file_ext]
                    signature_match = any(
                        header.startswith(sig) for sig in expected_sigs
                    )
                    
                    if not signature_match:
                        self._add_corruption(
                            analysis,
                            CorruptionType.METADATA_CORRUPTION,
                            CorruptionSeverity.HIGH,
                            file_path,
                            f"Invalid file signature for {file_ext} file"
                        )
                        
            except Exception:
                # Don't flag as corruption if we can't read the file
                pass
    
    def _check_metadata_consistency(
        self, 
        file_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check metadata consistency.
        
        Args:
            file_info: File information
            analysis: Analysis results to update
        """
        file_path = file_info.get('path', '')
        
        # Check for invalid inode numbers
        inode = file_info.get('inode', 0)
        if inode == 0:
            self._add_corruption(
                analysis,
                CorruptionType.INODE_CORRUPTION,
                CorruptionSeverity.MEDIUM,
                file_path,
                "Invalid inode number (0)"
            )
        
        # Check for invalid device numbers
        device = file_info.get('device', 0)
        if device == 0:
            self._add_corruption(
                analysis,
                CorruptionType.METADATA_CORRUPTION,
                CorruptionSeverity.LOW,
                file_path,
                "Invalid device number (0)"
            )
    
    def _check_directory_metadata(
        self, 
        dir_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check directory metadata for corruption.
        
        Args:
            dir_info: Directory information
            analysis: Analysis results to update
        """
        dir_path = dir_info.get('path', '')
        
        # Check for invalid directory size
        size = dir_info.get('size', 0)
        if size == 0:
            # Directories should have some size for metadata
            self._add_corruption(
                analysis,
                CorruptionType.DIRECTORY_CORRUPTION,
                CorruptionSeverity.LOW,
                dir_path,
                "Directory with zero size"
            )
    
    def _check_directory_permissions(
        self, 
        dir_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check directory permissions for anomalies.
        
        Args:
            dir_info: Directory information
            analysis: Analysis results to update
        """
        dir_path = dir_info.get('path', '')
        mode = dir_info.get('mode', 0)
        
        # Check if directory has execute permission for owner
        if not (mode & 0o100):
            self._add_corruption(
                analysis,
                CorruptionType.PERMISSION_CORRUPTION,
                CorruptionSeverity.MEDIUM,
                dir_path,
                "Directory without owner execute permission"
            )
    
    def _check_permission_anomalies(
        self, 
        file_path: str, 
        perm_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check for permission anomalies.
        
        Args:
            file_path: Path to file
            perm_info: Permission information
            analysis: Analysis results to update
        """
        # Check for world-writable files (security risk)
        if perm_info.get('other_write', False):
            self._add_corruption(
                analysis,
                CorruptionType.PERMISSION_CORRUPTION,
                CorruptionSeverity.MEDIUM,
                file_path,
                "World-writable file (security risk)"
            )
        
        # Check for executable files without owner execute
        file_ext = Path(file_path).suffix.lower()
        if file_ext in ['.exe', '.sh', '.py', '.pl'] and not perm_info.get('owner_execute', False):
            self._add_corruption(
                analysis,
                CorruptionType.PERMISSION_CORRUPTION,
                CorruptionSeverity.LOW,
                file_path,
                "Executable file without execute permission"
            )
    
    def _check_timestamp_anomalies(
        self, 
        file_path: str, 
        timestamp_info: Dict[str, Any], 
        analysis: Dict[str, Any]
    ) -> None:
        """Check for timestamp anomalies.
        
        Args:
            file_path: Path to file
            timestamp_info: Timestamp information
            analysis: Analysis results to update
        """
        now = datetime.now().timestamp()
        
        # Check modification time
        mtime = timestamp_info.get('modify_time', now)
        
        # Check for future timestamps
        future_threshold = now + (self.thresholds['timestamp_future_days'] * 24 * 3600)
        if mtime > future_threshold:
            self._add_corruption(
                analysis,
                CorruptionType.TIMESTAMP_ANOMALY,
                CorruptionSeverity.MEDIUM,
                file_path,
                f"File modified in future: {datetime.fromtimestamp(mtime)}"
            )
        
        # Check for very old timestamps (potential corruption)
        past_threshold = now - (self.thresholds['timestamp_past_years'] * 365 * 24 * 3600)
        if mtime < past_threshold:
            self._add_corruption(
                analysis,
                CorruptionType.TIMESTAMP_ANOMALY,
                CorruptionSeverity.LOW,
                file_path,
                f"Very old timestamp: {datetime.fromtimestamp(mtime)}"
            )
        
        # Check for impossible timestamp relationships
        atime = timestamp_info.get('access_time', mtime)
        ctime = timestamp_info.get('change_time', mtime)
        
        if atime < mtime:
            self._add_corruption(
                analysis,
                CorruptionType.TIMESTAMP_ANOMALY,
                CorruptionSeverity.LOW,
                file_path,
                "Access time before modification time"
            )
    
    def _should_verify_checksum(self, file_path: str) -> bool:
        """Determine if a file's checksum should be verified.
        
        Args:
            file_path: Path to file
            
        Returns:
            bool: True if checksum should be verified
        """
        try:
            # Don't verify very large files to avoid performance impact
            if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
                return False
            
            # Don't verify system files that change frequently
            system_paths = ['/proc', '/sys', '/dev', 'System Volume Information']
            if any(sys_path in file_path for sys_path in system_paths):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """Verify a file's checksum.
        
        Args:
            file_path: Path to file
            expected_checksum: Expected checksum value
            
        Returns:
            bool: True if checksum matches, False otherwise
        """
        try:
            # Determine algorithm from checksum length
            if len(expected_checksum) == 32:
                hasher = hashlib.md5()
            elif len(expected_checksum) == 40:
                hasher = hashlib.sha1()
            elif len(expected_checksum) == 64:
                hasher = hashlib.sha256()
            else:
                return False
            
            # Calculate current checksum
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            
            current_checksum = hasher.hexdigest()
            return current_checksum.lower() == expected_checksum.lower()
            
        except Exception:
            return False
    
    def _add_corruption(
        self,
        analysis: Dict[str, Any],
        corruption_type: CorruptionType,
        severity: CorruptionSeverity,
        path: str,
        description: str
    ) -> None:
        """Add a corruption finding to the analysis.
        
        Args:
            analysis: Analysis results to update
            corruption_type: Type of corruption
            severity: Severity level
            path: Path where corruption was found
            description: Description of the corruption
        """
        corruption = {
            'type': corruption_type.value,
            'severity': severity.value,
            'path': path,
            'description': description,
            'timestamp': datetime.now().isoformat()
        }
        
        analysis['corruptions'].append(corruption)
        analysis['statistics']['corruptions_found'] += 1
        
        # Update severity counters
        if severity == CorruptionSeverity.CRITICAL:
            analysis['statistics']['critical_issues'] += 1
        elif severity == CorruptionSeverity.HIGH:
            analysis['statistics']['high_severity'] += 1
        elif severity == CorruptionSeverity.MEDIUM:
            analysis['statistics']['medium_severity'] += 1
        elif severity == CorruptionSeverity.LOW:
            analysis['statistics']['low_severity'] += 1
    
    def _generate_analysis_summary(self, analysis: Dict[str, Any]) -> None:
        """Generate analysis summary and recommendations.
        
        Args:
            analysis: Analysis results to update
        """
        stats = analysis['statistics']
        corruptions = analysis['corruptions']
        
        # Calculate corruption rate
        if stats['files_analyzed'] > 0:
            corruption_rate = stats['corruptions_found'] / stats['files_analyzed']
            stats['corruption_rate'] = corruption_rate
        else:
            corruption_rate = 0.0
        
        # Determine overall health
        if stats['critical_issues'] > 0:
            overall_health = 'critical'
        elif stats['high_severity'] > 0:
            overall_health = 'poor'
        elif stats['medium_severity'] > 5:
            overall_health = 'fair'
        elif stats['corruptions_found'] > 0:
            overall_health = 'good'
        else:
            overall_health = 'excellent'
        
        analysis['summary']['overall_health'] = overall_health
        analysis['summary']['corruption_rate'] = corruption_rate
        
        # Find most common corruption type
        if corruptions:
            type_counts = {}
            for corruption in corruptions:
                corruption_type = corruption['type']
                type_counts[corruption_type] = type_counts.get(corruption_type, 0) + 1
            
            most_common = max(type_counts.items(), key=lambda x: x[1])
            analysis['summary']['most_common_issue'] = {
                'type': most_common[0],
                'count': most_common[1]
            }
        
        # Generate recommendations
        recommendations = []
        
        if stats['critical_issues'] > 0:
            recommendations.append(
                "URGENT: Critical filesystem corruption detected. "
                "Immediate backup and repair recommended."
            )
        
        if stats['high_severity'] > 0:
            recommendations.append(
                "High-severity corruption found. Run filesystem check tools."
            )
        
        if corruption_rate > 0.1:
            recommendations.append(
                "High corruption rate detected. Consider full filesystem scan."
            )
        
        if stats['corruptions_found'] == 0:
            recommendations.append("No corruption detected. Filesystem appears healthy.")
        
        analysis['summary']['recommendations'] = recommendations
    
    def update_thresholds(self, new_thresholds: Dict[str, Any]) -> None:
        """Update detection thresholds.
        
        Args:
            new_thresholds: New threshold values
        """
        self.thresholds.update(new_thresholds)
    
    def get_corruption_statistics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed corruption statistics.
        
        Args:
            analysis: Analysis results
            
        Returns:
            Dict containing detailed statistics
        """
        corruptions = analysis.get('corruptions', [])
        
        # Group by type
        type_stats = {}
        severity_stats = {}
        
        for corruption in corruptions:
            corruption_type = corruption['type']
            severity = corruption['severity']
            
            type_stats[corruption_type] = type_stats.get(corruption_type, 0) + 1
            severity_stats[severity] = severity_stats.get(severity, 0) + 1
        
        return {
            'total_corruptions': len(corruptions),
            'by_type': type_stats,
            'by_severity': severity_stats,
            'corruption_rate': analysis.get('statistics', {}).get('corruption_rate', 0.0),
            'overall_health': analysis.get('summary', {}).get('overall_health', 'unknown')
        }