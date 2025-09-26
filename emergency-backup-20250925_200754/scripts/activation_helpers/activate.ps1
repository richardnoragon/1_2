# Windows PowerShell Script for Virtual Environment Activation
# ===========================================================

Write-Host ""
Write-Host "🐍 Activating Python Virtual Environment..." -ForegroundColor Cyan
Write-Host ""

# Get script directory and construct venv path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VenvPath = Join-Path (Split-Path -Parent (Split-Path -Parent $ScriptDir)) "venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

# Check if virtual environment exists
if (-not (Test-Path $ActivateScript)) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python scripts/setup_venv.py" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 1
}

# Check execution policy
$ExecutionPolicy = Get-ExecutionPolicy
if ($ExecutionPolicy -eq "Restricted") {
    Write-Host "⚠️  PowerShell execution policy is restricted." -ForegroundColor Yellow
    Write-Host "To enable script execution, run as Administrator:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 1
}

try {
    # Activate virtual environment
    & $ActivateScript
    
    # Check if activation was successful
    if (-not $env:VIRTUAL_ENV) {
        throw "Failed to activate virtual environment"
    }
    
    Write-Host "✅ Virtual environment activated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Environment: $env:VIRTUAL_ENV" -ForegroundColor Cyan
    Write-Host "🐍 Python: $env:VIRTUAL_ENV\Scripts\python.exe" -ForegroundColor Cyan
    Write-Host "📦 Pip: $env:VIRTUAL_ENV\Scripts\pip.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 To deactivate, run: deactivate" -ForegroundColor Yellow
    Write-Host "💡 To verify environment, run: python scripts/verify_environment.py" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host "❌ Failed to activate virtual environment!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to continue"
    exit 1
}