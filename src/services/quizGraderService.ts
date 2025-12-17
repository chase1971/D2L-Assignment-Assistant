// Quiz Grader Service
// Handles API calls to the backend for quiz grading functionality

// Use environment variable if available, otherwise fall back to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Log entry from backend (new format with level info)
export interface LogEntry {
  level: 'SUCCESS' | 'ERROR' | 'WARNING' | 'INFO';
  message: string;
}

export interface ConfidenceScore {
  name: string;
  grade: string;
  confidence: number;
}

export interface ApiResult {
  success: boolean;
  error?: string;
  logs?: (string | LogEntry)[];  // Can be strings (legacy) or LogEntry objects (new)
  userLogs?: LogEntry[];  // New format from server.js
  classes?: string[];
  zip_files?: Array<{ index: number; filename: string; path: string }>;
  folders?: Array<{ name: string; path: string; size: string; modified: string }>;
  message?: string;
  killed?: number;  // For killProcesses response
  assignmentName?: string;  // For split PDF upload response
  assignment_name?: string;  // From Python backend
  combined_pdf_path?: string;  // From Python backend
  confidenceScores?: ConfidenceScore[];  // For grade extraction
  config?: {
    developerMode?: boolean;
  };
}

// ============================================================
// GENERIC API CALLER - Eliminates repetitive fetch/error handling
// ============================================================

type LogCallback = (msg: string) => void;

interface ApiCallOptions {
  endpoint: string;
  body?: Record<string, unknown>;
  logMessage?: string;
  errorMessage: string;
  addLog?: LogCallback;
}

async function apiCall({ endpoint, body, logMessage, errorMessage, addLog }: ApiCallOptions): Promise<ApiResult> {
  try {
    if (addLog && logMessage) {
      addLog(logMessage);
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { error: errorText };
      }
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.error || errorText}`);
    }

    const result = await response.json();
    
    // Process logs from backend
    if (addLog) {
      // New format: userLogs array of {level, message} objects
      if (result.userLogs && Array.isArray(result.userLogs)) {
        result.userLogs.forEach((entry: LogEntry | string) => {
          if (typeof entry === 'string') {
            addLog(entry);
          } else if (entry && entry.message) {
            addLog(entry.message);
          }
        });
      }
      // Legacy format: logs array of strings
      else if (result.logs && Array.isArray(result.logs)) {
        result.logs.forEach((entry: LogEntry | string) => {
          if (typeof entry === 'string') {
            const lines = entry.split('\n');
            lines.forEach(line => {
              const trimmed = line.trim();
              if (trimmed) {
                addLog(trimmed);
              }
            });
          } else if (entry && entry.message) {
            addLog(entry.message);
          }
        });
      }
    }
    
    return result;
  } catch (error) {
    console.error(`${errorMessage}:`, error);
    return {
      success: false,
      error: error instanceof Error ? error.message : errorMessage
    };
  }
}

// ============================================================
// PUBLIC API FUNCTIONS
// ============================================================

export const listClasses = (drive: string): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/list-classes',
    body: { drive },
    errorMessage: 'Failed to list classes'
  });

export const processQuizzes = (drive: string, selectedClass: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/process',
    body: { drive, className: selectedClass },
    errorMessage: 'Failed to process quizzes',
    addLog
  });

export const processSelectedQuiz = (drive: string, selectedClass: string, zipPath: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/process-selected',
    body: { drive, className: selectedClass, zipPath },
    errorMessage: 'Failed to process selected quiz',
    addLog
  });

export const processCompletion = (drive: string, selectedClass: string, dontOverride: boolean, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/process-completion',
    body: { drive, className: selectedClass, dontOverride: dontOverride || false },
    errorMessage: 'Failed to process completion',
    addLog
  });

export const processSelectedCompletion = (drive: string, selectedClass: string, zipPath: string, dontOverride: boolean, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/process-completion-selected',
    body: { drive, className: selectedClass, zipPath, dontOverride: dontOverride || false },
    errorMessage: 'Failed to process selected completion',
    addLog
  });

export const extractGrades = (drive: string, selectedClass: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/extract-grades',
    body: { drive, className: selectedClass },
    errorMessage: 'Failed to extract grades',
    addLog
  });

export const splitPdf = (drive: string, selectedClass: string, assignmentName: string | null, pdfPath: string | null, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/split-pdf',
    body: { drive, className: selectedClass, assignmentName, pdfPath },
    errorMessage: 'Failed to split PDF',
    addLog
  });

export const splitPdfUpload = async (drive: string, selectedClass: string, file: File, addLog: LogCallback): Promise<ApiResult> => {
  try {
    if (addLog) {
      addLog('📡 Uploading PDF to backend...');
    }
    
    const formData = new FormData();
    formData.append('pdf', file);
    formData.append('drive', drive);
    formData.append('className', selectedClass);
    
    const response = await fetch(`${API_BASE_URL}/quiz/split-pdf-upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { error: errorText };
      }
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.error || errorText}`);
    }

    const result = await response.json();
    
    if (addLog && result.logs) {
      result.logs.forEach((message: string) => {
        const lines = message.split('\n');
        lines.forEach(line => {
          const trimmed = line.trim();
          if (trimmed) {
            addLog(trimmed);
          }
        });
      });
    }
    
    return result;
  } catch (error) {
    console.error('Failed to upload and split PDF:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to upload and split PDF'
    };
  }
};

export const getPdfsFolderPath = async (drive: string, selectedClass: string): Promise<{ targetPath: string; existingPath: string } | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/quiz/get-pdfs-folder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ drive, className: selectedClass })
    });
    
    if (!response.ok) {
      console.error('Failed to get PDFs folder path:', response.status);
      return null;
    }
    
    const data = await response.json();
    if (data.success && data.path) {
      return {
        targetPath: data.path,
        existingPath: data.existingPath || data.path,
        classFolder: data.classFolder || null
      };
    }
    
    console.error('No path in response:', data);
    return null;
  } catch (error) {
    console.error('Error getting PDFs folder path:', error);
    return null;
  }
};

export const openFolder = (drive: string, selectedClass: string, addLog: LogCallback, classFolderOnly: boolean = false): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/open-folder',
    body: { drive, className: selectedClass, classFolderOnly },
    errorMessage: 'Failed to open folder',
    addLog
  });

export const openDownloads = (addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/open-folder',
    body: { drive: 'C', className: 'DOWNLOADS' },
    errorMessage: 'Failed to open downloads folder',
    addLog
  });

export const clearAllData = (drive: string, selectedClass: string, assignmentName: string | null, saveFoldersAndPdf: boolean, saveCombinedPdf: boolean, deleteEverything: boolean, deleteArchivedToo: boolean, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/clear-data',
    body: { drive, className: selectedClass, assignmentName, saveFoldersAndPdf, saveCombinedPdf, deleteEverything, deleteArchivedToo },
    errorMessage: 'Failed to clear data',
    addLog
  });

export const listProcessingFolders = (drive: string, selectedClass: string): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/list-processing-folders',
    body: { drive, className: selectedClass },
    errorMessage: 'Failed to list processing folders'
  });

export const clearArchivedData = (drive: string, selectedClass: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/clear-archived-data',
    body: { drive, className: selectedClass },
    errorMessage: 'Failed to clear archived data',
    addLog
  });

// LogTerminal API functions
export const killProcesses = (addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/kill-processes',
    logMessage: '🔄 Killing all Node processes...',
    errorMessage: 'Failed to kill processes',
    addLog
  });

export const openStudentPdf = (drive: string, className: string, studentName: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/open-student-pdf',
    body: { drive, className, studentName },
    logMessage: `📂 Opening PDF for: ${studentName}`,
    errorMessage: 'Error opening PDF',
    addLog
  });

export const openCombinedPdf = (drive: string, className: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/open-combined-pdf',
    body: { drive, className },
    logMessage: '📂 Opening combined PDF...',
    errorMessage: 'Error opening PDF',
    addLog
  });

export const openImportFile = (drive: string, className: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/open-import-file',
    body: { drive, className },
    logMessage: '📂 Opening import file...',
    errorMessage: 'Error opening import file',
    addLog
  });

// Server status check
export const checkServerStatus = async (timeoutMs: number = 3000): Promise<'online' | 'offline'> => {
  try {
    const response = await fetch(`${API_BASE_URL}/test`, {
      method: 'GET',
      signal: AbortSignal.timeout(timeoutMs)
    });
    return response.ok ? 'online' : 'offline';
  } catch {
    return 'offline';
  }
};

// Config management functions
export const getConfig = async (): Promise<ApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/config`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Get config service error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get config'
    };
  }
};

export const saveConfig = async (config: Record<string, unknown>): Promise<ApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Save config service error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to save config'
    };
  }
};

// ============================================================
// CLASS MANAGEMENT
// ============================================================

export interface ClassData {
  id: string;
  value: string;
  label: string;
  rosterFolderPath: string;
  isProtected?: boolean;
}

export interface ClassApiResult extends ApiResult {
  classes?: ClassData[];
  class?: ClassData;
  deletedCount?: number;
  folderPath?: string;
}

// Load all classes
export const loadClasses = async (): Promise<ClassApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/classes`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to load classes'
    };
  }
};

// Add a new class
export const addClass = async (classData: Omit<ClassData, 'id' | 'isProtected'>): Promise<ClassApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/classes/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(classData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to add class'
    };
  }
};

// Edit an existing class
export const editClass = async (id: string, classData: Omit<ClassData, 'id' | 'isProtected'>): Promise<ClassApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/classes/edit/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(classData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to edit class'
    };
  }
};

// Delete a class
export const deleteClass = async (id: string): Promise<ClassApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/classes/delete/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to delete class'
    };
  }
};

// Delete all non-protected classes
export const deleteAllClasses = async (): Promise<ClassApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/classes/deleteAll`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to delete classes'
    };
  }
};

// Open folder picker dialog
export const selectFolder = async (): Promise<ClassApiResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/classes/select-folder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to select folder'
    };
  }
};

// Validate folder has CSV file
export const validateFolder = async (folderPath: string): Promise<{ success: boolean; hasCSV: boolean; error?: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/classes/validate-folder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folderPath })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      hasCSV: false,
      error: error instanceof Error ? error.message : 'Failed to validate folder'
    };
  }
};

// ============================================================
// WINDOW CONTROLS (Electron API)
// ============================================================

// Electron API type for window controls
declare global {
  interface Window {
    electronAPI?: {
      closeWindow: () => void;
      reloadWindow: () => void;
      minimizeWindow: () => void;
      maximizeWindow: () => void;
      sendLog: (message: string, type?: string) => void;
    };
  }
}

export const closeWindow = () => {
  if (window.electronAPI?.closeWindow) {
    window.electronAPI.closeWindow();
  } else {
    window.close();
  }
};

export const reloadWindow = () => {
  if (window.electronAPI?.reloadWindow) {
    window.electronAPI.reloadWindow();
  } else {
    window.location.reload();
  }
};

export const minimizeWindow = () => {
  if (window.electronAPI?.minimizeWindow) {
    window.electronAPI.minimizeWindow();
  }
};

export const maximizeWindow = () => {
  if (window.electronAPI?.maximizeWindow) {
    window.electronAPI.maximizeWindow();
  }
};

