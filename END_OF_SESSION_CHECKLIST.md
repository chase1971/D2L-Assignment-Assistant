# End-of-Session Checklist

> **Copy this prompt block and paste it to AI at the end of EVERY coding session.**

---

## 🎯 Quick Copy-Paste Prompt

```
End of session checklist:

1. Create a session summary in SESSIONS.md with today's date (YYYY-MM-DD):
   - What we did this session
   - Files created/modified
   - Next session tasks

2. Update file headers in all modified .py files:
   - Set LAST VERIFIED to today's date
   - Update SAFE TO MODIFY if changed
   - Update FRAGILE sections if needed

3. Review our changes against PROJECT_SYNOPSIS.md:
   - Did we follow all patterns correctly?
   - Does documentation need updating?

4. Check if we created new patterns:
   - Add to PROJECT_SYNOPSIS.md if reusable
   - Update "Last Updated" date
```

---

## 📋 Detailed Checklist

Use this for reference if you need more detail:

### ✅ **1. Session Documentation (Required Every Session)**

**File:** `SESSIONS.md`

**What to add:**
```markdown
## YYYY-MM-DD - [Brief Title]

**What we did:**
- Feature/change 1
- Feature/change 2

**Files created:**
- path/to/file.py (description)

**Files modified:**
- path/to/file.py (what changed)

**Next session tasks:**
- [ ] Task 1
- [ ] Task 2

**Technical debt:**
- Any shortcuts taken

**Notes:**
- Important decisions or observations
```

**AI Prompt:**
```
"Add a session entry to SESSIONS.md with today's date (YYYY-MM-DD),
summarizing what we did, files modified, and next steps."
```

---

### ✅ **2. File Header Updates (Required for Modified Files)**

**What files need updating:**
- Any `.py` file we modified or created

**What to update:**
```
LAST VERIFIED: YYYY-MM-DD

SAFE TO MODIFY: (if changed)
- Update what can be safely changed

FRAGILE / HIGH-RISK AREAS: (if discovered new risks)
- Add new areas that are risky to change
```

**AI Prompt:**
```
"Update file headers in [list files] with today's date (YYYY-MM-DD)
in the LAST VERIFIED section."
```

---

### ✅ **3. PROJECT_SYNOPSIS.md Updates (If Significant Changes)**

**When to update:**
- Added new module or function
- Changed system architecture
- Modified core workflows
- Changed environment variable requirements
- Discovered important patterns

**What to update:**
```
1. "Core Modules" section
   - Add new modules

2. "Customization Guide" section
   - Add new configuration options

3. "Troubleshooting" section
   - Add common issues encountered

4. "Last Updated" date
   - Update to today's date
```

**AI Prompt:**
```
"Check if PROJECT_SYNOPSIS.md needs updating based on what we did.
If yes, update the appropriate sections and set Last Updated to YYYY-MM-DD."
```

---

### ✅ **4. README.md Updates (If User-Facing Changes)**

**When to update:**
- New features added
- Installation steps changed
- New dependencies added
- New environment variables needed

**AI Prompt:**
```
"Update README.md to document the [feature] we just added."
```

---

## ⏱️ Time Budget

**Minimum (every session):**
- Session summary: 1 min
- File headers: 2 min
- **Total: 3 minutes**

**Standard (most sessions):**
- Session summary: 1 min
- File headers: 2 min
- PROJECT_SYNOPSIS.md check: 2 min
- **Total: 5 minutes**

**Full (when adding major features):**
- Session summary: 1 min
- File headers: 2 min
- PROJECT_SYNOPSIS.md update: 2 min
- README.md update: 1 min
- **Total: 6 minutes**

---

## 🚦 Priority Levels

### **🔴 High Priority (MUST do every session):**
1. Session summary in SESSIONS.md
2. File header updates

### **🟡 Medium Priority (Do if applicable):**
3. PROJECT_SYNOPSIS.md updates (if significant changes)
4. README.md updates (if user-facing changes)

### **🟢 Low Priority (Occasional):**
5. Refactoring documentation
6. Pattern extraction

---

## 💡 Pro Tips

### **Tip 1: Use AI to Generate the Summary**
At the end of your session:
```
"Summarize everything we did this session for SESSIONS.md."
```

### **Tip 2: Batch File Header Updates**
Instead of updating each file individually:
```
"Update file headers in all files we modified today with today's date."
```

### **Tip 3: Set a Timer**
- Set a 5-minute timer at the end of your session
- Run through the checklist quickly
- Don't overthink it - just capture the essentials

### **Tip 4: Weekly Review**
Once a week (e.g., every Friday):
```
"Review SESSIONS.md for the past week and summarize what we accomplished.
Check if there are patterns in our changes that should be documented."
```

---

## 🎯 The Lazy Version (Absolute Minimum)

If you're short on time, just do this:

```
"Quick end-of-session: Add entry to SESSIONS.md with today's date,
what we did, and what's next. Update file headers with today's date."
```

**Takes 2 minutes.**

---

## 📝 Example Session End Prompt

Here's a real example you can use:

```
End of session - 2026-02-05:

1. Add session entry to SESSIONS.md:
   - Today we secured API keys in .env file
   - Created PROJECT_SYNOPSIS.md
   - Modified ocr_utils.py to load from environment
   - Next: Add file headers to all Python scripts

2. Update file headers in:
   - ocr_utils.py
   - load_env.py
   Set LAST VERIFIED to 2026-02-05

3. Check: Did we update PROJECT_SYNOPSIS.md correctly?

4. Review: Are all environment variables documented?
```

---

## 📅 Weekly Review (Optional but Recommended)

**Every Friday or end of week:**

```
Weekly review checklist:

1. Review SESSIONS.md entries from this week
2. Look for repeated patterns that should be documented
3. Check if any "Next session tasks" were forgotten
4. Review "Technical debt" items - prioritize cleanup
5. Update PROJECT_SYNOPSIS.md if patterns emerged
6. Clean up any TODO comments in code
```

**AI Prompt:**
```
"Read SESSIONS.md and summarize what we accomplished this week.
Are there any patterns we should add to PROJECT_SYNOPSIS.md?"
```

---

**Remember:** The goal is to keep documentation fresh so it actually helps you and AI in future sessions. Better to spend 5 minutes now than 30 minutes later trying to remember what you did! 🎯
