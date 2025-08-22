@echo off
REM Simple batch script to open text files in VS Code
REM Usage: open_files.bat [directory] [max_files]

setlocal enabledelayedexpansion

REM Set default values
set "target_dir=%~1"
set "max_files=%~2"

if "%target_dir%"=="" set "target_dir=."
if "%max_files%"=="" set "max_files=20"

echo Scanning directory: %target_dir%
echo Maximum files: %max_files%

REM Common text file extensions
set "extensions=*.txt *.py *.js *.ts *.html *.css *.json *.xml *.md *.yml *.yaml *.ini *.cfg *.sql *.bat *.ps1 *.sh"

REM Counter for files
set /a count=0

REM Temporary file to store found files
set "temp_file=%temp%\vscode_files.txt"
if exist "%temp_file%" del "%temp_file%"

REM Find files with specified extensions
for %%e in (%extensions%) do (
    for /r "%target_dir%" %%f in (%%e) do (
        REM Skip certain directories
        echo %%~dpf | findstr /i "\.git\\ __pycache__\\ node_modules\\ .venv\\ venv\\ build\\ dist\\" >nul
        if errorlevel 1 (
            set /a count+=1
            echo %%f >> "%temp_file%"
            if !count! geq %max_files% goto :found_enough
        )
    )
)

:found_enough
if %count%==0 (
    echo No text files found.
    goto :end
)

echo Found %count% text files.

REM Ask for confirmation if many files
if %count% gtr 10 (
    set /p "confirm=Open %count% files in VS Code? (y/N): "
    if /i not "!confirm!"=="y" if /i not "!confirm!"=="yes" (
        echo Cancelled.
        goto :end
    )
)

REM Try to open files in VS Code
if exist "%temp_file%" (
    echo Opening files in VS Code...
    
    REM Try different possible VS Code locations
    where code >nul 2>&1
    if %errorlevel%==0 (
        for /f "delims=" %%i in (%temp_file%) do (
            start "" code "%%i"
        )
    ) else (
        REM Try common installation paths
        if exist "%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" (
            for /f "delims=" %%i in (%temp_file%) do (
                start "" "%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd" "%%i"
            )
        ) else if exist "%ProgramFiles%\Microsoft VS Code\bin\code.cmd" (
            for /f "delims=" %%i in (%temp_file%) do (
                start "" "%ProgramFiles%\Microsoft VS Code\bin\code.cmd" "%%i"
            )
        ) else (
            echo VS Code not found. Please install VS Code or add it to PATH.
            echo Files that would be opened:
            type "%temp_file%"
        )
    )
)

:end
if exist "%temp_file%" del "%temp_file%"
echo Done.
pause