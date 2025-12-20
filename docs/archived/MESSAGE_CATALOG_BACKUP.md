# Message Catalog Backup

This file preserves all current log messages before the logging system rebuild.
Use these as the foundation for the new message catalog.

---

## SUCCESS MESSAGES

| ID | Message | Used In |
|----|---------|---------|
| CLASS_LOADED | ✅ Class loaded: {class_name} | Option2.tsx |
| QUIZ_SUCCESS | ✅ Quiz processing completed! | Option2.tsx, process_quiz_cli.py |
| COMPLETION_SUCCESS | ✅ Completion processing completed! | Option2.tsx |
| COMPLETION_AUTO_ASSIGN | ✅ Auto-assigned 10 points to all submissions | Option2.tsx, grading_processor.py |
| SPLIT_SUCCESS | ✅ Split PDF and rezip completed! | Option2.tsx |
| DATA_CLEARED | ✅ Data cleared successfully! | Option2.tsx |
| ARCHIVED_CLEARED | ✅ All archived data cleared successfully! | Option2.tsx |
| CLASSES_FOUND | ✅ Found {count} classes | Option2.tsx |
| DOWNLOADS_OPENED | ✅ Downloads folder opened successfully! | Option2.tsx |
| FOLDER_OPENED | 📂 Folder opened | Option2.tsx |
| CLASS_FOLDER_OPENED | 📂 Class roster folder opened | Option2.tsx |
| PDF_CREATED | ✅ Combined PDF created! | grading_processor.py |
| ZIP_VALIDATED | ✅ ZIP structure validated | grading_processor.py |
| EXTRACTED_FOLDERS | ✅ Extracted {count} student folders | grading_processor.py |
| IMPORT_FILE_READY | Import File ready for grade extraction | grading_processor.py |
| ZIP_CREATED | ✅ Created ZIP file: {filename} | split_pdf_cli.py |
| GRADE_EXTRACTION_SUCCESS | ✅ Grade extraction completed successfully! | extract_grades_cli.py |
| NAMES_MATCH | ✅ All student names match Import File | grading_processor.py |
| BACKUP_CREATED | Backup created successfully | backup_utils.py |
| FOLDER_DELETED | Folder deleted successfully | backup_utils.py |

---

## ERROR MESSAGES

| ID | Message | Used In |
|----|---------|---------|
| ERR_NO_CLASS | ❌ Please select a class first | Option2.tsx (many places) |
| ERR_NO_ZIP | ❌ No ZIP files found in Downloads | grading_processor.py |
| ERR_NO_FOLDER | ❌ No grade processing folder found | Option2.tsx |
| ERR_NO_PROCESSING_FOLDERS | ❌ No processing folders found for this class | Option2.tsx |
| ERR_NO_ASSIGNMENTS | ❌ No assignments selected | Option2.tsx |
| ERR_NO_ROSTER_FOLDER | ❌ Could not find roster folder | Option2.tsx |
| ERR_FILE_LOCKED | ❌ The file is being used by another process | clear_data_cli.py |
| ERR_PERMISSION | ❌ Cannot access file - permission denied | clear_data_cli.py |
| ERR_CORRUPT | ❌ File is corrupted or invalid | (implied) |
| ERR_UNZIPPED_NOT_FOUND | ❌ Unzipped folders directory not found | split_pdf_cli.py |
| ERR_ZIP_CREATE | ❌ Error creating ZIP: {error} | split_pdf_cli.py |
| ERR_COULD_NOT_MATCH | {name}: Could not match to roster | submission_processor.py |
| ERR_STUDENT_ERRORS | ❌ STUDENT ERRORS AND WARNINGS: | grading_processor.py |
| ERR_COULD_NOT_DELETE | Could not delete folder: {error} | backup_utils.py |
| ERR_COULD_NOT_BACKUP | Could not create backup: {error} | backup_utils.py |
| ERR_COULD_NOT_OPEN_PDF | Could not open PDF: {error} | grading_processor.py |
| ERR_IMPORT_FILE | Could not setup Import File: {error} | grading_processor.py |

---

## INFO/STATUS MESSAGES

| ID | Message | Used In |
|----|---------|---------|
| LOCATION | 📂 Location: {path} | Option2.tsx |
| LOADING_CLASSES | 📂 Loading classes from Rosters etc folder... | Option2.tsx |
| OPENING_DOWNLOADS | 📁 Opening Downloads folder... | Option2.tsx |
| SEARCHING_ZIP | 🔍 Searching for assignment ZIP in Downloads... | Option2.tsx |
| PROCESSING_FILE | 📦 Processing: {filename} | Option2.tsx |
| STARTING_SPLIT | 📦 Starting PDF split and rezip... | Option2.tsx |
| CLEARING_DATA | 🗑️ Clearing data for: {assignment}... | Option2.tsx |
| CLEARING_ARCHIVED | 🗑️ Clearing all archived data... | Option2.tsx |
| CLEARING_MULTIPLE | 🗑️ Clearing {count} assignment(s)... | Option2.tsx |
| FOUND_ARCHIVED | 📦 Found {count} archived folder(s) to delete | Option2.tsx |
| PLEASE_WAIT | ⏳ This may take a moment... | Option2.tsx |
| PROCESSING_ASSIGNMENT | 📂 Processing: {assignment}... | Option2.tsx |
| SELECTED_FILE | 📄 Selected: {filename} | Option2.tsx |
| NO_ARCHIVED | ℹ️ No archived folders found for this class | Option2.tsx |
| LOOKING_FOR_QUIZ | Looking for quiz files in Downloads... | grading_processor.py |
| FOUND_QUIZ_FILE | Found quiz file: {filename} | grading_processor.py |
| ASSIGNMENT_NAME | Assignment: {name} | grading_processor.py |
| VALIDATING_ZIP | Validating ZIP file structure... | grading_processor.py |
| EXTRACTING_TO | Extracting to: {folder} | grading_processor.py |
| PDF_SAVED | PDF saved as: {filename} | grading_processor.py |
| USING_ZIP | ✓ Using: {filename} | process_quiz_cli.py |
| SETTING_UP_IMPORT | Setting up Import File column... | grading_processor.py |
| CREATED_COLUMN | Created column: '{column}' | grading_processor.py |
| COLUMN_EXISTS | Column already exists: '{column}' | grading_processor.py |
| OPENING_PDF | Opening combined PDF for manual grading... | grading_processor.py |
| EXISTING_FOLDER_BACKUP | Existing folder found, creating backup... | backup_utils.py |
| EXISTING_FOLDER_DELETE | Existing folder found, deleting... | backup_utils.py |
| RENAMING_FOLDER | Renaming: {old_name} → {new_name} | backup_utils.py |
| CREATING_ZIP | 📦 Creating new ZIP: {filename} | split_pdf_cli.py |
| UNIQUE_STUDENTS | Found {count} unique students (after filtering duplicates) | submission_processor.py |
| MATCHED_USING_PARTS | {name}: Matched using name parts → {roster_name} | submission_processor.py |
| NEWER_SUBMISSION | {name}: Found newer submission, using that | submission_processor.py |

---

## GRADE EXTRACTION MESSAGES

| ID | Message | Used In |
|----|---------|---------|
| GRADE_EXTRACTION_START | 🔬 Starting grade extraction... | extract_grades_cli.py |
| ISSUES_FOUND | ISSUES FOUND (Please Review): | extract_grades_cli.py |
| NO_GRADE_FOUND | ❌ NO GRADE FOUND: | extract_grades_cli.py |
| LOW_CONFIDENCE | ❌ LOW CONFIDENCE (needs verification): | extract_grades_cli.py |
| NAME_MATCHING_ISSUES | ⚠️ NAME MATCHING ISSUES (fuzzy match - needs verification): | extract_grades_cli.py |
| NO_SUBMISSIONS | ❌ NO SUBMISSIONS: | extract_grades_cli.py |

---

## VALIDATION MESSAGES (Completion Processing)

| ID | Message | Used In |
|----|---------|---------|
| VALIDATION_CHECKS | VALIDATION CHECKS | grading_processor.py |
| STEP1_VALIDATING_ZIP | 📦 Step 1: Validating ZIP file structure... | grading_processor.py |
| ZIP_VALID | ✅ ZIP file structure is valid | grading_processor.py |
| STEP2_VALIDATING_IMPORT | 📋 Step 2: Validating Import File structure... | grading_processor.py |
| IMPORT_VALID | ✅ Import File structure is valid | grading_processor.py |
| STEP3_VALIDATING_NAMES | 👥 Step 3: Validating student names match Import File... | grading_processor.py |
| VALIDATION_COMPLETE | VALIDATION COMPLETE - Starting Processing | grading_processor.py |

---

## TECHNICAL/DEV MESSAGES (to be hidden from users)

| ID | Message | Used In |
|----|---------|---------|
| DRIVE_INFO | Drive: {drive}: | grading_processor.py |
| CLASS_INFO | Class: {class_name} | grading_processor.py |
| PROCESSING_FOLDER_INFO | Processing folder: {path} | grading_processor.py |
| PRESERVED_INDEX | Preserved original index.html | grading_processor.py |
| PROCESSING_STUDENT_SUBMISSIONS | PROCESSING STUDENT SUBMISSIONS | submission_processor.py |
| PROCESSING_COMPLETE_BANNER | PROCESSING COMPLETE! | grading_processor.py |
| REVERSE_PROCESSING_COMPLETE | REVERSE PROCESSING COMPLETE! | grading_processor.py |
| ADDED_INDEX | Added index.html to ZIP root | split_pdf_cli.py |

---

## Notes for New System

1. **Consolidate duplicates**: "Quiz processing completed" appears in BOTH frontend and backend - should only be ONE
2. **Consistent error format**: All errors should start with ❌
3. **Consistent success format**: All successes should start with ✅
4. **Remove technical details from user view**: Drive:, Class:, Processing folder: should be dev-only
5. **Simplify**: Many messages are too verbose for users

