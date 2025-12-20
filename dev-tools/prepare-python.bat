@echo off
setlocal enabledelayedexpansion

title Prepare Python for Standalone Build

echo ========================================
echo Prepare Python for Standalone Build
echo ========================================
echo.
echo This script will help you set up Python for bundling.
echo.
echo IMPORTANT: You must download Python embeddable package first!
echo.
echo Steps:
echo 1. Download Python 3.11 embeddable (64-bit) from:
echo    https://www.python.org/downloads/windows/
echo 2. Extract it to a folder named 'python' in this directory
echo 3. Run this script again
echo.
pause

set "PROJECT_DIR=%~dp0"
set "PYTHON_DIR=%PROJECT_DIR%python"

if not exist "%PYTHON_DIR%\python.exe" (
    echo.
    echo ERROR: Python not found in %PYTHON_DIR%
    echo.
    echo Please:
    echo 1. Download Python 3.11 embeddable (64-bit)
    echo 2. Extract to: %PYTHON_DIR%
    echo 3. Run this script again
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Found Python at: %PYTHON_DIR%\python.exe
echo.

echo Step 1: Installing pip...
echo ----------------------------------------
cd /d "%PYTHON_DIR%"
call python.exe -m ensurepip --default-pip
if errorlevel 1 (
    echo WARNING: ensurepip failed, trying alternative method...
    call python.exe -m pip install --upgrade pip
)
echo [OK] Pip installed
echo.

echo Step 2: Installing Python dependencies...
echo ----------------------------------------
call python.exe -m pip install -r "%PROJECT_DIR%requirements.txt" --target "%PYTHON_DIR%"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo.
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

echo Step 3: Configuring Python path...
echo ----------------------------------------
REM Find the _pth file
set "PTH_FILE="
for %%F in ("%PYTHON_DIR%\python*.pth") do (
    set "PTH_FILE=%%F"
    goto :found_pth
)

:found_pth
if not defined PTH_FILE (
    echo WARNING: Could not find python*.pth file
    echo You may need to manually configure Python paths
) else (
    echo Found Python path file: %PTH_FILE%
    echo.
    echo Please manually edit this file and ensure it contains:
    echo   python311.zip
    echo   .
    echo   Lib\site-packages
    echo.
    echo Or create/edit python311._pth with these lines.
)

echo.
echo ========================================
echo Python preparation complete!
echo ========================================
echo.
echo Next steps:
echo 1. Verify python311._pth is configured correctly
echo 2. Run BUILD.bat to create the installer
echo.
pause

