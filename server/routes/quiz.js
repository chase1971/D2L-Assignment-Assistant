/**
 * Quiz processing routes
 * Handles all /api/quiz/* endpoints
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { exec } = require('child_process');

const router = express.Router();

const { loadConfig } = require('../config');
const { runPythonScript, writeLog } = require('../python-runner');
const { validateClassName } = require('../helpers/validation');
const { getPossibleRostersPaths, findClassFolder, findPdfsFolder, findMostRecentProcessingFolder } = require('../helpers/file-paths');
const { getUserLogs, parseZipFilesFromOutput } = require('../helpers/log-parser');
const sseLogger = require('../../sse-logger');

// Standard API response helper
function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

// List classes
router.post('/list-classes', async (req, res) => {
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

// Process quiz
router.post('/process', async (req, res) => {
  try {
    const { drive, className } = req.body;

    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }

    // Broadcast process start
    sseLogger.broadcastProcessStart('process-quiz', { className });

    const result = await runPythonScript('process_quiz_cli.py', [drive || 'C', className]);

    // Broadcast process complete
    sseLogger.broadcastProcessComplete('process-quiz', result.success);

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
    sseLogger.broadcastProcessComplete('process-quiz', false, { error: error.message });
    apiResponse(res, { success: false, error: error.message });
  }
});

// Process selected quiz (specific ZIP)
router.post('/process-selected', async (req, res) => {
  try {
    const { drive, className, zipPath } = req.body;

    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }

    sseLogger.broadcastProcessStart('process-quiz-selected', { className });

    const result = await runPythonScript('process_quiz_cli.py', [drive || 'C', className, zipPath]);

    sseLogger.broadcastProcessComplete('process-quiz-selected', result.success);

    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      combined_pdf_path: result.data?.combined_pdf_path,
      assignment_name: result.data?.assignment_name,
      ...(result.success ? {} : { error: result.error || 'Processing failed' })
    });
  } catch (error) {
    sseLogger.broadcastProcessComplete('process-quiz-selected', false, { error: error.message });
    apiResponse(res, { success: false, error: error.message });
  }
});

// Process completion
router.post('/process-completion', async (req, res) => {
  try {
    const { drive, className, dontOverride } = req.body;

    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }

    const args = [drive || 'C', className];
    if (dontOverride) args.push('--dont-override');

    sseLogger.broadcastProcessStart('process-completion', { className });

    const result = await runPythonScript('process_completion_cli.py', args);

    sseLogger.broadcastProcessComplete('process-completion', result.success);

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
    sseLogger.broadcastProcessComplete('process-completion', false, { error: error.message });
    apiResponse(res, { success: false, error: error.message });
  }
});

// Process completion with selected ZIP
router.post('/process-completion-selected', async (req, res) => {
  try {
    const { drive, className, zipPath, dontOverride } = req.body;

    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }

    const args = [drive || 'C', className, zipPath];
    if (dontOverride) args.push('--dont-override');

    sseLogger.broadcastProcessStart('process-completion-selected', { className });

    const result = await runPythonScript('process_completion_cli.py', args);

    sseLogger.broadcastProcessComplete('process-completion-selected', result.success);

    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      combined_pdf_path: result.data?.combined_pdf_path,
      assignment_name: result.data?.assignment_name,
      ...(result.success ? {} : { error: result.error || 'Processing failed' })
    });
  } catch (error) {
    sseLogger.broadcastProcessComplete('process-completion-selected', false, { error: error.message });
    apiResponse(res, { success: false, error: error.message });
  }
});

// Extract grades
router.post('/extract-grades', async (req, res) => {
  try {
    const { drive, className, pdfPath } = req.body;

    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }

    // Pass pdfPath as optional third argument if provided
    const args = [drive || 'C', className];
    if (pdfPath) {
      args.push(pdfPath);
    }

    sseLogger.broadcastProcessStart('extract-grades', { className });

    const result = await runPythonScript('extract_grades_cli.py', args);

    sseLogger.broadcastProcessComplete('extract-grades', result.success);

    // Always use userLogs if available (they're already parsed from [LOG:LEVEL] format)
    let logs = [];
    let error = null;
    let success = result.success;

    if (result.userLogs && result.userLogs.length > 0) {
      // Convert userLogs array of {level, message} objects to strings for frontend
      logs = result.userLogs.map(log => log.message || log);
    } else {
      // Fallback: parse output manually
      logs = result.output.split('\n')
        .filter(l => {
          const trimmed = l.trim();
          return trimmed &&
                 !trimmed.startsWith('[DEV]') &&
                 !trimmed.startsWith('{') &&
                 !trimmed.match(/^\[LOG:/); // Skip raw [LOG:LEVEL] lines (already parsed)
        })
        .map(l => {
          const trimmed = l.trim();
          // Extract message from [LOG:LEVEL] format if needed
          const logMatch = trimmed.match(/^\[LOG:(SUCCESS|ERROR|WARNING|INFO)\] (.+)$/);
          if (logMatch) {
            return logMatch[2];
          }
          if (trimmed.startsWith('[USER]')) {
            return trimmed.substring(7);
          }
          return trimmed;
        });
    }

    if (!result.success) {
      error = result.error || 'Extraction failed';
    }

    // Extract confidence scores and assignment info from JSON response if available
    let confidenceScores = null;
    let assignmentName = null;
    let resultPdfPath = null;
    try {
      const trimmedOutput = result.output.trim();
      // Look for JSON at the end of output (after all logs)
      const jsonMatch = trimmedOutput.match(/\{[\s\S]*"confidenceScores"[\s\S]*\}/);
      if (jsonMatch) {
        const jsonData = JSON.parse(jsonMatch[0]);
        if (jsonData.confidenceScores) {
          confidenceScores = jsonData.confidenceScores;
        }
        if (jsonData.assignmentName) {
          assignmentName = jsonData.assignmentName;
        }
        if (jsonData.pdfPath) {
          resultPdfPath = jsonData.pdfPath;
        }
        // Also update success from JSON if available
        if (jsonData.success !== undefined) {
          success = jsonData.success !== false;
        }
      }
    } catch (parseError) {
      // Ignore parse errors for confidence scores
    }

    // Send both logs (for compatibility) and userLogs (for new format)
    // Convert logs array to userLogs format if needed
    const userLogs = result.userLogs && result.userLogs.length > 0
      ? result.userLogs.map(log => typeof log === 'string' ? { level: 'INFO', message: log } : log)
      : logs.map(log => typeof log === 'string' ? { level: 'INFO', message: log } : log);

    apiResponse(res, {
      success,
      logs,  // Keep for backward compatibility
      userLogs,  // New format with level info
      ...(confidenceScores ? { confidenceScores } : {}),
      ...(assignmentName ? { assignmentName } : {}),
      ...(resultPdfPath ? { pdfPath: resultPdfPath } : {}),
      ...(success ? {} : { error: error || 'Extraction failed' })
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Split PDF upload (with multer middleware passed from app.js)
router.post('/split-pdf-upload', async (req, res) => {
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

// Split PDF (from existing file)
router.post('/split-pdf', async (req, res) => {
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

    sseLogger.broadcastProcessStart('split-pdf', { className });

    const result = await runPythonScript('split_pdf_cli.py', args);

    sseLogger.broadcastProcessComplete('split-pdf', result.success);

    apiResponse(res, {
      success: result.success,
      logs: getUserLogs(result),
      ...(result.success ? {} : { error: result.error || 'Split failed' })
    });
  } catch (error) {
    sseLogger.broadcastProcessComplete('split-pdf', false, { error: error.message });
    apiResponse(res, { success: false, error: error.message });
  }
});

// Get PDFs folder
router.post('/get-pdfs-folder', async (req, res) => {
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
      // Check both C and G drives
      const drivesToCheck = ['C', 'G'];
      let existingRostersPath = null;

      for (const checkDrive of drivesToCheck) {
        const possiblePaths = getPossibleRostersPaths(checkDrive);
        for (const rostersPath of possiblePaths) {
          if (fs.existsSync(rostersPath)) {
            existingRostersPath = rostersPath;
            break;
          }
        }
        if (existingRostersPath) break;
      }

      if (existingRostersPath) {
        // Try to find the most recent grade processing folder
        const separator = existingRostersPath.includes(':\\') ? '\\' : path.sep;
        const classFolderPath = path.join(existingRostersPath, className);
        let constructedPath = null;
        let existingPath = existingRostersPath;

        const mostRecent = findMostRecentProcessingFolder(classFolderPath);
        if (mostRecent) {
          constructedPath = path.join(mostRecent, 'PDFs');
          existingPath = mostRecent;
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

// Open folder
router.post('/open-folder', async (req, res) => {
  try {
    const { drive, className, classFolderOnly } = req.body;

    // Handle DOWNLOADS special case
    if (className === 'DOWNLOADS') {
      // No validation needed for special DOWNLOADS case
      const downloadsPath = loadConfig().downloadsPath || path.join(os.homedir(), 'Downloads');
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

// Clear data
router.post('/clear-data', async (req, res) => {
  try {
    const { drive, className, assignmentName, saveFoldersAndPdf, saveCombinedPdf, deleteEverything, deleteArchivedToo } = req.body;

    if (!validateClassName(className)) {
      return apiResponse(res, { success: false, error: 'Invalid class name' });
    }

    if (!assignmentName) {
      return apiResponse(res, { success: false, error: 'Assignment name required' });
    }

    const args = [drive || 'C', className, assignmentName];
    if (saveFoldersAndPdf) {
      args.push('--save-folders-and-pdf');
    } else if (saveCombinedPdf) {
      args.push('--save-combined-pdf');
    } else if (deleteEverything) {
      args.push('--delete-everything');
    } else if (deleteArchivedToo) {
      // deleteAll with deleteArchivedToo=true: also delete archived folder
      args.push('--delete-all-with-archived');
    }
    // else default is --delete-all (only deletes processing folder, keeps archived)

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

// List processing folders
router.post('/list-processing-folders', async (req, res) => {
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

// Clear archived data
router.post('/clear-archived-data', async (req, res) => {
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

module.exports = router;
