"""
MESSAGE CATALOG
All user-facing messages in one place.
To change any message, edit it HERE.

Format: "MESSAGE_ID": ("template", "level")
Levels: SUCCESS, ERROR, WARNING, INFO
"""

MESSAGES = {
    # =========================================================================
    # GENERAL
    # =========================================================================
    "CLASS_LOADED": ("✅ Class loaded: {class_name}", "SUCCESS"),
    "LOCATION": ("📂 Location: {path}", "INFO"),
    "NO_CLASS": ("❌ Please select a class first", "ERROR"),
    
    # =========================================================================
    # LOADING CLASSES
    # =========================================================================
    "LOADING_CLASSES": ("📂 Loading classes from Rosters etc folder...", "INFO"),
    "CLASSES_FOUND": ("✅ Found {count} classes", "SUCCESS"),
    "ERR_NO_ROSTER_FOLDER": ("❌ Could not find roster folder", "ERROR"),
    
    # =========================================================================
    # PROCESS QUIZZES
    # =========================================================================
    "QUIZ_SEARCHING": ("🔍 Searching for quiz ZIP...", "INFO"),
    "QUIZ_PROCESSING": ("📦 Processing: {filename}", "INFO"),
    "QUIZ_USING": ("✓ Using: {filename}", "INFO"),
    "QUIZ_SUCCESS": ("✅ Quiz processing completed!", "SUCCESS"),
    "QUIZ_PROCESSING_HEADER": ("QUIZ PROCESSING", "INFO"),
    "QUIZ_FOUND_FILE": ("Found quiz file: {filename}", "INFO"),
    "QUIZ_ASSIGNMENT": ("Assignment: {name}", "INFO"),
    "QUIZ_VALIDATING": ("Validating ZIP file structure...", "INFO"),
    "QUIZ_VALIDATED": ("✅ ZIP structure validated", "SUCCESS"),
    "QUIZ_EXTRACTED": ("✅ Extracted {count} student folders", "SUCCESS"),
    "QUIZ_PDF_CREATED": ("✅ Combined PDF created!", "SUCCESS"),
    "QUIZ_PDF_SAVED": ("PDF saved as: {filename}", "INFO"),
    
    # =========================================================================
    # PROCESS COMPLETION
    # =========================================================================
    "COMPLETION_SEARCHING": ("🔍 Searching for assignment ZIP...", "INFO"),
    "COMPLETION_PROCESSING": ("📦 Processing: {filename}", "INFO"),
    "COMPLETION_SUCCESS": ("✅ Completion processing completed!", "SUCCESS"),
    "COMPLETION_AUTO_ASSIGN": ("✅ Auto-assigned {count} points to {students} submissions", "SUCCESS"),
    "COMPLETION_VALIDATION": ("📋 Validating student submissions...", "INFO"),
    "COMPLETION_VALIDATED": ("✅ Validation complete", "SUCCESS"),
    
    # =========================================================================
    # EXTRACT GRADES
    # =========================================================================
    "GRADES_STARTING": ("🔬 Starting grade extraction...", "INFO"),
    "GRADES_PDF_NOT_FOUND": ("❌ Combined PDF not found", "ERROR"),
    "GRADES_IMPORT_NOT_FOUND": ("❌ Import file not found", "ERROR"),
    "GRADES_NO_RESULTS": ("❌ No grades were extracted from the PDF", "ERROR"),
    "GRADES_SUCCESS": ("✅ Grade extraction completed successfully!", "SUCCESS"),
    "GRADES_ISSUES_HEADER": ("ISSUES FOUND (Please Review):", "WARNING"),
    "GRADES_NO_GRADE": ("❌ NO GRADE FOUND:", "ERROR"),
    "GRADES_LOW_CONFIDENCE": ("❌ LOW CONFIDENCE (needs verification):", "WARNING"),
    "GRADES_NAME_ISSUES": ("⚠️ NAME MATCHING ISSUES (fuzzy match):", "WARNING"),
    "GRADES_NO_SUBMISSIONS": ("❌ NO SUBMISSIONS:", "ERROR"),
    
    # =========================================================================
    # SPLIT PDF / REZIP
    # =========================================================================
    "SPLIT_STARTING": ("📦 Starting PDF split and rezip...", "INFO"),
    "SPLIT_SUCCESS": ("✅ Split PDF and rezip completed!", "SUCCESS"),
    "SPLIT_CREATING_ZIP": ("📦 Creating new ZIP: {filename}", "INFO"),
    "SPLIT_ZIP_CREATED": ("✅ Created ZIP file: {filename}", "SUCCESS"),
    
    # =========================================================================
    # OPEN FOLDERS
    # =========================================================================
    "FOLDER_OPENED": ("📂 Folder opened", "SUCCESS"),
    "FOLDER_CLASS_OPENED": ("📂 Class roster folder opened", "SUCCESS"),
    "DOWNLOADS_OPENING": ("📁 Opening Downloads folder...", "INFO"),
    "DOWNLOADS_OPENED": ("✅ Downloads folder opened successfully!", "SUCCESS"),
    
    # =========================================================================
    # CLEAR DATA
    # =========================================================================
    "CLEAR_STARTING": ("🗑️ Starting cleanup for {class_name}", "INFO"),
    "CLEAR_SUCCESS": ("✅ Cleanup completed!", "SUCCESS"),
    "CLEAR_ARCHIVED": ("🗑️ Clearing all archived data for {class_name}", "INFO"),
    "CLEAR_ARCHIVED_SUCCESS": ("✅ Cleared {count} archived folder(s)", "SUCCESS"),
    "CLEAR_NO_ARCHIVED": ("ℹ️ No archived folders found", "INFO"),
    "CLEAR_TARGET_FOLDER": ("Target folder: {folder_name}", "INFO"),
    "CLEAR_MODE_SELECTIVE": ("Mode: Selective (save folders and PDF)", "INFO"),
    "CLEAR_MODE_FULL": ("Mode: Full delete", "INFO"),
    "CLEAR_DELETED": ("✅ Deleted: {folder_name}", "SUCCESS"),
    "CLEAR_ARCHIVED_TO": ("✅ Archived to: {folder_name}", "SUCCESS"),
    "CLEAR_SELECTIVE_COMPLETE": ("✅ Selective clear completed", "SUCCESS"),
    "CLEAR_FOUND_MATCHING": ("⚠️ Found matching folder: {folder_name}", "WARNING"),
    "ERR_CLEAR_FOLDER_NOT_FOUND": ("❌ Processing folder not found for assignment: {assignment}\n   Tried: {path}", "ERROR"),
    "ERR_CLEAR_FAILED": ("❌ {message}", "ERROR"),
    "ERR_CLEAR_FAILED_DELETE": ("❌ Failed to delete folder (may be in use)", "ERROR"),
    "ERR_CLEAR_FAILED_RENAME": ("❌ Failed to rename: {error}", "ERROR"),
    
    # =========================================================================
    # BACKUP OPERATIONS
    # =========================================================================
    "BACKUP_CREATING": ("Existing folder found, creating backup...", "INFO"),
    "BACKUP_RENAMING": ("   Renaming: {old_name}", "INFO"),
    "BACKUP_TO": ("         to: {new_name}", "INFO"),
    "BACKUP_SUCCESS": ("   Backup created successfully", "SUCCESS"),
    "BACKUP_DELETING": ("Existing folder found, deleting...", "INFO"),
    "BACKUP_DELETE_SUCCESS": ("   Folder deleted successfully", "SUCCESS"),
    
    # =========================================================================
    # IMPORT FILE
    # =========================================================================
    "IMPORT_SETTING_UP": ("Setting up Import File column...", "INFO"),
    "IMPORT_COLUMN_CREATED": ("   Created column: '{column}'", "SUCCESS"),
    "IMPORT_COLUMN_EXISTS": ("   Column already exists: '{column}'", "INFO"),
    "IMPORT_READY": ("   Import File ready for grade extraction", "SUCCESS"),
    "IMPORT_LOADED": ("Loaded Import File: {count} students", "INFO"),
    
    # =========================================================================
    # STUDENT PROCESSING
    # =========================================================================
    "STUDENTS_UNIQUE": ("Found {count} unique students", "INFO"),
    "STUDENT_MATCHED": ("{name}: Matched using name parts → {roster_name}", "INFO"),
    "STUDENT_NEWER": ("{name}: Found newer submission, using that", "INFO"),
    "STUDENT_PDF": ("📄 {name} — PDF", "INFO"),
    
    # =========================================================================
    # FILE ERRORS (CONSISTENT ACROSS APP)
    # =========================================================================
    "ERR_FILE_LOCKED": ("❌ File is in use - please close it and try again", "ERROR"),
    "ERR_FILE_NOT_FOUND": ("❌ File not found: {file}", "ERROR"),
    "ERR_PERMISSION": ("❌ Permission denied - check file permissions", "ERROR"),
    "ERR_CORRUPT": ("❌ File is corrupted - please re-download", "ERROR"),
    "ERR_NO_ZIP": ("❌ No ZIP files found in Downloads", "ERROR"),
    "ERR_NO_FOLDER": ("❌ No grade processing folder found", "ERROR"),
    "ERR_NO_PROCESSING_FOLDERS": ("❌ No processing folders found for this class", "ERROR"),
    "ERR_NO_ASSIGNMENTS": ("❌ No assignments selected", "ERROR"),
    "ERR_NO_ARCHIVED": ("ℹ️ No archived folders found for this class", "INFO"),
    "ERR_UNZIPPED_NOT_FOUND": ("❌ Unzipped folders directory not found", "ERROR"),
    "ERR_ZIP_CREATE": ("❌ Error creating ZIP: {error}", "ERROR"),
    "ERR_COULD_NOT_MATCH": ("{name}: Could not match to roster", "WARNING"),
    "ERR_COULD_NOT_DELETE": ("   Could not delete folder: {error}", "ERROR"),
    "ERR_COULD_NOT_BACKUP": ("   Could not create backup: {error}", "ERROR"),
    "ERR_COULD_NOT_OPEN_PDF": ("   Could not open PDF: {error}", "ERROR"),
    "ERR_IMPORT_FILE": ("   Could not setup Import File: {error}", "ERROR"),
    "ERR_GENERIC": ("❌ Error: {error}", "ERROR"),
    
    # =========================================================================
    # SUBMISSION PROCESSING
    # =========================================================================
    "SUBMISSION_PROCESSING_HEADER": ("PROCESSING STUDENT SUBMISSIONS", "INFO"),
    "SUBMISSION_FOUND_UNIQUE": ("Found {count} unique students (after filtering duplicates)", "INFO"),
    "SUBMISSION_MULTIPLE_PDFS_HEADER": ("Students who submitted multiple PDFs (combined automatically):", "INFO"),
    "SUBMISSION_MULTIPLE_PDF_ITEM": ("   • {name}", "INFO"),
    "SUBMISSION_NO_MATCH": ("   {name}: Could not match to roster", "WARNING"),
    "SUBMISSION_NEWER_FOUND": ("   {name}: Found newer submission, using that", "INFO"),
    "SUBMISSION_NAME_PARTS_MATCH": ("   {name}: Matched using name parts → {roster_name}", "INFO"),
    "SUBMISSION_NO_SUB": ("   {name}: No submission", "INFO"),
    "SUBMISSION_NO_SUB_POINTS": ("   {name}: No submission → 0 points", "INFO"),
    "SUBMISSION_PDF_FOUND": ("   {name}: PDF found", "INFO"),
    "SUBMISSION_PDF_FOUND_POINTS": ("   {name}: PDF found → 10 points", "INFO"),
    "SUBMISSION_MULTI_PDF": ("   {name}: {count} PDFs found, combining", "INFO"),
    "SUBMISSION_MULTI_PDF_POINTS": ("   {name}: {count} PDFs found, combining → 10 points", "INFO"),
    "SUBMISSION_ERROR": ("   {error}", "ERROR"),
    
    # =========================================================================
    # PDF OPERATIONS (CREATING/SPLITTING)
    # =========================================================================
    "PDF_CREATING": ("Creating combined PDF...", "INFO"),
    "PDF_COMBINED_SUCCESS": ("✅ Combined PDF created!", "SUCCESS"),
    "PDF_ERROR_PROCESSING": ("   Error processing {name}: {error}", "ERROR"),
    "PDF_SPLITTING_HEADER": ("SPLITTING COMBINED PDF", "INFO"),
    "PDF_TOTAL_PAGES": ("   Combined PDF has {pages} pages", "INFO"),
    "PDF_EXTRACTING_NAMES": ("   Extracting student names from PDF...", "INFO"),
    "PDF_EXTRACTED_COUNT": ("   Extracted {count} names from PDF", "INFO"),
    "PDF_FIRST_NAMES_HEADER": ("   First 10 names found:", "INFO"),
    "PDF_NAME_ITEM": ("      {num:2d}. {name}", "INFO"),
    "PDF_MORE_NAMES": ("      ... and {count} more", "INFO"),
    "PDF_SPLIT_SUCCESS": ("Successfully split PDF for {count} students", "SUCCESS"),
    "PDF_SPLIT_ERROR": ("Error splitting combined PDF: {error}", "ERROR"),
    "PDF_NO_FOLDER_FOR": ("   Could not find folder for: {name}", "WARNING"),
    "PDF_PROCESSING_STUDENT": ("   Processing {name}: {pages} pages", "INFO"),
    "PDF_FOUND_FOLDER": ("      Found folder: {folder}", "INFO"),
    "PDF_NO_PDF_IN_FOLDER": ("   No PDF found in {name}'s folder", "WARNING"),
    "PDF_REPLACING": ("      Replacing: {filename}", "INFO"),
    "PDF_STUDENT_COMPLETE": ("   {name}: {pages} pages → {filename}", "SUCCESS"),
    
    # =========================================================================
    # IMPORT FILE OPERATIONS
    # =========================================================================
    "IMPORT_CLOSED_EXCEL": ("   📋 Closed Excel to save import file", "INFO"),
    "IMPORT_NO_EOL": ("   ⚠️  End-of-Line Indicator not found - adding it to column F", "WARNING"),
    "IMPORT_FILE_NOT_FOUND": ("❌ Import File not found: {path}", "ERROR"),
    "IMPORT_FILE_IN_USE": ("❌ The file is being used by another process", "ERROR"),
    "IMPORT_PERMISSION_DENIED": ("❌ Cannot access file - permission denied", "ERROR"),
    "IMPORT_UNABLE_TO_READ": ("❌ Unable to read file", "ERROR"),
    "IMPORT_LOADED_STUDENTS": ("Loaded Import File: {count} students", "INFO"),
    "IMPORT_UPDATE_HEADER": ("UPDATING IMPORT FILE", "INFO"),
    "IMPORT_CURRENT_COLUMNS": ("Current columns: {columns}", "INFO"),
    "IMPORT_NEW_COLUMN": ("   New column name: '{name}'", "INFO"),
    "IMPORT_UPDATING_GRADES": ("   Updating grades...", "INFO"),
    "IMPORT_SAVING_TO": ("   Saving to: {path}", "INFO"),
    "IMPORT_FUZZY_HEADER": ("   ⚠️  Fuzzy name matches (please verify):", "WARNING"),
    "IMPORT_FUZZY_ITEM": ("{warning}", "WARNING"),
    "IMPORT_UPDATE_ERROR": ("Error updating import file: {error}", "ERROR"),
    "IMPORT_CLEANUP_COLUMNS": ("   🧹 Cleaning up {count} corrupted columns after End-of-Line Indicator", "INFO"),
    "IMPORT_MODE_DONT_OVERRIDE": ("   Mode: Don't override - adding new column before End-of-Line Indicator", "INFO"),
    "IMPORT_MODE_OVERRIDE": ("   Mode: Override - removing old grade columns", "INFO"),
    "IMPORT_WARNING_FEW_COLUMNS": ("   Warning: Less than {required} columns, adding empty columns", "WARNING"),
    "IMPORT_COLUMN_EXISTS": ("   Column '{name}' already exists, using existing column", "INFO"),
    "IMPORT_ADDED_COLUMN": ("   Added new column '{name}' at index {index} (before '{before}')", "SUCCESS"),
    "IMPORT_FIXED_COLUMNS": ("   Fixed columns (0-{count}): {columns}", "INFO"),
    "IMPORT_EOL_INFO": ("   End-of-Line Indicator: '{name}' at index {index}", "INFO"),
    "IMPORT_TOTAL_COLUMNS": ("   Current total columns: {count}", "INFO"),
    "IMPORT_REMOVING_OLD": ("   Removing {count} old grade columns: {columns}", "INFO"),
    "IMPORT_RESULT_COLUMNS": ("   Result: {count} columns", "INFO"),
    "IMPORT_ADDED_AT_INDEX": ("   Added grade column '{name}' at index 5", "SUCCESS"),
    
    # =========================================================================
    # BACKUP OPERATIONS (DETAILED)
    # =========================================================================
    "BACKUP_DELETING_FOLDER": ("Existing folder found, deleting...", "INFO"),
    "BACKUP_DELETING_NAME": ("   Deleting: {name}", "INFO"),
    "BACKUP_DELETED": ("   Folder deleted successfully", "SUCCESS"),
    "BACKUP_DELETE_FAILED": ("   Could not delete folder: {error}", "ERROR"),
    "BACKUP_RENAME_FROM": ("   Renaming: {old_name}", "INFO"),
    "BACKUP_RENAME_TO": ("         to: {new_name}", "INFO"),
    "BACKUP_CREATE_FAILED": ("   Could not create backup: {error}", "ERROR"),
    
    # =========================================================================
    # SPLIT PDF / REZIP OPERATIONS
    # =========================================================================
    "REZIP_UNZIPPED_NOT_FOUND": ("❌ Unzipped folders directory not found", "ERROR"),
    "REZIP_CREATING": ("📦 Creating new ZIP: {filename}", "INFO"),
    "REZIP_USING_ORIGINAL_INDEX": ("   Using preserved original index.html (exact copy)", "INFO"),
    "REZIP_USING_EXTRACTED_INDEX": ("   Using original index.html from extraction (exact copy)", "INFO"),
    "REZIP_WARNING_NO_INDEX": ("   Warning: No original index.html found, generating new one", "WARNING"),
    "REZIP_GENERATED_INDEX": ("   Generated new index.html (fallback - may not work with D2L)", "WARNING"),
    "REZIP_ADDED_INDEX": ("   Added index.html to ZIP root", "INFO"),
    "REZIP_ADDED_ROOT_FILE": ("   Added root file: {filename}", "INFO"),
    "REZIP_ADDED_FILE": ("Added: {filename}", "INFO"),
    "REZIP_CREATED_ZIP": ("✅ Created ZIP file: {path}", "SUCCESS"),
    "REZIP_ERROR": ("❌ Error creating ZIP: {error}", "ERROR"),
    "REZIP_ERROR_DETAILS": ("   Details: {details}", "ERROR"),
    
    # =========================================================================
    # SPLIT PDF CLI SPECIFIC
    # =========================================================================
    "SPLIT_STARTING_PROCESS": ("📦 Starting PDF split and rezip...", "INFO"),
    "SPLIT_SPLITTING_PDF": ("Splitting combined PDF into individual student PDFs...", "INFO"),
    "SPLIT_SUCCESS_COUNT": ("✅ Successfully split PDF for {count} students", "SUCCESS"),
    "SPLIT_NO_STUDENTS": ("⚠️ No students processed - check if combined PDF exists", "WARNING"),
    "SPLIT_CREATING_ZIP_FILE": ("Creating ZIP file: {filename}...", "INFO"),
    "SPLIT_ZIP_FAILED": ("⚠️ ZIP creation failed, but PDFs were split", "WARNING"),
    "SPLIT_NO_NAME": ("⚠️ Could not determine assignment name or ZIP name, skipping rezip", "WARNING"),
    "SPLIT_ERRORS_HEADER": ("❌ Errors:", "ERROR"),
    "SPLIT_ERROR_ITEM": ("   {error}", "ERROR"),
    "SPLIT_COMPLETED": ("✅ completed!", "SUCCESS"),
    
    # =========================================================================
    # PROCESS COMPLETION CLI SPECIFIC
    # =========================================================================
    "COMPLETION_HEADER_START": ("COMPLETION PROCESSING STARTED", "INFO"),
    "COMPLETION_CLASS": ("Class: {class_name}", "INFO"),
    "COMPLETION_USING_ZIP": ("Using specified ZIP file: {filename}", "INFO"),
    "COMPLETION_LOOKING_FOR_ZIP": ("Looking for ZIP files in Downloads folder...", "INFO"),
    "COMPLETION_FOUND_ONE_ZIP": ("Found 1 ZIP file: {filename}", "INFO"),
    "COMPLETION_SELECTED_ZIP": ("Selected ZIP file: {filename}", "INFO"),
    "COMPLETION_PROCESSING_HEADER": ("STARTING COMPLETION PROCESSING", "INFO"),
    "COMPLETION_AUTO_ASSIGN": ("(Auto-assigning 10 points to all submissions)", "INFO"),
    "COMPLETION_MODE_DONT_OVERRIDE": ("Mode: Don't override (adding new column after column E)", "INFO"),
    "COMPLETION_MODE_OVERRIDE": ("Mode: Override column E (existing behavior)", "INFO"),
    "COMPLETION_SUCCESS": ("Completion processing completed successfully!", "SUCCESS"),
    "COMPLETION_OPENED_PDF": ("Opened PDF file: {filename}", "INFO"),
    "COMPLETION_COULD_NOT_OPEN_PDF": ("Could not open PDF: {error}", "WARNING"),
    "COMPLETION_HEADER_COMPLETE": ("COMPLETION PROCESSING COMPLETED", "SUCCESS"),
    "COMPLETION_FAILED_HEADER": ("COMPLETION PROCESSING FAILED", "ERROR"),
    "COMPLETION_FINISHED": ("PROCESSING FINISHED", "INFO"),
    
    # =========================================================================
    # MISC
    # =========================================================================
    "SELECTED_FILE": ("📄 Selected: {filename}", "INFO"),
    "OPENING_PDF": ("Opening combined PDF for manual grading...", "INFO"),
    "SEPARATOR_LINE": ("-" * 40, "INFO"),
    "SEPARATOR_DOUBLE": ("=" * 60, "INFO"),
    "EMPTY_LINE": ("", "INFO"),
}

