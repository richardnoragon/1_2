@echo off
REM Quick Start Script for Workspace Cleanup
REM Windows batch file for easy execution

echo.
echo ================================================================
echo                   WORKSPACE CLEANUP - QUICK START
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate.bat
    echo And: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Current Directory: %cd%
echo Virtual Environment: Found
echo.

REM Menu options
:menu
echo ================================================================
echo                        CLEANUP OPTIONS
echo ================================================================
echo.
echo 1. DRY RUN - Analyze what would be cleaned (RECOMMENDED FIRST)
echo 2. LIVE RUN - Actually perform cleanup (USE WITH CAUTION)
echo 3. Recovery Tool - Restore archived files
echo 4. Documentation Update Only
echo 5. Team Coordination Tools  
echo 6. Maintenance Tools
echo 7. View Reports
echo 8. Exit
echo.
set /p choice="Select option (1-8): "

if "%choice%"=="1" goto dryrun
if "%choice%"=="2" goto liverun
if "%choice%"=="3" goto recovery
if "%choice%"=="4" goto docs
if "%choice%"=="5" goto team
if "%choice%"=="6" goto maintenance
if "%choice%"=="7" goto reports
if "%choice%"=="8" goto exit
echo Invalid choice. Please try again.
goto menu

:dryrun
echo.
echo ================================================================
echo                       DRY RUN CLEANUP
echo ================================================================
echo.
echo This will analyze your workspace and show what would be cleaned
echo WITHOUT making any actual changes.
echo.
pause
venv\Scripts\python.exe scripts\workspace-cleanup\cleanup_orchestrator.py --workspace . --verbose
echo.
echo Dry run completed! Review the results above.
echo Use option 2 to perform the actual cleanup.
pause
goto menu

:liverun
echo.
echo ================================================================
echo                        LIVE CLEANUP  
echo ================================================================
echo.
echo WARNING: This will make ACTUAL CHANGES to your workspace!
echo.
echo - Files will be archived and removed
echo - Directory structure will be modified  
echo - Git commits will be created
echo.
echo Make sure you have:
echo 1. Committed all your current work
echo 2. Backed up any important files
echo 3. Reviewed the dry run results
echo.
set /p confirm="Are you absolutely sure? (type YES to continue): "
if not "%confirm%"=="YES" (
    echo Cancelled by user.
    goto menu
)
echo.
venv\Scripts\python.exe scripts\workspace-cleanup\cleanup_orchestrator.py --workspace . --live-run --verbose
pause
goto menu

:recovery
echo.
echo ================================================================
echo                        RECOVERY TOOLS
echo ================================================================
echo.
echo 1. List archived files
echo 2. Search for specific file
echo 3. Recover specific file
echo 4. Emergency restore (DANGER)
echo 5. Back to main menu
echo.
set /p rchoice="Select recovery option (1-5): "

if "%rchoice%"=="1" (
    venv\Scripts\python.exe scripts\workspace-cleanup\archive_recovery.py --workspace . --list
    pause
    goto recovery
)
if "%rchoice%"=="2" (
    set /p search="Enter search term: "
    venv\Scripts\python.exe scripts\workspace-cleanup\archive_recovery.py --workspace . --search "%search%"
    pause
    goto recovery
)
if "%rchoice%"=="3" (
    set /p recover="Enter file path to recover: "
    echo DRY RUN - use --live-run to actually recover
    venv\Scripts\python.exe scripts\workspace-cleanup\archive_recovery.py --workspace . --recover "%recover%"
    pause
    goto recovery
)
if "%rchoice%"=="4" (
    echo WARNING: This will restore ALL archived files!
    set /p archive="Enter archive name: "
    set /p econfirm="Type RESTORE to continue: "
    if "%econfirm%"=="RESTORE" (
        venv\Scripts\python.exe scripts\workspace-cleanup\archive_recovery.py --workspace . --emergency-restore "%archive%" --live-run
    )
    pause
    goto recovery
)
if "%rchoice%"=="5" goto menu
echo Invalid choice.
goto recovery

:docs
echo.
echo ================================================================
echo                   DOCUMENTATION UPDATE
echo ================================================================
echo.
venv\Scripts\python.exe scripts\workspace-cleanup\documentation_updater.py --workspace . --live-run
pause
goto menu

:team
echo.
echo ================================================================
echo                   TEAM COORDINATION
echo ================================================================
echo.
echo 1. Generate team checklists
echo 2. Send pre-cleanup notification (demo)
echo 3. Create status dashboard
echo 4. Back to main menu
echo.
set /p tchoice="Select option (1-4): "

if "%tchoice%"=="1" (
    venv\Scripts\python.exe scripts\workspace-cleanup\team_coordinator.py --workspace . --checklists
    pause
    goto team
)
if "%tchoice%"=="2" (
    venv\Scripts\python.exe scripts\workspace-cleanup\team_coordinator.py --workspace . --pre-cleanup
    pause
    goto team
)
if "%tchoice%"=="3" (
    echo {"phase": "Ready", "percentage": 0, "active": false} > status.json
    venv\Scripts\python.exe scripts\workspace-cleanup\team_coordinator.py --workspace . --dashboard status.json
    del status.json
    echo Dashboard created: cleanup-dashboard.html
    pause
    goto team
)
if "%tchoice%"=="4" goto menu
goto team

:maintenance
echo.
echo ================================================================
echo                    MAINTENANCE TOOLS
echo ================================================================  
echo.
echo 1. Run daily maintenance
echo 2. Show workspace metrics
echo 3. Generate maintenance summary
echo 4. Back to main menu
echo.
set /p mchoice="Select option (1-4): "

if "%mchoice%"=="1" (
    venv\Scripts\python.exe scripts\workspace-cleanup\workspace_maintenance.py --workspace . --daily
    pause
    goto maintenance
)
if "%mchoice%"=="2" (
    venv\Scripts\python.exe scripts\workspace-cleanup\workspace_maintenance.py --workspace . --metrics
    pause
    goto maintenance
)
if "%mchoice%"=="3" (
    venv\Scripts\python.exe scripts\workspace-cleanup\workspace_maintenance.py --workspace . --summary
    pause
    goto maintenance
)
if "%mchoice%"=="4" goto menu
goto maintenance

:reports
echo.
echo ================================================================
echo                         VIEW REPORTS
echo ================================================================
echo.
if exist "reports" (
    echo Available report directories:
    dir /b reports
    echo.
    echo Latest cleanup reports:
    if exist "reports\cleanup" (
        dir /b /o-d reports\cleanup | head -5
    )
    echo.
    echo To view reports, check the reports\ directory
) else (
    echo No reports directory found.
    echo Reports will be created after running cleanup operations.
)
pause
goto menu

:exit
echo.
echo Thank you for using the Workspace Cleanup Tools!
echo.
echo Quick reference:
echo   Dry run:    scripts\workspace-cleanup\cleanup_orchestrator.py --workspace .
echo   Live run:   scripts\workspace-cleanup\cleanup_orchestrator.py --workspace . --live-run  
echo   Recovery:   scripts\workspace-cleanup\archive_recovery.py --help
echo   Docs:       scripts\workspace-cleanup\documentation_updater.py --help
echo.
pause
exit /b 0