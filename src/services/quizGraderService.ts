// Quiz Grader Service
// Handles API calls to the backend for quiz grading functionality

const API_BASE_URL = 'http://localhost:5000/api';

export interface ApiResult {
  success: boolean;
  error?: string;
  logs?: string[];
  classes?: string[];
  zip_files?: Array<{ index: number; filename: string; path: string }>;
  message?: string;
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
    
    if (addLog && result.logs) {
      result.logs.forEach((message: string) => addLog(message));
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
    logMessage: '📡 Sending process request to backend...',
    errorMessage: 'Failed to process quizzes',
    addLog
  });

export const processSelectedQuiz = (drive: string, selectedClass: string, zipPath: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/process-selected',
    body: { drive, className: selectedClass, zipPath },
    logMessage: '📡 Sending selected quiz processing request to backend...',
    errorMessage: 'Failed to process selected quiz',
    addLog
  });

export const processCompletion = (drive: string, selectedClass: string, dontOverride: boolean, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/process-completion',
    body: { drive, className: selectedClass, dontOverride: dontOverride || false },
    logMessage: '📡 Sending completion processing request to backend...',
    errorMessage: 'Failed to process completion',
    addLog
  });

export const processSelectedCompletion = (drive: string, selectedClass: string, zipPath: string, dontOverride: boolean, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/process-completion-selected',
    body: { drive, className: selectedClass, zipPath, dontOverride: dontOverride || false },
    logMessage: '📡 Sending selected completion processing request to backend...',
    errorMessage: 'Failed to process selected completion',
    addLog
  });

export const extractGrades = (drive: string, selectedClass: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/extract-grades',
    body: { drive, className: selectedClass },
    logMessage: '📡 Sending grade extraction request to backend...',
    errorMessage: 'Failed to extract grades',
    addLog
  });

export const splitPdf = (drive: string, selectedClass: string, assignmentName: string | null, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/split-pdf',
    body: { drive, className: selectedClass, assignmentName },
    logMessage: '📡 Sending split PDF request to backend...',
    errorMessage: 'Failed to split PDF',
    addLog
  });

export const openFolder = (drive: string, selectedClass: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/open-folder',
    body: { drive, className: selectedClass },
    logMessage: '📡 Sending open folder request to backend...',
    errorMessage: 'Failed to open folder',
    addLog
  });

export const openDownloads = (addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/open-folder',
    body: { drive: 'C', className: 'DOWNLOADS' },
    logMessage: '📡 Sending open downloads request to backend...',
    errorMessage: 'Failed to open downloads folder',
    addLog
  });

export const clearAllData = (drive: string, selectedClass: string, addLog: LogCallback): Promise<ApiResult> =>
  apiCall({
    endpoint: '/quiz/clear-data',
    body: { drive, className: selectedClass },
    logMessage: '📡 Sending clear request to backend...',
    errorMessage: 'Failed to clear data',
    addLog
  });

// Config management functions
export const getConfig = async (): Promise<ApiResult> => {
  try {
    const response = await fetch('http://localhost:5000/api/config', {
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
    const response = await fetch('http://localhost:5000/api/config', {
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

