"""
MESSAGE CATALOG
All user-facing messages in one place.
To change any message, edit it HERE.

Format: "MESSAGE_ID": ("template", "level", "code")

Levels: SUCCESS, ERROR, WARNING, INFO

Error Code Numbering Scheme:
  E1xxx - User-facing errors (E1001-E1999)
  W1xxx - User-facing warnings (W1001-W1999)
  I1xxx - User-facing info messages (I1001-I1999)
  S1xxx - User-facing success messages (S1001-S1999)
  D2xxx - Developer errors (D2001-D2999) - not shown to users
  D3xxx - Developer warnings (D3001-D3999) - not shown to users

Codes are displayed at the end of messages: "Message text [E1001]"
Codes are unique identifiers for debugging and support.
"""

MESSAGES = {
    # =========================================================================
    # GENERAL
    # =========================================================================
    "CLASS_LOADED": ("✅ Class loaded: {class_name}", "SUCCESS", "S1001"),
    "LOCATION": ("📂 Location: {path}", "INFO", "I1001"),
    "NO_CLASS": ("❌ Please select a class first", "ERROR", "E1001"),
    
    # =========================================================================
    # LOADING CLASSES
    # =========================================================================
    "LOADING_CLASSES": ("📂 Loading classes from Rosters etc folder...", "INFO", "I1002"),
    "CLASSES_FOUND": ("✅ Found {count} classes", "SUCCESS", "S1002"),
    "ERR_NO_ROSTER_FOLDER": ("❌ Could not find roster folder", "ERROR", "E1002"),
    
    # =========================================================================
    # PROCESS QUIZZES
    # =========================================================================
    "QUIZ_SEARCHING": ("🔍 Searching for quiz ZIP...", "INFO", "I1003"),
    "QUIZ_PROCESSING": ("📦 Processing: {filename}", "INFO", "I1004"),
    "QUIZ_USING": ("✓ Using: {filename}", "INFO", "I1005"),
    "QUIZ_SUCCESS": ("✅ Quiz processing completed!", "SUCCESS", "S1003"),
    "QUIZ_PROCESSING_HEADER": ("QUIZ PROCESSING", "INFO", "I1006"),
    "QUIZ_FOUND_FILE": ("Found quiz file: {filename}", "INFO", "I1007"),
    "QUIZ_ASSIGNMENT": ("Assignment: {name}", "INFO", "I1008"),
    "QUIZ_VALIDATING": ("Validating ZIP file structure...", "INFO", "I1009"),
    "QUIZ_VALIDATED": ("✅ ZIP structure validated", "SUCCESS", "S1004"),
    "QUIZ_EXTRACTED": ("✅ Extracted {count} student folders", "SUCCESS", "S1005"),
    "QUIZ_PDF_CREATED": ("✅ Combined PDF created!", "SUCCESS", "S1006"),
    "QUIZ_PDF_SAVED": ("PDF saved as: {filename}", "INFO", "I1010"),
    
    # =========================================================================
    # PROCESS COMPLETION
    # =========================================================================
    "COMPLETION_SEARCHING": ("🔍 Searching for assignment ZIP...", "INFO", "I1011"),
    "COMPLETION_PROCESSING": ("📦 Processing: {filename}", "INFO", "I1012"),
    "COMPLETION_SUCCESS": ("✅ Completion processing completed!", "SUCCESS", "S1007"),
    "COMPLETION_AUTO_ASSIGNED": ("✅ Auto-assigned {count} points to {students} submissions", "SUCCESS", "S1008"),
    "COMPLETION_VALIDATION": ("📋 Validating student submissions...", "INFO", "I1013"),
    "COMPLETION_VALIDATED": ("✅ Validation complete", "SUCCESS", "S1009"),
    
    # =========================================================================
    # EXTRACT GRADES
    # =========================================================================
    "GRADES_STARTING": ("🔬 Starting grade extraction...", "INFO", "I1014"),
    "GRADES_PDF_NOT_FOUND": ("❌ Combined PDF not found", "ERROR", "E1003"),
    "GRADES_IMPORT_NOT_FOUND": ("❌ Import file not found", "ERROR", "E1004"),
    "GRADES_NO_RESULTS": ("❌ No grades were extracted from the PDF", "ERROR", "E1005"),
    "GRADES_SUCCESS": ("✅ Grade extraction completed successfully!", "SUCCESS", "S1010"),
    "GRADES_ISSUES_HEADER": ("ISSUES FOUND (Please Review):", "WARNING", None),
    "GRADES_NO_GRADE": ("❌ NO GRADE FOUND:", "ERROR", None),
    "GRADES_LOW_CONFIDENCE": ("❌ LOW CONFIDENCE (needs verification):", "WARNING", None),
    "GRADES_NAME_ISSUES": ("⚠️ NAME MATCHING ISSUES (fuzzy match):", "WARNING", None),
    "GRADES_NO_SUBMISSIONS": ("❌ NO SUBMISSIONS:", "ERROR", None),
    
    # =========================================================================
    # SPLIT PDF / REZIP
    # =========================================================================
    "SPLIT_STARTING": ("📦 Starting PDF split and rezip...", "INFO", "I1015"),
    "SPLIT_SUCCESS": ("✅ Split PDF and rezip completed!", "SUCCESS", "S1011"),
    "SPLIT_CREATING_ZIP": ("📦 Creating new ZIP: {filename}", "INFO", "I1016"),
    "SPLIT_ZIP_CREATED": ("✅ Created ZIP file: {filename}", "SUCCESS", "S1012"),
    
    # =========================================================================
    # OPEN FOLDERS
    # =========================================================================
    "FOLDER_OPENED": ("📂 Folder opened", "SUCCESS", "S1013"),
    "FOLDER_CLASS_OPENED": ("📂 Class roster folder opened", "SUCCESS", "S1014"),
    "DOWNLOADS_OPENING": ("📁 Opening Downloads folder...", "INFO", "I1017"),
    "DOWNLOADS_OPENED": ("✅ Downloads folder opened successfully!", "SUCCESS", "S1015"),
    
    # =========================================================================
    # CLEAR DATA
    # =========================================================================
    "CLEAR_STARTING": ("🗑️ Starting cleanup for {class_name}", "INFO", "I1018"),
    "CLEAR_SUCCESS": ("✅ Cleanup completed!", "SUCCESS", "S1016"),
    "CLEAR_ARCHIVED": ("🗑️ Clearing all archived data for {class_name}", "INFO", "I1019"),
    "CLEAR_ARCHIVED_SUCCESS": ("✅ Cleared {count} archived folder(s)", "SUCCESS", "S1017"),
    "CLEAR_NO_ARCHIVED": ("ℹ️ No archived folders found", "INFO", "I1020"),
    "CLEAR_TARGET_FOLDER": ("Target folder: {folder_name}", "INFO", "I1021"),
    "CLEAR_MODE_SELECTIVE": ("Mode: Selective (save folders and PDF)", "INFO", "I1022"),
    "CLEAR_MODE_FULL": ("Mode: Full delete", "INFO", "I1023"),
    "CLEAR_DELETED": ("✅ Deleted: {folder_name}", "SUCCESS", "S1018"),
    "CLEAR_ARCHIVED_TO": ("✅ Archived to: {folder_name}", "SUCCESS", "S1019"),
    "CLEAR_SELECTIVE_COMPLETE": ("✅ Selective clear completed", "SUCCESS", "S1020"),
    "CLEAR_FOUND_MATCHING": ("⚠️ Found matching folder: {folder_name}", "WARNING", "W1004"),
    "ERR_CLEAR_FOLDER_NOT_FOUND": ("❌ Processing folder not found for assignment: {assignment}\n   Tried: {path}", "ERROR", "E1008"),
    "ERR_CLEAR_FAILED": ("❌ {message}", "ERROR", "E1009"),
    "ERR_CLEAR_FAILED_DELETE": ("❌ Failed to delete folder (may be in use)", "ERROR", "E1010"),
    "ERR_CLEAR_FAILED_RENAME": ("❌ Failed to rename: {error}", "ERROR", "E1011"),
    
    # =========================================================================
    # BACKUP OPERATIONS
    # =========================================================================
    "BACKUP_CREATING": ("Existing folder found, creating backup...", "INFO", "I1025"),
    "BACKUP_RENAMING": ("   Renaming: {old_name}", "INFO", "I1026"),
    "BACKUP_TO": ("         to: {new_name}", "INFO", "I1027"),
    "BACKUP_SUCCESS": ("   Backup created successfully", "SUCCESS", "S1021"),
    "BACKUP_DELETING": ("Existing folder found, deleting...", "INFO", "I1028"),
    "BACKUP_DELETE_SUCCESS": ("   Folder deleted successfully", "SUCCESS", "S1022"),
    
    # =========================================================================
    # IMPORT FILE
    # =========================================================================
    "IMPORT_SETTING_UP": ("Setting up Import File column...", "INFO", "I1029"),
    "IMPORT_COLUMN_CREATED": ("   Created column: '{column}'", "SUCCESS", "S1023"),
    "IMPORT_COLUMN_EXISTS": ("   Column already exists: '{column}'", "INFO", "I1030"),
    "IMPORT_READY": ("   Import File ready for grade extraction", "SUCCESS", "S1024"),
    "IMPORT_LOADED": ("Loaded Import File: {count} students", "INFO", "I1031"),
    
    # =========================================================================
    # STUDENT PROCESSING
    # =========================================================================
    "STUDENTS_UNIQUE": ("Found {count} unique students", "INFO", "I1032"),
    "STUDENT_MATCHED": ("{name}: Matched using name parts → {roster_name}", "INFO", "I1033"),
    "STUDENT_NEWER": ("{name}: Found newer submission, using that", "INFO", "I1034"),
    "STUDENT_PDF": ("📄 {name} — PDF", "INFO", "I1035"),
    
    # =========================================================================
    # FILE ERRORS (CONSISTENT ACROSS APP)
    # =========================================================================
    "ERR_FILE_LOCKED": ("❌ File is in use - please close it and try again", "ERROR", "E1012"),
    "ERR_FILE_NOT_FOUND": ("❌ File not found: {file}", "ERROR", "E1013"),
    "ERR_PERMISSION": ("❌ Permission denied - check file permissions", "ERROR", "E1014"),
    "ERR_CORRUPT": ("❌ File is corrupted - please re-download", "ERROR", "E1015"),
    "ERR_NO_ZIP": ("❌ No ZIP files found in Downloads", "ERROR", "E1016"),
    "ERR_NO_FOLDER": ("❌ No grade processing folder found", "ERROR", "E1017"),
    "ERR_NO_PROCESSING_FOLDERS": ("❌ No processing folders found for this class", "ERROR", "E1018"),
    "ERR_NO_ASSIGNMENTS": ("❌ No assignments selected", "ERROR", "E1019"),
    "ERR_NO_ARCHIVED": ("ℹ️ No archived folders found for this class", "INFO", "I1024"),
    "ERR_UNZIPPED_NOT_FOUND": ("❌ Unzipped folders directory not found", "ERROR", "E1020"),
    "ERR_ZIP_CREATE": ("❌ Error creating ZIP: {error}", "ERROR", "E1021"),
    "ERR_COULD_NOT_MATCH": ("{name}: Could not match to roster", "WARNING", "W1005"),
    "ERR_COULD_NOT_DELETE": ("   Could not delete folder: {error}", "ERROR", "E1022"),
    "ERR_COULD_NOT_BACKUP": ("   Could not create backup: {error}", "ERROR", "E1023"),
    "ERR_COULD_NOT_OPEN_PDF": ("   Could not open PDF: {error}", "ERROR", "E1024"),
    "ERR_IMPORT_FILE": ("   Could not setup Import File: {error}", "ERROR", "E1025"),
    "ERR_GENERIC": ("❌ {error}", "ERROR", "E1026"),
    
    # =========================================================================
    # SUBMISSION PROCESSING
    # =========================================================================
    "SUBMISSION_PROCESSING_HEADER": ("PROCESSING STUDENT SUBMISSIONS", "INFO", "I1036"),
    "SUBMISSION_FOUND_UNIQUE": ("Found {count} unique students (after filtering duplicates)", "INFO", "I1037"),
    "SUBMISSION_MULTIPLE_PDFS_HEADER": ("Students who submitted multiple PDFs (combined automatically):", "INFO", "I1038"),
    "SUBMISSION_MULTIPLE_PDF_ITEM": ("   • {name}", "INFO", "I1039"),
    "SUBMISSION_NO_MATCH": ("   {name}: Could not match to roster", "WARNING", "W1006"),
    "SUBMISSION_NEWER_FOUND": ("   {name}: Found newer submission, using that", "INFO", "I1040"),
    "SUBMISSION_NAME_PARTS_MATCH": ("   {name}: Matched using name parts → {roster_name}", "INFO", "I1041"),
    "SUBMISSION_NO_SUB": ("   {name}: No submission", "INFO", "I1042"),
    "SUBMISSION_NO_SUB_POINTS": ("   {name}: No submission → 0 points", "INFO", "I1043"),
    "SUBMISSION_PDF_FOUND": ("   {name}: PDF found", "INFO", "I1044"),
    "SUBMISSION_PDF_FOUND_POINTS": ("   {name}: PDF found → 10 points", "INFO", "I1045"),
    "SUBMISSION_MULTI_PDF": ("   {name}: {count} PDFs found, combining", "INFO", "I1046"),
    "SUBMISSION_MULTI_PDF_POINTS": ("   {name}: {count} PDFs found, combining → 10 points", "INFO", "I1047"),
    "SUBMISSION_ERROR": ("   {error}", "ERROR", "E1027"),
    
    # =========================================================================
    # PDF OPERATIONS (CREATING/SPLITTING)
    # =========================================================================
    "PDF_CREATING": ("Creating combined PDF...", "INFO", "I1048"),
    "PDF_COMBINED_SUCCESS": ("✅ Combined PDF created: {filename}", "SUCCESS", "S1025"),
    "PDF_ERROR_PROCESSING": ("   Error processing {name}: {error}", "ERROR", "E1028"),
    "PDF_SPLITTING_HEADER": ("SPLITTING COMBINED PDF", "INFO", "I1049"),
    "PDF_TOTAL_PAGES": ("   Combined PDF has {pages} pages", "INFO", "I1050"),
    "PDF_EXTRACTING_NAMES": ("   Extracting student names from PDF...", "INFO", "I1051"),
    "PDF_EXTRACTED_COUNT": ("   Extracted {count} names from PDF", "INFO", "I1052"),
    "PDF_FIRST_NAMES_HEADER": ("   First 10 names found:", "INFO", "I1053"),
    "PDF_NAME_ITEM": ("      {num:2d}. {name}", "INFO", "I1054"),
    "PDF_MORE_NAMES": ("      ... and {count} more", "INFO", "I1055"),
    "PDF_SPLIT_SUCCESS": ("Successfully split PDF for {count} students", "SUCCESS", "S1026"),
    "PDF_SPLIT_ERROR": ("Error splitting combined PDF: {error}", "ERROR", "E1029"),
    "PDF_NO_FOLDER_FOR": ("   Could not find folder for: {name}", "WARNING", "W1007"),
    "PDF_PROCESSING_STUDENT": ("   Processing {name}: {pages} pages", "INFO", "I1056"),
    "PDF_FOUND_FOLDER": ("      Found folder: {folder}", "INFO", "I1057"),
    "PDF_NO_PDF_IN_FOLDER": ("   No PDF found in {name}'s folder", "WARNING", "W1008"),
    "PDF_REPLACING": ("      Replacing: {filename}", "INFO", "I1058"),
    "PDF_STUDENT_COMPLETE": ("   {name}: {pages} pages → {filename}", "SUCCESS", "S1027"),
    
    # =========================================================================
    # IMPORT FILE OPERATIONS
    # =========================================================================
    "IMPORT_CLOSED_EXCEL": ("   📋 Closed Excel to save import file", "INFO", "I1059"),
    "IMPORT_NO_EOL": ("   ⚠️  End-of-Line Indicator not found - adding it to column F", "WARNING", "W1009"),
    "IMPORT_FILE_NOT_FOUND": ("❌ Import File not found: {path}", "ERROR", "E1030"),
    "IMPORT_FILE_IN_USE": ("❌ The file is being used by another process", "ERROR", "E1031"),
    "IMPORT_PERMISSION_DENIED": ("❌ Cannot access file - permission denied", "ERROR", "E1032"),
    "IMPORT_UNABLE_TO_READ": ("❌ Unable to read file", "ERROR", "E1033"),
    "IMPORT_LOADED_STUDENTS": ("Loaded Import File: {count} students", "INFO", "I1060"),
    "IMPORT_UPDATE_HEADER": ("UPDATING IMPORT FILE", "INFO", "I1061"),
    "IMPORT_CURRENT_COLUMNS": ("Current columns: {columns}", "INFO", "I1062"),
    "IMPORT_NEW_COLUMN": ("   New column name: '{name}'", "INFO", "I1063"),
    "IMPORT_UPDATING_GRADES": ("   Updating grades...", "INFO", "I1064"),
    "IMPORT_SAVING_TO": ("   Saving to: {path}", "INFO", "I1065"),
    "IMPORT_FUZZY_HEADER": ("   ⚠️  Fuzzy name matches (please verify):", "WARNING", "W1010"),
    "IMPORT_FUZZY_ITEM": ("{warning}", "WARNING", "W1011"),
    "IMPORT_UPDATE_ERROR": ("Error updating import file: {error}", "ERROR", "E1034"),
    "IMPORT_CLEANUP_COLUMNS": ("   🧹 Cleaning up {count} corrupted columns after End-of-Line Indicator", "INFO", "I1066"),
    "IMPORT_MODE_DONT_OVERRIDE": ("   Mode: Don't override - adding new column before End-of-Line Indicator", "INFO", "I1067"),
    "IMPORT_MODE_OVERRIDE": ("   Mode: Override - removing old grade columns", "INFO", "I1068"),
    "IMPORT_WARNING_FEW_COLUMNS": ("   Warning: Less than {required} columns, adding empty columns", "WARNING", "W1012"),
    "IMPORT_COLUMN_EXISTS": ("   Column '{name}' already exists, using existing column", "INFO", "I1069"),
    "IMPORT_ADDED_COLUMN": ("   Added new column '{name}' at index {index} (before '{before}')", "SUCCESS", "S1028"),
    "IMPORT_FIXED_COLUMNS": ("   Fixed columns (0-{count}): {columns}", "INFO", "I1070"),
    "IMPORT_EOL_INFO": ("   End-of-Line Indicator: '{name}' at index {index}", "INFO", "I1071"),
    "IMPORT_TOTAL_COLUMNS": ("   Current total columns: {count}", "INFO", "I1072"),
    "IMPORT_REMOVING_OLD": ("   Removing {count} old grade columns: {columns}", "INFO", "I1073"),
    "IMPORT_RESULT_COLUMNS": ("   Result: {count} columns", "INFO", "I1074"),
    "IMPORT_ADDED_AT_INDEX": ("   Added grade column '{name}' at index 5", "SUCCESS", "S1029"),
    
    # =========================================================================
    # BACKUP OPERATIONS (DETAILED)
    # =========================================================================
    "BACKUP_DELETING_FOLDER": ("Existing folder found, deleting...", "INFO", "I1075"),
    "BACKUP_DELETING_NAME": ("   Deleting: {name}", "INFO", "I1076"),
    "BACKUP_DELETED": ("   Folder deleted successfully", "SUCCESS", "S1030"),
    "BACKUP_DELETE_FAILED": ("   Could not delete folder: {error}", "ERROR", "E1035"),
    "BACKUP_RENAME_FROM": ("   Renaming: {old_name}", "INFO", "I1077"),
    "BACKUP_RENAME_TO": ("         to: {new_name}", "INFO", "I1078"),
    "BACKUP_CREATE_FAILED": ("   Could not create backup: {error}", "ERROR", "E1036"),
    
    # =========================================================================
    # SPLIT PDF / REZIP OPERATIONS
    # =========================================================================
    "REZIP_UNZIPPED_NOT_FOUND": ("❌ Unzipped folders directory not found", "ERROR", "E1037"),
    "REZIP_CREATING": ("📦 Creating new ZIP: {filename}", "INFO", "I1079"),
    "REZIP_USING_ORIGINAL_INDEX": ("   Using preserved original index.html (exact copy)", "INFO", "I1080"),
    "REZIP_USING_EXTRACTED_INDEX": ("   Using original index.html from extraction (exact copy)", "INFO", "I1081"),
    "REZIP_WARNING_NO_INDEX": ("   Warning: No original index.html found, generating new one", "WARNING", "W1013"),
    "REZIP_GENERATED_INDEX": ("   Generated new index.html (fallback - may not work with D2L)", "WARNING", "W1014"),
    "REZIP_ADDED_INDEX": ("   Added index.html to ZIP root", "INFO", "I1082"),
    "REZIP_ADDED_ROOT_FILE": ("   Added root file: {filename}", "INFO", "I1083"),
    "REZIP_ADDED_FILE": ("Added: {filename}", "INFO", "I1084"),
    "REZIP_CREATED_ZIP": ("✅ Created ZIP file: {path}", "SUCCESS", "S1031"),
    "REZIP_ERROR": ("❌ Error creating ZIP: {error}", "ERROR", "E1038"),
    "REZIP_ERROR_DETAILS": ("   Details: {details}", "ERROR", "E1039"),
    
    # =========================================================================
    # SPLIT PDF CLI SPECIFIC
    # =========================================================================
    "SPLIT_STARTING_PROCESS": ("📦 Starting PDF split and rezip...", "INFO", "I1085"),
    "SPLIT_SPLITTING_PDF": ("Splitting combined PDF into individual student PDFs...", "INFO", "I1086"),
    "SPLIT_SUCCESS_COUNT": ("✅ Successfully split PDF for {count} students", "SUCCESS", "S1032"),
    "SPLIT_NO_STUDENTS": ("⚠️ No students processed - check if combined PDF exists", "WARNING", "W1015"),
    "SPLIT_CREATING_ZIP_FILE": ("Creating ZIP file: {filename}...", "INFO", "I1087"),
    "SPLIT_UNZIPPED_NOT_FOUND": ("❌ Unzipped folders directory not found - cannot create ZIP", "ERROR", "E1042"),
    "SPLIT_ZIP_FAILED": ("⚠️ ZIP creation failed, but PDFs were split", "WARNING", "W1016"),
    "SPLIT_NO_NAME": ("⚠️ Could not determine assignment name or ZIP name, skipping rezip", "WARNING", "W1017"),
    "SPLIT_ERRORS_HEADER": ("❌ Errors:", "ERROR", "E1040"),
    "SPLIT_ERROR_ITEM": ("   {error}", "ERROR", "E1041"),
    "SPLIT_COMPLETED": ("✅ Split PDF and rezip completed!", "SUCCESS", "S1033"),
    
    # =========================================================================
    # PROCESS COMPLETION CLI SPECIFIC
    # =========================================================================
    "COMPLETION_HEADER_START": ("COMPLETION PROCESSING STARTED", "INFO", "I1088"),
    "COMPLETION_CLASS": ("Class: {class_name}", "INFO", "I1089"),
    "COMPLETION_USING_ZIP": ("Using specified ZIP file: {filename}", "INFO", "I1090"),
    "COMPLETION_LOOKING_FOR_ZIP": ("Looking for ZIP files in Downloads folder...", "INFO", "I1091"),
    "COMPLETION_FOUND_ONE_ZIP": ("Found 1 ZIP file: {filename}", "INFO", "I1092"),
    "COMPLETION_SELECTED_ZIP": ("Selected ZIP file: {filename}", "INFO", "I1093"),
    "COMPLETION_PROCESSING_HEADER": ("STARTING COMPLETION PROCESSING", "INFO", "I1094"),
    "COMPLETION_AUTO_ASSIGN": ("(Auto-assigning 10 points to all submissions)", "INFO", "I1095"),
    "COMPLETION_MODE_DONT_OVERRIDE": ("Mode: Don't override (adding new column after column E)", "INFO", "I1096"),
    "COMPLETION_MODE_OVERRIDE": ("Mode: Override column E (existing behavior)", "INFO", "I1097"),
    "COMPLETION_SUCCESS": ("Completion processing completed successfully!", "SUCCESS", "S1034"),
    "COMPLETION_OPENED_PDF": ("Opened PDF file: {filename}", "INFO", "I1098"),
    "COMPLETION_COULD_NOT_OPEN_PDF": ("Could not open PDF: {error}", "WARNING", "W1018"),
    "COMPLETION_HEADER_COMPLETE": ("COMPLETION PROCESSING COMPLETED", "SUCCESS", "S1035"),
    "COMPLETION_FAILED_HEADER": ("COMPLETION PROCESSING FAILED", "ERROR", "E1043"),
    "COMPLETION_FINISHED": ("PROCESSING FINISHED", "INFO", "I1099"),
    
    # =========================================================================
    # MISC
    # =========================================================================
    "SELECTED_FILE": ("📄 Selected: {filename}", "INFO", "I1100"),
    "OPENING_PDF": ("Opening combined PDF for manual grading...", "INFO", "I1101"),
    "SEPARATOR_LINE": ("-" * 40, "INFO", "I1102"),
    "SEPARATOR_DOUBLE": ("=" * 60, "INFO", "I1103"),
    "DOUBLE_SEPARATOR_LINE": ("=" * 60, "INFO", "I1103"),  # Alias for SEPARATOR_DOUBLE
    "EMPTY_LINE": ("", "INFO", "I1104"),
    "ERR_UNEXPECTED": ("❌ {error}", "ERROR", "E1044"),
    
    # =========================================================================
    # DEVELOPER ERROR LOGGING (D2xxx series - not shown to users)
    # =========================================================================
    "DEV_ERROR_OPEN_PDF": ("DEV: Could not open combined PDF: {error}", "ERROR", "D2001"),
    "DEV_ERROR_PARSE_INDEX": ("DEV: Could not parse index.html: {error}", "ERROR", "D2002"),
    "DEV_ERROR_PDF_PAGE_COUNT": ("DEV: Could not read page count for {name}: {error}", "ERROR", "D2003"),
    "DEV_ERROR_READ_MULTI_PDF": ("DEV: Could not read {file} for {name}: {error}", "ERROR", "D2004"),
    "DEV_ERROR_COMBINE_PDFS": ("DEV: Could not combine PDFs for {name}: {error}", "ERROR", "D2005"),
    "DEV_ERROR_FALLBACK_PDF": ("DEV: Fallback PDF copy failed for {name}: {error}", "ERROR", "D2006"),
    "DEV_ERROR_OPEN_EXTRACTED_FILES": ("DEV: Could not open extracted files: {error}", "ERROR", "D2007"),
}

