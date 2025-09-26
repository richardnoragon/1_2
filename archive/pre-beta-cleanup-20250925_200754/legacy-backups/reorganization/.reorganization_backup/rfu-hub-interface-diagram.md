# RFU Hub Interface Structure Diagram

This document contains a comprehensive Mermaid flowchart diagram that maps the complete user interface structure of Richard's File Utilities (RFU) Hub. The diagram visually represents all primary navigation tabs, secondary menu items, action buttons, form controls, and their hierarchical relationships.

## Interface Overview

The RFU Hub is organized as a tabbed interface built on the StandardWindow architecture with comprehensive menu integration. The interface provides access to various file utilities, security tools, analysis functions, and system management features through both tabbed navigation and menu-driven operations.

## Complete Interface Structure Diagram

```mermaid
flowchart TB
    %% Main Application Entry Point
    START([RFU Hub Application Launch]) --> MAIN_WINDOW[Main Window - QMainWindow]
    
    %% Window Structure
    MAIN_WINDOW --> MENU_BAR[Menu Bar - QMenuBar]
    MAIN_WINDOW --> CENTRAL_WIDGET[Central Widget - QWidget]
    MAIN_WINDOW --> STATUS_BAR[Status Bar - QStatusBar]
    
    %% Menu Bar Structure
    MENU_BAR --> FILE_MENU{📁 File Menu}
    MENU_BAR --> EDIT_MENU{✏️ Edit Menu}
    MENU_BAR --> VIEW_MENU{👁️ View Menu}
    MENU_BAR --> TOOLS_MENU{🔧 Tools Menu}
    MENU_BAR --> HELP_MENU{❓ Help Menu}
    
    %% File Menu Items
    FILE_MENU --> FILE_NEW[📄 New Project - Ctrl+N]
    FILE_MENU --> FILE_OPEN[📂 Open - Ctrl+O]
    FILE_MENU --> FILE_RECENT[📋 Recent Files]
    FILE_MENU --> FILE_SAVE[💾 Save - Ctrl+S]
    FILE_MENU --> FILE_SAVE_AS[💾 Save As - Ctrl+Shift+S]
    FILE_MENU --> FILE_EXPORT[📤 Export Data]
    FILE_MENU --> FILE_IMPORT[📥 Import Data]
    FILE_MENU --> FILE_PRINT[🖨️ Print - Ctrl+P]
    FILE_MENU --> FILE_PREFERENCES[⚙️ Preferences - Ctrl+,]
    FILE_MENU --> FILE_EXIT[🚪 Exit - Ctrl+Q]
    
    %% Edit Menu Items
    EDIT_MENU --> EDIT_UNDO[↶ Undo - Ctrl+Z]
    EDIT_MENU --> EDIT_REDO[↷ Redo - Ctrl+Y]
    EDIT_MENU --> EDIT_CUT[✂️ Cut - Ctrl+X]
    EDIT_MENU --> EDIT_COPY[📋 Copy - Ctrl+C]
    EDIT_MENU --> EDIT_PASTE[📄 Paste - Ctrl+V]
    EDIT_MENU --> EDIT_SELECT_ALL[🔘 Select All - Ctrl+A]
    EDIT_MENU --> EDIT_FIND[🔍 Find - Ctrl+F]
    EDIT_MENU --> EDIT_REPLACE[🔄 Replace - Ctrl+H]
    
    %% View Menu Items
    VIEW_MENU --> VIEW_ZOOM_IN[🔍 Zoom In - Ctrl++]
    VIEW_MENU --> VIEW_ZOOM_OUT[🔍 Zoom Out - Ctrl+-]
    VIEW_MENU --> VIEW_ZOOM_RESET[🔍 Reset Zoom - Ctrl+0]
    VIEW_MENU --> VIEW_THEME[🎨 Theme]
    VIEW_MENU --> VIEW_FULLSCREEN[🖥️ Fullscreen - F11]
    VIEW_MENU --> VIEW_ALWAYS_TOP[📌 Always on Top]
    VIEW_MENU --> VIEW_REFRESH[🔄 Refresh - F5]
    
    %% Tools Menu Items
    TOOLS_MENU --> TOOLS_FILE_MGMT[📁 File Management]
    TOOLS_MENU --> TOOLS_ANALYSIS[📊 Analysis Tools]
    TOOLS_MENU --> TOOLS_SECURITY[🔒 Security Tools]
    TOOLS_MENU --> TOOLS_SYSTEM[💻 System Utilities]
    TOOLS_MENU --> TOOLS_OPTIONS[⚙️ Options]
    TOOLS_MENU --> TOOLS_LOG_VIEWER[📋 Log Viewer]
    TOOLS_MENU --> TOOLS_PERFORMANCE[📊 Performance Monitor]
    TOOLS_MENU --> TOOLS_RESET[🔄 Reset Settings]
    
    %% Help Menu Items
    HELP_MENU --> HELP_USER_GUIDE[📖 User Guide - F1]
    HELP_MENU --> HELP_SHORTCUTS[⌨️ Keyboard Shortcuts - Ctrl+?]
    HELP_MENU --> HELP_SYSTEM_INFO[📊 System Information]
    HELP_MENU --> HELP_LOGS[📋 View Logs]
    HELP_MENU --> HELP_ABOUT[ℹ️ About]
    
    %% Central Widget Structure
    CENTRAL_WIDGET --> HEADER_LABEL[Header Label: "Richard's File Utilities - Enhanced Edition"]
    CENTRAL_WIDGET --> SCROLL_AREA[Scroll Area - QScrollArea]
    CENTRAL_WIDGET --> FOOTER_LABEL[Footer Label: Menu System Guide]
    
    %% Main Tab Widget Structure
    SCROLL_AREA --> TAB_WIDGET[Tab Widget - QTabWidget]
    
    %% Primary Navigation Tabs
    TAB_WIDGET --> ANALYSIS_TAB{📊 Analysis Tools}
    TAB_WIDGET --> FILE_OPS_TAB{📁 File Operations}
    TAB_WIDGET --> METADATA_TAB{📄 Metadata Tools}
    TAB_WIDGET --> NETWORK_TAB{🌐 Network Tools}
    TAB_WIDGET --> PDF_TOOLS_TAB{📄 PDF Tools}
    TAB_WIDGET --> PRIVACY_TAB{🔒 Privacy Tools}
    TAB_WIDGET --> SECURITY_TAB{🛡️ Security Tools}
    TAB_WIDGET --> SYSTEM_TAB{💻 System Tools}
    TAB_WIDGET --> LOGS_TAB{📋 Logs}
    
    %% Analysis Tools Tab Content
    ANALYSIS_TAB --> ANALYSIS_GRID[Grid Layout - 3x2 Grid]
    ANALYSIS_GRID --> CHECKSUM_BTN[🔐 Checksum Verification]
    ANALYSIS_GRID --> DUPLICATE_BTN[🔍 Duplicate Finder]
    ANALYSIS_GRID --> SIZE_ANALYZER_BTN[📊 Size Analyzer]
    ANALYSIS_GRID --> EMPTY_FOLDERS_BTN[📂 Empty Folders]
    ANALYSIS_GRID --> CATALOG_BTN[📚 File Catalog]
    ANALYSIS_GRID --> ADVANCED_ANALYSIS_BTN[🔬 Advanced Analysis]
    
    %% File Operations Tab Content
    FILE_OPS_TAB --> FILE_OPS_GRID[Grid Layout - 3x2 Grid]
    FILE_OPS_GRID --> FILE_SPLITTER_BTN[📂 File Splitter]
    FILE_OPS_GRID --> CMSD_BTN[📋 Copy/Move/Sync]
    FILE_OPS_GRID --> SYNC_BACKUP_BTN[🔄 Sync & Backup]
    FILE_OPS_GRID --> FILE_TOUCH_BTN[⏰ File Touch]
    FILE_OPS_GRID --> ORGANIZE_BTN[📁 Organize Files]
    FILE_OPS_GRID --> BATCH_RENAME_BTN[🗂️ Batch Rename]
    
    %% Metadata Tools Tab Content
    METADATA_TAB --> METADATA_GRID[Grid Layout - 3x2 Grid]
    METADATA_GRID --> IMAGE_META_BTN[🖼️ Image Metadata]
    METADATA_GRID --> OFFICE_META_BTN[📄 Office Metadata]
    METADATA_GRID --> PDF_META_BTN[📕 PDF Metadata]
    METADATA_GRID --> AUDIO_META_BTN[🎵 Audio Metadata]
    METADATA_GRID --> VIDEO_META_BTN[🎬 Video Metadata]
    METADATA_GRID --> META_EDITOR_BTN[✏️ Metadata Editor]
    
    %% Network Tools Tab Content
    NETWORK_TAB --> NETWORK_GRID[Grid Layout - 3x2 Grid]
    NETWORK_GRID --> NETWORK_SCANNER_BTN[🌐 Network Scanner]
    NETWORK_GRID --> CONNECTIVITY_BTN[🔌 Connectivity Test]
    NETWORK_GRID --> NETWORK_TRANSFER_BTN[📡 Network Transfer]
    NETWORK_GRID --> BOOKMARK_BTN[🔗 Bookmark Manager]
    NETWORK_GRID --> BANDWIDTH_BTN[📊 Bandwidth Monitor]
    NETWORK_GRID --> NETWORK_SECURITY_BTN[🛡️ Network Security]
    
    %% PDF Tools Tab Content
    PDF_TOOLS_TAB --> PDF_CATEGORIES[Category Selection Interface]
    PDF_CATEGORIES --> PDF_READER_CAT[📖 PDF Readers]
    PDF_CATEGORIES --> PDF_CONVERTER_CAT[🔄 PDF Converters]
    PDF_CATEGORIES --> PDF_EDITOR_CAT[✏️ PDF Editors]
    PDF_CATEGORIES --> PDF_VIEWER_CAT[👁️ PDF Viewers]
    PDF_CATEGORIES --> PDF_UTILITY_CAT[🔧 PDF Utilities]
    
    %% Privacy Tools Tab Content
    PRIVACY_TAB --> PRIVACY_GRID[Grid Layout - 3x2 Grid]
    PRIVACY_GRID --> PRIVACY_CLEANER_BTN[🧹 Privacy Cleaner]
    PRIVACY_GRID --> BROWSER_CLEANER_BTN[🌐 Browser Cleaner]
    PRIVACY_GRID --> TEMP_CLEANER_BTN[🗑️ Temp File Cleaner]
    PRIVACY_GRID --> REGISTRY_CLEANER_BTN[📋 Registry Cleaner]
    PRIVACY_GRID --> PRIVACY_SCAN_BTN[🔍 Privacy Scan]
    PRIVACY_GRID --> PRIVACY_SHIELD_BTN[🛡️ Privacy Shield]
    
    %% Security Tools Tab Content
    SECURITY_TAB --> SECURITY_GRID[Grid Layout - 3x2 Grid]
    SECURITY_GRID --> FILE_ENCRYPT_BTN[🔒 File Encryption]
    SECURITY_GRID --> SECURE_DELETE_BTN[🗑️ Secure Delete]
    SECURITY_GRID --> PASSWORD_GEN_BTN[🔑 Password Generator]
    SECURITY_GRID --> SECURITY_SCAN_BTN[🔍 Security Scan]
    SECURITY_GRID --> SECURITY_MONITOR_BTN[🛡️ Security Monitor]
    SECURITY_GRID --> SECURITY_SETTINGS_BTN[⚙️ Security Settings]
    
    %% System Tools Tab Content
    SYSTEM_TAB --> SYSTEM_GRID[Grid Layout - 3x2 Grid]
    SYSTEM_GRID --> SYSTEM_INFO_BTN[💻 System Information]
    SYSTEM_GRID --> DISK_ANALYZER_BTN[💿 Disk Usage Analyzer]
    SYSTEM_GRID --> PROCESS_MONITOR_BTN[⚡ Process Monitor]
    SYSTEM_GRID --> SYSTEM_CLEANUP_BTN[🧹 System Cleanup]
    SYSTEM_GRID --> PERFORMANCE_BTN[📊 Performance Monitor]
    SYSTEM_GRID --> SYS_SETTINGS_BTN[⚙️ System Settings]
    
    %% Logs Tab Content
    LOGS_TAB --> LOGS_LAYOUT[Vertical Layout]
    LOGS_LAYOUT --> LOG_VIEWER[📋 Log Text Viewer - QTextEdit]
    LOGS_LAYOUT --> LOG_CONTROLS[Log Control Panel]
    LOG_CONTROLS --> REFRESH_LOGS_BTN[🔄 Refresh Logs]
    LOG_CONTROLS --> CLEAR_LOGS_BTN[🗑️ Clear Display]
    LOG_CONTROLS --> EXPORT_LOGS_BTN[💾 Export Logs]
    
    %% Modal Dialogs and Forms
    FILE_PREFERENCES --> PREFERENCES_DIALOG[Preferences Dialog - QDialog]
    PREFERENCES_DIALOG --> PREF_TABS[Settings Tab Widget]
    PREF_TABS --> GENERAL_TAB[🏠 General Settings]
    PREF_TABS --> DUPLICATES_TAB[🔍 Duplicates Settings]
    PREF_TABS --> SECURE_DELETE_TAB[🗑️ Secure Delete Settings]
    PREF_TABS --> COMPRESSION_TAB[📦 Compression Settings]
    PREF_TABS --> SYNC_TAB[🔄 Sync Settings]
    PREF_TABS --> CATALOG_TAB[📚 Catalog Settings]
    PREF_TABS --> ORGANIZE_TAB[📁 Organize Settings]
    
    %% General Settings Form Controls
    GENERAL_TAB --> THEME_COMBO[Theme ComboBox: Light/Dark]
    GENERAL_TAB --> DEFAULT_DIR_EDIT[Default Directory LineEdit + Browse Button]
    GENERAL_TAB --> RECENT_SPIN[Max Recent Entries SpinBox]
    GENERAL_TAB --> LOG_LEVEL_COMBO[Logging Level ComboBox]
    GENERAL_TAB --> DEBUG_CHECK[Debug Logging CheckBox]
    
    %% Duplicates Settings Form Controls
    DUPLICATES_TAB --> HASH_ALGO_COMBO[Hash Algorithm ComboBox]
    DUPLICATES_TAB --> MIN_SIZE_SPIN[Minimum File Size SpinBox]
    DUPLICATES_TAB --> SKIP_SYSTEM_CHECK[Skip System Files CheckBox]
    
    %% Secure Delete Settings Form Controls
    SECURE_DELETE_TAB --> DEFAULT_PASSES_SPIN[Default Passes SpinBox]
    SECURE_DELETE_TAB --> MAX_PASSES_SPIN[Maximum Passes SpinBox]
    
    %% Compression Settings Form Controls
    COMPRESSION_TAB --> FORMAT_COMBO[Default Format ComboBox]
    COMPRESSION_TAB --> COMPRESSION_SPIN[Compression Level SpinBox]
    COMPRESSION_TAB --> PASSWORD_CHECK[Password Protection CheckBox]
    
    %% Sync Settings Form Controls
    SYNC_TAB --> SYNC_MODE_COMBO[Sync Mode ComboBox]
    SYNC_TAB --> BACKUP_CHECK[Create Backups CheckBox]
    SYNC_TAB --> SKIP_NEWER_CHECK[Skip Newer Files CheckBox]
    
    %% Catalog Settings Form Controls
    CATALOG_TAB --> CATALOG_RECURSIVE_CHECK[Recursive by Default CheckBox]
    CATALOG_TAB --> CATALOG_DUPLICATES_CHECK[Check Duplicates CheckBox]
    CATALOG_TAB --> SHOW_SIZES_CHECK[Show File Sizes CheckBox]
    CATALOG_TAB --> SHOW_DATES_CHECK[Show Dates CheckBox]
    CATALOG_TAB --> SORT_BY_COMBO[Sort By ComboBox]
    CATALOG_TAB --> SORT_ORDER_COMBO[Sort Order ComboBox]
    
    %% Organize Settings Form Controls
    ORGANIZE_TAB --> ORGANIZE_RECURSIVE_CHECK[Recursive by Default CheckBox]
    ORGANIZE_TAB --> CATEGORY_FOLDERS_CHECK[Create Category Folders CheckBox]
    ORGANIZE_TAB --> MOVE_FILES_CHECK[Move Files CheckBox]
    
    %% Preferences Dialog Buttons
    PREFERENCES_DIALOG --> PREF_BUTTONS[Dialog Button Box]
    PREF_BUTTONS --> RESET_ALL_BTN[Reset All Button]
    PREF_BUTTONS --> SAVE_BTN[Save Button]
    PREF_BUTTONS --> CANCEL_BTN[Cancel Button]
    
    %% Other Modal Dialogs
    TOOLS_LOG_VIEWER --> LOG_VIEWER_DIALOG[Log Viewer Dialog]
    HELP_SHORTCUTS --> SHORTCUTS_DIALOG[Keyboard Shortcuts Dialog]
    HELP_SYSTEM_INFO --> SYSTEM_INFO_DIALOG[System Information Dialog]
    HELP_ABOUT --> ABOUT_DIALOG[About Dialog]
    
    %% Tool Launch Windows
    CHECKSUM_BTN --> CHECKSUM_WINDOW[Checksum Verification Window]
    DUPLICATE_BTN --> DUPLICATE_WINDOW[Duplicate Finder Window]
    SIZE_ANALYZER_BTN --> SIZE_ANALYZER_WINDOW[Size Analyzer Window]
    FILE_SPLITTER_BTN --> FILE_SPLITTER_WINDOW[File Splitter Window]
    CMSD_BTN --> CMSD_WINDOW[Copy/Move/Sync/Delete Window]
    
    %% Appearance and Theming
    VIEW_THEME --> THEME_SELECTION[Theme Selection]
    THEME_SELECTION --> LIGHT_THEME[☀️ Light Theme]
    THEME_SELECTION --> DARK_THEME[🌙 Dark Theme]
    
    %% User Flow Paths
    START --> |User launches application| MAIN_WINDOW
    TAB_WIDGET --> |User selects tab| ANALYSIS_TAB
    TAB_WIDGET --> |User selects tab| FILE_OPS_TAB
    TAB_WIDGET --> |User selects tab| METADATA_TAB
    ANALYSIS_GRID --> |User clicks tool| CHECKSUM_BTN
    FILE_OPS_GRID --> |User clicks tool| FILE_SPLITTER_BTN
    MENU_BAR --> |User accesses preferences| FILE_PREFERENCES
    FILE_PREFERENCES --> |Opens modal dialog| PREFERENCES_DIALOG
    PREF_BUTTONS --> |User saves changes| SAVE_BTN
    PREF_BUTTONS --> |User cancels| CANCEL_BTN
    
    %% Styling Classes
    classDef primaryTab fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef secondaryButton fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px,color:#000
    classDef menuItem fill:#e8f5e8,stroke:#388e3c,stroke-width:1px,color:#000
    classDef dialog fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef control fill:#fce4ec,stroke:#c2185b,stroke-width:1px,color:#000
    classDef window fill:#f1f8e9,stroke:#689f38,stroke-width:2px,color:#000
    
    %% Apply Styling
    class ANALYSIS_TAB,FILE_OPS_TAB,METADATA_TAB,NETWORK_TAB,PDF_TOOLS_TAB,PRIVACY_TAB,SECURITY_TAB,SYSTEM_TAB,LOGS_TAB primaryTab
    class CHECKSUM_BTN,DUPLICATE_BTN,SIZE_ANALYZER_BTN,FILE_SPLITTER_BTN,CMSD_BTN,SYNC_BACKUP_BTN secondaryButton
    class FILE_NEW,FILE_OPEN,FILE_SAVE,EDIT_UNDO,EDIT_COPY,VIEW_REFRESH menuItem
    class PREFERENCES_DIALOG,LOG_VIEWER_DIALOG,SHORTCUTS_DIALOG,ABOUT_DIALOG dialog
    class THEME_COMBO,DEFAULT_DIR_EDIT,RECENT_SPIN,HASH_ALGO_COMBO,MIN_SIZE_SPIN control
    class MAIN_WINDOW,CHECKSUM_WINDOW,DUPLICATE_WINDOW,SIZE_ANALYZER_WINDOW window
```

## Interface Navigation Flows

### Primary User Journeys

1. **Initial Access Flow**: Application Launch → Main Window → Tab Selection → Tool Access
2. **Menu-Driven Flow**: Menu Bar → Menu Item → Dialog/Action → Result
3. **Preferences Flow**: File Menu → Preferences → Settings Dialog → Tab Selection → Form Controls → Save/Cancel
4. **Tool Launch Flow**: Tab Selection → Tool Button → Tool Window Launch → Tool Operations

### Secondary Navigation Patterns

1. **Keyboard Shortcuts**: Direct access to menu functions via keyboard combinations
2. **Context Menus**: Right-click operations on interface elements
3. **Status Bar Feedback**: Real-time status updates and operation progress
4. **Theme Switching**: Dynamic interface appearance changes

## Interface Component Types

### Navigation Elements

- **Primary Tabs**: Main functional areas (Analysis, File Operations, etc.)
- **Menu Bar**: Traditional menu structure with keyboard shortcuts
- **Tool Buttons**: Grid-arranged action buttons within tabs
- **Status Bar**: Information and progress display

### Form Controls

- **ComboBoxes**: Dropdown selection lists (Theme, Hash Algorithm, etc.)
- **SpinBoxes**: Numeric input controls with increment/decrement
- **CheckBoxes**: Boolean option toggles
- **LineEdits**: Text input fields with optional browse buttons
- **Buttons**: Action triggers (Save, Cancel, Browse, etc.)

### Modal Elements

- **Settings Dialog**: Multi-tab preferences configuration
- **Tool Windows**: Dedicated windows for specific utilities
- **Information Dialogs**: About, System Info, Help displays
- **Confirmation Dialogs**: User action confirmations

### Layout Structures

- **Grid Layouts**: Organized button arrangements (3x2 grids typical)
- **Form Layouts**: Label-control pairs in settings dialogs
- **Vertical/Horizontal Layouts**: Linear control arrangements
- **Scroll Areas**: Scrollable content containers

This comprehensive diagram represents the complete interface architecture of the RFU Hub, showing the hierarchical relationships between all UI elements and the logical flow patterns users follow when navigating through the application.
