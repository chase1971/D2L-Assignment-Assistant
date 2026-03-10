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

**Doc index (find everything):** **docs/README.md**

**Read in this order:**

1. **START_HERE.md** (this file) - First-time setup and orientation
2. **docs/all-docs/PROJECT_SYNOPSIS.md** - Complete system architecture
3. **README.md** - Installation, dependencies, and usage
4. **END_OF_SESSION_CHECKLIST.md** - Development workflow
5. **.cursorrules** - AI coding guidelines and tips for making the app distributable

**For specific tasks:**
- **docs/CONFIGURATION.md** - Making the app work for other professors (paths, config, removing hardcoded logic)
- **SESSIONS.md** - Development history
- File headers in Python modules - Module-specific details

---

## 🚨 CRITICAL: User-Specific Configuration

### This System Has Hardcoded Fallbacks

Path resolution (in **python-modules/config_reader.py**) uses config when available but **falls back to hardcoded paths** (e.g. C:/G: drives, username `chase`). That makes the app work only on the original developer’s machine unless you change it.

**⚠️ TO GIVE THIS APP TO OTHER PROFESSORS:** Remove those fallbacks and rely on config (or first-run setup) only. See **docs/CONFIGURATION.md** for what to change and how.

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

3. **Configure paths for your machine** (see docs/CONFIGURATION.md)

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

**Base path** comes from config (CLASS SETUP or config file). To make the app work for any professor, see **docs/CONFIGURATION.md**.

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
- Paths come from config; hardcoded fallbacks may point to the wrong place. See **docs/CONFIGURATION.md** to make the app use config only.

### "Could not start server"
- Port 3000 or 5000 may be in use
- Close other applications using these ports

---

## 🎓 Learning the Codebase

**Recommended reading order:**

1. **This file** - Orientation ✓
2. **docs/CONFIGURATION.md** - Making the app work for other professors (if distributing)
3. **docs/all-docs/PROJECT_SYNOPSIS.md** - Full architecture
4. **.cursorrules** - Coding guidelines and AI tips
5. **grading_processor.py** - Core workflow
6. **Option2.tsx** - Frontend controller
7. **Other files** as needed (see **docs/README.md** for full doc index)

---

## ⚠️ Before Making Changes

**Always check:**
- [ ] Is config set up for your machine? (See docs/CONFIGURATION.md if distributing or moving to another machine.)
- [ ] Is your `.env` file set up?
- [ ] Do you have all dependencies installed?
- [ ] Have you read the relevant file headers?
- [ ] Do you have sample data to test with?

---

## 🔗 External References

- **Global Patterns:** `C:\Users\chase\Documents\Programs\cursor-patterns\`
- **Documentation index:** `docs/README.md` — single index for all docs
- **Local Patterns:** `.cursor-patterns/` in this project
- **Electron Docs:** https://www.electronjs.org/docs
- **React Docs:** https://react.dev

---

## 📝 Next Steps

**For Original Developer (Chase):**
- Continue using as-is
- Follow END_OF_SESSION_CHECKLIST.md for changes

**For New Users / Distributing to Other Professors:**
1. ⚠️ **Read docs/CONFIGURATION.md** — how to remove hardcoded paths and make the app work for any professor
2. Set up config (CLASS SETUP or config file) and base folder path
3. Set up `.env` file (API keys)
4. Install dependencies
5. Test with sample data
6. Read docs/all-docs/PROJECT_SYNOPSIS.md for full understanding

---

**Last Updated:** 2026-02-05
**Version:** 0.0.1 (Beta)
**Status:** Production-ready (requires configuration for new users)
