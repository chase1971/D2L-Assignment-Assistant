# D2L Assignment Assistant - Project Synopsis

## Purpose
A desktop application to streamline grading of D2L/Brightspace assignment submissions. It extracts PDFs from downloaded ZIP files, combines them for grading, extracts grades via OCR, and prepares files for re-upload to D2L.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│  (Option2.tsx, LogTerminal.tsx, ZipSelectionModal.tsx)      │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API
┌─────────────────────▼───────────────────────────────────────┐
│                  Node.js Backend (server.js)                 │
│  - Routes API calls to Python scripts                        │
│  - Parses JSON responses                                     │
│  - Handles file operations                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ subprocess
┌─────────────────────▼───────────────────────────────────────┐
│                    Python Scripts                            │
│  - PDF processing (PyPDF2)                                   │
│  - OCR grade extraction (Google Vision / Tesseract)          │
│  - CSV manipulation (pandas)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### Frontend (`src/`)

| File | Purpose |
|------|---------|
| `components/Option2.tsx` | Main UI - class selection, action buttons, state management |
| `components/LogTerminal.tsx` | Displays log messages, filters technical output |
| `components/ZipSelectionModal.tsx` | Modal for selecting from multiple ZIP files |
| `components/NavigationBar.tsx` | Top bar with class dropdown and controls |
| `components/ServerStatusIndicator.tsx` | Shows backend server status |
| `services/quizGraderService.ts` | API client for all backend calls |

### Backend (`server.js`)

- Express server on port 5000
- Routes:
  - `/api/quiz/process` - Process quizzes (extract, combine PDFs)
  - `/api/quiz/process-completion` - Process completions (auto-grade 10 points)
  - `/api/quiz/extract-grades` - OCR grade extraction
  - `/api/quiz/split-pdf` - Split combined PDF back to individual files
  - `/api/quiz/open-folder` - Open grade processing folder
  - `/api/quiz/clear-data` - Delete processing data

### Python Scripts

| File | Purpose |
|------|---------|
| `grading_processor.py` | Core orchestration - ZIP extraction, PDF combining, grade updates |
| `import_file_handler.py` | Load, validate, and update D2L Import File.csv |
| `pdf_operations.py` | Create combined PDFs, add watermarks, split PDFs |
| `extract_grades_cli.py` | OCR-based grade extraction from graded PDFs |
| `submission_processor.py` | Process individual student submissions |
| `name_matching.py` | Fuzzy matching of student names |
| `ocr_utils.py` | Google Vision and Tesseract OCR wrappers |
| `config_reader.py` | Read configuration (paths, settings) |
| `backup_utils.py` | Backup existing folders before processing |

### CLI Scripts (called by server.js)

| File | Purpose |
|------|---------|
| `process_quiz_cli.py` | Quiz processing entry point |
| `process_completion_cli.py` | Completion processing entry point |
| `extract_grades_cli.py` | Grade extraction entry point |
| `split_pdf_cli.py` | PDF split and rezip entry point |
| `helper_cli.py` | Utility commands (list classes, open folders) |
| `cleanup_data_cli.py` | Clear processing data |

---

## Data Flow

### Process Quizzes
1. User selects class, clicks "Process Quizzes"
2. Frontend calls `/api/quiz/process`
3. Backend runs `process_quiz_cli.py`
4. Script finds ZIP in Downloads, extracts to "grade processing" folder
5. Extracts PDFs from each student folder
6. Combines all PDFs into one (watermarked with student names)
7. Opens combined PDF for grading

### Extract Grades
1. User grades the combined PDF (writes scores on pages)
2. User clicks "Extract Grades"
3. Backend runs `extract_grades_cli.py`
4. Script uses OCR to read grades from first page of each student's section
5. Updates Import File.csv with extracted grades
6. Reports confidence levels for each extraction

### Split PDF
1. After grading, user clicks "Split PDF"
2. Backend runs `split_pdf_cli.py`
3. Script splits combined PDF back into individual student PDFs
4. Creates new ZIP file matching D2L's expected format
5. ZIP is ready for re-upload to D2L

---

## File Structure

```
D2L-Assignment-Assistant/
├── src/                      # React frontend
│   ├── components/           # UI components
│   └── services/             # API services
├── server.js                 # Node.js backend
├── *.py                      # Python processing scripts
├── preview_user_messages.py  # Log message preview tool
├── config.json               # User configuration
└── package.json              # Node dependencies
```

---

## Configuration

`config.json` (created on first run):
```json
{
  "rostersPath": "C:\\Users\\chase\\My Drive\\Rosters etc",
  "downloadsPath": "C:\\Users\\chase\\Downloads",
  "developerMode": false
}
```

---

## Import File Structure

The D2L Import File.csv has this structure:
- Column A: OrgDefinedId
- Column B: Username
- Column C: First Name
- Column D: Last Name
- Column E: Email
- Column F: End-of-Line Indicator
- Columns after E (before End-of-Line): Grade columns
- Column after End-of-Line: Verify column (for low-confidence grades)

---

## User Message Preview

All user-facing log messages are defined in `preview_user_messages.py`. This file serves as:
1. A single source of truth for all user messages
2. A preview tool to see how messages will appear
3. A GUI editor for modifying messages

Run with: `python preview_user_messages.py`
Or GUI: `python preview_user_messages_gui.py`

---

## Development

### Start Development Server
```bash
npm run dev:all  # Starts both frontend and backend
```

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
pytest tests/
```

