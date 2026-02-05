@echo off
REM ============================================================
REM CREATE PATCH FILE for D2L Assignment Assistant
REM ============================================================
REM 
REM This script creates a patch file (.zip) that can be imported
REM by users to update their installed app without reinstalling.
REM 
REM Usage:
REM   1. Make changes to Python scripts in /scripts or /python-modules
REM   2. Run this script
REM   3. Enter patch version and description
REM   4. A patch zip file will be created in the /patches directory
REM   5. Send this zip file to users to import via Patch Manager
REM 
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   D2L Assignment Assistant - CREATE PATCH
echo ============================================================
echo.

REM Create patches directory if it doesn't exist
if not exist "patches" mkdir patches

REM Get version and description from user
set /p "VERSION=Enter patch version (e.g., 1.0.1): "
set /p "DESCRIPTION=Enter patch description: "

if "%VERSION%"=="" (
    echo ERROR: Version is required
    pause
    exit /b 1
)

if "%DESCRIPTION%"=="" (
    echo ERROR: Description is required
    pause
    exit /b 1
)

REM Create timestamp for filename
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%-%datetime:~8,6%

REM Patch filename
set "PATCH_NAME=patch-v%VERSION%-%TIMESTAMP%.zip"
set "PATCH_PATH=patches\%PATCH_NAME%"

echo.
echo Creating patch: %PATCH_NAME%
echo.

REM Create temporary directory for patch contents
set "TEMP_DIR=%TEMP%\d2l-patch-%RANDOM%"
mkdir "%TEMP_DIR%"
mkdir "%TEMP_DIR%\scripts"
mkdir "%TEMP_DIR%\scripts\python-modules"

REM Copy scripts
echo Copying scripts...
xcopy /Y /E /I "scripts\*.py" "%TEMP_DIR%\scripts\" >nul 2>&1
xcopy /Y /E /I "scripts\classes.json" "%TEMP_DIR%\scripts\" >nul 2>&1

REM Copy python-modules
echo Copying python-modules...
xcopy /Y /E /I "python-modules\*" "%TEMP_DIR%\scripts\python-modules\" >nul 2>&1

REM Create metadata file
echo Creating metadata...
(
    echo {
    echo   "version": "%VERSION%",
    echo   "date": "%date% %time%",
    echo   "description": "%DESCRIPTION%",
    echo   "files": []
    echo }
) > "%TEMP_DIR%\patch-metadata.json"

REM Create the zip file using PowerShell
echo Compressing patch file...
powershell -Command "Compress-Archive -Path '%TEMP_DIR%\*' -DestinationPath '%PATCH_PATH%' -Force"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Failed to create patch file
    rmdir /S /Q "%TEMP_DIR%"
    pause
    exit /b 1
)

REM Clean up temp directory
rmdir /S /Q "%TEMP_DIR%"

echo.
echo ============================================================
echo   SUCCESS!
echo ============================================================
echo.
echo Patch file created: %PATCH_PATH%
echo Version: %VERSION%
echo Description: %DESCRIPTION%
echo.
echo To apply this patch:
echo   1. Send this file to users
echo   2. Users open D2L Assignment Assistant
echo   3. Click "PATCHES" button in top bar
echo   4. Click "Import Patch File"
echo   5. Select the patch file
echo   6. Restart the app
echo.
echo ============================================================
echo.

REM Open patches folder
explorer "patches"

pause
