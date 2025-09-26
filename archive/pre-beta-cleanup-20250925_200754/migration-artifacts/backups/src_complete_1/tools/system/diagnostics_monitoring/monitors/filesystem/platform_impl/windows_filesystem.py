"""Windows-specific filesystem implementation with NTFS and chkdsk support."""

import os
import subprocess
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from ....core.platform_detector import get_platform_detector
from core.error_handler import error_handler


class WindowsFilesystemImpl:
    """Windows filesystem implementation.
    
    Provides Windows-specific filesystem operations including:
    - NTFS filesystem analysis
    - chkdsk integration and automation
    - Windows API filesystem checks
    - Volume and partition analysis
    - System file integrity checking
    - Registry-based filesystem information
    """
    
    def __init__(self):
        """Initialize Windows filesystem implementation."""
        self.logger = logging.getLogger(
            'RFU.DiagnosticsMonitoring.WindowsFilesystem'
        )
        self.platform_detector = get_platform_detector()
        
        # Windows-specific tools
        self.tools = {
            'chkdsk': 'chkdsk.exe',
            'sfc': 'sfc.exe',
            'dism': 'dism.exe',
            'fsutil': 'fsutil.exe',
            'wmic': 'wmic.exe'
        }
        
        # Check tool availability
        self._check_tool_availability()
        
        # NTFS-specific features
        self.ntfs_features = {
            'compression': True,
            'encryption': True,
            'quotas': True,
            'sparse_files': True,
            'reparse_points': True,
            'alternate_data_streams': True
        }
    
    def _check_tool_availability(self) -> None:
        """Check availability of Windows filesystem tools."""
        for tool_name, tool_path in self.tools.items():
            try:
                result = subprocess.run(
                    [tool_path, '/?'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0 and 'not found' in result.stderr.lower():
                    self.logger.warning(f"Tool not available: {tool_name}")
                    self.tools[tool_name] = None
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.logger.warning(f"Tool not found or timeout: {tool_name}")
                self.tools[tool_name] = None
            except Exception as e:
                self.logger.error(f"Error checking tool {tool_name}: {e}")
                self.tools[tool_name] = None
    
    def get_filesystem_info(self) -> Dict[str, Any]:
        """Get comprehensive Windows filesystem information.
        
        Returns:
            Dict containing filesystem information
        """
        try:
            info = {
                'platform': 'windows',
                'timestamp': datetime.now().isoformat(),
                'volumes': [],
                'system_info': {},
                'ntfs_features': self.ntfs_features.copy(),
                'tools_available': {k: v is not None for k, v in self.tools.items()}
            }
            
            # Get volume information
            info['volumes'] = self._get_volume_info()
            
            # Get system filesystem information
            info['system_info'] = self._get_system_filesystem_info()
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting filesystem info: {e}")
            error_handler.handle_error(e, "WindowsFilesystemImpl.get_filesystem_info")
            return {'error': str(e), 'platform': 'windows'}
    
    def _get_volume_info(self) -> List[Dict[str, Any]]:
        """Get information about all volumes.
        
        Returns:
            List of volume information dictionaries
        """
        volumes = []
        
        try:
            # Get drive letters
            drives = [f"{chr(i)}:\\" for i in range(ord('A'), ord('Z')+1) 
                     if os.path.exists(f"{chr(i)}:\\")]
            
            for drive in drives:
                try:
                    volume_info = self._get_single_volume_info(drive)
                    if volume_info:
                        volumes.append(volume_info)
                except Exception as e:
                    self.logger.error(f"Error getting info for {drive}: {e}")
                    volumes.append({
                        'drive': drive,
                        'error': str(e)
                    })
            
            return volumes
            
        except Exception as e:
            self.logger.error(f"Error enumerating volumes: {e}")
            return []
    
    def _get_single_volume_info(self, drive: str) -> Optional[Dict[str, Any]]:
        """Get information for a single volume.
        
        Args:
            drive: Drive letter (e.g., 'C:\\')
            
        Returns:
            Volume information dictionary or None
        """
        try:
            # Basic volume information
            stat_info = os.statvfs(drive) if hasattr(os, 'statvfs') else None
            
            volume_info = {
                'drive': drive,
                'exists': os.path.exists(drive),
                'filesystem': self._get_filesystem_type(drive),
                'label': self._get_volume_label(drive),
                'serial': self._get_volume_serial(drive),
                'total_space': 0,
                'free_space': 0,
                'used_space': 0,
                'ntfs_info': {},
                'health_status': 'unknown'
            }
            
            # Get space information
            if os.path.exists(drive):
                try:
                    total, used, free = self._get_disk_usage(drive)
                    volume_info.update({
                        'total_space': total,
                        'free_space': free,
                        'used_space': used,
                        'free_percent': (free / total * 100) if total > 0 else 0
                    })
                except Exception as e:
                    self.logger.error(f"Error getting disk usage for {drive}: {e}")
            
            # Get NTFS-specific information
            if volume_info['filesystem'].upper() == 'NTFS':
                volume_info['ntfs_info'] = self._get_ntfs_info(drive)
            
            # Get health status
            volume_info['health_status'] = self._get_volume_health(drive)
            
            return volume_info
            
        except Exception as e:
            self.logger.error(f"Error getting volume info for {drive}: {e}")
            return None
    
    def _get_filesystem_type(self, drive: str) -> str:
        """Get filesystem type for a drive.
        
        Args:
            drive: Drive letter
            
        Returns:
            Filesystem type string
        """
        try:
            if self.tools['fsutil']:
                result = subprocess.run(
                    [self.tools['fsutil'], 'fsinfo', 'volumeinfo', drive],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'File System Name' in line:
                            return line.split(':')[-1].strip()
            
            # Fallback method using wmic
            if self.tools['wmic']:
                result = subprocess.run(
                    [self.tools['wmic'], 'logicaldisk', 'where', f'DeviceID="{drive[:-1]}"',
                     'get', 'FileSystem', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'FileSystem=' in line:
                            return line.split('=')[-1].strip()
            
            return 'Unknown'
            
        except Exception as e:
            self.logger.error(f"Error getting filesystem type for {drive}: {e}")
            return 'Unknown'
    
    def _get_volume_label(self, drive: str) -> str:
        """Get volume label for a drive.
        
        Args:
            drive: Drive letter
            
        Returns:
            Volume label string
        """
        try:
            if self.tools['wmic']:
                result = subprocess.run(
                    [self.tools['wmic'], 'logicaldisk', 'where', f'DeviceID="{drive[:-1]}"',
                     'get', 'VolumeName', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'VolumeName=' in line:
                            return line.split('=')[-1].strip()
            
            return 'Unknown'
            
        except Exception as e:
            self.logger.error(f"Error getting volume label for {drive}: {e}")
            return 'Unknown'
    
    def _get_volume_serial(self, drive: str) -> str:
        """Get volume serial number for a drive.
        
        Args:
            drive: Drive letter
            
        Returns:
            Volume serial number string
        """
        try:
            if self.tools['wmic']:
                result = subprocess.run(
                    [self.tools['wmic'], 'logicaldisk', 'where', f'DeviceID="{drive[:-1]}"',
                     'get', 'VolumeSerialNumber', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'VolumeSerialNumber=' in line:
                            return line.split('=')[-1].strip()
            
            return 'Unknown'
            
        except Exception as e:
            self.logger.error(f"Error getting volume serial for {drive}: {e}")
            return 'Unknown'
    
    def _get_disk_usage(self, path: str) -> tuple:
        """Get disk usage information.
        
        Args:
            path: Path to check
            
        Returns:
            Tuple of (total, used, free) in bytes
        """
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            return total, used, free
        except Exception as e:
            self.logger.error(f"Error getting disk usage for {path}: {e}")
            return 0, 0, 0
    
    def _get_ntfs_info(self, drive: str) -> Dict[str, Any]:
        """Get NTFS-specific information.
        
        Args:
            drive: Drive letter
            
        Returns:
            NTFS information dictionary
        """
        ntfs_info = {
            'cluster_size': 0,
            'mft_size': 0,
            'compression_enabled': False,
            'encryption_enabled': False,
            'quotas_enabled': False,
            'features': []
        }
        
        try:
            if self.tools['fsutil']:
                # Get NTFS volume information
                result = subprocess.run(
                    [self.tools['fsutil'], 'fsinfo', 'ntfsinfo', drive],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    
                    # Parse cluster size
                    cluster_match = re.search(r'Bytes Per Cluster\s*:\s*(\d+)', output)
                    if cluster_match:
                        ntfs_info['cluster_size'] = int(cluster_match.group(1))
                    
                    # Parse MFT information
                    mft_match = re.search(r'Mft Valid Data Length\s*:\s*(\d+)', output)
                    if mft_match:
                        ntfs_info['mft_size'] = int(mft_match.group(1))
                    
                    # Check for features
                    if 'Compression' in output:
                        ntfs_info['compression_enabled'] = True
                        ntfs_info['features'].append('compression')
                    
                    if 'Encryption' in output:
                        ntfs_info['encryption_enabled'] = True
                        ntfs_info['features'].append('encryption')
                    
                    if 'Quotas' in output:
                        ntfs_info['quotas_enabled'] = True
                        ntfs_info['features'].append('quotas')
            
            return ntfs_info
            
        except Exception as e:
            self.logger.error(f"Error getting NTFS info for {drive}: {e}")
            return ntfs_info
    
    def _get_volume_health(self, drive: str) -> str:
        """Get volume health status.
        
        Args:
            drive: Drive letter
            
        Returns:
            Health status string
        """
        try:
            if self.tools['chkdsk']:
                # Run chkdsk in read-only mode to check health
                result = subprocess.run(
                    [self.tools['chkdsk'], drive, '/scan'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    output = result.stdout.lower()
                    if 'no problems found' in output or 'healthy' in output:
                        return 'healthy'
                    elif 'errors found' in output:
                        return 'errors_found'
                    elif 'corruption' in output:
                        return 'corrupted'
                    else:
                        return 'unknown'
                else:
                    return 'check_failed'
            
            return 'unknown'
            
        except Exception as e:
            self.logger.error(f"Error checking volume health for {drive}: {e}")
            return 'unknown'
    
    def _get_system_filesystem_info(self) -> Dict[str, Any]:
        """Get system-wide filesystem information.
        
        Returns:
            System filesystem information
        """
        system_info = {
            'windows_version': 'Unknown',
            'filesystem_drivers': [],
            'system_integrity': 'unknown',
            'boot_volume': 'Unknown'
        }
        
        try:
            # Get Windows version
            system_info['windows_version'] = self._get_windows_version()
            
            # Get filesystem drivers
            system_info['filesystem_drivers'] = self._get_filesystem_drivers()
            
            # Check system file integrity
            system_info['system_integrity'] = self._check_system_integrity()
            
            # Get boot volume
            system_info['boot_volume'] = self._get_boot_volume()
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Error getting system filesystem info: {e}")
            return system_info
    
    def _get_windows_version(self) -> str:
        """Get Windows version information.
        
        Returns:
            Windows version string
        """
        try:
            if self.tools['wmic']:
                result = subprocess.run(
                    [self.tools['wmic'], 'os', 'get', 'Caption,Version', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    caption = ''
                    version = ''
                    for line in result.stdout.split('\n'):
                        if 'Caption=' in line:
                            caption = line.split('=')[-1].strip()
                        elif 'Version=' in line:
                            version = line.split('=')[-1].strip()
                    
                    return f"{caption} ({version})" if caption and version else 'Unknown'
            
            return 'Unknown'
            
        except Exception as e:
            self.logger.error(f"Error getting Windows version: {e}")
            return 'Unknown'
    
    def _get_filesystem_drivers(self) -> List[str]:
        """Get list of filesystem drivers.
        
        Returns:
            List of filesystem driver names
        """
        drivers = []
        
        try:
            if self.tools['wmic']:
                result = subprocess.run(
                    [self.tools['wmic'], 'systemdriver', 'where', 
                     'ServiceType="File System Driver"', 'get', 'Name', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'Name=' in line:
                            driver_name = line.split('=')[-1].strip()
                            if driver_name:
                                drivers.append(driver_name)
            
            return drivers
            
        except Exception as e:
            self.logger.error(f"Error getting filesystem drivers: {e}")
            return []
    
    def _check_system_integrity(self) -> str:
        """Check system file integrity using SFC.
        
        Returns:
            System integrity status
        """
        try:
            if self.tools['sfc']:
                # Run SFC scan (this may take a while)
                result = subprocess.run(
                    [self.tools['sfc'], '/verifyonly'],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout
                )
                
                if result.returncode == 0:
                    output = result.stdout.lower()
                    if 'no integrity violations' in output:
                        return 'healthy'
                    elif 'corrupt files' in output:
                        return 'corrupted'
                    else:
                        return 'unknown'
                else:
                    return 'check_failed'
            
            return 'unknown'
            
        except subprocess.TimeoutExpired:
            self.logger.warning("SFC scan timed out")
            return 'timeout'
        except Exception as e:
            self.logger.error(f"Error checking system integrity: {e}")
            return 'unknown'
    
    def _get_boot_volume(self) -> str:
        """Get boot volume information.
        
        Returns:
            Boot volume identifier
        """
        try:
            if self.tools['wmic']:
                result = subprocess.run(
                    [self.tools['wmic'], 'logicaldisk', 'where', 
                     'DriveType=3', 'get', 'DeviceID,SystemName', '/value'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Usually C: is the boot volume, but let's be more specific
                    for line in result.stdout.split('\n'):
                        if 'DeviceID=C' in line:
                            return 'C:\\'
            
            return 'C:\\'  # Default assumption
            
        except Exception as e:
            self.logger.error(f"Error getting boot volume: {e}")
            return 'Unknown'
    
    def run_chkdsk(
        self, 
        drive: str, 
        fix_errors: bool = False,
        scan_only: bool = True
    ) -> Dict[str, Any]:
        """Run chkdsk on a specified drive.
        
        Args:
            drive: Drive letter to check
            fix_errors: Whether to fix errors (requires admin)
            scan_only: Whether to only scan without fixing
            
        Returns:
            chkdsk results dictionary
        """
        try:
            if not self.tools['chkdsk']:
                return {
                    'success': False,
                    'error': 'chkdsk tool not available'
                }
            
            # Build command
            cmd = [self.tools['chkdsk'], drive]
            
            if scan_only:
                cmd.append('/scan')
            elif fix_errors:
                cmd.extend(['/f', '/r'])
            
            # Run chkdsk
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd),
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'chkdsk timed out',
                'timeout': True
            }
        except Exception as e:
            self.logger.error(f"Error running chkdsk: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_repair_recommendations(
        self, 
        volume_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get Windows-specific repair recommendations.
        
        Args:
            volume_info: Volume information from analysis
            
        Returns:
            List of repair recommendations
        """
        recommendations = []
        
        try:
            drive = volume_info.get('drive', 'C:\\')
            health_status = volume_info.get('health_status', 'unknown')
            filesystem = volume_info.get('filesystem', '').upper()
            
            # Basic health recommendations
            if health_status == 'errors_found':
                recommendations.append({
                    'priority': 'high',
                    'action': 'run_chkdsk_fix',
                    'description': f'Run chkdsk /f /r on {drive} to fix errors',
                    'command': f'chkdsk {drive} /f /r',
                    'requires_admin': True,
                    'requires_reboot': drive.upper() == 'C:\\'
                })
            
            elif health_status == 'corrupted':
                recommendations.append({
                    'priority': 'critical',
                    'action': 'emergency_repair',
                    'description': f'Critical corruption on {drive} - immediate repair needed',
                    'command': f'chkdsk {drive} /f /r /x',
                    'requires_admin': True,
                    'requires_reboot': True
                })
            
            # NTFS-specific recommendations
            if filesystem == 'NTFS':
                ntfs_info = volume_info.get('ntfs_info', {})
                cluster_size = ntfs_info.get('cluster_size', 0)
                
                if cluster_size > 0 and cluster_size > 8192:
                    recommendations.append({
                        'priority': 'low',
                        'action': 'optimize_cluster_size',
                        'description': f'Large cluster size ({cluster_size}) may waste space',
                        'command': 'Consider reformatting with smaller cluster size',
                        'requires_admin': False,
                        'requires_reboot': False
                    })
            
            # System integrity recommendations
            if drive.upper() == 'C:\\':
                recommendations.append({
                    'priority': 'medium',
                    'action': 'run_sfc',
                    'description': 'Run System File Checker to verify system files',
                    'command': 'sfc /scannow',
                    'requires_admin': True,
                    'requires_reboot': False
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating repair recommendations: {e}")
            return []
    
    def is_admin_required(self, operation: str) -> bool:
        """Check if operation requires administrator privileges.
        
        Args:
            operation: Operation to check
            
        Returns:
            True if admin privileges required
        """
        admin_operations = {
            'chkdsk_fix', 'sfc_scan', 'system_repair',
            'driver_update', 'registry_repair'
        }
        
        return operation in admin_operations
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported filesystem operations.
        
        Returns:
            List of supported operation names
        """
        operations = [
            'volume_scan',
            'health_check',
            'ntfs_analysis',
            'system_integrity_check'
        ]
        
        if self.tools['chkdsk']:
            operations.extend(['chkdsk_scan', 'chkdsk_fix'])
        
        if self.tools['sfc']:
            operations.append('sfc_scan')
        
        if self.tools['dism']:
            operations.append('dism_repair')
        
        return operations