"""
PII Detector for RFU Hub

Detects Personally Identifiable Information in directory paths
and assigns appropriate sensitivity levels.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import re
import logging
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class PIIAnalysisResult:
    """Result of PII analysis operation"""
    contains_pii: bool
    sensitivity_level: int
    pii_indicators: List[str]
    anonymized_path: str
    requires_encryption: bool


class PIIDetector:
    """
    Detects Personally Identifiable Information in directory paths
    and assigns appropriate sensitivity levels.
    """
    
    def __init__(self):
        """Initialize PIIDetector"""
        self.pii_patterns = self._load_pii_patterns()
        self.sensitivity_rules = self._load_sensitivity_rules()
        self.logger = logging.getLogger('RFU.PIIDetector')
        
        self.logger.info("PIIDetector initialized successfully")
    
    def analyze_directory_path(self, directory_path: str) -> PIIAnalysisResult:
        """
        Analyze directory path for PII content and sensitivity
        
        Args:
            directory_path: Directory path to analyze
            
        Returns:
            PIIAnalysisResult with PII detection and sensitivity information
        """
        try:
            if not directory_path:
                return PIIAnalysisResult(
                    contains_pii=False,
                    sensitivity_level=1,
                    pii_indicators=[],
                    anonymized_path="",
                    requires_encryption=False
                )
            
            # Normalize path for analysis
            normalized_path = directory_path.lower().replace('\\', '/')
            
            # Check for PII patterns
            pii_indicators = []
            for pattern_name, pattern_regex in self.pii_patterns.items():
                if re.search(pattern_regex, normalized_path):
                    pii_indicators.append(pattern_name)
            
            # Calculate sensitivity level
            sensitivity_level = self._calculate_sensitivity_level(
                pii_indicators, normalized_path
            )
            
            # Determine if path contains PII
            contains_pii = len(pii_indicators) > 0 or sensitivity_level >= 3
            
            # Generate anonymized version for logging
            anonymized_path = self._create_anonymized_path(
                directory_path, pii_indicators
            )
            
            # Determine if encryption is required
            requires_encryption = sensitivity_level >= 3
            
            self.logger.debug(
                f"PII analysis complete: sensitivity={sensitivity_level}, "
                f"indicators={len(pii_indicators)}"
            )
            
            return PIIAnalysisResult(
                contains_pii=contains_pii,
                sensitivity_level=sensitivity_level,
                pii_indicators=pii_indicators,
                anonymized_path=anonymized_path,
                requires_encryption=requires_encryption
            )
            
        except Exception as e:
            self.logger.error(f"PII analysis failed: {e}")
            # Err on the side of caution
            return PIIAnalysisResult(
                contains_pii=True,
                sensitivity_level=5,
                pii_indicators=['analysis_error'],
                anonymized_path='***ERROR***',
                requires_encryption=True
            )
    
    def get_pii_warnings(self, directory_path: str) -> List[str]:
        """
        Get human-readable PII warnings for a directory path
        
        Args:
            directory_path: Directory path to analyze
            
        Returns:
            List of warning messages
        """
        try:
            analysis = self.analyze_directory_path(directory_path)
            warnings = []
            
            if not analysis.contains_pii:
                return warnings
            
            # Generate specific warnings based on indicators
            indicator_warnings = {
                'username_directory': 
                    "Path contains user directory information",
                'personal_documents': 
                    "Path may contain personal documents",
                'desktop_directory': 
                    "Path accesses user desktop directory",
                'downloads_directory': 
                    "Path accesses user downloads directory",
                'pictures_directory': 
                    "Path may contain personal photos/images",
                'videos_directory': 
                    "Path may contain personal videos",
                'music_directory': 
                    "Path may contain personal music files",
                'email_directory': 
                    "Path may contain email data (HIGH SENSITIVITY)",
                'browser_data': 
                    "Path may contain browser data and history",
                'social_security': 
                    "Path may contain social security information (CRITICAL)",
                'financial_data': 
                    "Path may contain financial information (CRITICAL)",
                'medical_records': 
                    "Path may contain medical records (CRITICAL)",
                'legal_documents': 
                    "Path may contain legal documents",
                'private_keys': 
                    "Path may contain private keys/certificates (CRITICAL)",
                'backup_data': 
                    "Path may contain backup/archive data",
                'cloud_sync': 
                    "Path may contain cloud synchronized data",
            }
            
            for indicator in analysis.pii_indicators:
                if indicator in indicator_warnings:
                    warnings.append(indicator_warnings[indicator])
            
            # Add general sensitivity warning
            if analysis.sensitivity_level >= 5:
                warnings.append("CRITICAL: Extremely sensitive data detected")
            elif analysis.sensitivity_level >= 4:
                warnings.append("HIGH: Highly sensitive data detected")
            elif analysis.sensitivity_level >= 3:
                warnings.append("MEDIUM: Moderately sensitive data detected")
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"Warning generation failed: {e}")
            return ["ERROR: Unable to analyze path for PII content"]
    
    def _load_pii_patterns(self) -> Dict[str, str]:
        """Load PII detection patterns"""
        return {
            'username_directory': r'/(?:users?|home)/([^/]+)/',
            'personal_documents': r'/(?:documents?|my documents?|personal)/',
            'desktop_directory': r'/desktop/',
            'downloads_directory': r'/downloads?/',
            'pictures_directory': r'/(?:pictures?|photos?|images?)/',
            'videos_directory': r'/(?:videos?|movies?)/',
            'music_directory': r'/(?:music|audio)/',
            'email_directory': r'/(?:mail|email|outlook|thunderbird)/',
            'browser_data': r'/(?:chrome|firefox|safari|edge|browser)/',
            'social_security': r'/(?:ssn|social.?security)/',
            'financial_data': r'/(?:bank|finance|tax|irs|financial)/',
            'medical_records': r'/(?:medical|health|doctor|hospital)/',
            'legal_documents': r'/(?:legal|lawyer|attorney|court)/',
            'private_keys': r'/(?:\.ssh|\.gnupg|keys?|certificates?)/',
            'backup_data': r'/(?:backup|restore|archive)/',
            'cloud_sync': r'/(?:dropbox|onedrive|google.?drive|icloud)/',
            'sensitive_names': r'/(?:private|confidential|secret|personal)/',
            'id_numbers': r'/(?:ssn|license|passport|id)/',
            'financial_apps': r'/(?:quickbooks|mint|turbo.?tax)/',
            'password_files': r'/(?:password|passwd|keychain)/',
        }
    
    def _load_sensitivity_rules(self) -> Dict[str, int]:
        """Load sensitivity level rules (1-5 scale)"""
        return {
            'username_directory': 2,
            'personal_documents': 4,
            'desktop_directory': 3,
            'downloads_directory': 2,
            'pictures_directory': 3,
            'videos_directory': 3,
            'music_directory': 2,
            'email_directory': 5,
            'browser_data': 4,
            'social_security': 5,
            'financial_data': 5,
            'medical_records': 5,
            'legal_documents': 4,
            'private_keys': 5,
            'backup_data': 3,
            'cloud_sync': 3,
            'sensitive_names': 4,
            'id_numbers': 5,
            'financial_apps': 5,
            'password_files': 5,
        }
    
    def _calculate_sensitivity_level(self, pii_indicators: List[str], 
                                   path: str) -> int:
        """Calculate overall sensitivity level"""
        
        if not pii_indicators:
            return self._calculate_base_sensitivity(path)
        
        # Get maximum sensitivity from indicators
        max_sensitivity = max(
            self.sensitivity_rules.get(indicator, 1) 
            for indicator in pii_indicators
        )
        
        # Increase sensitivity for multiple indicators
        if len(pii_indicators) > 2:
            max_sensitivity = min(5, max_sensitivity + 1)
        
        # Check for additional sensitive patterns in path
        additional_sensitivity = self._calculate_additional_sensitivity(path)
        max_sensitivity = max(max_sensitivity, additional_sensitivity)
        
        return max_sensitivity
    
    def _calculate_base_sensitivity(self, path: str) -> int:
        """Calculate base sensitivity level for paths without PII indicators"""
        
        path_lower = path.lower()
        
        # Check for sensitive keywords
        if any(keyword in path_lower for keyword in 
               ['private', 'confidential', 'secret', 'personal']):
            return 3
        
        # Check for hidden directories (Unix)
        if re.search(r'/\.[^/]+/', path_lower):
            return 2
        
        # Check for very deep paths (might indicate complexity/sensitivity)
        if path_lower.count('/') > 10 or path_lower.count('\\') > 10:
            return 2
        
        return 1  # Low sensitivity
    
    def _calculate_additional_sensitivity(self, path: str) -> int:
        """Calculate additional sensitivity based on path characteristics"""
        
        path_lower = path.lower()
        sensitivity = 1
        
        # Check for encryption-related terms
        crypto_terms = ['crypt', 'encrypt', 'decrypt', 'cipher', 'key']
        if any(term in path_lower for term in crypto_terms):
            sensitivity = max(sensitivity, 4)
        
        # Check for administrative/system terms
        admin_terms = ['admin', 'administrator', 'system', 'config']
        if any(term in path_lower for term in admin_terms):
            sensitivity = max(sensitivity, 3)
        
        # Check for temporary/cache directories (lower sensitivity)
        temp_terms = ['temp', 'tmp', 'cache', 'temporary']
        if any(term in path_lower for term in temp_terms):
            sensitivity = max(sensitivity, 1)  # Keep low
        
        # Check for source code patterns
        code_terms = ['src', 'source', 'code', 'project', 'git']
        if any(term in path_lower for term in code_terms):
            sensitivity = max(sensitivity, 2)
        
        return sensitivity
    
    def _create_anonymized_path(self, directory_path: str, 
                               pii_indicators: List[str]) -> str:
        """Create anonymized version of path for logging"""
        
        if not directory_path:
            return ""
        
        anonymized = directory_path.lower()
        
        # Replace usernames
        anonymized = re.sub(
            r'/(?:users?|home)/[^/]+/', 
            '/[USER]/', 
            anonymized
        )
        anonymized = re.sub(
            r'\\users\\[^\\]+\\', 
            '\\[USER]\\', 
            anonymized, 
            flags=re.IGNORECASE
        )
        
        # Replace other PII patterns based on indicators
        replacements = {
            'personal_documents': (
                r'/(?:documents?|my documents?|personal)/', 
                '/[DOCS]/'
            ),
            'email_directory': (
                r'/(?:mail|email|outlook|thunderbird)/', 
                '/[EMAIL]/'
            ),
            'financial_data': (
                r'/(?:bank|finance|tax|irs|financial)/', 
                '/[FINANCIAL]/'
            ),
            'medical_records': (
                r'/(?:medical|health|doctor|hospital)/', 
                '/[MEDICAL]/'
            ),
            'legal_documents': (
                r'/(?:legal|lawyer|attorney|court)/', 
                '/[LEGAL]/'
            ),
            'private_keys': (
                r'/(?:\.ssh|\.gnupg|keys?|certificates?)/', 
                '/[KEYS]/'
            ),
            'browser_data': (
                r'/(?:chrome|firefox|safari|edge|browser)/', 
                '/[BROWSER]/'
            ),
            'cloud_sync': (
                r'/(?:dropbox|onedrive|google.?drive|icloud)/', 
                '/[CLOUD]/'
            ),
        }
        
        for indicator in pii_indicators:
            if indicator in replacements:
                pattern, replacement = replacements[indicator]
                anonymized = re.sub(pattern, replacement, anonymized)
        
        # Replace any remaining potentially sensitive directory names
        components = anonymized.split('/')
        anonymized_components = []
        
        for component in components:
            if not component:
                anonymized_components.append(component)
                continue
            
            # Long directory names might contain PII
            if len(component) > 20:
                anonymized_components.append('[LONG_NAME]')
            # Numeric names might be IDs
            elif (any(char.isdigit() for char in component) and 
                  len(component) > 8):
                anonymized_components.append('[NUMERIC_NAME]')
            # Hidden directories
            elif component.startswith('.'):
                anonymized_components.append('[HIDDEN]')
            # Keep short, common names
            else:
                anonymized_components.append(component)
        
        return '/'.join(anonymized_components)
    
    def is_path_pii_sensitive(self, directory_path: str) -> bool:
        """
        Quick check if path is PII sensitive
        
        Args:
            directory_path: Directory path to check
            
        Returns:
            True if path is PII sensitive, False otherwise
        """
        try:
            analysis = self.analyze_directory_path(directory_path)
            return analysis.contains_pii
            
        except Exception:
            # Err on the side of caution
            return True
    
    def get_sensitivity_level(self, directory_path: str) -> int:
        """
        Get sensitivity level for directory path
        
        Args:
            directory_path: Directory path to analyze
            
        Returns:
            Sensitivity level (1-5)
        """
        try:
            analysis = self.analyze_directory_path(directory_path)
            return analysis.sensitivity_level
            
        except Exception:
            # Err on the side of caution
            return 5