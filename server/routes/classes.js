/**
 * Class management routes
 * Handles all /api/classes/* endpoints
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { exec } = require('child_process');

const router = express.Router();

const { runPythonScript, writeLog } = require('../python-runner');

// Standard API response helper
function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

// Load all classes
router.get('/', async (req, res) => {
  try {
    const result = await runPythonScript('class_manager_cli.py', ['list']);

    if (result.success && result.classes) {
      apiResponse(res, { success: true, classes: result.classes });
    } else {
      apiResponse(res, { success: false, error: result.error || 'Failed to load classes' });
    }
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Add a new class
router.post('/add', async (req, res) => {
  try {
    const { value, label, rosterFolderPath } = req.body;

    if (!value || !label) {
      return apiResponse(res, { success: false, error: 'Missing required parameters: value, label' });
    }

    const result = await runPythonScript('class_manager_cli.py', [
      'add',
      value,
      label,
      rosterFolderPath || ''
    ]);

    if (result.success) {
      apiResponse(res, { success: true, class: result.class });
    } else {
      apiResponse(res, { success: false, error: result.error || 'Failed to add class' });
    }
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Edit an existing class
router.put('/edit/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { value, label, rosterFolderPath } = req.body;

    if (!value || !label) {
      return apiResponse(res, { success: false, error: 'Missing required parameters: value, label' });
    }

    const result = await runPythonScript('class_manager_cli.py', [
      'edit',
      id,
      value,
      label,
      rosterFolderPath || ''
    ]);

    if (result.success) {
      apiResponse(res, { success: true });
    } else {
      apiResponse(res, { success: false, error: result.error || 'Failed to edit class' });
    }
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Delete a class
router.delete('/delete/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const result = await runPythonScript('class_manager_cli.py', ['delete', id]);

    if (result.success) {
      apiResponse(res, { success: true });
    } else {
      apiResponse(res, { success: false, error: result.error || 'Failed to delete class' });
    }
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Delete all non-protected classes
router.delete('/deleteAll', async (req, res) => {
  try {
    const result = await runPythonScript('class_manager_cli.py', ['deleteAll']);

    if (result.success) {
      apiResponse(res, { success: true, deletedCount: result.deletedCount || 0 });
    } else {
      apiResponse(res, { success: false, error: result.error || 'Failed to delete classes' });
    }
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Validate folder has CSV file
router.post('/validate-folder', async (req, res) => {
  try {
    const { folderPath } = req.body;

    if (!folderPath) {
      return apiResponse(res, { success: false, hasCSV: false, error: 'Folder path is required' });
    }

    // Normalize the path - handle both single and double backslashes
    const normalizedPath = path.normalize(folderPath.replace(/\\/g, path.sep));

    writeLog(`[Validate Folder] Checking path: ${normalizedPath}`);
    writeLog(`[Validate Folder] Path exists: ${fs.existsSync(normalizedPath)}`);

    if (!fs.existsSync(normalizedPath)) {
      writeLog(`[Validate Folder] ERROR: Folder does not exist at: ${normalizedPath}`);
      return apiResponse(res, { success: false, hasCSV: false, error: `Folder does not exist: ${normalizedPath}` });
    }

    if (!fs.statSync(normalizedPath).isDirectory()) {
      writeLog(`[Validate Folder] ERROR: Path is not a directory: ${normalizedPath}`);
      return apiResponse(res, { success: false, hasCSV: false, error: 'Path is not a directory' });
    }

    const files = fs.readdirSync(normalizedPath);
    const hasCSV = files.some(file => file.toLowerCase().endsWith('.csv'));

    writeLog(`[Validate Folder] Success: Found ${files.length} files, hasCSV: ${hasCSV}`);
    apiResponse(res, { success: true, hasCSV });
  } catch (error) {
    writeLog(`[Validate Folder] Exception: ${error.message}`);
    apiResponse(res, { success: false, hasCSV: false, error: error.message });
  }
});

// Open folder picker dialog
router.post('/select-folder', async (req, res) => {
  try {
    writeLog('Opening folder picker dialog...');

    // Create a temporary PowerShell script
    const tempScriptPath = path.join(os.tmpdir(), `folder-picker-${Date.now()}.ps1`);
    const psScript = `
Add-Type -AssemblyName System.Windows.Forms
$FolderBrowser = New-Object System.Windows.Forms.FolderBrowserDialog
$FolderBrowser.Description = 'Select Roster Folder'
$FolderBrowser.ShowNewFolderButton = $false
$result = $FolderBrowser.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $FolderBrowser.SelectedPath
}
`;

    // Write the script to a temporary file
    fs.writeFileSync(tempScriptPath, psScript, 'utf8');

    // Execute the script
    exec(`powershell -NoProfile -ExecutionPolicy Bypass -Sta -File "${tempScriptPath}"`,
      {
        maxBuffer: 10 * 1024 * 1024,
        windowsHide: false
      },
      (error, stdout, stderr) => {
        // Clean up the temporary script
        try {
          fs.unlinkSync(tempScriptPath);
        } catch (cleanupError) {
          writeLog(`Failed to delete temp script: ${cleanupError.message}`, true);
        }

        const selectedPath = stdout.trim();

        writeLog(`Folder picker result: ${selectedPath || 'cancelled'}`);

        if (stderr) {
          writeLog(`Folder picker stderr: ${stderr}`, true);
        }

        if (selectedPath) {
          writeLog(`Selected folder: ${selectedPath}`);
          apiResponse(res, { success: true, folderPath: selectedPath });
        } else {
          writeLog('No folder selected or dialog cancelled');
          apiResponse(res, { success: false, error: 'No folder selected' });
        }
      }
    );
  } catch (error) {
    writeLog(`Folder picker error: ${error.message}`, true);
    apiResponse(res, { success: false, error: error.message });
  }
});

module.exports = router;
