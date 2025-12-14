# User Message Preview Script

This script lets you preview what users will see during different operations in the app.

## GUI Version (Recommended)

**Easy-to-use graphical interface:**
```bash
python preview_user_messages_gui.py
```

Features:
- ✅ Visual preview with color coding
- ✅ Search/filter scenarios
- ✅ Edit messages directly
- ✅ Export/import changes as JSON
- ✅ Reset to original messages

## Command Line Version

### Show a specific scenario:
```bash
python preview_user_messages.py "Process Quizzes (Success)"
python preview_user_messages.py "Extract Grades (Error - Missing Column)"
```

### Interactive menu (shows all scenarios):
```bash
python preview_user_messages.py
```

Then select a number from the menu.

### Show all scenarios at once:
```bash
python preview_user_messages.py
# Then select option 0
```

## Available Scenarios

1. **Process Quizzes (Success)** - Normal quiz processing flow
2. **Process Quizzes (Error - No ZIP)** - When no ZIP file is found
3. **Process Quizzes (Error - Multiple ZIPs)** - When multiple ZIPs are found
4. **Process Completion (Success)** - Completion processing flow
5. **Extract Grades (Success)** - Grade extraction with confidence scores
6. **Extract Grades (Error - Missing Column)** - Missing required column error
7. **Extract Grades (Error - File Open)** - When Excel needs to be closed
8. **Split PDF (Success)** - PDF splitting and rezipping
9. **Open Folder (Success)** - Opening grade processing folder
10. **Open Folder (No Processing Folder)** - When folder doesn't exist
11. **Clear Data (Success)** - Clearing processing data
12. **Load Classes (Success)** - Loading classes from folder
13. **Load Classes (Error)** - Error loading classes

## Customizing Messages

Edit the `SCENARIOS` dictionary in `preview_user_messages.py` to:
- Add new scenarios
- Modify existing messages
- Test different message formats

The script uses Rich library for colored output, so messages will appear with:
- ✅ Green for success messages
- ❌ Red for errors
- ⚠️ Yellow for warnings
- 🔍 Cyan for search/processing messages
- 📄 Blue for file-related messages

## Next Steps

After reviewing these previews, you can:
1. Update the actual log messages in the source files
2. Use Option 1 (mapping script) to create a transformation map
3. Use Option 2 (AI suggestions) to get alternative wording

