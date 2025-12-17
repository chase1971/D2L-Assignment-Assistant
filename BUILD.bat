@echo off
setlocal enabledelayedexpansion

title D2L Assignment Assistant - Build and Install

echo ========================================
echo D2L Assignment Assistant - Build and Install
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

echo Step 2: Checking for bundled Python...
echo ----------------------------------------
if exist "%PROJECT_DIR%python\python.exe" (
    echo [OK] Found bundled Python
) else (
    echo [WARNING] Bundled Python not found!
    echo.
    echo For a standalone installer, you should bundle Python.
    echo Run prepare-python.bat first, or the installer will require
    echo Python to be installed on the target computer.
    echo.
    echo Continue anyway? (Y/N)
    set /p CONTINUE=
    if /i not "!CONTINUE!"=="Y" (
        echo Build cancelled.
        pause
        exit /b 1
    )
)
echo.

echo Step 3: Building Frontend (Vite)...
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

echo Step 4: Building Electron Installer...
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

echo Step 5: Finding and launching installer...
echo ----------------------------------------
set "INSTALLER_PATH="
for %%F in ("%DIST_DIR%\D2L Assignment Assistant Setup*.exe") do (
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

