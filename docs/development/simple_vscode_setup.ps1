# Simple VS Code PATH Setup
# Replace the path below with your actual VS Code installation path

# Common paths - uncomment the one that matches your installation:
# $VSCodePath = "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\bin"
# $VSCodePath = "C:\Program Files\Microsoft VS Code\bin"
# $VSCodePath = "C:\Program Files (x86)\Microsoft VS Code\bin"

Write-Host "Please uncomment and edit the correct VS Code path above, then run the commands below:"
Write-Host ""
Write-Host "# 1. Set your VS Code path:"
Write-Host '$VSCodePath = "YOUR_VSCODE_PATH\bin"'
Write-Host ""
Write-Host "# 2. Add to current session PATH:"
Write-Host '$env:PATH += ";$VSCodePath"'
Write-Host ""
Write-Host "# 3. Add to permanent PATH (run as Admin):"
Write-Host '[Environment]::SetEnvironmentVariable("PATH", $env:PATH, "Machine")'
Write-Host ""
Write-Host "# 4. Test the command:"
Write-Host 'code --version'