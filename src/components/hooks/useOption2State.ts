/**
 * useOption2State - State management hook for Option2 component
 * Manages all state, effects, and state-related logic
 */

import { useState, useEffect } from 'react';
import { loadClasses, checkServerStatus, ClassData } from '../../services/quizGraderService';
import { SERVER_POLL_INTERVAL_MS, SERVER_CHECK_TIMEOUT_MS } from '../constants/ui-constants';
import { useLogStream } from './useLogStream';
import type {
  ZipFile,
  ProcessingFolder,
  UploadedPdfFile,
  ConfirmationConfig,
  ClearOptionsConfig,
  ServerStatus,
  EmailStudent,
  ConfidenceScore,
  LastProcessedAssignment,
  ClassOption
} from '../../types';

export interface Option2State {
  // Theme
  isDark: boolean;
  setIsDark: (value: boolean) => void;

  // Class management
  selectedClass: string;
  setSelectedClass: (value: string) => void;
  classOptions: ClassOption[];
  setClassOptions: (value: ClassOption[]) => void;
  classes: ClassData[];
  setClasses: (value: ClassData[]) => void;
  showClassSetup: boolean;
  setShowClassSetup: (value: boolean) => void;
  showPatchManager: boolean;
  setShowPatchManager: (value: boolean) => void;

  // Processing states
  processing: boolean;
  setProcessing: (value: boolean) => void;
  processingCompletion: boolean;
  setProcessingCompletion: (value: boolean) => void;
  extracting: boolean;
  setExtracting: (value: boolean) => void;
  splitting: boolean;
  setSplitting: (value: boolean) => void;
  clearing: boolean;
  setClearing: (value: boolean) => void;

  // Settings
  dontOverride: boolean;
  setDontOverride: (value: boolean) => void;

  // Logs
  logs: string[];
  setLogs: (value: string[] | ((prev: string[]) => string[])) => void;
  addLog: (message: string) => void;
  isConnected: boolean;

  // ZIP selection
  zipFiles: ZipFile[];
  setZipFiles: (value: ZipFile[]) => void;
  showZipSelection: boolean;
  setShowZipSelection: (value: boolean) => void;
  zipSelectionMode: 'quiz' | 'completion';
  setZipSelectionMode: (value: 'quiz' | 'completion') => void;

  // Last processed assignment
  lastProcessedAssignment: LastProcessedAssignment | null;
  setLastProcessedAssignment: (value: LastProcessedAssignment | null) => void;

  // Confidence scores
  confidenceScores: ConfidenceScore[] | null;
  setConfidenceScores: (value: ConfidenceScore[] | null) => void;

  // Email students modal
  showEmailModal: boolean;
  setShowEmailModal: (value: boolean) => void;
  emailModalMode: 'all' | 'without-assignment';
  setEmailModalMode: (value: 'all' | 'without-assignment') => void;
  emailStudents: EmailStudent[];
  setEmailStudents: (value: EmailStudent[]) => void;

  // Uploaded files
  uploadedPdfFile: UploadedPdfFile | File | null;
  setUploadedPdfFile: (value: UploadedPdfFile | File | null) => void;
  uploadedPdfFileForExtraction: UploadedPdfFile | File | null;
  setUploadedPdfFileForExtraction: (value: UploadedPdfFile | File | null) => void;
  selectedPdfPathForExtraction: string | null;
  setSelectedPdfPathForExtraction: (value: string | null) => void;

  // Paths
  pdfsFolderPath: string | null;
  setPdfsFolderPath: (value: string | null) => void;
  classRosterPath: string | null;
  setClassRosterPath: (value: string | null) => void;

  // Clear data states
  showAssignmentSelection: boolean;
  setShowAssignmentSelection: (value: boolean) => void;
  processingFolders: ProcessingFolder[];
  setProcessingFolders: (value: ProcessingFolder[]) => void;
  selectedAssignments: Set<string>;
  setSelectedAssignments: (value: Set<string> | ((prev: Set<string>) => Set<string>)) => void;
  wasSelectAllUsed: boolean;
  setWasSelectAllUsed: (value: boolean) => void;

  // Modal states
  showConfirmation: boolean;
  setShowConfirmation: (value: boolean) => void;
  confirmationConfig: ConfirmationConfig | null;
  setConfirmationConfig: (value: ConfirmationConfig | null) => void;
  showClearOptions: boolean;
  setShowClearOptions: (value: boolean) => void;
  clearOptionsConfig: ClearOptionsConfig | null;
  setClearOptionsConfig: (value: ClearOptionsConfig | null) => void;

  // Server status
  serverStatus: ServerStatus;
  setServerStatus: (value: ServerStatus) => void;

  // Helper functions
  reloadClasses: () => Promise<void>;
  requireClass: () => boolean;
}

export function useOption2State(): Option2State {
  // Theme
  const [isDark, setIsDark] = useState(false);

  // Class management
  const [selectedClass, setSelectedClass] = useState('');
  const [classOptions, setClassOptions] = useState<ClassOption[]>([
    { value: '', label: 'Select Class' }
  ]);
  const [classes, setClasses] = useState<ClassData[]>([]);
  const [showClassSetup, setShowClassSetup] = useState(false);
  const [showPatchManager, setShowPatchManager] = useState(false);

  // Processing states
  const [processing, setProcessing] = useState(false);
  const [processingCompletion, setProcessingCompletion] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [splitting, setSplitting] = useState(false);
  const [clearing, setClearing] = useState(false);

  // Settings
  const [dontOverride, setDontOverride] = useState(false);

  // Logs
  const [logs, setLogs] = useState<string[]>([]);

  // Add log function with duplicate filtering
  const addLog = (message: string) => {
    if (message) {
      setLogs(prevLogs => {
        // Filter out unwanted messages
        const messageLower = message.toLowerCase();
        const unwantedPatterns = [
          'loaded import file',
          'sending split pdf request to backend',
          'uploading pdf to backend',
          'sending request to backend',
          'sending process request to backend',
          'sending selected quiz processing request to backend',
          'sending completion processing request to backend',
          'sending selected completion processing request to backend',
          'sending open downloads request to backend',
          'sending clear request to backend',
          'sending clear archived data request to backend',
          'opening downloads folder',
          'opening folder',
          '📡 sending',
          '📁 opening'
        ];

        if (unwantedPatterns.some(pattern => messageLower.includes(pattern))) {
          return prevLogs;
        }

        // Filter out duplicate consecutive messages
        if (prevLogs.length > 0 && prevLogs[prevLogs.length - 1] === message) {
          return prevLogs;
        }

        return [...prevLogs, message];
      });
    }
  };

  // Connect to SSE log stream
  const { isConnected } = useLogStream(addLog);

  // ZIP selection
  const [zipFiles, setZipFiles] = useState<ZipFile[]>([]);
  const [showZipSelection, setShowZipSelection] = useState(false);
  const [zipSelectionMode, setZipSelectionMode] = useState<'quiz' | 'completion'>('quiz');

  // Last processed assignment
  const [lastProcessedAssignment, setLastProcessedAssignment] = useState<LastProcessedAssignment | null>(null);

  // Confidence scores
  const [confidenceScores, setConfidenceScores] = useState<ConfidenceScore[] | null>(null);

  // Email students modal
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailModalMode, setEmailModalMode] = useState<'all' | 'without-assignment'>('all');
  const [emailStudents, setEmailStudents] = useState<EmailStudent[]>([]);

  // Uploaded files
  const [uploadedPdfFile, setUploadedPdfFile] = useState<UploadedPdfFile | File | null>(null);
  const [uploadedPdfFileForExtraction, setUploadedPdfFileForExtraction] = useState<UploadedPdfFile | File | null>(null);
  const [selectedPdfPathForExtraction, setSelectedPdfPathForExtraction] = useState<string | null>(null);

  // Paths
  const [pdfsFolderPath, setPdfsFolderPath] = useState<string | null>(null);
  const [classRosterPath, setClassRosterPath] = useState<string | null>(null);

  // Clear data states
  const [showAssignmentSelection, setShowAssignmentSelection] = useState(false);
  const [processingFolders, setProcessingFolders] = useState<ProcessingFolder[]>([]);
  const [selectedAssignments, setSelectedAssignments] = useState<Set<string>>(new Set());
  const [wasSelectAllUsed, setWasSelectAllUsed] = useState(false);

  // Modal states
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationConfig, setConfirmationConfig] = useState<ConfirmationConfig | null>(null);
  const [showClearOptions, setShowClearOptions] = useState(false);
  const [clearOptionsConfig, setClearOptionsConfig] = useState<ClearOptionsConfig | null>(null);

  // Server status
  const [serverStatus, setServerStatus] = useState<ServerStatus>('checking');

  // Check server status periodically
  useEffect(() => {
    const checkServer = async () => {
      const status = await checkServerStatus(SERVER_CHECK_TIMEOUT_MS);
      setServerStatus(status as ServerStatus);
    };

    checkServer();
    const interval = setInterval(checkServer, SERVER_POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  // Load classes on mount
  useEffect(() => {
    const fetchClasses = async () => {
      try {
        const result = await loadClasses();
        if (result.success && result.classes) {
          setClasses(result.classes);

          const options: ClassOption[] = [
            { value: '', label: 'Select Class' },
            ...result.classes
              .sort((a, b) => a.label.localeCompare(b.label))
              .map(cls => ({ value: cls.value, label: cls.label }))
          ];
          setClassOptions(options);
          addLog('👋 Welcome!');
        } else {
          setClassOptions([{ value: '', label: 'Select Class' }]);
          addLog('👋 Welcome!');
        }
      } catch (error) {
        console.error('Error loading classes:', error);
        setClassOptions([{ value: '', label: 'Select Class' }]);
        addLog('👋 Welcome!');
      }
    };

    fetchClasses();
  }, []);

  // Handler to reload classes
  const reloadClasses = async () => {
    try {
      const result = await loadClasses();
      if (result.success && result.classes) {
        setClasses(result.classes);
        const options: ClassOption[] = [
          { value: '', label: 'Select Class' },
          ...result.classes
            .sort((a, b) => a.label.localeCompare(b.label))
            .map(cls => ({ value: cls.value, label: cls.label }))
        ];
        setClassOptions(options);
      } else {
        addLog('❌ Failed to reload classes');
      }
    } catch (error) {
      addLog(`❌ Error loading classes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Helper for class validation
  const requireClass = (): boolean => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return false;
    }
    return true;
  };

  return {
    isDark,
    setIsDark,
    selectedClass,
    setSelectedClass,
    classOptions,
    setClassOptions,
    classes,
    setClasses,
    showClassSetup,
    setShowClassSetup,
    showPatchManager,
    setShowPatchManager,
    processing,
    setProcessing,
    processingCompletion,
    setProcessingCompletion,
    extracting,
    setExtracting,
    splitting,
    setSplitting,
    clearing,
    setClearing,
    dontOverride,
    setDontOverride,
    logs,
    setLogs,
    addLog,
    isConnected,
    zipFiles,
    setZipFiles,
    showZipSelection,
    setShowZipSelection,
    zipSelectionMode,
    setZipSelectionMode,
    lastProcessedAssignment,
    setLastProcessedAssignment,
    confidenceScores,
    setConfidenceScores,
    showEmailModal,
    setShowEmailModal,
    emailModalMode,
    setEmailModalMode,
    emailStudents,
    setEmailStudents,
    uploadedPdfFile,
    setUploadedPdfFile,
    uploadedPdfFileForExtraction,
    setUploadedPdfFileForExtraction,
    selectedPdfPathForExtraction,
    setSelectedPdfPathForExtraction,
    pdfsFolderPath,
    setPdfsFolderPath,
    classRosterPath,
    setClassRosterPath,
    showAssignmentSelection,
    setShowAssignmentSelection,
    processingFolders,
    setProcessingFolders,
    selectedAssignments,
    setSelectedAssignments,
    wasSelectAllUsed,
    setWasSelectAllUsed,
    showConfirmation,
    setShowConfirmation,
    confirmationConfig,
    setConfirmationConfig,
    showClearOptions,
    setShowClearOptions,
    clearOptionsConfig,
    setClearOptionsConfig,
    serverStatus,
    setServerStatus,
    reloadClasses,
    requireClass
  };
}
