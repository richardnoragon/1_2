@echo off
REM Test execution script for size_analyzer_config.py
REM Created: 2025-08-29

echo ========================================
echo Size Analyzer Config - Unit Test Suite
echo ========================================
echo Execution Date: %date% %time%
echo.

REM Navigate to test directory
cd /d "C:\Users\richardi\1_2\tests\unit"

REM Activate virtual environment if it exists
if exist "..\..\venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "..\..\venv\Scripts\activate.bat"
)

REM Install test requirements
echo Installing test requirements...
python -m pip install -r test_requirements_size_analyzer_config_2025-08-29.txt

REM Run the test runner
echo.
echo Running comprehensive unit tests...
echo.
python run_size_analyzer_config_tests_2025-08-29.py

echo.
echo ========================================
echo Test execution completed!
echo Check the generated reports in:
echo %CD%
echo ========================================
pause