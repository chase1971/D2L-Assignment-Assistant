# Auto-Update System - Quick Start

## ✅ What's Been Set Up

Your D2L Assignment Assistant now has **automatic delta patching**! 

When you release an update:
- ✅ Users get notified automatically when they launch the app
- ✅ Only changed files are downloaded (not the whole 100MB+ app)
- ✅ Update installs automatically on app restart
- ✅ No manual uninstall/reinstall needed

---

## 🚀 How to Create and Publish a Patch

### Simple 3-Step Process:

1. **Fix your bug** (e.g., edit split_pdf_cli.py)

2. **Bump version in package.json:**
   ```json
   "version": "1.0.1"  // change from 1.0.0
   ```

3. **Run these two commands:**
   ```batch
   BUILD.bat
   PUBLISH_UPDATE.bat
   ```

That's it! The update is now available.

---

## 📦 What Happens Behind the Scenes

### BUILD.bat creates:
- `dist\D2L Assignment Assistant Setup 1.0.1.exe` (full installer)
- `dist\D2L Assignment Assistant Setup 1.0.1.exe.blockmap` (for delta updates)  
- `dist\latest.yml` (version info)

### PUBLISH_UPDATE.bat copies them to:
- `C:\Users\<YourName>\Documents\D2L-Updates\`

### When users launch the app:
1. App checks `D2L-Updates` folder for new version
2. Shows "Update Available" dialog
3. Downloads only the changed files (delta patch)
4. Installs on restart

---

## 🧪 How to Test It

### Test on your own computer:

1. Install v1.0.0 (current version)
2. Make a small change to any Python file
3. Update version to 1.0.1 in package.json
4. Run `BUILD.bat` then `PUBLISH_UPDATE.bat`
5. Launch the installed v1.0.0 app
6. Wait 3 seconds - you'll see "Update Available - Version 1.0.1"
7. Click "Download & Install"
8. Watch it download only the changed files
9. Click "Restart Now" or close and reopen
10. App is now v1.0.1! 🎉

---

## 📁 Files Modified

- **package.json** - Added `electron-updater` and publish config
- **electron/main.js** - Added auto-update checking and dialogs
- **BUILD.bat** - (no changes, works as before)
- **PUBLISH_UPDATE.bat** - NEW: Helper to copy update files
- **PATCHING_GUIDE.md** - NEW: Detailed patching guide

---

## 🔧 Configuration

The app looks for updates in:
```
C:\Users\<YourUsername>\Documents\D2L-Updates
```

To change this location, edit `package.json`:
```json
"publish": {
  "provider": "generic",
  "url": "file:///${env.USERPROFILE}/Documents/D2L-Updates"
}
```

For network sharing, use:
```json
"url": "file:///Z:/shared-folder/D2L-Updates"
```

---

## 💡 Key Benefits

### Before (Old Way):
- Fix bug → Rebuild entire app (100+ MB)
- Users manually uninstall old version
- Users manually install new version
- All 100+ MB downloaded again

### After (New Way):
- Fix bug → Build once
- Run PUBLISH_UPDATE.bat
- Users launch app → see update notification
- Users click "Download" → only changed files download (maybe 5MB)
- Users restart → update installed
- ✅ No manual uninstall/reinstall

---

## 📝 Version Numbering

- **1.0.0 → 1.0.1** = Bug fix (patch)
- **1.0.0 → 1.1.0** = New feature (minor update)
- **1.0.0 → 2.0.0** = Major changes (breaking changes)

Always increment before building a new version!

---

## 🎯 Next Steps

1. **Build v1.0.1 with the fix for split PDF**
2. **Run PUBLISH_UPDATE.bat**
3. **Test the update on your installed app**
4. **Enjoy easy patching!** 🚀

For more details, see **PATCHING_GUIDE.md**

