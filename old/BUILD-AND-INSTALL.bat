@echo off
setlocal enabledelayedexpansion

title D2L Assignment Extractor - Rebuild and Auto-Install

echo ========================================
echo D2L Assignment Extractor
echo Rebuild and Auto-Install
echo ========================================
echo.

set "PROJECT_DIR=%~dp0"
set "DIST_DIR=%PROJECT_DIR%dist"

cd /d "%PROJECT_DIR%"

echo Step 1: Building React Frontend...
echo ----------------------------------------
cd react-frontend
call npm run build
if errorlevel 1 (
    echo.
    echo ERROR: React build failed!
    pause
    exit /b 1
)
cd ..
echo [OK] React frontend built successfully
echo.

echo Step 2: Building Electron Installer...
echo ----------------------------------------
REM Set environment variable to skip code signing
set CSC_IDENTITY_AUTO_DISCOVERY=false

REM Clear the problematic cache
set CACHE_DIR=%LOCALAPPDATA%\electron-builder\Cache\winCodeSign
if exist "%CACHE_DIR%" (
    echo Clearing code signing cache...
    rmdir /s /q "%CACHE_DIR%" 2>nul
)

call npm run build:win
if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)
echo [OK] Installer built successfully
echo.

echo Step 3: Finding installer...
echo ----------------------------------------
REM Look for installer - it might have version number in name
set "INSTALLER_PATH="
for %%F in ("%DIST_DIR%\D2L Assignment Extractor Setup*.exe") do (
    set "INSTALLER_PATH=%%F"
    goto :found
)

:found
if not defined INSTALLER_PATH (
    echo ERROR: Installer not found in dist folder!
    echo.
    echo Looking for any .exe files in dist folder...
    if exist "%DIST_DIR%" (
        dir /b "%DIST_DIR%\*.exe" 2>nul
    ) else (
        echo Dist folder does not exist: %DIST_DIR%
    )
    echo.
    echo Please check the dist folder manually.
    pause
    exit /b 1
)
echo [OK] Installer found: %INSTALLER_PATH%
echo.

echo Step 4: Running installer...
echo ----------------------------------------
echo The installer will now launch automatically.
echo You can close this window after the installer opens.
echo.
timeout /t 2 /nobreak >nul
start "" "%INSTALLER_PATH%"

echo.
echo ========================================
echo Done! The installer should be opening now.
echo ========================================
echo.
echo This window will close in 5 seconds...
timeout /t 5 /nobreak >nul

