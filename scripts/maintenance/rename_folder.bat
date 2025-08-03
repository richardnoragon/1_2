@echo off
echo 🔄 Starting folder rename process...
echo Current directory: %CD%

REM Check if 1_1 folder exists
if exist "1_1" (
    echo ✅ Found 1_1 folder
    
    REM Check if pdf_utilities already exists
    if exist "pdf_utilities" (
        echo ⚠️  pdf_utilities folder already exists!
        set /p response="Do you want to remove it and continue? (y/N): "
        if /i "%response%"=="y" (
            rmdir /s /q "pdf_utilities"
            echo 🗑️  Removed existing pdf_utilities folder
        ) else (
            echo ❌ Operation cancelled
            pause
            exit /b 1
        )
    )
    
    REM Perform the rename
    ren "1_1" "pdf_utilities"
    
    REM Verify the rename
    if exist "pdf_utilities" (
        echo ✅ Successfully renamed 1_1 to pdf_utilities
        echo ✅ Verification: pdf_utilities folder exists
        
        echo 📁 Checking key files in pdf_utilities:
        if exist "pdf_utilities\main.py" (echo   ✅ main.py) else (echo   ❌ main.py missing)
        if exist "pdf_utilities\config_manager.py" (echo   ✅ config_manager.py) else (echo   ❌ config_manager.py missing)
        if exist "pdf_utilities\log_config.py" (echo   ✅ log_config.py) else (echo   ❌ log_config.py missing)
        if exist "pdf_utilities\extract_text_migrated.py" (echo   ✅ extract_text_migrated.py) else (echo   ❌ extract_text_migrated.py missing)
        
        echo.
        echo 🎉 Folder rename completed successfully!
        echo 📋 Next steps:
        echo   1. Restart your application
        echo   2. Test the PDF Tools button
        echo   3. Verify all PDF utilities work correctly
        
    ) else (
        echo ❌ Verification failed: pdf_utilities folder not found after rename
        pause
        exit /b 1
    )
    
) else (
    echo ❌ 1_1 folder not found in current directory
    echo 📁 Current directory contents:
    dir /ad
    pause
    exit /b 1
)

echo.
echo ✨ Rename process completed!
pause