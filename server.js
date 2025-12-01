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

const app = express();
const DEFAULT_PORT = 5000;
let PORT = DEFAULT_PORT;

// Middleware
app.use(cors());
app.use(express.json());

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

// Get possible rosters paths (mirrors Python config_reader.py logic)
function getPossibleRostersPaths(drive) {
  return [
    path.join(os.homedir(), 'My Drive', 'Rosters etc'),  // Google Drive path
    path.join(drive + ':', 'Rosters etc'),  // Direct drive path
    path.join(drive + ':', 'Users', os.userInfo().username, 'My Drive', 'Rosters etc'),  // Full path
  ];
}

// Find class folder in any of the possible rosters paths
function findClassFolder(drive, className) {
  const possiblePaths = getPossibleRostersPaths(drive);
  
  for (const rostersPath of possiblePaths) {
    const classFolder = path.join(rostersPath, className);
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
  
  const pdfsFolder = path.join(result.classFolder, 'grade processing', 'PDFs');
  if (fs.existsSync(pdfsFolder)) {
    return {
      ...result,
      pdfsFolder,
      processingFolder: path.join(result.classFolder, 'grade processing'),
      importFilePath: path.join(result.classFolder, 'Import File.csv')
    };
  }
  return null;
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
      maxBuffer: 10 * 1024 * 1024 // 10MB buffer
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
      // Log each line as it comes
      data.toString().split('\n').filter(l => l.trim()).forEach(line => {
        writeLog(`[Python] ${line}`);
      });
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
      writeLog(`[Python Error] ${data.toString()}`, true);
    });

    proc.on('close', (code) => {
      resolve({
        success: code === 0,
        output: stdout,
        error: stderr,
        code
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
  res.json({ success: true, message: 'Backend server is running!' });
});

// Config endpoints
app.get('/api/config', (req, res) => {
  res.json({ success: true, config: loadConfig() });
});

app.post('/api/config', (req, res) => {
  const success = saveConfig(req.body);
  res.json({ success, config: success ? req.body : null });
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
    
    res.json({ success: result.success, classes, logs: result.output.split('\n').filter(l => l.trim()) });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.post('/api/quiz/process', async (req, res) => {
  try {
    const { drive, className } = req.body;
    const result = await runPythonScript('process_quiz_cli.py', [drive || 'C', className]);
    
    // Check for multiple ZIP files
    const zipResult = parseZipFilesFromOutput(result.output, loadConfig().downloadsPath);
    if (zipResult.found) {
      return apiResponse(res, {
        success: false,
        error: 'Multiple ZIP files found',
        zip_files: zipResult.zipFiles,
        logs: zipResult.logs
      });
    }
    
    apiResponse(res, {
      success: result.success,
      logs: result.output.split('\n').filter(l => l.trim()),
      error: result.error || 'Processing failed'
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/process-selected', async (req, res) => {
  try {
    const { drive, className, zipPath } = req.body;
    const result = await runPythonScript('process_quiz_cli.py', [drive || 'C', className, zipPath]);
    
    apiResponse(res, {
      success: result.success,
      logs: result.output.split('\n').filter(l => l.trim()),
      error: result.error || 'Processing failed'
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/process-completion', async (req, res) => {
  try {
    const { drive, className, dontOverride } = req.body;
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
        logs: zipResult.logs
      });
    }
    
    apiResponse(res, {
      success: result.success,
      logs: result.output.split('\n').filter(l => l.trim()),
      error: result.error || 'Processing failed'
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/process-completion-selected', async (req, res) => {
  try {
    const { drive, className, zipPath, dontOverride } = req.body;
    const args = [drive || 'C', className, zipPath];
    if (dontOverride) args.push('--dont-override');
    
    const result = await runPythonScript('process_completion_cli.py', args);
    
    apiResponse(res, {
      success: result.success,
      logs: result.output.split('\n').filter(l => l.trim()),
      error: result.error || 'Processing failed'
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/extract-grades', async (req, res) => {
  try {
    const { drive, className } = req.body;
    const result = await runPythonScript('extract_grades_cli.py', [drive || 'C', className]);
    
    apiResponse(res, {
      success: result.success,
      logs: result.output.split('\n').filter(l => l.trim()),
      error: result.error || 'Extraction failed'
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/split-pdf', async (req, res) => {
  try {
    const { drive, className, assignmentName } = req.body;
    const args = [drive || 'C', className];
    if (assignmentName) {
      args.push(assignmentName);
    }
    const result = await runPythonScript('split_pdf_cli.py', args);
    
    apiResponse(res, {
      success: result.success,
      logs: result.output.split('\n').filter(l => l.trim()),
      error: result.error || 'Split failed'
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

app.post('/api/quiz/open-folder', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    // Handle DOWNLOADS special case
    if (className === 'DOWNLOADS') {
      const downloadsPath = loadConfig().downloadsPath || path.join(os.homedir(), 'Downloads');
      const { exec } = require('child_process');
      exec(`explorer "${downloadsPath}"`);
      res.json({ success: true, message: 'Downloads folder opened', logs: ['📂 Downloads folder opened'] });
      return;
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
    
    res.json({ 
      success: pythonResult.success, 
      logs: logs,
      message: pythonResult.message || pythonResult.error,
      error: pythonResult.success ? null : (pythonResult.error || 'Failed to open folder')
    });
  } catch (error) {
    res.json({ success: false, error: error.message, logs: [`❌ ${error.message}`] });
  }
});

app.post('/api/quiz/clear-data', async (req, res) => {
  try {
    const { drive, className } = req.body;
    const result = await runPythonScript('cleanup_data_cli.py', [drive || 'C', className]);
    
    apiResponse(res, {
      success: result.success,
      logs: result.output.split('\n').filter(l => l.trim()),
      error: result.error || 'Clear failed'
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
      res.json({ success: false, error: 'No file path provided' });
      return;
    }
    
    // Check if file exists
    if (!fs.existsSync(filePath)) {
      res.json({ success: false, error: 'File not found' });
      return;
    }
    
    writeLog(`Opening file: ${filePath}`);
    
    // Open file with default application
    const { exec } = require('child_process');
    exec(`start "" "${filePath}"`, (error) => {
      if (error) {
        writeLog(`Error opening file: ${error.message}`, true);
        res.json({ success: false, error: error.message });
      } else {
        res.json({ success: true, message: 'File opened' });
      }
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

// Open student's individual PDF
app.post('/api/open-student-pdf', async (req, res) => {
  try {
    const { drive, className, studentName } = req.body;
    
    if (!drive || !className || !studentName) {
      return res.json({ success: false, error: 'Missing required parameters' });
    }
    
    // Find PDFs folder using helper
    const folders = findPdfsFolder(drive, className);
    if (!folders) {
      return res.json({ success: false, error: 'Class folder not found' });
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
      return res.json({ success: false, error: `PDF not found for ${studentName}` });
    }
    
    writeLog(`Opening PDF: ${pdfPath}`);
    exec(`start "" "${pdfPath}"`, (error) => {
      if (error) {
        res.json({ success: false, error: error.message });
      } else {
        res.json({ success: true, message: 'PDF opened' });
      }
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

// Open combined PDF
app.post('/api/open-combined-pdf', async (req, res) => {
  try {
    const { drive, className } = req.body;
    
    if (!drive || !className) {
      return res.json({ success: false, error: 'Missing required parameters' });
    }
    
    // Find PDFs folder using helper
    const folders = findPdfsFolder(drive, className);
    if (!folders) {
      return res.json({ success: false, error: 'Combined PDF not found - class folder not found' });
    }
    
    const combinedPdf = path.join(folders.pdfsFolder, '1combinedpdf.pdf');
    
    if (!fs.existsSync(combinedPdf)) {
      return res.json({ success: false, error: 'Combined PDF not found' });
    }
    
    writeLog(`Opening combined PDF: ${combinedPdf}`);
    exec(`start "" "${combinedPdf}"`, (error) => {
      if (error) {
        res.json({ success: false, error: error.message });
      } else {
        res.json({ success: true, message: 'PDF opened' });
      }
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

// Kill all Node processes
app.post('/api/kill-processes', async (req, res) => {
  try {
    const { exec } = require('child_process');
    
    // Use PowerShell to kill Node processes (excluding current one)
    const command = `powershell -Command "Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne ${process.pid} } | Stop-Process -Force"`;
    
    exec(command, (error, stdout, stderr) => {
      if (error && !error.message.includes('Cannot find a process')) {
        res.json({ success: false, error: error.message });
      } else {
        // Count how many were killed
        exec('powershell -Command "Get-Process -Name node -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"', (err, output) => {
          const remaining = parseInt(output.trim()) || 0;
          const killed = remaining > 1 ? remaining - 1 : 0; // Subtract current process
          res.json({ success: true, killed, message: 'Processes killed' });
        });
      }
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
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

