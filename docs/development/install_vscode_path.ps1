# VS Code PATH Installation Script
# Run this script as Administrator

Write-Host "=== VS Code PATH Installation Script ===" -ForegroundColor Green
Write-Host ""

# Common VS Code installation paths
$possiblePaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code",
    "C:\Program Files\Microsoft VS Code",
    "C:\Program Files (x86)\Microsoft VS Code"
)

$vscodeFound = $false
$vscodePath = ""

# Search for VS Code installation
Write-Host "Searching for VS Code installation..." -ForegroundColor Yellow
foreach ($path in $possiblePaths) {
    $codeExe = Join-Path $path "Code.exe"
    if (Test-Path $codeExe) {
        Write-Host "✅ Found VS Code at: $path" -ForegroundColor Green
        $vscodePath = $path
        $vscodeFound = $true
        break
    }
}

if (-not $vscodeFound) {
    Write-Host "❌ VS Code not found in common locations" -ForegroundColor Red
    Write-Host "Please manually specify your VS Code installation path:" -ForegroundColor Yellow
    $userPath = Read-Host "Enter VS Code installation path (e.g., C:\Program Files\Microsoft VS Code)"
    
    if (Test-Path (Join-Path $userPath "Code.exe")) {
        $vscodePath = $userPath
        $vscodeFound = $true
        Write-Host "✅ VS Code found at user-specified path" -ForegroundColor Green
    } else {
        Write-Host "❌ VS Code not found at specified path" -ForegroundColor Red
        exit 1
    }
}

# Add bin directory to the path
$binPath = Join-Path $vscodePath "bin"

if (-not (Test-Path $binPath)) {
    Write-Host "❌ VS Code bin directory not found at: $binPath" -ForegroundColor Red
    Write-Host "Creating bin directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $binPath -Force
}

# Check if already in PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($currentPath -like "*$binPath*") {
    Write-Host "✅ VS Code is already in system PATH" -ForegroundColor Green
} else {
    Write-Host "Adding VS Code to system PATH..." -ForegroundColor Yellow
    
    try {
        # Add to system PATH (requires Administrator)
        $newPath = $currentPath + ";" + $binPath
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")
        Write-Host "✅ Successfully added VS Code to system PATH" -ForegroundColor Green
        Write-Host "   Path added: $binPath" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ Failed to add to system PATH. You may need to run as Administrator" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Fallback: Add to user PATH
        Write-Host "Trying to add to user PATH instead..." -ForegroundColor Yellow
        try {
            $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
            if (-not ($userPath -like "*$binPath*")) {
                $newUserPath = $userPath + ";" + $binPath
                [Environment]::SetEnvironmentVariable("PATH", $newUserPath, "User")
                Write-Host "✅ Successfully added VS Code to user PATH" -ForegroundColor Green
            }
        } catch {
            Write-Host "❌ Failed to add to user PATH as well" -ForegroundColor Red
            Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# Test the installation
Write-Host ""
Write-Host "Testing 'code' command..." -ForegroundColor Yellow

# Refresh PATH for current session
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")

try {
    $codeVersion = & code --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SUCCESS! 'code' command is working" -ForegroundColor Green
        Write-Host "VS Code version:" -ForegroundColor Cyan
        $codeVersion | ForEach-Object { Write-Host "   $_" -ForegroundColor Cyan }
    } else {
        throw "Command failed"
    }
} catch {
    Write-Host "❌ 'code' command not working yet" -ForegroundColor Red
    Write-Host "You may need to:" -ForegroundColor Yellow
    Write-Host "   1. Restart your terminal/PowerShell" -ForegroundColor Yellow
    Write-Host "   2. Restart VS Code" -ForegroundColor Yellow
    Write-Host "   3. Log out and back in to Windows" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Installation Complete ===" -ForegroundColor Green
Write-Host "If the test failed, please restart your terminal and try again." -ForegroundColor Cyan

# Pause to see results
Read-Host "Press Enter to exit"