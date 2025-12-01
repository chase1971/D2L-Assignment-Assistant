@echo off
setlocal enabledelayedexpansion

title Quiz Grader - Build and Install

echo ========================================
echo Quiz Grader - Build and Install
echo ========================================
echo.

set "PROJECT_DIR=%~dp0"
set "DIST_DIR=%PROJECT_DIR%dist"

cd /d "%PROJECT_DIR%"

echo Step 1: Cleaning old builds...
echo ----------------------------------------
if exist "%DIST_DIR%" (
    echo Removing old dist folder...
    rmdir /s /q "%DIST_DIR%" 2>nul
)
if exist "%PROJECT_DIR%dist-frontend" (
    echo Removing old dist-frontend folder...
    rmdir /s /q "%PROJECT_DIR%dist-frontend" 2>nul
)
echo [OK] Clean complete
echo.

echo Step 2: Building Frontend (Vite)...
echo ----------------------------------------
call npm run build
if errorlevel 1 (
    echo.
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)
echo [OK] Frontend built successfully
echo.

echo Step 3: Building Electron Installer...
echo ----------------------------------------
REM Skip code signing
set CSC_IDENTITY_AUTO_DISCOVERY=false

call npx electron-builder --win
if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)
echo [OK] Installer built successfully
echo.

echo Step 4: Finding and launching installer...
echo ----------------------------------------
set "INSTALLER_PATH="
for %%F in ("%DIST_DIR%\Quiz Grader Setup*.exe") do (
    set "INSTALLER_PATH=%%F"
    goto :found
)

:found
if not defined INSTALLER_PATH (
    echo ERROR: Installer not found in dist folder!
    echo.
    echo Looking for .exe files in dist folder:
    if exist "%DIST_DIR%" (
        dir /b "%DIST_DIR%\*.exe" 2>nul
    )
    pause
    exit /b 1
)

echo [OK] Installer found: %INSTALLER_PATH%
echo.
echo ========================================
echo Launching installer...
echo ========================================
echo.

start "" "%INSTALLER_PATH%"

echo Done! Installer has been launched.
echo This window will close in 3 seconds...
timeout /t 3 /nobreak >nul

