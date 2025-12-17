import React, { useState, useEffect } from 'react';
import { FolderOpen } from 'lucide-react';
import ZipSelectionModal from './ZipSelectionModal';
import AssignmentSelectionModal from './AssignmentSelectionModal';
import ConfirmationModal from './ConfirmationModal';
import ClearOptionsModal, { ClearOption } from './ClearOptionsModal';
import ActionCard from './ActionCard';
import LogTerminal from './LogTerminal';
import NavigationBar from './NavigationBar';
import {
  listClasses,
  processQuizzes,
  processSelectedQuiz,
  processCompletion,
  processSelectedCompletion,
  extractGrades,
  splitPdf,
  splitPdfUpload,
  openFolder,
  openDownloads,
  clearAllData,
  listProcessingFolders,
  clearArchivedData,
  checkServerStatus,
  getPdfsFolderPath
} from '../services/quizGraderService';
import { SERVER_POLL_INTERVAL_MS, SERVER_CHECK_TIMEOUT_MS } from './constants/ui-constants';
import { useThemeStyles } from './hooks/useThemeStyles';

// Class options - same as original QuizGrader.js
const CLASS_OPTIONS = [
  { value: '', label: 'Select Class' },
  { value: 'MW 11-1220  FM 4103', label: 'FM 4103 (MW 11:00-12:20)' },
  { value: 'MW 930-1050 CA 4105', label: 'CA 4105 (MW 9:30-10:50)' },
  { value: 'TTH 8-920  CA 4201', label: 'CA 4201 (TTH 8:00-9:20)' },
  { value: 'TTH 11-1220 FM 4202', label: 'FM 4202 (TTH 11:00-12:20)' },
  { value: 'TTH 930-1050 CA 4203', label: 'CA 4203 (TTH 9:30-10:50)' },
];

// Option 2: Horizontal Top Bar with Grid Layout Below - Figma Metallic Style
export default function Option2() {
  const drive = 'C'; // Always use C drive
  const [isDark, setIsDark] = useState(false);
  const [selectedClass, setSelectedClass] = useState('');
  const [dontOverride, setDontOverride] = useState(false);
  const [logs, setLogs] = useState([]);
  
  // Processing states
  const [processing, setProcessing] = useState(false);
  const [processingCompletion, setProcessingCompletion] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [splitting, setSplitting] = useState(false);
  const [clearing, setClearing] = useState(false);
  
  // ZIP selection state
  const [zipFiles, setZipFiles] = useState([]);
  const [showZipSelection, setShowZipSelection] = useState(false);
  const [zipSelectionMode, setZipSelectionMode] = useState('quiz');
  
  // Track last processed assignment (for Split PDF visibility)
  const [lastProcessedAssignment, setLastProcessedAssignment] = useState(null);
  
  // Store confidence scores from grade extraction
  const [confidenceScores, setConfidenceScores] = useState<Array<{name: string; grade: string; confidence: number}> | null>(null);
  
  // Helper function to extract class code from class folder name (e.g., "TTH 11-1220 FM 4202" -> "FM 4202")
  const extractClassCode = (className: string): string => {
    // Look for pattern: 2 letters, space, 4 digits at the end
    const match = className.match(/([A-Z]{2}\s+\d{4})\s*$/);
    if (match) {
      return match[1];
    }
    // Fallback: try to extract last 7 characters
    if (className.length >= 7) {
      return className.slice(-7).trim();
    }
    return '';
  };
  
  // Helper function to format assignment display name: "{assignment_name} {class_code}"
  const formatAssignmentDisplayName = (assignmentName: string, className: string): string => {
    // Remove "combined PDF" from the name (case insensitive)
    let cleaned = assignmentName.replace(/\s+combined\s+pdf\s*$/i, '').trim();
    
    // Extract class code
    const classCode = extractClassCode(className);
    
    // Remove class code from assignment name if it's already in there
    if (classCode) {
      const classCodePattern = new RegExp('\\s*' + classCode.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*', 'gi');
      cleaned = cleaned.replace(classCodePattern, ' ').trim();
    }
    
    // Clean up any extra spaces
    cleaned = cleaned.replace(/\s+/g, ' ').trim();
    
    // Add class code back if we have one
    if (classCode) {
      return `${cleaned} ${classCode}`;
    }
    return cleaned;
  };
  
  // Store uploaded PDF file (for browser mode)
  const [uploadedPdfFile, setUploadedPdfFile] = useState(null);
  
  // Store PDFs folder paths for selected class
  const [pdfsFolderPath, setPdfsFolderPath] = useState(null);
  // Store class roster folder path
  const [classRosterPath, setClassRosterPath] = useState<string | null>(null);
  
  // Clear All Data states
  const [showAssignmentSelection, setShowAssignmentSelection] = useState(false);
  const [processingFolders, setProcessingFolders] = useState([]);
  const [selectedAssignments, setSelectedAssignments] = useState(new Set());
  const [wasSelectAllUsed, setWasSelectAllUsed] = useState(false);
  
  // Confirmation modal state
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationConfig, setConfirmationConfig] = useState(null);
  
  // Clear options modal state
  const [showClearOptions, setShowClearOptions] = useState(false);
  const [clearOptionsConfig, setClearOptionsConfig] = useState<{
    title: string;
    message: string;
    onConfirm: (option: ClearOption) => void;
  } | null>(null);
  
  // Server status state
  const [serverStatus, setServerStatus] = useState('checking');
  
  // Check server status periodically
  useEffect(() => {
    const checkServer = async () => {
      const status = await checkServerStatus(SERVER_CHECK_TIMEOUT_MS);
      setServerStatus(status);
    };
    
    // Check immediately
    checkServer();
    
    // Check periodically
    const interval = setInterval(checkServer, SERVER_POLL_INTERVAL_MS);
    
    return () => clearInterval(interval);
  }, []);
  

  // Add log helper with duplicate filtering
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
          return prevLogs; // Don't add unwanted messages
        }
        
        // Filter out duplicate consecutive messages
        if (prevLogs.length > 0 && prevLogs[prevLogs.length - 1] === message) {
          return prevLogs; // Don't add duplicate
        }
        
        return [...prevLogs, message];
      });
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

  // Get theme styles from hook
  const { metalButtonClass, metalButtonStyle } = useThemeStyles();

  // Helper function to clean assignment name and format as folder name
  const formatAssignmentFolderName = (assignmentName: string, className: string): string => {
    if (!assignmentName) return '';
    
    // Remove "combined PDF" suffix (case insensitive)
    let cleaned = assignmentName.replace(/\s+combined\s+pdf\s*$/i, '');
    
    // Extract class code from class name (e.g., "FM 4202" from "TTH 11-1220 FM 4202")
    const classCodeMatch = className.match(/([A-Z]{2}\s+\d{4})\s*$/);
    const classCode = classCodeMatch ? classCodeMatch[1] : '';
    
    // Remove class code from assignment name if it's in there
    if (classCode) {
      const classCodeRegex = new RegExp(`\\s*${classCode.replace(/\s+/g, '\\s+')}\\s*`, 'gi');
      cleaned = cleaned.replace(classCodeRegex, ' ').trim();
    }
    
    // Clean up extra spaces
    cleaned = cleaned.replace(/\s+/g, ' ').trim();
    
    // Format as "grade processing [CLASS_CODE] [ASSIGNMENT]" or just "grade processing [ASSIGNMENT]"
    if (classCode) {
      return `grade processing ${classCode} ${cleaned}`;
    }
    return `grade processing ${cleaned}`;
  };

  // Handle class selection
  const handleClassChange = async (e: any) => {
    const newClass = e.target.value;
    setSelectedClass(newClass);
    setPdfsFolderPath(null); // Clear previous path
    setUploadedPdfFile(null); // Clear uploaded file when class changes
    
    // Clear last processed assignment when class changes (it should only be set after processing quizzes)
    setLastProcessedAssignment(null);
    
    if (newClass) {
      // Fetch and store the PDFs folder path for this class
      const pathResult = await getPdfsFolderPath(drive, newClass);
      setPdfsFolderPath(pathResult);
      
      // Get class roster folder path
      if (pathResult?.classFolder) {
        setClassRosterPath(pathResult.classFolder);
      } else if (pathResult?.targetPath) {
        // Fallback: Extract class roster folder from PDFs path if classFolder not provided
        const pdfsPath = pathResult.targetPath;
        const classRosterFolder = pdfsPath.split(/[/\\]PDFs/)[0]?.split(/[/\\]grade processing/)[0]?.trim() || null;
        if (classRosterFolder) {
          setClassRosterPath(classRosterFolder);
        }
      }
      
      if (pathResult) {
        addLog(`✅ Class loaded: ${newClass}`);
        // Show class roster folder location, not the PDFs folder
        const locationPath = pathResult.classFolder || pathResult.targetPath?.split(/[/\\]PDFs/)[0]?.split(/[/\\]grade processing/)[0]?.trim() || pathResult.targetPath;
        addLog(`📂 Location: ${locationPath}`);
      } else {
        addLog(`✅ Class loaded: ${newClass}`);
        addLog(`⚠️ Could not determine class folder location`);
      }
    } else {
      setClassRosterPath(null);
    }
  };

  // Open Downloads folder
  const handleOpenDownloads = async () => {
    try {
      const result = await openDownloads(addLog);
      if (result.success) {
        addLog('✅ Downloads folder opened successfully!');
      } else {
        addLog(`❌ ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Process quizzes
  const handleProcessQuizzes = async () => {
    if (!requireClass()) return;

    setProcessing(true);
    addLog('🔍 Searching for assignment ZIP in Downloads...');
    
    try {
      const result = await processQuizzes(drive, selectedClass, addLog);
      
      if (result.success) {
        // Success message already logged by backend - don't duplicate
      } else if (result.error === 'Multiple ZIP files found') {
        setZipFiles(result.zip_files || []);
        setZipSelectionMode('quiz');
        setShowZipSelection(true);
        // Don't log anything - just show the modal
        return;
      } else {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  // Handle ZIP file selection for quizzes
  const handleZipSelection = async (zipPath: string) => {
    setShowZipSelection(false);
    setProcessing(true);
    const zipFilename = zipPath.split('\\').pop() || '';
    addLog(`📦 Processing: ${zipFilename}`);
    
    try {
      const result = await processSelectedQuiz(drive, selectedClass, zipPath, addLog);
      
      if (result.success) {
        // Success message already logged by backend - don't duplicate
        // Use combined PDF name if available, otherwise fall back to assignment name
        let rawName = result.combined_pdf_path 
          ? result.combined_pdf_path.split('\\').pop()?.replace('.pdf', '') || result.assignment_name
          : result.assignment_name || zipFilename.replace(/\s*Download.*\.zip$/i, '').trim();
        
        // Format as "{assignment_name} {class_code}" (without "combined PDF")
        const displayName = formatAssignmentDisplayName(rawName, selectedClass);
        
        setLastProcessedAssignment({
          name: displayName,
          className: selectedClass,
          zipPath: zipPath
        });
      } else {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  // Handle ZIP modal close
  const handleZipModalClose = () => {
    setShowZipSelection(false);
    setProcessing(false);
    setProcessingCompletion(false);
  };

  // Handle ZIP modal selection (routes to quiz or completion based on mode)
  const handleZipModalSelect = (zipPath: string) => {
    if (zipSelectionMode === 'quiz') {
      handleZipSelection(zipPath);
    } else {
      handleCompletionZipSelection(zipPath);
    }
  };

  // Handle ZIP file selection for completions
  const handleCompletionZipSelection = async (zipPath: string) => {
    setShowZipSelection(false);
    setProcessingCompletion(true);
    const zipFilename = zipPath.split('\\').pop() || '';
    addLog(`📦 Processing: ${zipFilename}`);
    
    try {
      const result = await processSelectedCompletion(drive, selectedClass, zipPath, dontOverride, addLog);
      
      if (result.success) {
        addLog('✅ Completion processing completed!');
        addLog('✅ Auto-assigned 10 points to all submissions');
        // Note: Don't set lastProcessedAssignment for completion - it's only for quiz processing
      } else {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setProcessingCompletion(false);
    }
  };

  // Process completion
  const handleProcessCompletion = async () => {
    if (!requireClass()) return;

    setProcessingCompletion(true);
    addLog('🔍 Searching for assignment ZIP in Downloads...');
    
    try {
      const result = await processCompletion(drive, selectedClass, dontOverride, addLog);
      
      if (result.success) {
        addLog('✅ Completion processing completed!');
        addLog('✅ Auto-assigned 10 points to all submissions');
      } else if (result.error === 'Multiple ZIP files found') {
        setZipFiles(result.zip_files || []);
        setZipSelectionMode('completion');
        setShowZipSelection(true);
        // Don't log anything - just show the modal
        return;
      } else {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setProcessingCompletion(false);
    }
  };

  // Helper to display error messages (removes "Error:" prefix, handles multi-line)
  const displayError = (error: string | undefined) => {
    if (!error) return;
    
    // Remove "Error:" prefix if present (case insensitive)
    let cleanError = error.replace(/^Error:\s*/i, '').trim();
    
    // Remove duplicate ❌ at the start if present
    cleanError = cleanError.replace(/^❌\s*❌\s*/, '❌ ');
    
    // Split multi-line errors and display each line
    const errorLines = cleanError.split('\n');
    errorLines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed) {
        // If line doesn't start with ❌, add it (unless it's a continuation line)
        if (!trimmed.startsWith('❌') && !trimmed.startsWith('Please') && !trimmed.match(/^[A-Z]/)) {
          addLog(`❌ ${trimmed}`);
        } else {
          addLog(trimmed);
        }
      }
    });
  };

  // Extract grades
  const handleExtractGrades = async () => {
    if (!requireClass()) return;

    setExtracting(true);
    
    try {
      const result = await extractGrades(drive, selectedClass, addLog);
      
      // Store confidence scores if available
      if (result.success && result.confidenceScores) {
        setConfidenceScores(result.confidenceScores);
      } else {
        setConfidenceScores(null);
      }
      
      // Note: Success message is already printed by the backend
      // Only handle errors if they weren't already displayed in logs
      if (!result.success) {
        // Error is already displayed in logs from apiCall, but if logs weren't displayed
        // (e.g., network error), display the error separately
        if (result.error && (!result.logs || result.logs.length === 0)) {
          displayError(result.error);
        }
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setExtracting(false);
    }
  };

  // Handle PDF file selection for split
  const handleSelectPdfFile = async () => {
    if (!requireClass()) return;

    try {
      // Use Electron dialog if available (for file path)
      if ((window as any).electronAPI?.showOpenDialog) {
        // Fetch path for Electron dialog
        let pathInfo = pdfsFolderPath;
        if (!pathInfo) {
          pathInfo = await getPdfsFolderPath(drive, selectedClass);
          if (pathInfo) {
            setPdfsFolderPath(pathInfo);
          }
        }
        
        const dialogOptions: any = {
          filters: [{ name: 'PDF Files', extensions: ['pdf'] }],
          properties: ['openFile']
        };
        
        if (pathInfo && pathInfo.existingPath) {
          dialogOptions.defaultPath = pathInfo.existingPath;
        }
        
        const result = await (window as any).electronAPI.showOpenDialog(dialogOptions);
        
        if (result && !result.canceled && result.filePaths && result.filePaths.length > 0) {
          const filePath = result.filePaths[0];
          addLog(`📄 Selected: ${filePath.split(/[/\\]/).pop()}`);
          await handleSplitPdf(null, filePath);
        }
      } else {
        // Browser mode: Use file upload (works in any browser)
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pdf';
        input.onchange = async (e: any) => {
          const file = e.target.files?.[0];
          if (file) {
            addLog(`📄 Selected: ${file.name}`);
            // Just store the file and set assignment - don't process yet
            setUploadedPdfFile(file);
            const rawAssignmentName = file.name.replace(/\.pdf$/i, '').trim();
            // Format as "{assignment_name} {class_code}" (without "combined PDF")
            const displayName = formatAssignmentDisplayName(rawAssignmentName, selectedClass);
            setLastProcessedAssignment({
              name: displayName,
              className: selectedClass,
              zipPath: ''
            });
          }
        };
        input.click();
      }
    } catch (error) {
      addLog(`❌ Error selecting PDF: ${error}`);
    }
  };
  
  // Handle PDF upload and split (for browser mode)
  const handleSplitPdfUpload = async (file: File) => {
    if (!requireClass()) return;

    setSplitting(true);
    
    try {
      const result = await splitPdfUpload(drive, selectedClass, file, addLog);
      
      if (!result.success) {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setSplitting(false);
    }
  };

  // Split PDF and rezip
  const handleSplitPdf = async (assignmentName: string | null = null, pdfPath: string | null = null) => {
    if (!requireClass()) return;

    // Check if we have an uploaded file (browser mode) instead of a path
    if (!pdfPath && uploadedPdfFile && uploadedPdfFile.name) {
      // Use the uploaded file
      await handleSplitPdfUpload(uploadedPdfFile);
      return;
    }

    setSplitting(true);
    
    try {
      // Determine assignment name:
      // 1. Use provided assignmentName parameter
      // 2. Or use last processed assignment if same class
      // 3. Or extract from PDF filename if pdfPath provided
      let finalAssignmentName = assignmentName;
      
      if (!finalAssignmentName && pdfPath) {
        // Extract assignment name from PDF filename (remove .pdf extension)
        const filename = pdfPath.split(/[/\\]/).pop() || '';
        finalAssignmentName = filename.replace(/\.pdf$/i, '').trim();
      } else if (!finalAssignmentName && lastProcessedAssignment && lastProcessedAssignment.className === selectedClass) {
        finalAssignmentName = lastProcessedAssignment.name;
      }
      
      const result = await splitPdf(drive, selectedClass, finalAssignmentName, pdfPath, addLog);
      
      if (!result.success) {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setSplitting(false);
    }
  };

  // Open folder (grade processing folder or class roster folder based on context)
  const handleOpenFolder = async () => {
    if (!requireClass()) return;
    
    try {
      // If there's a current assignment, open the grade processing folder
      // Otherwise, open the class roster folder
      const openClassFolderOnly = !lastProcessedAssignment || lastProcessedAssignment.className !== selectedClass;
      const result = await openFolder(drive, selectedClass, addLog, openClassFolderOnly);
      
      if (result.success) {
        if (openClassFolderOnly) {
          addLog('✅ Class roster folder opened');
        } else {
          addLog('✅ Grade processing folder opened');
        }
      } else {
        if (result.error?.includes('No grade processing folder found')) {
          addLog('❌ No grade processing folder found');
        } else {
          addLog(`❌ ${result.error}`);
        }
      }
    } catch (error) {
      addLog(`❌ ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Open class roster folder (not the processing folder)
  const handleOpenClassRosterFolder = async () => {
    if (!requireClass()) return;
    
    try {
      // Open class roster folder directly (not the processing folder)
      const result = await openFolder(drive, selectedClass, addLog, true);
      
      if (result.success) {
        addLog('📂 Class roster folder opened');
      } else {
        addLog(`❌ ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Clear all data
  const handleClearAllData = async () => {
    if (!requireClass()) return;

    // If current assignment exists, show options modal
    if (lastProcessedAssignment && lastProcessedAssignment.className === selectedClass) {
      const assignmentName = lastProcessedAssignment.name;
      const folderDisplayName = formatAssignmentFolderName(assignmentName, selectedClass);
      
      setClearOptionsConfig({
        title: 'Clear Current Assignment',
        message: `Select how to clear "${folderDisplayName}":`,
        onConfirm: async (option: ClearOption) => {
          setShowClearOptions(false);
          setClearing(true);
          
          try {
            let saveFoldersAndPdf = false;
            let saveCombinedPdf = false;
            
            if (option === 'saveFoldersAndPdf') {
              saveFoldersAndPdf = true;
            } else if (option === 'saveCombinedPdf') {
              saveCombinedPdf = true;
            }
            // else option === 'deleteAll' - both flags remain false
            
            const result = await clearAllData(
              drive, 
              selectedClass, 
              assignmentName, 
              saveFoldersAndPdf, 
              saveCombinedPdf,
              addLog
            );
            
            if (result.success) {
              // Clear the last processed assignment
              setLastProcessedAssignment(null);
            } else {
              displayError(result.error);
            }
          } catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Unknown error';
            displayError(errorMsg);
          } finally {
            setClearing(false);
          }
        }
      });
      setShowClearOptions(true);
      return;
    }

    // No current assignment - show selection modal
    try {
      const result = await listProcessingFolders(drive, selectedClass);
      
      if (result.success && result.folders && result.folders.length > 0) {
        // Filter out archived folders for normal clear operation
        const processingFolders = result.folders.filter(folder => 
          folder.name.startsWith('grade processing ')
        );
        
        if (processingFolders.length === 0) {
          addLog('❌ No processing folders found for this class');
          return;
        }
        
        setProcessingFolders(processingFolders);
        setSelectedAssignments(new Set()); // Clear previous selections
        setWasSelectAllUsed(false); // Reset flag
        setShowAssignmentSelection(true);
      } else {
        addLog('❌ No processing folders found for this class');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    }
  };
  
  // Handle assignment selection from modal (now handles multiple)
  const handleAssignmentSelection = () => {
    if (selectedAssignments.size === 0) {
      addLog('❌ No assignments selected');
      return;
    }
    
    const assignmentsList: string[] = Array.from(selectedAssignments);
    
    // If "Select All" was used, show options modal
    if (wasSelectAllUsed && assignmentsList.length === processingFolders.length) {
      setShowAssignmentSelection(false);
      setClearOptionsConfig({
        title: 'Clear All Assignments',
        message: `Select how to clear ${assignmentsList.length} assignment(s):`,
        onConfirm: async (option: ClearOption) => {
          setShowClearOptions(false);
          setClearing(true);
          
          try {
            let saveFoldersAndPdf = false;
            let saveCombinedPdf = false;
            
            if (option === 'saveFoldersAndPdf') {
              saveFoldersAndPdf = true;
            } else if (option === 'saveCombinedPdf') {
              saveCombinedPdf = true;
            }
            // else option === 'deleteAll' - both flags remain false
            
            let successCount = 0;
            let failCount = 0;
            
            for (const assignmentName of assignmentsList) {
              const result = await clearAllData(
                drive, 
                selectedClass, 
                assignmentName as string, 
                saveFoldersAndPdf, 
                saveCombinedPdf,
                addLog
              );
              
              if (result.success) {
                successCount++;
              } else {
                failCount++;
                displayError(`  ❌ Failed: ${result.error || 'Unknown error'}`);
              }
            }
            
            // Clear the last processed assignment if it was cleared
            if (lastProcessedAssignment && selectedAssignments.has(lastProcessedAssignment.name)) {
              setLastProcessedAssignment(null);
            }
          } catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Unknown error';
            displayError(errorMsg);
          } finally {
            setClearing(false);
          }
        }
      });
      setShowClearOptions(true);
      return;
    }
    
    // Normal assignment clearing (individual selections) - show options modal
    setShowAssignmentSelection(false);
    setClearOptionsConfig({
      title: 'Clear Assignment',
      message: `Select how to clear ${assignmentsList.length} assignment(s):`,
      onConfirm: async (option: ClearOption) => {
        setShowClearOptions(false);
        setClearing(true);
        
        try {
          let saveFoldersAndPdf = false;
          let saveCombinedPdf = false;
          
          if (option === 'saveFoldersAndPdf') {
            saveFoldersAndPdf = true;
          } else if (option === 'saveCombinedPdf') {
            saveCombinedPdf = true;
          }
          // else option === 'deleteAll' - both flags remain false
          
          let successCount = 0;
          let failCount = 0;
          
          for (const assignmentName of assignmentsList) {
            const result = await clearAllData(
              drive, 
              selectedClass, 
              assignmentName as string, 
              saveFoldersAndPdf, 
              saveCombinedPdf,
              addLog
            );
            
            if (result.success) {
              successCount++;
            } else {
              failCount++;
              displayError(`  ❌ Failed: ${result.error || 'Unknown error'}`);
            }
          }
          
          // Clear the last processed assignment if it was cleared
          if (lastProcessedAssignment && selectedAssignments.has(lastProcessedAssignment.name)) {
            setLastProcessedAssignment(null);
          }
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Unknown error';
          displayError(errorMsg);
        } finally {
          setClearing(false);
        }
      }
    });
    setShowClearOptions(true);
  };
  
  // Handle assignment selection modal close
  const handleAssignmentModalClose = () => {
    setShowAssignmentSelection(false);
    setSelectedAssignments(new Set());
    setWasSelectAllUsed(false);
    setClearing(false);
  };
  
  // Toggle assignment selection
  const handleToggleAssignment = (assignmentName: string) => {
    setSelectedAssignments(prev => {
      const newSet = new Set(prev);
      if (newSet.has(assignmentName)) {
        newSet.delete(assignmentName);
      } else {
        newSet.add(assignmentName);
      }
      // If user manually toggles, reset the select all flag
      if (wasSelectAllUsed && newSet.size !== processingFolders.length) {
        setWasSelectAllUsed(false);
      }
      return newSet;
    });
  };
  
  // Select all assignments
  const handleSelectAll = () => {
    setSelectedAssignments(new Set(processingFolders.map(f => f.name)));
    setWasSelectAllUsed(true);
  };
  
  // Deselect all assignments
  const handleDeselectAll = () => {
    setSelectedAssignments(new Set());
    setWasSelectAllUsed(false);
  };

  return (
    <div className={`h-screen flex flex-col transition-colors ${isDark ? 'bg-[#0a0e1a]' : 'bg-[#d0d0d2]'}`}>
      {/* Top Navigation Bar */}
      <NavigationBar
        isDark={isDark}
        setIsDark={setIsDark}
        selectedClass={selectedClass}
        handleClassChange={handleClassChange}
        classOptions={CLASS_OPTIONS}
        handleOpenDownloads={handleOpenDownloads}
        serverStatus={serverStatus}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />

      {/* ZIP File Selection Modal */}
      <ZipSelectionModal
        isOpen={showZipSelection}
        onClose={handleZipModalClose}
        zipFiles={zipFiles}
        onSelect={handleZipModalSelect}
        isDark={isDark}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />
      
      {/* Assignment Selection Modal for Clear Data */}
      <AssignmentSelectionModal
        isOpen={showAssignmentSelection}
        onClose={handleAssignmentModalClose}
        folders={processingFolders}
        selectedAssignments={selectedAssignments}
        onToggleAssignment={handleToggleAssignment}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
        onConfirm={handleAssignmentSelection}
        isDark={isDark}
        metalButtonClass={metalButtonClass}
        metalButtonStyle={metalButtonStyle}
      />
      
      {/* Confirmation Modal */}
      {confirmationConfig && (
        <ConfirmationModal
          isOpen={showConfirmation}
          onClose={() => {
            setShowConfirmation(false);
            setConfirmationConfig(null);
          }}
          onConfirm={confirmationConfig.onConfirm}
          title={confirmationConfig.title}
          message={confirmationConfig.message}
          confirmText="CLEAR"
          cancelText="CANCEL"
          isDark={isDark}
          metalButtonClass={metalButtonClass}
          metalButtonStyle={metalButtonStyle}
        />
      )}
      
      {/* Clear Options Modal */}
      {clearOptionsConfig && (
        <ClearOptionsModal
          isOpen={showClearOptions}
          onClose={() => {
            setShowClearOptions(false);
            setClearOptionsConfig(null);
          }}
          onConfirm={clearOptionsConfig.onConfirm}
          title={clearOptionsConfig.title}
          message={clearOptionsConfig.message}
          isDark={isDark}
          metalButtonClass={metalButtonClass}
          metalButtonStyle={metalButtonStyle}
        />
      )}

      {/* Main Content Grid */}
      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-3 gap-4 h-full max-h-full">
          {/* Left Column - Actions */}
          <div className="space-y-4">
            {/* Process Quizzes */}
            <ActionCard title="PROCESS QUIZZES" isDark={isDark}>
              <div className="space-y-3">
                <button
                  onClick={handleProcessQuizzes}
                  disabled={!selectedClass || processing || processingCompletion}
                  className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                  style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
                >
                  {processing ? 'PROCESSING...' : 'PROCESS QUIZZES'}
                </button>
                <button
                  onClick={handleProcessCompletion}
                  disabled={!selectedClass || processing || processingCompletion}
                  className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                  style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
                >
                  {processingCompletion ? 'PROCESSING...' : 'PROCESS COMPLETION'}
                </button>
                <label className="flex items-center gap-2 mt-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={dontOverride}
                    onChange={(e) => setDontOverride(e.target.checked)}
                    className="rounded"
                  />
                  <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-700'}`}>
                    Don't override grades
                  </span>
                </label>
              </div>
            </ActionCard>

            {/* Extract Grades */}
            <ActionCard title="EXTRACT GRADES" isDark={isDark}>
              <button
                onClick={handleExtractGrades}
                disabled={!selectedClass || extracting}
                className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
              >
                {extracting ? 'EXTRACTING...' : 'EXTRACT GRADES'}
              </button>
            </ActionCard>

            {/* Split PDF */}
            <ActionCard title="SPLIT PDF" isDark={isDark}>
              {/* Show current assignment being worked on */}
              <div className={`mb-3 p-2 rounded border ${
                isDark ? 'bg-[#1a2942]/50 border-[#2a3952]' : 'bg-[#d0d0d4] border-gray-400'
              }`}>
                <div className="flex items-center justify-between gap-2">
                  <div className="flex-1">
                    <div className={`text-xs uppercase tracking-wider mb-1 ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
                      Current Assignment:
                    </div>
                    {lastProcessedAssignment && lastProcessedAssignment.className === selectedClass ? (
                      <div className={`text-sm font-medium truncate ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                        📄 {lastProcessedAssignment.name}
                      </div>
                    ) : (
                      <div className={`text-sm italic ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                        None
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleSelectPdfFile}
                    disabled={!selectedClass || splitting}
                    className={`px-3 py-1.5 text-xs rounded transition-all border font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                    style={{ ...metalButtonStyle(isDark), fontSize: '11px', padding: '6px 12px' }}
                    title="Select any PDF file to split and rezip"
                  >
                    📄 Upload PDF
                  </button>
                </div>
              </div>
              
              <div className="space-y-3">
                <button
                  onClick={() => handleSplitPdf(lastProcessedAssignment?.name || null, null)}
                  disabled={!selectedClass || splitting || !lastProcessedAssignment || lastProcessedAssignment.className !== selectedClass}
                  className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                  style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
                  title={!lastProcessedAssignment || lastProcessedAssignment.className !== selectedClass ? 'Process quizzes first or select a PDF above' : ''}
                >
                  {splitting ? 'PROCESSING...' : 'SPLIT PDF AND REZIP'}
                </button>
                
                <button
                  onClick={handleOpenFolder}
                  disabled={!selectedClass}
                  className={`w-full rounded-lg transition-all border shadow-lg flex items-center justify-center gap-2 font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                  style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '14px' }}
                  title={lastProcessedAssignment && lastProcessedAssignment.className === selectedClass 
                    ? `Open grade processing folder for ${lastProcessedAssignment.name}`
                    : selectedClass 
                    ? `Open class roster folder for ${selectedClass}`
                    : 'Select a class first'}
                >
                  <FolderOpen size={18} />
                  {lastProcessedAssignment && lastProcessedAssignment.className === selectedClass 
                    ? `OPEN: ${lastProcessedAssignment.name.replace(/\s+combined\s+pdf\s*$/i, '').toUpperCase()}`
                    : selectedClass 
                    ? `OPEN: ${selectedClass.toUpperCase()}`
                    : 'OPEN FOLDER'}
                </button>
              </div>
            </ActionCard>

            {/* Clear Data */}
            <ActionCard title="CLEAR DATA" isDark={isDark} titleColor={isDark ? 'text-red-400' : 'text-red-700'}>
              <div className="flex items-center gap-4">
                <button
                  onClick={handleClearAllData}
                  disabled={!selectedClass || clearing}
                  className={`rounded-lg transition-all border-2 shadow-lg font-bold text-white disabled:opacity-50 disabled:cursor-not-allowed`}
                  style={{ 
                    fontSize: '18px', 
                    padding: '12px 40px',
                    backgroundColor: isDark ? '#dc2626' : '#ef4444',
                    borderColor: isDark ? '#b91c1c' : '#dc2626',
                  }}
                  onMouseEnter={(e) => {
                    if (!clearing && selectedClass) {
                      e.currentTarget.style.backgroundColor = isDark ? '#b91c1c' : '#dc2626';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = isDark ? '#dc2626' : '#ef4444';
                  }}
                >
                  {clearing ? 'CLEARING...' : 'CLEAR'}
                </button>
                
                {/* Show current assignment */}
                <div className={`flex-1 p-2 rounded border ${
                  isDark ? 'bg-[#1a2942]/50 border-[#2a3952]' : 'bg-[#d0d0d4] border-gray-400'
                }`}>
                  <div className={`text-xs uppercase tracking-wider mb-1 ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
                    Current Assignment:
                  </div>
                  {lastProcessedAssignment && lastProcessedAssignment.className === selectedClass ? (
                    <div className={`text-sm font-medium truncate ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                      📄 {lastProcessedAssignment.name}
                    </div>
                  ) : (
                    <div className={`text-sm italic ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                      None
                    </div>
                  )}
                </div>
              </div>
            </ActionCard>
          </div>

          {/* Right Column Spanning 2/3 - Log Terminal */}
          <LogTerminal
            logs={logs}
            isDark={isDark}
            addLog={addLog}
            confidenceScores={confidenceScores}
            drive={drive}
            selectedClass={selectedClass}
          />
        </div>
      </div>
    </div>
  );
}
