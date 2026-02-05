/**
 * File path resolution helpers for rosters, class folders, and PDFs
 */

const path = require('path');
const fs = require('fs');
const os = require('os');

// Get possible rosters paths (mirrors Python config_reader.py logic)
function getPossibleRostersPaths(drive) {
  const username = os.userInfo().username;
  // Use proper Windows path format with backslashes
  // Check both C and G drives
  const paths = [
    `${drive}:\\Users\\${username}\\My Drive\\Rosters etc`,  // Standard path: C:\Users\chase\My Drive\Rosters etc
    `${drive}:\\${username}\\My Drive\\Rosters etc`,  // Alternative: C:\chase\My Drive\Rosters etc
    `${drive}:\\My Drive\\Rosters etc`,  // Direct: C:\My Drive\Rosters etc
  ];

  // Also add G drive path if checking C drive
  if (drive === 'C') {
    paths.push(`G:\\My Drive\\Rosters etc`);  // G drive path: G:\My Drive\Rosters etc
  }

  // Add home directory path
  paths.push(path.join(os.homedir(), 'My Drive', 'Rosters etc'));  // From home directory

  return paths;
}

// Find class folder in any of the possible rosters paths
// Checks both C and G drives automatically
function findClassFolder(drive, className) {
  // Try both C and G drives
  const drivesToCheck = ['C', 'G'];

  for (const checkDrive of drivesToCheck) {
    const possiblePaths = getPossibleRostersPaths(checkDrive);

    for (const rostersPath of possiblePaths) {
      // Use path.join for cross-platform compatibility, but handle Windows drive paths
      const classFolder = rostersPath.includes(':\\')
        ? `${rostersPath}\\${className}`  // Windows absolute path
        : path.join(rostersPath, className);  // Relative or home directory path

      if (fs.existsSync(classFolder)) {
        return { rostersPath, classFolder };
      }
    }
  }
  return null;
}

// Find the most recent "grade processing" folder within a class folder
function findMostRecentProcessingFolder(classFolder) {
  try {
    if (!fs.existsSync(classFolder)) return null;

    const folders = fs.readdirSync(classFolder);
    const processingFolders = [];

    for (const folderName of folders) {
      const folderPath = path.join(classFolder, folderName);
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
      return processingFolders[0].path;
    }
  } catch (error) {
    console.error('Error finding processing folder:', error);
  }

  return null;
}

// Find PDFs folder for a class
function findPdfsFolder(drive, className) {
  const result = findClassFolder(drive, className);
  if (!result) return null;

  // Use proper path joining for Windows
  const separator = result.classFolder.includes(':\\') ? '\\' : path.sep;
  // Check for both "Import File.csv" and "import.csv"
  let importFilePath = `${result.classFolder}${separator}Import File.csv`;
  if (!fs.existsSync(importFilePath)) {
    const altPath = `${result.classFolder}${separator}import.csv`;
    if (fs.existsSync(altPath)) {
      importFilePath = altPath;
    }
  }

  // Find the most recent "grade processing [CLASS_CODE] [ASSIGNMENT]" folder
  let pdfsFolder = null;
  let processingFolder = null;

  const mostRecent = findMostRecentProcessingFolder(result.classFolder);
  if (mostRecent) {
    processingFolder = mostRecent;
    pdfsFolder = path.join(processingFolder, 'PDFs');
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

module.exports = {
  getPossibleRostersPaths,
  findClassFolder,
  findMostRecentProcessingFolder,
  findPdfsFolder
};
