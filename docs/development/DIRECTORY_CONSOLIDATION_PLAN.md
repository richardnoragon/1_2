# Directory Consolidation Plan: RFU Tools → Utilities Migration

## Objective

Consolidate redundant directories by migrating from `src/rfu/tools/` to `src/utilities/` while maintaining full functionality.

## Analysis Summary

### ✅ Ready to Migrate (Utilities has superior/complete versions):

1. **File Catalog**: `tools/file_management/catalog.py` → `utilities/file_operations/catalog/catalog.py`

   - Utilities: 468 lines, comprehensive functionality
   - Tools: Simplified version
   - **Action**: Update imports to utilities version

2. **File Organization**: `tools/file_management/organize.py` → `utilities/file_operations/organize/organize.py`

   - Utilities: Enhanced with UI file
   - **Action**: Update imports to utilities version

3. **Office Metadata**: `tools/metadata/office_meta_data_editor.py` → `utilities/metadata/office_meta_data_editor.py`
   - Both have GUI implementations
   - **Action**: Update imports to utilities version

### 🔄 Needs GUI Wrapper Creation:

1. **File Splitter**: `tools/file_operations/file_splitter_joiner.py` vs `utilities/file_operations/file_splitter_*.py`

   - Tools: 192-line GUI
   - Utilities: Logic components only (829 lines of enhanced logic)
   - **Action**: Create GUI wrapper that uses utilities logic

2. **Copy/Move/Sync/Delete**: `file_utilities_2/gui/cmsd_gui.py` + `file_utilities_2/core/cmsd_logic.py`

   - GUI now lives in the file utilities package
   - Core logic remains in `cmsd_logic`
   - **Action**: Update remaining imports to target the new package structure

3. **Image Metadata**: `tools/metadata/edit_image_metadata.py` vs `utilities/metadata/image_metadata_logic.py`
   - Tools: 1186-line comprehensive GUI
   - Utilities: Logic only
   - **Action**: Migrate GUI to utilities structure

### ❌ Tools-Only (No utilities equivalent):

1. **Rename Tool**: `tools/file_operations/rename/rename.py`

   - **Action**: Migrate entire component to utilities structure

2. **File Finder**: Both exist, but need to compare functionality
   - Tools: 395 lines (simplified)
   - Utilities: 712 lines (comprehensive)
   - **Action**: Use utilities version

## Implementation Plan

### Phase 1: Direct Import Updates (Low Risk)

- [x] Update catalog imports: `tools/file_management/catalog` → `utilities/file_operations/catalog`
- [x] Update organize imports: `tools/file_management/organize` → `utilities/file_operations/organize`
- [x] Update office metadata imports: `tools/metadata/office_meta_data_editor` → `utilities/metadata/office_meta_data_editor`

### Phase 2: Create GUI Wrappers (Medium Risk)

- [ ] Create `utilities/file_operations/file_splitter/gui.py` wrapper for file_splitter_logic
- [x] Adopt `file_utilities_2/gui/cmsd_gui.py` wrapper for CMSD logic
- [ ] Migrate image metadata GUI to utilities structure

### Phase 3: Migrate Tools-Only Components (Medium Risk)

- [ ] Move `tools/file_management/rename.py` → `tools/file_operations/rename/rename.py`
- [ ] Update all imports

### Phase 4: Import Path Fixes (High Risk)

- [ ] Fix import path issues in utilities modules
- [ ] Ensure all modules can be imported correctly
- [ ] Test all functionality

### Phase 5: Cleanup (Low Risk)

- [ ] Remove obsolete `src/rfu/tools/` directory
- [ ] Update documentation
- [ ] Run comprehensive tests

## Files Requiring Import Updates

### Primary Files:

- `src/rfu/simple_hub.py` - Main hub with multiple tool imports
- `enhanced_tools_demo.py`
- `test_menu_integration.py`
- `test_file_operations_fix.py`
- Various test files in `tests/` directory

### Import Pattern Changes:

```python
# OLD
from rfu.tools.file_management.catalog import CatalogWindow
from rfu.tools.file_management.organize import OrganizeWindow
from src.rfu.tools.metadata.office_meta_data_editor import OfficeMetaDataEditorGUI

# NEW
from src.tools.file_management.catalog.catalog import CatalogWindow
from src.tools.file_management.organizer.organize import OrganizeWindow
from src.tools.metadata.office_metadata.office_meta_data_editor import OfficeMetaDataEditorGUI
```

## Risk Assessment

- **Low Risk**: Direct import updates for fully migrated components
- **Medium Risk**: Creating GUI wrappers and component migration
- **High Risk**: Import path resolution across the application

## Success Criteria

1. All functionality preserved
2. No broken imports
3. Applications launch and function correctly
4. Reduced code duplication
5. Cleaner directory structure
