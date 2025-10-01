# Richard's File Utilities (RFU) - AI Coding Agent Instructions

## Architecture Overview

RFU is a comprehensive PyQt5-based file management suite organized around **tool categorization** and **modular integration**. The architecture uses a hub-and-spoke model where `main.py` serves as the central entry point launching tool-specific GUI classes.

### Key Architectural Patterns

**Tool Discovery System**: Tools are auto-discovered using metadata-driven patterns. Each tool follows `{ToolName}GUI` class naming and imports through fallback strategies:
```python
# Main pattern in launch_tool()
import_strategies = [
    lambda: self._import_direct(module_name, class_name),
    lambda: self._import_absolute(module_name, class_name), 
    lambda: self._import_dynamic(module_name, class_name),
    lambda: self._import_legacy(module_name, class_name)
]
```

**Configuration Management**: Singleton `ConfigManager` with JSON persistence in `config/rfu_config.json`. Use `get_config_manager()` for consistent access.

**Database Integration**: Optional SQLite tracking via `standalone_database_manager.py` with graceful fallback when unavailable.

## Directory Structure & Import Paths

```
src/
├── rfu/                    # Main application package
│   ├── main.py            # Entry point with QApplication
│   ├── hub.py             # Main hub interface
│   ├── config_manager.py  # Singleton configuration
│   └── core/              # Core system components
├── utilities/             # Tool modules by category
│   ├── file_management/   # FileFinderGUI, CatalogWindow, etc.
│   ├── file_operations/   # CopyMoveSyncDeleteWindow, etc.  
│   ├── analysis/          # SizeAnalyzerGUI, DuplicateFinderApp
│   ├── pdf_tools/         # Comprehensive PDF suite
│   ├── network/           # NetworkConnectivityGUI, etc.
│   └── security/          # EnAndDecryptGUI, SecureDeleteGUI
```

**Import Convention**: All tools use `src.utilities.{category}.{module}` paths. The main launcher handles path resolution automatically.

## Tool Integration Patterns

### Standard Tool Class Structure
```python
class ToolNameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # UI initialization
        
    def track_operation(self, operation_type):
        # Optional database tracking
```

### Tool Registration in main.py
Add to appropriate category tab:
```python
("Tool Display Name", "Tool description", self.open_tool_function)
```

Implement launcher method:
```python
def open_tool_function(self):
    self.launch_tool("Tool Name", "src.tools.category.module", "ToolNameGUI")
```

## PDF Tools Architecture

**Engine-Based Design**: PDF functionality uses specialized engines (`analysis_engine.py`, `conversion_engine.py`, etc.) with unified interfaces.

**Tool Discovery**: PDF tools use `PDFToolDiscovery` class for automatic registration and categorization:
```python
@dataclass
class ToolMetadata:
    name: str
    category: str
    supports_batch: bool
    dependencies: List[str]
```

**Integration Pattern**: Enhanced PDF widget (`EnhancedPDFToolsWidget`) provides tabbed interface with signal-based communication to main hub.

## Testing & Validation

**Test Structure**: Uses pytest with comprehensive markers (`@pytest.mark.gui`, `@pytest.mark.integration`, etc.).

**Tool Validation**: Before launching, tools go through validation pipeline:
```python
validation_result = self.validate_tool_before_launch(module_name, class_name)
if not validation_result["success"]:
    self._handle_import_failure(tool_name, module_name, class_name, last_error)
```

**Error Handling**: Multi-strategy error handling with specific guidance based on error types (import failures, instantiation errors, validation failures).

## Critical Development Patterns

### Database Operations
Always check `DATABASE_AVAILABLE` before database operations:
```python
if self.database_available:
    self.db_manager.execute_update(query, params)
```

### Security Integration
Security features use comprehensive menu system with emergency controls. All security operations log through `get_log_manager()`.

### Logging System
Use centralized logging via `log_manager.py`:
```python
from log_manager import get_log_manager
logger = get_log_manager().get_logger('ToolName')
```

## Common Development Tasks

**Adding New Tools**: 
1. Create tool class in appropriate `src/utilities/{category}/` directory
2. Follow `{ToolName}GUI` naming convention  
3. Add launcher method to `main.py`
4. Add to category tab in `init_ui()`

**Debugging Import Issues**: Use the automated tool corrector: `python scripts/maintenance/automated_tool_corrector.py`

**Configuration Changes**: Modify via `ConfigManager.set_setting(section, key, value)` - changes persist automatically.

## Integration Points

**Menu System**: Uses `MenuManager` with callback registration for comprehensive menu integration.

**Status Tracking**: All tool launches tracked via `track_tool_usage()` when database available.

**Cross-Platform**: Windows-focused but with Path() usage for cross-platform compatibility.

The codebase emphasizes **graceful fallbacks**, **comprehensive error handling**, and **modular tool integration** - maintain these patterns when extending functionality.
