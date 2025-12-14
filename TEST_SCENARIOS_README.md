# Test Scenario Runner

This tool allows you to test different submission scenarios without needing real data. You can simulate various edge cases and see how the system handles them.

## Quick Start

Run the test scenario runner:

```bash
python test_scenario_runner.py
```

You'll be presented with a menu to select from pre-built scenarios or create your own.

## Available Scenarios

### 1. Basic Scenario
Normal submissions - all students have PDFs. Good for testing the happy path.

### 2. No PDF Scenario
One student is missing a PDF in their folder. Tests error handling for missing submissions.

### 3. Duplicate Submission
One student submitted twice. Tests that the system correctly identifies and uses the latest submission.

### 4. Mixed Issues
A comprehensive scenario with multiple different problems:
- Normal submission
- Missing PDF
- Duplicate submission
- Multiple PDFs (will be combined)
- Unreadable files (images)
- Empty folder

### 5. Custom Scenario
Create your own scenario interactively, defining exactly what you want to test.

### 6. Run All Scenarios
Run all pre-built scenarios in sequence.

## Scenario Types

When creating custom scenarios, you can specify these types for each student:

- **normal**: Student has a single PDF (default)
- **no_pdf**: Student has no PDF in their folder
- **duplicate**: Student submitted twice (will create two folders with different timestamps)
- **multiple_pdfs**: Student has multiple PDFs (will be combined automatically)
- **unreadable**: Student has non-PDF files (images, text files, etc.)
- **empty**: Student folder is empty

## Example Usage

### Testing Missing PDF Handling

```python
from test_scenario_runner import TestScenario, run_scenario

scenario = TestScenario("Missing PDF Test", "Test error handling for missing PDFs")
scenario.add_student("John", "Smith", "jsmith01", "normal", pdf_pages=5)
scenario.add_student("Jane", "Doe", "jdoe02", "no_pdf")  # This student has no PDF
scenario.add_student("Bob", "Johnson", "bjohnson03", "normal", pdf_pages=6)

run_scenario(scenario)
```

### Testing Duplicate Submissions

```python
from test_scenario_runner import TestScenario, run_scenario

scenario = TestScenario("Duplicate Test", "Test duplicate submission handling")
scenario.add_student("Jane", "Doe", "jdoe02", "duplicate", pdf_pages=8)
# This will create two submission folders with different timestamps
# The system should log that a newer submission was found

run_scenario(scenario)
```

## What Gets Tested

The test runner will:

1. Create temporary mock student folders with the specified scenarios
2. Create a mock roster (Import File.csv equivalent)
3. Run the actual `process_submissions` function
4. Display all logging output
5. Show a summary of results:
   - Which students submitted successfully
   - Which students had unreadable files
   - Which students had no submission
   - All errors and warnings
   - Page counts for each student

## Output

The test runner shows:
- Setup information (what folders were created)
- All log messages from the processing (exactly as they would appear in real usage)
- Results summary with counts and details
- Any errors that occurred

This lets you see exactly what messages and logging would appear for each scenario without needing to gather real data.

## Integration with Real Code

The test runner uses the actual `process_submissions` function from `submission_processor.py`, so you're testing the real code path. The only difference is that it uses temporary mock data instead of real student folders.
