@echo off
REM Windows Batch Script for Virtual Environment Activation
REM ========================================================

echo.
echo 🐍 Activating Python Virtual Environment...
echo.

REM Check if virtual environment exists
if not exist "%~dp0..\..\venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run: python scripts/setup_venv.py
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call "%~dp0..\..\venv\Scripts\activate.bat"

REM Check if activation was successful
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Failed to activate virtual environment!
    pause
    exit /b 1
)

echo ✅ Virtual environment activated successfully!
echo.
echo 📍 Environment: %VIRTUAL_ENV%
echo 🐍 Python: %VIRTUAL_ENV%\Scripts\python.exe
echo 📦 Pip: %VIRTUAL_ENV%\Scripts\pip.exe
echo.
echo 💡 To deactivate, run: deactivate
echo 💡 To verify environment, run: python scripts/verify_environment.py
echo.