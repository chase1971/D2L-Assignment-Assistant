/**
 * Log parsing helpers for Python script output
 */

const path = require('path');
const os = require('os');

// Helper to extract user logs from result
function getUserLogs(result) {
  if (result.userLogs && result.userLogs.length > 0) {
    // New format: array of {level, message} objects
    return result.userLogs;
  }

  // Fallback: check for logs array in JSON data (legacy format)
  if (result.data && result.data.logs && result.data.logs.length > 0) {
    return result.data.logs.map(msg => ({ level: 'INFO', message: msg }));
  }

  // Legacy: parse output
  return result.output.split('\n')
    .filter(l => l.trim() && !l.trim().startsWith('[DEV]') && !l.trim().startsWith('{'))
    .map(l => {
      const trimmed = l.trim();
      const logMatch = trimmed.match(/^\[LOG:(SUCCESS|ERROR|WARNING|INFO)\] (.+)$/);
      if (logMatch) {
        return { level: logMatch[1], message: logMatch[2] };
      }
      if (trimmed.startsWith('[USER]')) {
        return { level: 'INFO', message: trimmed.substring(7) };
      }
      return { level: 'INFO', message: trimmed };
    });
}

// Parse ZIP files from Python script output
function parseZipFilesFromOutput(output, downloadsPath) {
  const outputLines = output.split('\n');

  // Try to parse JSON response first
  for (const line of outputLines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('{') && trimmed.includes('zip_files')) {
      try {
        const jsonResult = JSON.parse(trimmed);
        if (jsonResult.zip_files && jsonResult.zip_files.length > 0) {
          return {
            found: true,
            zipFiles: jsonResult.zip_files,
            logs: jsonResult.logs || []
          };
        }
      } catch (parseErr) {
        // Could not parse JSON line
      }
    }
  }

  // Fallback: Check for multiple ZIP files in text output
  if (output.includes('Multiple ZIP files found')) {
    const zipFiles = [];
    outputLines.forEach((line) => {
      const match = line.match(/^\s*(\d+)\.\s+(.+\.zip)$/i);
      if (match) {
        zipFiles.push({
          index: parseInt(match[1]),
          filename: match[2],
          path: path.join(downloadsPath || path.join(os.homedir(), 'Downloads'), match[2])
        });
      }
    });

    if (zipFiles.length > 0) {
      return { found: true, zipFiles, logs: [] };
    }
  }

  return { found: false };
}

module.exports = { getUserLogs, parseZipFilesFromOutput };
