/**
 * useOption2State - State management hook for Option2 component
 * Manages all state, effects, and state-related logic
 */

import { useState, useEffect } from 'react';
import { loadClasses, checkServerStatus, ClassData } from '../../services/quizGraderService';
import { SERVER_POLL_INTERVAL_MS, SERVER_CHECK_TIMEOUT_MS } from '../constants/ui-constants';
import { useLogStream } from '../../hooks/useLogStream';

export interface Option2State {
  // Theme
  isDark: boolean;
  setIsDark: (value: boolean) => void;
  
  // Class management
  selectedClass: string;
  setSelectedClass: (value: string) => void;
  classOptions: Array<{ value: string; label: string }>;
  setClassOptions: (value: Array<{ value: string; label: string }>) => void;
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
  zipFiles: any[];
  setZipFiles: (value: any[]) => void;
  showZipSelection: boolean;
  setShowZipSelection: (value: boolean) => void;
  zipSelectionMode: 'quiz' | 'completion';
  setZipSelectionMode: (value: 'quiz' | 'completion') => void;
  
  // Last processed assignment
  lastProcessedAssignment: { name: string; className: string; zipPath: string } | null;
  setLastProcessedAssignment: (value: { name: string; className: string; zipPath: string } | null) => void;
  
  // Confidence scores
  confidenceScores: Array<{name: string; grade: string; confidence: number}> | null;
  setConfidenceScores: (value: Array<{name: string; grade: string; confidence: number}> | null) => void;
  
  // Email students modal
  showEmailModal: boolean;
  setShowEmailModal: (value: boolean) => void;
  emailModalMode: 'all' | 'without-assignment';
  setEmailModalMode: (value: 'all' | 'without-assignment') => void;
  emailStudents: Array<{name: string; hasAssignment: boolean; email?: string; isUnreadable?: boolean}>;
  setEmailStudents: (value: Array<{name: string; hasAssignment: boolean; email?: string; isUnreadable?: boolean}>) => void;
  studentsWithoutSubmission: string[];
  setStudentsWithoutSubmission: (value: string[]) => void;
  
  // Statistics modal
  showStatisticsModal: boolean;
  setShowStatisticsModal: (value: boolean) => void;
  statisticsStudents: any[];
  setStatisticsStudents: (value: any[]) => void;
  
  // Uploaded files
  uploadedPdfFile: any | null;
  setUploadedPdfFile: (value: any | null) => void;
  uploadedPdfFileForExtraction: any | null;
  setUploadedPdfFileForExtraction: (value: any | null) => void;
  selectedPdfPathForExtraction: string | null;
  setSelectedPdfPathForExtraction: (value: string | null) => void;
  
  // Paths
  pdfsFolderPath: any | null;
  setPdfsFolderPath: (value: any | null) => void;
  classRosterPath: string | null;
  setClassRosterPath: (value: string | null) => void;
  
  // Clear data states
  showAssignmentSelection: boolean;
  setShowAssignmentSelection: (value: boolean) => void;
  processingFolders: any[];
  setProcessingFolders: (value: any[]) => void;
  selectedAssignments: Set<string>;
  setSelectedAssignments: (value: Set<string> | ((prev: Set<string>) => Set<string>)) => void;
  wasSelectAllUsed: boolean;
  setWasSelectAllUsed: (value: boolean) => void;
  
  // Modal states
  showConfirmation: boolean;
  setShowConfirmation: (value: boolean) => void;
  confirmationConfig: any | null;
  setConfirmationConfig: (value: any | null) => void;
  showClearOptions: boolean;
  setShowClearOptions: (value: boolean) => void;
  clearOptionsConfig: any | null;
  setClearOptionsConfig: (value: any | null) => void;
  
  // Server status
  serverStatus: string;
  setServerStatus: (value: string) => void;
  
  // Helper functions
  reloadClasses: () => Promise<void>;
  requireClass: () => boolean;
}

export function useOption2State(): Option2State {
  // Theme
  const [isDark, setIsDark] = useState(false);
  
  // Class management
  const [selectedClass, setSelectedClass] = useState('');
  const [classOptions, setClassOptions] = useState<Array<{ value: string; label: string }>>([
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
  const [zipFiles, setZipFiles] = useState([]);
  const [showZipSelection, setShowZipSelection] = useState(false);
  const [zipSelectionMode, setZipSelectionMode] = useState<'quiz' | 'completion'>('quiz');
  
  // Last processed assignment
  const [lastProcessedAssignment, setLastProcessedAssignment] = useState<{ name: string; className: string; zipPath: string } | null>(null);
  
  // Confidence scores
  const [confidenceScores, setConfidenceScores] = useState<Array<{name: string; grade: string; confidence: number}> | null>(null);
  
  // Email students modal
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailModalMode, setEmailModalMode] = useState<'all' | 'without-assignment'>('all');
  const [emailStudents, setEmailStudents] = useState<Array<{name: string; hasAssignment: boolean; email?: string; isUnreadable?: boolean}>>([]);
  const [studentsWithoutSubmission, setStudentsWithoutSubmission] = useState<string[]>([]);
  
  // Statistics modal
  const [showStatisticsModal, setShowStatisticsModal] = useState(false);
  const [statisticsStudents, setStatisticsStudents] = useState<any[]>([]);
  
  // Uploaded files
  const [uploadedPdfFile, setUploadedPdfFile] = useState<any | null>(null);
  const [uploadedPdfFileForExtraction, setUploadedPdfFileForExtraction] = useState<any | null>(null);
  const [selectedPdfPathForExtraction, setSelectedPdfPathForExtraction] = useState<string | null>(null);
  
  // Paths
  const [pdfsFolderPath, setPdfsFolderPath] = useState<any | null>(null);
  const [classRosterPath, setClassRosterPath] = useState<string | null>(null);
  
  // Clear data states
  const [showAssignmentSelection, setShowAssignmentSelection] = useState(false);
  const [processingFolders, setProcessingFolders] = useState<any[]>([]);
  const [selectedAssignments, setSelectedAssignments] = useState<Set<string>>(new Set());
  const [wasSelectAllUsed, setWasSelectAllUsed] = useState(false);
  
  // Modal states
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationConfig, setConfirmationConfig] = useState<any | null>(null);
  const [showClearOptions, setShowClearOptions] = useState(false);
  const [clearOptionsConfig, setClearOptionsConfig] = useState<any | null>(null);
  
  // Server status
  const [serverStatus, setServerStatus] = useState('checking');
  
  // Check server status periodically
  useEffect(() => {
    const checkServer = async () => {
      const status = await checkServerStatus(SERVER_CHECK_TIMEOUT_MS);
      setServerStatus(status);
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
          
          const options = [
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
        const options = [
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
    studentsWithoutSubmission,
    setStudentsWithoutSubmission,
    showStatisticsModal,
    setShowStatisticsModal,
    statisticsStudents,
    setStatisticsStudents,
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
