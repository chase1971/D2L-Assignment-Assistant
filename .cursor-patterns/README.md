# Cursor Patterns Directory

This directory contains comprehensive coding patterns and best practices for the D2L Assignment Assistant project. These patterns are automatically read by Cursor AI when working on this project.

## Purpose

The pattern files in this directory serve as:
- **Reference documentation** for common coding scenarios
- **Style guides** for consistent code quality
- **Best practices** learned from this project
- **Quick examples** for common tasks

## Pattern Files

### 1. refactoring-checklist.md
**Phased approach to refactoring code**

Topics covered:
- Phase 0-5 refactoring workflow
- When to run each phase (quick wins vs deep refactoring vs final build)
- Model usage guidelines (Sonnet vs Opus)
- Quality targets (6/10 → 9/10)
- Dead code removal and secrets check
- File splitting and duplicate extraction
- Testing and environment configuration
- Common refactoring mistakes to avoid

**When to consult:**
- User asks to "refactor" or "clean up" code
- Deciding what level of refactoring to apply
- Determining if code needs refactoring at all
- Planning refactoring scope and timeline

### 2. d2l-automation.md
**Core automation patterns for D2L interaction**

Topics covered:
- Async browser context management with Playwright
- Element selection strategies with fallbacks
- Date processing and input handling
- CSV data processing patterns
- Comprehensive logging and debugging
- Error handling and retry logic
- Session management strategies
- GUI design patterns with Tkinter

**When to consult:**
- Implementing new D2L automation features
- Working with date/time processing
- Adding logging or debugging functionality
- Designing error recovery strategies

### 3. selenium-patterns.md
**Selenium WebDriver specific patterns**

Topics covered:
- Driver setup with persistent Chrome profiles
- Safe element interaction with retry logic
- Iframe switching and handling
- Input field and checkbox management
- Custom wait conditions
- Fuzzy text matching for elements
- Process cleanup and resource management
- JavaScript execution helpers

**When to consult:**
- Working with Selenium WebDriver code
- Debugging element selection issues
- Implementing waits and timeouts
- Managing browser sessions

### 4. code-style.md
**General coding standards and best practices**

Topics covered:
- Python style guidelines (PEP 8 compliance)
- Naming conventions for classes, functions, variables
- Google-style docstring format
- Import organization
- Exception handling patterns
- Logging best practices
- Function design principles
- Testing patterns
- Configuration management

**When to consult:**
- Starting any new code
- Refactoring existing code
- Writing tests
- Documenting code

## How Cursor Uses These Patterns

### Automatic Reading
When you open this project in Cursor, it will:
1. Read the `.cursorrules` file in the project root
2. Be directed to these pattern files for specific scenarios
3. Apply these patterns when suggesting code or making changes

### Pattern Priority
The patterns are consulted in this order:
1. **Project-specific patterns** (d2l-automation.md, selenium-patterns.md)
2. **General style guidelines** (code-style.md)
3. **Existing code patterns** in the project
4. **Standard Python conventions**

## Using These Patterns

### For Developers

When working on this project:
1. **Before implementing** - Check if a pattern exists for your scenario
2. **During implementation** - Follow the pattern examples
3. **After implementation** - Verify your code matches the patterns
4. **Found a better way?** - Update the pattern file

### For AI Assistants (Cursor)

When assisting with this project:
1. **Always reference these patterns first** before suggesting code
2. **Maintain consistency** with established patterns
3. **Cite specific patterns** when making suggestions
4. **Suggest pattern updates** when introducing better approaches

## Pattern File Format

Each pattern file follows this structure:

```markdown
# Title

## Category Name

### Pattern: Descriptive Name
Explanation of when and why to use this pattern.

```python
# Code example demonstrating the pattern
```

**When to use:**
- Specific scenario 1
- Specific scenario 2

**Avoid:**
- Anti-pattern 1
- Anti-pattern 2
```

## Updating Patterns

### When to Add New Patterns
- You've solved a complex problem that others might face
- You've found a better way to handle an existing scenario
- You've encountered and solved a common bug
- You've implemented a reusable solution

### How to Update
1. Identify the appropriate pattern file
2. Add your pattern under a relevant category (or create new category)
3. Include clear examples and explanations
4. Update this README if adding a new file

### Pattern Quality Guidelines
Good patterns should be:
- **Specific**: Address a concrete scenario
- **Clear**: Easy to understand and apply
- **Complete**: Include full, working examples
- **Justified**: Explain why this approach is preferred

## Examples of Good Patterns

### ✅ Good Pattern Example
```markdown
### Pattern: Retry Logic for Flaky Operations
When dealing with unreliable network or UI operations, implement exponential backoff retry logic.

```python
async def retry_operation(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
```

**When to use:**
- Network requests that may fail temporarily
- UI element interactions that may not be immediately available
- Any operation that could fail due to timing issues

**Avoid:**
- Using for operations that should never fail
- Using without a maximum retry limit
```

### ❌ Poor Pattern Example
```markdown
### Pattern: Error Handling
Always handle errors.

```python
try:
    do_something()
except:
    pass
```
```

*Why it's poor: Too vague, shows bad practice (bare except), no context*

## Integration with .cursorrules

The `.cursorrules` file in the project root:
- References these pattern files
- Provides project context
- Directs Cursor to consult specific patterns for specific tasks
- Establishes project-wide coding standards

Together, `.cursorrules` and `.cursor-patterns/` create a comprehensive guide for maintaining code quality and consistency.

## Benefits

Following these patterns provides:
- **Consistency**: All code follows similar patterns
- **Quality**: Proven solutions to common problems
- **Speed**: Less time deciding how to implement features
- **Maintainability**: Code is predictable and well-documented
- **Learning**: New team members can quickly understand conventions

## Resources

- **Project Documentation**: `../PROJECT_STRUCTURE.md`
- **Cursor Rules**: `../.cursorrules`
- **Python Style Guide**: [PEP 8](https://pep8.org/)
- **Selenium Documentation**: [selenium.dev](https://www.selenium.dev/documentation/)
- **Playwright Documentation**: [playwright.dev](https://playwright.dev/python/)

---

**Remember**: These patterns are living documents. As the project evolves and you discover better approaches, update these files to reflect current best practices.
