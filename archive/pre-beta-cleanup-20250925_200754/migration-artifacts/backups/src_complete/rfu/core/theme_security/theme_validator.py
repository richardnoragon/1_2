"""
Theme Integrity Validator for RFU Hub

Provides comprehensive corruption detection and validation for theme data:
- Structure validation for theme configuration
- Checksum verification and integrity checking
- Malformed data detection and reporting
- Corruption analysis and classification
"""

import logging
import json
import hashlib
import os
from typing import Dict, Any, Optional
import datetime
import re


class CorruptionType:
    """Constants for different types of corruption."""
    STRUCTURAL = "structural"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    MALFORMED_JSON = "malformed_json"
    MISSING_FIELDS = "missing_fields"
    INVALID_VALUES = "invalid_values"
    FILE_TRUNCATED = "file_truncated"
    ENCODING_ERROR = "encoding_error"


class ValidationConstants:
    """Constants for validation recommendations and messages."""
    RESTORE_FROM_BACKUP = 'Restore from backup'
    USE_DEFAULT_THEME = 'Use default theme as fallback'
    ATTEMPT_AUTO_REPAIR = 'Attempt automatic repair'
    MONITOR_ISSUES = 'Monitor for further issues'


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self, valid: bool = True, corruption_type: str = None,
                 error_message: str = None, details: Dict[str, Any] = None):
        self.valid = valid
        self.corruption_type = corruption_type
        self.error_message = error_message
        self.details = details or {}
        self.timestamp = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            'valid': self.valid,
            'corruption_type': self.corruption_type,
            'error_message': self.error_message,
            'details': self.details,
            'timestamp': self.timestamp
        }


class ThemeIntegrityValidator:
    """
    Comprehensive validator for theme data integrity and corruption detection.
    
    This class provides multiple validation methods to detect various types
    of corruption in theme data files.
    """
    
    def __init__(self):
        """Initialize the Theme Integrity Validator."""
        self.logger = logging.getLogger('RFU.ThemeIntegrityValidator')
        
        # Define required theme structure
        self.required_fields = {
            'theme_name': str,
            'version': str,
            'colors': dict,
            'fonts': dict,
            'layout': dict
        }
        
        # Define required color fields
        self.required_color_fields = {
            'primary': str,
            'secondary': str,
            'background': str,
            'text': str
        }
        
        # Define required font fields
        self.required_font_fields = {
            'family': str,
            'size': (int, float),
            'weight': str
        }
        
        # Pattern for valid color values (hex, rgb, rgba, named colors)
        self.color_pattern = re.compile(
            r'^#[0-9a-fA-F]{6}$|'
            r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$|'
            r'^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[01]?\.?\d*\s*\)$|'
            r'^[a-zA-Z]+$'
        )
        
        self.logger.info("Theme Integrity Validator initialized")
    
    def validate_theme_file(self, file_path: str) -> ValidationResult:
        """
        Validate a theme file for corruption and integrity.
        
        Args:
            file_path: Path to the theme file
            
        Returns:
            ValidationResult object with validation status and details
        """
        try:
            self.logger.debug(f"Validating theme file: {file_path}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.MISSING_FIELDS,
                    error_message=f"Theme file not found: {file_path}"
                )
            
            # Check file size (detect truncation)
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.FILE_TRUNCATED,
                    error_message="Theme file is empty"
                )
            
            # Read and validate file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError as e:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.ENCODING_ERROR,
                    error_message=f"File encoding error: {e}"
                )
            
            # Validate JSON structure
            try:
                theme_data = json.loads(content)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.MALFORMED_JSON,
                    error_message=f"Invalid JSON format: {e}",
                    details={'line': e.lineno, 'column': e.colno}
                )
            
            # Validate theme data structure
            return self.validate_theme_data(theme_data)
            
        except Exception as e:
            self.logger.error(f"Theme file validation failed: {e}")
            return ValidationResult(
                valid=False,
                corruption_type=CorruptionType.STRUCTURAL,
                error_message=f"Validation error: {e}"
            )
    
    def validate_theme_data(self, theme_data: Any) -> ValidationResult:
        """
        Validate theme data structure and content.
        
        Args:
            theme_data: Theme data to validate
            
        Returns:
            ValidationResult object with validation status and details
        """
        try:
            # Check if data is a dictionary
            if not isinstance(theme_data, dict):
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.STRUCTURAL,
                    error_message="Theme data must be a dictionary"
                )
            
            # Validate required fields
            missing_fields = []
            invalid_types = []
            
            for field, expected_type in self.required_fields.items():
                if field not in theme_data:
                    missing_fields.append(field)
                elif not isinstance(theme_data[field], expected_type):
                    invalid_types.append({
                        'field': field,
                        'expected': expected_type.__name__,
                        'actual': type(theme_data[field]).__name__
                    })
            
            if missing_fields:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.MISSING_FIELDS,
                    error_message=f"Missing required fields: {missing_fields}",
                    details={'missing_fields': missing_fields}
                )
            
            if invalid_types:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.INVALID_VALUES,
                    error_message="Invalid field types detected",
                    details={'invalid_types': invalid_types}
                )
            
            # Validate colors section
            color_validation = self._validate_colors(theme_data.get('colors', {}))
            if not color_validation.valid:
                return color_validation
            
            # Validate fonts section
            font_validation = self._validate_fonts(theme_data.get('fonts', {}))
            if not font_validation.valid:
                return font_validation
            
            # Validate layout section
            layout_validation = self._validate_layout(theme_data.get('layout', {}))
            if not layout_validation.valid:
                return layout_validation
            
            # Validate theme name format
            theme_name = theme_data.get('theme_name', '')
            if not re.match(r'^[a-zA-Z0-9_\-\s]+$', theme_name):
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.INVALID_VALUES,
                    error_message="Invalid theme name format",
                    details={'theme_name': theme_name}
                )
            
            # Validate version format
            version = theme_data.get('version', '')
            if not re.match(r'^\d+\.\d+(\.\d+)?$', version):
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.INVALID_VALUES,
                    error_message="Invalid version format",
                    details={'version': version}
                )
            
            return ValidationResult(valid=True)
            
        except Exception as e:
            self.logger.error(f"Theme data validation failed: {e}")
            return ValidationResult(
                valid=False,
                corruption_type=CorruptionType.STRUCTURAL,
                error_message=f"Validation error: {e}"
            )
    
    def _validate_colors(self, colors: Dict[str, Any]) -> ValidationResult:
        """Validate colors section of theme data."""
        try:
            # Check required color fields
            missing_colors = []
            invalid_colors = []
            
            for color_field in self.required_color_fields:
                if color_field not in colors:
                    missing_colors.append(color_field)
                else:
                    color_value = colors[color_field]
                    if not isinstance(color_value, str):
                        invalid_colors.append({
                            'field': color_field,
                            'value': color_value,
                            'error': 'Color value must be a string'
                        })
                    elif not self.color_pattern.match(color_value):
                        invalid_colors.append({
                            'field': color_field,
                            'value': color_value,
                            'error': 'Invalid color format'
                        })
            
            if missing_colors:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.MISSING_FIELDS,
                    error_message=f"Missing required colors: {missing_colors}",
                    details={'missing_colors': missing_colors}
                )
            
            if invalid_colors:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.INVALID_VALUES,
                    error_message="Invalid color values detected",
                    details={'invalid_colors': invalid_colors}
                )
            
            return ValidationResult(valid=True)
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                corruption_type=CorruptionType.STRUCTURAL,
                error_message=f"Color validation error: {e}"
            )
    
    def _validate_fonts(self, fonts: Dict[str, Any]) -> ValidationResult:
        """Validate fonts section of theme data."""
        try:
            # Check if fonts is a dictionary with at least one font
            if not fonts:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.MISSING_FIELDS,
                    error_message="No font configurations found"
                )
            
            invalid_fonts = []
            
            for font_name, font_config in fonts.items():
                if not isinstance(font_config, dict):
                    invalid_fonts.append({
                        'font': font_name,
                        'error': 'Font configuration must be a dictionary'
                    })
                    continue
                
                # Check required font fields
                for field, expected_type in self.required_font_fields.items():
                    if field not in font_config:
                        invalid_fonts.append({
                            'font': font_name,
                            'field': field,
                            'error': f'Missing required field: {field}'
                        })
                    elif not isinstance(font_config[field], expected_type):
                        invalid_fonts.append({
                            'font': font_name,
                            'field': field,
                            'error': f'Expected {expected_type}, got {type(font_config[field])}'
                        })
                
                # Validate font size range
                if 'size' in font_config:
                    size = font_config['size']
                    if isinstance(size, (int, float)) and (size < 6 or size > 72):
                        invalid_fonts.append({
                            'font': font_name,
                            'field': 'size',
                            'error': f'Font size {size} out of valid range (6-72)'
                        })
            
            if invalid_fonts:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.INVALID_VALUES,
                    error_message="Invalid font configurations detected",
                    details={'invalid_fonts': invalid_fonts}
                )
            
            return ValidationResult(valid=True)
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                corruption_type=CorruptionType.STRUCTURAL,
                error_message=f"Font validation error: {e}"
            )
    
    def _validate_layout(self, layout: Dict[str, Any]) -> ValidationResult:
        """Validate layout section of theme data."""
        try:
            # Layout validation is more flexible - just check basic structure
            if not isinstance(layout, dict):
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.STRUCTURAL,
                    error_message="Layout configuration must be a dictionary"
                )
            
            # Check for numeric values in layout (dimensions, margins, etc.)
            invalid_layout = []
            
            for key, value in layout.items():
                if isinstance(value, dict):
                    # Nested layout properties
                    for nested_key, nested_value in value.items():
                        if isinstance(nested_value, str) and nested_value.endswith('px'):
                            # Check pixel values
                            try:
                                pixel_value = int(nested_value[:-2])
                                if pixel_value < 0:
                                    invalid_layout.append({
                                        'field': f'{key}.{nested_key}',
                                        'value': nested_value,
                                        'error': 'Negative pixel values not allowed'
                                    })
                            except ValueError:
                                invalid_layout.append({
                                    'field': f'{key}.{nested_key}',
                                    'value': nested_value,
                                    'error': 'Invalid pixel value format'
                                })
            
            if invalid_layout:
                return ValidationResult(
                    valid=False,
                    corruption_type=CorruptionType.INVALID_VALUES,
                    error_message="Invalid layout values detected",
                    details={'invalid_layout': invalid_layout}
                )
            
            return ValidationResult(valid=True)
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                corruption_type=CorruptionType.STRUCTURAL,
                error_message=f"Layout validation error: {e}"
            )
    
    def calculate_file_checksum(self, file_path: str) -> Optional[str]:
        """
        Calculate SHA-256 checksum for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex-encoded SHA-256 checksum or None if failed
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
            
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return None
    
    def verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        """
        Verify file checksum against expected value.
        
        Args:
            file_path: Path to the file
            expected_checksum: Expected SHA-256 checksum
            
        Returns:
            True if checksum matches
        """
        actual_checksum = self.calculate_file_checksum(file_path)
        return actual_checksum is not None and actual_checksum == expected_checksum
    
    def analyze_corruption(self, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive corruption analysis on a theme file.
        
        Args:
            file_path: Path to the theme file
            
        Returns:
            Dictionary with detailed corruption analysis
        """
        try:
            analysis = {
                'file_path': file_path,
                'timestamp': datetime.datetime.now().isoformat(),
                'file_exists': os.path.exists(file_path),
                'corruption_detected': False,
                'corruption_types': [],
                'severity': 'none',
                'recommendations': []
            }
            
            if not analysis['file_exists']:
                analysis['corruption_detected'] = True
                analysis['corruption_types'].append(CorruptionType.MISSING_FIELDS)
                analysis['severity'] = 'critical'
                analysis['recommendations'].append(
                    ValidationConstants.RESTORE_FROM_BACKUP
                )
                return analysis
            
            # File size analysis
            file_size = os.path.getsize(file_path)
            analysis['file_size'] = file_size
            
            if file_size == 0:
                analysis['corruption_detected'] = True
                analysis['corruption_types'].append(CorruptionType.FILE_TRUNCATED)
                analysis['severity'] = 'critical'
                analysis['recommendations'].append('Restore from backup')
                return analysis
            
            # Validate the file
            validation_result = self.validate_theme_file(file_path)
            
            if not validation_result.valid:
                analysis['corruption_detected'] = True
                analysis['corruption_types'].append(validation_result.corruption_type)
                analysis['error_message'] = validation_result.error_message
                analysis['validation_details'] = validation_result.details
                
                # Determine severity
                if validation_result.corruption_type in [
                    CorruptionType.MISSING_FIELDS,
                    CorruptionType.FILE_TRUNCATED,
                    CorruptionType.MALFORMED_JSON
                ]:
                    analysis['severity'] = 'high'
                    analysis['recommendations'].extend([
                        'Restore from backup',
                        'Use default theme as fallback'
                    ])
                elif validation_result.corruption_type in [
                    CorruptionType.INVALID_VALUES,
                    CorruptionType.CHECKSUM_MISMATCH
                ]:
                    analysis['severity'] = 'medium'
                    analysis['recommendations'].extend([
                        'Attempt automatic repair',
                        'Restore from backup if repair fails'
                    ])
                else:
                    analysis['severity'] = 'low'
                    analysis['recommendations'].append('Monitor for further issues')
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Corruption analysis failed: {e}")
            return {
                'file_path': file_path,
                'timestamp': datetime.datetime.now().isoformat(),
                'error': str(e),
                'corruption_detected': True,
                'severity': 'unknown'
            }
    
    def get_validation_statistics(self, theme_directory: str) -> Dict[str, Any]:
        """
        Get validation statistics for all theme files in a directory.
        
        Args:
            theme_directory: Directory containing theme files
            
        Returns:
            Dictionary with validation statistics
        """
        try:
            stats = {
                'total_files': 0,
                'valid_files': 0,
                'corrupted_files': 0,
                'corruption_types': {},
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            if not os.path.exists(theme_directory):
                stats['error'] = 'Theme directory not found'
                return stats
            
            # Scan theme files
            theme_files = []
            for root, dirs, files in os.walk(theme_directory):
                for file in files:
                    if file.endswith(('.json', '.secure')):
                        theme_files.append(os.path.join(root, file))
            
            stats['total_files'] = len(theme_files)
            
            for file_path in theme_files:
                validation_result = self.validate_theme_file(file_path)
                
                if validation_result.valid:
                    stats['valid_files'] += 1
                else:
                    stats['corrupted_files'] += 1
                    corruption_type = validation_result.corruption_type
                    if corruption_type in stats['corruption_types']:
                        stats['corruption_types'][corruption_type] += 1
                    else:
                        stats['corruption_types'][corruption_type] = 1
            
            # Calculate percentages
            if stats['total_files'] > 0:
                stats['corruption_rate'] = (
                    stats['corrupted_files'] / stats['total_files']
                )
                stats['health_score'] = (
                    stats['valid_files'] / stats['total_files']
                )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get validation statistics: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }