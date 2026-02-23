/**
 * Shared TypeScript type definitions
 */

// ZIP file information from backend
export interface ZipFile {
  index: number;
  filename: string;
  path: string;
}

// Processing folder information
export interface ProcessingFolder {
  name: string;
  path: string;
  size: string;
  modified: string;
}

// PDF file information (from File API or Electron dialog)
export interface UploadedPdfFile {
  name: string;
  path?: string;
  size?: number;
  type?: string;
  // For File API compatibility
  arrayBuffer?: () => Promise<ArrayBuffer>;
}

// Confirmation modal configuration
export interface ConfirmationConfig {
  title: string;
  message: string;
  confirmText: string;
  onConfirm: () => void;
  isDanger?: boolean;
}

// Clear options modal configuration
export interface ClearOptionsConfig {
  title: string;
  message: string;
  onConfirm: (option: ClearOption) => void;
  hasCurrentAssignment?: boolean;
  onBack?: () => void;
}

// Clear option values
export type ClearOption = 'saveFoldersAndPdf' | 'saveCombinedPdf' | 'deleteAll' | 'deleteEverything';

// Server status types
export type ServerStatus = 'checking' | 'online' | 'offline';

// Email student information
export interface EmailStudent {
  name: string;
  hasAssignment: boolean;
  email?: string;
  isUnreadable?: boolean;
}

// Confidence score for grade extraction
export interface ConfidenceScore {
  name: string;
  grade: string;
  confidence: number;
}

// Last processed assignment info
export interface LastProcessedAssignment {
  name: string;
  className: string;
  zipPath: string;
}

// Class option for dropdown
export interface ClassOption {
  value: string;
  label: string;
}

// Electron API types (for window.electronAPI)
export interface ElectronAPI {
  showOpenDialog: (options: ElectronDialogOptions) => Promise<ElectronDialogResult>;
}

export interface ElectronDialogOptions {
  title?: string;
  defaultPath?: string;
  buttonLabel?: string;
  filters?: Array<{ name: string; extensions: string[] }>;
  properties?: Array<'openFile' | 'openDirectory' | 'multiSelections' | 'showHiddenFiles'>;
}

export interface ElectronDialogResult {
  canceled: boolean;
  filePaths: string[];
}

// Window augmentation for Electron API
declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}
