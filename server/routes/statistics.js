const express = require('express');
const router = express.Router();
const { runPythonScript } = require('../python-runner');

// Standard API response helper
function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

// Load statistics for a class
router.post('/load', async (req, res) => {
  try {
    const { className } = req.body;

    if (!className) {
      return apiResponse(res, { success: false, error: 'Class name is required' });
    }

    const result = await runPythonScript('statistics_cli.py', ['load', className]);

    apiResponse(res, {
      success: result.success,
      statistics: result.statistics || {},
      students: result.students || [],
      ...(result.success ? {} : { error: result.error || 'Failed to load statistics' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Save statistics for a class
router.post('/save', async (req, res) => {
  try {
    const { className, statistics } = req.body;

    if (!className) {
      return apiResponse(res, { success: false, error: 'Class name is required' });
    }

    if (!statistics) {
      return apiResponse(res, { success: false, error: 'Statistics data is required' });
    }

    const statsJson = JSON.stringify(statistics);
    const result = await runPythonScript('statistics_cli.py', ['save', className, statsJson]);

    apiResponse(res, {
      success: result.success,
      message: result.message,
      ...(result.success ? {} : { error: result.error || 'Failed to save statistics' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Update student notes
router.post('/update-notes', async (req, res) => {
  try {
    const { className, studentName, notes } = req.body;

    if (!className) {
      return apiResponse(res, { success: false, error: 'Class name is required' });
    }

    if (!studentName) {
      return apiResponse(res, { success: false, error: 'Student name is required' });
    }

    const result = await runPythonScript('statistics_cli.py', [
      'update-notes',
      className,
      studentName,
      notes || ''
    ]);

    apiResponse(res, {
      success: result.success,
      message: result.message,
      ...(result.success ? {} : { error: result.error || 'Failed to update notes' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Update failed submission count
router.post('/update-count', async (req, res) => {
  try {
    const { className, studentName, count } = req.body;

    if (!className) {
      return apiResponse(res, { success: false, error: 'Class name is required' });
    }

    if (!studentName) {
      return apiResponse(res, { success: false, error: 'Student name is required' });
    }

    if (typeof count !== 'number') {
      return apiResponse(res, { success: false, error: 'Count must be a number' });
    }

    const result = await runPythonScript('statistics_cli.py', [
      'update-count',
      className,
      studentName,
      count.toString()
    ]);

    apiResponse(res, {
      success: result.success,
      message: result.message,
      ...(result.success ? {} : { error: result.error || 'Failed to update count' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

module.exports = router;
