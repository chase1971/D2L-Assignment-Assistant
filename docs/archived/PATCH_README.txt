# D2L Assignment Assistant - Patch 1.0.1

## What This Patch Fixes

✅ **Split PDF and Rezip** - ZIP file now saves to grade processing folder  
✅ **Better Error Messages** - Clear message when folders are in use  
✅ **No More Duplicates** - Fixed error messages appearing twice  
✅ **ZIP Location Link** - Shows clickable path to where ZIP is saved  

---

## How to Install This Patch

### Step 1: Download
Make sure you have these files:
- `PATCH_1.0.1.bat`
- `patch_files\` folder with all the updated files inside

### Step 2: Close the App
**Important:** Close D2L Assignment Assistant if it's running!

### Step 3: Run the Patch
1. Double-click `PATCH_1.0.1.bat`
2. The patch will:
   - Find your installation automatically
   - Create a backup of your current files
   - Copy the updated files
   - Show success message

### Step 4: Done!
Launch D2L Assignment Assistant - you're now on v1.0.1!

---

## What Gets Updated

The patch only replaces the files that changed:
- `split_pdf_cli.py` - Fixed ZIP location
- `process_quiz_cli.py` - Fixed duplicate errors
- `backup_utils.py` - Better error handling
- `user_messages\catalog.py` - New error messages
- (Plus supporting files)

Your data, settings, and rosters are **not touched**!

---

## Safety Features

✅ **Automatic Backup** - Creates backup before patching  
✅ **Installation Detection** - Finds your app automatically  
✅ **Safety Checks** - Won't run if app is open  
✅ **Rollback Available** - Backup saved in `installation\backup_DATE_TIME\`  

---

## If Something Goes Wrong

**To rollback to v1.0.0:**
1. Go to your installation folder (usually `C:\Users\YourName\AppData\Local\Programs\D2L Assignment Assistant`)
2. Find the `backup_` folder the patch created
3. Copy the files from `backup_\scripts\` to `resources\scripts\`
4. Done - you're back to v1.0.0

**Or just reinstall:**
Run the full v1.0.0 installer

---

## For Distributing This Patch

**To send this patch to someone:**

1. Zip these files together:
   ```
   PATCH_1.0.1.bat
   patch_files\
   PATCH_README.txt (this file)
   ```

2. Send them the zip file

3. They extract it and run `PATCH_1.0.1.bat`

That's it! No need to send the full 155MB installer - just send this ~500KB patch!

---

## Technical Details

**Files Modified:**
- `resources\scripts\split_pdf_cli.py`
- `resources\scripts\process_quiz_cli.py`
- `resources\scripts\backup_utils.py`
- `resources\scripts\user_messages\catalog.py`
- `resources\scripts\user_messages\*.py` (supporting files)

**Installation Locations Checked:**
- `%LOCALAPPDATA%\Programs\D2L Assignment Assistant`
- `%ProgramFiles%\D2L Assignment Assistant`
- `%ProgramFiles(x86)%\D2L Assignment Assistant`

See `CHANGELOG.md` for full details of changes.

