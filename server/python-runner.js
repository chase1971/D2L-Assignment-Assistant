/**
 * Python script execution helpers
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

const { SCRIPTS_PATH } = require('./config');
const patchManager = require('../patch-manager');
const sseLogger = require('../sse-logger');

// Constants
const MAX_BUFFER_SIZE = 10 * 1024 * 1024; // 10MB buffer for Python script output

// Logging
function writeLog(message, isError = false) {
  const timestamp = new Date().toISOString();
  const prefix = isError ? '[ERROR]' : '[INFO]';
  console.log(`${timestamp} ${prefix} ${message}`);
}

// Find Python executable
// In packaged app, checks for bundled Python first, then system Python
async function findPython() {
  const possiblePaths = [];

  // First, check for bundled Python (in packaged app)
  if (process.resourcesPath) {
    // Check for portable Python in resources
    const bundledPaths = [
      path.join(process.resourcesPath, 'python', 'python.exe'),
      path.join(process.resourcesPath, 'python', 'pythonw.exe'),
      path.join(process.resourcesPath, '..', 'python', 'python.exe'),
      path.join(process.resourcesPath, '..', 'python', 'pythonw.exe'),
      // Also check in app directory (for portable installs)
      path.join(process.resourcesPath, '..', '..', 'python', 'python.exe'),
      path.join(process.resourcesPath, '..', '..', 'python', 'pythonw.exe'),
    ];
    possiblePaths.push(...bundledPaths);
  }

  // Also check in app directory relative to project root (for development/portable)
  const appDir = path.join(__dirname, '..');
  const appPythonPaths = [
    path.join(appDir, 'python', 'python.exe'),
    path.join(appDir, 'python', 'pythonw.exe'),
    path.join(path.dirname(appDir), 'python', 'python.exe'),
    path.join(path.dirname(appDir), 'python', 'pythonw.exe'),
  ];
  possiblePaths.push(...appPythonPaths);

  // Then check system Python installations
  const systemPaths = [
    'python',
    'python3',
    'C:\\Python311\\python.exe',
    'C:\\Python310\\python.exe',
    'C:\\Python39\\python.exe',
    path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'Python', 'Python311', 'python.exe'),
    path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'Python', 'Python310', 'python.exe'),
    path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'Python', 'Python39', 'python.exe'),
  ];
  possiblePaths.push(...systemPaths);

  for (const pythonPath of possiblePaths) {
    try {
      const result = await new Promise((resolve) => {
        const proc = spawn(pythonPath, ['--version'], { shell: true });
        proc.on('close', (code) => resolve(code === 0));
        proc.on('error', () => resolve(false));
        proc.stdout.on('data', () => {}); // Consume output
        proc.stderr.on('data', () => {}); // Consume errors
        // Timeout after 5 seconds
        setTimeout(() => resolve(false), 5000);
      });
      if (result) {
        writeLog(`Found Python at: ${pythonPath}`);
        return pythonPath;
      }
    } catch {
      continue;
    }
  }

  throw new Error('Python not found. Please install Python 3.9+ and add to PATH, or ensure bundled Python is included in the installer.');
}

// Helper to run Python scripts
async function runPythonScript(scriptName, args = []) {
  const pythonPath = await findPython();

  // Check for patched version first
  const scriptInfo = patchManager.getScriptPath(SCRIPTS_PATH, scriptName);
  const scriptPath = scriptInfo.path;

  // Get appropriate working directory (patch dir if patches exist)
  const workingDir = patchManager.getWorkingDirectory(SCRIPTS_PATH);

  if (scriptInfo.isPatched) {
    writeLog(`🔧 Using PATCHED script: ${scriptName}`);
  }

  writeLog(`Running: ${scriptName} ${args.join(' ')}`);
  writeLog(`Full path: ${scriptPath}`);

  return new Promise((resolve, reject) => {
    // Quote paths and arguments to handle spaces properly
    const quotedPythonPath = `"${pythonPath}"`;
    const quotedScriptPath = `"${scriptPath}"`;
    const quotedArgs = args.map(arg => {
      // If arg already contains quotes or spaces, ensure it's properly quoted
      if (arg.includes(' ') || arg.includes('"')) {
        return `"${arg.replace(/"/g, '\\"')}"`;
      }
      return arg;
    }).join(' ');

    // Construct command string for Windows shell with -u flag for unbuffered output
    const command = `${quotedPythonPath} -u ${quotedScriptPath} ${quotedArgs}`;

    const proc = exec(command, {
      cwd: workingDir,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
      maxBuffer: MAX_BUFFER_SIZE
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
      // Parse [USER] and [DEV] prefixes and route accordingly
      data.toString().split('\n').filter(l => l.trim()).forEach(line => {
        const trimmed = line.trim();

        // Broadcast to SSE clients in real-time
        sseLogger.parseAndBroadcastLogLine(trimmed);

        if (trimmed.startsWith('[USER]')) {
          // User-facing log - strip prefix and log normally
          const userMessage = trimmed.substring(7); // Remove '[USER]' prefix
          writeLog(`[Python] ${userMessage}`);
        } else if (trimmed.startsWith('[DEV]')) {
          // Developer log - only log in debug mode
          const devMessage = trimmed.substring(6); // Remove '[DEV]' prefix
          writeLog(`[Python Debug] ${devMessage}`);
        } else {
          // Legacy format (no prefix) - treat as user log for backward compatibility
          writeLog(`[Python] ${trimmed}`);
        }
      });
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
      const errorText = data.toString().trim();

      // Filter out harmless pypdf warnings that clutter the logs
      const pypdfWarnings = [
        'Object 0 0 not defined',
        'Overwriting cache for 0 0',
        'Object.*not defined',
        'Overwriting cache for'
      ];

      const isPypdfWarning = pypdfWarnings.some(pattern => {
        const regex = new RegExp(pattern.replace(/\.\*/g, '.*'), 'i');
        return regex.test(errorText);
      });

      // Only log if it's not a harmless pypdf warning
      if (!isPypdfWarning && errorText) {
        writeLog(`[Python Error] ${errorText}`, true);
      }
    });

    proc.on('close', (code) => {
      // Try to parse JSON from stderr (some Python scripts output JSON there)
      let jsonData = null;
      try {
        // Look for JSON in stderr
        const lines = stderr.split('\n');
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
            jsonData = JSON.parse(trimmed);
            break;
          }
        }
      } catch (e) {
        // If JSON parsing fails, that's okay - we'll try stdout
      }

      // Try to parse JSON from stdout if not found in stderr
      // (class_manager_cli.py and other scripts output JSON to stdout)
      if (!jsonData) {
        try {
          const stdoutLines = stdout.split('\n');
          for (const line of stdoutLines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
              jsonData = JSON.parse(trimmed);
              break;
            }
          }
        } catch (e) {
          // If JSON parsing fails, continue without jsonData
        }
      }

      // Parse stdout to extract user logs
      // New format: [LOG:LEVEL] message (e.g., [LOG:SUCCESS] ✅ Quiz processing completed!)
      // Legacy format: [USER] message or plain text
      const userLogs = [];
      const lines = stdout.split('\n').filter(l => l.trim());

      lines.forEach(line => {
        const trimmed = line.trim();

        // Skip JSON lines (we already parsed them)
        if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
          return;
        }

        // New format: [LOG:LEVEL] message
        const logMatch = trimmed.match(/^\[LOG:(SUCCESS|ERROR|WARNING|INFO)\] (.+)$/);
        if (logMatch) {
          userLogs.push({ level: logMatch[1], message: logMatch[2] });
          return;
        }

        // Legacy format: [USER] message
        if (trimmed.startsWith('[USER]')) {
          userLogs.push({ level: 'INFO', message: trimmed.substring(7) });
          return;
        }

        // Skip [DEV] messages and JSON responses
        // JSON responses start with { and contain "confidenceScores" or "success"
        if (trimmed.startsWith('[DEV]') ||
            (trimmed.startsWith('{') && (trimmed.includes('"confidenceScores"') || trimmed.includes('"success"')))) {
          return;
        }

        // Skip other lines starting with [ that aren't [LOG:LEVEL] or [USER]
        if (trimmed.startsWith('[') && !trimmed.match(/^\[LOG:/) && !trimmed.startsWith('[USER]')) {
          return;
        }

        // Legacy plain text - treat as INFO (for backward compatibility with logs array in JSON)
        if (trimmed) {
          userLogs.push({ level: 'INFO', message: trimmed });
        }
      });

      resolve({
        success: jsonData?.success ?? (code === 0),
        output: stdout,
        error: stderr,
        code,
        ...jsonData,  // Spread JSON fields (class, classes, error, etc.)
        data: jsonData,  // Keep for backward compatibility
        userLogs         // User-facing logs with level info
      });
    });

    proc.on('error', (error) => {
      reject(error);
    });
  });
}

module.exports = { writeLog, findPython, runPythonScript };
