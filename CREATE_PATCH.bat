@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM CREATE_PATCH.bat - Creates a distributable patch ZIP
REM ============================================================
REM 
REM This script:
REM 1. Identifies which files changed since last version
REM 2. Copies changed files to patch_files/ folder
REM 3. Creates APPLY_PATCH.bat for users
REM 4. Creates a README with instructions
REM 5. Zips everything into a distributable patch
REM
REM Usage: Just run .\CREATE_PATCH.bat
REM ============================================================

title Creating Patch for D2L Assignment Assistant

echo ============================================================
echo D2L Assignment Assistant - Patch Creator
echo ============================================================
echo.

set "PROJECT_DIR=%~dp0"
set "PATCH_DIR=%PROJECT_DIR%patch_files"
set "PATCH_SCRIPTS=%PATCH_DIR%\scripts"
set "PATCH_MODULES=%PATCH_DIR%\python-modules"
set "PATCH_FRONTEND=%PATCH_DIR%\dist-frontend"
set "PATCH_ELECTRON=%PATCH_DIR%\electron"

REM Read version from package.json
echo Step 1: Reading version from package.json...
echo ----------------------------------------
for /f "tokens=2 delims=:, " %%a in ('findstr /C:"\"version\"" "%PROJECT_DIR%package.json"') do (
    set "VERSION=%%~a"
    goto :version_found
)
:version_found
echo Current version: %VERSION%
echo.

REM Clean old patch files
echo Step 2: Cleaning old patch files...
echo ----------------------------------------
if exist "%PATCH_DIR%" (
    rmdir /s /q "%PATCH_DIR%" 2>nul
)
mkdir "%PATCH_DIR%"
mkdir "%PATCH_SCRIPTS%"
mkdir "%PATCH_MODULES%"
mkdir "%PATCH_FRONTEND%"
mkdir "%PATCH_ELECTRON%"
echo [OK] Patch directory created
echo.

REM Copy changed files
echo Step 3: Copying changed files...
echo ----------------------------------------
echo.
echo Which files have changed? (Select all that apply)
echo.
echo 1. Python CLI scripts (scripts/*.py)
echo 2. Python modules (python-modules/*.py)
echo 3. Frontend (React/TypeScript)
echo 4. Electron main process (electron/main.js)
echo 5. Backend server (server.js)
echo 6. All of the above
echo.
set /p "CHOICE=Enter choice (1-6): "

if "%CHOICE%"=="1" goto :scripts_only
if "%CHOICE%"=="2" goto :modules_only
if "%CHOICE%"=="3" goto :frontend_only
if "%CHOICE%"=="4" goto :electron_only
if "%CHOICE%"=="5" goto :server_only
if "%CHOICE%"=="6" goto :all_files
echo Invalid choice!
pause
exit /b 1

:scripts_only
echo Copying Python CLI scripts...
xcopy /E /I /Y "%PROJECT_DIR%scripts" "%PATCH_SCRIPTS%"
goto :create_patch

:modules_only
echo Copying Python modules...
xcopy /E /I /Y "%PROJECT_DIR%python-modules" "%PATCH_MODULES%"
goto :create_patch

:frontend_only
echo Building frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)
echo Copying frontend...
xcopy /E /I /Y "%PROJECT_DIR%dist-frontend" "%PATCH_FRONTEND%"
goto :create_patch

:electron_only
echo Copying Electron main process...
xcopy /E /I /Y "%PROJECT_DIR%electron" "%PATCH_ELECTRON%"
goto :create_patch

:server_only
echo Copying server.js...
copy "%PROJECT_DIR%server.js" "%PATCH_DIR%\server.js"
goto :create_patch

:all_files
echo Building frontend...
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed!
    pause
    exit /b 1
)
echo Copying all files...
xcopy /E /I /Y "%PROJECT_DIR%scripts" "%PATCH_SCRIPTS%"
xcopy /E /I /Y "%PROJECT_DIR%python-modules" "%PATCH_MODULES%"
xcopy /E /I /Y "%PROJECT_DIR%dist-frontend" "%PATCH_FRONTEND%"
xcopy /E /I /Y "%PROJECT_DIR%electron" "%PATCH_ELECTRON%"
copy "%PROJECT_DIR%server.js" "%PATCH_DIR%\server.js"

:create_patch
echo [OK] Files copied
echo.

REM Create APPLY_PATCH.bat for users
echo Step 4: Creating APPLY_PATCH.bat...
echo ----------------------------------------
(
echo @echo off
echo setlocal
echo.
echo title Applying D2L Assignment Assistant Patch v%VERSION%
echo.
echo ============================================================
echo D2L Assignment Assistant - Patch Installer v%VERSION%
echo ============================================================
echo.
echo This will update your installed D2L Assignment Assistant.
echo.
echo Default installation location:
echo C:\Users\%%USERNAME%%\AppData\Local\Programs\D2L Assignment Assistant
echo.
echo Press Ctrl+C to cancel, or
pause
echo.
echo.
echo Step 1: Locating installation...
echo ----------------------------------------
echo.
echo Please enter the path to your D2L Assignment Assistant installation
echo ^(or press Enter to use default location^):
echo.
set /p "INSTALL_DIR="
echo.
if "%%INSTALL_DIR%%"=="" (
    set "INSTALL_DIR=C:\Users\%%USERNAME%%\AppData\Local\Programs\D2L Assignment Assistant"
)
echo.
echo Using installation directory:
echo %%INSTALL_DIR%%
echo.
if not exist "%%INSTALL_DIR%%\D2L Assignment Assistant.exe" (
    echo.
    echo ERROR: D2L Assignment Assistant not found at this location!
    echo.
    echo Please verify the installation path and try again.
    echo Common locations:
    echo   - C:\Users\%%USERNAME%%\AppData\Local\Programs\D2L Assignment Assistant
    echo   - C:\Program Files\D2L Assignment Assistant
    echo.
    pause
    exit /b 1
)
echo [OK] Installation found
echo.
echo.
echo Step 2: Backing up current installation...
echo ----------------------------------------
if not exist "%%INSTALL_DIR%%\backup" mkdir "%%INSTALL_DIR%%\backup"
echo Backing up resources folder...
if exist "%%INSTALL_DIR%%\resources\app.asar" (
    copy "%%INSTALL_DIR%%\resources\app.asar" "%%INSTALL_DIR%%\backup\app.asar.bak" ^>nul 2^>^&1
)
if exist "%%INSTALL_DIR%%\resources\scripts" (
    xcopy /E /I /Y "%%INSTALL_DIR%%\resources\scripts" "%%INSTALL_DIR%%\backup\scripts" ^>nul 2^>^&1
)
echo [OK] Backup complete
echo.
echo.
echo Step 3: Applying patch...
echo ----------------------------------------
set "PATCH_DIR=%%~dp0"
if exist "%%PATCH_DIR%%scripts" (
    echo Updating Python scripts...
    xcopy /E /I /Y "%%PATCH_DIR%%scripts" "%%INSTALL_DIR%%\resources\scripts"
)
if exist "%%PATCH_DIR%%python-modules" (
    echo Updating Python modules...
    xcopy /E /I /Y "%%PATCH_DIR%%python-modules" "%%INSTALL_DIR%%\resources\scripts\python-modules"
)
if exist "%%PATCH_DIR%%dist-frontend" (
    echo Updating frontend...
    xcopy /E /I /Y "%%PATCH_DIR%%dist-frontend" "%%INSTALL_DIR%%\resources\app\dist-frontend"
)
if exist "%%PATCH_DIR%%electron" (
    echo Updating Electron...
    xcopy /E /I /Y "%%PATCH_DIR%%electron" "%%INSTALL_DIR%%\resources\app\electron"
)
if exist "%%PATCH_DIR%%server.js" (
    echo Updating server...
    copy "%%PATCH_DIR%%server.js" "%%INSTALL_DIR%%\resources\app\server.js"
)
echo.
echo [OK] Patch applied successfully!
echo.
echo ============================================================
echo Patch Installation Complete
echo ============================================================
echo.
echo Your D2L Assignment Assistant has been updated to v%VERSION%.
echo.
echo A backup of your previous installation was saved to:
echo %%INSTALL_DIR%%\backup\
echo.
echo You can now restart the application.
echo.
pause
) > "%PATCH_DIR%\APPLY_PATCH.bat"
echo [OK] APPLY_PATCH.bat created
echo.

REM Create README
echo Step 5: Creating README...
echo ----------------------------------------
(
echo ============================================================
echo D2L Assignment Assistant - Patch v%VERSION%
echo ============================================================
echo.
echo WHAT THIS PATCH FIXES:
echo ----------------------------------------
echo.
echo [MANUAL: Edit this section to describe what changed]
echo.
echo - Bug fix: [describe fix]
echo - New feature: [describe feature]
echo - Performance improvement: [describe improvement]
echo.
echo.
echo INSTALLATION INSTRUCTIONS:
echo ----------------------------------------
echo.
echo 1. Close D2L Assignment Assistant if it's running
echo.
echo 2. Extract this ZIP file to any location
echo.
echo 3. Run APPLY_PATCH.bat
echo.
echo 4. Follow the on-screen instructions
echo.
echo 5. Restart D2L Assignment Assistant
echo.
echo.
echo DEFAULT INSTALLATION LOCATION:
echo ----------------------------------------
echo.
echo C:\Users\[YOUR USERNAME]\AppData\Local\Programs\D2L Assignment Assistant
echo.
echo If you installed to a different location, you'll be prompted
echo to enter the path during patch installation.
echo.
echo.
echo BACKUP:
echo ----------------------------------------
echo.
echo The patch installer automatically creates a backup of your
echo current installation before applying the patch.
echo.
echo If something goes wrong, you can manually restore from:
echo [Your Install Dir]\backup\
echo.
echo.
echo TROUBLESHOOTING:
echo ----------------------------------------
echo.
echo If the patch fails to apply:
echo 1. Make sure D2L Assignment Assistant is fully closed
echo 2. Run APPLY_PATCH.bat as Administrator
echo 3. Manually verify the installation path
echo.
echo If problems persist, you may need to:
echo 1. Uninstall D2L Assignment Assistant
echo 2. Reinstall using the full installer
echo.
echo ============================================================
) > "%PATCH_DIR%\README.txt"
echo [OK] README created
echo.

REM Create ZIP
echo Step 6: Creating patch ZIP...
echo ----------------------------------------
set "PATCH_ZIP=%PROJECT_DIR%D2L_Assignment_Assistant_Patch_%VERSION%.zip"
if exist "%PATCH_ZIP%" del "%PATCH_ZIP%"

powershell -Command "Compress-Archive -Path '%PATCH_DIR%\*' -DestinationPath '%PATCH_ZIP%' -Force"

if not exist "%PATCH_ZIP%" (
    echo ERROR: Failed to create ZIP file!
    pause
    exit /b 1
)
echo [OK] Patch ZIP created
echo.

echo ============================================================
echo Patch Creation Complete!
echo ============================================================
echo.
echo Patch file created: D2L_Assignment_Assistant_Patch_%VERSION%.zip
echo.
echo NEXT STEPS:
echo ----------------------------------------
echo.
echo 1. Edit README.txt in patch_files\ folder to describe changes
echo 2. Test the patch on a clean installation
echo 3. Distribute D2L_Assignment_Assistant_Patch_%VERSION%.zip to users
echo.
echo Users should:
echo 1. Extract the ZIP
echo 2. Run APPLY_PATCH.bat
echo 3. Restart the application
echo.
pause

