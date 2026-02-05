/**
 * File operation routes
 * Handles file opening, PDF viewing, email student loading
 */

const express = require('express');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { exec } = require('child_process');

const router = express.Router();

const { loadConfig } = require('../config');
const { writeLog } = require('../python-runner');
const { findPdfsFolder } = require('../helpers/file-paths');
const { parseCSVLine } = require('../helpers/csv-parser');

// Standard API response helper
function apiResponse(res, { success, logs = [], error = null, ...extra }) {
  res.json({ success, logs, error: success ? null : error, ...extra });
}

// Open a specific file (PDF, Excel, etc.)
router.post('/open-file', async (req, res) => {
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

// Load students from import file for email functionality
router.post('/load-students-for-email', async (req, res) => {
  try {
    const { drive, className, assignmentName } = req.body;

    if (!drive || !className) {
      return apiResponse(res, { success: false, error: 'Missing required parameters' });
    }

    // Find import file using helper
    const folders = findPdfsFolder(drive, className);
    if (!folders) {
      writeLog(`Class folder not found for drive: ${drive}, className: ${className}`, true);
      return apiResponse(res, { success: false, error: 'Class folder not found' });
    }

    const { importFilePath } = folders;

    // Check for both "Import File.csv" and "import.csv"
    let actualImportPath = importFilePath;
    if (!fs.existsSync(actualImportPath)) {
      // Try "import.csv" instead
      const altPath = importFilePath.replace(/Import File\.csv$/i, 'import.csv');
      if (fs.existsSync(altPath)) {
        actualImportPath = altPath;
      } else {
        writeLog(`Import file not found at either location`, true);
        return apiResponse(res, { success: false, error: `Import file not found. Checked: ${importFilePath} and ${altPath}` });
      }
    }

    // Read and parse CSV (handle quoted fields properly)
    const csvContent = fs.readFileSync(actualImportPath, 'utf8');
    const lines = csvContent.split(/\r?\n/).filter(line => line.trim());

    if (lines.length < 2) {
      return apiResponse(res, { success: false, error: 'Import file is empty or invalid' });
    }

    // Parse header
    const header = parseCSVLine(lines[0]).map(h => h.replace(/^"|"$/g, ''));
    const firstNameIdx = header.findIndex(h => h.toLowerCase() === 'first name');
    const lastNameIdx = header.findIndex(h => h.toLowerCase() === 'last name');
    const emailIdx = header.findIndex(h => h.toLowerCase() === 'email');

    if (firstNameIdx === -1 || lastNameIdx === -1) {
      return apiResponse(res, { success: false, error: 'Import file missing required columns (First Name, Last Name)' });
    }

    // Find assignment column if assignmentName is provided
    let assignmentColumnIdx = -1;
    if (assignmentName) {
      const assignmentColumnName = `${assignmentName} Points Grade`;

      assignmentColumnIdx = header.findIndex(h => h.toLowerCase() === assignmentColumnName.toLowerCase());

      if (assignmentColumnIdx === -1) {
        // Try to find any column that contains the assignment name
        const partialMatch = header.findIndex(h =>
          h.toLowerCase().includes(assignmentName.toLowerCase()) &&
          h.toLowerCase().includes('points grade')
        );
        if (partialMatch !== -1) {
          assignmentColumnIdx = partialMatch;
        } else {
          // Try just the assignment name without " Points Grade"
          const nameOnlyMatch = header.findIndex(h =>
            h.toLowerCase().trim() === assignmentName.toLowerCase().trim()
          );
          if (nameOnlyMatch !== -1) {
            assignmentColumnIdx = nameOnlyMatch;
          }
        }
      }
    }

    // Parse student rows
    const students = [];
    for (let i = 1; i < lines.length; i++) {
      const row = parseCSVLine(lines[i]).map(c => c.replace(/^"|"$/g, ''));

      if (row.length <= Math.max(firstNameIdx, lastNameIdx)) continue;

      const firstName = row[firstNameIdx] || '';
      const lastName = row[lastNameIdx] || '';

      // Skip empty rows
      if (!firstName.trim() || !lastName.trim()) continue;

      const fullName = `${firstName.trim()} ${lastName.trim()}`;
      const email = emailIdx !== -1 && row[emailIdx] ? row[emailIdx].trim() : undefined;

      // Check if student has assignment (has a value in the assignment column)
      let hasAssignment = false;
      let isUnreadable = false;
      if (assignmentColumnIdx !== -1 && row.length > assignmentColumnIdx) {
        const assignmentValue = row[assignmentColumnIdx] || '';
        const trimmedValue = assignmentValue.trim();
        const trimmedValueLower = trimmedValue.toLowerCase();

        // Check if it's unreadable
        isUnreadable = trimmedValueLower === 'unreadable';
        // A student has an assignment if the value is not empty, not "0", and not "unreadable"
        hasAssignment = trimmedValue !== '' &&
                       trimmedValue !== '0' &&
                       !isUnreadable &&
                       trimmedValueLower !== 'nan' &&
                       trimmedValueLower !== 'none';
      } else if (assignmentColumnIdx === -1 && assignmentName) {
        // If assignment column not found but assignment name was provided,
        // we can't determine submission status, so default to false
        hasAssignment = false;
      }

      students.push({
        name: fullName,
        email: email,
        hasAssignment: hasAssignment,
        isUnreadable: isUnreadable
      });
    }

    return apiResponse(res, {
      success: true,
      students: students,
      assignmentName: assignmentName || null
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Launch Firefox with Outlook URL
router.post('/launch-firefox-outlook', async (req, res) => {
  try {
    const firefoxPath = 'C:\\Program Files\\Mozilla Firefox\\firefox.exe';
    const outlookUrl = 'https://outlook.office.com/mail/';

    // Check if Firefox exists
    if (!fs.existsSync(firefoxPath)) {
      return apiResponse(res, { success: false, error: 'Firefox not found at expected path' });
    }

    writeLog(`Launching Firefox with Outlook URL...`);

    // Launch Firefox with the Outlook URL
    exec(`"${firefoxPath}" "${outlookUrl}"`, (error) => {
      if (error) {
        writeLog(`Error launching Firefox: ${error.message}`, true);
        apiResponse(res, { success: false, error: error.message });
      } else {
        apiResponse(res, { success: true, message: 'Firefox launched' });
      }
    });
  } catch (error) {
    apiResponse(res, { success: false, error: error.message });
  }
});

// Open student's individual PDF
router.post('/open-student-pdf', async (req, res) => {
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
router.post('/open-combined-pdf', async (req, res) => {
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
router.post('/open-import-file', async (req, res) => {
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

module.exports = router;
