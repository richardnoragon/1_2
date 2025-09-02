@echo off
REM Batch file to run filesystem_integrity_widget unit tests
REM Created: 2025-08-29

echo ================================================================================
echo FILESYSTEM INTEGRITY WIDGET UNIT TESTS - BATCH RUNNER
echo ================================================================================
echo Execution started: %date% %time%
echo Test framework: pytest
echo Target module: filesystem_integrity_widget.py
echo ================================================================================

REM Change to the test directory
cd /d "%~dp0"

REM Run the Python test runner
C:\Users\richardi\1_2\venv\Scripts\python.exe run_filesystem_integrity_widget_tests_2025-08-29.py

echo ================================================================================
echo Test execution completed: %date% %time%
echo Check the generated report files for detailed results
echo ================================================================================

pause