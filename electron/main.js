/**
 * D2L Assignment Assistant - Electron Main Process
 * 
 * This file handles the Electron window and starts the backend server.
 */

const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn, fork, exec } = require('child_process');
const { autoUpdater } = require('electron-updater');

let mainWindow = null;
let serverProcess = null;

// Determine if we're in development or production
const isDev = !app.isPackaged;

// Configure auto-updater
autoUpdater.autoDownload = false; // Don't auto-download, let user decide
autoUpdater.autoInstallOnAppQuit = true; // Install when app closes

// Auto-updater event handlers
autoUpdater.on('checking-for-update', () => {
  console.log('Checking for updates...');
});

autoUpdater.on('update-available', (info) => {
  console.log('Update available:', info.version);
  if (mainWindow) {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Available',
      message: `Version ${info.version} is available!`,
      detail: 'Would you like to download and install it?',
      buttons: ['Download & Install', 'Later']
    }).then(result => {
      if (result.response === 0) {
        autoUpdater.downloadUpdate();
      }
    });
  }
});

autoUpdater.on('update-not-available', (info) => {
  console.log('No updates available. Current version:', info.version);
});

autoUpdater.on('error', (err) => {
  console.error('Update error:', err);
});

autoUpdater.on('download-progress', (progressObj) => {
  console.log(`Download progress: ${progressObj.percent.toFixed(2)}%`);
});

autoUpdater.on('update-downloaded', (info) => {
  console.log('Update downloaded:', info.version);
  if (mainWindow) {
    dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Ready',
      message: `Version ${info.version} has been downloaded`,
      detail: 'The update will be installed when you close the application.',
      buttons: ['Restart Now', 'Later']
    }).then(result => {
      if (result.response === 0) {
        autoUpdater.quitAndInstall();
      }
    });
  }
});

// Check if server is already running (for dev mode with concurrently)
function isServerRunning() {
  return new Promise((resolve) => {
    const http = require('http');
    const req = http.get('http://localhost:5000/api/test', (res) => {
      resolve(true);
    });
    req.on('error', () => {
      resolve(false);
    });
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

// Kill any process using port 5000 before starting (only if server is NOT already running)
function killPort5000() {
  return new Promise(async (resolve) => {
    // In dev mode, if server is already running (started by concurrently), don't kill it
    const serverAlreadyRunning = await isServerRunning();
    if (serverAlreadyRunning) {
      console.log('Server already running on port 5000, skipping port cleanup');
      resolve();
      return;
    }
    
    console.log('Checking for processes on port 5000...');
    
    // Windows command to find and kill process on port 5000
    exec('netstat -ano | findstr :5000', (error, stdout) => {
      if (error || !stdout.trim()) {
        console.log('No process found on port 5000');
        resolve();
        return;
      }
      
      // Parse the PID from netstat output
      const lines = stdout.trim().split('\n');
      const pids = new Set();
      
      lines.forEach(line => {
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid && !isNaN(pid) && pid !== '0') {
          pids.add(pid);
        }
      });
      
      if (pids.size === 0) {
        console.log('No PIDs found to kill');
        resolve();
        return;
      }
      
      console.log(`Found PIDs on port 5000: ${[...pids].join(', ')}`);
      
      // Kill each PID
      let killed = 0;
      pids.forEach(pid => {
        exec(`taskkill /F /PID ${pid}`, (err) => {
          killed++;
          if (err) {
            console.log(`Could not kill PID ${pid}: ${err.message}`);
          } else {
            console.log(`Killed PID ${pid}`);
          }
          
          if (killed === pids.size) {
            // Wait a moment for port to be released
            setTimeout(resolve, 500);
          }
        });
      });
    });
  });
}

// Start the backend server
function startServer() {
  return new Promise((resolve, reject) => {
    const serverPath = isDev 
      ? path.join(__dirname, '..', 'server.js')  // In dev, server.js is in parent of electron/
      : path.join(app.getAppPath(), 'server.js');  // In production, server.js is in app.asar
    
    console.log('Starting server from:', serverPath);
    
    serverProcess = fork(serverPath, [], {
      stdio: ['pipe', 'pipe', 'pipe', 'ipc'],
      env: { ...process.env, ELECTRON_RUN_AS_NODE: '1' }
    });

    serverProcess.stdout.on('data', (data) => {
      console.log(`[Server] ${data}`);
    });

    serverProcess.stderr.on('data', (data) => {
      console.error(`[Server Error] ${data}`);
    });

    serverProcess.on('error', (error) => {
      console.error('Server process error:', error);
      reject(error);
    });

    // Wait a bit for server to start
    setTimeout(() => {
      console.log('Server should be ready');
      resolve();
    }, 2000);
  });
}

// Create the main window
function createWindow() {
  console.log('Creating window...');
  console.log('isDev:', isDev);
  console.log('__dirname:', __dirname);
  console.log('app.getAppPath():', app.getAppPath());
  
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    frame: false,           // Frameless/borderless window
    autoHideMenuBar: true,  // Hide the menu bar
    title: 'D2L Assignment Assistant',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#d0d0d2',
    show: false
  });
  
  // Start maximized
  mainWindow.maximize();

  // Load the app
  if (isDev) {
    // In development, load from Vite dev server
    const viteUrl = 'http://localhost:3000';
    console.log('Loading from Vite dev server:', viteUrl);
    
    // Wait a bit for Vite to be ready
    setTimeout(() => {
      mainWindow.loadURL(viteUrl).catch(err => {
        console.error('Failed to load Vite dev server:', err);
        // Try again after another second
        setTimeout(() => {
          console.log('Retrying to load:', viteUrl);
          mainWindow.loadURL(viteUrl);
        }, 1000);
      });
    }, 2000);
    
    // Log when page loads
    mainWindow.webContents.on('did-finish-load', () => {
      console.log('✅ Page loaded successfully');
      const url = mainWindow.webContents.getURL();
      console.log('Current URL:', url);
    });
    
    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
      console.error('❌ Failed to load:', errorCode, errorDescription);
    });
    
    // DevTools can be opened manually with Ctrl+Shift+I or F12
    // mainWindow.webContents.openDevTools();
  } else {
    // In production, load from built files in app.asar
    const distPath = path.join(app.getAppPath(), 'dist-frontend', 'index.html');
    console.log('Loading from production build:', distPath);
    mainWindow.loadFile(distPath);
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.whenReady().then(async () => {
  console.log('App ready, starting...');
  
  try {
    // Kill any existing process on port 5000 first
    await killPort5000();
    
    // Start server
    await startServer();
    console.log('Server started');
    
    // Then create window
    createWindow();
    
    // Auto-update disabled - using manual patch system instead
    // Check for updates after window is created (only in production)
    // if (!isDev) {
    //   setTimeout(() => {
    //     console.log('Checking for updates...');
    //     autoUpdater.checkForUpdates();
    //   }, 3000); // Wait 3 seconds after launch
    // }
  } catch (error) {
    console.error('Failed to start:', error);
  }
});

app.on('window-all-closed', () => {
  // Kill server process
  if (serverProcess) {
    serverProcess.kill();
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('before-quit', () => {
  if (serverProcess) {
    serverProcess.kill();
  }
});

// IPC handlers for window controls
ipcMain.handle('close-window', () => {
  if (mainWindow) {
    mainWindow.close();
  }
  app.quit();
});

ipcMain.handle('reload-window', () => {
  if (mainWindow) {
    mainWindow.reload();
  }
});

ipcMain.handle('minimize-window', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
});

ipcMain.handle('maximize-window', () => {
  if (mainWindow) {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  }
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  // Normalize defaultPath for Windows - ensure it uses proper path format
  if (options.defaultPath) {
    options.defaultPath = path.normalize(options.defaultPath);
  }
  
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

