# PowerShell Script to Rename 1_1 folder to pdf_utilities
# Run this script from the project root directory

Write-Host "🔄 Starting folder rename process..." -ForegroundColor Cyan
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow

# Check if 1_1 folder exists
if (Test-Path "1_1") {
    Write-Host "✅ Found 1_1 folder" -ForegroundColor Green
    
    # Check if pdf_utilities already exists
    if (Test-Path "pdf_utilities") {
        Write-Host "⚠️  pdf_utilities folder already exists!" -ForegroundColor Yellow
        $response = Read-Host "Do you want to remove it and continue? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Remove-Item "pdf_utilities" -Recurse -Force
            Write-Host "🗑️  Removed existing pdf_utilities folder" -ForegroundColor Yellow
        } else {
            Write-Host "❌ Operation cancelled" -ForegroundColor Red
            exit 1
        }
    }
    
    # Perform the rename
    try {
        Rename-Item -Path "1_1" -NewName "pdf_utilities"
        Write-Host "✅ Successfully renamed 1_1 to pdf_utilities" -ForegroundColor Green
        
        # Verify the rename
        if (Test-Path "pdf_utilities") {
            Write-Host "✅ Verification: pdf_utilities folder exists" -ForegroundColor Green
            
            # List some key files to confirm
            $keyFiles = @("main.py", "config_manager.py", "log_config.py", "extract_text_migrated.py")
            Write-Host "📁 Checking key files in pdf_utilities:" -ForegroundColor Cyan
            
            foreach ($file in $keyFiles) {
                if (Test-Path "pdf_utilities\$file") {
                    Write-Host "  ✅ $file" -ForegroundColor Green
                } else {
                    Write-Host "  ❌ $file (missing)" -ForegroundColor Red
                }
            }
            
            Write-Host "`n🎉 Folder rename completed successfully!" -ForegroundColor Green
            Write-Host "📋 Next steps:" -ForegroundColor Cyan
            Write-Host "  1. Restart your application" -ForegroundColor White
            Write-Host "  2. Test the PDF Tools button" -ForegroundColor White
            Write-Host "  3. Verify all PDF utilities work correctly" -ForegroundColor White
            
        } else {
            Write-Host "❌ Verification failed: pdf_utilities folder not found after rename" -ForegroundColor Red
            exit 1
        }
        
    } catch {
        Write-Host "❌ Error during rename: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
    
} else {
    Write-Host "❌ 1_1 folder not found in current directory" -ForegroundColor Red
    Write-Host "📁 Current directory contents:" -ForegroundColor Yellow
    Get-ChildItem -Directory | Select-Object Name | Format-Table -AutoSize
    exit 1
}

Write-Host "`n✨ Rename process completed!" -ForegroundColor Green