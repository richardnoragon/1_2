@echo off
echo Activating Richard's File Utilities Python Environment...
call "%~dp0venv\Scripts\activate.bat"
echo.
echo Environment activated! Python executable: %~dp0venv\Scripts\python.exe
echo To run the main application: python main.py
echo To run tests: python -m pytest
echo To deactivate: deactivate
echo.