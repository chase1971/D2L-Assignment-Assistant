# All Log Messages in D2L Assignment Assistant

This file lists all user-facing log messages that can appear in the app.
Edit these as needed, then update the corresponding source files.

---

## Frontend Messages (Option2.tsx)

### Class Loading
- `✅ Class loaded: {class name}`
- `📂 Loading classes from Rosters etc folder...`
- `✅ Found {count} classes`
- `❌ Error: {error message}`
- `❌ Error loading classes: {error message}`

### Downloads Folder
- `📁 Opening Downloads folder...`
- `✅ Downloads folder opened successfully!`
- `❌ Error: {error message}`

### Quiz Processing
- `❌ Please select a class first`
- `🔍 Searching for Canvas ZIP in Downloads...`
- `✅ Quiz processing completed!`
- `📂 Combined PDF ready for manual grading`
- `📁 Multiple ZIP files found - please select one`
- `📁 Processing selected ZIP file: {filename}`
- `❌ Error: {error message}`

### Completion Processing
- `❌ Please select a class first`
- `🔍 Searching for Canvas ZIP in Downloads...`
- `✅ Completion processing completed!`
- `✅ Auto-assigned 10 points to all submissions`
- `📁 Multiple ZIP files found - please select one`
- `📁 Processing selected ZIP file: {filename}`
- `❌ Error: {error message}`

### Grade Extraction
- `❌ Please select a class first`
- `🔬 Starting grade extraction...`
- `✅ Grade extraction completed successfully!`
- `❌ Error: {error message}`

### Split PDF
- `❌ Please select a class first`
- `📦 Starting PDF split and rezip...`
- `✅ Split PDF and rezip completed!`
- `❌ Error: {error message}`

### Open Folder
- `❌ Please select a class first`
- `📂 Opening grade processing folder...`
- `📁 Class folder opened (no grade processing folder found)`
- `✅ Grade processing folder opened!`
- `❌ Error: {error message}`

### Clear Data
- `❌ Please select a class first`
- `🗑️ Clearing all processing data...`
- `✅ All data cleared successfully!`
- `❌ Error: {error message}`

---

## Frontend Messages (LogTerminal.tsx)

### Process Actions
- `✅ Killed {count} processes`
- `❌ Error: {error message}`
- `✅ Opened PDF for {student name}`
- `✅ Combined PDF opened`
- `✅ Import file opened`

---

## Python Backend Messages

### Backup (backup_utils.py)
- `Existing folder found, creating backup...`
- `   Renaming: {folder name}`
- `         to: {backup name}`
- `   Backup created successfully`
- `   Could not create backup: {error}`

### Grade Extraction (extract_grades_cli.py)
- `🔬 Starting grade extraction...`
- `📋 EXTRACTED GRADES:`
- `   {number}. {name}: {grade} {indicator} (confidence: {value})`
- `📊 Processed {count} students`
- `✅ Grade extraction complete!`
- `⚠️ ISSUES FOUND (Please Review):`
- `   ❌ {error message}`
- `   ⚠️ {warning message}`

### Grading Processor (grading_processor.py)
- `Looking for quiz files in Downloads...`
- `No quiz files found in Downloads`
- `Found quiz file: {filename}`
- `Assignment: {name}`
- `Extracting to: {path}`
- `   Preserved original index.html`
- `Extracted {count} student folders`
- `   Preserved index.html from original ZIP`
- `Drive: {letter}:`
- `Class: {name}`
- `Processing folder: {path}`
- `   PDF saved as: {filename}`
- `COMBINED PDF CREATED!`
- `Ready for grading or splitting back to individual PDFs`
- `Found combined PDF: {filename}`
- `REVERSE PROCESSING COMPLETE!`
- `Processed {count} students`
- `Setting up Import File column...`
- `   Created column: '{name}'`
- `   Added column: '{name}'`
- `   ❌ You might have the import file open, please close and try again!`
- `   Import File ready for grade extraction`
- `   Column already exists: '{name}'`
- `   Could not setup Import File: {error}`
- `Opening combined PDF for manual grading...`
- `   Could not open PDF: {error}`
- `PROCESSING COMPLETE!`
- `COMPLETION PROCESSING COMPLETE!`
- `✅ Auto-assigned 10 points to {count} submissions`
- `❌ STUDENT ERRORS AND WARNINGS:`
- `❌ {error}`
- `ERROR: {message}`

### Import File Handler (import_file_handler.py)
- `   📋 Closed Excel to save import file`
- `   ⚠️  End-of-Line Indicator not found - adding it to column F`
- `   ✅ Added End-of-Line Indicator column`
- `Import File not found: {path}`
- `Loaded Import File: {count} students`
- `UPDATING IMPORT FILE`
- `Current columns: {list}`
- `   New column name: '{name}'`
- `   Updating grades...`
- `   Saving to: {path}`
- `   ⚠️  Fuzzy name matches (please verify):`
- `Updated grades for {count} students`
- `Error updating import file: {message}`
- `   🧹 Cleaning up {count} corrupted columns after End-of-Line Indicator`
- `   Mode: Don't override - adding new column before End-of-Line Indicator`
- `   Warning: Less than 5 columns, adding empty columns`
- `   Column '{name}' already exists, using existing column`
- `   Added new column '{name}' at index {index} (before '{column}')`
- `   Mode: Override - removing old grade columns`
- `   Fixed columns (0-4): {list}`
- `   End-of-Line Indicator: '{name}' at index {index}`
- `   Current total columns: {count}`
- `   Removing {count} old grade columns: {list}`
- `   Result: {count} columns`
- `   Added grade column '{name}' at index 5`
- `❌ You might have the import file open, please close and try again!`

### Import File Validation Errors
- `❌ The import file is missing the {column} column.`
- `❌ The import file is missing the {list} columns.`
- `Please download a fresh import file from D2L that includes all required columns:`
- `OrgDefinedId, Username, First Name, Last Name, and Email.`

### PDF Operations (pdf_operations.py)
- `NORMALIZING AND COMBINING PDFs`
- `   Error processing {name}: {error}`
- `Created combined PDF: {count} submissions (sorted by last name)`
- `SPLITTING COMBINED PDF`
- `   Combined PDF has {count} pages`
- `   Extracting student names from PDF...`
- `   Extracted {count} names from PDF`
- `   First 10 names found:`
- `      {number}. {name}`
- `      ... and {count} more`
- `Successfully split PDF for {count} students`
- `Error splitting combined PDF: {error}`
- `   Could not find folder for: {name}`
- `   Processing {name}: {count} pages`
- `      Found folder: {folder}`
- `   No PDF found in {name}'s folder`
- `      Replacing: {filename}`
- `   {name}: {count} pages → {filename}`

### Split PDF CLI (split_pdf_cli.py)
- `❌ Grade processing folder not found`
- `📦 Creating new ZIP: {filename}`
- `   Using preserved original index.html (exact copy)`
- `   Using original index.html from extraction (exact copy)`
- `   Warning: No original index.html found, generating new one`
- `   Generated new index.html (fallback - may not work with D2L)`
- `   Added index.html to ZIP root`
- `   Added root file: {filename}`
- `Added: {path}`
- `✅ Created ZIP file: {path}`
- `❌ Error creating ZIP: {error}`
- `   Details: {traceback}`

### Submission Processor (submission_processor.py)
- `PROCESSING STUDENT SUBMISSIONS`
- `Found {count} unique students (after filtering duplicates)`
- `   {name}: Could not match to roster`
- `Students who submitted multiple PDFs (combined automatically):`
- `   • {name}`
- `   {name}: Found newer submission, using that`
- `   {name}: Matched using name parts → {roster name}`
- `   {name}: PDF found`
- `   {name}: {count} PDFs found, combining`
- `   {name}: {count} PDFs found, combining → 10 points`

### Cleanup (cleanup_data_cli.py)
- `🗑️ Starting cleanup for {class} on {drive}: drive`
- `SUCCESS: Cleanup completed - {count} ZIP files and {count} folders removed`
- `❌ Error: {message}`

---

## Notes

1. Messages with `{variable}` are dynamic - the actual value is inserted at runtime
2. Messages starting with emoji (✅❌⚠️📁📂🔬📦📋📊🗑️🧹) are user-facing
3. Messages without emoji are typically technical/verbose (hidden in normal mode)
4. The LogTerminal filters these - check `shouldShowLog()` function for filtering rules

