# Remove Drive Detection - Configuration Guide

> **For New Users:** This guide explains how to remove the C:/G: drive detection logic and configure the system for your own folder structure.

---

## 🎯 What This Guide Does

The current system has hard-coded logic that switches between:
- **C: drive:** `C:\Users\chase\My Drive\Rosters etc\`
- **G: drive:** Multiple path variations for network drive

**This is specific to the original developer's setup and won't work for you.**

This guide shows you how to:
1. Remove the drive detection logic
2. Use a single configurable base path
3. Make it work with YOUR folder structure

---

## 🚨 Why This Matters

If you don't make this change, the system will:
- Try to find folders on C: or G: drive that don't exist on your system
- Fail with path errors
- Not work at all

**Estimated time to fix: 5 minutes**

---

## 📍 Files That Need Changing

You need to modify **2 files:**

1. **`common.py`** - Path resolution functions
2. **`grading_processor.py`** - Drive path lookup

---

## 🔧 Step-by-Step Instructions

### Step 1: Choose Your Configuration Method

**Option A: Environment Variable (Recommended)**
- Flexible, easy to change
- No code modification after initial setup
- Best for multiple users

**Option B: Config File**
- Simple JSON file
- Easy to edit
- Good for single user

**Option C: Hard-coded Path**
- Simplest to implement
- Requires code change to modify
- Fine for personal use

---

### Step 2: Modify `common.py`

**Location:** Line ~15-50 (look for `get_rosters_path` and `get_drive_path` functions)

#### CURRENT CODE (Remove This):

```python
def get_rosters_path(drive_letter):
    """Get rosters path based on drive letter (C or G)."""
    if drive_letter.upper() == 'C':
        return r"C:\Users\chase\My Drive\Rosters etc"
    elif drive_letter.upper() == 'G':
        # Try multiple G: drive variations
        possible_paths = [
            r"G:\Users\chase\My Drive\Rosters etc",
            r"G:\chase\My Drive\Rosters etc",
            r"G:\My Drive\Rosters etc"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return possible_paths[0]  # Return first if none exist
    else:
        raise ValueError(f"Invalid drive letter: {drive_letter}")

def get_drive_path(drive_letter, class_name):
    """Get full path to class folder."""
    rosters_path = get_rosters_path(drive_letter)
    return os.path.join(rosters_path, class_name)
```

#### NEW CODE - Option A (Environment Variable):

```python
def get_rosters_path():
    """Get rosters base path from environment variable."""
    base_path = os.getenv("ROSTERS_BASE_PATH")
    
    if not base_path:
        raise ValueError(
            "ROSTERS_BASE_PATH not set in environment.\n"
            "Add to your .env file:\n"
            "ROSTERS_BASE_PATH=C:\\path\\to\\your\\rosters\\folder"
        )
    
    if not os.path.exists(base_path):
        raise ValueError(f"Rosters base path does not exist: {base_path}")
    
    return base_path

def get_class_folder_path(class_name):
    """Get full path to class folder."""
    rosters_path = get_rosters_path()
    return os.path.join(rosters_path, class_name)
```

**Then update your `.env` file:**
```
GOOGLE_VISION_API_KEY=your_api_key_here
ROSTERS_BASE_PATH=C:\path\to\your\rosters\folder
```

#### NEW CODE - Option B (Config File):

```python
import json

def get_rosters_path():
    """Get rosters base path from config file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    if not os.path.exists(config_path):
        raise ValueError(
            "config.json not found. Create it with:\n"
            '{"rosters_base_path": "C:\\\\path\\\\to\\\\your\\\\rosters"}'
        )
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    base_path = config.get('rosters_base_path')
    if not base_path:
        raise ValueError("rosters_base_path not found in config.json")
    
    if not os.path.exists(base_path):
        raise ValueError(f"Rosters base path does not exist: {base_path}")
    
    return base_path

def get_class_folder_path(class_name):
    """Get full path to class folder."""
    rosters_path = get_rosters_path()
    return os.path.join(rosters_path, class_name)
```

**Then create `config.json`:**
```json
{
  "rosters_base_path": "C:\\Users\\YourName\\Documents\\Rosters"
}
```

#### NEW CODE - Option C (Hard-coded):

```python
def get_rosters_path():
    """Get rosters base path."""
    # CHANGE THIS PATH TO YOUR OWN:
    base_path = r"C:\Users\YourName\Documents\Rosters"
    
    if not os.path.exists(base_path):
        raise ValueError(f"Rosters base path does not exist: {base_path}")
    
    return base_path

def get_class_folder_path(class_name):
    """Get full path to class folder."""
    rosters_path = get_rosters_path()
    return os.path.join(rosters_path, class_name)
```

---

### Step 3: Update All Function Calls in `common.py`

**Find and replace throughout `common.py`:**

**OLD:**
```python
rosters_path = get_rosters_path(drive)
class_folder = get_drive_path(drive, class_name)
```

**NEW:**
```python
rosters_path = get_rosters_path()
class_folder = get_class_folder_path(class_name)
```

---

### Step 4: Modify `grading_processor.py`

**Location:** Line ~50-80 (look for `get_drive_path` function)

#### REMOVE THIS FUNCTION:

```python
def get_drive_path(drive_letter, class_name):
    """Get the rosters path based on drive letter."""
    # ... drive detection logic ...
```

#### ADD THIS FUNCTION:

```python
def get_class_folder_path(class_name):
    """Get full path to class folder."""
    from common import get_rosters_path
    rosters_path = get_rosters_path()
    return os.path.join(rosters_path, class_name)
```

---

### Step 5: Update Function Calls in `grading_processor.py`

**Find all occurrences of:**
```python
get_drive_path(drive, class_name)
```

**Replace with:**
```python
get_class_folder_path(class_name)
```

**Use Find & Replace:**
- Search: `get_drive_path\(drive,\s*class_name\)`
- Replace: `get_class_folder_path(class_name)`

---

### Step 6: Update CLI Scripts

The CLI scripts currently accept a `drive` parameter. You have two options:

**Option A: Remove drive parameter entirely**

**OLD:**
```python
python process_quiz_cli.py C "ClassName" "file.zip"
```

**NEW:**
```python
python process_quiz_cli.py "ClassName" "file.zip"
```

**Option B: Keep drive parameter for backwards compatibility**

Just ignore the drive parameter in the scripts:

```python
def main():
    # Parse arguments
    if len(sys.argv) < 3:
        # ...
    
    drive = sys.argv[1]  # Keep for compatibility, but ignore it
    class_name = sys.argv[2]
    # ... rest stays the same
```

---

## ✅ Testing Your Changes

After making changes, test with:

```bash
# 1. Verify path resolution
python -c "from common import get_rosters_path; print(get_rosters_path())"

# 2. Test with actual class
python process_quiz_cli.py "TestClass" "path/to/test.zip"
```

---

## 📋 Checklist

Before you're done, make sure:

- [ ] Modified `get_rosters_path()` in `common.py`
- [ ] Modified `get_class_folder_path()` in `common.py`  
- [ ] Updated all calls to `get_drive_path()` in `common.py`
- [ ] Removed/updated `get_drive_path()` in `grading_processor.py`
- [ ] Updated all calls to `get_drive_path()` in `grading_processor.py`
- [ ] Set up `.env` file (Option A) OR `config.json` (Option B)
- [ ] Tested path resolution
- [ ] Tested with sample data
- [ ] Updated file headers with today's date

---

## 🐛 Troubleshooting

### "ROSTERS_BASE_PATH not set"
- Add to `.env` file: `ROSTERS_BASE_PATH=your_path_here`
- Use double backslashes: `C:\\Users\\...`

### "Path does not exist"
- Check your path is correct
- Use full absolute path
- Windows: Use raw string `r"C:\..."` or double backslashes

### "Invalid drive letter" error
- You didn't update all the function calls
- Search for remaining `get_drive_path(drive, ...)` calls

---

## 💡 Recommended Approach

**For most users, I recommend Option A (Environment Variable):**

1. Add to `.env`:
   ```
   ROSTERS_BASE_PATH=C:\your\path\here
   ```

2. Modify `common.py` as shown in Option A

3. Update `grading_processor.py`

4. Test thoroughly

**Advantages:**
- Easy to change without code modification
- Keeps sensitive paths out of code
- Works with existing `.env` setup
- Most flexible

---

## 📝 After Completing Changes

1. **Update SESSIONS.md** with what you changed
2. **Update file headers** in `common.py` and `grading_processor.py`
3. **Test all CLI scripts** to make sure they work
4. **Delete this file** if you want (you're done with it!)

---

**Time to complete:** 5-10 minutes
**Difficulty:** Easy
**Impact:** Required for system to work on your computer

---

**Need Help?**

If you get stuck:
1. Check the file headers in `common.py` and `grading_processor.py`
2. Review error messages carefully
3. Test path resolution separately first
4. Make sure `.env` file is in the project root

**Last Updated:** 2026-02-05
