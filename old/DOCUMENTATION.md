# D2L Assignment Extractor - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Development](#development)
7. [Build Process](#build-process)
8. [Troubleshooting](#troubleshooting)
9. [File Structure](#file-structure)
10. [Known Issues and Solutions](#known-issues-and-solutions)

---

## Project Overview

The D2L Assignment Extractor is a standalone desktop application built with Electron that processes Canvas quiz submissions. It extracts ZIP files, combines PDFs, and prepares quizzes for grading. The application was converted from a web-based interface project into a double-clickable executable that can be installed on Windows.

### Key Requirements Met
- ✅ Standalone executable (no web server required)
- ✅ Windows installer with custom installation location
- ✅ First-run setup wizard for folder configuration
- ✅ Automatic Python dependency installation
- ✅ Developer Mode for frontend customization
- ✅ Comprehensive error handling and logging
- ✅ Console window for real-time debugging
- ✅ Uninstaller with process cleanup

---

## Architecture

### Technology Stack
- **Frontend**: React (built with Create React App)
- **Backend**: Electron (Node.js + Express.js)
- **Python Scripts**: CLI tools for quiz processing
- **Build Tool**: electron-builder with NSIS installer
- **Package Format**: app.asar (Electron's archive format)

### Application Flow

```
User launches executable
    ↓
Electron main process starts
    ↓
Express server starts on localhost:5000
    ↓
Console window opens (for logging)
    ↓
Check config.json for first-run status
    ↓
If first-run: Show setup wizard
    ↓
If configured: Load React frontend from app.asar
    ↓
User interacts with React UI
    ↓
React makes API calls to Express backend
    ↓
Express spawns Python scripts with user paths
    ↓
Python scripts process quizzes and return results
```

### Key Components

1. **Main Process** (`electron/main.js`)
   - Window management
   - Backend server (Express)
   - IPC handlers
   - Config management
   - Error handling

2. **Renderer Process** (React Frontend)
   - Quiz grader UI
   - Settings panel
   - Developer Mode toggle
   - Real-time logging

3. **Python Backend**
   - `process_quiz_cli.py` - Extract and combine quiz PDFs
   - `process_completion_cli.py` - Process completion assignments
   - `extract_grades_cli_fixed.py` - Extract grades from PDFs
   - `split_pdf_cli.py` - Split combined PDFs
   - `cleanup_data_cli.py` - Clean up temporary files
   - `config_reader.py` - Read Electron config.json

---

## Features

### 1. First-Run Setup Wizard
- Prompts user to select:
  - Downloads folder (where Canvas ZIP files are saved)
  - Rosters folder (parent folder containing class folders)
- Validates paths before saving
- Creates `config.json` in `%APPDATA%\D2L Assignment Extractor\`

### 2. Developer Mode
- Toggle in Settings panel
- When enabled:
  - App attempts to load frontend from `http://localhost:3000` (React dev server)
  - User must run `npm start` in `react-frontend` directory
  - Allows real-time frontend development without rebuilding
- When disabled:
  - App loads from packaged `app.asar` (production build)

### 3. Console Window
- Separate Electron window that opens automatically
- Displays all logs, errors, and warnings in real-time
- Dark theme with color-coded log levels:
  - Info: White
  - Warning: Yellow
  - Error: Red
  - Success: Green

### 4. Error Handling
- Global error handlers catch all uncaught exceptions
- Native OS error dialogs (`dialog.showErrorBox()`) always show errors
- Persistent error logging to `error.log` file
- Errors displayed in console window
- Errors shown in main window if possible

### 5. Class Folder Detection
- Automatically finds class folders by matching class codes
- Example: If user selects "CA 4203", finds "TTH 930-1050 CA 4203" folder
- Handles both full folder names and class codes

---

## Installation

### For End Users

1. Run the installer: `D2L Assignment Extractor Setup 1.0.0.exe`
2. Choose installation directory (default: `C:\Users\[username]\Documents\Programs\D2L Assignment Extractor`)
3. Complete installation
4. Launch the application
5. On first run:
   - Setup wizard will appear
   - Select Downloads folder
   - Select Rosters folder
   - Python packages will be installed automatically (may take a few minutes)

### Installation Location
- **Executable**: `C:\Users\[username]\Documents\Programs\D2L Assignment Extractor\`
- **Config File**: `%APPDATA%\D2L Assignment Extractor\config.json`
- **Error Log**: `%APPDATA%\D2L Assignment Extractor\error.log`
- **Start Menu**: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Education\`

### Uninstallation
- Use Windows "Add or Remove Programs"
- Or run the uninstaller from the installation directory
- The uninstaller will:
  - Close any running instances of the app
  - Delete the installation directory
  - Remove Start Menu shortcuts
  - **Note**: AppData folder is NOT deleted (to preserve user config)

---

## Configuration

### Config File Location
`%APPDATA%\D2L Assignment Extractor\config.json`

### Config Structure
```json
{
  "firstRun": false,
  "downloadsPath": "C:\\Users\\chase\\Downloads",
  "rostersPath": "C:\\Users\\chase\\My Drive\\Rosters etc",
  "developerMode": false
}
```

### Config Validation
- `downloadsPath` and `rostersPath` must be non-empty strings
- `rostersPath` must point to the parent folder (not a specific class folder)
- If paths are invalid, `firstRun` is forced to `true` to show setup wizard

### Reopening Setup
- Click "Settings" button in the app
- Click "Reopen Setup" button
- This allows changing folder paths without reinstalling

---

## Development

### Prerequisites
- Node.js (v16 or higher)
- Python 3.x
- npm

### Project Structure
```
Quiz-extraction/
├── electron/              # Electron main process
│   ├── main.js           # Main entry point
│   ├── preload.js        # IPC bridge
│   └── routes/           # Express API routes
│       └── quizRoutes.js
├── react-frontend/       # React application
│   ├── src/
│   │   ├── pages/
│   │   │   └── QuizGrader.js
│   │   └── services/
│   │       └── quizGraderService.js
│   └── build/            # Production build (generated)
├── renderer/             # Setup wizard HTML
│   └── setup.html
├── scripts/              # Build and utility scripts
│   ├── after-pack.js     # Post-build verification
│   └── uninstall-pre-check.nsh  # Uninstaller script
├── *.py                  # Python CLI scripts
├── package.json          # Main package config
└── requirements.txt      # Python dependencies
```

### Running in Development Mode

1. **Start React Dev Server** (for Developer Mode):
   ```bash
   cd react-frontend
   npm start
   ```

2. **Run Electron App**:
   ```bash
   npm start
   ```

3. **Enable Developer Mode**:
   - Open the app
   - Click "Settings" button
   - Toggle "Enable Developer Mode"
   - Restart the app
   - App will now load from `http://localhost:3000`

### Building for Production

1. **Build React Frontend**:
   ```bash
   cd react-frontend
   npm run build
   ```

2. **Build Electron Installer**:
   ```bash
   npm run build:win
   ```

3. **Output**:
   - Installer: `dist/D2L Assignment Extractor Setup 1.0.0.exe`
   - Unpacked app: `dist/win-unpacked/`

### Automated Build Script
Run `REBUILD-AND-INSTALL.bat` to:
1. Build React frontend
2. Build Electron installer
3. Automatically launch the installer

---

## Build Process

### Electron Builder Configuration
Located in `package.json` under `"build"`:

```json
{
  "appId": "com.d2l.assignmentextractor",
  "productName": "D2L Assignment Extractor",
  "directories": {
    "output": "dist"
  },
  "files": [
    "electron/**/*",
    "react-frontend/build/**/*",
    "react-frontend/src/**/*",
    "react-frontend/public/**/*",
    "scripts/**/*",
    "*.py",
    "requirements.txt",
    "renderer/**/*"
  ],
  "win": {
    "target": [{
      "target": "nsis",
      "arch": ["x64"]
    }]
  },
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "perMachine": false,
    "createDesktopShortcut": true,
    "createStartMenuShortcut": true,
    "shortcutName": "D2L Assignment Extractor",
    "deleteAppDataOnUninstall": false,
    "runAfterFinish": true,
    "menuCategory": "Education"
  }
}
```

### Packaging Process
1. Electron Builder packages all files into `app.asar`
2. React build files are included in `app.asar`
3. Python scripts are included at root of `app.asar`
4. NSIS creates Windows installer
5. `after-pack.js` verifies React build is included

### Important Notes
- `express.static` does NOT work with `app.asar`
- Custom middleware reads files from `app.asar` using `fs.readFileSync`
- Path resolution uses `app.getAppPath()` for packaged apps
- Python scripts are accessed via `app.getAppPath()` (root of `app.asar`)

---

## Troubleshooting

### Blank White Screen
**Symptoms**: App opens but shows blank white screen, no errors visible

**Possible Causes**:
1. Backend server failed to start
2. React build files missing from `app.asar`
3. Port 5000 already in use
4. File path resolution issues

**Solutions**:
1. Check console window for errors
2. Check `error.log` in `%APPDATA%\D2L Assignment Extractor\`
3. Verify React build was included: Run `npx asar list app.asar | findstr react-frontend/build`
4. Check if port 5000 is in use: `netstat -ano | findstr :5000`
5. Rebuild the installer

### Setup Wizard Not Appearing
**Symptoms**: App launches directly to main UI, but paths are invalid

**Possible Causes**:
1. Config file exists but has invalid paths
2. `rostersPath` points to a class folder instead of parent folder

**Solutions**:
1. Delete `%APPDATA%\D2L Assignment Extractor\config.json`
2. Restart the app
3. Or click "Settings" → "Reopen Setup"

### 404 Error When Processing Quizzes
**Symptoms**: "Script not found" error when clicking "Process Quizzes"

**Possible Causes**:
1. Python scripts not found in `app.asar`
2. `pythonScriptsPath` incorrectly resolved
3. Python executable not found in PATH

**Solutions**:
1. Verify Python scripts are in `app.asar`: `npx asar list app.asar | findstr .py`
2. Check Python is installed: `python --version`
3. Verify `pythonScriptsPath` uses `app.getAppPath()` for packaged apps

### Files Locked During Uninstallation
**Symptoms**: Uninstaller fails with "file in use" error

**Possible Causes**:
1. App process still running
2. Windows Explorer has folder open
3. Background process holding file handles

**Solutions**:
1. Close all instances of the app
2. Close Windows Explorer windows showing the installation folder
3. Restart computer if necessary
4. Use `FORCE-DELETE-OLD-APP.bat` script (if available)

### Developer Mode Not Working
**Symptoms**: App doesn't load from `localhost:3000` when Developer Mode enabled

**Possible Causes**:
1. React dev server not running
2. Port 3000 not accessible
3. CORS issues

**Solutions**:
1. Ensure `npm start` is running in `react-frontend` directory
2. Verify `http://localhost:3000` is accessible in browser
3. Check console window for specific error messages

---

## File Structure

### Electron Main Process
- **`electron/main.js`**: Main entry point, window management, server startup
- **`electron/preload.js`**: Secure IPC bridge between renderer and main
- **`electron/routes/quizRoutes.js`**: Express API routes for quiz processing

### React Frontend
- **`react-frontend/src/pages/QuizGrader.js`**: Main quiz grader UI component
- **`react-frontend/src/services/quizGraderService.js`**: API service layer
- **`react-frontend/build/`**: Production build (generated, included in package)

### Setup Wizard
- **`renderer/setup.html`**: First-run setup wizard HTML

### Python Scripts
- **`process_quiz_cli.py`**: Extract ZIP, combine PDFs
- **`process_completion_cli.py`**: Process completion assignments
- **`extract_grades_cli_fixed.py`**: Extract grades from PDFs
- **`split_pdf_cli.py`**: Split combined PDFs
- **`cleanup_data_cli.py`**: Clean up temporary files
- **`config_reader.py`**: Read Electron config.json
- **`helper_cli.py`**: Helper utilities
- **`grade_parser.py`**: Grade parsing logic
- **`grading_processor.py`**: Grade processing logic
- **`ocr_utils.py`**: OCR utilities

### Build Scripts
- **`scripts/after-pack.js`**: Post-build verification
- **`scripts/uninstall-pre-check.nsh`**: NSIS uninstaller script
- **`REBUILD-AND-INSTALL.bat`**: Automated build and install script

---

## Known Issues and Solutions

### Issue 1: `express.static` Doesn't Work with `app.asar`
**Problem**: `express.static()` cannot serve files from `app.asar` archives.

**Solution**: Implemented custom Express middleware that:
- Reads files from `app.asar` using `fs.readFileSync`
- Sets appropriate `Content-Type` headers
- Handles directory listings and index files

**Location**: `electron/main.js` - `startBackendServer()` function

### Issue 2: Python Scripts Not Found in Packaged App
**Problem**: `pythonScriptsPath` was incorrectly resolved for packaged apps.

**Solution**: Changed from:
```javascript
path.join(path.dirname(process.execPath), 'resources', 'app')
```
To:
```javascript
app.getAppPath()
```

**Location**: `electron/main.js` - Python script path resolution

### Issue 3: `spawn ENOENT` Error
**Problem**: `child_process.spawn` with `shell: true` couldn't find `cmd.exe`.

**Solution**: 
- Changed `shell: true` to `shell: false`
- Explicitly pass `PATH` and `SystemRoot` in `env` option
- Spawn Python directly instead of through shell

**Location**: `electron/routes/quizRoutes.js` - `runPythonScript()` function

### Issue 4: Setup Window Loading Main App
**Problem**: Static file middleware was intercepting `/setup.html` requests.

**Solution**: 
- Reordered middleware to define `/setup.html` route handler BEFORE static file middleware
- Added explicit skip condition in static file middleware

**Location**: `electron/main.js` - Express middleware order

### Issue 5: Config Validation Not Catching Invalid Paths
**Problem**: Config file could have empty strings or invalid paths, but setup wizard wouldn't appear.

**Solution**: Enhanced `loadConfig()` to:
- Check if `downloadsPath` and `rostersPath` are non-empty strings
- Validate `rostersPath` doesn't point to a class folder
- Force `firstRun: true` if paths are invalid

**Location**: `electron/main.js` - `loadConfig()` function

### Issue 6: Uninstaller Not Deleting Files
**Problem**: Uninstaller runs but files remain.

**Possible Causes**:
- Processes still running
- File handles locked
- Permissions issues

**Solution**: 
- `uninstall-pre-check.nsh` kills processes before uninstall
- User may need to manually close Explorer windows
- May require computer restart in extreme cases

**Location**: `scripts/uninstall-pre-check.nsh`

### Issue 7: Class Folder Not Found
**Problem**: User selects "CA 4203" but app can't find the folder.

**Solution**: Implemented `findClassFolder()` helper that:
- Searches for folders containing the class code
- Handles both full folder names and class codes
- Returns the first matching folder

**Location**: `electron/routes/quizRoutes.js` - `findClassFolder()` function

---

## API Endpoints

All API endpoints are prefixed with `/api/quiz`:

- `POST /api/quiz/process` - Process quizzes (extract ZIP, combine PDFs)
- `POST /api/quiz/process-selected` - Process selected quizzes
- `POST /api/quiz/process-completion` - Process completion assignments
- `POST /api/quiz/process-completion-selected` - Process selected completions
- `POST /api/quiz/extract-grades` - Extract grades from PDFs
- `POST /api/quiz/split-pdf` - Split combined PDF
- `POST /api/quiz/clear-data` - Clear temporary data
- `GET /api/quiz/open-folder` - Open a folder in Explorer
- `GET /api/quiz/test` - Test endpoint to verify server is running

---

## Environment Variables

### Development
- `NODE_ENV=development` (when running `npm start`)
- React dev server runs on `http://localhost:3000`
- Electron loads from dev server when Developer Mode enabled

### Production
- `NODE_ENV=production` (when packaged)
- Express server runs on `http://localhost:5000`
- React app served from `app.asar`

---

## Logging

### Log Locations
1. **Console Window**: Real-time display of all logs
2. **Error Log File**: `%APPDATA%\D2L Assignment Extractor\error.log`
3. **Node.js Console**: When running from command line

### Log Levels
- **INFO**: General information (white)
- **WARNING**: Warnings (yellow)
- **ERROR**: Errors (red)
- **SUCCESS**: Success messages (green)

### Logging Functions
- `writeLog(message, isError)`: Write to file and console window
- `sendToConsole(message, type)`: Send to console window only
- `showErrorDialog(title, message)`: Show native OS error dialog

---

## Python Dependencies

Python packages are automatically installed on first run. Dependencies are listed in `requirements.txt`:

- pdf2image
- Pillow
- pytesseract
- PyPDF2
- (and others as needed)

Installation happens via:
```python
subprocess.run([python, '-m', 'pip', 'install', '-r', 'requirements.txt'])
```

---

## Security Considerations

1. **IPC Communication**: Uses `contextBridge` for secure IPC
2. **Node Integration**: Disabled in renderer process (except console window)
3. **Context Isolation**: Enabled in main window
4. **File System Access**: Limited to user-selected folders
5. **Network**: Only localhost connections (no external network access)

---

## Future Improvements

1. **Auto-update**: Implement Electron auto-updater
2. **Multi-platform**: Support macOS and Linux
3. **Better error recovery**: Retry mechanisms for failed operations
4. **Progress indicators**: Better feedback during long operations
5. **Batch processing**: Process multiple classes at once
6. **Export options**: Export grades to different formats
7. **Settings persistence**: Remember more user preferences

---

## Support and Maintenance

### Common Commands

**Build installer**:
```bash
npm run build:win
```

**Run in development**:
```bash
npm start
```

**Build React frontend**:
```bash
cd react-frontend && npm run build
```

**Check installed app**:
```powershell
Test-Path "C:\Users\chase\Documents\D2L Assignment Extractor"
```

**View error log**:
```powershell
Get-Content "$env:APPDATA\D2L Assignment Extractor\error.log"
```

### Getting Help

1. Check the console window for real-time errors
2. Check `error.log` for persistent error history
3. Verify config.json has valid paths
4. Ensure Python is installed and in PATH
5. Rebuild installer if files are missing

---

## Version History

### Version 1.0.0
- Initial release
- Standalone Electron app
- First-run setup wizard
- Developer Mode
- Console window for debugging
- Comprehensive error handling
- Windows installer with NSIS

---

## License

MIT License - See LICENSE file for details

---

## Author

Chase

---

*Last Updated: [Current Date]*
*Documentation Version: 1.0.0*

