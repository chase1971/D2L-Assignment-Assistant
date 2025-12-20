# D2L Assignment Assistant - Project Synopsis

**Version 0.0.1 (Beta)**

## Purpose

A desktop application to streamline grading of D2L/Brightspace assignment submissions. It extracts PDFs from downloaded ZIP files, combines them for grading, extracts grades via OCR, and prepares files for re-upload to D2L.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File Organization](#file-organization)
3. [Key Components](#key-components)
4. [Data Flow & Workflows](#data-flow--workflows)
5. [Building & Development](#building--development)
6. [Configuration](#configuration)
7. [User Messages System](#user-messages-system)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│  (Option2.tsx, LogTerminal.tsx, ZipSelectionModal.tsx)      │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API (port 3000 → 5000)
┌─────────────────────▼───────────────────────────────────────┐
│                  Node.js Backend (server.js)                 │
│  - Routes API calls to Python scripts                        │
│  - Parses JSON responses                                     │
│  - Handles file operations                                   │
│  - Path: scripts/ (dev) or resources/scripts/ (packaged)    │
└─────────────────────┬───────────────────────────────────────┘
                      │ subprocess.exec()
┌─────────────────────▼───────────────────────────────────────┐
│                    Python CLI Scripts                        │
│  - scripts/*.py (entry points)                               │
│  - python-modules/*.py (shared logic)                        │
│  - PDF processing, OCR, CSV manipulation                     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Backend**: Node.js + Express
- **Desktop**: Electron 28
- **Python**: 3.11 (embedded in installer)
- **Key Libraries**: 
  - PyPDF2, pdf2image (PDF processing)
  - Google Vision API, Tesseract (OCR)
  - pandas (CSV manipulation)
  - express, multer (backend)

---

## File Organization

```
D2L-Assignment-Assistant/
├── src/                           # React frontend (TypeScript)
│   ├── components/                # UI components
│   │   ├── Option2.tsx            # Main UI controller
│   │   ├── LogTerminal.tsx        # Log display
│   │   ├── NavigationBar.tsx      # Top navigation
│   │   ├── ZipSelectionModal.tsx  # Multiple ZIP selection
│   │   ├── ClassSetupModal.tsx    # Class configuration
│   │   └── ...
│   ├── services/
│   │   └── quizGraderService.ts   # API client
│   └── styles/                    # Global CSS
│
├── electron/                      # Electron process files
│   ├── main.js                    # Electron entry point
│   └── preload.js                 # IPC bridge
│
├── scripts/                       # Python CLI scripts (entry points)
│   ├── process_quiz_cli.py        # Quiz processing
│   ├── process_completion_cli.py  # Completion processing
│   ├── extract_grades_cli.py      # Grade extraction
│   ├── split_pdf_cli.py           # PDF split & rezip
│   ├── clear_data_cli.py          # Data cleanup
│   ├── class_manager_cli.py       # Class CRUD operations
│   └── helper_cli.py              # Utility functions
│
├── python-modules/                # Reusable Python modules
│   ├── grading_processor.py       # Core orchestration logic
│   ├── pdf_operations.py          # PDF manipulation
│   ├── import_file_handler.py     # CSV operations
│   ├── backup_utils.py            # Folder backup logic
│   ├── name_matching.py           # Fuzzy name matching
│   ├── ocr_utils.py               # OCR wrappers
│   ├── config_reader.py           # Config management
│   ├── file_utils.py              # File operations
│   └── user_messages/             # User-facing logging
│       ├── logger.py              # Log formatting
│       ├── catalog.py             # Message definitions
│       └── file_logger.py         # File logging
│
├── docs/                          # Documentation
│   ├── plans/                     # Planning documents
│   └── archived/                  # Outdated docs (reference only)
│
├── dev-tools/                     # Development utilities
│   ├── tests/                     # pytest tests
│   ├── test_scenario_runner.py    # Test automation
│   └── prepare-python.bat         # Python setup script
│
├── server.js                      # Express backend
├── BUILD.bat                      # Build automation script
├── package.json                   # Node dependencies & scripts
├── classes.json                   # Class configurations
├── requirements.txt               # Python dependencies
├── README.md                      # Quick start guide
├── CHANGELOG.md                   # Version history
└── PROJECT_SYNOPSIS.md            # This file
```

---

## Key Components

### Frontend (`src/`)

| File | Purpose |
|------|---------|
| `components/Option2.tsx` | Main UI - class selection, action buttons, state management |
| `components/LogTerminal.tsx` | Displays log messages with clickable file/folder paths |
| `components/ZipSelectionModal.tsx` | Modal for selecting from multiple ZIP files |
| `components/NavigationBar.tsx` | Top bar with class dropdown, theme toggle, window controls |
| `components/ServerStatusIndicator.tsx` | Backend server connection status |
| `components/ClassSetupModal.tsx` | Class configuration wizard |
| `services/quizGraderService.ts` | API client for all backend calls |

### Backend (`server.js`)

- Express server on port 5000 (auto-increments if busy)
- Key API Routes:
  - `/api/quiz/process` - Process quizzes (extract, combine PDFs)
  - `/api/quiz/process-completion` - Process completions (auto-grade 10 points)
  - `/api/quiz/extract-grades` - OCR grade extraction
  - `/api/quiz/split-pdf` - Split combined PDF back to individual files
  - `/api/quiz/split-pdf-upload` - Upload and split a PDF file
  - `/api/quiz/open-folder` - Open grade processing folder
  - `/api/quiz/clear-data` - Delete processing data
  - `/api/classes/*` - Class management CRUD operations

### Python CLI Scripts (`scripts/`)

| File | Purpose | Called By |
|------|---------|-----------|
| `process_quiz_cli.py` | Extract ZIP, combine PDFs, add watermarks | `/api/quiz/process` |
| `process_completion_cli.py` | Auto-assign 10 points to all students | `/api/quiz/process-completion` |
| `extract_grades_cli.py` | OCR grades from annotated combined PDF | `/api/quiz/extract-grades` |
| `split_pdf_cli.py` | Split combined PDF, rezip for D2L upload | `/api/quiz/split-pdf` |
| `clear_data_cli.py` | Delete or archive processing folders | `/api/quiz/clear-data` |
| `class_manager_cli.py` | Manage `classes.json` | `/api/classes/*` |
| `helper_cli.py` | List classes, open folders | Various |

**Import Path Configuration:**
All CLI scripts add `python-modules/` to `sys.path` for imports:
```python
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_MODULES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'python-modules')
sys.path.insert(0, PYTHON_MODULES_DIR)
```

### Python Modules (`python-modules/`)

| File | Purpose |
|------|---------|
| `grading_processor.py` | Core orchestration - ZIP extraction, PDF combining, grade updates |
| `import_file_handler.py` | Load, validate, and update D2L Import File.csv |
| `pdf_operations.py` | Create combined PDFs, add watermarks, split PDFs |
| `submission_processor.py` | Process individual student submissions |
| `backup_utils.py` | Backup existing folders before processing |
| `name_matching.py` | Fuzzy matching of student names |
| `ocr_utils.py` | Google Vision and Tesseract OCR wrappers |
| `config_reader.py` | Read/write configuration (paths, settings) |
| `file_utils.py` | File operations and path utilities |
| `user_messages/` | Centralized user-facing logging system |

---

## Data Flow & Workflows

### 1. Process Quizzes

```
User clicks "Process Quizzes"
  ↓
Frontend → POST /api/quiz/process { drive, className }
  ↓
Backend → process_quiz_cli.py <drive> <className>
  ↓
Python:
  1. Find ZIP in Downloads (or prompt user to select)
  2. Backup existing "grade processing" folder (if exists)
  3. Extract ZIP to "grade processing <CLASS> <ASSIGNMENT>/"
  4. Extract PDF from each student's folder
  5. Combine all PDFs with watermarks (student names)
  6. Save as "grade processing/PDFs/<ASSIGNMENT>.pdf"
  7. Open combined PDF in default viewer
  ↓
Return: { success, logs, combined_pdf_path, assignment_name }
```

### 2. Extract Grades

```
User grades combined PDF (writes scores on pages)
  ↓
User clicks "Extract Grades"
  ↓
Frontend → POST /api/quiz/extract-grades { drive, className }
  ↓
Backend → extract_grades_cli.py <drive> <className>
  ↓
Python:
  1. Find combined PDF in "grade processing/PDFs/"
  2. Load Import File.csv from class roster folder
  3. For each student in Import File:
     a. Find their page(s) in combined PDF (by watermark)
     b. Extract first page
     c. Run OCR (Google Vision → Tesseract fallback)
     d. Parse grade using regex patterns
     e. Calculate confidence score
  4. Update Import File.csv with extracted grades
  5. Add "Verify" column for low-confidence grades
  6. Save updated Import File
  7. Create "first pages.pdf" for manual review
  ↓
Return: { success, logs, confidenceScores: { studentName: confidence% } }
```

### 3. Split PDF & Rezip

```
User clicks "Split PDF & Rezip"
  ↓
Frontend → POST /api/quiz/split-pdf { drive, className, assignmentName }
  ↓
Backend → split_pdf_cli.py <drive> <className> <assignmentName>
  ↓
Python:
  1. Load combined PDF from "grade processing/PDFs/"
  2. For each student folder in "unzipped folders/":
     a. Extract their page(s) from combined PDF
     b. Save as individual PDF in their folder
  3. Create ZIP from all student folders
  4. Save ZIP in grade processing folder (ready for D2L upload)
  5. Log clickable path to ZIP location
  ↓
Return: { success, logs }
```

### 4. Process Completions

```
User clicks "Process Completions"
  ↓
Frontend → POST /api/quiz/process-completion { drive, className, dontOverride }
  ↓
Backend → process_completion_cli.py <drive> <className> [--dont-override]
  ↓
Python:
  1. Find ZIP in Downloads
  2. Backup existing folder (if exists)
  3. Extract ZIP
  4. Load Import File.csv
  5. For each student in ZIP:
     a. Assign 10 points (or skip if --dont-override and grade exists)
  6. Update Import File.csv
  7. Open Import File for review
  ↓
Return: { success, logs }
```

### 5. Clear Data

```
User clicks "Clear Data" → selects option
  ↓
Frontend → POST /api/quiz/clear-data { 
  drive, className, assignmentName,
  saveFoldersAndPdf, saveCombinedPdf, deleteEverything, deleteArchivedToo
}
  ↓
Backend → clear_data_cli.py <drive> <className> <assignmentName> [flags]
  ↓
Python:
  1. Find "grade processing <ASSIGNMENT>" folder
  2. Apply selective deletion:
     - Save individual PDFs + unzipped folders (if saveFoldersAndPdf)
     - Save combined PDF only (if saveCombinedPdf)
     - Delete all processing folders (if deleteEverything)
     - Include archived folder (if deleteArchivedToo)
  3. Move saved items to "archived/" folder (if applicable)
  4. Delete processing folder
  ↓
Return: { success, logs }
```

---

## Building & Development

### Building the Installer

**Automated Build Script:**
```bash
.\BUILD.bat
```

This script:
1. Cleans old `dist/` and `dist-frontend/` folders
2. Checks for bundled Python (downloads if missing)
3. Builds frontend: `npm run build` (Vite)
4. Packages Electron app: `npm run package` (electron-builder)
5. Launches installer: `dist/D2L Assignment Assistant Setup 0.0.1.exe`

**Manual Steps:**
```bash
# Clean
Remove-Item dist, dist-frontend -Recurse -Force

# Build frontend
npm run build

# Package Electron app
npm run package
```

### Development Mode

**Start both frontend and backend:**
```bash
npm run dev:all
```

This runs:
- Frontend: `http://localhost:3000` (Vite dev server)
- Backend: `http://localhost:5000` (Express server)

**Or run separately:**
```bash
# Terminal 1: Backend
npm run dev:server

# Terminal 2: Frontend
npm run dev:frontend
```

### Python Environment

**In Development:**
- Uses system Python (PATH)
- Install dependencies: `pip install -r requirements.txt`

**In Packaged App:**
- Uses bundled Python: `python/` folder (included in installer)
- Downloaded by `BUILD.bat` if missing
- Python 3.11 embeddable package

### Testing

**Run Python tests:**
```bash
cd dev-tools
pytest tests/
```

**Test scenarios:**
```bash
python dev-tools/test_scenario_runner.py
```

---

## Configuration

### `config.json` (User Configuration)

Created automatically on first run:

```json
{
  "rostersPath": "C:\\Users\\<USERNAME>\\My Drive\\Rosters etc",
  "downloadsPath": "C:\\Users\\<USERNAME>\\Downloads",
  "developerMode": false
}
```

### `classes.json` (Class Configuration)

Managed via "CLASS SETUP" in the app:

```json
{
  "classes": [
    {
      "id": "1",
      "value": "TTH 11-1220 FM 4202",
      "label": "FM 4202 (TTH 11:00-12:20)",
      "rosterFolderPath": "C:\\Users\\chase\\My Drive\\Rosters etc\\TTH 11-1220 FM 4202",
      "isProtected": false
    }
  ]
}
```

### Class Folder Structure (Expected)

```
C:\Users\<USERNAME>\My Drive\Rosters etc\
└── <CLASS_NAME>/
    ├── Import File.csv                    # D2L grade import file
    ├── grade processing <CLASS> <ASSIGNMENT>/
    │   ├── PDFs/
    │   │   ├── <ASSIGNMENT>.pdf           # Combined PDF
    │   │   ├── <USERNAME>.pdf             # Individual PDFs
    │   │   └── first pages.pdf            # For grade verification
    │   ├── unzipped folders/
    │   │   └── <D2L_FOLDER_NAME>/         # Extracted student submissions
    │   │       └── <FILES>
    │   └── archived/                      # Backups from "Clear Data"
    └── grade processing <CLASS> <ASSIGNMENT> backup 1/  # Auto-backups
```

---

## User Messages System

All user-facing log messages are centralized in `python-modules/user_messages/`.

### Structure

```
python-modules/user_messages/
├── logger.py          # Main logging functions (log, log_raw)
├── catalog.py         # Message definitions (CATALOG dict)
└── file_logger.py     # File logging (for debugging)
```

### Usage in Python Scripts

```python
from user_messages import log

# Success message
log("QUIZ_PROCESS_SUCCESS", count=25)

# Error message with error code
log("ERR_ZIP_NOT_FOUND", assignment_name="Quiz 1")

# Warning
log("BACKUP_FOLDER_IN_USE", folder_name="grade processing")

# Info with clickable path
log("SPLIT_ZIP_LOCATION", path="C:\\Users\\...\\grade processing\\")
```

### Message Format

```python
CATALOG = {
    "MESSAGE_KEY": (
        "📝 Message text with {variable} placeholders",
        "LEVEL",      # SUCCESS, ERROR, WARNING, INFO
        "E1234"       # Error code (for ERR_* messages)
    )
}
```

### Log Levels & Formatting

| Level | Icon | Color (Dark Mode) | Color (Light Mode) |
|-------|------|-------------------|-------------------|
| SUCCESS | ✅ | `text-green-400` | `text-green-700` |
| ERROR | ❌ | `text-red-400` | `text-red-700` |
| WARNING | ⚠️ | `text-yellow-400` | `text-yellow-700` |
| INFO | ℹ️ | `text-blue-400` | `text-blue-700` |

**Clickable Paths:**
- Folder paths are automatically made clickable in the UI
- Use `log("SPLIT_ZIP_LOCATION", path=...)` to show folder locations

---

## Troubleshooting

### Common Issues

**"Cannot connect to backend"**
- Backend server not running
- Port 5000 in use (server auto-increments to 5001, 5002, etc.)
- Check terminal for server startup message

**"Python not found"**
- In development: Install Python 3.9+ and add to PATH
- In packaged app: Ensure `python/` folder exists next to executable

**"ModuleNotFoundError: No module named 'user_messages'"**
- In development: Scripts are now in `scripts/`, modules in `python-modules/`
- Check that `sys.path.insert()` is at the top of CLI scripts
- In packaged app: Check `package.json` `extraResources` configuration

**"Zip file does not contain student assignments"**
- ZIP structure doesn't match expected D2L format
- Expected: `<ASSIGNMENT>/*.../Submission attachment(s)/file.pdf`
- Actual: May be a different download format

**"Backup folder in use"**
- Close File Explorer windows viewing the grade processing folder
- Close any open PDFs from that folder
- Google Drive sync may be locking the folder - pause sync temporarily

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

**Current Version: 0.0.1 (Beta)**
- First beta release
- Bug fixes for split PDF, backup errors, duplicate logging
- Organized project structure

---

## Future Enhancements

- Git-based automatic patching system
- Support for other LMS platforms (Canvas, Moodle)
- Batch processing across multiple assignments
- Advanced OCR settings and manual correction UI
- Student analytics and grade distribution reports
