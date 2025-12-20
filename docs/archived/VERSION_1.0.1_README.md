# Version 1.0.1 Update - Available Now!

## What's New in 1.0.1

### Bug Fixes
✅ **Split PDF and Rezip** - ZIP file now saves to the correct location (grade processing folder)  
✅ **Better Error Messages** - Clear message when folders are in use instead of cryptic errors  
✅ **No More Duplicates** - Fixed error messages appearing twice  
✅ **ZIP Location Link** - Shows clickable path to where your rezipped file is saved  

---

## How to Get the Update

### Automatic Update (Recommended)

**If you have v1.0.0 installed:**

1. **Close** D2L Assignment Assistant if it's running
2. **Launch** the app again
3. **Wait 3 seconds** - you'll see a notification: "Update Available - Version 1.0.1"
4. **Click "Download & Install"**
5. The app will download only the changed files (~5-10MB, not the full 100+MB!)
6. **Restart** when prompted
7. Done! You're now on v1.0.1 ✅

### Manual Install (If Auto-Update Doesn't Work)

**Full installer available at:**
```
C:\Users\chase\Documents\Programs\School Scrips\D2L-Assignment-Assistant\dist\D2L Assignment Assistant Setup 1.0.1.exe
```

**Steps:**
1. Uninstall v1.0.0 from Windows Settings
2. Run the Setup 1.0.1.exe installer
3. Install as normal

---

## What the Auto-Updater Does

- ✅ Checks for updates when you launch the app
- ✅ Downloads only the files that changed (delta update)
- ✅ Shows progress and size
- ✅ Installs on restart (doesn't interrupt your work)
- ✅ You can click "Later" and update when convenient

---

## For Developers

**Files in `C:\Users\chase\Documents\D2L-Updates`:**
- `D2L Assignment Assistant Setup 1.0.1.exe` - Full installer (for new installs)
- `D2L Assignment Assistant Setup 1.0.1.exe.blockmap` - For delta updates
- `latest.yml` - Tells the app what version is available

**To create future patches:**
1. Fix bugs
2. Update version in `package.json`
3. Run `BUILD.bat`
4. Run `PUBLISH_UPDATE.bat`
5. Users get notified automatically!

See `CHANGELOG.md` for full details of all changes.

