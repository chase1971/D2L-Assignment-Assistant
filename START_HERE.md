# START HERE - D2L Assignment Assistant

> **IMPORTANT: Read this file FIRST before making any changes to the codebase**

---

## 🎯 Quick Overview

This is a desktop application (Electron + React + Python) for grading D2L/Brightspace assignment submissions. It:
1. Extracts student submissions from ZIP files
2. Combines PDFs for efficient grading
3. Uses OCR to extract handwritten grades
4. Updates Import File.csv for upload to D2L

---

## 📖 Documentation Structure

**Read in this order:**

1. **START_HERE.md** (this file) - First-time setup and orientation
2. **docs/all-docs/PROJECT_SYNOPSIS.md** - Complete system architecture  
3. **README.md** - Installation, dependencies, and usage
4. **END_OF_SESSION_CHECKLIST.md** - Development workflow
5. **.cursorrules** - AI coding guidelines

**For specific tasks:**
- **REMOVE_DRIVE_DETECTION.md** - How to remove C:/G: drive logic (user-specific)
- **SESSIONS.md** - Development history
- File headers in Python modules - Module-specific details

---

## 🚨 CRITICAL: User-Specific Configuration

### This System is Currently Configured for Original Developer

The system has **hard-coded drive detection** that switches between:
- C: drive: `C:\Users\chase\My Drive\Rosters etc\`
- G: drive (with 3 path variations): `G:\Users\chase\My Drive\Rosters etc\`

**⚠️ NEW USERS MUST REMOVE THIS LOGIC ⚠️**

### For New Users:

**Read `REMOVE_DRIVE_DETECTION.md` and follow the instructions to:**
1. Remove C:/G: drive switching logic
2. Replace with single configurable base path
3. Use environment variable or config file

**This is a 5-minute change that makes the system work for your folder structure.**

---

## 🔑 Environment Setup

### Required: Google Cloud Vision API Key

1. Create `.env` file in project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   GOOGLE_VISION_API_KEY=your_api_key_here
   ```

3. Get API key from [Google Cloud Console](https://console.cloud.google.com/)

4. The system auto-loads this on startup

5. Falls back to Tesseract OCR if Google Vision unavailable

---

## 📦 Dependencies

### Quick Install

**Python packages:**
```bash
pip install -r requirements.txt
```

**Node.js packages:**
```bash
npm install
```

### System Dependencies

**Poppler** (REQUIRED for PDF to image conversion):
- Windows: https://github.com/oschwartz10612/poppler-windows/releases/
- Extract to `C:\poppler\`
- Mac: `brew install poppler`
- Linux: `sudo apt-get install poppler-utils`

**Tesseract OCR** (Optional fallback):
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

**Python 3.11** (For development - bundled in builds):
- Windows: https://www.python.org/downloads/

---

## 🏗️ Architecture

### Tech Stack

- **Frontend:** React 18 + TypeScript + Vite + TailwindCSS
- **Backend:** Node.js + Express
- **Desktop:** Electron 28
- **Python:** 3.11 (embedded in builds)
- **OCR:** Google Cloud Vision API + Tesseract fallback

### Project Structure

```
D2L-Assignment-Assistant/
├── src/                        # React frontend (TypeScript)
│   ├── components/             # UI components
│   ├── services/               # API client
│   └── styles/                 # Global CSS
│
├── electron/                   # Electron main process
│   ├── main.js                 # Entry point
│   └── preload.js              # IPC bridge
│
├── server/                     # Node.js backend (loaded by server.js)
│   ├── app.js                  # Express app
│   └── routes/                 # API routes
│
├── scripts/                    # Python CLI scripts
│   ├── process_quiz_cli.py     # Quiz processing
│   ├── extract_grades_cli.py   # Grade extraction
│   └── ...
│
├── python-modules/             # Shared Python logic
│   ├── grading_processor.py    # Core orchestration
│   ├── ocr_utils.py            # OCR integration
│   └── ...
│
├── server.js                   # Backend launcher (runs server/app.js)
├── .env                        # API keys (NOT in Git)
├── .env.example                # Template for .env
├── requirements.txt            # Python dependencies
└── package.json                # Node dependencies
```

---

## 🚀 Quick Start

### For Development

1. **Install dependencies:**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Set up `.env` file** (see Environment Setup above)

3. **Remove drive detection** (see REMOVE_DRIVE_DETECTION.md)

4. **Start development servers:**
   ```bash
   npm run dev:all
   ```
   This starts both frontend (Vite) and backend (Express) concurrently.

5. **Application opens automatically** at http://localhost:3000

### For Production Build

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Package as desktop app:**
   ```bash
   npm run package
   ```

3. **Installer created in** `dist/` folder

---

## 📂 Expected Folder Structure

The system expects:

```
<YourBasePath>\<ClassName>\
├── Import File.csv          # Student roster
└── grade processing\        # Created automatically
    ├── PDFs\
    │   └── 1combinedpdf.pdf
    └── [Student folders]
```

**Current system uses:** `C:\Users\chase\My Drive\Rosters etc\`

**You should change this to your own base path!** See `REMOVE_DRIVE_DETECTION.md`

---

## 🔧 Main Components

### Python Modules (python-modules/)

- **grading_processor.py** - Main orchestration logic
- **pdf_operations.py** - PDF manipulation
- **ocr_utils.py** - OCR integration
- **import_file_handler.py** - CSV operations
- **grade_parser.py** - Grade text parsing
- **name_matching.py** - Fuzzy name matching
- **submission_processor.py** - Submission handling

### Python CLI Scripts (scripts/)

- **process_quiz_cli.py** - Process quiz submissions
- **process_completion_cli.py** - Auto-assign completion grades
- **extract_grades_cli.py** - Extract grades from graded PDF
- **split_pdf_cli.py** - Split combined PDF back to individual files
- **clear_data_cli.py** - Clean up temporary files
- **class_manager_cli.py** - Class CRUD operations
- **helper_cli.py** - Utility functions

### Frontend Components (src/components/)

- **Option2.tsx** - Main UI controller
- **LogTerminal.tsx** - Real-time log display
- **ZipSelectionModal.tsx** - Multiple ZIP selection
- **ClassSetupModal.tsx** - Class configuration
- **NavigationBar.tsx** - Top navigation

---

## 💡 Development Workflow

### When Making Changes

1. **Read file header** in the module you're editing (if it exists)
2. **Check FRAGILE AREAS** section for warnings
3. **Make your changes**
4. **Test thoroughly** before committing
5. **Update SESSIONS.md** with what changed
6. **Follow END_OF_SESSION_CHECKLIST.md**

### Logging System

This app uses a dual-channel logging system:
- `user_log(message)` - User-facing (shown in UI)
- `dev_log(message)` - Debug (hidden from users)

**Always use emojis in user-facing logs** (see logging standards in `.cursorrules`)

---

## 🐛 Common Issues

### "Oops. You've chosen the wrong file or class"
- Less than 30% match rate between submissions and roster
- Check class name is correct
- Verify Import File.csv exists

### OCR Not Detecting Grades
- Grades must be in top 15% of page
- Write clearly in designated region
- Red ink works best

### Drive/Path Errors
- **You need to remove drive detection logic!**
- See `REMOVE_DRIVE_DETECTION.md`

### "Could not start server"
- Port 3000 or 5000 may be in use
- Close other applications using these ports

---

## 🎓 Learning the Codebase

**Recommended reading order:**

1. **This file** - Orientation ✓
2. **REMOVE_DRIVE_DETECTION.md** - Remove user-specific logic (REQUIRED)
3. **docs/all-docs/PROJECT_SYNOPSIS.md** - Full architecture
4. **.cursorrules** - Coding guidelines
5. **grading_processor.py** - Core workflow
6. **Option2.tsx** - Frontend controller
7. **Other files** as needed

---

## ⚠️ Before Making Changes

**Always check:**
- [ ] Have you removed drive detection if you're a new user?
- [ ] Is your `.env` file set up?
- [ ] Do you have all dependencies installed?
- [ ] Have you read the relevant file headers?
- [ ] Do you have sample data to test with?

---

## 🔗 External References

- **Global Patterns:** `C:\Users\chase\Documents\Programs\cursor-patterns\`
- **Local Patterns:** `.cursor-patterns/` in this project
- **Electron Docs:** https://www.electronjs.org/docs
- **React Docs:** https://react.dev

---

## 📝 Next Steps

**For Original Developer (Chase):**
- Continue using as-is
- Follow END_OF_SESSION_CHECKLIST.md for changes

**For New Users:**
1. ⚠️ **Read `REMOVE_DRIVE_DETECTION.md` NOW**
2. Remove C:/G: drive logic
3. Configure your base folder path
4. Set up `.env` file
5. Install dependencies
6. Test with sample data
7. Read docs/all-docs/PROJECT_SYNOPSIS.md for full understanding

---

**Last Updated:** 2026-02-05
**Version:** 0.0.1 (Beta)
**Status:** Production-ready (requires configuration for new users)
