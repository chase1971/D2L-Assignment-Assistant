/**
 * Patch management routes
 * Handles all /api/patches/* endpoints
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { exec } = require('child_process');

const router = express.Router();

const patchManager = require('../../patch-manager');
const { writeLog } = require('../python-runner');

// Standard API response helper
function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

// Get patch status
router.get('/status', async (req, res) => {
  try {
    const status = patchManager.getPatchStatus();
    apiResponse(res, { success: true, ...status });
  } catch (error) {
    writeLog(`[Patch Status] Error: ${error.message}`, true);
    apiResponse(res, { success: false, error: error.message });
  }
});

// Import patch file (multer middleware applied in app.js)
router.post('/import', async (req, res) => {
  try {
    if (!req.file) {
      return apiResponse(res, { success: false, error: 'No patch file provided' });
    }

    writeLog(`[Patch Import] Importing patch from: ${req.file.originalname}`);

    // The file is already uploaded to temp directory by multer
    const result = await patchManager.importPatchFile(req.file.path);

    // Clean up uploaded file
    try {
      fs.unlinkSync(req.file.path);
    } catch (cleanupError) {
      writeLog(`[Patch Import] Failed to delete temp file: ${cleanupError.message}`, true);
    }

    apiResponse(res, result);
  } catch (error) {
    writeLog(`[Patch Import] Error: ${error.message}`, true);
    apiResponse(res, { success: false, error: error.message });
  }
});

// Select patch file from file system
router.post('/select-file', async (req, res) => {
  try {
    writeLog('Opening patch file picker...');

    // Create a temporary PowerShell script for file picker
    const tempScriptPath = path.join(os.tmpdir(), `patch-picker-${Date.now()}.ps1`);
    const psScript = `
Add-Type -AssemblyName System.Windows.Forms
$FileBrowser = New-Object System.Windows.Forms.OpenFileDialog
$FileBrowser.Filter = 'Patch Files (*.zip)|*.zip|All Files (*.*)|*.*'
$FileBrowser.Title = 'Select Patch File'
$result = $FileBrowser.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $FileBrowser.FileName
}
`;

    // Write and execute the script
    fs.writeFileSync(tempScriptPath, psScript, 'utf8');

    exec(`powershell -NoProfile -ExecutionPolicy Bypass -Sta -File "${tempScriptPath}"`,
      { maxBuffer: 10 * 1024 * 1024, windowsHide: false },
      async (error, stdout, stderr) => {
        // Clean up temp script
        try {
          fs.unlinkSync(tempScriptPath);
        } catch (cleanupError) {
          writeLog(`Failed to delete temp script: ${cleanupError.message}`, true);
        }

        const selectedPath = stdout.trim();

        if (error || !selectedPath) {
          writeLog('Patch file selection cancelled or failed');
          return apiResponse(res, { success: false, error: 'No file selected' });
        }

        writeLog(`Selected patch file: ${selectedPath}`);

        // Import the patch
        const result = await patchManager.importPatchFile(selectedPath);
        apiResponse(res, result);
      }
    );
  } catch (error) {
    writeLog(`[Patch Select] Error: ${error.message}`, true);
    apiResponse(res, { success: false, error: error.message });
  }
});

// Clear all patches
router.post('/clear', async (req, res) => {
  try {
    writeLog('Clearing all patches...');
    const result = patchManager.clearAllPatches();
    apiResponse(res, result);
  } catch (error) {
    writeLog(`[Patch Clear] Error: ${error.message}`, true);
    apiResponse(res, { success: false, error: error.message });
  }
});

module.exports = router;
