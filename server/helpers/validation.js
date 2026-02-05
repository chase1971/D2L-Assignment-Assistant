/**
 * Input validation helpers
 */

function validateClassName(className) {
  if (!className || typeof className !== 'string') return false;
  // Block shell metacharacters that could be used for injection
  // Note: Parentheses () are allowed since arguments are properly quoted
  return !/[;&|`${}[\]<>]/.test(className);
}

function validateDrive(drive) {
  if (!drive || typeof drive !== 'string') return false;
  // Drive should be a single letter
  return /^[A-Za-z]$/.test(drive);
}

module.exports = { validateClassName, validateDrive };
