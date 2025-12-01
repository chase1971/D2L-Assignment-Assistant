/**
 * Quiz Grader - Electron Preload Script
 * 
 * Exposes safe APIs to the renderer process.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Window controls
  closeWindow: () => ipcRenderer.invoke('close-window'),
  reloadWindow: () => ipcRenderer.invoke('reload-window'),
  minimizeWindow: () => ipcRenderer.invoke('minimize-window'),
  maximizeWindow: () => ipcRenderer.invoke('maximize-window'),
  
  // Logging
  sendLog: (message, type = 'info') => {
    console.log(`[${type.toUpperCase()}] ${message}`);
  }
});

