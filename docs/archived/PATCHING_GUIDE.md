# D2L Assignment Assistant - Patching Guide

## Overview
Your app now supports **automatic delta updates** (patches). When you fix a bug and create a new version, users will only download the changed files, not the entire app.

---

## Setup (One Time Only)

### 1. Create the Updates Folder
The app looks for updates in: `C:\Users\<YourUsername>\Documents\D2L-Updates`

Create this folder:
```powershell
mkdir "$env:USERPROFILE\Documents\D2L-Updates"
```

---

## How to Create a Patch

### Step 1: Fix the Bug
Make your code changes (e.g., fix split_pdf_cli.py)

### Step 2: Bump the Version
Edit `package.json` and change line 3:
```json
"version": "1.0.1",  // was 1.0.0
```

### Step 3: Build the New Version
Run BUILD.bat as usual:
```batch
BUILD.bat
```

This creates:
- `dist\D2L Assignment Assistant Setup 1.0.1.exe` (full installer)
- `dist\D2L Assignment Assistant Setup 1.0.1.exe.blockmap` (for delta updates)
- `dist\latest.yml` (tells apps what version is available)

### Step 4: Copy Update Files to Updates Folder
Copy these 3 files to your updates folder:
```powershell
copy "dist\D2L Assignment Assistant Setup 1.0.1.exe" "$env:USERPROFILE\Documents\D2L-Updates\"
copy "dist\D2L Assignment Assistant Setup 1.0.1.exe.blockmap" "$env:USERPROFILE\Documents\D2L-Updates\"
copy "dist\latest.yml" "$env:USERPROFILE\Documents\D2L-Updates\"
```

### Step 5: Test the Update
1. Open your installed D2L Assignment Assistant (v1.0.0)
2. Wait 3 seconds - it will check for updates
3. You'll see a dialog: "Update Available - Version 1.0.1"
4. Click "Download & Install"
5. The app downloads **only the changed files** (delta patch)
6. When download completes, you can restart immediately or later
7. On restart, v1.0.1 is installed!

---

## What Gets Updated?

The auto-updater is **smart**:
- If only 1 Python file changed (5KB), it downloads ~5KB
- If the frontend changed (2MB), it downloads ~2MB  
- If nothing changed in Python folder (100MB), it downloads 0MB from Python
- Users never re-download the entire 100+ MB app

---

## Troubleshooting

### "No updates available"
- Check that `latest.yml` is in `C:\Users\<You>\Documents\D2L-Updates\`
- Check that the version in `latest.yml` is higher than your installed version
- Check the console logs in the app (Ctrl+Shift+I to open DevTools)

### Update doesn't start
- Make sure the `.blockmap` file is copied along with the `.exe`
- Check that the file paths in `latest.yml` match your actual files

### Want to share updates on a network?
Change the publish URL in `package.json`:
```json
"publish": {
  "provider": "generic",
  "url": "file:///Z:/shared-folder/D2L-Updates"
}
```
Then put your update files on the network share instead.

---

## Version Numbers

Follow semantic versioning:
- `1.0.0` → `1.0.1` = Bug fix (patch)
- `1.0.0` → `1.1.0` = New feature (minor)
- `1.0.0` → `2.0.0` = Breaking change (major)

Always increment the version before building a patch!

---

## Quick Reference

**Create patch:**
1. Fix bug
2. Edit version in package.json
3. Run BUILD.bat
4. Copy 3 files to D2L-Updates folder

**Test patch:**
1. Open app (old version)
2. Wait for "Update Available" dialog
3. Click "Download & Install"
4. Restart when ready

---

## Notes

- Updates only check when app starts (not continuously)
- Users can click "Later" and update next time
- If "Restart Now" is clicked, update installs immediately
- If "Later" is clicked, update installs when they close the app
- Dev mode (npm run electron:dev) never checks for updates

