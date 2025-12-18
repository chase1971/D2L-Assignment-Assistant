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
    echo [OK] Found bundled Python - will reuse existing
) else (
    echo [INFO] Bundled Python not found - downloading...
    echo.
    
    REM Create python folder
    if not exist "%PROJECT_DIR%python" mkdir "%PROJECT_DIR%python"
    
    REM Download Python embeddable package
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    set "PYTHON_ZIP=%PROJECT_DIR%python-embed.zip"
    
    echo Downloading Python 3.11 embeddable package...
    echo This may take a few minutes...
    echo.
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%' -UseBasicParsing}"
    
    if not exist "%PYTHON_ZIP%" (
        echo.
        echo ERROR: Failed to download Python!
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
    
    echo [OK] Download complete
    echo.
    
    REM Extract Python
    echo Extracting Python...
    powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PROJECT_DIR%python' -Force"
    
    if not exist "%PROJECT_DIR%python\python.exe" (
        echo.
        echo ERROR: Failed to extract Python!
        pause
        exit /b 1
    )
    
    echo [OK] Extraction complete
    echo.
    
    REM Clean up ZIP file
    del "%PYTHON_ZIP%" 2>nul
    
    REM Install pip
    echo Installing pip...
    cd /d "%PROJECT_DIR%python"
    call python.exe -m ensurepip --default-pip >nul 2>&1
    if errorlevel 1 (
        echo Installing pip via get-pip.py...
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py' -UseBasicParsing}"
        call python.exe get-pip.py >nul 2>&1
        del get-pip.py 2>nul
    )
    echo [OK] Pip installed
    echo.
    
    REM Install dependencies
    echo Installing Python dependencies...
    echo This may take a few minutes...
    call python.exe -m pip install -r "%PROJECT_DIR%requirements.txt" --target "%PROJECT_DIR%python" --quiet
    if errorlevel 1 (
        echo.
        echo WARNING: Some dependencies may have failed to install
        echo The build will continue, but Python scripts may not work correctly.
        echo.
    ) else (
        echo [OK] Dependencies installed
    )
    echo.
    
    REM Configure Python path file
    echo Configuring Python paths...
    set "PTH_FILE="
    for %%F in ("%PROJECT_DIR%python\python*.pth") do (
        set "PTH_FILE=%%F"
        goto :found_pth
    )
    
    :found_pth
    if defined PTH_FILE (
        REM Backup original
        copy "%PTH_FILE%" "%PTH_FILE%.bak" >nul 2>&1
        REM Create new config
        (
            echo python311.zip
            echo .
            echo Lib\site-packages
        ) > "%PTH_FILE%"
        echo [OK] Python configured
    ) else (
        echo WARNING: Could not find python*.pth file - Python may not find packages
    )
    echo.
    
    cd /d "%PROJECT_DIR%"
    echo [OK] Python setup complete!
    echo.
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

