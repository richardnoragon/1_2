# Enhanced Editor Comprehensive Test Runner - PowerShell Script
# Created: 2025-08-31
# Target: enhanced_editor.py comprehensive testing

param(
    [switch]$InstallRequirements,
    [switch]$Verbose,
    [switch]$GenerateReports,
    [string]$OutputDir = "results"
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TestDir = $ScriptDir
$RequirementsFile = Join-Path $TestDir "requirements_test_enhanced_editor_comprehensive_2025-08-31.txt"
$TestRunner = Join-Path $TestDir "run_enhanced_editor_comprehensive_tests_2025-08-31.py"

Write-Host "Enhanced Editor Comprehensive Test Suite" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "Test Directory: $TestDir" -ForegroundColor Gray
Write-Host ""

# Function to check if Python is available
function Test-PythonAvailable {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ Python not found in PATH" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to install requirements
function Install-TestRequirements {
    if (-not (Test-Path $RequirementsFile)) {
        Write-Host "✗ Requirements file not found: $RequirementsFile" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Installing test requirements..." -ForegroundColor Yellow
    try {
        python -m pip install --upgrade pip
        python -m pip install -r $RequirementsFile
        Write-Host "✓ Requirements installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to install requirements: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to create results directory
function New-ResultsDirectory {
    $ResultsPath = Join-Path $TestDir $OutputDir
    if (-not (Test-Path $ResultsPath)) {
        New-Item -ItemType Directory -Path $ResultsPath -Force | Out-Null
        Write-Host "✓ Created results directory: $ResultsPath" -ForegroundColor Green
    }
    return $ResultsPath
}

# Function to run tests
function Invoke-TestExecution {
    if (-not (Test-Path $TestRunner)) {
        Write-Host "✗ Test runner not found: $TestRunner" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Executing comprehensive test suite..." -ForegroundColor Yellow
    Write-Host "This may take several minutes..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        # Set environment variables for GUI testing
        $env:QT_QPA_PLATFORM = "offscreen"
        $env:QT_LOGGING_RULES = "qt.qpa.xcb=false"
        
        # Run the test runner
        $result = python $TestRunner
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Test execution completed successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Test execution completed with failures" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "✗ Error during test execution: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to display results summary
function Show-ResultsSummary {
    $ResultsPath = Join-Path $TestDir $OutputDir
    $SummaryFile = Join-Path $ResultsPath "result_enhanced_editor_comprehensive_2025-08-31_summary.json"
    
    if (Test-Path $SummaryFile) {
        try {
            $summary = Get-Content $SummaryFile | ConvertFrom-Json
            
            Write-Host ""
            Write-Host "TEST EXECUTION SUMMARY" -ForegroundColor Cyan
            Write-Host "=====================" -ForegroundColor Cyan
            
            $execInfo = $summary.test_execution_summary
            Write-Host "Duration: $($execInfo.execution_time_formatted)" -ForegroundColor White
            Write-Host "Success: $(if($execInfo.test_success){'✓ PASSED'}else{'✗ FAILED'})" -ForegroundColor $(if($execInfo.test_success){'Green'}else{'Red'})
            
            Write-Host ""
            Write-Host "Test Results:" -ForegroundColor White
            $results = $summary.test_results
            Write-Host "  Total: $($results.total_tests)" -ForegroundColor Gray
            Write-Host "  Passed: $($results.passed)" -ForegroundColor Green
            Write-Host "  Failed: $($results.failed)" -ForegroundColor Red
            Write-Host "  Skipped: $($results.skipped)" -ForegroundColor Yellow
            Write-Host "  Success Rate: $($results.success_rate)" -ForegroundColor White
            
            Write-Host ""
            Write-Host "Coverage:" -ForegroundColor White
            $coverage = $summary.coverage_analysis
            Write-Host "  Total Coverage: $([math]::Round($coverage.total_coverage, 2))%" -ForegroundColor White
            Write-Host "  Lines Covered: $($coverage.lines_covered)" -ForegroundColor Green
            Write-Host "  Lines Missing: $($coverage.lines_missing)" -ForegroundColor Red
            
            Write-Host ""
            Write-Host "Generated Reports:" -ForegroundColor White
            foreach ($file in $summary.output_files.PSObject.Properties) {
                if (Test-Path $file.Value) {
                    Write-Host "  ✓ $($file.Name): $($file.Value)" -ForegroundColor Green
                } else {
                    Write-Host "  ✗ $($file.Name): $($file.Value)" -ForegroundColor Red
                }
            }
            
            return $execInfo.test_success
        }
        catch {
            Write-Host "✗ Error reading summary file: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "✗ Summary file not found: $SummaryFile" -ForegroundColor Red
        return $false
    }
}

# Function to open reports
function Open-TestReports {
    $ResultsPath = Join-Path $TestDir $OutputDir
    $HtmlReport = Join-Path $ResultsPath "result_enhanced_editor_comprehensive_2025-08-31_report.html"
    $CoverageReport = Join-Path $ResultsPath "result_enhanced_editor_comprehensive_2025-08-31_coverage/index.html"
    
    if ($GenerateReports) {
        Write-Host ""
        Write-Host "Opening generated reports..." -ForegroundColor Yellow
        
        if (Test-Path $HtmlReport) {
            Write-Host "Opening test report..." -ForegroundColor Gray
            Start-Process $HtmlReport
        }
        
        if (Test-Path $CoverageReport) {
            Write-Host "Opening coverage report..." -ForegroundColor Gray
            Start-Process $CoverageReport
        }
    }
}

# Main execution
try {
    # Check Python availability
    if (-not (Test-PythonAvailable)) {
        Write-Host "Please install Python and ensure it's in your PATH" -ForegroundColor Red
        exit 1
    }
    
    # Install requirements if requested
    if ($InstallRequirements) {
        if (-not (Install-TestRequirements)) {
            Write-Host "Failed to install requirements" -ForegroundColor Red
            exit 1
        }
    }
    
    # Create results directory
    $resultsDir = New-ResultsDirectory
    
    # Run tests
    $testSuccess = Invoke-TestExecution
    
    # Show summary
    $summarySuccess = Show-ResultsSummary
    
    # Open reports if requested
    Open-TestReports
    
    # Final status
    Write-Host ""
    if ($testSuccess -and $summarySuccess) {
        Write-Host "Enhanced Editor testing completed successfully! ✓" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "Enhanced Editor testing completed with issues! ✗" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "Unexpected error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.ScriptStackTrace -ForegroundColor Red
    exit 1
}

# Usage examples:
# .\run_enhanced_editor_comprehensive_tests_2025-08-31.ps1
# .\run_enhanced_editor_comprehensive_tests_2025-08-31.ps1 -InstallRequirements
# .\run_enhanced_editor_comprehensive_tests_2025-08-31.ps1 -GenerateReports -Verbose