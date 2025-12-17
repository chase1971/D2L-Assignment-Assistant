# Quick Build Guide - Standalone Installer

## Prerequisites (One-Time Setup)

You only need these on YOUR development machine:
- ✅ Node.js (for building)
- ✅ Python 3.11+ (for preparing bundled Python)

The **final installer** will work on a fresh Windows computer with **nothing installed**.

## Step-by-Step Build Process

### Option 1: Standalone Installer (Recommended)

**1. Prepare Python (First Time Only)**
```batch
prepare-python.bat
```
This will:
- Check if Python embeddable package is downloaded
- Install all Python dependencies
- Configure Python paths

**2. Build the Installer**
```batch
BUILD.bat
```
This will:
- Clean old builds
- Check for bundled Python
- Build frontend
- Create installer
- Launch installer automatically

### Option 2: Installer Without Bundled Python

If you skip Python bundling, the installer will still work, but users will need to:
- Install Python 3.9+ separately
- Add Python to PATH

**To build without Python:**
```batch
BUILD.bat
```
(Answer 'Y' when warned about missing Python)

## What Gets Installed

The installer includes:
- ✅ Electron runtime (Node.js bundled automatically)
- ✅ Python runtime (if bundled)
- ✅ All Python dependencies (if bundled)
- ✅ All Python scripts
- ✅ Frontend application
- ✅ Backend server
- ✅ Desktop shortcut
- ✅ Start menu entry

## Testing the Installer

1. Install on a **clean Windows VM** or fresh computer
2. Launch the app
3. Verify all features work

## File Locations After Installation

- **App Directory**: `C:\Users\[User]\AppData\Local\Programs\d2l-assignment-assistant\`
- **Python** (if bundled): Inside app directory under `resources\python\`
- **Scripts**: Inside app directory under `resources\scripts\`

## Troubleshooting

### "Python not found" Error
- **If Python was bundled**: Check that `python` folder was included in build
- **If Python was NOT bundled**: User must install Python 3.9+ separately

### Import Errors
- Verify all dependencies are in `requirements.txt`
- Check that `prepare-python.bat` installed all packages
- Verify `python311._pth` configuration

### Large Installer Size
- Normal: ~200-300MB (includes Python + dependencies)
- Without Python: ~100-150MB (requires separate Python install)

## Next Steps

After building:
1. Test installer on clean Windows system
2. Distribute the `.exe` file from `dist` folder
3. Users can install and run without any prerequisites!

