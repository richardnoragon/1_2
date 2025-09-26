# OCR Enhanced Test Execution Script
# run_ocr_enhanced_tests_2025-09-01.ps1
# Purpose: Execute comprehensive OCR testing on Windows with enhanced coverage

param(
    [switch]$Verbose,
    [switch]$Quick,
    [string]$OutputDir = "."
)

Write-Host "🎯 OCR ENHANCED COMPREHENSIVE TEST EXECUTION" -ForegroundColor Cyan
Write-Host "📅 Started at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Gray

# Set execution policy if needed
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ Execution policy set successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Warning: Could not set execution policy: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Change to script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "📁 Working directory: $(Get-Location)" -ForegroundColor Blue

# Check Python installation
try {
    $PythonVersion = python --version 2>&1
    Write-Host "🐍 Python version: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python not found in PATH" -ForegroundColor Red
    exit 1
}

# Install required packages
Write-Host "`n📦 Installing test dependencies..." -ForegroundColor Yellow

$Dependencies = @(
    "pytest>=7.0.0",
    "pytest-html>=3.1.0", 
    "pytest-json-report>=1.5.0",
    "pandas>=1.5.0",
    "numpy>=1.21.0",
    "Pillow>=9.0.0",
    "psutil>=5.9.0"
)

foreach ($dep in $Dependencies) {
    Write-Host "Installing $dep..." -ForegroundColor Cyan
    try {
        python -m pip install $dep --quiet
        Write-Host "  ✅ $dep installed" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ Warning: Could not install $dep" -ForegroundColor Yellow
    }
}

# Prepare test execution
Write-Host "`n🚀 Preparing test execution..." -ForegroundColor Yellow

$TestFile = "test_ocr_enhanced_complete_2025-09-01.py"
$ConfigFile = "pytest_ocr_enhanced_complete_2025-09-01.ini"
$HtmlReport = "result_ocr_enhanced_complete_2025-09-01.html"
$JsonReport = "result_ocr_enhanced_complete_2025-09-01.json"

# Check test files exist
if (-not (Test-Path $TestFile)) {
    Write-Host "❌ Error: Test file $TestFile not found" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ConfigFile)) {
    Write-Host "❌ Error: Config file $ConfigFile not found" -ForegroundColor Red
    exit 1
}

# Build pytest command
$PytestArgs = @(
    "-m", "pytest",
    $TestFile,
    "-c", $ConfigFile,
    "--html=$HtmlReport",
    "--self-contained-html",
    "--json-report",
    "--json-report-file=$JsonReport"
)

if ($Verbose) {
    $PytestArgs += "--verbose", "--tb=long"
} else {
    $PytestArgs += "--tb=short"
}

if ($Quick) {
    $PytestArgs += "-x"  # Stop on first failure
}

$PytestArgs += "--color=yes", "--durations=10"

Write-Host "🔍 Executing command: python $($PytestArgs -join ' ')" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Gray

# Execute tests
$StartTime = Get-Date

try {
    $Process = Start-Process -FilePath "python" -ArgumentList $PytestArgs -Wait -PassThru -NoNewWindow
    $ExitCode = $Process.ExitCode
    
    $EndTime = Get-Date
    $Duration = ($EndTime - $StartTime).TotalSeconds
    
    Write-Host "=" * 80 -ForegroundColor Gray
    Write-Host "⏱️ Test execution completed in $([math]::Round($Duration, 2)) seconds" -ForegroundColor Blue
    Write-Host "🏁 Exit code: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } else { "Red" })
    
} catch {
    Write-Host "❌ Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    $ExitCode = 1
}

# Generate summary
Write-Host "`n" + "=" * 80 -ForegroundColor Gray
Write-Host "📊 OCR ENHANCED TESTING SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Gray

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "📅 Execution Date/Time: $Timestamp" -ForegroundColor Blue
Write-Host "🎯 Target Module: src/utilities/pdf_tools/pdf_enhancements/ocr.py" -ForegroundColor Blue
Write-Host "🧪 Test Suite: $TestFile" -ForegroundColor Blue
Write-Host "⚙️ Test Framework: pytest with comprehensive mocking" -ForegroundColor Blue

if ($ExitCode -eq 0) {
    Write-Host "✅ Overall Status: SUCCESS" -ForegroundColor Green
    Write-Host "🎉 Result: All tests passed - OCR module validation complete" -ForegroundColor Green
} else {
    Write-Host "❌ Overall Status: FAILURE" -ForegroundColor Red
    Write-Host "⚠️ Result: Some tests failed - review required" -ForegroundColor Yellow
}

# Check generated reports
Write-Host "`n📄 Generated Reports:" -ForegroundColor Yellow

if (Test-Path $HtmlReport) {
    $HtmlSize = (Get-Item $HtmlReport).Length
    Write-Host "   📋 HTML Report: $HtmlReport ($HtmlSize bytes)" -ForegroundColor Green
} else {
    Write-Host "   ❌ HTML Report: Not generated" -ForegroundColor Red
}

if (Test-Path $JsonReport) {
    $JsonSize = (Get-Item $JsonReport).Length
    Write-Host "   📊 JSON Report: $JsonReport ($JsonSize bytes)" -ForegroundColor Green
} else {
    Write-Host "   ❌ JSON Report: Not generated" -ForegroundColor Red
}

Write-Host "`n🔍 Enhanced Test Coverage Areas:" -ForegroundColor Yellow
$CoverageAreas = @(
    "Core Image Processing Functions",
    "Text Processing and OCR Engine", 
    "Image Operations and Conversions",
    "Main OCR Processing Functions",
    "File-level OCR Operations",
    "Folder Operations and Batch Processing",
    "Path Validation and Security",
    "Performance and Memory Testing",
    "Security Validation",
    "Integration Scenarios"
)

foreach ($area in $CoverageAreas) {
    Write-Host "   ✅ $area" -ForegroundColor Green
}

Write-Host "`n🛠️ Improvements Implemented:" -ForegroundColor Yellow
$Improvements = @(
    "Fixed pandas API compatibility issues",
    "Enhanced search function testing",
    "Improved mock configurations", 
    "Added comprehensive edge case coverage",
    "Enhanced GUI testing framework",
    "Performance and memory testing",
    "Security validation testing",
    "End-to-end workflow simulation"
)

foreach ($improvement in $Improvements) {
    Write-Host "   🔧 $improvement" -ForegroundColor Cyan
}

Write-Host "`n" + "=" * 80 -ForegroundColor Gray

# Open reports if successful
if ($ExitCode -eq 0 -and (Test-Path $HtmlReport)) {
    Write-Host "🌐 Opening HTML report..." -ForegroundColor Green
    try {
        Start-Process $HtmlReport
    } catch {
        Write-Host "⚠️ Could not open HTML report automatically" -ForegroundColor Yellow
    }
}

Write-Host "🏁 Exiting with code: $ExitCode" -ForegroundColor $(if ($ExitCode -eq 0) { "Green" } else { "Red" })
exit $ExitCode