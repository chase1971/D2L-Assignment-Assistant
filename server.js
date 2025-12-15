/**
 * Standalone Backend Server for Quiz Grader
 * Run with: node server.js
 * 
 * This server can run independently without Electron for development/testing.
 * For production, use the Electron packaged version.
 */

const express = require('express');
const cors = require('cors');
const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');
const multer = require('multer');

const app = express();
const DEFAULT_PORT = 5000;
let PORT = DEFAULT_PORT;

// Constants
const MAX_BUFFER_SIZE = 10 * 1024 * 1024; // 10MB buffer for Python script output

// Configure multer for file uploads
const upload = multer({
  dest: os.tmpdir(), // Store in system temp directory
  limits: {
    fileSize: 1000 * 1024 * 1024 // 1GB max file size (for very large combined PDFs)
  },
  fileFilter: (req, file, cb) => {
    // Only accept PDF files
    if (file.mimetype === 'application/pdf' || file.originalname.toLowerCase().endsWith('.pdf')) {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  }
});

// Middleware
app.use(cors());
app.use(express.json({ limit: '500mb' })); // Increase JSON body size limit
app.use(express.urlencoded({ extended: true, limit: '500mb' })); // Increase URL-encoded body size limit

// Logging
function writeLog(message, isError = false) {
  const timestamp = new Date().toISOString();
  const prefix = isError ? '[ERROR]' : '[INFO]';
  console.log(`${timestamp} ${prefix} ${message}`);
}

// Find Python executable
async function findPython() {
  const possiblePaths = [
    'python',
    'python3',
    'C:\\Python311\\python.exe',
    'C:\\Python310\\python.exe',
    'C:\\Python39\\python.exe',
    path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'Python', 'Python311', 'python.exe'),
    path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'Python', 'Python310', 'python.exe'),
  ];

  for (const pythonPath of possiblePaths) {
    try {
      const result = await new Promise((resolve) => {
        const proc = spawn(pythonPath, ['--version'], { shell: true });
        proc.on('close', (code) => resolve(code === 0));
        proc.on('error', () => resolve(false));
      });
      if (result) {
        writeLog(`Found Python at: ${pythonPath}`);
        return pythonPath;
      }
    } catch {
      continue;
    }
  }
  
  throw new Error('Python not found. Please install Python 3.9+ and add to PATH.');
}

// Config file path (same directory as server.js)
const CONFIG_PATH = path.join(__dirname, 'config.json');

// Load config
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    }
  } catch (error) {
    writeLog(`Error loading config: ${error.message}`, true);
  }
  
  // Default config
  return {
    downloadsPath: path.join(os.homedir(), 'Downloads'),
    rostersPath: path.join('C:', 'Rosters etc'),
    developerMode: true
  };
}

// Save config
function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    return true;
  } catch (error) {
    writeLog(`Error saving config: ${error.message}`, true);
    return false;
  }
}

// Python scripts path
// In packaged app: scripts are in resources/scripts (via extraResources)
// In development: scripts are in same directory as server.js
const SCRIPTS_PATH = process.resourcesPath 
  ? path.join(process.resourcesPath, 'scripts')
  : __dirname;

// ============================================================
// HELPER FUNCTIONS
// ============================================================

// Standard API response helper
function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

// Input validation helpers
function validateClassName(className) {
  if (!className || typeof className !== 'string') return false;
  // Block shell metacharacters that could be used for injection
  return !/[;&|`$(){}[\]<>]/.test(className);
}

function validateDrive(drive) {
  if (!drive || typeof drive !== 'string') return false;
  // Drive should be a single letter
  return /^[A-Za-z]$/.test(drive);
}

// Get possible rosters paths (mirrors Python config_reader.py logic)
function getPossibleRostersPaths(drive) {
  const username = os.userInfo().username;
  // Use proper Windows path format with backslashes
  return [
    `${drive}:\\Users\\${username}\\My Drive\\Rosters etc`,  // Standard path: C:\Users\chase\My Drive\Rosters etc
    `${drive}:\\${username}\\My Drive\\Rosters etc`,  // Alternative: C:\chase\My Drive\Rosters etc
    `${drive}:\\My Drive\\Rosters etc`,  // Direct: C:\My Drive\Rosters etc
    path.join(os.homedir(), 'My Drive', 'Rosters etc'),  // From home directory
  ];
}

// Find class folder in any of the possible rosters paths
function findClassFolder(drive, className) {
  const possiblePaths = getPossibleRostersPaths(drive);
  
  for (const rostersPath of possiblePaths) {
    // Use path.join for cross-platform compatibility, but handle Windows drive paths
    const classFolder = rostersPath.includes(':\\') 
      ? `${rostersPath}\\${className}`  // Windows absolute path
      : path.join(rostersPath, className);  // Relative or home directory path
      
    if (fs.existsSync(classFolder)) {
      return { rostersPath, classFolder };
    }
  }
  return null;
}

// Find PDFs folder for a class
function findPdfsFolder(drive, className) {
  const result = findClassFolder(drive, className);
  if (!result) return null;
  
  // Use proper path joining for Windows
  const separator = result.classFolder.includes(':\\') ? '\\' : path.sep;
  const importFilePath = `${result.classFolder}${separator}Import File.csv`;
  
  // Find the most recent "grade processing [CLASS_CODE] [ASSIGNMENT]" folder
  // Pattern matches both: "grade processing [CLASS_CODE] [ASSIGNMENT]" and "grade processing [ASSIGNMENT]"
  let pdfsFolder = null;
  let processingFolder = null;
  
  try {
    if (fs.existsSync(result.classFolder)) {
      const folders = fs.readdirSync(result.classFolder);
      const processingFolders = [];
      
      for (const folderName of folders) {
        const folderPath = path.join(result.classFolder, folderName);
        if (fs.statSync(folderPath).isDirectory()) {
          // Match "grade processing" followed by anything
          if (/^grade processing .+$/i.test(folderName)) {
            processingFolders.push({
              name: folderName,
              path: folderPath,
              mtime: fs.statSync(folderPath).mtime.getTime()
            });
          }
        }
      }
      
      if (processingFolders.length > 0) {
        // Sort by modification time (newest first) and use the most recent
        processingFolders.sort((a, b) => b.mtime - a.mtime);
        processingFolder = processingFolders[0].path;
        pdfsFolder = path.join(processingFolder, 'PDFs');
      }
    }
  } catch (error) {
    // If we can't read the folder, fall back to old naming convention
    console.error('Error finding processing folder:', error);
  }
  
  // Fallback to old naming convention if no processing folders found
  if (!processingFolder) {
    processingFolder = `${result.classFolder}${separator}grade processing`;
    pdfsFolder = `${processingFolder}${separator}PDFs`;
  }
  
  // Return the path even if folder doesn't exist yet (for file dialogs)
  return {
    ...result,
    pdfsFolder,
    processingFolder,
    importFilePath
  };
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
        writeLog(`Could not parse JSON line: ${parseErr.message}`, true);
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

// Helper to run Python scripts
async function runPythonScript(scriptName, args = []) {
  const pythonPath = await findPython();
  const scriptPath = path.join(SCRIPTS_PATH, scriptName);
  
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
    
    // Construct command string for Windows shell
    const command = `${quotedPythonPath} ${quotedScriptPath} ${quotedArgs}`;
    
    const proc = exec(command, {
      cwd: SCRIPTS_PATH,
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
      writeLog(`[Python Error] ${data.toString()}`, true);
    });

    proc.on('close', (code) => {
      // Try to parse JSON from stderr (our Python scripts output JSON there)
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
        // If JSON parsing fails, that's okay - we'll just use stdout
      }
      
      // Parse stdout to extract user logs
      // New format: [LOG:LEVEL] message (e.g., [LOG:SUCCESS] ✅ Quiz processing completed!)
      // Legacy format: [USER] message or plain text
      const userLogs = [];
      const lines = stdout.split('\n').filter(l => l.trim());
      
      lines.forEach(line => {
        const trimmed = line.trim();
        
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
        
        // Skip [DEV] messages and other internal output
        if (trimmed.startsWith('[DEV]') || trimmed.startsWith('{') || trimmed.startsWith('[')) {
          return;
        }
        
        // Legacy plain text - treat as INFO (for backward compatibility with logs array in JSON)
        if (trimmed) {
          userLogs.push({ level: 'INFO', message: trimmed });
        }
      });
      
      resolve({
        success: code === 0,
        output: stdout,
        error: stderr,
        code,
        data: jsonData,  // Include parsed JSON data if available
        userLogs         // User-facing logs with level info
      });
    });

    proc.on('error', (error) => {
      reject(error);
    });
  });
}

// ============================================================
// API ROUTES
// ============================================================

// Test endpoint
app.get('/api/test', (req, res) => {
  apiResponse(res, { success: true, message: 'Backend server is running!' });
});

// Config endpoints
app.get('/api/config', (req, res) => {
  apiResponse(res, { success: true, config: loadConfig() });
});

app.post('/api/config', (req, res) => {
  const success = saveConfig(req.body);
  apiResponse(res, { success, config: success ? req.body : null, error: success ? null : 'Failed to save config' });
});

// Quiz routes
app.post('/api/quiz/list-classes', async (req, res) => {
  try {
    const result = await runPythonScript('helper_cli.py', ['list-classes', req.body.drive || 'C']);
    
    // Parse output for class list
    const classes = [];
    if (result.success && result.output) {
      const lines = result.output.split('\n');
      lines.forEach(line => {
        if (line.trim() && !line.startsWith('[') && !line.includes('Found')) {
          classes.push(line.trim());
        }
      });
    }
    
    // Use separated user logs if available
    const logs = result.userLogs && result.userLogs.length > 0 
      ? result.userLogs 
      : result.output.split('\n').filter(l => l.trim() && !l.trim().startsWith('[DEV]'))
          .map(l => l.trim().startsWith('[USER]') ? l.trim().substring(7) : l.trim());
    apiResponse(res, { success: result.success, classes, logs });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/process', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const result = await runPythonScript('process_quiz_cli.py', [drive || 'C', className]);
    
    // Check for multiple ZIP files
    const zipResult = parseZipFilesFromOutput(result.output, loadConfig().downloadsPath);
    if (zipResult.found) {
      return apiResponse(res, {
        success: false,
        error: 'Multiple ZIP files found',
        zip_files: zipResult.zipFiles,
        logs: []  // Don't include logs - modal will show, no need for terminal output
      });
    }
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      combined_pdf_path: result.data?.combined_pdf_path,
      assignment_name: result.data?.assignment_name,
      ...(result.success ? {} : { error: result.error || 'Processing failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/process-selected', async (req, res) => {
  try {
    const { drive, className, zipPath } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const result = await runPythonScript('process_quiz_cli.py', [drive || 'C', className, zipPath]);
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      combined_pdf_path: result.data?.combined_pdf_path,
      assignment_name: result.data?.assignment_name,
      ...(result.success ? {} : { error: result.error || 'Processing failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/process-completion', async (req, res) => {
  try {
    const { drive, className, dontOverride } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const args = [drive || 'C', className];
    if (dontOverride) args.push('--dont-override');
    
    const result = await runPythonScript('process_completion_cli.py', args);
    
    // Check for multiple ZIP files
    const zipResult = parseZipFilesFromOutput(result.output, loadConfig().downloadsPath);
    if (zipResult.found) {
      return apiResponse(res, {
        success: false,
        error: 'Multiple ZIP files found',
        zip_files: zipResult.zipFiles,
        logs: []  // Don't include logs - modal will show, no need for terminal output
      });
    }
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      ...(result.success ? {} : { error: result.error || 'Processing failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/process-completion-selected', async (req, res) => {
  try {
    const { drive, className, zipPath, dontOverride } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const args = [drive || 'C', className, zipPath];
    if (dontOverride) args.push('--dont-override');
    
    const result = await runPythonScript('process_completion_cli.py', args);
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      combined_pdf_path: result.data?.combined_pdf_path,
      assignment_name: result.data?.assignment_name,
      ...(result.success ? {} : { error: result.error || 'Processing failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/extract-grades', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const result = await runPythonScript('extract_grades_cli.py', [drive || 'C', className]);
    
    // Check if output is JSON (Python script returned structured response)
    let logs = [];
    let error = null;
    let success = result.success;
    
    try {
      // Try to parse the entire output as JSON first (Python script may output pure JSON)
      const trimmedOutput = result.output.trim();
      if (trimmedOutput.startsWith('{')) {
        const jsonData = JSON.parse(trimmedOutput);
        success = jsonData.success !== false; // Explicitly check for false
        logs = jsonData.logs || [];
        error = jsonData.error || null;
      } else {
        // Try to find JSON in the output (might be mixed with other text)
        const jsonMatch = trimmedOutput.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const jsonData = JSON.parse(jsonMatch[0]);
          success = jsonData.success !== false;
          logs = jsonData.logs || [];
          error = jsonData.error || null;
        } else {
          // Use separated user logs if available, otherwise fall back to parsing output
          if (result.userLogs && result.userLogs.length > 0) {
            logs = result.userLogs;
          } else {
            // Legacy: parse output and filter out [DEV] lines
            logs = result.output.split('\n')
              .filter(l => l.trim() && !l.trim().startsWith('[DEV]'))
              .map(l => l.trim().startsWith('[USER]') ? l.trim().substring(7) : l.trim());
          }
          if (!result.success) {
            error = result.error || 'Extraction failed';
          }
        }
      }
    } catch (parseError) {
      // If JSON parsing fails, use separated user logs or fall back to plain text
      if (result.userLogs && result.userLogs.length > 0) {
        logs = result.userLogs;
      } else {
        logs = result.output.split('\n')
          .filter(l => l.trim() && !l.trim().startsWith('[DEV]'))
          .map(l => l.trim().startsWith('[USER]') ? l.trim().substring(7) : l.trim());
      }
      if (!result.success) {
        error = result.error || 'Extraction failed';
      }
    }
    
    apiResponse(res, {
      success,
      logs,
      ...(success ? {} : { error: error || 'Extraction failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Handle file upload for split PDF with error handling middleware
app.post('/api/quiz/split-pdf-upload', (req, res, next) => {
  upload.single('pdf')(req, res, (err) => {
    if (err) {
      // Handle multer errors
      if (err.code === 'LIMIT_FILE_SIZE') {
        return apiResponse(res, { 
          success: false, 
          error: `File too large. Maximum size is 1GB. Your file appears to exceed this limit.` 
        });
      }
      return apiResponse(res, { 
        success: false, 
        error: `File upload error: ${err.message}` 
      });
    }
    next();
  });
}, async (req, res) => {
  try {
    
    const { drive, className, assignmentName } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    if (!req.file) {
      return apiResponse(res, { success: false, error: 'No PDF file uploaded' });
    }
    
    const uploadedFilePath = req.file.path;
    const originalName = req.file.originalname || 'uploaded.pdf';
    
    // Extract assignment name from filename if not provided
    let finalAssignmentName = assignmentName;
    if (!finalAssignmentName) {
      finalAssignmentName = originalName.replace(/\.pdf$/i, '').trim();
    }
    
    // Call split_pdf_cli.py with the uploaded file path AND assignment name
    // Format: python split_pdf_cli.py <drive> <className> <assignmentName> '' <pdfPath>
    // (5 args: drive, className, assignmentName, empty string, pdfPath)
    const args = [drive || 'C', className, finalAssignmentName, '', uploadedFilePath];
    const result = await runPythonScript('split_pdf_cli.py', args);
    
    // Clean up uploaded file after processing
    try {
      fs.unlinkSync(uploadedFilePath);
    } catch (cleanupError) {
      // Ignore cleanup errors
    }
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      assignmentName: finalAssignmentName,
      ...(result.success ? {} : { error: result.error || 'Split failed' })
    });
  } catch (error) {
    // Clean up uploaded file on error
    if (req.file && req.file.path) {
      try {
        fs.unlinkSync(req.file.path);
      } catch (cleanupError) {
        // Ignore cleanup errors
      }
    }
    
    // Handle multer-specific errors
    let errorMessage = error.message;
    if (error.name === 'MulterError') {
      if (error.code === 'LIMIT_FILE_SIZE') {
        errorMessage = `File too large. Maximum size is 1GB. Your file appears to be larger than this limit.`;
      } else {
        errorMessage = `File upload error: ${error.message}`;
      }
    }
    
    apiResponse(res, { success: false, error: errorMessage });
  }
});

app.post('/api/quiz/split-pdf', async (req, res) => {
  try {
    const { drive, className, assignmentName, pdfPath } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const args = [drive || 'C', className];
    if (pdfPath) {
      // If PDF path is provided, use it directly (skip assignment name)
      args.push(''); // Empty assignment name
      args.push(pdfPath); // PDF path as 4th argument
    } else if (assignmentName) {
      args.push(assignmentName);
    }
    
    const result = await runPythonScript('split_pdf_cli.py', args);
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      ...(result.success ? {} : { error: result.error || 'Split failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/get-pdfs-folder', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const pdfsFolderResult = findPdfsFolder(drive || 'C', className);
    if (pdfsFolderResult) {
      // Return the PDFs folder path and find an existing parent for the file dialog
      const pdfsFolder = pdfsFolderResult.pdfsFolder;
      const processingFolder = pdfsFolderResult.processingFolder;
      const classFolder = pdfsFolderResult.classFolder;
      
      // Find the first existing directory to use as defaultPath
      // Electron file dialogs ignore defaultPath if the directory doesn't exist
      let existingPath = pdfsFolder;
      if (!fs.existsSync(pdfsFolder)) {
        if (fs.existsSync(processingFolder)) {
          existingPath = processingFolder;
        } else if (fs.existsSync(classFolder)) {
          existingPath = classFolder;
        } else {
          // Use the rosters path as fallback
          existingPath = pdfsFolderResult.rostersPath;
        }
      }
      
      apiResponse(res, { 
        success: true, 
        path: pdfsFolder,  // Target path for logging
        existingPath: existingPath,  // Existing parent for file dialog
        classFolder: pdfsFolderResult.classFolder  // Class roster folder path
      });
    } else {
      // Try to construct path even if class folder not found
      const possiblePaths = getPossibleRostersPaths(drive || 'C');
      if (possiblePaths.length > 0) {
        // Find the first existing rosters path
        let existingRostersPath = possiblePaths[0];
        for (const rostersPath of possiblePaths) {
          if (fs.existsSync(rostersPath)) {
            existingRostersPath = rostersPath;
            break;
          }
        }
        
        // Try to find the most recent grade processing folder
        const separator = existingRostersPath.includes(':\\') ? '\\' : path.sep;
        const classFolderPath = path.join(existingRostersPath, className);
        let constructedPath = null;
        let existingPath = existingRostersPath;
        
        try {
          if (fs.existsSync(classFolderPath)) {
            const folders = fs.readdirSync(classFolderPath);
            const processingFolders = [];
            
            for (const folderName of folders) {
              const folderPath = path.join(classFolderPath, folderName);
              if (fs.statSync(folderPath).isDirectory()) {
                // Match "grade processing" followed by anything
                if (/^grade processing .+$/i.test(folderName)) {
                  processingFolders.push({
                    name: folderName,
                    path: folderPath,
                    mtime: fs.statSync(folderPath).mtime.getTime()
                  });
                }
              }
            }
            
            if (processingFolders.length > 0) {
              // Sort by modification time (newest first) and use the most recent
              processingFolders.sort((a, b) => b.mtime - a.mtime);
              const mostRecentFolder = processingFolders[0].path;
              constructedPath = path.join(mostRecentFolder, 'PDFs');
              existingPath = mostRecentFolder; // Use the processing folder as existing path
            }
          }
        } catch (error) {
          console.error('Error finding processing folder:', error);
        }
        
        // Fallback to old naming convention if no processing folders found
        if (!constructedPath) {
          constructedPath = `${existingRostersPath}${separator}${className}${separator}grade processing${separator}PDFs`;
          existingPath = existingRostersPath;
        }
        
        apiResponse(res, { 
          success: true, 
          path: constructedPath,
          existingPath: existingPath
        });
      } else {
        apiResponse(res, { success: false, error: 'Could not determine rosters path' });
      }
    }
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/open-folder', async (req, res) => {
  try {
    const { drive, className, classFolderOnly } = req.body;
    
    // Handle DOWNLOADS special case
    if (className === 'DOWNLOADS') {
      // No validation needed for special DOWNLOADS case
      const downloadsPath = loadConfig().downloadsPath || path.join(os.homedir(), 'Downloads');
      const { exec } = require('child_process');
      exec(`explorer "${downloadsPath}"`);
      apiResponse(res, { success: true, message: 'Downloads folder opened', logs: ['📂 Downloads folder opened'] });
      return;
    }
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    // If classFolderOnly is true, open the class roster folder directly
    if (classFolderOnly) {
      const result = findClassFolder(drive || 'C', className);
      if (result && result.classFolder) {
        const { exec } = require('child_process');
        exec(`explorer "${result.classFolder}"`);
        apiResponse(res, { success: true, message: 'Class roster folder opened', logs: [`📂 Opened class roster folder: ${result.classFolder}`] });
        return;
      } else {
        return apiResponse(res, { success: false, error: `Class folder not found: ${className}` });
      }
    }
    
    const result = await runPythonScript('helper_cli.py', ['open-folder', drive || 'C', className]);
    
    // Parse JSON output from Python script
    let pythonResult;
    try {
      pythonResult = JSON.parse(result.output);
    } catch (e) {
      pythonResult = { success: false, error: 'Failed to parse response' };
    }
    
    // Build friendly log messages instead of raw JSON
    const logs = [];
    if (pythonResult.success) {
      logs.push(`📂 Folder opened: ${pythonResult.folder || className}`);
    } else {
      logs.push(`❌ ${pythonResult.error || 'Failed to open folder'}`);
    }
    
    apiResponse(res, { 
      success: pythonResult.success, 
      logs: logs,
      message: pythonResult.message || pythonResult.error,
      ...(pythonResult.success ? {} : { error: pythonResult.error || 'Failed to open folder' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message, logs: [`❌ ${error.message}`] });
  }
});

app.post('/api/quiz/clear-data', async (req, res) => {
  try {
    const { drive, className, assignmentName, saveFoldersAndPdf } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    if (!assignmentName) {
      return apiResponse(res, { success: false, error: 'Assignment name required' });
    }
    
    const args = [drive || 'C', className, assignmentName];
    if (saveFoldersAndPdf) {
      args.push('--save-folders-and-pdf');
    }
    
    const result = await runPythonScript('clear_data_cli.py', args);
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      ...(result.success ? {} : { error: result.error || 'Clear failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// List processing folders for a class
app.post('/api/quiz/list-processing-folders', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const result = await runPythonScript('clear_data_cli.py', [drive || 'C', className, '--list']);
    
    if (result.success) {
      // Parse JSON output from Python script
      try {
        const jsonOutput = JSON.parse(result.output);
        apiResponse(res, {
          success: jsonOutput.success,
          folders: jsonOutput.folders || [],
          ...(jsonOutput.error ? { error: jsonOutput.error } : {})
        });
      } catch (parseError) {
        apiResponse(res, { success: false, error: 'Failed to parse folder list' });
      }
    } else {
      apiResponse(res, { success: false, error: result.error || 'Failed to list folders' });
    }
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Clear all archived data for a class
app.post('/api/quiz/clear-archived-data', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }
    
    const result = await runPythonScript('clear_data_cli.py', [drive || 'C', className, '--clear-archived']);
    
    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      ...(result.success ? {} : { error: result.error || 'Clear archived failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Open a specific file (PDF, Excel, etc.)
app.post('/api/open-file', async (req, res) => {
  try {
    const { filePath } = req.body;
    
    if (!filePath) {
      return apiResponse(res, { success: false, error: 'No file path provided' });
    }
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return apiResponse(res, { success: false, error: 'File not found' });
    }
    
    writeLog(`Opening file: ${filePath}`);
    
    // Open file with default application
    exec(`start "" "${filePath}"`, (error) => {
      if (error) {
        writeLog(`Error opening file: ${error.message}`, true);
        apiResponse(res, { success: false, error: error.message });
      } else {
        apiResponse(res, { success: true, message: 'File opened' });
      }
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Open student's individual PDF
app.post('/api/open-student-pdf', async (req, res) => {
  try {
    const { drive, className, studentName } = req.body;
    
    if (!drive || !className || !studentName) {
      return apiResponse(res, { success: false, error: 'Missing required parameters' });
    }
    
    // Find PDFs folder using helper
    const folders = findPdfsFolder(drive, className);
    if (!folders) {
      return apiResponse(res, { success: false, error: 'Class folder not found' });
    }
    
    const { pdfsFolder, importFilePath } = folders;
    
    // Read Import File.csv to map student name to username
    let username = null;
    if (fs.existsSync(importFilePath)) {
      const csvContent = fs.readFileSync(importFilePath, 'utf8');
      const lines = csvContent.split('\n');
      
      // Parse CSV header to find column indices
      const header = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
      const firstNameIdx = header.findIndex(h => h.toLowerCase() === 'first name');
      const lastNameIdx = header.findIndex(h => h.toLowerCase() === 'last name');
      const usernameIdx = header.findIndex(h => h.toLowerCase() === 'username');
      
      if (usernameIdx !== -1) {
        const nameParts = studentName.toLowerCase().split(' ');
        
        for (let i = 1; i < lines.length; i++) {
          const row = lines[i].split(',').map(c => c.trim().replace(/"/g, ''));
          if (row.length <= usernameIdx) continue;
          
          const firstName = (row[firstNameIdx] || '').toLowerCase();
          const lastName = (row[lastNameIdx] || '').toLowerCase();
          const csvFullName = `${firstName} ${lastName}`;
          const studentNameLower = studentName.toLowerCase();
          
          // Strategy 1: Exact match or close match
          if (csvFullName === studentNameLower || 
              (studentNameLower.includes(firstName) && studentNameLower.includes(lastName))) {
            username = row[usernameIdx];
            break;
          }
          
          // Strategy 2: Match at least 2 name parts
          const csvParts = [...firstName.split(' '), ...lastName.split(' ')].filter(p => p);
          const matchCount = nameParts.filter(p => csvParts.includes(p)).length;
          if (matchCount >= 2) {
            username = row[usernameIdx];
            break;
          }
        }
      }
    }
    
    // If we found a username, look for that PDF
    let pdfPath = null;
    if (username) {
      const expectedPdf = path.join(pdfsFolder, `${username}.pdf`);
      if (fs.existsSync(expectedPdf)) {
        pdfPath = expectedPdf;
      }
    }
    
    // Fallback: search by name parts in filename
    if (!pdfPath) {
      const files = fs.readdirSync(pdfsFolder).filter(f => f.endsWith('.pdf') && !f.includes('combined'));
      const nameParts = studentName.toLowerCase().split(' ');
      
      const studentPdf = files.find(f => {
        const fileLower = f.toLowerCase();
        return nameParts.some(part => part.length > 2 && fileLower.includes(part));
      });
      
      if (studentPdf) {
        pdfPath = path.join(pdfsFolder, studentPdf);
      }
    }
    
    if (!pdfPath) {
      return apiResponse(res, { success: false, error: `PDF not found for ${studentName}` });
    }
    
    writeLog(`Opening PDF: ${pdfPath}`);
    exec(`start "" "${pdfPath}"`, (error) => {
      if (error) {
        apiResponse(res, { success: false, error: error.message });
      } else {
        apiResponse(res, { success: true, message: 'PDF opened' });
      }
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Open combined PDF
app.post('/api/open-combined-pdf', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!drive || !className) {
      return apiResponse(res, { success: false, error: 'Missing required parameters' });
    }
    
    // Find PDFs folder using helper
    const folders = findPdfsFolder(drive, className);
    if (!folders) {
      return apiResponse(res, { success: false, error: 'Combined PDF not found - class folder not found' });
    }
    
    // Find the most recent PDF in the folder (assignment-named PDFs)
    let combinedPdf = null;
    if (fs.existsSync(folders.pdfsFolder)) {
      const pdfFiles = fs.readdirSync(folders.pdfsFolder)
        .filter(f => f.endsWith('.pdf'))
        .map(f => ({ name: f, mtime: fs.statSync(path.join(folders.pdfsFolder, f)).mtime }))
        .sort((a, b) => b.mtime - a.mtime);
      
      if (pdfFiles.length > 0) {
        combinedPdf = path.join(folders.pdfsFolder, pdfFiles[0].name);
      }
    }
    
    if (!combinedPdf || !fs.existsSync(combinedPdf)) {
      return apiResponse(res, { success: false, error: 'Combined PDF not found' });
    }
    
    writeLog(`Opening combined PDF: ${combinedPdf}`);
    exec(`start "" "${combinedPdf}"`, (error) => {
      if (error) {
        apiResponse(res, { success: false, error: error.message });
      } else {
        apiResponse(res, { success: true, message: 'PDF opened' });
      }
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Open import file (CSV/Excel)
app.post('/api/open-import-file', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!drive || !className) {
      return apiResponse(res, { success: false, error: 'Missing required parameters' });
    }
    
    // Find the import file using helper
    const folders = findPdfsFolder(drive, className);
    if (!folders) {
      return apiResponse(res, { success: false, error: 'Class folder not found' });
    }
    
    const { importFilePath } = folders;
    
    if (!fs.existsSync(importFilePath)) {
      return apiResponse(res, { success: false, error: 'Import File not found' });
    }
    
    writeLog(`Opening import file: ${importFilePath}`);
    exec(`start "" "${importFilePath}"`, (error) => {
      if (error) {
        apiResponse(res, { success: false, error: error.message });
      } else {
        apiResponse(res, { success: true, message: 'Import file opened', path: importFilePath });
      }
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Kill all Node processes
app.post('/api/kill-processes', async (req, res) => {
  try {
    // Use PowerShell to kill Node processes (excluding current one)
    const command = `powershell -Command "Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne ${process.pid} } | Stop-Process -Force"`;
    
    exec(command, (error, stdout, stderr) => {
      if (error && !error.message.includes('Cannot find a process')) {
        apiResponse(res, { success: false, error: error.message });
      } else {
        // Count how many were killed
        exec('powershell -Command "Get-Process -Name node -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"', (err, output) => {
          const remaining = parseInt(output.trim()) || 0;
          const killed = remaining > 1 ? remaining - 1 : 0; // Subtract current process
          apiResponse(res, { success: true, killed, message: 'Processes killed' });
        });
      }
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// ============================================================
// START SERVER WITH DYNAMIC PORT
// ============================================================

function startServer(port) {
  const server = app.listen(port, () => {
    PORT = port;
    console.log('');
    console.log('='.repeat(50));
    console.log('  Quiz Grader Backend Server');
    console.log('='.repeat(50));
    console.log(`  Server running at: http://localhost:${PORT}`);
    console.log(`  API test endpoint: http://localhost:${PORT}/api/test`);
    console.log(`  Scripts path: ${SCRIPTS_PATH}`);
    console.log('='.repeat(50));
    console.log('');
    writeLog('Server started successfully');
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`Port ${port} is in use, trying ${port + 1}...`);
      startServer(port + 1);
    } else {
      console.error('Server error:', err);
      process.exit(1);
    }
  });
}

// Start with default port, will auto-increment if busy
startServer(DEFAULT_PORT);

