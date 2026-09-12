"""Central repository for RFU constants.

This module intentionally avoids importing GUI-only packages at import time so the
startup path stays lightweight and can be used by non-GUI tooling.
"""


_DEFAULT_THEME_TOKENS = {
    "text_primary": "#1f2937",
    "text_secondary": "#495057",
    "button_primary": "#3498db",
    "button_primary_hover": "#2980b9",
    "button_primary_pressed": "#21618c",
    "button_secondary": "#95a5a6",
    "button_secondary_hover": "#7f8c8d",
    "button_secondary_pressed": "#6c7a89",
}


def token(key: str, default: str = "#000000") -> str:
    """Return a lightweight theme token without importing PyQt during startup."""
    return _DEFAULT_THEME_TOKENS.get(key, default)


# Application Identity
_APP_DISPLAY_NAME = "Richard's File Utilities"
APP_NAME = _APP_DISPLAY_NAME
APP_TITLE = _APP_DISPLAY_NAME
APP_VERSION = "3.0.0"
APP_ORGANIZATION = _APP_DISPLAY_NAME

# File Types and Filters
JSON_FILES_FILTER = "JSON Files (*.json);;All Files (*)"
JSON_FILES_FILTER_SIMPLE = "JSON Files (*.json)"
TEXT_FILES_FILTER = "Text Files (*.txt)"
ALL_FILES_FILTER = "All Files (*.*)"

# Error Messages
IMPORT_ERROR = "Import Error"
EXPORT_ERROR = "Export Error"
FILE_NOT_FOUND_ERROR = "File Not Found"
PERMISSION_ERROR = "Permission Error"

# Security Constants
SECURITY_TEST = "Security Test"
SECURITY_STANDARD = "Standard (Recommended)"
SECURITY_HIGH = "High Security"
SECURITY_CUSTOM = "Custom"

# Network and Transfer
NETWORK_TRANSFER = "Network Transfer"
PLEASE_SELECT_COLLECTION = "Please select a collection."
CONNECTION_ERROR = "Connection Error"
TRANSFER_COMPLETE = "Transfer Complete"

# UI Categories
PDF_TOOLS = "PDF Tools"
FILE_TOOLS = "File Tools"
ANALYSIS_TOOLS = "Analysis Tools"
NETWORK_TOOLS = "Network Tools"
PRIVACY_TOOLS = "Privacy Tools"
UTILITIES_TOOLS = "Utilities"
SETTINGS_TOOLS = "Settings"

# Common UI Messages
OPERATION_COMPLETE = "Operation Complete"
OPERATION_FAILED = "Operation Failed"
PROCESSING = "Processing..."
PLEASE_WAIT = "Please wait..."

# CSS/Style Constants
SEGOE_UI_FONT = "Segoe UI"
TITLE_STYLE_COLOR = f"color: {token('text_primary')}; margin-bottom: 5px;"
SUBTITLE_STYLE_COLOR = f"color: {token('text_secondary')}; margin-bottom: 15px;"
DESCRIPTION_STYLE = f"color: {token('text_secondary')}; margin-bottom: 15px; font-size: 10px;"
SECTION_MARGIN_STYLE = f"color: {token('text_primary')}; margin: 10px 0px;"

# Help and Documentation
SUGGESTED_SOLUTIONS_HEADER = "\n🔧 Suggested Solutions:\n"
SUGGESTED_SOLUTIONS_HEADER_PLAIN = "Suggested Solutions"
USER_GUIDE_TITLE = "User Guide"
PREFERENCES_TITLE = "Preferences"
ABOUT_TITLE = "About"

# File Extensions
JSON_EXTENSION = ".json"
TXT_EXTENSION = ".txt"
LOG_EXTENSION = ".log"
BAK_EXTENSION = ".bak"

# Directory Names
BACKUP_DIR = "backups"
TEMP_DIR = "temp"
LOGS_DIR = "logs"
CONFIG_DIR = "config"

# Default Values
DEFAULT_TIMEOUT = 30
DEFAULT_BUFFER_SIZE = 8192
DEFAULT_RETRY_COUNT = 3

# Status Messages
STATUS_READY = "Ready"
STATUS_BUSY = "Busy"
STATUS_ERROR = "Error"
STATUS_SUCCESS = "Success"
