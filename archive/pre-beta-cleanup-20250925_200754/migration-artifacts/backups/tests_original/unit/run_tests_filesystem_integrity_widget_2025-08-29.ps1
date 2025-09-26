# PowerShell script to run filesystem_integrity_widget unit tests
# Created: 2025-08-29
# Framework: pytest

param(
    [switch]$Verbose,
    [switch]$Coverage,
    [switch]$SkipReports
)

$ErrorActionPreference = "Stop"

# Script information
$ScriptName = "Filesystem Integrity Widget Unit Test Runner"
$TestDate = "2025-08-29"
$TargetModule = "filesystem_integrity_widget.py"

# Color functions
function Write-Header {
    param([string]$Message)
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Yellow
    Write-Host "=" * 80 -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

# Main execution
try {
    Write-Header "$ScriptName - $TestDate"
    
    # Get script directory
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
    
    Write-Info "Script Directory: $ScriptDir"
    Write-Info "Project Root: $ProjectRoot"
    Write-Info "Target Module: $TargetModule"
    Write-Info "Test Framework: pytest"
    Write-Info "Execution Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    
    # Change to script directory
    Set-Location $ScriptDir
    
    # Define file paths
    $TestFile = "test_filesystem_integrity_widget_$TestDate.py"
    $RunnerScript = "run_filesystem_integrity_widget_tests_$TestDate.py"
    $PythonExe = "$ProjectRoot\venv\Scripts\python.exe"
    
    # Check if files exist
    if (-not (Test-Path $TestFile)) {
        Write-Error "Test file not found: $TestFile"
        exit 1
    }
    
    if (-not (Test-Path $RunnerScript)) {
        Write-Error "Runner script not found: $RunnerScript"
        exit 1
    }
    
    if (-not (Test-Path $PythonExe)) {
        Write-Error "Python executable not found: $PythonExe"
        Write-Info "Please ensure the virtual environment is properly configured"
        exit 1
    }
    
    Write-Success "All required files found"
    
    # Display test information
    Write-Header "TEST CONFIGURATION"
    Write-Info "Test File: $TestFile"
    Write-Info "Python Executable: $PythonExe"
    Write-Info "Verbose Mode: $($Verbose.IsPresent)"
    Write-Info "Coverage Analysis: $($Coverage.IsPresent)"
    Write-Info "Skip Reports: $($SkipReports.IsPresent)"
    
    # Run the tests
    Write-Header "EXECUTING TESTS"
    Write-Info "Starting test execution..."
    
    $StartTime = Get-Date
    
    # Execute the Python test runner
    & $PythonExe $RunnerScript
    $ExitCode = $LASTEXITCODE
    
    $EndTime = Get-Date
    $Duration = $EndTime - $StartTime
    
    # Display results
    Write-Header "EXECUTION RESULTS"
    Write-Info "Start Time: $($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Info "End Time: $($EndTime.ToString('yyyy-MM-dd HH:mm:ss'))"
    Write-Info "Duration: $($Duration.ToString('mm\:ss\.fff'))"
    Write-Info "Exit Code: $ExitCode"
    
    if ($ExitCode -eq 0) {
        Write-Success "All tests completed successfully!"
    } else {
        Write-Error "Some tests failed or encountered errors"
    }
    
    # List generated files
    Write-Header "GENERATED REPORTS"
    $ReportFiles = @(
        "result_filesystem_integrity_widget_$TestDate.html",
        "result_filesystem_integrity_widget_$TestDate.json",
        "result_filesystem_integrity_widget_coverage_$TestDate.xml",
        "result_filesystem_integrity_widget_summary_$TestDate.md"
    )
    
    foreach ($ReportFile in $ReportFiles) {
        if (Test-Path $ReportFile) {
            $FileSize = (Get-Item $ReportFile).Length
            Write-Success "✓ $ReportFile ($([math]::Round($FileSize/1KB, 2)) KB)"
        } else {
            Write-Error "✗ $ReportFile (not generated)"
        }
    }
    
    # Coverage directory
    $CoverageDir = "result_filesystem_integrity_widget_coverage_$TestDate"
    if (Test-Path $CoverageDir) {
        $CoverageFiles = (Get-ChildItem $CoverageDir -Recurse | Measure-Object).Count
        Write-Success "✓ $CoverageDir ($CoverageFiles files)"
    } else {
        Write-Error "✗ $CoverageDir (not generated)"
    }
    
    Write-Header "EXECUTION COMPLETED"
    Write-Info "Check the generated report files for detailed test results and coverage information"
    
    exit $ExitCode
    
} catch {
    Write-Error "An error occurred during test execution:"
    Write-Error $_.Exception.Message
    Write-Error $_.ScriptStackTrace
    exit 1
}