# CMSD Migration Implementation Guide

## 🚀 Ready-to-Execute Implementation Guide

This document provides step-by-step implementation instructions for executing the CMSD migration to file_utilities_2. All planning, validation procedures, and rollback mechanisms are now in place.

---

## 📋 Pre-Implementation Checklist

### Prerequisites Verification
- [ ] Python 3.7+ installed and configured
- [ ] PyQt5 properly installed and functional
- [ ] file_utilities_2 package structure exists
- [ ] Current CMSD functionality verified working
- [ ] Backup procedures tested and validated
- [ ] Development environment prepared
- [ ] All planning documents reviewed and approved

### Required Tools and Dependencies
```bash
# Verify Python environment
python3 --version
pip3 list | grep PyQt5

# Verify file_utilities_2 structure
ls -la file_utilities_2/
ls -la file_utilities_2/core/
ls -la file_utilities_2/gui/
ls -la file_utilities_2/integration/

# Test current CMSD
python3 -c "import cmsd; print('CMSD import successful')"
```

---

## 🎯 Implementation Execution Plan

### Phase 1: Pre-Migration Analysis & Backup
**Estimated Time:** 2-3 hours  
**Risk Level:** Low  
**Dependencies:** None

#### Step 1.1: Create Backup Structure
```bash
# Create backup directory with timestamp
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="backup/cmsd_migration/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "Backup directory created: $BACKUP_DIR"
```

#### Step 1.2: Backup Original Files
```bash
# Backup main files
cp cmsd.py "$BACKUP_DIR/"
cp cmsd.ui "$BACKUP_DIR/"

# Backup any related files that might be modified
if [ -f "file_utilities_2/__init__.py" ]; then
    cp file_utilities_2/__init__.py "$BACKUP_DIR/__init__.py.backup"
fi

if [ -f "file_utilities_2/integration/hub_connector.py" ]; then
    cp file_utilities_2/integration/hub_connector.py "$BACKUP_DIR/hub_connector.py.backup"
fi
```

#### Step 1.3: Create Backup Manifest
```bash
# Create backup manifest
cat > "$BACKUP_DIR/backup_manifest.txt" << EOF
CMSD Migration Backup Manifest
Created: $(date)
Backup Directory: $BACKUP_DIR

Original Files:
- cmsd.py ($(stat -c%s cmsd.py) bytes)
- cmsd.ui ($(stat -c%s cmsd.ui) bytes)

Checksums:
- cmsd.py: $(md5sum cmsd.py | cut -d' ' -f1)
- cmsd.ui: $(md5sum cmsd.ui | cut -d' ' -f1)

Migration Plan Version: 1.0
Rollback Procedures: Available
EOF

echo "Backup manifest created"
```

#### Step 1.4: Verify Backup Integrity
```bash
# Verify backup files
python3 << EOF
import os
import hashlib

backup_dir = "$BACKUP_DIR"
original_files = ["cmsd.py", "cmsd.ui"]

for file in original_files:
    original_path = file
    backup_path = os.path.join(backup_dir, file)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup missing: {file}")
        exit(1)
    
    # Compare file sizes
    orig_size = os.path.getsize(original_path)
    backup_size = os.path.getsize(backup_path)
    
    if orig_size != backup_size:
        print(f"❌ Size mismatch for {file}: {orig_size} vs {backup_size}")
        exit(1)
    
    print(f"✅ Backup verified: {file}")

print("🎉 All backups verified successfully")
EOF
```

### Phase 2: Dependency Analysis & Mapping
**Estimated Time:** 1-2 hours  
**Risk Level:** Low  
**Dependencies:** Phase 1 complete

#### Step 2.1: Analyze Current Dependencies
```python
# Create dependency analysis script
cat > analyze_dependencies.py << 'EOF'
#!/usr/bin/env python3
"""Analyze CMSD dependencies for migration planning."""

import ast
import os
from pathlib import Path

def analyze_imports(file_path):
    """Analyze imports in a Python file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    
    return imports

def main():
    print("🔍 Analyzing CMSD Dependencies...")
    
    # Analyze cmsd.py
    imports = analyze_imports("cmsd.py")
    
    print("\nCurrent Imports:")
    for imp in sorted(imports):
        print(f"  - {imp}")
    
    # Categorize imports
    pyqt5_imports = [imp for imp in imports if 'PyQt5' in imp]
    legacy_imports = [imp for imp in imports if 'gui.common' in imp]
    standard_imports = [imp for imp in imports if imp in ['os', 'sys', 'shutil', 'typing']]
    
    print(f"\nPyQt5 Imports ({len(pyqt5_imports)}):")
    for imp in pyqt5_imports:
        print(f"  ✅ {imp} (Compatible)")
    
    print(f"\nLegacy Imports ({len(legacy_imports)}):")
    for imp in legacy_imports:
        print(f"  ⚠️ {imp} (Needs Migration)")
    
    print(f"\nStandard Library ({len(standard_imports)}):")
    for imp in standard_imports:
        print(f"  ✅ {imp} (No Change Needed)")

if __name__ == "__main__":
    main()
EOF

python3 analyze_dependencies.py
```

#### Step 2.2: Create Migration Mapping
```python
# Create migration mapping
cat > migration_mapping.py << 'EOF'
#!/usr/bin/env python3
"""Create migration mapping for CMSD dependencies."""

MIGRATION_MAP = {
    # Legacy to Modern Mappings
    'gui.common.base_window.BaseWindow': 'file_utilities_2.gui.standard_window.StandardWindow',
    'gui.common.dialogs.get_existing_directory': 'StandardWindow.get_directory_path()',
    'gui.common.dialogs.show_error_dialog': 'StandardWindow.show_error_dialog()',
    
    # PyQt5 - No changes needed
    'PyQt5.QtGui.QStandardItemModel': 'PyQt5.QtGui.QStandardItemModel',
    'PyQt5.QtGui.QStandardItem': 'PyQt5.QtGui.QStandardItem',
    'PyQt5.QtWidgets.QApplication': 'PyQt5.QtWidgets.QApplication',
    'PyQt5.uic': 'PyQt5.uic',
    
    # Standard library - No changes needed
    'os': 'os',
    'sys': 'sys',
    'shutil': 'shutil',
    'typing': 'typing'
}

def print_migration_map():
    print("📋 CMSD Migration Mapping:")
    print("=" * 50)
    
    for old, new in MIGRATION_MAP.items():
        if old == new:
            print(f"✅ {old} → No change needed")
        else:
            print(f"🔄 {old} → {new}")

if __name__ == "__main__":
    print_migration_map()
EOF

python3 migration_mapping.py
```

### Phase 3: Directory Structure Planning
**Estimated Time:** 1-2 hours  
**Risk Level:** Low  
**Dependencies:** Phase 2 complete

#### Step 3.1: Create Directory Structure
```bash
# Create required directories
mkdir -p file_utilities_2/core
mkdir -p file_utilities_2/gui
mkdir -p file_utilities_2/integration
mkdir -p file_utilities_2/tests

echo "Directory structure created"
```

#### Step 3.2: Plan File Organization
```bash
# Document planned file structure
cat > planned_structure.txt << EOF
CMSD Migration - Planned File Structure
======================================

Target Structure:
file_utilities_2/
├── core/
│   └── cmsd_logic.py          # Business logic extracted from cmsd.py
├── gui/
│   ├── cmsd_gui.py           # GUI implementation using StandardWindow
│   └── cmsd.ui               # Migrated UI file
├── integration/
│   └── cmsd_connector.py     # Hub integration
└── tests/
    ├── test_cmsd_core.py     # Core logic tests
    ├── test_cmsd_gui.py      # GUI tests
    └── test_cmsd_integration.py # Integration tests

Files to be removed from root:
- cmsd.py (after successful migration)
- cmsd.ui (after successful migration)
EOF

cat planned_structure.txt
```

### Phase 4: Core Logic Migration
**Estimated Time:** 4-6 hours  
**Risk Level:** Medium  
**Dependencies:** Phase 3 complete

#### Step 4.1: Create Core Logic Module
```python
# Create the core logic file
cat > file_utilities_2/core/cmsd_logic.py << 'EOF'
"""
CMSD Core Logic Module

This module contains the business logic for the Content Management System Directory tool.
Extracted from the original cmsd.py for better separation of concerns.
"""

import os
import shutil
from typing import List, Optional, Tuple, NamedTuple
from pathlib import Path


class DirectoryComparison(NamedTuple):
    """Results of directory comparison."""
    only_left: List[str]
    only_right: List[str]
    common: List[str]
    total_left: int
    total_right: int


class OperationResult(NamedTuple):
    """Result of file operation."""
    success: bool
    processed_files: List[str]
    failed_files: List[Tuple[str, str]]  # (file, error)
    total_bytes: int


class CMSDLogic:
    """Core business logic for CMSD operations."""
    
    def __init__(self):
        """Initialize CMSD logic."""
        self.left_directory: str = "."
        self.right_directory: str = "."
        self.selected_files: List[str] = []
    
    def load_directory_contents(self, directory: str) -> List[str]:
        """Load files from a directory.
        
        Args:
            directory: Path to directory to scan
            
        Returns:
            List of file paths in the directory
        """
        files = []
        if not os.path.isdir(directory):
            return files
        
        try:
            for item in sorted(os.listdir(directory)):
                full_path = os.path.join(directory, item)
                if os.path.isfile(full_path):
                    files.append(full_path)
        except OSError:
            # Handle permission errors, etc.
            pass
        
        return files
    
    def compare_directories(self) -> DirectoryComparison:
        """Compare contents of left and right directories.
        
        Returns:
            DirectoryComparison with analysis results
        """
        left_files = set(os.path.basename(f) for f in self.get_left_files())
        right_files = set(os.path.basename(f) for f in self.get_right_files())
        
        only_left = sorted(left_files - right_files)
        only_right = sorted(right_files - left_files)
        common = sorted(left_files & right_files)
        
        return DirectoryComparison(
            only_left=only_left,
            only_right=only_right,
            common=common,
            total_left=len(left_files),
            total_right=len(right_files)
        )
    
    def get_left_files(self) -> List[str]:
        """Get files in left directory."""
        return self.load_directory_contents(self.left_directory)
    
    def get_right_files(self) -> List[str]:
        """Get files in right directory."""
        return self.load_directory_contents(self.right_directory)
    
    def add_to_selection(self, file_path: str) -> None:
        """Add file to selection."""
        if file_path not in self.selected_files:
            self.selected_files.append(file_path)
    
    def remove_from_selection(self, file_path: str) -> None:
        """Remove file from selection."""
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
    
    def clear_selection(self) -> None:
        """Clear all selected files."""
        self.selected_files.clear()
    
    def get_selected_files(self) -> List[str]:
        """Get copy of selected files list."""
        return self.selected_files.copy()
    
    def copy_files(self, source_files: List[str], destination_dir: str) -> OperationResult:
        """Copy files to destination directory.
        
        Args:
            source_files: List of source file paths
            destination_dir: Destination directory path
            
        Returns:
            OperationResult with operation details
        """
        processed = []
        failed = []
        total_bytes = 0
        
        if not os.path.isdir(destination_dir):
            return OperationResult(False, [], [("", "Destination directory does not exist")], 0)
        
        for file_path in source_files:
            if not os.path.isfile(file_path):
                failed.append((file_path, "Source file does not exist"))
                continue
            
            try:
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(destination_dir, file_name)
                
                # Get file size before copying
                file_size = os.path.getsize(file_path)
                
                shutil.copy2(file_path, dest_path)
                processed.append(file_path)
                total_bytes += file_size
                
            except OSError as e:
                failed.append((file_path, str(e)))
        
        success = len(failed) == 0
        return OperationResult(success, processed, failed, total_bytes)
    
    def delete_files(self, files: List[str]) -> OperationResult:
        """Delete specified files.
        
        Args:
            files: List of file paths to delete
            
        Returns:
            OperationResult with operation details
        """
        processed = []
        failed = []
        total_bytes = 0
        
        for file_path in files:
            if not os.path.isfile(file_path):
                failed.append((file_path, "File does not exist"))
                continue
            
            try:
                # Get file size before deletion
                file_size = os.path.getsize(file_path)
                
                os.remove(file_path)
                processed.append(file_path)
                total_bytes += file_size
                
            except OSError as e:
                failed.append((file_path, str(e)))
        
        success = len(failed) == 0
        return OperationResult(success, processed, failed, total_bytes)
EOF

echo "✅ Core logic module created"
```

#### Step 4.2: Test Core Logic
```python
# Test the core logic
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from file_utilities_2.core.cmsd_logic import CMSDLogic, DirectoryComparison, OperationResult
    
    # Test basic instantiation
    cmsd = CMSDLogic()
    print("✅ CMSDLogic instantiation successful")
    
    # Test directory loading
    files = cmsd.load_directory_contents(".")
    print(f"✅ Directory loading successful ({len(files)} files)")
    
    # Test comparison
    comparison = cmsd.compare_directories()
    print(f"✅ Directory comparison successful")
    
    print("🎉 Core logic tests passed")
    
except Exception as e:
    print(f"❌ Core logic test failed: {e}")
    sys.exit(1)
EOF
```

### Phase 5: GUI Migration & PyQt5 Conversion
**Estimated Time:** 6-8 hours  
**Risk Level:** Medium  
**Dependencies:** Phase 4 complete

#### Step 5.1: Create GUI Module
```python
# Create the GUI module
cat > file_utilities_2/gui/cmsd_gui.py << 'EOF'
"""
CMSD GUI Module

Modern PyQt5 GUI implementation using StandardWindow architecture.
Migrated from original cmsd.py with enhanced features and consistency.
"""

import os
import sys
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic

from file_utilities_2.gui.standard_window import StandardWindow
from file_utilities_2.gui.themes import ThemeManager
from file_utilities_2.core.cmsd_logic import CMSDLogic


class CMSDWindow(StandardWindow):
    """Content Management System Directory window."""
    
    def __init__(self):
        """Initialize CMSD window."""
        super().__init__(
            title="Content Management System Directory",
            icon_path=self._get_cmsd_icon()
        )
        
        # Initialize core logic
        self.cmsd_logic = CMSDLogic()
        
        # Initialize models
        self.left_model = QStandardItemModel()
        self.right_model = QStandardItemModel()
        
        # Setup UI
        self._setup_cmsd_ui()
        self._connect_signals()
        self._apply_cmsd_theme()
        
        # Load initial state
        self._load_initial_directories()
    
    def _get_cmsd_icon(self) -> str:
        """Get CMSD icon path."""
        return os.path.join(os.path.dirname(__file__), '..', 'icons', 'cmsd.png')
    
    def _setup_cmsd_ui(self) -> None:
        """Setup CMSD-specific UI components."""
        try:
            # Load UI file
            ui_path = os.path.join(os.path.dirname(__file__), 'cmsd.ui')
            uic.loadUi(ui_path, self)
            
            # Setup list views
            if hasattr(self, 'listView'):
                self.listView.setModel(self.left_model)
            if hasattr(self, 'selectView'):
                self.selectView.setModel(self.right_model)
                
        except Exception as e:
            self.show_error_dialog("UI Setup Error", f"Failed to load UI: {e}")
    
    def _connect_signals(self) -> None:
        """Connect UI signals to slots."""
        # Menu actions
        if hasattr(self, 'actionOpenLeft'):
            self.actionOpenLeft.triggered.connect(self.load_directory_left)
        if hasattr(self, 'actionOpenRight'):
            self.actionOpenRight.triggered.connect(self.load_directory_right)
        if hasattr(self, 'actionexit'):
            self.actionexit.triggered.connect(self.close)
        
        # Button connections would go here
        # if hasattr(self, 'selectButton'):
        #     self.selectButton.clicked.connect(self.select_files)
    
    def _apply_cmsd_theme(self) -> None:
        """Apply CMSD-specific theming."""
        ThemeManager.apply_utility_window_theme(self)
        
        # Additional CMSD-specific styling
        self.setStyleSheet(self.styleSheet() + """
            QListView {
                border: 1px solid #ccc;
                background-color: white;
                selection-background-color: #3498db;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                margin: 10px 0px;
                padding-top: 5px;
            }
        """)
    
    def _load_initial_directories(self) -> None:
        """Load initial directories."""
        self.load_directory_left(".")
        self.load_directory_right(".")
    
    def load_directory_left(self, directory: Optional[str] = None) -> None:
        """Load left directory."""
        if directory is None:
            directory = self.get_directory_path("Select Left Directory")
        
        if directory and os.path.isdir(directory):
            self.cmsd_logic.left_directory = directory
            self._update_left_view()
            self.show_status_message(f"Left directory: {directory}")
    
    def load_directory_right(self, directory: Optional[str] = None) -> None:
        """Load right directory."""
        if directory is None:
            directory = self.get_directory_path("Select Right Directory")
        
        if directory and os.path.isdir(directory):
            self.cmsd_logic.right_directory = directory
            self._update_right_view()
            self.show_status_message(f"Right directory: {directory}")
    
    def _update_left_view(self) -> None:
        """Update left directory view."""
        self.left_model.clear()
        files = self.cmsd_logic.get_left_files()
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            item = QStandardItem(file_name)
            item.setData(file_path)
            self.left_model.appendRow(item)
    
    def _update_right_view(self) -> None:
        """Update right directory view."""
        self.right_model.clear()
        files = self.cmsd_logic.get_right_files()
        
        for file_path in files:
            file_name = os.path.basename(file_path)
            item = QStandardItem(file_name)
            item.setData(file_path)
            self.right_model.appendRow(item)
    
    def _update_directory_views(self) -> None:
        """Update both directory views."""
        self._update_left_view()
        self._update_right_view()


def main():
    """Main entry point for standalone execution."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    window = CMSDWindow()
    window.show()
    
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
EOF

echo "✅ GUI module created"
```

#### Step 5.2: Test GUI Module
```python
# Test GUI creation (without showing)
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from PyQt5.QtWidgets import QApplication
    from file_utilities_2.gui.cmsd_gui import CMSDWindow
    
    # Create application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Test window creation
    window = CMSDWindow()
    print("✅ CMSDWindow creation successful")
    
    # Test basic properties
    if window.windowTitle():
        print(f"✅ Window title set: {window.windowTitle()}")
    
    # Close window
    window.close()
    print("🎉 GUI module tests passed")
    
except Exception as e:
    print(f"❌ GUI module test failed: {e}")
    sys.exit(1)
EOF
```

### Phase 6: UI File Migration & Standardization
**Estimated Time:** 2-3 hours  
**Risk Level:** Low  
**Dependencies:** Phase 5 complete

#### Step 6.1: Copy and Migrate UI File
```bash
# Copy UI file to new location
cp cmsd.ui file_utilities_2/gui/cmsd.ui

echo "✅ UI file copied to new location"
```

#### Step 6.2: Validate UI File Loading
```python
# Test UI file loading
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow
    from PyQt5 import uic
    import os
    
    # Create application
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Test UI loading
    ui_path = "file_utilities_2/gui/cmsd.ui"
    if not os.path.exists(ui_path):
        print(f"❌ UI file not found: {ui_path}")
        sys.exit(1)
    
    # Load UI into a test window
    test_window = QMainWindow()
    uic.loadUi(ui_path, test_window)
    
    print("✅ UI file loads successfully")
    
    # Test for expected components
    expected_components = ['listView', 'selectView', 'menubar']
    for component in expected_components:
        if hasattr(test_window, component):
            print(f"✅ Component found: {component}")
        else:
            print(f"⚠️ Component missing: {component}")
    
    test_window.close()
    print("🎉 UI file validation passed")
    
except Exception as e:
    print(f"❌ UI file validation failed: {e}")
    sys.exit(1)
EOF
```

### Phase 7: Hub Integration Implementation
**Estimated Time:** 3-4 hours  
**Risk Level:** Medium  
**Dependencies:** Phase 6 complete

#### Step 7.1: Create Hub Connector
```python
# Create hub connector
cat > file_utilities_2/integration/cmsd_connector.py << 'EOF'
"""
CMSD Hub Connector

Integration module for connecting CMSD with the RFU Hub system.
Provides menu registration and utility launch capabilities.
"""

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from file_utilities_2.gui.cmsd_gui import CMSDWindow


class CMSDHubConnector:
    """Hub integration connector for CMSD utility."""
    
    @staticmethod
    def get_menu_info() -> Dict[str, str]:
        """Get menu information for RFU Hub registration.
        
        Returns:
            Dictionary containing menu configuration
        """
        return {
            'name': 'Content Management System Directory',
            'description': 'Compare and manage files between two directories',
            'category': 'File Management',
            'icon': 'cmsd.png',
            'shortcut': 'Ctrl+Shift+C',
            'tooltip': 'Launch CMSD for directory comparison and file management',
            'version': '2.0.0'
        }
    
    @staticmethod
    def launch_utility(parent=None) -> 'CMSDWindow':
        """Launch CMSD utility from hub.
        
        Args:
            parent: Parent window (optional)
            
        Returns:
            CMSDWindow instance
        """
        from file_utilities_2.gui.cmsd_gui import CMSDWindow
        
        window = CMSDWindow()
        if parent:
            window.setParent(parent)
        
        window.show()
        return window
    
    @staticmethod
    def get_utility_info() -> Dict[str, any]:
        """Get detailed utility information.
        
        Returns:
            Dictionary containing utility details
        """
        return {
            'id': 'cmsd',
            'name': 'Content Management System Directory',
            'version': '2.0.0',
            'author': 'File Utilities Team',
            'last_updated': '2025-07-28',
            'description': 'A dual-pane directory comparison and file management tool',
            'features': [
                'Dual directory comparison',
                'File selection and management',
                'Batch file operations',
                'Directory synchronization tools',
                'Modern PyQt5 interface',
                'Integrated with RFU Hub'
            ],
            'requirements': [
                'PyQt5',
                'Python 3.7+'
            ],
            'category': 'File Management',
            'tags': ['directory', 'comparison', 'files', 'management', 'sync']
        }
    
    @staticmethod
    def is_available() -> bool:
        """Check if CMSD utility is available.
        
        Returns:
            True if utility can be launched
        """
        try:
            from file_utilities_2.gui.cmsd_gui import CMSDWindow
            from file_utilities_2.core.cmsd_logic import CMSDLogic
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_status() -> Dict[str, any]:
        """Get current utility status.
        
        Returns:
            Dictionary containing status information
        """
        return {
            'available': CMSDHubConnector.is_available(),
            'version': '2.0.0',
            'last_check': None,  # Could be implemented for health checks
            'dependencies_ok': True,
            'config_valid': True
        }
EOF

echo "✅ Hub connector created"
```

#### Step 7.2: Test Hub Integration
```python
# Test hub connector
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from file_utilities_2.integration.cmsd_connector import CMSDHubConnector
    
    # Test menu info
    menu_info = CMSDHubConnector.get_menu_info()
    required_keys = ['name', 'description', 'category', 'icon']
    
    for key in required_keys:
        if key in menu_info:
            print(f"✅ Menu info has {key}: {menu_info[key]}")
        else:
            print(f"❌ Missing menu info key: {key}")
            sys.exit(1)
    
    # Test utility info
    utility_info = CMSDHubConnector.get_utility_info()
    if 'version' in utility_info:
        print(f"✅ Utility version: {utility_info['version']}")
    
    # Test availability
    available = CMSDHubConnector.is_available()
    print(f"✅ Utility available: {available}")
    
    print("🎉 Hub integration tests passed")
    
except Exception as e:
    print(f"❌ Hub integration test failed: {e}")
    sys.exit(1)
EOF
```

### Phase 8: Import Path Updates & Module Initialization
**Estimated Time:** 1-2 hours  
**Risk Level:** Low  
**Dependencies:** Phase 7 complete

#### Step 8.1: Update Package Initialization
```python
# Update file_utilities_2/__init__.py
python3 << 'EOF'
import os

# Read current __init__.py
init_file = "file_utilities_2/__init__.py"
with open(init_file, 'r') as f:
    content = f.read()

# Add CMSD imports
cmsd_imports = '''
# Import CMSD functionality
from .core.cmsd_logic import CMSDLogic
from .gui.cmsd_gui import CMSDWindow
from .integration.cmsd_connector import CMSDHubConnector
'''

# Add to __all__ list
cm