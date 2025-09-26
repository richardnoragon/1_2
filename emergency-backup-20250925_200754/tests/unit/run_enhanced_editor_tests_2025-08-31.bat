@echo off
REM Enhanced Editor Test Execution Script
REM Generated: 2025-08-31
REM Target: enhanced_editor.py

echo =========================================
echo Enhanced Editor Test Suite Execution
echo =========================================
echo.
echo Date: 2025-08-31
echo Target: enhanced_editor.py
echo Framework: pytest
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Navigate to project root
cd /d "%~dp0..\.."

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python
)

REM Install test dependencies
echo.
echo Installing test dependencies...
pip install -r tests\unit\requirements_test_enhanced_editor_2025-08-31.txt

if errorlevel 1 (
    echo WARNING: Some dependencies may not have installed correctly
    echo Continuing with test execution...
)

REM Execute the test runner
echo.
echo Starting test execution...
echo.
python tests\unit\run_enhanced_editor_tests_2025-08-31.py

REM Capture exit code
set TEST_EXIT_CODE=%errorlevel%

echo.
echo =========================================
echo Test Execution Complete
echo =========================================
echo.
echo Exit Code: %TEST_EXIT_CODE%

if %TEST_EXIT_CODE% equ 0 (
    echo Status: SUCCESS - All tests passed
) else (
    echo Status: FAILURE - Some tests failed or encountered errors
)

echo.
echo Generated Reports:
echo   HTML Report: tests\unit\result_enhanced_editor_2025-08-31.html
echo   JSON Report: tests\unit\result_enhanced_editor_2025-08-31.json
echo   Coverage HTML: tests\unit\result_enhanced_editor_coverage_2025-08-31\
echo   Coverage JSON: tests\unit\result_enhanced_editor_coverage_2025-08-31.json
echo   JUnit XML: tests\unit\result_enhanced_editor_junit_2025-08-31.xml
echo   Summary JSON: tests\unit\result_enhanced_editor_summary_2025-08-31.json
echo.

REM Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV (
    echo Deactivating virtual environment...
    deactivate
)

echo Press any key to exit...
pause >nul

exit /b %TEST_EXIT_CODE%