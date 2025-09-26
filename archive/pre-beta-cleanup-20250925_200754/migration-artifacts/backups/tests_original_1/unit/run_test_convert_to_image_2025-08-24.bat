@echo off
REM Batch file to run comprehensive unit tests for convert_to_image.py
REM Created on: 2025-08-24

echo COMPREHENSIVE UNIT TEST SUITE FOR convert_to_image.py
echo ===========================================================
echo.

cd /d "C:\Users\HP1\1_2\1_2\tests\unit"

echo Installing test dependencies...
python -m pip install -r requirements_test_convert_to_image_2025-08-24.txt

echo.
echo Running comprehensive test suite...
python run_test_convert_to_image_2025-08-24.py

echo.
echo Test execution completed!
echo Check the following files for detailed results:
echo   - result_convert_to_image_2025-08-24.html
echo   - result_convert_to_image_2025-08-24.json  
echo   - result_convert_to_image_coverage_2025-08-24\
echo   - result_convert_to_image_summary_2025-08-24.txt

pause