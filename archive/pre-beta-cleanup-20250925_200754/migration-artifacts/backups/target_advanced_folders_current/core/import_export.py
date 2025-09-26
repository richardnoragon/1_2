"""
Advanced Folders Import/Export System

This module provides comprehensive import/export functionality for Advanced Folders
configurations, supporting multiple formats with validation and conflict resolution.
"""

import json
import logging
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .folder_configuration import (FolderConfiguration,
                                   FolderConfigurationManager,
                                   FolderStatistics, SearchParameters,
                                   SortCriteria)


class ImportExportError(Exception):
    """Base exception for import/export operations."""
    pass


class ValidationError(ImportExportError):
    """Exception for validation failures."""
    pass


class ConflictError(ImportExportError):
    """Exception for configuration conflicts."""
    pass


class ConfigurationValidator:
    """Validates imported configuration data."""
    
    def __init__(self):
        self.logger = logging.getLogger('AdvancedFolders.Validator')
    
    def validate_export_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate exported configuration data.
        
        Args:
            data: Configuration data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required top-level fields
        if 'advanced_folders_export' not in data:
            errors.append("Missing 'advanced_folders_export' root element")
            return errors
        
        export_data = data['advanced_folders_export']
        
        # Check version
        if 'version' not in export_data:
            errors.append("Missing export version")
        elif not isinstance(export_data['version'], str):
            errors.append("Export version must be a string")
        
        # Check metadata
        if 'metadata' not in export_data:
            errors.append("Missing export metadata")
        else:
            errors.extend(self._validate_metadata(export_data['metadata']))
        
        # Check configurations
        if 'configurations' not in export_data:
            errors.append("Missing configurations array")
        else:
            errors.extend(self._validate_configurations(export_data['configurations']))
        
        return errors
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate export metadata."""
        errors = []
        
        required_fields = ['export_date', 'exported_by', 'total_configurations']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"Missing metadata field: {field}")
        
        if 'total_configurations' in metadata:
            if not isinstance(metadata['total_configurations'], int):
                errors.append("total_configurations must be an integer")
            elif metadata['total_configurations'] < 0:
                errors.append("total_configurations cannot be negative")
        
        return errors
    
    def _validate_configurations(self, configurations: List[Dict[str, Any]]) -> List[str]:
        """Validate configuration data."""
        errors = []
        
        if not isinstance(configurations, list):
            errors.append("Configurations must be a list")
            return errors
        
        for i, config in enumerate(configurations):
            config_errors = self._validate_single_configuration(config, i)
            errors.extend(config_errors)
        
        return errors
    
    def _validate_single_configuration(self, config: Dict[str, Any], index: int) -> List[str]:
        """Validate a single configuration."""
        errors = []
        prefix = f"Configuration {index}: "
        
        # Required fields
        required_fields = ['folder_id', 'name', 'directory_paths']
        for field in required_fields:
            if field not in config:
                errors.append(f"{prefix}Missing required field: {field}")
        
        # Validate field types
        if 'name' in config and not isinstance(config['name'], str):
            errors.append(f"{prefix}Name must be a string")
        
        if 'directory_paths' in config:
            if not isinstance(config['directory_paths'], list):
                errors.append(f"{prefix}Directory paths must be a list")
            elif len(config['directory_paths']) == 0:
                errors.append(f"{prefix}At least one directory path required")
        
        return errors


class ConflictResolver:
    """Handles conflicts during import operations."""
    
    def __init__(self, manager: FolderConfigurationManager):
        self.manager = manager
        self.logger = logging.getLogger('AdvancedFolders.ConflictResolver')
    
    def resolve_conflicts(self, import_configs: List[Dict[str, Any]], 
                         resolution_strategy: str = 'prompt') -> Tuple[List[Dict[str, Any]], List[str]]:
        """Resolve conflicts between import and existing configurations.
        
        Args:
            import_configs: Configurations to import
            resolution_strategy: How to handle conflicts ('skip', 'overwrite', 'rename', 'prompt')
            
        Returns:
            Tuple of (resolved_configs, conflict_messages)
        """
        existing_configs = {config.name: config for config in self.manager.list_folders()}
        existing_ids = {config.folder_id: config for config in self.manager.list_folders()}
        
        resolved_configs = []
        conflict_messages = []
        
        for config_data in import_configs:
            name = config_data.get('name', '')
            folder_id = config_data.get('folder_id', '')
            
            # Check for name conflicts
            name_conflict = name in existing_configs
            id_conflict = folder_id in existing_ids
            
            if name_conflict or id_conflict:
                resolved_config, message = self._resolve_single_conflict(
                    config_data, name_conflict, id_conflict, resolution_strategy
                )
                if resolved_config:
                    resolved_configs.append(resolved_config)
                if message:
                    conflict_messages.append(message)
            else:
                resolved_configs.append(config_data)
        
        return resolved_configs, conflict_messages
    
    def _resolve_single_conflict(self, config_data: Dict[str, Any], 
                                name_conflict: bool, id_conflict: bool,
                                strategy: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Resolve a single configuration conflict."""
        name = config_data.get('name', '')
        
        if strategy == 'skip':
            return None, f"Skipped '{name}' due to conflict"
        
        elif strategy == 'overwrite':
            return config_data, f"Overwrote existing '{name}'"
        
        elif strategy == 'rename':
            new_name = self._generate_unique_name(name)
            config_data['name'] = new_name
            # Generate new ID to avoid ID conflicts
            from uuid import uuid4
            config_data['folder_id'] = str(uuid4())
            return config_data, f"Renamed '{name}' to '{new_name}'"
        
        elif strategy == 'prompt':
            # For automated testing, default to rename
            return self._resolve_single_conflict(config_data, name_conflict, id_conflict, 'rename')
        
        return None, f"Unresolved conflict for '{name}'"
    
    def _generate_unique_name(self, base_name: str) -> str:
        """Generate a unique name by appending a number."""
        existing_names = {config.name for config in self.manager.list_folders()}
        
        if base_name not in existing_names:
            return base_name
        
        counter = 1
        while f"{base_name} ({counter})" in existing_names:
            counter += 1
        
        return f"{base_name} ({counter})"


class ConfigurationExporter:
    """Handles export of Advanced Folders configurations."""
    
    def __init__(self, manager: FolderConfigurationManager):
        self.manager = manager
        self.validator = ConfigurationValidator()
        self.logger = logging.getLogger('AdvancedFolders.Exporter')
    
    def export_to_file(self, export_path: Path, 
                      config_ids: Optional[List[str]] = None,
                      include_statistics: bool = False,
                      compress: bool = False) -> bool:
        """Export configurations to file.
        
        Args:
            export_path: Destination file path
            config_ids: Optional list of specific config IDs to export (all if None)
            include_statistics: Whether to include statistics in export
            compress: Whether to compress the export file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get configurations to export
            if config_ids:
                configurations = []
                for config_id in config_ids:
                    config = self.manager.get_folder(config_id)
                    if config:
                        configurations.append(config)
                    else:
                        self.logger.warning(f"Configuration not found: {config_id}")
            else:
                configurations = self.manager.list_folders()
            
            # Create export data
            export_data = self._create_export_data(configurations, include_statistics)
            
            # Validate export data
            errors = self.validator.validate_export_data(export_data)
            if errors:
                self.logger.error(f"Export validation failed: {errors}")
                return False
            
            # Write to file
            if compress:
                return self._write_compressed_export(export_path, export_data)
            else:
                return self._write_json_export(export_path, export_data)
        
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return False
    
    def _create_export_data(self, configurations: List[FolderConfiguration],
                           include_statistics: bool) -> Dict[str, Any]:
        """Create export data structure."""
        config_dicts = []
        for config in configurations:
            config_dict = config.to_dict()
            if not include_statistics:
                # Remove statistics to reduce file size
                config_dict.pop('statistics', None)
            config_dicts.append(config_dict)
        
        export_data = {
            'advanced_folders_export': {
                'version': '1.0',
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'exported_by': 'Advanced Folders v1.0',
                    'total_configurations': len(configurations),
                    'include_statistics': include_statistics,
                    'export_format': 'json'
                },
                'configurations': config_dicts
            }
        }
        
        return export_data
    
    def _write_json_export(self, export_path: Path, export_data: Dict[str, Any]) -> bool:
        """Write export data as JSON file."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Export completed: {export_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to write JSON export: {e}")
            return False
    
    def _write_compressed_export(self, export_path: Path, export_data: Dict[str, Any]) -> bool:
        """Write export data as compressed ZIP file."""
        try:
            # Ensure .zip extension
            if not export_path.suffix.lower() == '.zip':
                export_path = export_path.with_suffix('.zip')
            
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
                zf.writestr('advanced_folders_config.json', json_data)
            
            self.logger.info(f"Compressed export completed: {export_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to write compressed export: {e}")
            return False


class ConfigurationImporter:
    """Handles import of Advanced Folders configurations."""
    
    def __init__(self, manager: FolderConfigurationManager):
        self.manager = manager
        self.validator = ConfigurationValidator()
        self.conflict_resolver = ConflictResolver(manager)
        self.logger = logging.getLogger('AdvancedFolders.Importer')
    
    def import_from_file(self, import_path: Path,
                        conflict_resolution: str = 'prompt',
                        validate_paths: bool = True) -> Tuple[bool, List[str]]:
        """Import configurations from file.
        
        Args:
            import_path: Source file path
            conflict_resolution: How to handle conflicts ('skip', 'overwrite', 'rename', 'prompt')
            validate_paths: Whether to validate directory paths exist
            
        Returns:
            Tuple of (success, messages)
        """
        try:
            # Read import data
            if import_path.suffix.lower() == '.zip':
                import_data = self._read_compressed_import(import_path)
            else:
                import_data = self._read_json_import(import_path)
            
            if not import_data:
                return False, ["Failed to read import file"]
            
            # Validate import data
            errors = self.validator.validate_export_data(import_data)
            if errors:
                return False, [f"Validation error: {error}" for error in errors]
            
            # Extract configurations
            config_data = import_data['advanced_folders_export']['configurations']
            
            # Resolve conflicts
            resolved_configs, conflict_messages = self.conflict_resolver.resolve_conflicts(
                config_data, conflict_resolution
            )
            
            # Import configurations
            success_count = 0
            error_messages = []
            
            for config_dict in resolved_configs:
                try:
                    if validate_paths:
                        path_errors = self._validate_directory_paths(config_dict)
                        if path_errors:
                            error_messages.extend(path_errors)
                            continue
                    
                    # Create configuration object
                    config = FolderConfiguration.from_dict(config_dict)
                    
                    # Add to manager
                    self.manager._configurations[config.folder_id] = config
                    success_count += 1
                    
                except Exception as e:
                    error_messages.append(f"Failed to import '{config_dict.get('name', 'Unknown')}': {e}")
            
            # Save imported configurations
            if success_count > 0:
                self.manager.save_configurations()
            
            # Prepare result messages
            messages = conflict_messages + error_messages
            messages.append(f"Successfully imported {success_count} configurations")
            
            self.logger.info(f"Import completed: {success_count} imported, {len(error_messages)} failed")
            
            return success_count > 0, messages
        
        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            return False, [f"Import failed: {e}"]
    
    def _read_json_import(self, import_path: Path) -> Optional[Dict[str, Any]]:
        """Read import data from JSON file."""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to read JSON import: {e}")
            return None
    
    def _read_compressed_import(self, import_path: Path) -> Optional[Dict[str, Any]]:
        """Read import data from compressed ZIP file."""
        try:
            with zipfile.ZipFile(import_path, 'r') as zf:
                # Look for the configuration file
                config_files = [name for name in zf.namelist() 
                               if name.endswith('.json')]
                
                if not config_files:
                    self.logger.error("No JSON configuration file found in ZIP")
                    return None
                
                # Read the first JSON file
                with zf.open(config_files[0]) as f:
                    return json.load(f)
        
        except Exception as e:
            self.logger.error(f"Failed to read compressed import: {e}")
            return None
    
    def _validate_directory_paths(self, config_dict: Dict[str, Any]) -> List[str]:
        """Validate that directory paths exist."""
        errors = []
        directory_paths = config_dict.get('directory_paths', [])
        
        for path_str in directory_paths:
            path = Path(path_str)
            if not path.exists():
                errors.append(f"Directory does not exist: {path_str}")
            elif not path.is_dir():
                errors.append(f"Path is not a directory: {path_str}")
        
        return errors


class ImportExportManager:
    """Main manager for import/export operations."""
    
    def __init__(self, config_manager: FolderConfigurationManager):
        self.config_manager = config_manager
        self.exporter = ConfigurationExporter(config_manager)
        self.importer = ConfigurationImporter(config_manager)
        self.logger = logging.getLogger('AdvancedFolders.ImportExport')
    
    def export_configurations(self, export_path: Union[str, Path],
                            config_ids: Optional[List[str]] = None,
                            **options) -> bool:
        """Export configurations with options.
        
        Args:
            export_path: Destination file path
            config_ids: Optional list of specific config IDs to export
            **options: Additional export options
            
        Returns:
            True if export successful
        """
        export_path = Path(export_path)
        
        # Filter options for export (remove import-only options)
        export_options = {k: v for k, v in options.items()
                          if k in ['include_statistics', 'compress']}

        return self.exporter.export_to_file(
            export_path, config_ids, **export_options)
    
    def import_configurations(self, import_path: Union[str, Path],
                            **options) -> Tuple[bool, List[str]]:
        """Import configurations with options.
        
        Args:
            import_path: Source file path
            **options: Additional import options
            
        Returns:
            Tuple of (success, messages)
        """
        import_path = Path(import_path)
        return self.importer.import_from_file(import_path, **options)
    
    def create_backup(self, backup_path: Union[str, Path]) -> bool:
        """Create a complete backup of all configurations.
        
        Args:
            backup_path: Backup file path
            
        Returns:
            True if backup successful
        """
        backup_path = Path(backup_path)
        
        # Add timestamp to backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if backup_path.suffix:
            name = backup_path.stem + f"_backup_{timestamp}"
            backup_path = backup_path.parent / f"{name}{backup_path.suffix}"
        else:
            backup_path = backup_path.parent / f"{backup_path.name}_backup_{timestamp}.json"
        
        return self.exporter.export_to_file(
            backup_path, 
            include_statistics=True,
            compress=True
        )
    
    def get_export_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return ['json', 'zip']
    
    def get_import_formats(self) -> List[str]:
        """Get list of supported import formats."""
        return ['json', 'zip']