# Building a Standalone Installer (No Prerequisites)

This guide explains how to build an installer that works on a fresh Windows computer with **no prerequisites** installed.

## Overview

The installer needs to bundle:
1. ✅ **Node.js runtime** - Automatically bundled by Electron
2. ✅ **Python runtime** - Must be manually bundled
3. ✅ **Python dependencies** - Installed in bundled Python
4. ✅ **All application files** - Frontend, backend, scripts

## Step 1: Download Portable Python

1. Download **Python 3.11 Windows embeddable package** (64-bit):
   - Go to: https://www.python.org/downloads/windows/
   - Download: "Windows embeddable package (64-bit)" for Python 3.11
   - File will be named: `python-3.11.x-embed-amd64.zip`

2. Extract the ZIP file to a folder named `python` in your project root:
   ```
   D2L-Assignment-Assistant/
   ├── python/
   │   ├── python.exe
   │   ├── pythonw.exe
   │   ├── python311.dll
   │   └── ... (other files)
   ```

## Step 2: Install Python Dependencies

1. Open PowerShell in the project root
2. Navigate to the python folder:
   ```powershell
   cd python
   ```

3. Install pip (if not included):
   ```powershell
   .\python.exe -m ensurepip --default-pip
   ```

4. Install all required packages:
   ```powershell
   .\python.exe -m pip install -r ..\requirements.txt --target .
   ```

   This installs all packages directly into the `python` folder.

## Step 3: Configure Python for Bundling

1. In the `python` folder, edit `python311._pth` (or similar):
   - Remove or comment out the line that says `import site`
   - Add these lines:
     ```
     python311.zip
     .
     Lib\site-packages
     ```

2. This ensures Python can find installed packages.

## Step 4: Build the Installer

1. Run the build script:
   ```batch
   BUILD.bat
   ```

   Or manually:
   ```batch
   npm run build
   npx electron-builder --win
   ```

2. The installer will be created in the `dist` folder.

## Step 5: Test the Installer

1. Install on a **clean Windows VM** or fresh computer
2. Verify:
   - ✅ App launches without errors
   - ✅ Python scripts run correctly
   - ✅ All features work

## Troubleshooting

### Python Not Found Error
- Check that `python` folder exists in project root
- Verify `python.exe` is in the folder
- Check that `package.json` includes Python in `extraResources`

### Import Errors
- Ensure all dependencies are installed in the `python` folder
- Check `python311._pth` configuration
- Verify `requirements.txt` is up to date

### Large Installer Size
- Python + dependencies can add ~100-200MB
- This is normal for a standalone installer
- Consider using PyInstaller to create smaller executables (advanced)

## Alternative: Using PyInstaller (Advanced)

For a smaller installer, you can convert Python scripts to standalone executables:

1. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```

2. Create executables for each script:
   ```powershell
   pyinstaller --onefile --name process_quiz process_quiz_cli.py
   pyinstaller --onefile --name clear_data clear_data_cli.py
   # ... repeat for all scripts
   ```

3. Update `server.js` to use `.exe` files instead of `.py` files when packaged.

This approach is more complex but results in a smaller installer.

