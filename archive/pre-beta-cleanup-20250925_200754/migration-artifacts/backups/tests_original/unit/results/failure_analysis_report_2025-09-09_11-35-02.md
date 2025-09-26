# Failure Analysis Report - Phase 5

**Generated:** 2025-09-09 11:35:02  
**Failed/Blocked Tests:** 5  

## Failure Breakdown by Category

### Performance Resource (1 issues)

#### performance_failed
- **Stage:** performance
- **Status:** FAILED
- **Error:** The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_benchmark\logger.py:39: PytestBenchmarkWarning: Not saving anything, no benchmarks have been run!
  warner(PytestBenchmarkWarning(text))
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
ERROR: file or directory not found: tests/unit/test_utilities_*.py


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

### Security Compliance (1 issues)

#### security_failed
- **Stage:** security
- **Status:** FAILED
- **Error:** C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
ERROR: file or directory not found: tests/unit/test_security_*.py


- **Stack Trace:**
```
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The ev...
```

### Environment Configuration (3 issues)

#### core_modules_failed
- **Stage:** core_modules
- **Status:** FAILED
- **Error:** C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
ERROR: file or directory not found: tests/unit/test_core_*.py


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

#### integration_failed
- **Stage:** integration
- **Status:** FAILED
- **Error:** C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
ERROR: file or directory not found: tests/unit/test_integration_*.py


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

#### system_failed
- **Stage:** system
- **Status:** FAILED
- **Error:** C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
C:\Users\HP1\1_2\src\utilities\file_operations\__init__.py:33: UserWarning: Could not import rename: cannot import name 'RenameWindow' from 'src.tools.file_operations.rename.gui' (C:\Users\HP1\1_2\src\utilities\file_operations\rename\gui.py)
  warnings.warn(f"Could not import rename: {e}")
ERROR: file or directory not found: tests/system/


- **Stack Trace:**
```
C:\Users\HP1\AppData\Local\Programs\Python\Python313\Lib\site-packages\pytest_asyncio\plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid...
```

