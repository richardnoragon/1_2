# Enhanced Editor Core Functionality Test Runner
# Created: 2025-08-31
# Target: enhanced_editor.py core functionality testing
# Platform: Windows PowerShell

param(
    [switch]$InstallRequirements,
    [switch]$SkipCoverage,
    [switch]$VerboseOutput,
    [switch]$ShowSummary = $true,
    [string]$OutputDir = "results"
)

# Configuration
$TestFile = "test_enhanced_editor_core_functionality_2025-08-31.py"
$ConfigFile = "pytest_enhanced_editor_core_functionality_2025-08-31.ini"
$RequirementsFile = "requirements_test_enhanced_editor_core_functionality_2025-08-31.txt"
$DateStamp = "2025-08-31"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Output files
$HtmlReport = "result_enhanced_editor_core_functionality_${DateStamp}_report.html"
$JsonReport = "result_enhanced_editor_core_functionality_${DateStamp}_results.json"
$JunitReport = "result_enhanced_editor_core_functionality_${DateStamp}_junit.xml"
$CoverageHtml = "result_enhanced_editor_core_functionality_${DateStamp}_coverage"
$CoverageJson = "result_enhanced_editor_core_functionality_${DateStamp}_coverage.json"
$SummaryFile = "result_enhanced_editor_core_functionality_${DateStamp}_summary.json"
$ExecutionLog = "result_enhanced_editor_core_functionality_${DateStamp}_execution.log"

function Write-LogMessage {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    
    # Also write to log file
    $LogFile = Join-Path $OutputDir $ExecutionLog
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-Requirements {
    Write-LogMessage "Checking Python and required packages..."
    
    # Check if Python is available
    try {
        $PythonVersion = python --version 2>&1
        Write-LogMessage "Python found: $PythonVersion"
    }
    catch {
        Write-LogMessage "Python not found in PATH" "ERROR"
        return $false
    }
    
    # Check if requirements file exists
    if (-not (Test-Path $RequirementsFile)) {
        Write-LogMessage "Requirements file not found: $RequirementsFile" "ERROR"
        return $false
    }
    
    # Check key packages
    try {
        python -c "import pytest, pytest_cov, pytest_html, pytest_mock" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Core test packages are available"
            return $true
        }
        else {
            Write-LogMessage "Some required packages are missing" "WARN"
            return $false
        }
    }
    catch {
        Write-LogMessage "Error checking packages" "ERROR"
        return $false
    }
}

function Install-Requirements {
    Write-LogMessage "Installing test requirements..."
    
    try {
        python -m pip install --upgrade pip
        python -m pip install -r $RequirementsFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Requirements installed successfully"
            return $true
        }
        else {
            Write-LogMessage "Failed to install requirements" "ERROR"
            return $false
        }
    }
    catch {
        Write-LogMessage "Error during requirements installation: $_" "ERROR"
        return $false
    }
}

function Initialize-Environment {
    Write-LogMessage "Setting up test environment..."
    
    # Create output directory
    if (-not (Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
        Write-LogMessage "Created output directory: $OutputDir"
    }
    
    # Set environment variables for Qt testing
    $env:QT_QPA_PLATFORM = "offscreen"
    $env:QT_LOGGING_RULES = "qt.qpa.xcb=false"
    $env:PYTEST_CURRENT_TEST = "enhanced_editor_core_functionality"
    
    # Add source path to PYTHONPATH
    $SrcPath = Join-Path $PSScriptRoot "..\..\src\utilities\file_operations\enhanced_editor"
    if (Test-Path $SrcPath) {
        $env:PYTHONPATH = "$SrcPath;$env:PYTHONPATH"
        Write-LogMessage "Added source path to PYTHONPATH: $SrcPath"
    }
    
    Write-LogMessage "Environment configured for core functionality testing"
}

function Invoke-Tests {
    Write-LogMessage "Starting core functionality test execution..."
    $StartTime = Get-Date
    
    # Build pytest command
    $PytestArgs = @(
        "-m", "pytest",
        $TestFile,
        "-c", $ConfigFile,
        "--verbose",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "--html=$OutputDir\$HtmlReport",
        "--self-contained-html",
        "--junitxml=$OutputDir\$JunitReport",
        "--json-report",
        "--json-report-file=$OutputDir\$JsonReport"
    )
    
    # Add coverage options if not skipped
    if (-not $SkipCoverage) {
        $PytestArgs += @(
            "--cov=enhanced_editor",
            "--cov-report=html:$OutputDir\$CoverageHtml",
            "--cov-report=json:$OutputDir\$CoverageJson",
            "--cov-report=term-missing",
            "--cov-fail-under=70",
            "--cov-branch"
        )
    }
    
    # Add markers to skip slow tests
    $PytestArgs += @("-m", "not slow")
    
    Write-LogMessage "Executing command: python $($PytestArgs -join ' ')"
    
    try {
        # Run tests
        $Process = Start-Process -FilePath "python" -ArgumentList $PytestArgs -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$OutputDir\stdout.log" -RedirectStandardError "$OutputDir\stderr.log"
        
        $EndTime = Get-Date
        $Duration = $EndTime - $StartTime
        
        # Read output files
        if (Test-Path "$OutputDir\stdout.log") {
            $StdOut = Get-Content "$OutputDir\stdout.log" -Raw
            Write-LogMessage "STDOUT:"
            $StdOut -split "`n" | ForEach-Object { if ($_.Trim()) { Write-LogMessage "  $_" } }
        }
        
        if (Test-Path "$OutputDir\stderr.log") {
            $StdErr = Get-Content "$OutputDir\stderr.log" -Raw
            if ($StdErr.Trim()) {
                Write-LogMessage "STDERR:"
                $StdErr -split "`n" | ForEach-Object { if ($_.Trim()) { Write-LogMessage "  $_" "WARN" } }
            }
        }
        
        Write-LogMessage "Test execution completed in $($Duration.TotalSeconds) seconds"
        return $Process.ExitCode -eq 0, $Duration
    }
    catch {
        Write-LogMessage "Error running tests: $_" "ERROR"
        return $false, $null
    }
}

function New-SummaryReport {
    param(
        [bool]$TestSuccess,
        [TimeSpan]$Duration
    )
    
    Write-LogMessage "Generating summary report..."
    
    # Load JSON results if available
    $JsonResults = @{}
    $JsonFile = Join-Path $OutputDir $JsonReport
    if (Test-Path $JsonFile) {
        try {
            $JsonResults = Get-Content $JsonFile -Raw | ConvertFrom-Json
        }
        catch {
            Write-LogMessage "Error reading JSON results: $_" "WARN"
        }
    }
    
    # Load coverage results if available
    $CoverageData = @{}
    $CoverageFile = Join-Path $OutputDir $CoverageJson
    if (Test-Path $CoverageFile) {
        try {
            $CoverageData = Get-Content $CoverageFile -Raw | ConvertFrom-Json
        }
        catch {
            Write-LogMessage "Error reading coverage data: $_" "WARN"
        }
    }
    
    # Create summary object
    $Summary = @{
        test_execution_summary = @{
            execution_timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            test_file = $TestFile
            target_module = "enhanced_editor.py"
            test_focus = "Core Functionality"
            config_file = $ConfigFile
            requirements_file = $RequirementsFile
            execution_time_seconds = [math]::Round($Duration.TotalSeconds, 2)
            execution_time_formatted = "{0}m {1}s" -f [int]($Duration.TotalMinutes), [int]($Duration.Seconds)
            test_success = $TestSuccess
            platform = "Windows PowerShell"
        }
        
        test_results = @{
            total_tests = if ($JsonResults.summary) { $JsonResults.summary.total } else { 0 }
            passed = if ($JsonResults.summary) { $JsonResults.summary.passed } else { 0 }
            failed = if ($JsonResults.summary) { $JsonResults.summary.failed } else { 0 }
            skipped = if ($JsonResults.summary) { $JsonResults.summary.skipped } else { 0 }
            errors = if ($JsonResults.summary) { $JsonResults.summary.error } else { 0 }
            success_rate = "0.00%"
        }
        
        coverage_analysis = @{
            total_coverage = if ($CoverageData.totals) { $CoverageData.totals.percent_covered } else { 0 }
            lines_covered = if ($CoverageData.totals) { $CoverageData.totals.covered_lines } else { 0 }
            lines_missing = if ($CoverageData.totals) { $CoverageData.totals.missing_lines } else { 0 }
            total_lines = if ($CoverageData.totals) { $CoverageData.totals.num_statements } else { 0 }
        }
        
        output_files = @{
            html_report = Join-Path $OutputDir $HtmlReport
            json_results = Join-Path $OutputDir $JsonReport
            junit_xml = Join-Path $OutputDir $JunitReport
            coverage_html = Join-Path $OutputDir "$CoverageHtml\index.html"
            coverage_json = Join-Path $OutputDir $CoverageJson
            summary_report = Join-Path $OutputDir $SummaryFile
            execution_log = Join-Path $OutputDir $ExecutionLog
        }
        
        next_steps = @{
            view_html_report = "Open $HtmlReport in a web browser"
            view_coverage = "Open $CoverageHtml\index.html for detailed coverage"
            check_failures = "Review failed tests in the HTML report"
            improve_coverage = "Add tests for uncovered core functionality"
            run_full_suite = "Execute the comprehensive test suite for complete coverage"
        }
    }
    
    # Calculate success rate
    if ($Summary.test_results.total_tests -gt 0) {
        $SuccessRate = ($Summary.test_results.passed / $Summary.test_results.total_tests) * 100
        $Summary.test_results.success_rate = "{0:F2}%" -f $SuccessRate
    }
    
    # Save summary to file
    $SummaryPath = Join-Path $OutputDir $SummaryFile
    $Summary | ConvertTo-Json -Depth 10 | Set-Content $SummaryPath -Encoding UTF8
    Write-LogMessage "Summary report saved to: $SummaryPath"
    
    return $Summary
}

function Show-Summary {
    param($Summary)
    
    Write-Host "`n" + "="*80 -ForegroundColor Cyan
    Write-Host " ENHANCED EDITOR CORE FUNCTIONALITY TEST SUMMARY" -ForegroundColor Cyan
    Write-Host "="*80 -ForegroundColor Cyan
    
    $ExecInfo = $Summary.test_execution_summary
    Write-Host "Execution Time: $($ExecInfo.execution_timestamp)" -ForegroundColor White
    Write-Host "Target Module: $($ExecInfo.target_module)" -ForegroundColor White
    Write-Host "Test Focus: $($ExecInfo.test_focus)" -ForegroundColor White
    Write-Host "Test File: $($ExecInfo.test_file)" -ForegroundColor White
    Write-Host "Duration: $($ExecInfo.execution_time_formatted)" -ForegroundColor White
    
    if ($ExecInfo.test_success) {
        Write-Host "Success: ✓ PASSED" -ForegroundColor Green
    } else {
        Write-Host "Success: ✗ FAILED" -ForegroundColor Red
    }
    
    Write-Host "`nTEST RESULTS:" -ForegroundColor Yellow
    $Results = $Summary.test_results
    Write-Host "  Total Tests: $($Results.total_tests)" -ForegroundColor White
    Write-Host "  Passed: $($Results.passed)" -ForegroundColor Green
    Write-Host "  Failed: $($Results.failed)" -ForegroundColor Red
    Write-Host "  Skipped: $($Results.skipped)" -ForegroundColor Yellow
    Write-Host "  Errors: $($Results.errors)" -ForegroundColor Red
    Write-Host "  Success Rate: $($Results.success_rate)" -ForegroundColor Cyan
    
    Write-Host "`nCOVERAGE ANALYSIS:" -ForegroundColor Yellow
    $Coverage = $Summary.coverage_analysis
    Write-Host "  Total Coverage: $($Coverage.total_coverage)%" -ForegroundColor Cyan
    Write-Host "  Lines Covered: $($Coverage.lines_covered)" -ForegroundColor Green
    Write-Host "  Lines Missing: $($Coverage.lines_missing)" -ForegroundColor Red
    Write-Host "  Total Lines: $($Coverage.total_lines)" -ForegroundColor White
    
    Write-Host "`nOUTPUT FILES:" -ForegroundColor Yellow
    $Files = $Summary.output_files
    foreach ($FileType in $Files.Keys) {
        $FilePath = $Files[$FileType]
        if (Test-Path $FilePath) {
            Write-Host "  ✓ $FileType`: $FilePath" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $FileType`: $FilePath (not found)" -ForegroundColor Red
        }
    }
    
    Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
    foreach ($Step in $Summary.next_steps.Values) {
        Write-Host "  • $Step" -ForegroundColor White
    }
    
    Write-Host "="*80 -ForegroundColor Cyan
}

# Main execution
function Main {
    Write-LogMessage "Enhanced Editor Core Functionality Test Runner Started"
    Write-LogMessage "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-LogMessage "Platform: Windows PowerShell"
    
    # Initialize environment
    Initialize-Environment
    
    # Install requirements if requested
    if ($InstallRequirements) {
        if (-not (Install-Requirements)) {
            Write-LogMessage "Failed to install requirements" "ERROR"
            exit 1
        }
    }
    
    # Check requirements
    if (-not (Test-Requirements)) {
        Write-LogMessage "Requirements check failed. Use -InstallRequirements to install." "ERROR"
        exit 1
    }
    
    # Check if test file exists
    if (-not (Test-Path $TestFile)) {
        Write-LogMessage "Test file not found: $TestFile" "ERROR"
        exit 1
    }
    
    # Run tests
    $TestSuccess, $Duration = Invoke-Tests
    
    # Generate summary
    $Summary = New-SummaryReport -TestSuccess $TestSuccess -Duration $Duration
    
    # Display summary if requested
    if ($ShowSummary) {
        Show-Summary -Summary $Summary
    }
    
    # Final status
    if ($TestSuccess) {
        Write-LogMessage "Core functionality test execution completed successfully ✓" "INFO"
        exit 0
    } else {
        Write-LogMessage "Core functionality test execution completed with failures ✗" "ERROR"
        exit 1
    }
}

# Execute main function
Main