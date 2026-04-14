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
    LOADING = "Loading File Finder…"


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
    LOADING = "Loading Size Analyzer…"


class DuplicateFinder:
    TITLE = "Duplicate Finder"
    LOADING = "Loading Duplicate Finder…"


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


class Organizer:
    TITLE = "File Organizer"
    LOADING = "Loading File Organizer…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


class AdvancedFolders:
    TITLE = "Advanced Folders"
    LOADING = "Loading Advanced Folders…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


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
    LOADING = "Loading Software Maintenance…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


# ---------------------------------------------------------------------------
# Network tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class NetworkTools:
    TITLE = "Network Tools"
    LOADING = "Loading Network Tools…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


# ---------------------------------------------------------------------------
# File Operations tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class FileOperations:
    TITLE = "File Operations"
    LOADING = "Loading File Operations…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"


# ---------------------------------------------------------------------------
# Privacy tools (side-effect — DR-5)
# ---------------------------------------------------------------------------


class Privacy:
    TITLE = "Privacy Tools"
    LOADING = "Loading Privacy Tools…"
    DRY_RUN_LABEL = "Dry Run (Preview Only)"
