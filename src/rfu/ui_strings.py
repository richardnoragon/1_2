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

# ---------------------------------------------------------------------------
# Phase 2 — Menu token additions (resolves TODO(UI_STRINGS_MENU_TOKENS))
# Compliant with §7.4 nomenclature: imperative verbs, Title Case, ellipsis
# only when a dialog follows.
# ---------------------------------------------------------------------------


class Menu:
    FILE = "&File"
    EDIT = "&Edit"
    VIEW = "&View"
    TOOLS = "&Tools"
    REPORTS = "&Reports"
    WINDOW = "&Window"
    HELP = "&Help"
    RETURN_TO_HUB = "Return to &Hub"
    LOAD_PLUGIN = "Load Local Plu&gin…"
    PLUGIN_FILTER = "Plugin manifests (*.json)"
    PLUGIN_ERROR = "The plugin could not be loaded. Check its manifest and installed Python package."
    REOPEN = "Reopen {tool}"
    OPEN_WINDOWS = "&Open Windows"
    UNAVAILABLE = "Tool &Unavailable"
    CAPABILITIES = "Tool Capa&bilities…"

    """Shared hub-level menu item tokens (§9.6 Hub-Specific Menu Items)."""

    # File menu — hub-provided items (§9.6, §9.7.1)
    FILE_RETURN_TO_HUB = "Return to Hub"
    FILE_EXIT = "Exit"

    # Edit menu — globally reserved (§7.4.4)
    EDIT_UNDO = "Undo"
    EDIT_REDO = "Redo"
    EDIT_CUT = "Cut"
    EDIT_COPY = "Copy"
    EDIT_PASTE = "Paste"
    EDIT_SELECT_ALL = "Select All"
    EDIT_FIND = "Find\u2026"
    EDIT_REPLACE = "Find and Replace\u2026"

    # View menu — hub items (§9.6)
    VIEW_SHOW_HUB_TABS = "Show Hub Tabs"
    VIEW_SHOW_TOOL_LIST = "Show Tool List"
    VIEW_RESET_LAYOUT = "Reset Layout"
    VIEW_ZOOM_IN = "Zoom In"
    VIEW_ZOOM_OUT = "Zoom Out"
    VIEW_RESET_ZOOM = "Reset Zoom"

    # Tools menu — hub items (§9.6)
    TOOLS_PREFERENCES = "Preferences"
    TOOLS_RELOAD_REGISTRY = "Reload Tool Registry"
    TOOLS_RUN_DIAGNOSTICS = "Run Diagnostics\u2026"

    # Window menu — hub items (§9.6)
    WINDOW_HUB_HOME = "Hub Home"
    WINDOW_OPEN_TOOL = "Open Tool Window\u2026"
    WINDOW_SWITCH_PREVIOUS = "Switch to Previous Tool"
    WINDOW_REOPEN_TOOL = "Reopen {tool_name}"  # Formatted at runtime

    # Help menu — hub items (§9.6)
    HELP_DOCUMENTATION = "Hub Documentation"
    HELP_KEYBOARD_SHORTCUTS = "Keyboard Shortcuts"
    HELP_ABOUT = "About"
    HELP_DIAGNOSTICS = "Diagnostics\u2026"
    HELP_CHECK_UPDATES = "Check for Updates\u2026"

    # Shared action labels (§7.4.4 / §8.3 command taxonomy)
    ACTION_DRY_RUN = "Dry Run (Preview Only)"
    ACTION_CANCEL = "Cancel"
    ACTION_CLOSE = "Close"
    ACTION_APPLY = "Apply Changes"
    ACTION_PREVIEW = "Preview"
    ACTION_EXPORT = "Export\u2026"
    ACTION_IMPORT = "Import\u2026"
    ACTION_REFRESH = "Refresh"
    ACTION_SETTINGS = "Settings\u2026"
    ACTION_RESET_DEFAULTS = "Reset to Defaults\u2026"

    # Shared confirmation strings
    CONFIRM_YES = "Yes"
    CONFIRM_NO = "No"
    CONFIRM_CANCEL = "Cancel"
    CONFIRM_DESTRUCTIVE_TITLE = "Confirm Operation"
    CONFIRM_DESTRUCTIVE_MSG = (
        "This action cannot be undone. "
        "Do you want to proceed?"
    )


# ---------------------------------------------------------------------------
# Missing tool classes — Phase 2 additions (canonical names per matrix §12.3)
# ---------------------------------------------------------------------------


class EnhancedEditor:
    """Enhanced text/file editor (matrix id: enhanced-editor)."""

    TITLE = "Enhanced Editor"
    WINDOW_TITLE = "Enhanced Editor \u2014 RFU"
    LOADING = "Loading Enhanced Editor\u2026"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Enhanced Editor"
    ERR_INIT_FAILED = (
        "Could not start Enhanced Editor. "
        "Please try again or restart the application."
    )
    ERR_OPEN_FAILED = (
        "Could not open the file. "
        "Check that the file exists and you have permission to read it."
    )
    ERR_SAVE_FAILED = (
        "Could not save the file. "
        "Check that you have write permission to the destination."
    )
    ERR_EXPORT_FAILED = (
        "Could not export. "
        "Check that you have write permission to the destination."
    )
    BTN_APPLY = "Apply Changes"
    BTN_EXPORT = "Export\u2026"
    BTN_FIND_REPLACE = "Find and Replace\u2026"
    MENU_TOOLS_APPLY = "Apply Changes"
    MENU_TOOLS_FORMAT = "Advanced Formatting\u2026"
    MENU_REPORTS_EXPORT = "Export Document\u2026"


class SecurityPreferences:
    """Security preferences panel (matrix id: security-preferences)."""

    TITLE = "Security Preferences"
    WINDOW_TITLE = "Security Preferences \u2014 RFU"
    LOADING = "Loading Security Preferences\u2026"
    MODAL_ERROR_TITLE = "Security Preferences"
    ERR_INIT_FAILED = (
        "Could not start Security Preferences. "
        "Please try again or restart the application."
    )
    ERR_SAVE_FAILED = (
        "Could not save security settings. "
        "Please try again or restart the application."
    )
    ERR_RESET_FAILED = (
        "Could not reset security settings. "
        "Please try again or restart the application."
    )
    BTN_APPLY = "Apply Changes"
    BTN_RESET = "Reset to Defaults\u2026"
    BTN_EXPORT = "Export Settings\u2026"
    CONFIRM_RESET_TITLE = "Confirm Reset"
    CONFIRM_RESET_MSG = (
        "Reset all security settings to defaults? This cannot be undone."
    )
    CONFIRM_RESET_YES = "Reset"
    MENU_TOOLS_APPLY = "Apply Changes"
    MENU_TOOLS_RESET = "Reset to Defaults\u2026"


class PDFExtractLinks:
    """PDF link extraction tool (matrix id: pdf-extract-links)."""

    TITLE = "Extract Links"
    WINDOW_TITLE = "Extract Links \u2014 RFU"
    LOADING = "Loading Extract Links\u2026"
    MODAL_ERROR_TITLE = "Extract Links"
    ERR_INIT_FAILED = (
        "Could not start Extract Links. "
        "Please try again or restart the application."
    )
    ERR_NO_FILE = "No PDF file selected. Select a file before extracting links."
    ERR_LOAD_FAILED = (
        "Could not load the PDF file. "
        "Check that the file is a valid PDF and you have permission to read it."
    )
    ERR_EXTRACT_FAILED = (
        "Link extraction failed. "
        "The file may be encrypted or contain no extractable links."
    )
    ERR_EXPORT_FAILED = (
        "Could not export results. "
        "Check that you have write permission to the destination."
    )
    BTN_EXTRACT = "Extract\u2026"
    BTN_EXPORT = "Export Report\u2026"
    BTN_FILTER = "Filter Options\u2026"
    MENU_TOOLS_EXTRACT = "Extract Links\u2026"
    MENU_REPORTS_EXPORT = "Export Link Report\u2026"


class PDFPageAdministration:
    """PDF page management tool (matrix id: pdf-page-administration)."""

    TITLE = "Page Administration"
    WINDOW_TITLE = "Page Administration \u2014 RFU"
    LOADING = "Loading Page Administration\u2026"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Page Administration"
    ERR_INIT_FAILED = (
        "Could not start Page Administration. "
        "Please try again or restart the application."
    )
    ERR_NO_FILE = "No PDF file selected. Select a file before managing pages."
    ERR_LOAD_FAILED = (
        "Could not load the PDF file. "
        "Check that the file is a valid PDF and you have permission to read it."
    )
    ERR_APPLY_FAILED = (
        "Page operation failed. "
        "Check that you have write permission to the destination."
    )
    ERR_REMOVE_FAILED = (
        "Could not remove the selected pages. "
        "The file may be protected or read-only."
    )
    BTN_APPLY = "Apply Changes"
    BTN_DRY_RUN = "Dry Run (Preview Only)"
    BTN_REMOVE_PAGES = "Remove Pages\u2026"
    CONFIRM_REMOVE_TITLE = "Confirm Page Removal"
    CONFIRM_REMOVE_MSG = "Remove the selected pages? This cannot be undone."
    CONFIRM_REMOVE_YES = "Remove Pages"
    MENU_TOOLS_APPLY = "Apply Page Changes"
    MENU_TOOLS_REMOVE = "Remove Pages\u2026"


class NetworkTransfer:
    """Network file transfer tool (matrix id: network-transfer)."""

    TITLE = "Network Transfer"
    WINDOW_TITLE = "Network Transfer \u2014 RFU"
    LOADING = "Loading Network Transfer\u2026"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Network Transfer"
    ERR_INIT_FAILED = (
        "Could not start Network Transfer. "
        "Please try again or restart the application."
    )
    ERR_CONNECT_FAILED = (
        "Could not connect to the remote host. "
        "Check the hostname, port, and your network connection."
    )
    ERR_TRANSFER_FAILED = (
        "Transfer failed. "
        "Check your connection and that you have permission to access the destination."
    )
    ERR_NO_TARGET = (
        "No transfer destination specified. "
        "Enter a hostname or IP address."
    )
    ERR_EXPORT_FAILED = (
        "Could not export transfer log. "
        "Check that you have write permission to the destination."
    )
    BTN_TRANSFER = "Transfer\u2026"
    BTN_DRY_RUN = "Dry Run (Preview Only)"
    BTN_ADVANCED = "Advanced Transfer\u2026"
    MENU_TOOLS_TRANSFER = "Transfer\u2026"


class BookmarkManager:
    """Network/path bookmark manager (matrix id: bookmark-manager)."""

    TITLE = "Bookmark Manager"
    WINDOW_TITLE = "Bookmark Manager \u2014 RFU"
    LOADING = "Loading Bookmark Manager\u2026"
    MODAL_ERROR_TITLE = "Bookmark Manager"
    ERR_INIT_FAILED = (
        "Could not start Bookmark Manager. "
        "Please try again or restart the application."
    )
    ERR_SAVE_FAILED = (
        "Could not save the bookmark. "
        "Check that the application data folder is writable."
    )
    ERR_DELETE_FAILED = (
        "Could not delete the bookmark. "
        "Please try again or restart the application."
    )
    ERR_EXPORT_FAILED = (
        "Could not export bookmarks. "
        "Check that you have write permission to the destination."
    )
    ERR_IMPORT_FAILED = (
        "Could not import bookmarks. "
        "Check that the file is a valid bookmark export."
    )
    BTN_SAVE = "Save"
    BTN_EXPORT = "Export Bookmarks\u2026"
    BTN_IMPORT = "Import Bookmarks\u2026"
    BTN_DELETE = "Delete Bookmark\u2026"
    CONFIRM_DELETE_TITLE = "Confirm Delete"
    CONFIRM_DELETE_MSG = "Delete the selected bookmark? This cannot be undone."
    CONFIRM_DELETE_YES = "Delete"
    MENU_TOOLS_SAVE = "Save Bookmark"
    MENU_TOOLS_IMPORT = "Import Bookmarks\u2026"
    MENU_REPORTS_EXPORT = "Export Bookmarks\u2026"


class PrivacyCleaner:
    """Privacy data cleaner (matrix id: privacy-cleaner)."""

    TITLE = "Privacy Cleaner"
    WINDOW_TITLE = "Privacy Cleaner \u2014 RFU"
    LOADING = "Loading Privacy Cleaner\u2026"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Privacy Cleaner"
    ERR_INIT_FAILED = (
        "Could not start Privacy Cleaner. "
        "Please try again or restart the application."
    )
    ERR_SCAN_FAILED = (
        "Privacy scan failed. "
        "Check that you have the required permissions."
    )
    ERR_CLEAN_FAILED = (
        "Privacy clean operation failed. "
        "Check that you have the required permissions and try again."
    )
    ERR_EXPORT_FAILED = (
        "Could not export results. "
        "Check that you have write permission to the destination."
    )
    BTN_CLEAN = "Clean\u2026"
    BTN_DRY_RUN = "Dry Run (Preview Only)"
    BTN_ADVANCED = "Advanced Targets\u2026"
    CONFIRM_CLEAN_TITLE = "Confirm Privacy Clean"
    CONFIRM_CLEAN_MSG = (
        "Clean the selected privacy data? "
        "Deleted items cannot be recovered."
    )
    CONFIRM_CLEAN_YES = "Clean"
    MENU_TOOLS_CLEAN = "Clean\u2026"
    MENU_TOOLS_DRY_RUN = "Dry Run (Preview Only)"
    MENU_REPORTS_EXPORT = "Export Clean Report\u2026"


class DataAnonymizer:
    """Data anonymization tool (matrix id: data-anonymizer)."""

    TITLE = "Data Anonymizer"
    WINDOW_TITLE = "Data Anonymizer \u2014 RFU"
    LOADING = "Loading Data Anonymizer\u2026"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
    MODAL_ERROR_TITLE = "Data Anonymizer"
    ERR_INIT_FAILED = (
        "Could not start Data Anonymizer. "
        "Please try again or restart the application."
    )
    ERR_LOAD_FAILED = (
        "Could not load the source file. "
        "Check that the file is accessible and in a supported format."
    )
    ERR_APPLY_FAILED = (
        "Anonymization failed. "
        "Check that you have write permission to the destination."
    )
    ERR_EXPORT_FAILED = (
        "Could not export the anonymized file. "
        "Check that you have write permission to the destination."
    )
    BTN_APPLY = "Apply Changes"
    BTN_DRY_RUN = "Dry Run (Preview Only)"
    BTN_RULES = "Anonymization Rules\u2026"
    MENU_TOOLS_APPLY = "Apply Anonymization"
    MENU_TOOLS_RULES = "Anonymization Rules\u2026"
    MENU_REPORTS_EXPORT = "Export Anonymized File\u2026"


class EnhancedClipboard:
    """Enhanced clipboard manager (matrix id: enhanced-clipboard)."""

    TITLE = "Enhanced Clipboard"
    WINDOW_TITLE = "Enhanced Clipboard \u2014 RFU"
    LOADING = "Loading Enhanced Clipboard\u2026"
    MODAL_ERROR_TITLE = "Enhanced Clipboard"
    ERR_INIT_FAILED = (
        "Could not start Enhanced Clipboard. "
        "Please try again or restart the application."
    )
    ERR_PASTE_FAILED = (
        "Could not paste the selected item. "
        "The clipboard content may no longer be available."
    )
    ERR_CLEAR_FAILED = (
        "Could not clear the clipboard history. "
        "Please try again or restart the application."
    )
    ERR_EXPORT_FAILED = (
        "Could not export clipboard history. "
        "Check that you have write permission to the destination."
    )
    BTN_PASTE = "Paste"
    BTN_EXPORT = "Export\u2026"
    BTN_CLEAR_ALL = "Clear All\u2026"
    BTN_HISTORY = "Clipboard History\u2026"
    CONFIRM_CLEAR_TITLE = "Confirm Clear"
    CONFIRM_CLEAR_MSG = "Clear all clipboard history? This cannot be undone."
    CONFIRM_CLEAR_YES = "Clear All"
    MENU_TOOLS_PASTE = "Paste"
    MENU_TOOLS_HISTORY = "Clipboard History\u2026"
    MENU_TOOLS_CLEAR = "Clear All\u2026"
    MENU_REPORTS_EXPORT = "Export Clipboard History\u2026"


class Undo:
    HISTORY = "Undo &History…"
    TITLE = "Undo History"


class Capabilities:
    TITLE = "Tool Capabilities"
    DESCRIPTION = "Capabilities require recorded review evidence. Unverified does not mean unsupported."
    TABLE = "Tool capability matrix"
    HEADERS = "Tool|Source|Dry Run|Critical Engine|Accessibility|Performance|Undo|Health|Last Activity"
    REFRESH = "Refresh"
    VERIFIED = "Verified"
    UNVERIFIED = "Unverified"
    NOT_APPLICABLE = "Not applicable"
    UNKNOWN = "Unknown"
    SUPPORTED = "Supported"
    UNSUPPORTED = "Unsupported"
    PRESENT = "Present"
    MISSING = "Not in source tree"


class Workflow:
    TITLE = "File Inspection Workflow"
    INSTRUCTIONS = "Choose a folder to find files and calculate SHA-256 checksums. Inspection leaves the files unchanged. Export creates a CSV report."
    INSPECT = "Inspect Folder…"
    EXPORT = "Export Report…"
    CLOSE = "Close"
    CHOOSE = "Choose a Folder"
    RUNNING = "Operation in progress…"
    COUNT = "Inspected {count} files"
    COMPLETE = "Inspected {count} files. The report is ready to export."
    EXPORTED = "Report exported."
    INPUT_OVERWRITE = "Choose another destination to avoid overwriting an inspected file."


class MenuLabels:
    """Canonical labels shared by both legacy menu builders."""
    FILE_WORKFLOW = "Inspect Files and &Checksums…"
    LOAD_LOCALE = "Load &Language Pack…"
    LANGUAGE = "&Language"
    ABOUT = '&About'
    ALWAYS_ON_TOP = 'Always on &Top'
    CHECK_FOR_UPDATES = 'Check for &Updates…'
    COPY = '&Copy'
    CUT = 'Cu&t'
    DARK_THEME = '&Dark Theme'
    EDIT = '&Edit'
    EXIT = 'E&xit'
    EXPORT = '&Export…'
    FILE = '&File'
    FIND = '&Find…'
    FONT = '&Font…'
    FULLSCREEN = '&Fullscreen'
    HELP = '&Help'
    IMPORT = '&Import…'
    KEYBOARD_SHORTCUTS = '&Keyboard Shortcuts…'
    LIGHT_THEME = '&Light Theme'
    LOG_VIEWER = '&Log Viewer…'
    NEW_PROJECT = '&New Project…'
    OPEN = '&Open…'
    OPTIONS = '&Options…'
    PASTE = '&Paste'
    PERFORMANCE_MONITOR = '&Performance Monitor…'
    PREFERENCES = 'Pr&eferences…'
    RECENT_FILES = 'Recent &Files'
    REDO = '&Redo'
    REFRESH = '&Refresh'
    REPLACE = '&Replace…'
    REPORT_BUG = '&Report Bug…'
    RESET_PREFERENCES = '&Reset Preferences…'
    RESET_ZOOM = 'Reset &Zoom'
    SAVE = '&Save'
    SAVE_AS = 'Save &As…'
    SELECT_ALL = 'Select &All'
    SYSTEM_INFORMATION = 'System &Information…'
    THEME = '&Theme'
    TOOLS = '&Tools'
    UNDO = '&Undo'
    USER_GUIDE = '&User Guide'
    VIEW = '&View'
    VISIT_WEBSITE = 'Visit &Website'
    WORKING_DIRECTORY = '&Working Directory…'
    ZOOM_IN = 'Zoom &In'
    ZOOM_OUT = 'Zoom &Out'


class DocumentTool:
    OPEN = 'Open file…'
    SAVE = 'Save As…'
    CANCEL = 'Cancel operation'
    BUSY = 'Working…'
    READY = 'Ready.'
    SAVED = 'Export complete. Source files were preserved.'
    FAILED = 'The operation could not be completed. Check the file format and destination.'
    CANCELLED = 'Operation cancelled; no output was committed.'
    PDF_TITLE = 'PDF Page Administration'
    PDF_HELP = 'Open a PDF, select pages, and edit the draft. Save As exports the full draft; Extract exports selected pages. Insert adds all pages from another PDF after the selected page. Undo applies to draft edits.'
    INSERT = 'Insert PDF…'
    UP = 'Move up'
    DOWN = 'Move down'
    ROTATE = 'Rotate 90°'
    DELETE = 'Remove from draft'
    EXTRACT = 'Extract selected…'
    PAGES = 'Pages in output order'
    PREVIEW = 'Page preview'
    PAGE = '{position}: {file}, page {page} (+{rotation}°)'
    ANON_TITLE = 'Data Anonymizer'
    ANON_HELP = 'Choose top-level CSV columns or JSON fields to transform. Nested values are replaced as a whole. Preview up to 100 records (64 KiB of text) before exporting a separate copy. Pseudonyms are consistent within this session; unselected fields may still identify people.'
    FIELDS = 'Field transformations'
    HEADERS = 'Field|Transformation'
    KEEP = 'Keep'
    REDACT = 'Redact'
    PSEUDONYM = 'Pseudonymize'
    PREVIEW_DATA = 'Preview transformations'
    DATA_PREVIEW = 'Transformed records (first 100, up to 64 KiB)'
    PREVIEW_READY = '{count} records transformed. Review the preview before export.'
    SELECT_RULE = 'Select at least one field to redact or pseudonymize.'
    DRAFT_EDIT = 'Edit page draft'
    INSPECT_LINKS = 'Inspect links in exported PDF'
    HANDOFF_FAILED = 'The document could not be handed off. Check that it still exists and the destination tool is ready.'


class ToolCatalogue:
    TITLE = 'Tools'
    SEARCH = 'Search tools by name or category'
    HEADERS = 'Tool|Category'
    OPEN = 'Open selected tool'
    UNAVAILABLE = 'This tool could not start. Check its installed dependencies and try again.'


class PDFLinks:
    TITLE = 'PDF Link Extractor'
    HELP = 'Open a PDF to inspect its link annotations. Export the list to a separate CSV file. The source PDF stays in place; links are never opened automatically.'
    TABLE = 'Extracted PDF links'
    HEADERS = 'Page|URL'
    READY = '{count} links found (preview shows up to 1,000). Choose Save As to export all.'


class StorageMonitor:
    TITLE = 'Storage Monitor'
    DRIVE = 'Drive or network path'
    ADD = 'Add path…'
    PATH = 'Enter a mounted folder or network path (for example, a mapped drive or UNC share).'
    REFRESH = 'Refresh drives'
    TOP = 'Always on top'
    SOURCE = 'Activity source (operating-system device)'
    UNAVAILABLE = 'Activity unavailable for this drive'
    RESERVED = 'Used percentage is based on total capacity. Free space can exclude filesystem-reserved space.'
    SPACE = 'Used capacity'
    CAPACITY = 'Total: {total}    Used: {used}    Free: {free}'
    READING = 'Reading: {rate}    Highest observed: {peak}'
    WRITING = 'Writing: {rate}    Highest observed: {peak}'
    WAITING = 'Waiting for a second activity sample…'
    UNKNOWN = 'Unavailable'
    READY = 'Activity source: {device}. Rates cover that device, which may serve several volumes.'
    NETWORK = 'No activity device is matched to this path. You may select an OS device separately. Network shares generally do not expose per-share counters here; capacity and an optional path benchmark remain available.'
    FAILED = 'Drive data unavailable or the network path did not respond. Retrying…'
    ENABLE_BENCH = 'Enable optional speed benchmark'
    BENCH = 'Run 128 MiB benchmark'
    BENCH_TITLE = 'Confirm Speed Benchmark'
    BENCH_CONFIRM = 'Write and read a temporary 128 MiB file in:\n{path}\n\nThis uses free space and bandwidth. The test file is removed afterwards. Existing files are not modified. Cached results are not the drive’s maximum speed.'
    BENCH_RESULT = 'Benchmark (128 MiB): read {read}, write {write}. Read may be cached; write includes a flush. This is not rated maximum speed.'
    BENCH_HELP = 'Benchmark is optional and requires a writable path with at least 192 MiB free. Cancel waits for the current I/O call, then removes the test file.'
    GRAPH = 'Recent read and write activity; read is blue, write is orange'
    IDLE = 'Idle'
    ACTIVE = 'Active'
    STATE = '{state} — capacity and activity refresh about once per second.'
