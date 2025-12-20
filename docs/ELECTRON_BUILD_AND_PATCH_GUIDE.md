# Electron Build and Patch System Guide

**Last Updated:** December 20, 2025  
**Version:** 0.0.1

This guide documents the complete process of building an Electron application with a bundled Python backend, creating an installer, and implementing a Git-based patch system. Use this as a template for replicating this setup in other projects.

---

## Table of Contents

1. [Project Architecture Overview](#project-architecture-overview)
2. [Building the Installer](#building-the-installer)
3. [How Installation Works](#how-installation-works)
4. [Patch/Update System](#patchupdate-system)
5. [File Organization Requirements](#file-organization-requirements)
6. [Replicating for Other Projects](#replicating-for-other-projects)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Project Architecture Overview

### Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Desktop Framework**: Electron 28
- **Backend**: Node.js (Express)
- **Python Scripts**: Python 3.11 (embedded)
- **Build Tool**: electron-builder
- **Installer**: NSIS (Windows)

### How It Works

```
┌─────────────────────────────────────────┐
│   React Frontend (Vite build)           │
│   → dist-frontend/                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Electron Main Process                  │
│   - Hosts frontend in BrowserWindow     │
│   - Spawns Express backend (server.js) │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Express Backend (server.js)           │
│   - Runs Python CLI scripts via exec   │
│   - Path: resources/scripts/*.py        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Python Scripts (bundled)              │
│   - Uses embedded Python interpreter    │
│   - Path: resources/../python/          │
└─────────────────────────────────────────┘
```

---

## Building the Installer

### Prerequisites

1. **Node.js 18+** installed and in PATH
2. **Python 3.11+** installed (for development)
3. **Git** (for version control)
4. All dependencies installed:
   ```bash
   npm install
   pip install -r requirements.txt  # For dev/testing
   ```

### Automated Build Process

**The Easy Way:** Run the build script

```bash
.\BUILD.bat
```

This script automates everything:

1. **Clean old builds**
   ```batch
   Remove-Item dist, dist-frontend -Recurse -Force
   ```

2. **Check for bundled Python** (downloads if missing)
   - Downloads Python 3.11 embeddable package from python.org
   - Extracts to `python/` folder
   - Configures paths and dependencies

3. **Build frontend** (Vite)
   ```batch
   npm run build
   ```
   - Outputs to `dist-frontend/`

4. **Package Electron app** (electron-builder)
   ```batch
   npm run package
   ```
   - Outputs to `dist/D2L Assignment Assistant Setup 0.0.1.exe`

5. **Launch installer** (optional - last step of BUILD.bat)

### Manual Build Steps

If you need to build manually or customize:

```bash
# 1. Clean
Remove-Item dist, dist-frontend -Recurse -Force

# 2. Build frontend
npm run build

# 3. Package Electron app
npm run package

# 4. Installer is in: dist/D2L Assignment Assistant Setup 0.0.1.exe
```

---

## How Installation Works

### electron-builder Configuration

The magic happens in `package.json`:

```json
{
  "version": "0.0.1",
  "build": {
    "appId": "com.d2lassistant.app",
    "productName": "D2L Assignment Assistant",
    "directories": {
      "output": "dist",
      "buildResources": "build"
    },
    "files": [
      "dist-frontend/**/*",
      "electron/**/*",
      "server.js",
      "package.json"
    ],
    "extraResources": [
      {
        "from": "scripts",
        "to": "scripts",
        "filter": ["**/*.py"]
      },
      {
        "from": "python-modules",
        "to": "scripts/python-modules",
        "filter": ["**/*"]
      },
      {
        "from": "python",
        "to": "python",
        "filter": ["**/*"]
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "build/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "installerIcon": "build/icon.ico",
      "uninstallerIcon": "build/icon.ico"
    }
  }
}
```

### Key Configuration Sections

#### 1. `files`
Files included in the Electron app package (ASAR):
- Built frontend (`dist-frontend/`)
- Electron main process (`electron/`)
- Backend server (`server.js`)
- Package metadata (`package.json`)

#### 2. `extraResources`
Files copied outside ASAR (accessible via `process.resourcesPath`):
- Python CLI scripts → `resources/scripts/`
- Python modules → `resources/scripts/python-modules/`
- Bundled Python → `resources/../python/`

**Why extraResources?**
- Python scripts need to be executed as separate processes
- Can't execute files inside ASAR
- `process.resourcesPath` points to `resources/` in installed app

#### 3. `nsis` (Installer Settings)
- **oneClick: false** → User can choose install location
- **allowToChangeInstallationDirectory: true** → Custom install path
- **createDesktopShortcut: true** → Desktop icon
- **createStartMenuShortcut: true** → Start menu entry
- **Uninstaller is automatically created** by NSIS

### Installation Flow

1. **User runs installer**: `D2L Assignment Assistant Setup 0.0.1.exe`
2. **NSIS wizard appears**:
   - Welcome screen
   - License agreement (if configured)
   - Installation directory selection (default: `C:\Users\<USER>\AppData\Local\Programs\D2L Assignment Assistant`)
   - Installation progress
3. **Files are extracted**:
   ```
   C:\Users\<USER>\AppData\Local\Programs\D2L Assignment Assistant\
   ├── D2L Assignment Assistant.exe    # Main executable
   ├── resources\
   │   ├── app.asar                     # Electron app (frontend, electron/, server.js)
   │   └── scripts\                     # Python scripts
   │       ├── *.py                     # CLI scripts
   │       └── python-modules\          # Python modules
   ├── python\                          # Bundled Python interpreter
   │   ├── python.exe
   │   ├── python311.dll
   │   └── ...
   ├── locales\                         # Electron locales
   └── Uninstall D2L Assignment Assistant.exe  # Auto-generated uninstaller
   ```
4. **Shortcuts created**:
   - Desktop: `D2L Assignment Assistant.lnk`
   - Start Menu: `Start Menu\Programs\D2L Assignment Assistant\`
5. **Registry entries created** (for uninstall info)

### How Python is Found at Runtime

In `server.js`:

```javascript
const SCRIPTS_PATH = process.resourcesPath 
  ? path.join(process.resourcesPath, 'scripts')
  : path.join(__dirname, 'scripts');  // Development fallback

async function findPython() {
  const possiblePaths = [];
  
  // 1. Check bundled Python (packaged app)
  if (process.resourcesPath) {
    possiblePaths.push(
      path.join(process.resourcesPath, 'python', 'python.exe'),
      path.join(process.resourcesPath, '..', 'python', 'python.exe')
    );
  }
  
  // 2. Check local python/ folder (development)
  possiblePaths.push(
    path.join(__dirname, 'python', 'python.exe')
  );
  
  // 3. Check system Python (fallback)
  possiblePaths.push('python', 'python3', ...);
  
  // Test each path and return first working one
}
```

**Python Import Path in CLI Scripts:**

Each Python CLI script adds `python-modules/` to `sys.path`:

```python
import sys
import os

# Add python-modules to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_MODULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'python-modules')
sys.path.insert(0, PYTHON_MODULES_DIR)

# Now imports work
from grading_processor import run_grading_process
from user_messages import log
```

---

## Patch/Update System

### Current Status

- **Auto-update is DISABLED** (commented out in `electron/main.js`)
- **Manual patches** were tested but deemed cumbersome
- **Future plan**: Git-based automatic patch system

### Why Manual Patches Were Abandoned

Manual patch system required:
1. User downloads patch ZIP
2. User runs batch script
3. Script copies files to install directory
4. Requires elevated permissions
5. Error-prone (wrong install path, permissions issues)

**Problems:**
- Not user-friendly
- No verification of successful application
- No rollback capability
- Requires manual distribution

### Future: Git-Based Automatic Patch System

**Goal:** Seamless updates similar to VS Code, Discord, etc.

#### Planned Architecture

```
Developer Machine (You)                    User Machine
─────────────────────                      ────────────
1. Make code changes
2. Commit to Git
3. Tag version: v0.0.2
4. Run: .\CREATE_PATCH.bat
   ↓
   Generates:
   - Builds new installer
   - Generates diff from v0.0.1
   - Creates update metadata
   - Uploads to update server
                                           5. App checks for updates on startup
                                              ↓
                                           6. Downloads delta patch
                                              ↓
                                           7. Applies patch in background
                                              ↓
                                           8. Prompts user to restart
```

#### Implementation Plan

**1. Use electron-updater (already installed)**

`package.json` already has:
```json
{
  "dependencies": {
    "electron-updater": "^6.3.9"
  },
  "build": {
    "publish": {
      "provider": "generic",
      "url": "file:///${env.USERPROFILE}/Documents/D2L-Updates"
    }
  }
}
```

**2. Enable auto-update in `electron/main.js`**

Currently commented out:
```javascript
const { autoUpdater } = require('electron-updater');

app.whenReady().then(async () => {
  createWindow();
  // autoUpdater.checkForUpdatesAndNotify();  // <-- Uncomment this
});
```

**3. Create automated patch generation script**

`CREATE_PATCH.bat`:
```batch
@echo off
REM 1. Get current version from package.json
REM 2. Build new installer
REM 3. Generate delta patch (electron-builder does this automatically)
REM 4. Upload to update server or file share
REM 5. Update latest.yml metadata file
```

**4. Set up update server**

Options:
- **Local file share**: `C:\Users\chase\Documents\D2L-Updates\` (current config)
- **GitHub Releases**: Free, automatic hosting
- **Self-hosted server**: Full control
- **S3 bucket**: Scalable, cheap

**5. Delta updates**

electron-updater automatically creates delta patches:
- Only downloads changed files
- Reduces download size from ~300MB to ~5MB for small changes
- Uses block-level differencing

#### Git-Based Workflow

```bash
# 1. Make changes
git add .
git commit -m "Fix split PDF bug"

# 2. Tag version
git tag v0.0.2

# 3. Generate patch
.\CREATE_PATCH.bat

# CREATE_PATCH.bat does:
# - Reads current version from package.json
# - Compares with previous tag (git diff v0.0.1..v0.0.2)
# - Builds full installer
# - Generates delta patch
# - Updates CHANGELOG.md
# - Uploads to update server
```

#### Update Flow (User Perspective)

```
User opens app
  ↓
App checks: "Is there a newer version?"
  ↓
If YES:
  - Downloads delta patch in background
  - Shows notification: "Update available (5.2 MB)"
  - User clicks "Update & Restart"
  - App applies patch
  - App restarts with new version
  ↓
If NO:
  - Continue normally
```

#### Security

- **Code signing**: Sign installer with certificate (prevents Windows warnings)
- **HTTPS**: Use HTTPS for update server (prevents man-in-the-middle)
- **Checksum verification**: electron-updater verifies SHA512 hashes
- **Delta integrity**: Verifies patch applies cleanly

---

## File Organization Requirements

### Required Structure for Build

```
YourProject/
├── src/                        # React frontend
│   ├── components/
│   ├── services/
│   └── main.tsx
│
├── electron/                   # Electron process
│   ├── main.js                 # REQUIRED: Electron entry point
│   └── preload.js              # REQUIRED: IPC bridge
│
├── scripts/                    # Python CLI scripts (entry points)
│   ├── process_*.py
│   └── ...
│
├── python-modules/             # Python reusable modules
│   ├── *.py
│   └── user_messages/
│
├── python/                     # Bundled Python interpreter
│   ├── python.exe
│   └── ...
│
├── dist-frontend/              # Built frontend (auto-generated)
├── dist/                       # Built installer (auto-generated)
│
├── server.js                   # REQUIRED: Backend server
├── package.json                # REQUIRED: Dependencies & build config
├── BUILD.bat                   # Build automation script
└── vite.config.ts              # Frontend build config
```

### Critical Files

#### 1. `package.json`

Must have:
```json
{
  "name": "your-app",
  "version": "0.0.1",
  "main": "electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "package": "electron-builder"
  },
  "dependencies": {
    "electron": "^28.0.0",
    "express": "^4.18.0",
    "electron-updater": "^6.3.9"
  },
  "build": {
    "appId": "com.yourcompany.app",
    "productName": "Your App Name",
    "files": ["dist-frontend/**/*", "electron/**/*", "server.js", "package.json"],
    "extraResources": [
      {"from": "scripts", "to": "scripts", "filter": ["**/*.py"]},
      {"from": "python-modules", "to": "scripts/python-modules", "filter": ["**/*"]},
      {"from": "python", "to": "python", "filter": ["**/*"]}
    ],
    "win": {"target": "nsis"},
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true
    }
  }
}
```

#### 2. `electron/main.js`

Must have:
```javascript
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let serverProcess;

function startBackendServer() {
  const serverPath = path.join(__dirname, '..', 'server.js');
  serverProcess = spawn('node', [serverPath]);
  // Wait for server to start...
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Development: http://localhost:3000
  // Production: file://dist-frontend/index.html
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
  } else {
    mainWindow.loadFile(path.join(__dirname, '..', 'dist-frontend', 'index.html'));
  }
}

app.whenReady().then(async () => {
  await startBackendServer();
  createWindow();
});

app.on('window-all-closed', () => {
  if (serverProcess) serverProcess.kill();
  app.quit();
});
```

#### 3. `server.js`

Must have:
```javascript
const express = require('express');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const PORT = 5000;

// Scripts path: development vs production
const SCRIPTS_PATH = process.resourcesPath 
  ? path.join(process.resourcesPath, 'scripts')
  : path.join(__dirname, 'scripts');

// Python path: bundled vs system
async function findPython() {
  // Check bundled Python first, then system Python
}

app.post('/api/your-endpoint', async (req, res) => {
  const pythonPath = await findPython();
  const scriptPath = path.join(SCRIPTS_PATH, 'your_script.py');
  
  exec(`"${pythonPath}" "${scriptPath}" arg1 arg2`, (error, stdout) => {
    res.json({ success: !error, output: stdout });
  });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

#### 4. `BUILD.bat`

```batch
@echo off
echo Building Your App...

REM Clean old builds
if exist dist rmdir /s /q dist
if exist dist-frontend rmdir /s /q dist-frontend

REM Check for bundled Python (download if missing)
if not exist python (
  echo Downloading Python...
  powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-embed.zip'"
  powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath 'python'"
  del python-embed.zip
)

REM Build frontend
call npm run build

REM Package Electron app
call npm run package

echo Build complete! Installer is in dist/
pause
```

---

## Replicating for Other Projects

### Step-by-Step Checklist

Use this checklist when setting up a new project:

#### Phase 1: Project Setup

- [ ] Create project folder structure (see [File Organization](#file-organization-requirements))
- [ ] Install dependencies:
  ```bash
  npm init -y
  npm install electron electron-builder vite react react-dom express cors
  npm install electron-updater  # For auto-updates
  ```
- [ ] Create `electron/main.js` and `electron/preload.js`
- [ ] Create `server.js` for backend
- [ ] Set up React frontend with Vite

#### Phase 2: Configure Build

- [ ] Update `package.json` with:
  - `"main": "electron/main.js"`
  - Build scripts: `dev`, `build`, `package`
  - `build` section with electron-builder config
  - `files` array (what goes in ASAR)
  - `extraResources` array (Python scripts, etc.)
  - NSIS installer settings
- [ ] Create `vite.config.ts` for frontend build
- [ ] Add Python scripts to `scripts/` folder
- [ ] Add Python modules to `python-modules/` folder
- [ ] Add Python import path to all CLI scripts:
  ```python
  SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
  PYTHON_MODULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'python-modules')
  sys.path.insert(0, PYTHON_MODULES_DIR)
  ```

#### Phase 3: Bundle Python

- [ ] Download Python embeddable package:
  ```bash
  # Windows 64-bit Python 3.11
  https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
  ```
- [ ] Extract to `python/` folder
- [ ] Configure `python/python311._pth` to include:
  ```
  python311.zip
  .
  ..
  ../scripts
  ../scripts/python-modules
  ```
- [ ] Install packages into `python/`:
  ```bash
  python/python.exe -m pip install --target python/ package-name
  ```

#### Phase 4: Create Build Script

- [ ] Create `BUILD.bat` (see template above)
- [ ] Test build script:
  ```bash
  .\BUILD.bat
  ```
- [ ] Verify installer is created in `dist/`
- [ ] Test installation on clean system

#### Phase 5: Set Up Updates (Optional)

- [ ] Uncomment auto-updater code in `electron/main.js`
- [ ] Configure `publish` section in `package.json`
- [ ] Create update server or use GitHub Releases
- [ ] Create `CREATE_PATCH.bat` script
- [ ] Set up Git tagging workflow

#### Phase 6: Documentation

- [ ] Create `README.md` with quick start
- [ ] Create `PROJECT_SYNOPSIS.md` with architecture
- [ ] Create `CHANGELOG.md` for version history
- [ ] Document build process (copy this guide!)

### Common Gotchas

1. **Python paths in CLI scripts**
   - Must add `python-modules/` to `sys.path`
   - Use `os.path.dirname(os.path.abspath(__file__))` for script location

2. **server.js paths**
   - Must check `process.resourcesPath` for production
   - Development fallback to `__dirname`

3. **extraResources paths**
   - Use `to:` carefully - it's relative to `resources/`
   - Use `filter:` to exclude unnecessary files

4. **Electron security**
   - Always use `contextIsolation: true`
   - Always use `nodeIntegration: false`
   - Use `preload.js` for IPC

5. **Build order**
   - Frontend build MUST happen before Electron package
   - Python folder MUST exist before build

---

## Troubleshooting Common Issues

### Build Issues

**Issue:** `electron-builder` fails with "Cannot find module"
- **Solution**: Run `npm install` again, check `package.json` dependencies

**Issue:** Python not found during build
- **Solution**: Run `prepare-python.bat` or manually download Python embeddable package

**Issue:** Build succeeds but installer is huge (>1GB)
- **Solution**: Check `extraResources` - may be including too much
- **Solution**: Add `.gitignore` patterns to `filter` arrays

### Installation Issues

**Issue:** Installer shows "Windows protected your PC"
- **Solution**: Code sign the installer (requires certificate, ~$100/year)
- **Workaround**: Click "More info" → "Run anyway"

**Issue:** App crashes on startup
- **Solution**: Check Electron DevTools Console (F12)
- **Solution**: Check server.js logs (stdout/stderr)
- **Solution**: Verify Python scripts are in `resources/scripts/`

**Issue:** Python scripts not found
- **Solution**: Check `process.resourcesPath` in server.js
- **Solution**: Verify `extraResources` in package.json
- **Solution**: Check paths in electron-builder output logs

### Runtime Issues

**Issue:** "ModuleNotFoundError: No module named 'X'"
- **Solution**: Check `sys.path.insert()` in CLI script
- **Solution**: Verify `python-modules/` is in `extraResources`
- **Solution**: Check `python311._pth` configuration

**Issue:** Python script hangs or times out
- **Solution**: Increase `maxBuffer` in exec() call
- **Solution**: Add timeout handling
- **Solution**: Use spawn() instead of exec() for long-running scripts

**Issue:** File permissions errors on Windows
- **Solution**: Run as administrator (not recommended for production)
- **Solution**: Install to user directory, not Program Files
- **Solution**: Use `allowToChangeInstallationDirectory: true`

---

## Version History

| Version | Changes |
|---------|---------|
| 0.0.1 | Initial beta release, manual build process documented |
| 0.0.2 | Planned: Git-based auto-update system |

---

## Resources

### Official Documentation

- [Electron Builder](https://www.electron.build/)
- [Electron Updater](https://www.electron.build/auto-update)
- [Electron Documentation](https://www.electronjs.org/docs/latest/)
- [NSIS Installer](https://nsis.sourceforge.io/)
- [Vite](https://vitejs.dev/)

### Python Embeddable Package

- [Python Downloads](https://www.python.org/downloads/windows/)
- [Python Embeddable Package Docs](https://docs.python.org/3/using/windows.html#embedded-distribution)

### Example Projects

- VS Code (Electron + auto-updates)
- Discord (Electron + delta updates)
- Slack (Electron + background updates)

---

## Summary

**For AI Assistants Reading This:**

When replicating this setup for a new project:

1. **Create folder structure**: `src/`, `electron/`, `scripts/`, `python-modules/`, `python/`
2. **Configure `package.json`**: Add electron-builder config with `files`, `extraResources`, NSIS settings
3. **Set up Python paths**: Add `sys.path.insert()` to all CLI scripts
4. **Create `BUILD.bat`**: Automate clean, Python check, frontend build, Electron package
5. **Test build**: Run `.\BUILD.bat`, verify installer in `dist/`
6. **Test installation**: Install on clean system, verify app starts and Python scripts run
7. **Optional: Enable auto-updates**: Configure electron-updater, create update server

**Key Concepts:**
- `files` = goes in ASAR (can't execute)
- `extraResources` = goes outside ASAR (can execute)
- `process.resourcesPath` = path to `resources/` in installed app
- Python CLI scripts need `sys.path.insert()` for imports
- `server.js` needs conditional paths for dev vs production

**This guide is complete and ready to be used for other projects.**

