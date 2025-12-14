# Selenium WebDriver Patterns for D2L

## Driver Setup and Configuration

### Pattern: Persistent Chrome Profile
Use persistent Chrome profiles to maintain login sessions:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import os

def setup_driver(use_profile=True):
    options = Options()

    if use_profile:
        profile_path = os.path.join(tempfile.gettempdir(), 'd2l_profile')
        options.add_argument(f'--user-data-dir={profile_path}')

    # Additional options for stability
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver
```

## Element Interaction Patterns

### Pattern: Safe Element Interaction
Always use explicit waits and handle stale elements:

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

def safe_click(driver, locator, timeout=10):
    """Safely click an element with retry logic."""
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            return True
        except StaleElementReferenceException:
            if attempt < max_attempts - 1:
                continue
            raise
        except TimeoutException:
            logger.error(f"Element not clickable: {locator}")
            return False
```

### Pattern: Iframe Handling
D2L uses iframes extensively, handle them properly:

```python
def interact_with_iframe(driver, iframe_locator, action_fn):
    """
    Switch to iframe, perform action, then switch back.

    Args:
        driver: Selenium WebDriver instance
        iframe_locator: Tuple of (By.*, 'locator_string')
        action_fn: Function to execute within iframe context
    """
    try:
        # Wait for iframe to be available
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(iframe_locator)
        )

        # Perform action within iframe
        result = action_fn(driver)

        return result
    finally:
        # Always switch back to default content
        driver.switch_to.default_content()
```

## Input and Form Handling

### Pattern: Clear and Safe Text Input
Clear inputs properly before setting new values:

```python
def set_input_value(driver, locator, value, clear_first=True):
    """
    Safely set input field value.

    Args:
        driver: Selenium WebDriver instance
        locator: Tuple of (By.*, 'locator_string')
        value: Value to set
        clear_first: Whether to clear existing value first
    """
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(locator)
    )

    if clear_first:
        element.clear()
        # Verify it's actually cleared
        if element.get_attribute('value'):
            # Try JavaScript clear as backup
            driver.execute_script("arguments[0].value = '';", element)

    element.send_keys(value)

    # Verify value was set
    actual_value = element.get_attribute('value')
    if actual_value != value:
        logger.warning(f"Value mismatch. Expected: {value}, Got: {actual_value}")
```

### Pattern: Checkbox Management
Handle checkboxes with state verification:

```python
def set_checkbox_state(driver, checkbox_locator, should_be_checked):
    """
    Set checkbox to specific state.

    Args:
        driver: Selenium WebDriver instance
        checkbox_locator: Tuple of (By.*, 'locator_string')
        should_be_checked: Boolean - desired state
    """
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(checkbox_locator)
    )

    is_checked = checkbox.is_selected()

    # Only click if state needs to change
    if is_checked != should_be_checked:
        checkbox.click()

        # Verify state changed
        if checkbox.is_selected() != should_be_checked:
            logger.error("Checkbox state did not change as expected")
            raise Exception("Failed to set checkbox state")
```

## Wait Strategies

### Pattern: Custom Wait Conditions
Create custom wait conditions for complex scenarios:

```python
class element_has_text(object):
    """Wait until element contains specific text."""

    def __init__(self, locator, text):
        self.locator = locator
        self.text = text

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        return self.text in element.text

# Usage
WebDriverWait(driver, 10).until(
    element_has_text((By.ID, 'status'), 'Success')
)
```

### Pattern: Fuzzy Element Finding
Find elements with fuzzy text matching:

```python
import re

def find_element_by_fuzzy_text(driver, text, tag='*', threshold=0.8):
    """
    Find element by fuzzy matching text content.

    Args:
        driver: Selenium WebDriver instance
        text: Text to search for
        tag: HTML tag to search within (default: any)
        threshold: Similarity threshold (0-1)

    Returns:
        WebElement or None
    """
    from difflib import SequenceMatcher

    elements = driver.find_elements(By.TAG_NAME, tag)

    best_match = None
    best_ratio = 0

    for element in elements:
        element_text = element.text.strip()
        if not element_text:
            continue

        ratio = SequenceMatcher(None, text.lower(), element_text.lower()).ratio()

        if ratio > best_ratio and ratio >= threshold:
            best_ratio = ratio
            best_match = element

    if best_match:
        logger.info(f"Found fuzzy match with ratio {best_ratio}: {best_match.text}")

    return best_match
```

## Process Cleanup

### Pattern: Clean Process Shutdown
Properly cleanup Chrome/ChromeDriver processes:

```python
import psutil
import subprocess

def cleanup_existing_processes():
    """Clean up any existing Chrome/ChromeDriver processes."""
    processes_to_kill = ['chrome.exe', 'chromedriver.exe']

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in processes_to_kill:
                proc.kill()
                logger.info(f"Killed process: {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def cleanup_driver(driver):
    """Properly cleanup WebDriver instance."""
    try:
        driver.quit()
    except Exception as e:
        logger.error(f"Error during driver cleanup: {e}")
    finally:
        # Force kill if still running
        cleanup_existing_processes()
```

## JavaScript Execution

### Pattern: JavaScript Helpers
Use JavaScript for complex interactions:

```python
def scroll_to_element(driver, element):
    """Scroll element into view."""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)

def click_with_javascript(driver, element):
    """Click element using JavaScript (bypasses visibility checks)."""
    driver.execute_script("arguments[0].click();", element)

def get_element_attributes(driver, element):
    """Get all attributes of an element."""
    return driver.execute_script(
        "var items = {}; "
        "for (index = 0; index < arguments[0].attributes.length; ++index) { "
        "    items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value"
        "}; "
        "return items;",
        element
    )
```
