# Complete Guide: Packaging React + Python Projects as Electron Executables

## Overview

This guide documents how to convert a React frontend + Python backend project into a standalone Windows executable using Electron. Follow this guide exactly to avoid the common pitfalls that cause hours of debugging.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Dependencies and Setup](#2-dependencies-and-setup)
3. [Electron Configuration](#3-electron-configuration)
4. [The ASAR Problem (Critical)](#4-the-asar-problem-critical)
5. [Python Execution in Packaged Apps](#5-python-execution-in-packaged-apps)
6. [Environment Variables and PATH](#6-environment-variables-and-path)
7. [Window Configuration](#7-window-configuration)
8. [Build Process](#8-build-process)
9. [Common Errors and Solutions](#9-common-errors-and-solutions)
10. [Future Improvements](#10-future-improvements)
11. [Checklist for New Projects](#11-checklist-for-new-projects)

---

## 1. Project Structure

### Required Directory Layout

```
project-root/
├── electron/
│   ├── main.js              # Electron main process
│   ├── preload.js           # IPC bridge (secure communication)
│   └── routes/
│       └── quizRoutes.js    # Express API routes
├── react-frontend/
│   ├── src/
│   │   ├── pages/           # React components
│   │   └── services/        # API service layer
│   ├── build/               # Production build (generated)
│   └── package.json
├── renderer/
│   └── setup.html           # Any standalone HTML files
├── *.py                      # Python scripts (at root level)
├── requirements.txt          # Python dependencies
├── package.json              # Main Electron package config
└── node_modules/
```

### Key Points

- **Python scripts MUST be at the root level** (not in subdirectories) for easier ASAR unpacking
- **React build folder** is generated and included in the package
- **electron/main.js** is the entry point specified in package.json

---

## 2. Dependencies and Setup

### package.json Dependencies

```json
{
  "name": "your-app-name",
  "version": "1.0.0",
  "main": "electron/main.js",
  "dependencies": {
    "cors": "^2.8.5",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "electron": "^28.3.3",
    "electron-builder": "^24.13.3"
  },
  "scripts": {
    "start": "electron .",
    "build": "electron-builder",
    "build:win": "electron-builder --win"
  }
}
```

### Install Commands

```bash
# In project root
npm install

# In react-frontend
cd react-frontend
npm install
npm run build
cd ..
```

---

## 3. Electron Configuration

### package.json Build Configuration

```json
{
  "build": {
    "appId": "com.yourcompany.appname",
    "productName": "Your App Name",
    "directories": {
      "output": "dist"
    },
    "files": [
      "electron/**/*",
      "react-frontend/build/**/*",
      "renderer/**/*",
      "*.py",
      "requirements.txt",
      "package.json"
    ],
    "asarUnpack": [
      "*.py",
      "requirements.txt"
    ],
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ]
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "perMachine": false,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

### CRITICAL: The `asarUnpack` Setting

**This is the most important setting.** Without it, Python cannot read scripts from inside the ASAR archive.

```json
"asarUnpack": [
  "*.py",
  "requirements.txt"
]
```

This extracts Python files to `app.asar.unpacked/` where Python can read them.

---

## 4. The ASAR Problem (Critical)

### What is ASAR?

ASAR (Atom Shell Archive) is Electron's archive format. When you build an Electron app, all files are packed into `app.asar`. 

**The Problem:** Node.js can read from ASAR archives, but Python cannot.

### Symptoms of ASAR Issues

- Python script errors like "file not found" even though the file exists
- Scripts work in development but fail in packaged app
- Error messages showing paths like `app.asar/script.py`

### The Solution

1. **Add `asarUnpack` to package.json** (see above)

2. **Update path resolution in main.js:**

```javascript
// In main.js - where you set the Python scripts path
let pythonScriptsPath = app.getAppPath();

// Check if we're running from a packaged app (app.asar)
if (pythonScriptsPath.includes('app.asar')) {
  // Replace app.asar with app.asar.unpacked for Python scripts
  pythonScriptsPath = pythonScriptsPath.replace('app.asar', 'app.asar.unpacked');
}
```

### Verification

After building, check that files exist in:
- `resources/app.asar` - Main app files (Node.js can read)
- `resources/app.asar.unpacked/` - Python files (Python can read)

---

## 5. Python Execution in Packaged Apps

### Finding Python

The packaged app runs in a restricted environment. You must:

1. **Find Python dynamically** using `where` command
2. **Get the full path** (not just 'python')
3. **Use `exec` instead of `spawn`** for reliability

### Python Detection Code

```javascript
const { exec } = require('child_process');

function findPython() {
  return new Promise((resolve, reject) => {
    // Use 'where' command to find Python's actual path
    exec('where python', (error, stdout) => {
      if (error || !stdout) {
        reject(new Error('Python not found'));
        return;
      }
      // Get first path from output and normalize it
      const paths = stdout.trim().split('\n').map(p => p.trim()).filter(p => p);
      if (paths.length > 0) {
        resolve(path.normalize(paths[0]));
      } else {
        reject(new Error('Python not found in PATH'));
      }
    });
  });
}
```

### Running Python Scripts

**Use `exec`, not `spawn`:**

```javascript
const { exec } = require('child_process');

async function runPythonScript(scriptName, args) {
  const pythonPath = await findPython();
  const scriptPath = path.join(pythonScriptsPath, scriptName);
  
  // Build command with proper quoting for Windows
  const argsString = args.map(arg => `"${arg}"`).join(' ');
  const command = `"${pythonPath}" "${scriptPath}" ${argsString}`;
  
  const options = {
    cwd: pythonScriptsPath,
    windowsHide: true,
    maxBuffer: 10 * 1024 * 1024 // 10MB buffer
  };
  
  exec(command, options, (error, stdout, stderr) => {
    // Handle result
  });
}
```

### Why `exec` Instead of `spawn`?

| Method | Shell | Works in Packaged App? |
|--------|-------|------------------------|
| `spawn` with `shell: false` | No | ❌ ENOENT errors |
| `spawn` with `shell: true` | Yes, needs to find cmd.exe | ❌ cmd.exe ENOENT |
| `exec` | Yes, built-in | ✅ Works reliably |

`exec` internally handles shell execution and is more reliable in packaged Electron apps.

---

## 6. Environment Variables and PATH

### The PATH Problem

In development, Node.js inherits your full environment (including Python in PATH).

In a packaged app, the environment is minimal and may not include:
- Python installation directories
- System32 (needed for cmd.exe)
- Other tools

### Setting Up Environment

```javascript
// Build proper PATH for the child process
const systemRoot = process.env.SystemRoot || 'C:\\Windows';
const system32Path = path.join(systemRoot, 'System32');

const existingPath = process.env.PATH || process.env.Path || '';
const newPath = existingPath 
  ? `${system32Path};${systemRoot};${existingPath}`
  : `${system32Path};${systemRoot}`;

const env = { 
  ...process.env, 
  PYTHONIOENCODING: 'utf-8',
  PATH: newPath,
  Path: newPath,  // Windows uses both
  SystemRoot: systemRoot,
  windir: systemRoot
};
```

---

## 7. Window Configuration

### Frameless Fullscreen Window

```javascript
mainWindow = new BrowserWindow({
  width: 1200,
  height: 800,
  show: true,
  frame: false,           // No window border/title bar
  autoHideMenuBar: true,  // No menu bar
  webPreferences: {
    preload: path.join(__dirname, 'preload.js'),
    nodeIntegration: false,
    contextIsolation: true
  }
});

// Maximize to fill screen
mainWindow.maximize();
```

### Adding Window Controls (Close/Reload)

Since there's no frame, add buttons in your React app:

**preload.js:**
```javascript
contextBridge.exposeInMainWorld('electronAPI', {
  closeWindow: () => ipcRenderer.invoke('close-window'),
  reloadWindow: () => ipcRenderer.invoke('reload-window'),
  // ... other methods
});
```

**main.js:**
```javascript
ipcMain.handle('close-window', () => {
  if (mainWindow) mainWindow.close();
  app.quit();
});

ipcMain.handle('reload-window', () => {
  if (mainWindow) mainWindow.reload();
});
```

**React component:**
```jsx
<button onClick={() => window.electronAPI.closeWindow()}>Close</button>
<button onClick={() => window.electronAPI.reloadWindow()}>Reload</button>
```

---

## 8. Build Process

### Step-by-Step Build

```bash
# 1. Build React frontend
cd react-frontend
npm run build
cd ..

# 2. Build Electron installer
npm run build:win

# 3. Installer is at: dist/Your App Name Setup X.X.X.exe
```

### Automated Build Script (REBUILD-AND-INSTALL.bat)

```batch
@echo off
echo Building React Frontend...
cd react-frontend
call npm run build
if errorlevel 1 exit /b 1
cd ..

echo Building Electron Installer...
call npm run build:win
if errorlevel 1 exit /b 1

echo Done! Installer at: dist\
start "" "dist\Your App Name Setup 1.0.0.exe"
```

---

## 9. Common Errors and Solutions

### Error: `spawn python ENOENT`

**Cause:** Node.js can't find Python executable

**Solution:**
1. Use `exec` instead of `spawn`
2. Find Python path dynamically with `where python`
3. Use the full path to python.exe

### Error: `spawn C:\WINDOWS\system32\cmd.exe ENOENT`

**Cause:** When using `shell: true`, Node.js can't find cmd.exe

**Solution:**
1. Use `exec` instead of `spawn` with shell
2. Or ensure System32 is in PATH before spawning

### Error: Script not found (but file exists)

**Cause:** Python script is inside ASAR archive

**Solution:**
1. Add `asarUnpack` to package.json for Python files
2. Update path to use `app.asar.unpacked` instead of `app.asar`

### Error: Blank white screen

**Cause:** React build not included or Express server not serving files

**Solution:**
1. Verify `react-frontend/build/` is included in `files` array
2. Check Express static file middleware is configured correctly
3. For files inside ASAR, use `fs.readFileSync` instead of `express.static`

### Error: Setup window doesn't load

**Cause:** HTML files inside ASAR can't be loaded with `loadFile()`

**Solution:**
1. Serve HTML via Express: `http://localhost:5000/setup.html`
2. Use `loadURL()` instead of `loadFile()`

---

## 10. Future Improvements

### Bundling Python (For Users Without Python)

If users don't have Python installed, you have two options:

#### Option A: Python Embeddable Distribution

1. Download Python embeddable package from python.org
2. Include it in your project
3. Update `findPython()` to check for bundled Python first

```javascript
function findPython() {
  // Check for bundled Python first
  const bundledPython = path.join(app.getAppPath().replace('app.asar', 'app.asar.unpacked'), 'python', 'python.exe');
  if (fs.existsSync(bundledPython)) {
    return bundledPython;
  }
  
  // Fall back to system Python
  return findSystemPython();
}
```

**package.json update:**
```json
"asarUnpack": [
  "*.py",
  "requirements.txt",
  "python/**/*"
]
```

#### Option B: First-Run Python Installation

1. Check if Python exists on first run
2. If not, prompt user to install it
3. Or automatically download and install

### Auto-Updates

Add electron-updater for automatic updates:

```bash
npm install electron-updater
```

### Code Signing

For distribution, sign your app to avoid security warnings:

```json
"win": {
  "certificateFile": "path/to/certificate.pfx",
  "certificatePassword": "password"
}
```

---

## 11. Checklist for New Projects

### Before Starting

- [ ] React frontend is working standalone
- [ ] Python scripts work from command line
- [ ] Node.js and npm installed
- [ ] Electron and electron-builder installed

### Project Setup

- [ ] Create proper directory structure
- [ ] Set up package.json with correct `main` entry
- [ ] Configure `build.files` to include all needed files
- [ ] Configure `build.asarUnpack` for Python files
- [ ] Create electron/main.js with Express server
- [ ] Create electron/preload.js for IPC

### Python Integration

- [ ] Python scripts at root level (not in subdirectories)
- [ ] Use `exec` instead of `spawn` for running Python
- [ ] Implement `findPython()` function with `where` command
- [ ] Update script paths to use `app.asar.unpacked`
- [ ] Set proper environment variables (PATH, SystemRoot)

### React Integration

- [ ] React build included in `files` array
- [ ] Express serves static files from React build
- [ ] Custom middleware for ASAR file reading (if needed)
- [ ] API endpoints working

### Window Configuration

- [ ] Window settings (frame, size, etc.)
- [ ] Window controls in React app (if frameless)
- [ ] IPC handlers for window controls

### Testing

- [ ] Test in development mode (`npm start`)
- [ ] Test packaged app (not just unpacked)
- [ ] Test on clean machine (no dev tools)
- [ ] Verify Python scripts run correctly
- [ ] Verify all UI features work

### Build & Distribution

- [ ] React frontend builds successfully
- [ ] Electron installer builds successfully
- [ ] Installer works on target machines
- [ ] Uninstaller works correctly

---

## Quick Reference: Key Code Snippets

### Path Resolution for Unpacked Files

```javascript
let scriptsPath = app.getAppPath();
if (scriptsPath.includes('app.asar')) {
  scriptsPath = scriptsPath.replace('app.asar', 'app.asar.unpacked');
}
```

### Running Python with exec

```javascript
const command = `"${pythonPath}" "${scriptPath}" ${args.map(a => `"${a}"`).join(' ')}`;
exec(command, { cwd: scriptsPath, windowsHide: true }, callback);
```

### Finding Python

```javascript
exec('where python', (err, stdout) => {
  const pythonPath = stdout.trim().split('\n')[0].trim();
  resolve(path.normalize(pythonPath));
});
```

### Environment Setup

```javascript
const env = { 
  ...process.env,
  PATH: `${process.env.SystemRoot}\\System32;${process.env.PATH}`,
  PYTHONIOENCODING: 'utf-8'
};
```

---

## Summary

The key challenges when packaging React + Python as Electron apps:

1. **ASAR archives** - Python can't read from them; use `asarUnpack`
2. **Python execution** - Use `exec` instead of `spawn`; find full path with `where`
3. **Environment** - Packaged apps have minimal environment; set PATH explicitly
4. **File serving** - Use Express server; custom middleware for ASAR files

Follow this guide step-by-step and check off items in the checklist to avoid the common pitfalls that cause hours of debugging.

---

*Last Updated: November 2024*
*Based on real-world debugging of D2L Assignment Extractor project*

