# D2L Automation Patterns

## Browser Automation with Playwright

### Pattern: Async Browser Context Management
When working with Playwright for D2L automation:
- Always use async/await patterns
- Implement proper error handling with try/except blocks
- Write debug reports on exceptions for troubleshooting
- Use persistent browser contexts to maintain login sessions

```python
async def automate_d2l(page, context):
    try:
        # Automation logic here
        await page.goto(url)
        # ...
    except Exception as e:
        logger.error(f"Error: {e}")
        _write_debug_report("stage_name", e)
```

### Pattern: Element Selection with Fallbacks
D2L UI can vary, so implement multiple selection strategies:
- Try CSS selectors first
- Fall back to XPath if needed
- Use fuzzy matching for assignment names
- Add explicit waits for dynamic content

```python
# Try multiple selectors
try:
    element = await page.wait_for_selector('.primary-selector', timeout=5000)
except:
    element = await page.wait_for_selector('xpath=//fallback', timeout=5000)
```

## Date Processing Patterns

### Pattern: Date Input Handling
When setting dates in D2L forms:
- Clear existing values before setting new ones
- Use consistent date format (YYYY-MM-DD)
- Handle time separately from date
- Verify checkboxes are properly set/unset

```python
def set_date_in_dialog(date_str, time_str):
    # Clear existing
    date_input.clear()
    # Set new date
    date_input.send_keys(date_str)
    # Set time
    time_input.send_keys(time_str)
```

### Pattern: CSV Processing
When processing assignment dates from CSV:
- Validate CSV structure before processing
- Use pandas for robust CSV handling
- Implement progress tracking/logging
- Handle missing or invalid data gracefully

```python
import pandas as pd

def process_csv_file(csv_path):
    df = pd.read_csv(csv_path)
    required_columns = ['Assignment Name', 'Start Date', 'Due Date']

    if not all(col in df.columns for col in required_columns):
        raise ValueError("Missing required columns")

    for _, row in df.iterrows():
        # Process each assignment
        logger.info(f"Processing: {row['Assignment Name']}")
```

## Logging and Debugging

### Pattern: Comprehensive Logging
Maintain detailed logs for debugging:
- Use different log levels appropriately (DEBUG, INFO, WARNING, ERROR)
- Log all significant actions and state changes
- Include timestamps in all log entries
- Create separate debug logs for complex operations

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# File handler for detailed logs
fh = logging.FileHandler('d2l_processor.log')
fh.setLevel(logging.DEBUG)

# Console handler for important messages
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
```

### Pattern: Debug Report Generation
When errors occur, generate comprehensive debug reports:
- Capture full exception traceback
- Include system state (page URL, elements visible)
- Save HTML snapshots if applicable
- Auto-open reports in text editor for immediate review

```python
def _write_debug_report(stage, exception):
    report_path = os.path.join(LOGS_DIR, f'debug_{stage}_{timestamp}.txt')
    with open(report_path, 'w') as f:
        f.write(f"Stage: {stage}\n")
        f.write(f"Exception: {str(exception)}\n")
        f.write(f"Traceback:\n{traceback.format_exc()}\n")

    # Open in notepad for review
    subprocess.Popen(['notepad.exe', report_path])
```

## Error Handling and Recovery

### Pattern: Retry Logic
Implement retry mechanisms for flaky operations:
- Add configurable retry counts
- Use exponential backoff for waits
- Log each retry attempt
- Fail gracefully after max retries

```python
async def retry_operation(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### Pattern: Graceful Degradation
When automation fails:
- Capture current state before failing
- Provide clear error messages to users
- Suggest manual steps if automation cannot proceed
- Clean up resources (close browsers, save progress)

## Session Management

### Pattern: Persistent Login Sessions
Maintain user sessions across runs:
- Use Chrome profile directories
- Store session data securely
- Implement session validation
- Provide clear login functionality

```python
def setup_driver(use_profile=True):
    options = Options()
    if use_profile:
        profile_path = os.path.join(tempfile.gettempdir(), 'd2l_profile')
        options.add_argument(f'--user-data-dir={profile_path}')

    driver = webdriver.Chrome(options=options)
    return driver
```

## GUI Design Patterns

### Pattern: Tkinter GUI Structure
When building GUI applications:
- Separate GUI logic from business logic
- Use threading for long-running operations
- Update status labels to show progress
- Provide clear visual feedback for actions

```python
class D2LDateProcessorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.create_widgets()

    def process_csv(self):
        # Run in separate thread to prevent GUI freeze
        thread = threading.Thread(target=self._process_csv_thread)
        thread.start()

    def _process_csv_thread(self):
        # Business logic here
        self.update_status("Processing...")
```
