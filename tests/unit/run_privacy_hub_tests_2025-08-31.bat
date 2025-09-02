@echo off
REM Privacy Hub Unit Test Execution Script
REM Generated: 2025-08-31
REM Target: src/utilities/privacy/privacy_tools/gui/privacy_hub.py

echo ====================================
echo Privacy Hub Unit Test Executor
echo ====================================
echo Generated: 2025-08-31
echo Target: privacy_hub.py
echo Framework: pytest
echo ====================================

REM Set working directory
cd /d "%~dp0"
echo Working directory: %CD%

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not available in PATH
    echo Please install Python and ensure it's in your PATH
    pause
    exit /b 1
)

REM Create results directory if it doesn't exist
if not exist "results" mkdir "results"

REM Install requirements if needed
echo.
echo Checking test requirements...
python -c "import pytest, pytest_html, pytest_cov" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing test requirements...
    python -m pip install -r requirements_test_privacy_hub_2025-08-31.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install test requirements
        pause
        exit /b 1
    )
)

REM Execute tests using the Python script
echo.
echo Executing comprehensive unit tests...
echo Start time: %date% %time%
echo.

python run_privacy_hub_tests_2025-08-31.py

set test_exit_code=%errorlevel%

echo.
echo End time: %date% %time%
echo.

REM Display results
if %test_exit_code% equ 0 (
    echo ====================================
    echo ALL TESTS COMPLETED SUCCESSFULLY
    echo ====================================
    echo.
    echo Generated reports:
    echo - HTML Report: results\result_privacy_hub_2025-08-31_report.html
    echo - JSON Results: results\result_privacy_hub_2025-08-31_results.json
    echo - Coverage Report: results\result_privacy_hub_2025-08-31_coverage\index.html
    echo - Execution Summary: results\result_privacy_hub_2025-08-31_summary.json
) else (
    echo ====================================
    echo SOME TESTS FAILED OR ENCOUNTERED ERRORS
    echo ====================================
    echo Exit code: %test_exit_code%
    echo Please check the reports for details
)

echo.
echo Press any key to open the HTML report...
pause >nul

REM Try to open the HTML report
if exist "results\result_privacy_hub_2025-08-31_report.html" (
    start "" "results\result_privacy_hub_2025-08-31_report.html"
) else (
    echo HTML report not found
)

exit /b %test_exit_code%