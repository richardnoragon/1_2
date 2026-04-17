"""
src/rfu/ui_strings.py — Centralised UI string constants (P1-C15).

One class per tool + Hub.  Each class exposes TITLE and LOADING.
Phase 3 will populate tool-specific copy; Phase 1 provides skeleton constants.

Usage:
    from src.rfu.ui_strings import Hub
    print(Hub.TITLE)   # -> "RFU Hub"
"""

# ---------------------------------------------------------------------------
# Hub
# ---------------------------------------------------------------------------


class Hub:
    TITLE = "RFU Hub"
    LOADING = "Loading Hub…"


# ---------------------------------------------------------------------------
# File Management tools
# ---------------------------------------------------------------------------


class FileFinder:
    TITLE = "File Finder"
    WINDOW_TITLE = "File Finder — RFU"
    LOADING = "Loading File Finder…"
    MODAL_ERROR_TITLE = "File Finder"
    ERR_INIT_FAILED = (
        "Could not start File Finder. " "Please try again or restart the application."
    )
    ERR_SEARCH_FAILED = (
        "File search could not be completed. "
        "Check that the folder is accessible and try again."
    )
    ERR_OPEN_FAILED = "Could not open the selected file. Check that the file still exists and you have permission to open it."
    ERR_METADATA_FAILED = "Could not load file metadata."


class FileRenamer:
    TITLE = "File Renamer"
    LOADING = "Loading File Renamer…"


class FileCatalog:
    TITLE = "File Catalog"
    LOADING = "Loading File Catalog…"


class FileTagger:
    TITLE = "File Tagger"
    LOADING = "Loading File Tagger…"


class FileVersioning:
    TITLE = "File Versioning"
    LOADING = "Loading File Versioning…"


# ---------------------------------------------------------------------------
# File Operations tools
# ---------------------------------------------------------------------------


class CopyMoveSync:
    TITLE = "Copy / Move / Sync"
    LOADING = "Loading Copy / Move / Sync…"


class BatchFileOperations:
    TITLE = "Batch File Operations"
    LOADING = "Loading Batch File Operations…"


class ArchiveManager:
    TITLE = "Archive Manager"
    LOADING = "Loading Archive Manager…"


class QuickMover:
    TITLE = "Quick Mover"
    LOADING = "Loading Quick Mover…"


# ---------------------------------------------------------------------------
# Analysis tools
# ---------------------------------------------------------------------------


class SizeAnalyzer:
    TITLE = "Size Analyzer"
    WINDOW_TITLE = "Size Analyzer — RFU"
    LOADING = "Loading Size Analyzer…"
    MODAL_ERROR_TITLE = "Size Analyzer"
    ERR_INIT_FAILED = (
        "Could not start Size Analyzer. " "Please try again or restart the application."
    )
    ERR_ANALYSIS_FAILED = (
        "Size analysis could not be completed. "
        "Check that the folder is accessible and try again."
    )
    ERR_FILTER_INVALID = (
        "Invalid name filter. "
        "Please enter a valid file name pattern or leave the filter empty."
    )
    ERR_EXPORT_FAILED = (
        "Could not export analysis results. "
        "Check that you have write permission to the chosen location."
    )


class DuplicateFinder:
    TITLE = "Duplicate Finder"
    WINDOW_TITLE = "Duplicate Finder — RFU"
    LOADING = "Loading Duplicate Finder…"
    ERR_INIT_FAILED = (
        "Could not start Duplicate Finder. "
        "Please try again or restart the application."
    )
    ERR_SCAN_FAILED = (
        "Duplicate scan could not be completed. "
        "Check that the folder is accessible and try again."
    )


class FileComparison:
    TITLE = "File Comparison"
    LOADING = "Loading File Comparison…"


class StorageReports:
    TITLE = "Storage Reports"
    LOADING = "Loading Storage Reports…"


# ---------------------------------------------------------------------------
# PDF Tools
# ---------------------------------------------------------------------------


class PDFTools:
    TITLE = "PDF Tools"
    LOADING = "Loading PDF Tools…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


class PDFEditor:
    TITLE = "PDF Editor"
    LOADING = "Loading PDF Editor…"


class PDFConverter:
    TITLE = "PDF Converter"
    LOADING = "Loading PDF Converter…"


class PDFMerger:
    TITLE = "PDF Merger"
    LOADING = "Loading PDF Merger…"


# ---------------------------------------------------------------------------
# Network tools
# ---------------------------------------------------------------------------


class NetworkConnectivity:
    TITLE = "Network Connectivity"
    LOADING = "Loading Network Connectivity…"


class NetworkScanner:
    TITLE = "Network Scanner"
    LOADING = "Loading Network Scanner…"


class BandwidthMonitor:
    TITLE = "Bandwidth Monitor"
    LOADING = "Loading Bandwidth Monitor…"


# ---------------------------------------------------------------------------
# Security tools
# ---------------------------------------------------------------------------


class EncryptDecrypt:
    TITLE = "Encrypt / Decrypt"
    LOADING = "Loading Encrypt / Decrypt…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


class SecureDelete:
    TITLE = "Secure Delete"
    LOADING = "Loading Secure Delete…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


class PermissionsEditor:
    TITLE = "Permissions Editor"
    LOADING = "Loading Permissions Editor…"


class PasswordManager:
    TITLE = "Password Manager"
    LOADING = "Loading Password Manager…"


class HashChecker:
    TITLE = "Hash Checker"
    LOADING = "Loading Hash Checker…"


# ---------------------------------------------------------------------------
# File Management tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class SynchronizationBackup:
    TITLE = "Synchronization & Backup"
    LOADING = "Loading Synchronization & Backup…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    WINDOW_TITLE = "Synchronize - Richard's File Utilities"
    # Labels
    LABEL_NO_DIR_SELECTED = "No directory selected"
    # Status messages
    STATUS_COMPARISON_COMPLETE = "Comparison complete — ready to sync"
    STATUS_SYNC_COMPLETE = "Synchronization complete!"
    STATUS_DRY_RUN_COMPLETE = "Dry run complete — no files were modified"
    # Empty state messages (ERR-6c: actionable)
    EMPTY_STATE_NO_FILES = "No files to display — select a directory first."
    # User-friendly error messages (ERR-4b: clear, actionable, non-technical)
    ERR_CANNOT_READ_DIR = (
        "Could not read the selected directory. "
        "Check that the folder exists and you have permission to access it."
    )
    ERR_CANNOT_COMPARE = (
        "Could not compare the directories. "
        "Check that both folders are accessible and try again."
    )
    ERR_CANNOT_START_SYNC = (
        "Could not start the sync operation. "
        "Check that both directories are accessible and try again."
    )
    ERR_SYNC_FAILED = (
        "Synchronization encountered an error. "
        "Some files may not have been copied. Check the log for details."
    )


class Organizer:
    TITLE = "File Organizer"
    WINDOW_TITLE = "File Organizer — RFU"
    LOADING = "Loading File Organizer…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Error"
    ERR_INIT_FAILED = (
        "Could not start File Organizer. "
        "Please try again or restart the application."
    )
    ERR_ORGANIZE_FAILED = (
        "File organization could not be completed. "
        "Check that the source folder is accessible and try again."
    )
    ERR_SAVE_SETTINGS_FAILED = (
        "Could not save organizer settings. "
        "Check that the destination folder is writable and try again."
    )
    ERR_LOAD_SETTINGS_FAILED = (
        "Could not load organizer settings. "
        "Check that the file is a valid settings file and try again."
    )
    ERR_EXPORT_RESULTS_FAILED = (
        "Could not export results. "
        "Check that you have write permission to the chosen location."
    )
    ERR_PREVIEW_FAILED = (
        "Could not generate a preview. "
        "Make sure the source folder is accessible and try again."
    )
    ERR_READ_DIR_FAILED = (
        "Could not read the source directory. "
        "Check that the folder exists and you have the required permissions."
    )
    ERR_UNDO_FAILED = (
        "Could not undo the last organization. "
        "The files may have already been moved or deleted."
    )


class AdvancedFolders:
    TITLE = "Advanced Folders"
    LOADING = "Loading Advanced Folders…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    WINDOW_TITLE = "Advanced Folders - Richard's File Utilities"
    # Buttons
    BTN_NEW_FOLDER = "📁 New Folder"
    BTN_EDIT_FOLDER = "✏️ Edit"
    BTN_DELETE_FOLDER = "🗑️ Delete"
    BTN_REFRESH = "🔄 Refresh"
    BTN_SEARCH = "🔍 Search"
    BTN_EXPORT = "📤 Export"
    BTN_SETTINGS = "⚙️ Settings"
    # Labels
    LABEL_NO_FOLDER_SELECTED = "No folder selected"
    LABEL_PANEL_TITLE = "Advanced Folders"
    LABEL_RESULTS_TITLE = "Search Results"
    # Empty state messages (ERR-6c: actionable)
    EMPTY_STATE_NO_FOLDER = (
        "No folder selected — choose a folder from the list on the left."
    )
    EMPTY_STATE_NO_RESULTS = "No results found — try adjusting your search filter or select a different folder."
    # Modal titles
    MODAL_ERROR_TITLE = "Error"
    MODAL_VALIDATION_TITLE = "Validation Error"
    MODAL_SETTINGS_TITLE = "Settings"
    # User-friendly error messages (ERR-4b: clear, actionable, non-technical)
    ERR_CREATE_FAILED = (
        "Could not create the folder configuration. "
        "Check that your settings are valid and try again."
    )
    ERR_UPDATE_FAILED = (
        "Could not update the folder configuration. "
        "Check that your settings are valid and try again."
    )
    ERR_DELETE_FAILED = (
        "Could not delete the folder configuration. "
        "Please try again or restart the application."
    )
    ERR_EXPORT_FAILED = (
        "Could not export results. "
        "Check that you have write permission to the chosen location."
    )
    ERR_SEARCH_FAILED = (
        "Search could not be completed. "
        "Check that the configured directories exist and are accessible."
    )
    # Status messages
    STATUS_READY = "Ready"
    STATUS_SEARCHING = "Searching…"
    STATUS_FOLDER_DELETED = "Folder deleted"


# ---------------------------------------------------------------------------
# System tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class SystemCleanup:
    TITLE = "System Cleanup"
    LOADING = "Loading System Cleanup…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    ESTIMATE_LABEL = "Estimate Space to Free"
    PREVIEW_LABEL = "Preview Temp Files Cleanup"
    # Window
    WINDOW_TITLE = "System Cleanup - Richard's File Utilities"
    # Tabs
    TAB_QUICK_CLEANUP = "Quick Cleanup"
    TAB_ADVANCED_TOOLS = "Advanced Tools"
    TAB_SAFETY_BACKUPS = "Safety & Backups"
    TAB_RESULTS_REPORTS = "Results & Reports"
    # Group boxes
    GROUP_QUICK_CLEANUP = "Quick Cleanup"
    GROUP_QUICK_CONTROLS = "Quick Cleanup Controls"
    GROUP_CLEANUP_ESTIMATE = "Cleanup Estimate"
    GROUP_ADDITIONAL_TOOLS = "Additional Cleanup Tools"
    GROUP_TEMP_ADVANCED = "Temporary Files - Advanced Options"
    GROUP_SAFETY_SETTINGS = "Safety Settings"
    GROUP_BACKUP_MGMT = "Backup Management"
    GROUP_SYSTEM_INFO = "System Information"
    GROUP_OP_STATUS = "Current Operation Status"
    GROUP_CLEANUP_RESULTS = "Cleanup Results"
    # Checkboxes
    CHK_TEMP_FILES = "Clean Temporary Files"
    CHK_CACHE = "Clear Application Caches"
    CHK_LOGS = "Clean Windows Logs"
    CHK_TEMP_SYSTEM = "Include system temp directories"
    CHK_TEMP_BACKUP = "Create backup before deletion"
    CHK_TEMP_SECURE = "Secure deletion (overwrite data)"
    CHK_RESTORE_POINT = "Create system restore point before cleanup"
    CHK_BACKUP_FILES = "Backup important files before deletion"
    CHK_CONFIRM_OPS = "Show confirmation dialogs for destructive operations"
    # Buttons
    BTN_RUN_QUICK_CLEANUP = "Run Quick Cleanup"
    BTN_EXECUTE_TEMP_CLEANUP = "Execute Temp Files Cleanup"
    BTN_VIEW_BACKUPS = "View Backups"
    BTN_CLEANUP_OLD_BACKUPS = "Cleanup Old Backups"
    BTN_RESTORE_ALL_BACKUPS = "Restore All Backups"
    BTN_STOP_OPERATION = "Stop Current Operation"
    BTN_EXPORT_RESULTS = "Export Results Report"
    # Labels
    LABEL_AGE_FILTER = "Delete files older than (days):"
    LABEL_SIZE_FILTER = "Minimum file size (MB):"
    LABEL_BACKUP_LOCATION = "Backup Location:"
    LABEL_BACKUP_NOT_INITIALIZED = "Not initialized"
    LABEL_TOOLS_UNAVAILABLE = "Advanced Tools are temporarily unavailable."
    LABEL_SAFETY_UNAVAILABLE = "Safety & Backup settings are temporarily unavailable."
    LABEL_NO_OPERATION = "No cleanup operation in progress"
    LABEL_ADDITIONAL_TOOLS_COMING = (
        "Additional cleanup tools will be available in future updates:"
    )
    LABEL_TOOLS_LIST = "• Registry Cleaner\n• Cache Cleaner\n• Log Files Cleaner\n• Restore Points Manager\n• Memory Dumps Cleaner"
    # Static text content
    TEXT_ESTIMATE_PROMPT = (
        "Click 'Estimate Space to Free' to see potential cleanup results."
    )
    TEXT_NO_RESULTS = "No cleanup operations performed yet.\n\nSelect a cleanup operation from the Quick Cleanup or Advanced Tools tabs to begin."
    # Loading indicator
    LOADING_INDICATOR_MSG = "Cleanup in progress..."
    # Status messages
    STATUS_UNABLE_TO_START = "Unable to start cleanup. Please try again."
    STATUS_CLEANUP_COMPLETED = "Cleanup completed"
    STATUS_CLEANUP_FAILED = "Cleanup failed"
    STATUS_ESTIMATING = "Estimating cleanup size\u2026"
    STATUS_ESTIMATE_ERROR = "Unable to estimate cleanup size. Please try again."
    STATUS_ESTIMATE_DISPLAY_ERROR = (
        "Unable to display estimate results. Please try again."
    )
    # Modal — informational
    MODAL_NO_TOOLS_TITLE = "No Tools Selected"
    MODAL_NO_TOOLS_MSG = "Please select at least one cleanup option to proceed."
    MODAL_TOOL_NA_TITLE = "Tool Not Available"
    MODAL_TOOL_NA_MSG = "Temporary files cleanup tool is not available."
    MODAL_PREVIEW_ERR_TITLE = "Preview Error"
    MODAL_PREVIEW_ERR_MSG = "Unable to generate preview. Please try again."
    MODAL_PREVIEW_DISPLAY_ERR_MSG = "Unable to display preview. Please try again."
    MODAL_QUICK_ERR_TITLE = "Quick Cleanup Error"
    MODAL_QUICK_ERR_MSG = "Quick cleanup could not be started. Please try again or check the application logs."
    MODAL_CLEANUP_ERR_TITLE = "Cleanup Error"
    MODAL_CLEANUP_ERR_MSG_START = (
        "Failed to start the cleanup operation. Please try again."
    )
    MODAL_CLEANUP_ERR_MSG_WORKER = (
        "Cleanup failed. Please try again or check the application logs."
    )
    MODAL_CLEANUP_ERR_MSG_UNABLE = (
        "Unable to start cleanup. Please try again or check the application logs."
    )
    MODAL_CLEANUP_COMPLETE_TITLE = "Cleanup Complete"
    MODAL_CLEANUP_WARNING_TITLE = "Cleanup Warning"
    MODAL_OP_IN_PROGRESS_TITLE = "Operation In Progress"
    MODAL_OP_IN_PROGRESS_MSG = "Another cleanup operation is currently running. Please wait for it to complete."
    MODAL_EXPORT_TITLE = "Export Results"
    MODAL_EXPORT_MSG = "Export functionality will be available in a future update.\n\nYou can select and copy the results text manually."
    MODAL_BACKUPS_NA_TITLE = "Backups Unavailable"
    MODAL_BACKUPS_NO_DIR_MSG = (
        "Safety manager is not initialised; no backup directory available."
    )
    MODAL_BACKUPS_NA_MSG = "Safety manager is not initialised."
    MODAL_BACKUPS_RESTORE_NA_MSG = (
        "Safety manager is not initialised; cannot restore backups."
    )
    MODAL_CANT_OPEN_DIR_TITLE = "Cannot Open Directory"
    MODAL_CANT_OPEN_DIR_MSG = (
        "Unable to open the backup directory. Please check the path and try again."
    )
    MODAL_BACKUPS_CLEANED_TITLE = "Backups Cleaned"
    MODAL_BACKUPS_CLEANED_MSG = "Old backups removed successfully."
    MODAL_BACKUPS_FAILED_TITLE = "Cleanup Failed"
    MODAL_BACKUPS_FAILED_MSG = "Failed to remove old backups."
    MODAL_RESTORE_COMPLETE_TITLE = "Restore Complete"
    MODAL_RESTORE_COMPLETE_MSG = "All backups restored successfully."
    MODAL_RESTORE_FAILED_TITLE = "Restore Failed"
    MODAL_RESTORE_FAILED_MSG = "Failed to restore all backups."
    # ConfirmationModal strings
    CONFIRM_BACKUP_CLEANUP_TITLE = "Confirm Backup Cleanup"
    CONFIRM_BACKUP_CLEANUP_MSG = (
        "Delete all backups older than 7 days? This cannot be undone."
    )
    CONFIRM_BACKUP_CLEANUP_YES = "Delete Backups"
    CONFIRM_RESTORE_ALL_TITLE = "Restore All Backups"
    CONFIRM_RESTORE_ALL_MSG = "Restore ALL session backups? This will overwrite current files and cannot be undone."
    CONFIRM_RESTORE_ALL_YES = "Restore"
    CONFIRM_QUICK_CLEANUP_TITLE = "Confirm Quick Cleanup"
    CONFIRM_TEMP_CLEANUP_TITLE = "Confirm Temp Files Cleanup"
    CONFIRM_TEMP_CLEANUP_MSG = "Are you sure you want to clean temporary files?\n\nThis operation may delete files permanently."
    CONFIRM_YES = "Yes"
    CONFIRM_CANCEL = "Cancel"


class SoftwareMaintenance:
    TITLE = "Software Maintenance"
    WINDOW_TITLE = "Software Maintenance — RFU"
    LOADING = "Loading Software Maintenance…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Software Maintenance"
    ERR_INIT_FAILED = (
        "Could not start Software Maintenance. "
        "Please try again or restart the application."
    )
    ERR_SCAN_FAILED = "Software scan could not be completed. Please try again."
    ERR_EXPORT_FAILED = (
        "Could not export. Check that you have write permission to the destination."
    )
    ERR_IMPORT_FAILED = "Could not import. Check that the file is valid and accessible."


# ---------------------------------------------------------------------------
# Network tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class NetworkTools:
    TITLE = "Network Tools"
    WINDOW_TITLE = "Network Tools — RFU"
    LOADING = "Loading Network Tools…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Network Error"
    ERR_INIT_FAILED = (
        "Could not start Network Tools. " "Please try again or restart the application."
    )
    ERR_OPERATION_FAILED = (
        "Network operation could not be completed. "
        "Check your network connection and try again."
    )
    ERR_PORT_INVALID = (
        "Invalid port format. "
        "Please enter comma-separated port numbers (e.g., 80, 443, 8080)."
    )
    ERR_EXPORT_FAILED = (
        "Could not export results. "
        "Check that you have write permission to the chosen location."
    )
    ERR_NO_TARGET = (
        "Please enter a target hostname or IP address before starting a scan."
    )


# ---------------------------------------------------------------------------
# File Operations tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class FileOperations:
    TITLE = "File Operations"
    WINDOW_TITLE = "File Operations — RFU"
    LOADING = "Loading File Operations…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    HEADER = "File Operations"
    DESC = "Tools for file manipulation, splitting, copying, and synchronization"
    ERR_INIT_FAILED = "Could not open the File Operations tools. Please try again."


class Logs:
    TITLE = "Logs"
    WINDOW_TITLE = "Application Logs — RFU"
    LOADING = "Loading Logs…"
    HEADER = "Application Logs"
    DESC = "Real-time application logs and system monitoring"
    BTN_REFRESH = "🔄 Refresh Logs"
    BTN_CLEAR = "🗑️ Clear Display"
    BTN_EXPORT = "💾 Export Logs"
    ERR_LOAD_FAILED = "Could not load log file."
    ERR_EXPORT_FAILED = "Could not export logs."


class FileSplitter:
    TITLE = "File Splitter"
    WINDOW_TITLE = "File Splitter — RFU"
    LOADING = "Loading File Splitter…"
    ERR_INIT_FAILED = (
        "Could not start File Splitter. " "Please try again or restart the application."
    )


class BatchRename:
    TITLE = "Batch Rename"
    WINDOW_TITLE = "Batch Rename — RFU"
    LOADING = "Loading Batch Rename…"
    ERR_INIT_FAILED = (
        "Could not start Batch Rename. " "Please try again or restart the application."
    )


class CompressionTools:
    TITLE = "Compression Tools"
    WINDOW_TITLE = "Compression Tools — RFU"
    LOADING = "Loading Compression Tools…"
    ERR_INIT_FAILED = (
        "Could not start Compression Tools. "
        "Please try again or restart the application."
    )


# ---------------------------------------------------------------------------
# Privacy tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class Privacy:
    TITLE = "Privacy Tools"
    LOADING = "Loading Privacy Tools…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


# ---------------------------------------------------------------------------
# Tier 2 tools — added during Phase 3 harmonization
# ---------------------------------------------------------------------------


class Checksum:
    TITLE = "Checksum Calculator"
    WINDOW_TITLE = "Checksum Calculator — RFU"
    LOADING = "Loading Checksum Calculator…"
    ERR_INIT_FAILED = (
        "Could not start Checksum Calculator. "
        "Please try again or restart the application."
    )
    ERR_CALCULATE_FAILED = (
        "Checksum calculation failed. "
        "Check that the file is accessible and try again."
    )


class EmptyFolders:
    TITLE = "Empty Folders Finder"
    WINDOW_TITLE = "Empty Folders Finder — RFU"
    LOADING = "Loading Empty Folders Finder…"
    ERR_INIT_FAILED = (
        "Could not start Empty Folders Finder. "
        "Please try again or restart the application."
    )
    ERR_SCAN_FAILED = (
        "Empty folders scan could not be completed. "
        "Check that the directory is accessible and try again."
    )
    ERR_DELETE_FAILED = (
        "Could not delete the selected folders. " "Check permissions and try again."
    )


class AdvancedCatalog:
    TITLE = "Advanced File Catalog"
    WINDOW_TITLE = "Advanced File Catalog — RFU"
    LOADING = "Loading Advanced File Catalog…"
    ERR_INIT_FAILED = (
        "Could not start Advanced File Catalog. "
        "Please try again or restart the application."
    )
    ERR_SCAN_FAILED = (
        "Catalog scan could not be completed. "
        "Check that the directory is accessible and try again."
    )
    ERR_EXPORT_FAILED = (
        "Catalog export could not be completed. "
        "Check that you have write permission to the destination."
    )


class SystemDiagnostics:
    TITLE = "System Diagnostics"
    WINDOW_TITLE = "System Diagnostics — RFU"
    LOADING = "Loading System Diagnostics…"
    ERR_INIT_FAILED = (
        "Could not start System Diagnostics. "
        "Please try again or restart the application."
    )
    ERR_GATHER_FAILED = "Could not gather system information. Please try again."


class ProcessMonitor:
    TITLE = "Process Monitor"
    WINDOW_TITLE = "Process Monitor — RFU"
    LOADING = "Loading Process Monitor…"
    ERR_INIT_FAILED = (
        "Could not start Process Monitor. "
        "Please try again or restart the application."
    )
    ERR_REFRESH_FAILED = (
        "Could not retrieve process list. "
        "Some processes may require administrator access."
    )


class SystemInfo:
    TITLE = "System Information"
    WINDOW_TITLE = "System Information — RFU"
    LOADING = "Loading System Information…"
    MODAL_ERROR_TITLE = "System Information"
    ERR_INIT_FAILED = (
        "Could not start System Information. "
        "Please try again or restart the application."
    )
    ERR_GATHER_FAILED = "Could not gather system information. Please try again."
    ERR_EXPORT_FAILED = "Could not export system information. Check that you have write permission to the destination."


class PreferencePortability:
    TITLE = "Preference Portability"
    WINDOW_TITLE = "Preference Portability — RFU"
    LOADING = "Loading Preference Portability…"
    MODAL_ERROR_TITLE = "Preference Portability"
    ERR_INIT_FAILED = (
        "Could not start Preference Portability. "
        "Please try again or restart the application."
    )
    ERR_EXPORT_FAILED = (
        "Preference export failed. "
        "Check that you have write permission to the destination."
    )
    ERR_IMPORT_FAILED = (
        "Preference import failed. "
        "Check that the source file is valid and accessible."
    )


class ImageMetadata:
    TITLE = "Image Metadata Editor"
    WINDOW_TITLE = "Image Metadata Editor — RFU"
    LOADING = "Loading Image Metadata Editor…"
    MODAL_ERROR_TITLE = "Image Metadata Editor"
    ERR_INIT_FAILED = (
        "Could not start Image Metadata Editor. "
        "Please try again or restart the application."
    )
    ERR_LOAD_FAILED = (
        "Failed to load image metadata. "
        "Check that the file is a supported image format."
    )
    ERR_SAVE_FAILED = (
        "Failed to save image metadata. "
        "Check that you have write permission to the file."
    )


class OfficeMetadata:
    TITLE = "Office Metadata Tools"
    WINDOW_TITLE = "Office Metadata Tools — RFU"
    LOADING = "Loading Office Metadata Tools…"
    ERR_INIT_FAILED = (
        "Could not start Office Metadata Tools. "
        "Please try again or restart the application."
    )
    ERR_LOAD_FAILED = (
        "Failed to load office document metadata. "
        "Check that the file is a supported office format."
    )
    ERR_SAVE_FAILED = (
        "Failed to save office document metadata. "
        "Check that you have write permission to the file."
    )


class FileTouch:
    TITLE = "File Touch"
    WINDOW_TITLE = "File Touch — RFU"
    LOADING = "Loading File Touch…"
    MODAL_ERROR_TITLE = "File Touch"
    ERR_INIT_FAILED = (
        "Could not start File Touch. " "Please try again or restart the application."
    )
    ERR_FETCH_FAILED = (
        "Failed to fetch file timestamps. "
        "Check that the file exists and is accessible."
    )
    ERR_APPLY_FAILED = (
        "Failed to apply timestamp changes. "
        "Check that you have write permission to the file."
    )


class SecureDelete:
    TITLE = "Secure Delete"
    WINDOW_TITLE = "Secure Delete — RFU"
    LOADING = "Loading Secure Delete…"
    ERR_INIT_FAILED = (
        "Could not start Secure Delete. " "Please try again or restart the application."
    )
    ERR_DELETE_FAILED = (
        "Secure deletion failed. "
        "Check that you have permission to delete the selected files."
    )
    ERR_NO_FILES = "No files selected for deletion."


class Encryption:
    TITLE = "Encrypt / Decrypt"
    WINDOW_TITLE = "Encrypt / Decrypt — RFU"
    LOADING = "Loading Encrypt / Decrypt…"
    ERR_INIT_FAILED = (
        "Could not start Encrypt / Decrypt. "
        "Please try again or restart the application."
    )
    ERR_OPERATION_FAILED = (
        "Encryption/decryption operation failed. "
        "Check your password and file permissions."
    )
    ERR_NO_FILES = "No files selected for the operation."


class SecurityScanner:
    TITLE = "Security Scanner"
    WINDOW_TITLE = "Security Scanner — RFU"
    LOADING = "Loading Security Scanner…"
    ERR_INIT_FAILED = (
        "Could not start Security Scanner. "
        "Please try again or restart the application."
    )
    ERR_SCAN_FAILED = (
        "Security scan failed. "
        "Some scan modules may not be available on this system."
    )


class PasswordGenerator:
    TITLE = "Password Generator"
    WINDOW_TITLE = "Password Generator — RFU"
    LOADING = "Loading Password Generator…"
    ERR_INIT_FAILED = (
        "Could not start Password Generator. "
        "Please try again or restart the application."
    )


class PDFTools:
    TITLE = "PDF Tools"
    WINDOW_TITLE = "PDF Tools — RFU"
    LOADING = "Loading PDF Tools…"
    ERR_INIT_FAILED = (
        "Could not start PDF Tools. " "Please try again or restart the application."
    )
    ERR_NO_FILE = "No PDF file selected."
    ERR_LOAD_FAILED = "Failed to load the selected PDF file."


class Privacy:
    TITLE = "Privacy Tools"
    WINDOW_TITLE = "Privacy Tools — RFU"
    LOADING = "Loading Privacy Tools…"
    MODAL_ERROR_TITLE = "Privacy Tools"
    ERR_INIT_FAILED = (
        "Could not start Privacy Tools. " "Please try again or restart the application."
    )
    ERR_CLEAN_FAILED = (
        "Privacy clean operation failed. "
        "Check that you have the required permissions."
    )
    ERR_PREVIEW_FAILED = (
        "Could not preview the operation. "
        "Check that you have the required permissions."
    )


class SecureDelete:
    TITLE = "Secure Delete"
    WINDOW_TITLE = "Secure Delete — RFU"
    LOADING = "Loading Secure Delete…"
    ERR_INIT_FAILED = (
        "Could not start Secure Delete. " "Please try again or restart the application."
    )
    ERR_DELETE_FAILED = (
        "Secure deletion failed. "
        "Check that you have permission to delete the selected files."
    )
    ERR_NO_FILES = "No files selected for deletion."


class Encryption:
    TITLE = "Encrypt / Decrypt"
    WINDOW_TITLE = "Encrypt / Decrypt — RFU"
    LOADING = "Loading Encrypt / Decrypt…"
    ERR_INIT_FAILED = (
        "Could not start Encrypt / Decrypt. "
        "Please try again or restart the application."
    )
    ERR_OPERATION_FAILED = (
        "Encryption/decryption operation failed. "
        "Check your password and file permissions."
    )
    ERR_NO_FILES = "No files selected for the operation."


class SecurityScanner:
    TITLE = "Security Scanner"
    WINDOW_TITLE = "Security Scanner — RFU"
    LOADING = "Loading Security Scanner…"
    ERR_INIT_FAILED = (
        "Could not start Security Scanner. "
        "Please try again or restart the application."
    )
    ERR_SCAN_FAILED = (
        "Security scan failed. "
        "Some scan modules may not be available on this system."
    )


class PasswordGenerator:
    TITLE = "Password Generator"
    WINDOW_TITLE = "Password Generator — RFU"
    LOADING = "Loading Password Generator…"
    ERR_INIT_FAILED = (
        "Could not start Password Generator. "
        "Please try again or restart the application."
    )


class PDFTools:
    TITLE = "PDF Tools"
    WINDOW_TITLE = "PDF Tools — RFU"
    LOADING = "Loading PDF Tools…"
    ERR_INIT_FAILED = (
        "Could not start PDF Tools. " "Please try again or restart the application."
    )
    ERR_NO_FILE = "No PDF file selected."
    ERR_LOAD_FAILED = "Failed to load the selected PDF file."


class Privacy:
    TITLE = "Privacy Tools"
    WINDOW_TITLE = "Privacy Tools — RFU"
    LOADING = "Loading Privacy Tools…"
    MODAL_ERROR_TITLE = "Privacy Tools"
    ERR_INIT_FAILED = (
        "Could not start Privacy Tools. " "Please try again or restart the application."
    )
    ERR_CLEAN_FAILED = (
        "Privacy clean operation failed. "
        "Check that you have the required permissions."
    )
    ERR_PREVIEW_FAILED = (
        "Could not preview the operation. "
        "Check that you have the required permissions."
    )
