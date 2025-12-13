import React, { useState, useEffect } from 'react';
import { FolderOpen } from 'lucide-react';
import ZipSelectionModal from './ZipSelectionModal';
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
  openFolder,
  openDownloads,
  clearAllData,
  checkServerStatus
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
  const [expandedLogging, setExpandedLogging] = useState(false);
  const [dontOverride, setDontOverride] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  
  // Processing states
  const [processing, setProcessing] = useState(false);
  const [processingCompletion, setProcessingCompletion] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [splitting, setSplitting] = useState(false);
  const [clearing, setClearing] = useState(false);
  
  // ZIP selection state
  const [zipFiles, setZipFiles] = useState<Array<{ index: number; filename: string; path: string }>>([]);
  const [showZipSelection, setShowZipSelection] = useState(false);
  const [zipSelectionMode, setZipSelectionMode] = useState<'quiz' | 'completion'>('quiz');
  
  // Track last processed assignment (for Split PDF visibility)
  const [lastProcessedAssignment, setLastProcessedAssignment] = useState<{
    name: string;
    className: string;
    zipPath: string;
  } | null>(null);
  
  // Server status state
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  
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

  // Add log helper
  const addLog = (message: string) => {
    if (message) {
      setLogs(prevLogs => [...prevLogs, message]);
    }
  };

  // Get theme styles from hook
  const { metalButtonClass, metalButtonStyle } = useThemeStyles();

  // Handle class selection
  const handleClassChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newClass = e.target.value;
    setSelectedClass(newClass);
    if (newClass) {
      addLog(`✅ Class loaded: ${newClass}`);
    }
  };

  // Refresh classes
  const handleRefresh = async () => {
    addLog('📂 Loading classes from Rosters etc folder...');
    try {
      const result = await listClasses(drive);
      if (result.success && result.classes) {
        addLog(`✅ Found ${result.classes.length} classes`);
      } else {
        if (result.error?.includes('Could not find roster folder')) {
          addLog('❌ Could not find roster folder');
        } else {
          addLog(`❌ ${result.error}`);
        }
      }
    } catch (error) {
      addLog(`❌ Error loading classes: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Open Downloads folder
  const handleOpenDownloads = async () => {
    addLog('📁 Opening Downloads folder...');
    try {
      const result = await openDownloads(addLog);
      if (result.success) {
        addLog('✅ Downloads folder opened successfully!');
      } else {
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Process quizzes
  const handleProcessQuizzes = async () => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

    setProcessing(true);
    addLog('🔍 Searching for assignment ZIP in Downloads...');
    
    try {
      const result = await processQuizzes(drive, selectedClass, addLog);
      
      if (result.success) {
        addLog('✅ Quiz processing completed!');
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
        addLog('✅ Quiz processing completed!');
        // Extract assignment name from ZIP filename (remove "Download..." suffix)
        const assignmentName = zipFilename.replace(/\s*Download.*\.zip$/i, '').trim();
        setLastProcessedAssignment({
          name: assignmentName || zipFilename,
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
        // Extract assignment name from ZIP filename (remove "Download..." suffix)
        const assignmentName = zipFilename.replace(/\s*Download.*\.zip$/i, '').trim();
        setLastProcessedAssignment({
          name: assignmentName || zipFilename,
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
      setProcessingCompletion(false);
    }
  };

  // Process completion
  const handleProcessCompletion = async () => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

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
    
    // Remove "Error:" prefix if present
    let cleanError = error.replace(/^Error:\s*/i, '').trim();
    
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
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

    setExtracting(true);
    addLog('🔬 Starting grade extraction...');
    
    try {
      const result = await extractGrades(drive, selectedClass, addLog);
      
      if (result.success) {
        addLog('✅ Grade extraction completed successfully!');
      } else {
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

  // Split PDF and rezip
  const handleSplitPdf = async () => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

    setSplitting(true);
    addLog('📦 Starting PDF split and rezip...');
    
    try {
      // Get assignment name from last processed assignment
      const assignmentName = lastProcessedAssignment && lastProcessedAssignment.className === selectedClass
        ? lastProcessedAssignment.name
        : null;
      
      const result = await splitPdf(drive, selectedClass, assignmentName, addLog);
      
      if (result.success) {
        addLog('✅ Split PDF and rezip completed!');
      } else {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setSplitting(false);
    }
  };

  // Open folder
  const handleOpenFolder = async () => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

    addLog('📂 Opening grade processing folder...');
    
    try {
      const result = await openFolder(drive, selectedClass, addLog);
      
      if (result.success) {
        addLog('✅ Grade processing folder opened!');
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

  // Clear all data
  const handleClearAllData = async () => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

    if (!window.confirm('⚠️ This will delete the grade processing folder and Canvas ZIP file. Continue?')) {
      return;
    }

    setClearing(true);
    addLog('🗑️ Clearing all processing data...');
    
    try {
      const result = await clearAllData(drive, selectedClass, addLog);
      
      if (result.success) {
        addLog('✅ All data cleared successfully!');
        // Clear the last processed assignment if it was for this class
        if (lastProcessedAssignment?.className === selectedClass) {
          setLastProcessedAssignment(null);
        }
      } else {
        displayError(result.error);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      displayError(errorMsg);
    } finally {
      setClearing(false);
    }
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
        handleRefresh={handleRefresh}
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
                <div className={`text-xs uppercase tracking-wider mb-1 ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
                  Current Assignment:
                </div>
                {lastProcessedAssignment && lastProcessedAssignment.className === selectedClass ? (
                  <button
                    onClick={handleOpenFolder}
                    className={`text-sm font-medium truncate block w-full text-left hover:opacity-80 ${
                      isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'
                    }`}
                    style={{ textDecoration: 'underline', textUnderlineOffset: '2px' }}
                    title={`Click to open folder\n${lastProcessedAssignment.name}`}
                  >
                    📄 {lastProcessedAssignment.name}
                  </button>
                ) : (
                  <div className={`text-sm italic ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                    No assignment processed yet
                  </div>
                )}
              </div>
              
              <div className="space-y-3">
                <button
                  onClick={handleSplitPdf}
                  disabled={!selectedClass || splitting || !lastProcessedAssignment || lastProcessedAssignment.className !== selectedClass}
                  className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                  style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
                  title={!lastProcessedAssignment || lastProcessedAssignment.className !== selectedClass ? 'Process quizzes first' : ''}
                >
                  {splitting ? 'PROCESSING...' : 'SPLIT PDF AND REZIP'}
                </button>
                <button
                  onClick={handleOpenFolder}
                  disabled={!selectedClass}
                  className={`w-full rounded-lg transition-all border shadow-lg flex items-center justify-center gap-2 font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                  style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
                >
                  <FolderOpen size={18} />
                  OPEN FOLDER
                </button>
              </div>
            </ActionCard>

            {/* Clear Data */}
            <ActionCard title="CLEAR DATA" isDark={isDark} titleColor={isDark ? 'text-red-400' : 'text-red-700'}>
              <button
                onClick={handleClearAllData}
                disabled={!selectedClass || clearing}
                className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
              >
                {clearing ? 'CLEARING...' : 'CLEAR ALL DATA'}
              </button>
            </ActionCard>
          </div>

          {/* Right Column Spanning 2/3 - Log Terminal */}
          <LogTerminal
            logs={logs}
            isDark={isDark}
            expandedLogging={expandedLogging}
            setExpandedLogging={setExpandedLogging}
            addLog={addLog}
            drive={drive}
            selectedClass={selectedClass}
          />
        </div>
      </div>
    </div>
  );
}
