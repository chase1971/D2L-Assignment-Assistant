# Move old/unused files to 'old' folder
# Run this from the Quiz-extraction folder

$oldFolder = "old"

# Create old folder
if (-not (Test-Path $oldFolder)) {
    New-Item -ItemType Directory -Path $oldFolder
    Write-Host "Created '$oldFolder' folder"
}

# Files and folders to MOVE TO OLD (not needed for NewStyle app)
$toMove = @(
    # Old Node.js stuff for the homepage launcher
    "node_modules",
    "package.json",
    "package-lock.json",
    
    # Old documentation/build files
    "BUILD-AND-INSTALL.bat",
    "ELECTRON-PACKAGING-GUIDE.md",
    "DOCUMENTATION.md",
    "AUTO-INSTALL-SETUP.md",
    
    # Temp/test files
    "__pycache__",
    "temp_output.json",
    "output.json",
    "Quiz-extraction.code-workspace",
    
    # Old/unused Python scripts (not called by NewStyle server)
    "extract_grades_cli_fixed.py",
    "extract_grades_simple.py",
    "compare_zips.py",
    "simple_extract_test.py",
    "test_matching.py",
    "minimal_extract.py"
)

Write-Host ""
Write-Host "Moving old files to '$oldFolder' folder..."
Write-Host ""

foreach ($item in $toMove) {
    if (Test-Path $item) {
        try {
            Move-Item -Path $item -Destination $oldFolder -Force
            Write-Host "  Moved: $item" -ForegroundColor Green
        } catch {
            Write-Host "  FAILED: $item - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  Skipped (not found): $item" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Done! You can now delete the 'old' folder when ready."
Write-Host ""
Write-Host "KEPT (required for NewStyle app):"
Write-Host "  - NewStyle/           (the new app)"
Write-Host "  - helper_cli.py"
Write-Host "  - process_quiz_cli.py"
Write-Host "  - process_completion_cli.py"
Write-Host "  - extract_grades_cli.py"
Write-Host "  - split_pdf_cli.py"
Write-Host "  - cleanup_data_cli.py"
Write-Host "  - grading_processor.py"
Write-Host "  - grade_parser.py"
Write-Host "  - ocr_utils.py"
Write-Host "  - config_reader.py"
Write-Host "  - requirements.txt"
Write-Host "  - .git/"
Write-Host ""

