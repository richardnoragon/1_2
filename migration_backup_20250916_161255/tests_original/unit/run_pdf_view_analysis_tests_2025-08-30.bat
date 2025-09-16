@echo off
REM Comprehensive test execution script for PDF View Analysis module
REM Created: 2025-08-30
REM Target: src/utilities/pdf_tools/pdf_view_analysis/view.py

echo ================================================================================
echo PDF VIEW ANALYSIS - COMPREHENSIVE UNIT TESTING
echo ================================================================================
echo Timestamp: %date% %time%
echo Target Module: src/utilities/pdf_tools/pdf_view_analysis/view.py
echo Test Suite: test_pdf_view_analysis_2025-08-30.py
echo ================================================================================

REM Change to the test directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not available or not in PATH
    echo Please ensure Python 3.7+ is installed and accessible
    pause
    exit /b 1
)

echo ✓ Python detected: 
python --version

REM Install test dependencies
echo.
echo Installing test dependencies...
echo ────────────────────────────────────────────────────────────────────────────────
pip install -r requirements_test_pdf_view_analysis_2025-08-30.txt
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may not have installed correctly
    echo Continuing with test execution...
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run the comprehensive test suite
echo.
echo Starting test execution...
echo ────────────────────────────────────────────────────────────────────────────────
python run_pdf_view_analysis_tests_2025-08-30.py

REM Capture the exit code
set TEST_EXIT_CODE=%errorlevel%

echo.
echo ================================================================================
echo TEST EXECUTION COMPLETED
echo ================================================================================

if %TEST_EXIT_CODE% equ 0 (
    echo ✅ Status: SUCCESS
    echo 📊 All tests passed successfully
) else (
    echo ❌ Status: FAILURE
    echo 🔍 Check logs for details
)

echo.
echo Generated Reports:
echo ────────────────────────────────────────────────────────────────────────────────
if exist "result_pdf_view_analysis_2025-08-30_report.html" (
    echo ✓ HTML Report: result_pdf_view_analysis_2025-08-30_report.html
) else (
    echo ✗ HTML Report: Not generated
)

if exist "result_pdf_view_analysis_2025-08-30.json" (
    echo ✓ JSON Results: result_pdf_view_analysis_2025-08-30.json
) else (
    echo ✗ JSON Results: Not generated
)

if exist "result_pdf_view_analysis_2025-08-30_junit.xml" (
    echo ✓ JUnit XML: result_pdf_view_analysis_2025-08-30_junit.xml
) else (
    echo ✗ JUnit XML: Not generated
)

if exist "result_pdf_view_analysis_coverage_2025-08-30\" (
    echo ✓ Coverage HTML: result_pdf_view_analysis_coverage_2025-08-30\
) else (
    echo ✗ Coverage HTML: Not generated
)

if exist "result_pdf_view_analysis_coverage_2025-08-30.json" (
    echo ✓ Coverage JSON: result_pdf_view_analysis_coverage_2025-08-30.json
) else (
    echo ✗ Coverage JSON: Not generated
)

if exist "result_pdf_view_analysis_summary_2025-08-30.json" (
    echo ✓ Summary Report: result_pdf_view_analysis_summary_2025-08-30.json
) else (
    echo ✗ Summary Report: Not generated
)

if exist "result_pdf_view_analysis_testing_documentation_2025-08-30.md" (
    echo ✓ Documentation: result_pdf_view_analysis_testing_documentation_2025-08-30.md
) else (
    echo ✗ Documentation: Not generated
)

echo.
echo ================================================================================
echo.

REM Open the main HTML report if it exists
if exist "result_pdf_view_analysis_2025-08-30_report.html" (
    echo Opening HTML report...
    start result_pdf_view_analysis_2025-08-30_report.html
)

REM Pause to allow user to see results
pause

exit /b %TEST_EXIT_CODE%