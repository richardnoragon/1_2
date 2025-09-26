@echo off
REM Software Maintenance Test Execution Script
REM Generated on: 2025-08-28
REM Purpose: Execute comprehensive unit tests for software_maintenance.py

echo =====================================
echo Software Maintenance Test Execution
echo =====================================
echo Date: %date% %time%
echo.

REM Set working directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Create results directory if it doesn't exist
if not exist "results" mkdir results
if not exist "logs" mkdir logs

echo Setting up environment...
echo.

REM Install required packages
echo Installing test dependencies...
pip install -r requirements_test_software_maintenance_2025-08-28.txt
if errorlevel 1 (
    echo WARNING: Some packages may not have installed correctly
    echo Continuing with test execution...
    echo.
)

REM Execute test runner
echo.
echo =====================================
echo Starting Test Execution
echo =====================================
echo.

python run_tests_software_maintenance_2025-08-28.py

REM Check test result
if errorlevel 1 (
    echo.
    echo =====================================
    echo TEST EXECUTION FAILED
    echo =====================================
    echo Please check the generated reports for details:
    echo - results\result_software_maintenance_2025-08-28.html
    echo - results\result_software_maintenance_2025-08-28.json
    echo - logs\software_maintenance_test_2025-08-28.log
) else (
    echo.
    echo =====================================
    echo TEST EXECUTION COMPLETED SUCCESSFULLY
    echo =====================================
    echo Check the following reports:
    echo - results\result_software_maintenance_2025-08-28.html ^(Main Report^)
    echo - results\result_software_maintenance_coverage_2025-08-28\index.html ^(Coverage^)
    echo - results\SOFTWARE_MAINTENANCE_TEST_COMPLETION_REPORT_2025-08-28.md
)

echo.
echo Test execution completed at: %date% %time%
echo.

REM Open HTML report if it exists
if exist "results\result_software_maintenance_2025-08-28.html" (
    echo Opening test report...
    start "" "results\result_software_maintenance_2025-08-28.html"
)

pause