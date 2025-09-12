# Simple PowerShell script to open text files in VS Code
# Usage: .\open_files.ps1 [directory] [-MaxFiles 50] [-ListOnly]

param(
    [string]$Directory = ".",
    [int]$MaxFiles = 50,
    [switch]$ListOnly
)

# Common text file extensions
$textExtensions = @(
    '.txt', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml',
    '.md', '.rst', '.yml', '.yaml', '.toml', '.cfg', '.ini',
    '.sql', '.sh', '.bat', '.ps1', '.java', '.c', '.cpp', '.h',
    '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
    '.r', '.m', '.pl', '.lua', '.vim', '.tex', '.log'
)

# Directories to skip
$skipDirs = @(
    '.git', '.svn', '.hg', '__pycache__', 'node_modules',
    '.pytest_cache', '.mypy_cache', '.tox', 'venv', '.venv',
    'env', '.env', 'build', 'dist', '.idea', '.vscode'
)

# Check if directory exists
if (-not (Test-Path $Directory -PathType Container)) {
    Write-Error "Directory '$Directory' does not exist."
    exit 1
}

Write-Host "Scanning directory: $(Resolve-Path $Directory)"

# Find text files
$files = @()
Get-ChildItem -Path $Directory -Recurse -File | ForEach-Object {
    $file = $_
    
    # Skip files in excluded directories
    $skip = $false
    foreach ($skipDir in $skipDirs) {
        if ($file.DirectoryName -like "*\$skipDir" -or $file.DirectoryName -like "*\$skipDir\*") {
            $skip = $true
            break
        }
    }
    
    if (-not $skip) {
        # Check if it's a text file
        $extension = $file.Extension.ToLower()
        if ($textExtensions -contains $extension) {
            $files += $file.FullName
            
            # Check file limit
            if ($files.Count -ge $MaxFiles) {
                Write-Host "Reached maximum of $MaxFiles files."
                return
            }
        }
    }
}

if ($files.Count -eq 0) {
    Write-Host "No text files found."
    exit 0
}

Write-Host "Found $($files.Count) text files."

if ($ListOnly) {
    Write-Host "`nText files that would be opened:"
    for ($i = 0; $i -lt $files.Count; $i++) {
        Write-Host ("{0,3}. {1}" -f ($i + 1), $files[$i])
    }
} else {
    # Ask for confirmation if many files
    if ($files.Count -gt 15) {
        $response = Read-Host "Open $($files.Count) files in VS Code? (y/N)"
        if ($response -notmatch '^[Yy]') {
            Write-Host "Cancelled."
            exit 0
        }
    }
    
    # Open files in VS Code
    try {
        & code $files
        Write-Host "Opened $($files.Count) files in VS Code."
    } catch {
        Write-Error "Error opening files in VS Code: $_"
        Write-Host "Make sure VS Code is installed and 'code' command is available in PATH."
    }
}