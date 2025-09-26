# Migration Manager Refactoring Plan

## Overview
The `_get_pending_migrations` function in migration_manager.py has cognitive complexity of 26 (exceeds limit of 15). This document outlines the refactoring strategy to break it into smaller, more maintainable functions.

## Current Function Analysis
- **Function:** `_get_pending_migrations(target_version: Optional[str] = None) -> List[str]`
- **Lines:** 436-549 (114 lines)
- **Complexity:** 26
- **Issues:** Too many responsibilities, complex nested logic, extensive error handling

## Refactoring Strategy

### 1. Extract Validation Logic
**New Function:** `_validate_target_version(target_version: Optional[str]) -> Optional[str]`
- Validates target version parameter
- Returns cleaned target version or None
- Handles validation errors

### 2. Extract Applied Migrations Query
**New Function:** `_get_applied_migrations() -> Set[str]`
- Queries database for applied migrations
- Returns set of applied version strings
- Handles database errors

### 3. Extract Available Migrations Discovery
**New Function:** `_get_available_migrations() -> Dict[str, type]`
- Discovers available migration files
- Returns mapping of versions to migration classes
- Handles discovery errors

### 4. Extract Pending Logic
**New Function:** `_filter_pending_migrations(available: Dict[str, type], applied: Set[str], target: Optional[str]) -> List[str]`
- Filters available migrations against applied ones
- Handles target version logic
- Returns ordered list of pending migrations

### 5. Extract Chain Validation
**New Function:** `_validate_pending_chain(pending: List[str], available: Dict[str, type]) -> None`
- Validates migration chain integrity
- Throws validation errors if chain is broken
- Logs validation results

## Implementation Benefits

1. **Reduced Complexity:** Each function has single responsibility
2. **Better Testing:** Individual functions can be unit tested
3. **Improved Readability:** Clear separation of concerns
4. **Easier Maintenance:** Changes to validation logic isolated
5. **Reusability:** Helper functions can be reused elsewhere

## Refactored Function Structure

```python
def _get_pending_migrations(self, target_version: Optional[str] = None) -> List[str]:
    """
    Get list of pending migrations to execute.
    
    Args:
        target_version: Target version to migrate to (None for all pending)
        
    Returns:
        List of migration versions to execute in order
    """
    try:
        # Validate and clean target version
        target_version = self._validate_target_version(target_version)
        
        # Get applied and available migrations
        applied_versions = self._get_applied_migrations()
        available_migrations = self._get_available_migrations()
        
        # Filter pending migrations
        pending = self._filter_pending_migrations(
            available_migrations, applied_versions, target_version
        )
        
        # Validate migration chain
        if pending:
            self._validate_pending_chain(pending, available_migrations)
        
        # Log results and return
        self._log_pending_results(pending)
        return pending
        
    except (MigrationError, MigrationValidationError):
        raise
    except Exception as e:
        self.logger.error(f"Unexpected error while getting pending migrations: {e}")
        raise MigrationError(f"Unexpected error: {e}")
```

## Testing Strategy

1. **Unit Tests:** Create tests for each helper function
2. **Integration Tests:** Test complete _get_pending_migrations flow
3. **Error Testing:** Verify error handling in each component
4. **Performance Testing:** Ensure refactoring doesn't impact performance

## Risk Assessment

- **Low Risk:** Pure refactoring, no logic changes
- **Validation:** Extensive testing ensures identical behavior
- **Rollback:** Git allows easy reversion if issues arise

## Implementation Timeline

- **Phase 1:** Extract helper functions (30 min)
- **Phase 2:** Update main function (15 min)
- **Phase 3:** Add unit tests (45 min)
- **Phase 4:** Integration testing (30 min)

Total estimated time: 2 hours