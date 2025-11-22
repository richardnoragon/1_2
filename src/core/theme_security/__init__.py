"""
Theme Security Framework for RFU Hub

This package provides comprehensive security features for theme data:
- AES-256-GCM encryption for theme storage
- Integrity validation and corruption detection
- Access control and audit logging
- Automatic backup and recovery systems
- Key management with OS keyring integration
"""

try:
    from .theme_security_manager import ThemeSecurityManager
except ImportError:  # Fallback for optional dependencies such as cryptography
    ThemeSecurityManager = None  # type: ignore[assignment]

try:
    from .theme_encryption import ThemeDataEncryption
except ImportError:  # Optional cryptography dependency may be missing
    ThemeDataEncryption = None  # type: ignore[assignment]

try:
    from .theme_validator import ThemeIntegrityValidator
except ImportError:
    ThemeIntegrityValidator = None  # type: ignore[assignment]

try:
    from .theme_access_control import ThemeAccessController
except ImportError:
    ThemeAccessController = None  # type: ignore[assignment]

try:
    from .theme_backup import ThemeBackupManager
except ImportError:
    ThemeBackupManager = None  # type: ignore[assignment]

__all__ = [
    "ThemeSecurityManager",
    "ThemeDataEncryption",
    "ThemeIntegrityValidator",
    "ThemeAccessController",
    "ThemeBackupManager",
]
