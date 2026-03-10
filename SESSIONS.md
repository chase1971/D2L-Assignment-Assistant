# Development Sessions

> **Purpose:** Track development history, changes, and decisions for the D2L Assignment Assistant

---

## 2026-02-05 - Documentation and Security Setup

**What we did:**
- Created START_HERE.md as entry point for new users
- Added REMOVE_DRIVE_DETECTION.md with step-by-step instructions
- Added END_OF_SESSION_CHECKLIST.md for development workflow
- Secured API keys by moving to .env file (excluded from Git)
- Created .env.example template file
- Updated .cursorrules to reference START_HERE.md

**Files created:**
- START_HERE.md (orientation guide for new users)
- REMOVE_DRIVE_DETECTION.md (guide to remove user-specific drive logic)  
- END_OF_SESSION_CHECKLIST.md (development workflow guide)
- SESSIONS.md (this file - development history)
- .env (API key storage, not in Git)
- .env.example (template for new users)

**Files modified:**
- python-modules/ocr_utils.py (removed hardcoded API key, loads from environment)

**Patterns used:**
- File Headers Standard (from cursor-patterns/file-headers.md)
- Environment variable security pattern
- Documentation structure from Calendar app

**Next session tasks:**
- [ ] Add file headers to all Python modules
- [ ] Update .cursorrules to reference START_HERE.md
- [ ] Test with sample data after drive detection removal
- [ ] Review documentation with new developer

**Technical debt:**
- Python modules still need file headers
- Drive detection logic still present (documented for removal)

**Notes:**
- API key security is now properly implemented
- Documentation structure ready for handoff
- System still uses hard-coded C:/G: drive paths (intentionally documented for user removal)
- Both Quiz-extraction and D2L-Assignment-Assistant now have complete documentation

---

## 2026-03-10 - Fix Split-and-Rezip Using Wrong PDF

**What we did:**
- Diagnosed bug where split-and-rezip was splitting the `_GRADES_ONLY` PDF (first pages only) instead of the full multi-page combined PDF
- The root cause: the file picker filtered for any PDF containing "combined PDF" in the name, and since `_GRADES_ONLY` is created after the original, it was the newest file and got selected
- Fixed by excluding `_GRADES_ONLY` files from the search

**Files modified:**
- `python-modules/grading_processor.py` — added `and 'GRADES_ONLY' not in f` to the combined PDF file picker in `run_reverse_process()`

**Patterns used:**
- Minimal change — one line fix

**Next session tasks:**
- [ ] Test split-and-rezip end-to-end with a real quiz to confirm graded multi-page PDFs are returned correctly

**Technical debt:**
- None introduced

**Notes:**
- The `_GRADES_ONLY` PDF exists purely to reduce data sent to Google Vision API (only first pages needed for OCR). It should never be used as the source for splitting.
- The full graded combined PDF is never deleted by the split-and-rezip flow — a missing file in one instance was a Google Drive sync delay (large file)
- Committed and pushed to GitHub (commit 94f7e59)

---

## Session Template (Copy for Future Sessions)

```markdown
## YYYY-MM-DD - [Brief Title]

**What we did:**
- Change 1
- Change 2

**Files created:**
- path/to/file.py (description)

**Files modified:**
- path/to/file.py (what changed)

**Patterns used:**
- Pattern name

**Next session tasks:**
- [ ] Task 1
- [ ] Task 2

**Technical debt:**
- Any shortcuts taken

**Notes:**
- Important decisions or observations
```

---

**Last Updated:** 2026-03-10
