/**
 * Quiz Grader - Electron Main Process
 * 
 * This file handles the Electron window and starts the backend server.
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn, fork, exec } = require('child_process');

let mainWindow = null;
let serverProcess = null;

// Determine if we're in development or production
const isDev = !app.isPackaged;

// Kill any process using port 5000 before starting
function killPort5000() {
  return new Promise((resolve) => {
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
    
    mainWindow.webContents.openDevTools();
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

