# Browser Detector Enhanced Unit Test Summary

## Test Execution Details
- **Execution Date**: 2025-08-30 22:09:21
- **Test Target**: browser_detector.py
- **Test File**: test_browser_detector_enhanced_2025-08-30.py
- **Return Code**: 1
- **Status**: FAILED

## Test Output
### STDOUT
```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-8.4.1, pluggy-1.6.0 -- C:\Users\richardi\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
metadata: {'Python': '3.13.2', 'Platform': 'Windows-11-10.0.26100-SP0', 'Packages': {'pytest': '8.4.1', 'pluggy': '1.6.0'}, 'Plugins': {'benchmark': '5.1.0', 'cov': '6.2.1', 'html': '4.1.1', 'json-report': '1.5.0', 'metadata': '3.1.1', 'mock': '3.14.1', 'qt': '4.5.0', 'timeout': '2.4.0', 'xdist': '3.8.0'}}
PyQt5 5.15.11 -- Qt runtime 5.15.2 -- Qt compiled 5.15.2
rootdir: C:\Users\richardi\1_2\tests\unit
configfile: pytest_browser_detector_enhanced_2025-08-30.ini
plugins: benchmark-5.1.0, cov-6.2.1, html-4.1.1, json-report-1.5.0, metadata-3.1.1, mock-3.14.1, qt-4.5.0, timeout-2.4.0, xdist-3.8.0
collecting ... collected 29 items

tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_init_basic PASSED: test_init_basic
PASSED [  3%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_init_with_platform_mock PASSED: test_init_with_platform_mock
PASSED [  6%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_detect_installed_browsers_first_call_success PASSED: test_detect_installed_browsers_first_call_success
PASSED [ 10%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_detect_installed_browsers_cached_result PASSED: test_detect_installed_browsers_cached_result
PASSED [ 13%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_installed_windows_platform PASSED: test_is_browser_installed_windows_platform
PASSED [ 17%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_installed_macos_platform FAILED: test_is_browser_installed_macos_platform
FAILED [ 20%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_installed_linux_platform FAILED: test_is_browser_installed_linux_platform
FAILED [ 24%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_installed_unknown_platform PASSED: test_is_browser_installed_unknown_platform
PASSED [ 27%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_windows_browser_chrome_exists PASSED: test_check_windows_browser_chrome_exists
PASSED [ 31%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_windows_browser_firefox_exists PASSED: test_check_windows_browser_firefox_exists
PASSED [ 34%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_windows_browser_edge_exists PASSED: test_check_windows_browser_edge_exists
PASSED [ 37%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_windows_browser_no_appdata_directories PASSED: test_check_windows_browser_no_appdata_directories
PASSED [ 41%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_macos_browser_chrome_app_directory PASSED: test_check_macos_browser_chrome_app_directory
PASSED [ 44%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_macos_browser_safari_exists PASSED: test_check_macos_browser_safari_exists
PASSED [ 48%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_linux_browser_chrome_config_directory PASSED: test_check_linux_browser_chrome_config_directory
PASSED [ 51%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_command_exists_found PASSED: test_check_command_exists_found
PASSED [ 55%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_check_command_exists_not_found PASSED: test_check_command_exists_not_found
PASSED [ 58%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_get_running_browsers_with_running_processes FAILED: test_get_running_browsers_with_running_processes
FAILED [ 62%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_running_positive_case PASSED: test_is_browser_running_positive_case
PASSED [ 65%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_running_negative_case PASSED: test_is_browser_running_negative_case
PASSED [ 68%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_close_browser_not_running PASSED: test_close_browser_not_running
PASSED [ 72%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_get_browser_data_paths_new_browser PASSED: test_get_browser_data_paths_new_browser
PASSED [ 75%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_get_browser_profile_paths_with_profiles PASSED: test_get_browser_profile_paths_with_profiles
PASSED [ 79%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_validate_browser_access_file_accessible PASSED: test_validate_browser_access_file_accessible
PASSED [ 82%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_get_browser_info_comprehensive PASSED: test_get_browser_info_comprehensive
PASSED [ 86%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_refresh_detection_clears_cache PASSED: test_refresh_detection_clears_cache
PASSED [ 89%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_edge_case_empty_browser_name PASSED: test_edge_case_empty_browser_name
PASSED [ 93%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_detect_installed_browsers_empty_result PASSED: test_detect_installed_browsers_empty_result
PASSED [ 96%]
tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_module_imports_availability PASSED: test_module_imports_availability
PASSED [100%]
Test summary saved to: result_system_cleanup_test_summary_2025-08-28.json
Total tests executed: 29
Session exit status: 1


================================== FAILURES ===================================
____ TestBrowserDetectorEnhanced.test_is_browser_installed_macos_platform _____
..\AppData\Local\Programs\Python\Python313\Lib\unittest\mock.py:988: in assert_called_once_with
    raise AssertionError(msg)
E   AssertionError: Expected '_check_macos_browser' to be called once. Called 0 times.

During handling of the above exception, another exception occurred:
tests\unit\test_browser_detector_enhanced_2025-08-30.py:120: in test_is_browser_installed_macos_platform
    mock_check_macos.assert_called_once_with("safari")
E   AssertionError: Expected '_check_macos_browser' to be called once. Called 0 times.
---------------------------- Captured stdout setup ----------------------------

Starting test: test_is_browser_installed_macos_platform
-------------------------- Captured stdout teardown ---------------------------
Completed test: test_is_browser_installed_macos_platform
____ TestBrowserDetectorEnhanced.test_is_browser_installed_linux_platform _____
tests\unit\test_browser_detector_enhanced_2025-08-30.py:132: in test_is_browser_installed_linux_platform
    assert result is True
E   assert False is True
---------------------------- Captured stdout setup ----------------------------

Starting test: test_is_browser_installed_linux_platform
-------------------------- Captured stdout teardown ---------------------------
Completed test: test_is_browser_installed_linux_platform
_ TestBrowserDetectorEnhanced.test_get_running_browsers_with_running_processes _
tests\unit\test_browser_detector_enhanced_2025-08-30.py:287: in test_get_running_browsers_with_running_processes
    assert result == ["chrome", "firefox"]
E   AssertionError: assert ['chrome'] == ['chrome', 'firefox']
E     
E     Right contains one more item: 'firefox'
E     
E     Full diff:
E       [
E           'chrome',
E     -     'firefox',
E       ]
---------------------------- Captured stdout setup ----------------------------

Starting test: test_get_running_browsers_with_running_processes
-------------------------- Captured stdout teardown ---------------------------
Completed test: test_get_running_browsers_with_running_processes
- generated xml file: C:\Users\richardi\1_2\tests\unit\results\result_browser_detector_enhanced_2025-08-30_junit.xml -
--------------------------------- JSON report ---------------------------------
report saved to: C:\Users\richardi\1_2\tests\unit\results/result_browser_detector_enhanced_2025-08-30.json
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.13.2-final-0 _______________

Name                                                           Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------------------
src\utilities\privacy\privacy_tools\core\browser_detector.py     128     32    75%   42-46, 82, 89-93, 104-112, 142-152, 180-184, 201-204
--------------------------------------------------------------------------------------------
TOTAL                                                            128     32    75%
Coverage HTML written to dir C:\Users\richardi\1_2\tests\unit\results/coverage_browser_detector_enhanced_2025-08-30
Coverage JSON written to file C:\Users\richardi\1_2\tests\unit\results/coverage_browser_detector_enhanced_2025-08-30.json
Required test coverage of 70% reached. Total coverage: 75.00%
- Generated html report: file:///C:/Users/richardi/1_2/tests/unit/results/result_browser_detector_enhanced_2025-08-30.html -
=========================== short test summary info ===========================
FAILED tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_installed_macos_platform
FAILED tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_is_browser_installed_linux_platform
FAILED tests\unit\test_browser_detector_enhanced_2025-08-30.py::TestBrowserDetectorEnhanced::test_get_running_browsers_with_running_processes
======================== 3 failed, 26 passed in 16.01s ========================

```

### STDERR
```

```

## Generated Reports
- **HTML Report**: result_browser_detector_enhanced_2025-08-30.html
- **JSON Report**: result_browser_detector_enhanced_2025-08-30.json
- **JUnit XML**: result_browser_detector_enhanced_2025-08-30_junit.xml
- **Coverage HTML**: coverage_browser_detector_enhanced_2025-08-30/
- **Coverage JSON**: coverage_browser_detector_enhanced_2025-08-30.json

## Test Configuration
- Minimum Coverage Threshold: 70%
- Test Discovery Pattern: test_*
- Reporting Format: HTML, JSON, JUnit XML
- Coverage Analysis: Enabled with detailed reporting

## Notes
This comprehensive test suite validates all functionality of the BrowserDetector class
including platform-specific browser detection, process management, and data access validation.
