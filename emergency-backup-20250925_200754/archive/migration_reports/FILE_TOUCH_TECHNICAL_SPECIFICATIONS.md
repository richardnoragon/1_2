# File Touch Utility - Technical Specifications
**Richard's File Utilities Hub - File Touch Integration**

**Document Version:** 1.0  
**Created:** 2025-07-28  
**Status:** Technical Specification  
**Related Document:** [FILE_TOUCH_COMPREHENSIVE_MIGRATION_PLAN.md](FILE_TOUCH_COMPREHENSIVE_MIGRATION_PLAN.md)

---

## Technical Architecture Specifications

### Component Architecture

#### Core Logic Layer
**Location**: `file_utilities_2/core/`

##### FileTouchLogic Class
```python
class FileTouchLogic(HubIntegratedTool):
    """Enhanced file touch logic with hub integration."""
    
    # Signal Definitions
    timestamps_fetched = pyqtSignal(dict)      # {access, modification, creation}
    operation_result = pyqtSignal(bool, str)   # success, message
    error_occurred = pyqtSignal(str)           # error_message
    progress_updated = pyqtSignal(int, str)    # percentage, status
    finished = pyqtSignal()                    # operation_complete
    
    # Core Methods
    def get_file_timestamps(self, filepath: str) -> None
    def set_file_timestamps(self, filepath: str, atime: int, mtime: int) -> None
    def validate_file_access(self, filepath: str) -> bool
    def backup_timestamps(self, filepath: str) -> dict
    def restore_timestamps(self, filepath: str, backup: dict) -> bool
```

##### FileTouchConfig Class
```python
class FileTouchConfig:
    """Configuration manager for File Touch utility."""
    
    # Configuration Sections
    SECTIONS = ['general', 'profiles', 'ui', 'operations', 'hub_integration']
    
    # Core Methods
    def get_setting(self, subsection: str, key: str, default: Any = None) -> Any
    def set_setting(self, subsection: str, key: str, value: Any) -> bool
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]
    def save_profile(self, profile_name: str, settings: Dict[str, Any]) -> bool
    def delete_profile(self, profile_name: str) -> bool
    def export_profiles(self, file_path: str) -> bool
    def import_profiles(self, file_path: str) -> bool
```

##### FileTouchLogger Class
```python
class FileTouchLogger:
    """Categorized logging for File Touch utility."""
    
    # Log Categories
    CATEGORIES = ['core_logic', 'gui_events', 'hub_integration', 'file_operations', 'errors']
    
    # Core Methods
    def log_operation(self, operation: str, filepath: str, success: bool)
    def log_timestamp_change(self, filepath: str, old_times: dict, new_times: dict)
    def log_profile_action(self, action: str, profile_name: str, success: bool)
    def log_hub_event(self, event_type: str, data: Dict[str, Any])
    def log_error(self, error_type: str, message: str, exception: Exception = None)
```

#### GUI Layer
**Location**: `file_utilities_2/gui/`

##### FileTouchGUI Class
```python
class FileTouchGUI(StandardWindow):
    """Standardized file touch GUI with full integration."""
    
    # UI Components
    filePathEdit: QLineEdit           # File path input
    browseButton: QPushButton         # File browser
    refreshButton: QPushButton        # Refresh timestamps
    applyButton: QPushButton          # Apply changes
    accessTimeEdit: QDateTimeEdit     # Access time editor
    modificationTimeEdit: QDateTimeEdit  # Modification time editor
    creationTimeEdit: QDateTimeEdit  # Creation time display
    profileCombo: QComboBox           # Profile selector
    
    # Core Methods
    def _load_ui(self) -> None
    def _setup_components(self) -> None
    def _connect_signals(self) -> None
    def _apply_theme(self) -> None
    def browse_file(self) -> None
    def refresh_timestamps(self) -> None
    def apply_changes(self) -> None
    def save_profile(self) -> None
    def load_profile(self, profile_name: str) -> None
    def delete_profile(self) -> None
```

### Integration Specifications

#### Hub Connector Integration

##### Communication Protocol
```python
# Message Types
TOOL_STARTED = "file_touch_started"
TOOL_PROGRESS = "file_touch_progress"
TOOL_COMPLETED = "file_touch_completed"
TOOL_ERROR = "file_touch_error"
FILE_MODIFIED = "file_modified"

# Event Broadcasting
class FileTouchHubEvents:
    def broadcast_file_modification(self, filepath: str, operation: str)
    def broadcast_operation_start(self, operation: str, filepath: str)
    def broadcast_operation_complete(self, operation: str, success: bool)
    def request_file_lock(self, filepath: str) -> bool
    def release_file_lock(self, filepath: str) -> bool
```

##### Resource Coordination
```python
# Resource Requirements
RESOURCE_REQUIREMENTS = {
    'cpu_priority': 'low',
    'memory_limit_mb': 64,
    'disk_io_priority': 'normal',
    'file_access': 'exclusive'
}

# Coordination with Other Tools
COORDINATED_TOOLS = ['file_finder', 'organize', 'checksum']
```

#### Theme Integration

##### StandardWindow Integration
```python
class FileTouchGUI(StandardWindow):
    def __init__(self):
        super().__init__(
            title="File Touch - Timestamp Editor",
            icon_path=self._get_file_touch_icon()
        )
        
    def _get_file_touch_icon(self) -> str:
        return self.config.get_resource_path('icon_path')
        
    def _apply_custom_styling(self):
        # File Touch specific styling
        self.filePathEdit.setStyleSheet(ThemeManager.INPUT_FIELD)
        self.profileCombo.setStyleSheet(ThemeManager.COMBO_BOX)
```

##### Theme Customizations
```python
# File Touch Specific Styles
FILE_TOUCH_STYLES = {
    'timestamp_group': f"""
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {Colors.ACCENT};
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 15px;
        }}
    """,
    'datetime_edit': f"""
        QDateTimeEdit {{
            background-color: {Colors.WINDOW_BACKGROUND};
            border: 1px solid {Colors.TEXT_DISABLED};
            border-radius: 4px;
            padding: 8px;
            font-family: {Fonts.MONOSPACE_FAMILY};
        }}
    """
}
```

### Configuration Schema

#### Complete Configuration Structure
```json
{
  "file_touch": {
    "general": {
      "module_path": "file_utilities_2.gui.file_touch_gui",
      "class_name": "FileTouchGUI",
      "last_opened_file": "",
      "recent_files": [],
      "max_recent_files": 10,
      "auto_refresh_timestamps": true,
      "confirm_timestamp_changes": true,
      "enable_file_validation": true,
      "show_hidden_files": false
    },
    "profiles": {
      "enable_profile_management": true,
      "default_profile": "current_time",
      "auto_save_profiles": true,
      "profile_categories": ["timestamp_sets", "file_operations"],
      "max_profiles": 50,
      "profile_backup_enabled": true,
      "shared_profiles": true
    },
    "ui": {
      "window_geometry": {
        "width": 600,
        "height": 400,
        "remember_size": true,
        "remember_position": true,
        "center_on_screen": true
      },
      "display_options": {
        "show_creation_time_warning": true,
        "show_milliseconds": false,
        "use_local_timezone": true,
        "date_format": "yyyy-MM-dd",
        "time_format": "HH:mm:ss"
      },
      "interaction": {
        "enable_drag_drop": true,
        "show_tooltips": true,
        "confirm_destructive_actions": true,
        "auto_select_text": true
      }
    },
    "operations": {
      "backup_before_changes": false,
      "log_all_operations": true,
      "enable_undo": false,
      "operation_timeout": 30,
      "validate_timestamps": true,
      "preserve_permissions": true,
      "handle_readonly_files": "warn"
    },
    "hub_integration": {
      "enable_hub_integration": true,
      "tool_name": "File Touch",
      "tool_category": "file_operations",
      "broadcast_operations": true,
      "coordinate_with_tools": ["file_finder", "organize"],
      "resource_sharing": {
        "allow_concurrent_access": false,
        "request_exclusive_lock": true,
        "lock_timeout": 10
      },
      "event_broadcasting": {
        "broadcast_start": true,
        "broadcast_progress": true,
        "broadcast_completion": true,
        "broadcast_errors": true,
        "broadcast_file_changes": true
      }
    },
    "logging": {
      "enable_tool_logging": true,
      "log_level": "INFO",
      "log_file": "logs/file_touch/file_touch.log",
      "max_log_size_mb": 5,
      "backup_count": 3,
      "log_categories": {
        "core_logic": "INFO",
        "gui_events": "DEBUG",
        "hub_integration": "INFO",
        "file_operations": "INFO",
        "errors": "ERROR"
      }
    },
    "resources": {
      "icon_path": "file_utilities_2/gui/icons/file_touch.png",
      "ui_file": "file_utilities_2/gui/file_touch.ui",
      "help_file": "file_utilities_2/docs/file_touch_help.html",
      "template_path": "file_utilities_2/templates/file_touch",
      "cache_directory": "cache/file_touch",
      "temp_directory": "temp/file_touch",
      "log_directory": "logs/file_touch"
    }
  }
}
```

### Database Schema (Profile Storage)

#### Profile Table Structure
```sql
-- File Touch Profiles
CREATE TABLE file_touch_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) DEFAULT 'timestamp_sets',
    description TEXT,
    settings JSON NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    is_shared BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE
);

-- Profile Usage History
CREATE TABLE file_touch_profile_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER REFERENCES file_touch_profiles(id),
    used_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path TEXT,
    operation_type VARCHAR(50),
    success BOOLEAN
);
```

### API Specifications

#### Public API Interface
```python
class FileTouchAPI:
    """Public API for File Touch utility integration."""
    
    @staticmethod
    def get_file_timestamps(filepath: str) -> Dict[str, datetime]:
        """Get file timestamps."""
        
    @staticmethod
    def set_file_timestamps(filepath: str, atime: datetime = None, 
                          mtime: datetime = None) -> bool:
        """Set file timestamps."""
        
    @staticmethod
    def create_profile(name: str, settings: Dict[str, Any]) -> bool:
        """Create timestamp profile."""
        
    @staticmethod
    def apply_profile(filepath: str, profile_name: str) -> bool:
        """Apply profile to file."""
        
    @staticmethod
    def batch_process(filepaths: List[str], operation: str, 
                     settings: Dict[str, Any]) -> Dict[str, bool]:
        """Batch process multiple files."""
```

### Performance Specifications

#### Performance Requirements
```python
PERFORMANCE_REQUIREMENTS = {
    'timestamp_retrieval': {
        'max_time_ms': 100,
        'target_time_ms': 50,
        'memory_usage_kb': 512
    },
    'timestamp_modification': {
        'max_time_ms': 200,
        'target_time_ms': 100,
        'memory_usage_kb': 1024
    },
    'gui_responsiveness': {
        'max_ui_freeze_ms': 50,
        'target_ui_freeze_ms': 16,
        'startup_time_ms': 1000
    },
    'hub_communication': {
        'max_message_delay_ms': 100,
        'target_message_delay_ms': 50,
        'heartbeat_interval_ms': 30000
    }
}
```

#### Memory Management
```python
class FileTouchMemoryManager:
    """Memory management for File Touch utility."""
    
    MAX_MEMORY_USAGE_MB = 64
    CACHE_SIZE_ENTRIES = 100
    PROFILE_CACHE_SIZE = 50
    
    def monitor_memory_usage(self) -> Dict[str, float]
    def cleanup_cache(self) -> None
    def optimize_memory(self) -> None
```

### Security Specifications

#### File Access Security
```python
class FileTouchSecurity:
    """Security measures for File Touch utility."""
    
    def validate_file_path(self, filepath: str) -> bool:
        """Validate file path for security."""
        
    def check_file_permissions(self, filepath: str) -> Dict[str, bool]:
        """Check file access permissions."""
        
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input."""
        
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events."""
```

#### Permission Requirements
```python
REQUIRED_PERMISSIONS = {
    'file_read': True,
    'file_write': True,
    'file_stat': True,
    'directory_access': True,
    'system_time_access': False,
    'registry_access': False  # Windows only
}
```

### Error Handling Specifications

#### Error Categories
```python
class FileTouchErrors:
    """Error handling for File Touch utility."""
    
    # Error Types
    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    INVALID_TIMESTAMP = "invalid_timestamp"
    OPERATION_TIMEOUT = "operation_timeout"
    CONFIGURATION_ERROR = "configuration_error"
    HUB_COMMUNICATION_ERROR = "hub_communication_error"
    
    # Error Handlers
    def handle_file_error(self, error_type: str, filepath: str, exception: Exception)
    def handle_permission_error(self, filepath: str, required_permission: str)
    def handle_timestamp_error(self, timestamp_value: Any, expected_type: str)
    def handle_hub_error(self, operation: str, error_details: Dict[str, Any])
```

#### Recovery Procedures
```python
class FileTouchRecovery:
    """Recovery procedures for File Touch utility."""
    
    def recover_from_file_error(self, filepath: str) -> bool
    def recover_from_permission_error(self, filepath: str) -> bool
    def recover_from_hub_disconnection(self) -> bool
    def recover_configuration(self) -> bool
    def create_error_report(self, error_context: Dict[str, Any]) -> str
```

### Testing Specifications

#### Unit Test Coverage
```python
class TestFileTouchLogic(unittest.TestCase):
    """Comprehensive unit tests for File Touch logic."""
    
    def test_timestamp_retrieval_success(self)
    def test_timestamp_retrieval_file_not_found(self)
    def test_timestamp_modification_success(self)
    def test_timestamp_modification_permission_denied(self)
    def test_profile_management(self)
    def test_configuration_handling(self)
    def test_error_handling(self)
    def test_hub_integration(self)
```

#### Integration Test Scenarios
```python
INTEGRATION_TEST_SCENARIOS = [
    'gui_logic_integration',
    'hub_communication',
    'configuration_persistence',
    'theme_integration',
    'cross_tool_coordination',
    'error_propagation',
    'performance_under_load',
    'concurrent_access_handling'
]
```

#### Performance Test Benchmarks
```python
PERFORMANCE_BENCHMARKS = {
    'single_file_operation': {
        'files_count': 1,
        'max_time_ms': 200,
        'memory_limit_mb': 32
    },
    'batch_operation': {
        'files_count': 100,
        'max_time_ms': 5000,
        'memory_limit_mb': 64
    },
    'stress_test': {
        'files_count': 1000,
        'max_time_ms': 30000,
        'memory_limit_mb': 128
    }
}
```

### Deployment Specifications

#### Package Structure
```
file_utilities_2/
├── core/
│   ├── file_touch_logic.py      # Core business logic
│   ├── file_touch_config.py     # Configuration management
│   └── file_touch_logging.py    # Logging system
├── gui/
│   ├── file_touch_gui.py        # GUI implementation
│   ├── file_touch.ui            # UI definition
│   └── icons/
│       └── file_touch.png       # Application icon
├── tests/
│   ├── test_file_touch.py       # Unit tests
│   ├── test_file_touch_integration.py  # Integration tests
│   └── test_file_touch_performance.py  # Performance tests
├── docs/
│   ├── file_touch_api.md        # API documentation
│   ├── file_touch_user_guide.md # User documentation
│   └── file_touch_help.html     # Help system
└── templates/
    └── file_touch/
        ├── default_profiles.json   # Default profiles
        └── configuration_template.json  # Config template
```

#### Installation Requirements
```python
INSTALLATION_REQUIREMENTS = {
    'python_version': '>=3.8',
    'dependencies': [
        'PyQt5>=5.15.0',
        'file_utilities_2>=2.0.0'
    ],
    'optional_dependencies': [
        'pywin32>=227'  # Windows creation time support
    ],
    'system_requirements': {
        'memory_mb': 128,
        'disk_space_mb': 50,
        'cpu_cores': 1
    }
}
```

This technical specification provides the detailed implementation guidelines needed to execute the migration plan successfully. All components are designed to integrate seamlessly with the existing file_utilities_2 architecture while maintaining full functionality and enhancing capabilities through shared resources and hub integration.