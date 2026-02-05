/**
 * System routes
 * Handles test, config, kill-processes, and SSE log stream endpoints
 */

const express = require('express');
const { exec } = require('child_process');

const router = express.Router();

const { loadConfig, saveConfig } = require('../config');
const sseLogger = require('../../sse-logger');

// Standard API response helper
function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

// SSE log stream endpoint
router.get('/logs/stream', sseLogger.handleSseConnection);

// Test endpoint
router.get('/test', (req, res) => {
  apiResponse(res, { success: true, message: 'Backend server is running!' });
});

// Config endpoints
router.get('/config', (req, res) => {
  apiResponse(res, { success: true, config: loadConfig() });
});

router.post('/config', (req, res) => {
  const success = saveConfig(req.body);
  apiResponse(res, { success, config: success ? req.body : null, error: success ? null : 'Failed to save config' });
});

// Kill all Node processes
router.post('/kill-processes', async (req, res) => {
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

module.exports = router;
