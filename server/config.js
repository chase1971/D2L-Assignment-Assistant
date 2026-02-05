/**
 * Configuration management
 */

const path = require('path');
const fs = require('fs');
const os = require('os');

// Config file path (same directory as the project root)
const CONFIG_PATH = path.join(__dirname, '..', 'config.json');

// Python scripts path
// In packaged app: scripts are in resources/scripts (via extraResources)
// In development: scripts are in scripts/ subdirectory
const SCRIPTS_PATH = process.resourcesPath
  ? path.join(process.resourcesPath, 'scripts')
  : path.join(__dirname, '..', 'scripts');

function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    }
  } catch (error) {
    const timestamp = new Date().toISOString();
    console.log(`${timestamp} [ERROR] Error loading config: ${error.message}`);
  }

  // Default config
  return {
    downloadsPath: path.join(os.homedir(), 'Downloads'),
    rostersPath: path.join('C:', 'Rosters etc'),
    developerMode: true
  };
}

function saveConfig(config) {
  try {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
    return true;
  } catch (error) {
    const timestamp = new Date().toISOString();
    console.log(`${timestamp} [ERROR] Error saving config: ${error.message}`);
    return false;
  }
}

module.exports = { CONFIG_PATH, SCRIPTS_PATH, loadConfig, saveConfig };
