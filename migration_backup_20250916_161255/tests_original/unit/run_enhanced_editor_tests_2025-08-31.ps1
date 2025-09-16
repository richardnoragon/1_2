# Enhanced Editor Test Execution Script (PowerShell)
# Generated: 2025-08-31
# Target: enhanced_editor.py

param(
    [switch]$SkipDependencies,
    [switch]$Verbose,
    [switch]$Coverage,
    [string]$OutputDir = "tests\unit"
)

$ErrorActionPreference = "Continue"

# Test configuration
$TestDate = "2025-08-31"
$TargetFile = "enhanced_editor"
$TestFile = "test_$($TargetFile)_$($TestDate).py"
$ConfigFile = "pytest_$($TargetFile)_$($TestDate).ini"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Enhanced Editor Test Suite Execution" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Date: $TestDate" -ForegroundColor Green
Write-Host "Target: $TargetFile.py" -ForegroundColor Green
Write-Host "Framework: pytest" -ForegroundColor Green
Write-Host "Output Directory: $OutputDir" -ForegroundColor Green
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check Python availability
if (-not (Test-Command "python")) {
    Write-Host "ERROR: Python is not available in PATH" -ForegroundColor Red
    Write-Host "Please install Python or add it to your PATH" -ForegroundColor Red
    exit 1
}

$PythonVersion = python --version 2>&1
Write-Host "Python Version: $PythonVersion" -ForegroundColor Green

# Navigate to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
Set-Location $ProjectRoot

Write-Host "Project Root: $(Get-Location)" -ForegroundColor Green

# Check for virtual environment
$VenvPath = Join-Path $ProjectRoot "venv"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $VenvActivate
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Virtual environment activated" -ForegroundColor Green
    } else {
        Write-Host "Warning: Failed to activate virtual environment" -ForegroundColor Yellow
    }
} else {
    Write-Host "No virtual environment found, using system Python" -ForegroundColor Yellow
}

# Install dependencies if not skipped
if (-not $SkipDependencies) {
    Write-Host ""
    Write-Host "Installing test dependencies..." -ForegroundColor Yellow
    
    $RequirementsFile = Join-Path $OutputDir "requirements_test_enhanced_editor_2025-08-31.txt"
    if (Test-Path $RequirementsFile) {
        python -m pip install -r $RequirementsFile
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Warning: Some dependencies may not have installed correctly" -ForegroundColor Yellow
            Write-Host "Continuing with test execution..." -ForegroundColor Yellow
        } else {
            Write-Host "Dependencies installed successfully" -ForegroundColor Green
        }
    } else {
        Write-Host "Warning: Requirements file not found: $RequirementsFile" -ForegroundColor Yellow
    }
}

# Prepare test execution
Write-Host ""
Write-Host "Preparing test execution..." -ForegroundColor Yellow

$TestRunner = Join-Path $OutputDir "run_enhanced_editor_tests_2025-08-31.py"
if (-not (Test-Path $TestRunner)) {
    Write-Host "ERROR: Test runner not found: $TestRunner" -ForegroundColor Red
    exit 1
}

$TestScript = Join-Path $OutputDir $TestFile
if (-not (Test-Path $TestScript)) {
    Write-Host "ERROR: Test script not found: $TestScript" -ForegroundColor Red
    exit 1
}

Write-Host "Test Runner: $TestRunner" -ForegroundColor Green
Write-Host "Test Script: $TestScript" -ForegroundColor Green

# Execute tests
Write-Host ""
Write-Host "Starting test execution..." -ForegroundColor Cyan
Write-Host ""

$StartTime = Get-Date

try {
    if ($Verbose) {
        python $TestRunner --verbose
    } else {
        python $TestRunner
    }
    
    $TestExitCode = $LASTEXITCODE
    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime
    
} catch {
    Write-Host "ERROR: Test execution failed with exception: $_" -ForegroundColor Red
    $TestExitCode = 1
    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime
}

# Report results
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Test Execution Complete" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Execution Time: $($Duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Green
Write-Host "Exit Code: $TestExitCode" -ForegroundColor Green

if ($TestExitCode -eq 0) {
    Write-Host "Status: SUCCESS - All tests passed" -ForegroundColor Green
} else {
    Write-Host "Status: FAILURE - Some tests failed or encountered errors" -ForegroundColor Red
}

# List generated reports
Write-Host ""
Write-Host "Generated Reports:" -ForegroundColor Cyan

$ReportFiles = @(
    "result_enhanced_editor_2025-08-31.html",
    "result_enhanced_editor_2025-08-31.json",
    "result_enhanced_editor_coverage_2025-08-31.json",
    "result_enhanced_editor_junit_2025-08-31.xml",
    "result_enhanced_editor_summary_2025-08-31.json"
)

$CoverageDir = "result_enhanced_editor_coverage_2025-08-31"

foreach ($ReportFile in $ReportFiles) {
    $FullPath = Join-Path $OutputDir $ReportFile
    if (Test-Path $FullPath) {
        $FileSize = (Get-Item $FullPath).Length
        Write-Host "  ✓ $ReportFile ($FileSize bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $ReportFile (not found)" -ForegroundColor Red
    }
}

$CoverageDirPath = Join-Path $OutputDir $CoverageDir
if (Test-Path $CoverageDirPath) {
    $CoverageFiles = Get-ChildItem $CoverageDirPath -File | Measure-Object
    Write-Host "  ✓ $CoverageDir ($($CoverageFiles.Count) files)" -ForegroundColor Green
} else {
    Write-Host "  ✗ $CoverageDir (not found)" -ForegroundColor Red
}

# Offer to open reports
Write-Host ""
$OpenReports = Read-Host "Would you like to open the HTML test report? (y/N)"
if ($OpenReports -eq "y" -or $OpenReports -eq "Y") {
    $HtmlReport = Join-Path $OutputDir "result_enhanced_editor_2025-08-31.html"
    if (Test-Path $HtmlReport) {
        Write-Host "Opening HTML report..." -ForegroundColor Green
        Start-Process $HtmlReport
    } else {
        Write-Host "HTML report not found" -ForegroundColor Red
    }
}

# Performance summary
Write-Host ""
Write-Host "Performance Summary:" -ForegroundColor Cyan
Write-Host "  Start Time: $($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Green
Write-Host "  End Time: $($EndTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Green
Write-Host "  Duration: $($Duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Green

# Cleanup virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host ""
    Write-Host "Deactivating virtual environment..." -ForegroundColor Yellow
    deactivate
}

Write-Host ""
Write-Host "Test execution completed. Press any key to exit..." -ForegroundColor Cyan
if (-not $env:AUTOMATED) {
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

exit $TestExitCode