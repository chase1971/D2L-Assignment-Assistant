# Quick Start Guide

## Which Folder to Use?

### 🎨 **NewStyle Folder** (Use This for the New UI!)
**Location:** `Quiz-extraction/NewStyle/`

This is the **new Figma-styled UI** with metallic buttons.

**To launch the Electron app:**
```bash
cd "C:\Users\chase\Documents\School Scrips\Programs\Quiz-extraction\NewStyle"
npm start
```

**To test in browser (development):**
```bash
cd "C:\Users\chase\Documents\School Scrips\Programs\Quiz-extraction\NewStyle"
npm run dev:all
```
Then open http://localhost:3000

---

### 📦 **Root Folder** (Original App)
**Location:** `Quiz-extraction/`

This is the **original React frontend** with the old UI.

**To launch:**
```bash
cd "C:\Users\chase\Documents\School Scrips\Programs\Quiz-extraction"
npm start
```

---

## Summary

| What You Want | Folder | Command |
|--------------|--------|---------|
| **New Figma UI** (metallic buttons) | `NewStyle/` | `npm start` |
| **Original UI** | Root folder | `npm start` |
| **Test new UI in browser** | `NewStyle/` | `npm run dev:all` |

---

## What `npm start` Does

### In NewStyle folder:
- Starts backend server (port 5000)
- Starts frontend dev server (port 3000)
- Launches Electron window with the new UI

### In root folder:
- Launches Electron with the original React frontend

