# Patch System for D2L Assignment Assistant

The D2L Assignment Assistant includes a built-in patch management system that allows you to distribute bug fixes and updates without requiring users to reinstall the entire application.

## Overview

- **Patch files** are `.zip` files containing updated Python scripts
- Patched files are stored in `%APPDATA%\D2L Assignment Assistant\patches\`
- Patched files take priority over bundled files
- Users can import patches through the UI
- No admin rights required to apply patches

## For Administrators: Creating Patches

### Step 1: Make Your Changes

Edit any Python files in:
- `/scripts/` - Main CLI scripts
- `/python-modules/` - Core processing modules

### Step 2: Create Patch File

1. Run `CREATE_PATCH.bat`
2. Enter version number (e.g., `1.0.1`)
3. Enter description (e.g., `Fixed page count calculation bug`)
4. Patch file will be created in `/patches/` folder

Example:
```
patch-v1.0.1-20260204-153042.zip
```

### Step 3: Distribute to Users

Send the patch file to users via:
- Email attachment
- Shared drive
- USB drive
- Any file transfer method

## For Users: Applying Patches

### Method 1: UI Import

1. Open D2L Assignment Assistant
2. Click **🔧 PATCHES** button (top navigation bar)
3. Click **📥 Import Patch File**
4. Select the patch file you received
5. Click **Restart** when prompted

### Method 2: Manual File Selection

If the patch file is on a network drive or USB:

1. Open Patch Manager
2. Use file picker to navigate to patch location
3. Select and import

## Patch Management

### View Current Patches

In the Patch Manager, you can see:
- ✓ Whether patches are active
- Number of patched files
- Patch version and description
- List of all patched files
- When patch was imported

### Clear Patches

To restore bundled (original) versions:

1. Open Patch Manager
2. Click **🗑️ Clear All Patches**
3. Confirm the action
4. Restart the app

## Technical Details

### How It Works

1. **Priority System**: When the app needs a Python script, it checks:
   - First: `%APPDATA%\D2L Assignment Assistant\patches\scripts\{script}`
   - Fallback: Bundled script in app installation

2. **No Reinstall Needed**: Patches are applied to the user's AppData folder, which persists across app updates

3. **Safe**: Original bundled files are never modified - patches are overlays

### Patch File Structure

```
patch-v1.0.1.zip
├── patch-metadata.json           # Version, date, description
├── scripts/
│   ├── *.py                      # Updated CLI scripts
│   └── python-modules/           # Updated core modules
│       └── *.py
```

### Patch Metadata

Example `patch-metadata.json`:
```json
{
  "version": "1.0.1",
  "date": "2026-02-04",
  "description": "Fixed page count mode calculation",
  "files": []
}
```

## Best Practices

### For Administrators

✅ **DO**:
- Test patches thoroughly before distribution
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Write clear descriptions
- Keep a changelog of patch versions
- Archive patch files for future reference

❌ **DON'T**:
- Include user-specific data (classes, rosters)
- Patch files you didn't change (keep patches minimal)
- Skip version numbers (maintain sequential releases)

### For Users

✅ **DO**:
- Always restart after importing patches
- Keep patch files for future reference
- Import patches from trusted sources only

❌ **DON'T**:
- Import patches from unknown sources
- Apply patches while processes are running

## Troubleshooting

### Patch Import Failed

**Problem**: Error when importing patch file

**Solutions**:
1. Verify file is not corrupted (re-download if needed)
2. Check file is actually a `.zip` file
3. Try extracting manually to verify contents
4. Check disk space in `%APPDATA%`

### Patch Not Taking Effect

**Problem**: Changes not visible after patch import

**Solutions**:
1. Ensure you restarted the app (required!)
2. Check Patch Manager shows patch as active
3. Verify correct files are in patched files list
4. Clear patches and re-import

### Want to Rollback

**Problem**: Patch caused issues, need original behavior

**Solutions**:
1. Open Patch Manager
2. Click "Clear All Patches"
3. Restart app
4. Original bundled versions will be used

## Example Workflow

### Scenario: Fix Quiz Processing Bug

1. **Developer Makes Fix**:
   ```
   - Edit: python-modules/submission_processor.py
   - Fix: Line 145 - correct mode calculation
   ```

2. **Create Patch**:
   ```batch
   C:\...\D2L-Assignment-Assistant> CREATE_PATCH.bat
   Enter patch version: 1.0.2
   Enter description: Fixed quiz mode calculation bug
   → Created: patches\patch-v1.0.2-20260204-160000.zip
   ```

3. **Distribute**:
   ```
   Email to instructors with subject:
   "D2L Assistant Update v1.0.2 - Quiz Processing Fix"
   ```

4. **User Applies**:
   ```
   1. Receives email with patch-v1.0.2-*.zip
   2. Opens D2L Assistant
   3. Clicks PATCHES → Import Patch File
   4. Selects downloaded patch
   5. Clicks Restart
   6. Bug is fixed!
   ```

## Appendix: Patchable Files

The following files can be patched:

### Scripts (Main CLIs)
- `process_quiz_cli.py`
- `split_pdf_cli.py`
- `extract_grades_cli.py`
- `class_manager_cli.py`
- `classes.json` (can be patched too)

### Python Modules (Core Logic)
- `submission_processor.py`
- `grading_processor.py`
- `roster_handler.py`
- `pdf_splitter.py`
- `canvas_api_handler.py`
- `user_messages/catalog.py`
- And any other `.py` files in `python-modules/`

## Support

If you encounter issues with the patch system:

1. Check patch status in Patch Manager
2. Try clearing and re-importing patch
3. Verify patch file structure
4. Contact administrator for replacement patch
