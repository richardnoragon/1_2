# Dependency Mapping and Import Analysis

## Overview
This document provides a comprehensive mapping of all dependencies and import statements that need to be updated during the migration from `src\utilities` to `src\tools`.

## Import Statement Analysis

### Files with utilities imports requiring updates:

#### 1. Main Hub Files
- `src\rfu\backup_20250823_184612\simple_hub.py.original`
- `src\rfu\archive_20250823_191555\simple_hub.py.backup`
- `src\rfu\archive_20250823_191555\simple_hub.py`

#### 2. Tool Integration Files
- `src\tools\system\system_cleanup.py`

#### 3. Test Files
- `tests\test_core_only_persistence.py`
- `tests\test_gui_integration_simple.py`
- `tests\test_import_export_backup_restore.py`
- `tests\test_inheritance_debug.py`
- `tests\test_rfu_integration_validation.py`
- `tests\test_settings_persistence.py`
- `tests\test_size_analyzer_imports.py`

#### 4. Documentation Files
- `src\rfu\advanced_folders\README.md`
- `src\rfu\advanced_folders\INTEGRATION_GUIDE.md`

#### 5. Internal Module Files
- `src\utilities\advanced_folders\gui\preview_pane.py`

## Detailed Import Mappings

### PDF Tools Imports
```python
# Current imports that need updating:
from src.tools.pdf_tools.widgets.enhanced_pdf_tools_widget import

# Should become:
from src.tools.pdf_tools.widgets.enhanced_pdf_tools_widget import
```

### File Operations Imports
```python
# Current imports:
from src.tools.file_operations.catalog.catalog import CatalogWindow
from src.tools.file_operations.file_splitter.gui import
from src.tools.file_operations.cmsd import CopyMoveSyncDeleteWindow
from src.tools.file_operations.organize.organize import OrganizeWindow

# Should become:
from src.tools.file_operations.catalog.catalog import CatalogWindow
from src.tools.file_operations.file_splitter.gui import
from src.tools.file_operations.cmsd import CopyMoveSyncDeleteWindow
from src.tools.file_operations.organize.organize import OrganizeWindow
```

### File Management Imports
```python
# Current imports:
from src.tools.file_management.rename import RenameWindow

# Should become:
from src.tools.file_management.rename import RenameWindow
```

### Metadata Imports
```python
# Current imports:
from src.tools.metadata.image_metadata import ImageMetadataEditorGUI
from src.tools.metadata.image_metadata import \
from src.tools.metadata.office_meta_data_editor import \

# Should become:
from src.tools.metadata.image_metadata import ImageMetadataEditorGUI
from src.tools.metadata.image_metadata import \
from src.tools.metadata.office_meta_data_editor import \
```

### Network Imports
```python
# Current imports:
from src.tools.network.network_scanner import NetworkScannerGUI
from src.tools.network.network_transfer import \
from src.tools.network.network_connectivity_complex.gui.\

# Should become:
from src.tools.network.network_scanner import NetworkScannerGUI
from src.tools.network.network_transfer import \
from src.tools.network.network_connectivity_complex.gui.\
```

### Privacy Imports
```python
# Current imports:
from src.tools.privacy.privacy_tools_simple import SimplePrivacyHub
from src.tools.privacy.data_anonymizer import DataAnonymizerGUI

# Should become:
from src.tools.privacy.privacy_tools_simple import SimplePrivacyHub
from src.tools.privacy.data_anonymizer import DataAnonymizerGUI
```

### Security Imports
```python
# Current imports:
from src.tools.security.simple_password_generator import SimplePasswordGeneratorGUI
from src.tools.security.simple_security_scanner import SimpleSecurityScannerGUI

# Should become:
from src.tools.security.simple_password_generator import SimplePasswordGeneratorGUI
from src.tools.security.simple_security_scanner import SimpleSecurityScannerGUI
```

### System Imports
```python
# Current imports:
from src.tools.system.simple_system_info import \
from src.tools.system.simple_process_monitor import \
from src.tools.system.diagnostics_monitoring.system_diagnostics_gui import SystemDiagnosticsGUI

# Should become:
from src.tools.system.simple_system_info import \
from src.tools.system.simple_process_monitor import \
from src.tools.system.diagnostics_monitoring.system_diagnostics_gui import SystemDiagnosticsGUI
```

### Advanced Folders Imports
```python
# Current imports:
from tools.file_management.advanced_folders.core.folder_configuration import
from tools.file_management.advanced_folders.core.backup_restore import
from tools.file_management.advanced_folders.core.import_export import
from src.tools.advanced_folders.gui.toolbar_manager import
from src.tools.advanced_folders.gui.menu_manager import
from src.tools.advanced_folders.models.folder_models import FileMetadata

# Should become:
from tools.file_management.advanced_folders.core.folder_configuration import
from tools.file_management.advanced_folders.core.backup_restore import
from tools.file_management.advanced_folders.core.import_export import
from src.tools.advanced_folders.gui.toolbar_manager import
from src.tools.advanced_folders.gui.menu_manager import
from src.tools.advanced_folders.models.folder_models import FileMetadata
```

## Configuration File Updates

### Files potentially containing path references:
1. `config/rfu_config.json` - May contain module paths
2. Various `.ui` files - May contain resource paths
3. Documentation files - Contain import examples
4. Test configuration files

## Cross-Module Dependencies

### Internal Dependencies within utilities:
1. **Advanced Folders System**:
   - Heavy internal cross-referencing
   - Database schema dependencies
   - GUI component dependencies

2. **PDF Tools System**:
   - Engine-based architecture
   - Widget interdependencies
   - Dialog system connections

3. **System Tools**:
   - Diagnostics monitoring dependencies
   - Performance monitoring cross-references

### External Dependencies:
1. **PyQt5 Framework**: All GUI components
2. **Database Systems**: SQLite connections
3. **File System**: Path handling and monitoring
4. **Network Libraries**: Connectivity tools
5. **Security Libraries**: Encryption and security tools

## Migration Impact Assessment

### High Impact (Requires careful handling):
1. **Main Hub Files**: Central import points for all tools
2. **Advanced Folders**: Complex internal structure
3. **PDF Tools**: Large integrated system
4. **Test Suite**: Many test files with hardcoded imports

### Medium Impact:
1. **Individual Tool Modules**: Self-contained but interconnected
2. **Configuration Systems**: Path-dependent configurations
3. **Documentation**: Examples and guides need updates

### Low Impact:
1. **Log Files**: Can be regenerated
2. **Cache Files**: Can be cleared and rebuilt
3. **Compiled Python Files**: Will be regenerated automatically

## Automated Update Strategy

### Regular Expression Patterns for Updates:
```regex
# Pattern to find utilities imports:
from\s+src\.utilities\.(.+?)\s+import

# Pattern to find utilities module imports:
import\s+src\.utilities\.(.+?)

# Replacement patterns:
from src.tools.\1 import
import src.tools.\1
```

### File Types Requiring Updates:
1. **Python files (.py)**: All import statements
2. **Documentation (.md)**: Import examples
3. **Configuration files**: Path references
4. **Test files**: Import and path references

## Validation Requirements

### Import Validation:
1. Check all imports resolve correctly
2. Verify no circular dependencies
3. Confirm all modules load properly

### Functionality Validation:
1. All GUI components display correctly
2. All tool functions work as expected
3. Database connections remain functional
4. File operations complete successfully

### Performance Validation:
1. Import times remain acceptable
2. Tool launch times unchanged
3. Memory usage patterns consistent

This mapping provides the foundation for creating automated migration scripts that can update all import statements systematically while maintaining functionality.