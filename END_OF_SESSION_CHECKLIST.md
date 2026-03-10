# End of Session Checklist

**Do this at the end of every coding session** so the next session (or future you) can pick up cleanly.

**Last completed:** _(Update this line when you finish a session — e.g. "2026-03-10 — Consolidated docs, .cursorrules for distributable app, CONFIGURATION.md.")_

---

## Do at end of every session

1. **Summarize what happened** — In a sentence or two: main goal and what you shipped or changed.
2. **Add (or update) a session entry in `SESSIONS.md`** — Date (YYYY-MM-DD), goal, files created/modified (with line counts for large files), changes summary, testing done, next session priorities. Optionally: known issues, technical debt.
3. **Update file headers in modified `.py` files** — Set `LAST VERIFIED` to today’s date; update `SAFE TO MODIFY` or `FRAGILE` sections if needed.
4. **File size check** — List modified files with current line count. Flag anything approaching 800+ lines (see .cursorrules); note if extraction/splitting is needed.
5. **Quick verification** — At least: app runs (`npm run dev:all` or run backend + frontend), `npm run build` passes, no new linter errors on modified files. If you touched Python scripts: run the affected flow (e.g. Process Quiz, Extract Grades) once.
6. **Optional but useful** — Note any known issues or shortcuts taken; write down the top 1–3 next-session priorities.

**Quick prompt you can paste to AI:**
```
End of session. Do the end-of-session checklist:
1. Summarize what we did and add a session entry to SESSIONS.md (today's date, goal, files modified with line counts, summary, next priorities).
2. Update file headers in all modified .py files (LAST VERIFIED = today).
3. List modified files with line counts; flag any approaching 800+ lines.
4. Confirm build passes and no new linter errors; if we changed Python/backend flow, note what to verify (e.g. Process Quiz, Extract Grades).
```

---

## Template (fill this out, then add entry to SESSIONS.md)

Copy the template below and fill it out at the end of each development session. When you're done, **add a corresponding session entry to `SESSIONS.md`** (goal, files changed, summary, testing, next priorities) so the session history stays up to date.

### Session — YYYY-MM-DD — [Brief title]

**Status:** _Completed / In progress_

#### 1. Files modified
- **Modified:** `path/to/file.py` (N lines)
- **Created:** `path/to/newfile.ts` (N lines)

#### 2. Changes summary
- **Main goal:** _One line._
- **Accomplished:** _Bullet list of what you did._
- **Remains (if any):** _What’s left or deferred._

#### 3. File size check
- `Option2.tsx`: **N lines** — _✓ OK / ⚠️ approaching 800_
- _List other modified files with line counts._

#### 4. File headers
- [ ] All modified `.py` files have `LAST VERIFIED: YYYY-MM-DD` (and SAFE TO MODIFY / FRAGILE if needed).

#### 5. Testing
- [ ] App runs (frontend + backend)
- [ ] `npm run build` — ✓
- [ ] No new linter errors on modified files
- [ ] _If you touched a workflow:_ e.g. Process Quiz or Extract Grades run once and succeed

#### 6. Documentation
- [ ] Session entry added to `SESSIONS.md`
- [ ] If significant: `docs/all-docs/PROJECT_SYNOPSIS.md` or `docs/CONFIGURATION.md` updated (and "Last updated" date)
- [ ] If user-facing: `README.md` updated

#### 7. Known issues (optional)
- _Any shortcuts, TODOs, or things to fix next time._

#### 8. Next session priorities
1. _First priority_
2. _Second_
3. _Third_

---

## Example session entry (for reference)

### Session — 2026-02-05 — Documentation and config setup

**Status: Completed**

#### 1. Files modified
- **Created:** `START_HERE.md`
- **Created:** `docs/CONFIGURATION.md`
- **Modified:** `python-modules/ocr_utils.py` (load API key from .env)
- **Modified:** `SESSIONS.md` (added this session)

#### 2. Changes summary
- **Main goal:** Add orientation docs and secure API keys.
- **Accomplished:** START_HERE and CONFIGURATION guides; API key moved to .env; SESSIONS.md and END_OF_SESSION_CHECKLIST in place.

#### 3. File size check
- All modified/created files under 800 lines ✓

#### 4. File headers
- [x] `ocr_utils.py` — LAST VERIFIED: 2026-02-05

#### 5. Testing
- [x] App runs
- [x] `npm run build` — ✓
- [x] No new linter errors

#### 6. Documentation
- [x] Session entry in SESSIONS.md
- [x] PROJECT_SYNOPSIS / CONFIGURATION referenced where needed

#### 7. Next session priorities
1. Add file headers to remaining Python modules
2. Test with sample data after config path changes

---

## Weekly review (optional)

**Once a week (e.g. Friday):**
- Review `SESSIONS.md` for the past week; summarize what was accomplished.
- Check for patterns that should be documented in PROJECT_SYNOPSIS or CONFIGURATION.
- Triage "Next session priorities" and technical debt.

**Remember:** Doing this at the end of every session keeps the project easy to resume and helps anyone (or AI) understand what changed. Aim for a few minutes; the template and prompt above make it fast.
