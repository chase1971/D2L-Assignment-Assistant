# Refactoring Checklist

## Quick Reference: What to Run When

| User Says | Run | Model | Why |
|-----------|-----|-------|-----|
| "Refactor", "Clean up" | **Phase 1-2** | Sonnet | Default - quick wins only |
| "Deep refactor", "Improve structure" | **Phase 1-3** | Sonnet | Add patterns/architecture |
| "Polish", "Almost done" | **Phase 1-4** | Sonnet | Add documentation |
| "Final build", "Ready to ship", "9/10" | **Phase 1-5** | Opus if needed | Ship-ready quality |
| "Check if refactoring needed" | **Phase 0** | Sonnet | Assessment only |

**DEFAULT**: If user just says "refactor" with no context → Run **Phase 1-2** with Sonnet

---

## Understanding the Phases

### Phase 0: Assessment
**Purpose**: Figure out IF refactoring is needed and what scope
**Time**: 1-2 minutes
**Model**: Sonnet
**Run**: When user asks "does this need refactoring?" or before starting any refactor

### Phase 1-2: Quick Wins (Routine Maintenance)
**Purpose**: Remove clutter, fix obvious issues
**Time**: 5-10 minutes
**Model**: Sonnet
**Run**: Every 2-3 coding sessions, or when code feels messy
**Quality**: 6-7/10 → 7/10

### Phase 3: Structure (When Things Get Messy)
**Purpose**: Split large files, extract duplicates, fix architecture
**Time**: 15-20 minutes
**Model**: Sonnet
**Run**: When files > 500 lines, or copy-paste appears 3+ times
**Quality**: 7/10 → 8/10

### Phase 4: Documentation (Feature Complete)
**Purpose**: Add docstrings, update README, document decisions
**Time**: 10-15 minutes
**Model**: Sonnet
**Run**: When feature is done, before moving to next feature
**Quality**: 8/10 → 8.5/10

### Phase 5: Final Build (Ready to Ship)
**Purpose**: Tests, env config, error boundaries, 9/10 quality
**Time**: 1-2 hours
**Model**: Sonnet first, Opus if Sonnet struggles
**Run**: **ONLY when actually preparing to ship/sell the code**
**Quality**: 8.5/10 → 9/10

---

## Phase Decision Tree

```
User says "refactor"
  ↓
Is code being actively developed?
  YES → Phase 1-2 (Quick wins only)
  NO → Continue...
    ↓
  Is feature complete but not shipping yet?
    YES → Phase 1-4 (Add docs, skip tests)
    NO → Continue...
      ↓
    Are you preparing to ship/sell this?
      YES → Phase 1-5 (Full final build)
      NO → Phase 1-2 (Quick wins only)
```

---

## When NOT to Refactor

**Skip refactoring entirely if:**
- Code was just written in current session
- Feature is still being prototyped/tested
- User is about to add more features
- Code works and isn't causing issues
- Files under 300 lines with no obvious problems

**Tell the user**: "Code looks good for current development phase. No refactoring needed right now."

---

## Phase 0: Assessment (Optional - Before Refactoring)

Run this when you're unsure if refactoring is needed.

### Questions to Answer

1. **Does this need refactoring?**
   - Are there files over 500 lines?
   - Is code duplicated 3+ times?
   - Are functions over 50 lines?
   - Are there obvious naming issues?
   - Is error handling inconsistent?

2. **What's the current development phase?**
   - Still prototyping → No refactoring needed
   - Feature in progress → Phase 1-2 at most
   - Feature complete → Phase 1-4
   - Preparing to ship → Phase 1-5

3. **What's the scope?**
   - Which files need changes?
   - Which files should NOT be touched?
   - What are the risks?

### Output Format

```markdown
## Refactoring Assessment

**Current Quality**: X/10
**Recommendation**: Run Phase 1-X
**Reason**: [Brief explanation]

**Issues Found**:
- [List specific issues if any]

**Scope**:
- Files to touch: [list]
- Files to preserve: [list]
- Estimated time: X minutes
```

If no issues found:
```markdown
## Refactoring Assessment

**Current Quality**: 7/10
**Recommendation**: No refactoring needed
**Reason**: Code is clean for current development phase
```

---

## Phase 1: Dead Code & Quick Fixes (5 minutes)

**Always run this phase** - it's fast and always helps.

### Dead Code Removal
- [ ] Delete unused imports
- [ ] Delete unused functions
- [ ] Delete unused variables
- [ ] Delete commented-out code (git has history)
- [ ] Delete empty files

### Secrets Check (CRITICAL)
- [ ] No API keys hardcoded in source files
- [ ] No passwords or tokens in code
- [ ] No connection strings with credentials
- [ ] Secrets use environment variables or config files
- [ ] `.gitignore` includes `.env`, `*.pem`, `credentials.json`

### Magic Numbers → Constants
```python
# Before
if len(items) > 100:
    time.sleep(0.5)

# After
MAX_ITEMS = 100
RATE_LIMIT_DELAY = 0.5

if len(items) > MAX_ITEMS:
    time.sleep(RATE_LIMIT_DELAY)
```

### Stop After Phase 1 If:
- Code is actively being developed
- User is prototyping/testing
- Files are under 300 lines
- No obvious structural issues

---

## Phase 2: Naming & Consistency (5 minutes)

### Naming Improvements
- [ ] Rename vague variables (`x`, `data`, `temp`, `result`)
- [ ] Rename functions that don't describe what they do
- [ ] Fix inconsistent naming (mixing `camelCase` and `snake_case`)

### Error Handling Consistency
- [ ] Fix mixed try/except styles (make consistent across module)
- [ ] Replace bare `except:` with specific exceptions
- [ ] Ensure error messages include context (not just "Error")

```python
# Before
try:
    result = process()
except:
    print("Error")

# After
try:
    result = process()
except ValueError as e:
    print(f"Failed to process data: {e}")
    return None
```

### Stop After Phase 2 If:
- This is routine maintenance
- User didn't ask for deep refactoring
- Code is under 400 lines per file
- No obvious duplication

---

## Phase 3: Structure & Architecture (15 minutes)

**Only run if user asks for "deep refactor" or you see structural issues.**

### Split Large Files

For each file over 500 lines:
- [ ] Can constants be extracted to `*_constants.py`?
- [ ] Can state management be extracted to `*_state.py`?
- [ ] Can helper functions be extracted to `*_helpers.py`?
- [ ] Can the file be split by responsibility?

**Target**: 200-400 lines per file. **Max**: 800 lines.

### Extract Duplicates

Look for:
- [ ] Same code block appearing 3+ times → Extract to function
- [ ] Similar code with small variations → Extract with parameters
- [ ] Same pattern across files → Extract to shared module

**Rule**: Only extract if it appears 3+ times. Don't prematurely abstract.

### Simplify Functions

For each function over 50 lines:
- [ ] Can it be split into smaller functions?
- [ ] Are there deeply nested blocks that could use guard clauses?
- [ ] Is there a loop that could be its own function?

```python
# Before - deeply nested
def process(data):
    if data:
        if data.is_valid:
            if data.has_items:
                # actual logic buried here
                return result
    return None

# After - guard clauses
def process(data):
    if not data:
        return None
    if not data.is_valid:
        return None
    if not data.has_items:
        return None

    # actual logic at top level
    return result
```

### Parameter Reduction

For functions with 5+ parameters:
```python
# Before
def create_window(x, y, width, height, title, color, alpha, topmost):
    ...

# After
from dataclasses import dataclass

@dataclass
class WindowConfig:
    x: int
    y: int
    width: int
    height: int
    title: str = "Window"
    color: str = "#333333"
    alpha: float = 1.0
    topmost: bool = True

def create_window(config: WindowConfig):
    ...
```

### Check Against Patterns

- [ ] Is there a pattern in `cursor-patterns/` that should be used?
- [ ] Is the code doing something a pattern already solves?
- [ ] Should this code become a new pattern?

### Stop After Phase 3 If:
- User didn't ask for documentation
- Feature isn't complete yet
- This is just structural cleanup

---

## Phase 4: Documentation (10 minutes)

**Only run when feature is complete.**

### Add Docstrings to Public Functions

```python
def process_items(
    items: List[str],
    count: int = 10,
    options: Optional[Dict[str, Any]] = None
) -> Tuple[bool, str]:
    """
    Process items and return success status with message.

    Args:
        items: List of item names to process
        count: Maximum number of items to process (default: 10)
        options: Optional configuration dict

    Returns:
        Tuple of (success, message)

    Example:
        >>> success, msg = process_items(["a", "b"], count=5)
        >>> print(msg)
        "Processed 2 items"
    """
    ...
```

### Add JSDoc to TypeScript Functions

```typescript
/**
 * Process quiz submissions for a class.
 *
 * @param drive - Drive letter (e.g., 'C')
 * @param className - Class folder name
 * @param addLog - Callback to display progress
 * @returns Promise with success status
 *
 * @example
 * const result = await processQuizzes('C', 'MW 11-1220', console.log);
 */
export const processQuizzes = (
  drive: string,
  className: string,
  addLog: LogCallback
): Promise<ApiResult> => { ... }
```

### Comment Complex Logic

Only comment the "why", not the "what":
```python
# BAD - obvious from code
# Loop through items
for item in items:
    process(item)

# GOOD - explains non-obvious decision
# Process in chunks to avoid memory issues with large datasets
for chunk in chunks(items, size=100):
    process(chunk)
```

### Update README

If there's a README, check:
- [ ] Installation instructions are accurate
- [ ] Basic usage examples are current
- [ ] Breaking changes are documented

### Stop After Phase 4 If:
- Not preparing to ship/sell
- Tests aren't needed yet
- Environment config isn't required

---

## Phase 5: Final Build (1-2 hours)

**ONLY run when user explicitly says "ready to ship", "final build", or "make it 9/10".**

This phase is expensive and only needed when preparing to sell/ship code.

---

### 5.1: Testing

#### Identify What Needs Tests

- [ ] List all complex functions with multiple branches
- [ ] List all public API functions other modules call
- [ ] List any edge cases discovered during development
- [ ] List any bugs that were fixed (each needs a regression test)

**Priority testing targets:**
- Name matching / fuzzy matching logic
- Data parsing (CSV, JSON, file formats)
- Grade calculation / scoring logic
- File path resolution across platforms
- Any function with 3+ if/else branches

#### Write Minimum Tests

For each complex function:
- [ ] Test the happy path (normal input → expected output)
- [ ] Test edge cases (empty input, null, boundary values)
- [ ] Test error cases (invalid input → graceful failure)

```python
# Example: Name matching function
def test_match_exact_name():
    assert match("John Smith", roster) == "jsmith123"

def test_match_hyphenated_name():
    assert match("John-Paul Smith", roster) == "jpsmith456"

def test_no_match_returns_none():
    assert match("Unknown Person", roster) is None

def test_empty_roster_returns_none():
    assert match("John Smith", empty_roster) is None
```

#### Verify Tests Pass
- [ ] All new tests pass
- [ ] All existing tests still pass
- [ ] No tests are skipped or commented out

---

### 5.2: Environment Configuration

#### Find Hardcoded Values

Search for:
- [ ] `localhost:` URLs
- [ ] Absolute file paths (`C:\`, `/Users/`)
- [ ] API keys or tokens (should already be gone)
- [ ] Port numbers

#### Extract to Config

```python
# Before
API_URL = "http://localhost:5000"
ROSTERS_PATH = "C:\\Rosters etc"

# After
import os
API_URL = os.environ.get("API_URL", "http://localhost:5000")
ROSTERS_PATH = os.environ.get("ROSTERS_PATH", "C:\\Rosters etc")
```

```typescript
// Before
const API_BASE_URL = 'http://localhost:5000/api';

// After
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
```

#### Create Environment Files
- [ ] Create `.env.example` (committed) with all required variables
- [ ] Ensure `.env` is in `.gitignore`
- [ ] Document required environment variables in README

---

### 5.3: State Management (React)

**Only if component > 300 lines**

#### Check Component Size

For each component over 300 lines:
- [ ] Count useState/useReducer calls
- [ ] If > 5 state variables, extract to custom hook

#### Extract State to Hook

```tsx
// Before: Option2.tsx has 15 useState calls and 500+ lines

// After: Create useQuizProcessor.ts
export function useQuizProcessor() {
  const [state, dispatch] = useReducer(quizReducer, initialState);

  const processQuizzes = async () => {
    dispatch({ type: 'START_PROCESSING' });
    // ... logic
  };

  return {
    ...state,
    processQuizzes,
    // ... other actions
  };
}

// Option2.tsx now just renders UI
function Option2() {
  const { state, actions } = useQuizProcessor();
  return (/* UI only */);
}
```

---

### 5.4: CLI Function Refactoring (Python)

**Only if main() > 100 lines**

#### Extract to Testable Functions

```python
# Before: main() does everything (300+ lines)
def main():
    # Parse args, find files, process, write output...
    pass

# After: main() orchestrates, functions do work
def find_pdf_files(folder: str) -> List[Path]:
    """Find all PDF files in folder."""
    ...

def extract_grade_from_pdf(pdf_path: Path) -> Optional[GradeResult]:
    """Extract grade from a single PDF."""
    ...

def main():
    args = parse_args()
    pdfs = find_pdf_files(args.folder)
    grades = [extract_grade_from_pdf(p) for p in pdfs]
    write_output(grades, args.output)
```

---

### 5.5: Error Handling

#### Add Error Boundaries (React)

```tsx
// components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong. Please reload.</div>;
    }
    return this.props.children;
  }
}

// App.tsx
export default function App() {
  return (
    <ErrorBoundary>
      <YourApp />
    </ErrorBoundary>
  );
}
```

#### Improve Error Messages

```python
# Bad
return {"error": "Failed"}

# Good
return {"error": "Could not find class folder. Check that the class name matches a folder in Rosters etc."}
```

---

### 5.6: API Consistency

#### Centralize All API Calls

- [ ] Search for direct `fetch()` calls outside service layer
- [ ] Move all API calls to service file
- [ ] Ensure all calls use the `apiCall()` helper

```typescript
// Before: Direct fetch in component
const response = await fetch('/api/process', {
  method: 'POST',
  body: JSON.stringify({ data })
});

// After: Service layer
export const processData = (data: any): Promise<ApiResult> =>
  apiCall({
    endpoint: '/process',
    body: { data },
    logMessage: 'Processing data...',
    errorMessage: 'Failed to process data'
  });
```

#### Verify Response Shape
- [ ] All endpoints return `{ success, error?, data? }`
- [ ] All error responses include helpful message
- [ ] All success responses include relevant data

---

### 5.7: Final Verification

#### Run Full Test Suite
```bash
# Python
pytest

# JavaScript/TypeScript
npm test
```

#### Manual Smoke Test
- [ ] App starts without errors
- [ ] Main workflow completes successfully
- [ ] Error cases show helpful messages
- [ ] No console errors in browser

#### Code Quality Check
- [ ] No TypeScript/ESLint errors
- [ ] No Python linting errors
- [ ] No unused imports or variables

---

## Refactoring Report Templates

### After Phase 1-2 (Quick Wins)

```markdown
## Quick Refactoring Complete

**Changes Made**:
- Removed X unused imports/functions
- Extracted Y magic numbers to constants
- Fixed Z naming issues

**Quality**: 6/10 → 7/10

**Next Steps**: None needed unless adding significant new features
```

### After Phase 1-3 (Structure)

```markdown
## Structural Refactoring Complete

**Changes Made**:
- Split X large files
- Extracted Y duplicate code blocks
- Simplified Z complex functions

**Code Metrics**:
- Files over 500 lines: X → Y
- Functions over 50 lines: X → Y
- Duplicate blocks: X → 0

**Quality**: 7/10 → 8/10

**Next Steps**: Add documentation when feature is complete
```

### After Phase 1-4 (Documentation)

```markdown
## Documentation Refactoring Complete

**Changes Made**:
- Added docstrings to X functions
- Updated README with Y sections
- Documented Z non-obvious decisions

**Quality**: 8/10 → 8.5/10

**Next Steps**: Ready for continued development. Run Phase 5 when preparing to ship.
```

### After Phase 1-5 (Final Build)

```markdown
## Final Build Complete - 9/10 Quality

### Tests Added
- `test_module.py` - X tests for core logic
- `service.test.ts` - Y tests for API layer

### Environment Configuration
- Extracted X hardcoded values to environment variables
- Created `.env.example` with Y variables

### State Management
- Extracted state from ComponentName to useHookName
- Reduced component from X lines to Y lines

### Documentation
- Docstrings on X functions
- JSDoc on Y service functions
- Updated README with setup instructions

### Error Handling
- Added ErrorBoundary component
- Improved X error messages with context

### API Consistency
- Moved X inline fetch calls to service layer
- All Y endpoints use consistent response shape

**Quality**: 8.5/10 → 9/10

**Status**: Ready to ship/sell
```

---

## Common Mistakes to Avoid

### ❌ Running Phase 5 on work-in-progress code
**Why it's bad**: Wastes time on tests/docs that will change
**Do instead**: Only run Phase 5 when actually shipping

### ❌ Refactoring code just written in current session
**Why it's bad**: Code hasn't had time to reveal its problems
**Do instead**: Let it sit for a session, then refactor

### ❌ Extracting patterns after seeing them once or twice
**Why it's bad**: Premature abstraction, pattern might not be real
**Do instead**: Wait until 3rd occurrence, then extract

### ❌ Splitting files that are under 400 lines
**Why it's bad**: Creates unnecessary complexity
**Do instead**: Only split files over 500 lines

### ❌ Using Opus for routine Phase 1-4 refactoring
**Why it's bad**: Wastes expensive token budget
**Do instead**: Use Sonnet for all refactoring, only use Opus for Phase 5 if Sonnet struggles

---

## Model Usage Guidelines

**Use Sonnet (Auto mode) for:**
- Phase 0: Assessment
- Phase 1-2: Quick wins
- Phase 3: Structure
- Phase 4: Documentation
- Phase 5: First attempt at final build

**Use Opus only when:**
- Phase 5 (final build) AND Sonnet failed/struggled
- Complex architectural decisions during Phase 5
- Test writing for very complex logic
- Sonnet produced incorrect refactoring

**Never use Opus for:**
- Phase 1-2 (quick wins) - complete waste
- Routine code cleanup
- Simple file splits
- Naming improvements

---

## Summary

**Default behavior**: User says "refactor" → Run Phase 1-2 with Sonnet

**Escalate to Phase 3-4**: Only if user asks for deeper refactoring or you see structural issues

**Run Phase 5**: ONLY when user explicitly says "ready to ship" or "final build"

**Model choice**: Sonnet for everything, Opus only for Phase 5 if needed

**Quality targets**:
- Rough draft: 6-7/10 (Phase 1-2)
- Feature complete: 7-8/10 (Phase 1-4)
- Ready to ship: 9/10 (Phase 1-5)
