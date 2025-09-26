# Richard's File Utilities - Virtual Environment Setup
# Activate the virtual environment for this project

Write-Host "Activating Richard's File Utilities Python Environment..." -ForegroundColor Green

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Activate the virtual environment
& "$ScriptDir\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Environment activated! Python executable: $ScriptDir\venv\Scripts\python.exe" -ForegroundColor Yellow
Write-Host "To run the main application: python main.py" -ForegroundColor Cyan
Write-Host "To run tests: python -m pytest" -ForegroundColor Cyan
Write-Host "To deactivate: deactivate" -ForegroundColor Cyan
Write-Host ""