# Blocker Resolution Management Script (Fixed)
# PowerShell script for managing blocker resolution process
# Generated: September 2, 2025

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "update", "report", "init", "help")]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$BlockerId,
    
    [Parameter()]
    [ValidateSet("NOT_STARTED", "IN_PROGRESS", "BLOCKED", "COMPLETED", "CANCELLED")]
    [string]$Status,
    
    [Parameter()]
    [string]$Notes,
    
    [Parameter()]
    [switch]$Daily,
    
    [Parameter()]
    [switch]$Weekly
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TrackerScript = Join-Path $ScriptDir "blocker_resolution_tracker.py"
$DataFile = Join-Path $ScriptDir "blocker_resolution_tracking.json"

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Yellow
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "--- $Title ---" -ForegroundColor Green
    Write-Host ""
}

function Initialize-BlockerTracking {
    Write-Header "INITIALIZING BLOCKER RESOLUTION TRACKING SYSTEM"
    
    Write-Host "Setting up tracking system..." -ForegroundColor Yellow
    
    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python detected: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "Python not found. Please install Python 3.8+ to use the tracking system." -ForegroundColor Red
        return
    }
    
    # Check if tracker script exists
    if (-not (Test-Path $TrackerScript)) {
        Write-Host "Tracker script not found at: $TrackerScript" -ForegroundColor Red
        return
    }
    
    # Initialize the tracking system
    Write-Host "Initializing tracking database..." -ForegroundColor Yellow
    try {
        python $TrackerScript
        Write-Host "Tracking system initialized successfully!" -ForegroundColor Green
        Write-Host "Data file created at: $DataFile" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Failed to initialize tracking system: $_" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Use './manage-blockers-fixed.ps1 status' to view current blocker status"
    Write-Host "2. Use './manage-blockers-fixed.ps1 update VD-001 -Status IN_PROGRESS' to update blocker status"
    Write-Host "3. Use './manage-blockers-fixed.ps1 report -Daily' to generate daily reports"
}

function Show-BlockerStatus {
    Write-Header "BLOCKER RESOLUTION STATUS"
    
    if (-not (Test-Path $DataFile)) {
        Write-Host "No tracking data found. Run 'init' command first." -ForegroundColor Red
        return
    }
    
    try {
        $data = Get-Content $DataFile | ConvertFrom-Json
        $blockers = $data.blockers
        
        Write-Section "OVERALL SUMMARY"
        $totalBlockers = ($blockers | Get-Member -MemberType NoteProperty).Count
        $completedBlockers = 0
        $inProgressBlockers = 0
        $notStartedBlockers = 0
        $blockedBlockers = 0
        
        foreach ($blockerProperty in ($blockers | Get-Member -MemberType NoteProperty)) {
            $blocker = $blockers.($blockerProperty.Name)
            switch ($blocker.status) {
                "COMPLETED" { $completedBlockers++ }
                "IN_PROGRESS" { $inProgressBlockers++ }
                "NOT_STARTED" { $notStartedBlockers++ }
                "BLOCKED" { $blockedBlockers++ }
            }
        }
        
        Write-Host "Total Blockers: $totalBlockers" -ForegroundColor Cyan
        Write-Host "Completed: $completedBlockers" -ForegroundColor Green
        Write-Host "In Progress: $inProgressBlockers" -ForegroundColor Yellow
        Write-Host "Not Started: $notStartedBlockers" -ForegroundColor Gray
        Write-Host "Blocked: $blockedBlockers" -ForegroundColor Red
        
        Write-Section "BLOCKER DETAILS"
        
        foreach ($blockerProperty in ($blockers | Get-Member -MemberType NoteProperty)) {
            $blockerId = $blockerProperty.Name
            $blocker = $blockers.$blockerId
            
            $statusIcon = switch ($blocker.status) {
                "COMPLETED" { "[DONE]" }
                "IN_PROGRESS" { "[WORK]" }
                "NOT_STARTED" { "[TODO]" }
                "BLOCKED" { "[STOP]" }
                default { "[????]" }
            }
            
            $priorityColor = switch ($blocker.priority) {
                "CRITICAL" { "Red" }
                "HIGH" { "Yellow" }
                "MEDIUM" { "Green" }
                "LOW" { "Blue" }
                default { "White" }
            }
            
            Write-Host ""
            Write-Host "$statusIcon $blockerId - $($blocker.title)" -ForegroundColor $priorityColor
            Write-Host "   Status: $($blocker.status) | Progress: $($blocker.progress_percentage)%" -ForegroundColor Gray
            Write-Host "   Owner: $($blocker.owner) | Target: $($blocker.estimated_completion)" -ForegroundColor Gray
            
            if ($blocker.current_obstacles -and $blocker.current_obstacles.Count -gt 0) {
                Write-Host "   Obstacles: $($blocker.current_obstacles[-1])" -ForegroundColor Red
            }
            
            if ($blocker.next_steps -and $blocker.next_steps.Count -gt 0) {
                Write-Host "   Next: $($blocker.next_steps[-1])" -ForegroundColor Cyan
            }
        }
        
        Write-Host ""
        Write-Host "Last Updated: $($data.last_updated)" -ForegroundColor Gray
        
    }
    catch {
        Write-Host "Error reading tracking data: $_" -ForegroundColor Red
    }
}

function Update-BlockerStatus {
    param(
        [string]$BlockerId,
        [string]$Status,
        [string]$Notes
    )
    
    Write-Header "UPDATING BLOCKER STATUS"
    
    if (-not $BlockerId) {
        Write-Host "Blocker ID is required" -ForegroundColor Red
        return
    }
    
    if (-not $Status) {
        Write-Host "Status is required" -ForegroundColor Red
        return
    }
    
    Write-Host "Updating blocker $BlockerId to status: $Status" -ForegroundColor Yellow
    
    # Create Python script to update status
    $updateScript = @"
import sys
import os
sys.path.append('$($ScriptDir.Replace('\', '\\'))')
from blocker_resolution_tracker import BlockerResolutionTracker, BlockerStatus

tracker = BlockerResolutionTracker('$($DataFile.Replace('\', '\\'))')
status = BlockerStatus.$Status
notes = '$Notes' if '$Notes' else ''

if '$BlockerId' in tracker.blockers:
    tracker.update_blocker_status('$BlockerId', status, notes)
    print(f'Successfully updated {$BlockerId} to {status.value}')
    if notes:
        print(f'Notes: {notes}')
else:
    print(f'Blocker {$BlockerId} not found')
"@
    
    try {
        $updateScript | python
        Write-Host "Blocker status updated successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to update blocker status: $_" -ForegroundColor Red
    }
}

function Generate-Report {
    param(
        [switch]$Daily,
        [switch]$Weekly
    )
    
    $reportType = if ($Weekly) { "Weekly" } else { "Daily" }
    Write-Header "$reportType BLOCKER RESOLUTION REPORT"
    
    $reportScript = @"
import sys
import os
sys.path.append('$($ScriptDir.Replace('\', '\\'))')
from blocker_resolution_tracker import BlockerResolutionTracker

tracker = BlockerResolutionTracker('$($DataFile.Replace('\', '\\'))')
if $($Weekly.ToString().ToLower()):
    report = tracker.generate_weekly_report()
else:
    report = tracker.generate_daily_report()

print(report)
"@
    
    try {
        $report = $reportScript | python
        Write-Host $report
        
        # Save report to file
        $timestamp = Get-Date -Format "yyyy-MM-dd"
        $reportFile = Join-Path $ScriptDir "${reportType.ToLower()}_report_$timestamp.md"
        $report | Out-File -FilePath $reportFile -Encoding UTF8
        
        Write-Host ""
        Write-Host "Report saved to: $reportFile" -ForegroundColor Cyan
        
    }
    catch {
        Write-Host "Failed to generate report: $_" -ForegroundColor Red
    }
}

function Show-Help {
    Write-Header "BLOCKER RESOLUTION MANAGEMENT HELP"
    
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  ./manage-blockers-fixed.ps1 <command> [parameters]"
    Write-Host ""
    
    Write-Host "COMMANDS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  init" -ForegroundColor Green
    Write-Host "    Initialize the blocker tracking system"
    Write-Host "    Example: ./manage-blockers-fixed.ps1 init"
    Write-Host ""
    
    Write-Host "  status" -ForegroundColor Green
    Write-Host "    Show current status of all blockers"
    Write-Host "    Example: ./manage-blockers-fixed.ps1 status"
    Write-Host ""
    
    Write-Host "  update <BlockerId> -Status <Status> [-Notes <Notes>]" -ForegroundColor Green
    Write-Host "    Update blocker status"
    Write-Host "    Statuses: NOT_STARTED, IN_PROGRESS, BLOCKED, COMPLETED, CANCELLED"
    Write-Host "    Example: ./manage-blockers-fixed.ps1 update VD-001 -Status IN_PROGRESS -Notes 'Started package installation'"
    Write-Host ""
    
    Write-Host "  report [-Daily] [-Weekly]" -ForegroundColor Green
    Write-Host "    Generate progress report"
    Write-Host "    Example: ./manage-blockers-fixed.ps1 report -Daily"
    Write-Host ""
    
    Write-Host "  help" -ForegroundColor Green
    Write-Host "    Show this help message"
}

# Main command execution
switch ($Command.ToLower()) {
    "init" {
        Initialize-BlockerTracking
    }
    "status" {
        Show-BlockerStatus
    }
    "update" {
        Update-BlockerStatus -BlockerId $BlockerId -Status $Status -Notes $Notes
    }
    "report" {
        Generate-Report -Daily:$Daily -Weekly:$Weekly
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use './manage-blockers-fixed.ps1 help' for usage information." -ForegroundColor Yellow
    }
}