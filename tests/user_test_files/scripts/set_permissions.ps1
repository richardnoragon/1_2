# scripts/set_permissions.ps1
# PowerShell script to set Windows file attributes for permission testing
# Run from the user_test_files directory

$base = $PSScriptRoot | Split-Path -Parent | Join-Path -ChildPath "permissions"

Write-Host "Setting file permissions in: $base" -ForegroundColor Cyan
Write-Host "=" * 60

# Read-only files
$readonlyFile = Join-Path $base "readonly\perm_readonly.txt"
if (Test-Path $readonlyFile) {
    Set-ItemProperty -Path $readonlyFile -Name IsReadOnly -Value $true
    Write-Host "[OK] Set read-only: perm_readonly.txt" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Not found: perm_readonly.txt" -ForegroundColor Yellow
}

# Read-only directory
$readonlyDir = Join-Path $base "readonly\perm_readonly_dir"
if (Test-Path $readonlyDir) {
    attrib +R $readonlyDir
    Write-Host "[OK] Set read-only: perm_readonly_dir" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Not found: perm_readonly_dir" -ForegroundColor Yellow
}

# Hidden files
$hiddenFile = Join-Path $base "hidden\perm_hidden.txt"
if (Test-Path $hiddenFile) {
    attrib +H $hiddenFile
    Write-Host "[OK] Set hidden: perm_hidden.txt" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Not found: perm_hidden.txt" -ForegroundColor Yellow
}

# Hidden directory
$hiddenDir = Join-Path $base "hidden\perm_hidden_dir"
if (Test-Path $hiddenDir) {
    attrib +H $hiddenDir
    Write-Host "[OK] Set hidden: perm_hidden_dir" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Not found: perm_hidden_dir" -ForegroundColor Yellow
}

# System attribute
$systemFile = Join-Path $base "system\perm_system.txt"
if (Test-Path $systemFile) {
    attrib +S $systemFile
    Write-Host "[OK] Set system: perm_system.txt" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Not found: perm_system.txt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 60
Write-Host "Permission configuration complete!" -ForegroundColor Cyan

# Verification
Write-Host ""
Write-Host "Verification:" -ForegroundColor Cyan
Get-ChildItem -Path $base -Recurse -Force | ForEach-Object { 
    [PSCustomObject]@{ 
        Name = $_.Name
        Attributes = $_.Attributes 
    } 
} | Format-Table -AutoSize
