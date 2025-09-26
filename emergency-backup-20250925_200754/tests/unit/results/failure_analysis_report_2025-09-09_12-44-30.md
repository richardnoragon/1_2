# Failure Analysis Report - Phase 5

**Generated:** 2025-09-09 12:44:30  
**Failed/Blocked Tests:** 5  

## Failure Breakdown by Category

### Import Dependency (5 issues)

#### core_modules_failed
- **Stage:** core_modules
- **Status:** FAILED
- **Error:**   warnings.warn(f"Could not import file_finder: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:28: UserWarning: Could not import organize: No module named 'core.error_handler'
  warnings.warn(f"Could not import organize: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:38: UserWarning: Could not import file_touch: No module named 'core.error_handler'
  warnings.warn(f"Could not import file_touch: {e}")
ERROR: file or directory not found: tests/unit/test_core_*.py


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

#### integration_failed
- **Stage:** integration
- **Status:** FAILED
- **Error:**   warnings.warn(f"Could not import file_finder: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:28: UserWarning: Could not import organize: No module named 'core.error_handler'
  warnings.warn(f"Could not import organize: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:38: UserWarning: Could not import file_touch: No module named 'core.error_handler'
  warnings.warn(f"Could not import file_touch: {e}")
ERROR: file or directory not found: tests/unit/test_integration_*.py


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

#### security_failed
- **Stage:** security
- **Status:** FAILED
- **Error:**   warnings.warn(f"Could not import rename: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:38: UserWarning: Could not import file_touch: No module named 'core.error_handler'
  warnings.warn(f"Could not import file_touch: {e}")
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
ERROR: file or directory not found: tests/unit/test_security_*.py


- **Stack Trace:**
```
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:23: UserWarning: Could not import file_finder: No module named 'core.error_handler'
  warnings.warn(f"Could not import file_finder: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:28: UserWarning: Could not import organize: No module named 'core.error_handler'
  warnings.warn(f"Could not import organize: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot impo...
```

#### performance_failed
- **Stage:** performance
- **Status:** FAILED
- **Error:**   warnings.warn(f"Could not import file_finder: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:28: UserWarning: Could not import organize: No module named 'core.error_handler'
  warnings.warn(f"Could not import organize: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:38: UserWarning: Could not import file_touch: No module named 'core.error_handler'
  warnings.warn(f"Could not import file_touch: {e}")
ERROR: file or directory not found: tests/unit/test_utilities_*.py


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

#### system_failed
- **Stage:** system
- **Status:** FAILED
- **Error:**   warnings.warn(f"Could not import file_finder: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:28: UserWarning: Could not import organize: No module named 'core.error_handler'
  warnings.warn(f"Could not import organize: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:38: UserWarning: Could not import file_touch: No module named 'core.error_handler'
  warnings.warn(f"Could not import file_touch: {e}")
ERROR: file or directory not found: tests/system/


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

