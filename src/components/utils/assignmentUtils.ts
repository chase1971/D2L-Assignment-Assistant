/**
 * Assignment utility functions for D2L Assignment Assistant
 * Pure functions for formatting assignment names, extracting class codes, and error display
 */

/**
 * Extracts class code from class folder name
 * @param className - Full class folder name (e.g., "TTH 11-1220 FM 4202")
 * @returns Class code (e.g., "FM 4202") or empty string if not found
 * @example
 * extractClassCode("TTH 11-1220 FM 4202") // returns "FM 4202"
 */
export function extractClassCode(className: string): string {
  // Look for pattern: 2 letters, space, 4 digits at the end
  const match = className.match(/([A-Z]{2}\s+\d{4})\s*$/);
  if (match) {
    return match[1];
  }
  // Fallback: try to extract last 7 characters
  if (className.length >= 7) {
    return className.slice(-7).trim();
  }
  return '';
}

/**
 * Formats assignment display name by cleaning and adding class code
 * @param assignmentName - Raw assignment name (may include "combined PDF")
 * @param className - Full class folder name
 * @returns Formatted name: "{assignment_name} {class_code}"
 * @example
 * formatAssignmentDisplayName("Quiz 1 combined PDF", "TTH 11-1220 FM 4202")
 * // returns "Quiz 1 FM 4202"
 */
export function formatAssignmentDisplayName(assignmentName: string, className: string): string {
  // Remove "combined PDF" from the name (case insensitive)
  let cleaned = assignmentName.replace(/\s+combined\s+pdf\s*$/i, '').trim();
  
  // Extract class code
  const classCode = extractClassCode(className);
  
  // Remove class code from assignment name if it's already in there
  if (classCode) {
    const classCodePattern = new RegExp('\\s*' + classCode.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*', 'gi');
    cleaned = cleaned.replace(classCodePattern, ' ').trim();
  }
  
  // Clean up any extra spaces
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  
  // Add class code back if we have one
  if (classCode) {
    return `${cleaned} ${classCode}`;
  }
  return cleaned;
}

/**
 * Helper function to clean assignment name and format as folder name
 * @param assignmentName - Raw assignment name
 * @param className - Full class folder name
 * @returns Formatted folder name: "grade processing [CLASS_CODE] [ASSIGNMENT]"
 * @example
 * formatAssignmentFolderName("Quiz 1 combined PDF", "TTH 11-1220 FM 4202")
 * // returns "grade processing FM 4202 Quiz 1"
 */
export function formatAssignmentFolderName(assignmentName: string, className: string): string {
  if (!assignmentName) return '';
  
  // Remove "combined PDF" suffix (case insensitive)
  let cleaned = assignmentName.replace(/\s+combined\s+pdf\s*$/i, '');
  
  // Extract class code from class name (e.g., "FM 4202" from "TTH 11-1220 FM 4202")
  const classCodeMatch = className.match(/([A-Z]{2}\s+\d{4})\s*$/);
  const classCode = classCodeMatch ? classCodeMatch[1] : '';
  
  // Remove class code from assignment name if it's in there
  if (classCode) {
    const classCodeRegex = new RegExp(`\\s*${classCode.replace(/\s+/g, '\\s+')}\\s*`, 'gi');
    cleaned = cleaned.replace(classCodeRegex, ' ').trim();
  }
  
  // Clean up extra spaces
  cleaned = cleaned.replace(/\s+/g, ' ').trim();
  
  // Format as "grade processing [CLASS_CODE] [ASSIGNMENT]" or just "grade processing [ASSIGNMENT]"
  if (classCode) {
    return `grade processing ${classCode} ${cleaned}`;
  }
  return `grade processing ${cleaned}`;
}

/**
 * Helper to display error messages (removes "Error:" prefix, handles multi-line)
 * @param error - Error message string
 * @param addLog - Log callback function
 */
export function displayError(error: string | undefined, addLog: (message: string) => void): void {
  if (!error) return;
  
  // Remove "Error:" prefix if present (case insensitive)
  let cleanError = error.replace(/^Error:\s*/i, '').trim();
  
  // Remove duplicate ❌ at the start if present
  cleanError = cleanError.replace(/^❌\s*❌\s*/, '❌ ');
  
  // Split multi-line errors and display each line
  const errorLines = cleanError.split('\n');
  errorLines.forEach((line, index) => {
    const trimmed = line.trim();
    if (trimmed) {
      // Always add ❌ if line doesn't already have it
      // Skip only if it's clearly a continuation line (starts with lowercase, space, or tab)
      // or already has an emoji prefix
      const hasEmoji = /^[❌✅⚠️📂🔍📦]/.test(trimmed);
      const isContinuation = index > 0 && /^[a-z\s\t]/.test(trimmed);
      
      if (!hasEmoji && !isContinuation) {
        addLog(`❌ ${trimmed}`);
      } else {
        addLog(trimmed);
      }
    }
  });
}
