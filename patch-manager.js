/**
 * Patch Management System for D2L Assignment Assistant
 * 
 * Allows loading patched scripts from user's AppData folder.
 * Patched scripts override bundled scripts, enabling bug fixes
 * and updates without reinstalling the app.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

// Patch directory in user's AppData
const PATCH_DIR = path.join(
  os.homedir(),
  'AppData',
  'Roaming',
  'D2L Assignment Assistant',
  'patches'
);

const PATCH_METADATA_FILE = path.join(PATCH_DIR, 'patch-info.json');

/**
 * Ensure patch directory exists
 */
function ensurePatchDirectory() {
  if (!fs.existsSync(PATCH_DIR)) {
    fs.mkdirSync(PATCH_DIR, { recursive: true });
    console.log(`[Patch Manager] Created patch directory: ${PATCH_DIR}`);
  }
}

/**
 * Get patched script path if exists, otherwise return bundled path
 * @param {string} bundledScriptsPath - Path to bundled scripts directory
 * @param {string} scriptName - Name of script (e.g., 'process_quiz_cli.py')
 * @returns {object} - { path: string, isPatched: boolean }
 */
function getScriptPath(bundledScriptsPath, scriptName) {
  ensurePatchDirectory();
  
  const patchedPath = path.join(PATCH_DIR, 'scripts', scriptName);
  const bundledPath = path.join(bundledScriptsPath, scriptName);
  
  // Check if patched version exists
  if (fs.existsSync(patchedPath)) {
    console.log(`[Patch Manager] Using PATCHED script: ${scriptName}`);
    return { path: patchedPath, isPatched: true };
  }
  
  // Fall back to bundled version
  return { path: bundledPath, isPatched: false };
}

/**
 * Get patched python-modules path if exists, otherwise return bundled path
 * @param {string} bundledScriptsPath - Path to bundled scripts directory
 * @param {string} modulePath - Relative path within python-modules (e.g., 'submission_processor.py')
 * @returns {object} - { path: string, isPatched: boolean }
 */
function getPythonModulePath(bundledScriptsPath, modulePath) {
  ensurePatchDirectory();
  
  const patchedPath = path.join(PATCH_DIR, 'scripts', 'python-modules', modulePath);
  const bundledPath = path.join(bundledScriptsPath, 'python-modules', modulePath);
  
  // Check if patched version exists
  if (fs.existsSync(patchedPath)) {
    console.log(`[Patch Manager] Using PATCHED module: python-modules/${modulePath}`);
    return { path: patchedPath, isPatched: true };
  }
  
  // Fall back to bundled version
  return { path: bundledPath, isPatched: false };
}

/**
 * Get working directory for Python scripts
 * If any patches are active, use patch directory, otherwise use bundled directory
 * @param {string} bundledScriptsPath - Path to bundled scripts directory
 * @returns {string} - Working directory path
 */
function getWorkingDirectory(bundledScriptsPath) {
  const patchScriptsDir = path.join(PATCH_DIR, 'scripts');
  
  // If patch scripts directory exists and has files, use it as cwd
  if (fs.existsSync(patchScriptsDir)) {
    const files = fs.readdirSync(patchScriptsDir);
    if (files.length > 0) {
      console.log(`[Patch Manager] Using patch directory as cwd`);
      return patchScriptsDir;
    }
  }
  
  return bundledScriptsPath;
}

/**
 * Import a patch file (.zip containing scripts and python-modules)
 * @param {string} patchFilePath - Path to patch zip file
 * @returns {Promise<object>} - { success: boolean, message: string, filesUpdated: string[] }
 */
async function importPatchFile(patchFilePath) {
  ensurePatchDirectory();
  
  try {
    console.log(`[Patch Manager] Importing patch from: ${patchFilePath}`);
    
    // Check if file exists
    if (!fs.existsSync(patchFilePath)) {
      return { success: false, message: 'Patch file not found' };
    }
    
    // Extract using PowerShell (built into Windows, no dependencies)
    const extractCmd = `powershell -Command "Expand-Archive -Path '${patchFilePath}' -DestinationPath '${PATCH_DIR}' -Force"`;
    
    await execPromise(extractCmd);
    
    // Read patch metadata if included
    let metadata = {
      version: 'unknown',
      date: new Date().toISOString(),
      description: 'Imported patch',
      files: []
    };
    
    const metadataPath = path.join(PATCH_DIR, 'patch-metadata.json');
    if (fs.existsSync(metadataPath)) {
      metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
      console.log(`[Patch Manager] Patch version: ${metadata.version}`);
      console.log(`[Patch Manager] Description: ${metadata.description}`);
    }
    
    // List extracted files
    const extractedFiles = listPatchedFiles();
    
    // Save patch info
    savePatchInfo({
      lastImported: new Date().toISOString(),
      importedFrom: path.basename(patchFilePath),
      ...metadata
    });
    
    return {
      success: true,
      message: `Patch imported successfully (${extractedFiles.length} files)`,
      filesUpdated: extractedFiles,
      metadata
    };
    
  } catch (error) {
    console.error(`[Patch Manager] Error importing patch:`, error);
    return {
      success: false,
      message: `Failed to import patch: ${error.message}`
    };
  }
}

/**
 * List all patched files
 * @returns {string[]} - Array of patched file paths (relative to patch dir)
 */
function listPatchedFiles() {
  ensurePatchDirectory();
  
  const patchedFiles = [];
  const scriptsDir = path.join(PATCH_DIR, 'scripts');
  
  if (fs.existsSync(scriptsDir)) {
    // Recursively find all .py files
    const findFiles = (dir, baseDir) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          findFiles(fullPath, baseDir);
        } else if (entry.name.endsWith('.py') || entry.name.endsWith('.json')) {
          const relativePath = path.relative(baseDir, fullPath);
          patchedFiles.push(relativePath);
        }
      }
    };
    
    findFiles(scriptsDir, scriptsDir);
  }
  
  return patchedFiles;
}

/**
 * Get patch information
 * @returns {object|null} - Patch metadata or null
 */
function getPatchInfo() {
  if (fs.existsSync(PATCH_METADATA_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(PATCH_METADATA_FILE, 'utf8'));
    } catch (error) {
      console.error('[Patch Manager] Error reading patch info:', error);
      return null;
    }
  }
  return null;
}

/**
 * Save patch information
 * @param {object} info - Patch metadata
 */
function savePatchInfo(info) {
  try {
    fs.writeFileSync(PATCH_METADATA_FILE, JSON.stringify(info, null, 2), 'utf8');
  } catch (error) {
    console.error('[Patch Manager] Error saving patch info:', error);
  }
}

/**
 * Clear all patches (restore to bundled versions)
 * @returns {object} - { success: boolean, message: string }
 */
function clearAllPatches() {
  try {
    const patchedFiles = listPatchedFiles();
    
    // Remove scripts directory
    const scriptsDir = path.join(PATCH_DIR, 'scripts');
    if (fs.existsSync(scriptsDir)) {
      fs.rmSync(scriptsDir, { recursive: true, force: true });
    }
    
    // Remove metadata
    if (fs.existsSync(PATCH_METADATA_FILE)) {
      fs.unlinkSync(PATCH_METADATA_FILE);
    }
    
    console.log(`[Patch Manager] Cleared ${patchedFiles.length} patched files`);
    
    return {
      success: true,
      message: `Cleared ${patchedFiles.length} patched files. Restart to use bundled versions.`,
      filesCleared: patchedFiles
    };
  } catch (error) {
    console.error('[Patch Manager] Error clearing patches:', error);
    return {
      success: false,
      message: `Failed to clear patches: ${error.message}`
    };
  }
}

/**
 * Get patch status
 * @returns {object} - Status information
 */
function getPatchStatus() {
  const patchedFiles = listPatchedFiles();
  const info = getPatchInfo();
  
  return {
    hasPatch: patchedFiles.length > 0,
    patchedFilesCount: patchedFiles.length,
    patchedFiles: patchedFiles,
    patchInfo: info,
    patchDirectory: PATCH_DIR
  };
}

module.exports = {
  getScriptPath,
  getPythonModulePath,
  getWorkingDirectory,
  importPatchFile,
  listPatchedFiles,
  getPatchInfo,
  clearAllPatches,
  getPatchStatus,
  PATCH_DIR
};
