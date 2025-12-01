import React, { useState, useRef, useEffect } from 'react';
import { Settings, RotateCw, X, FolderOpen, Folder, Sun, Moon, Minus, Square } from 'lucide-react';
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
  closeWindow,
  reloadWindow,
  minimizeWindow,
  maximizeWindow
} from '../services/quizGraderService';

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
  
  const logContainerRef = useRef<HTMLDivElement>(null);
  
  // Server status state
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  
  // Check server status periodically
  useEffect(() => {
    const checkServer = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/test', {
          method: 'GET',
          signal: AbortSignal.timeout(2000) // 2 second timeout
        });
        if (response.ok) {
          setServerStatus('online');
        } else {
          setServerStatus('offline');
        }
      } catch {
        setServerStatus('offline');
      }
    };
    
    // Check immediately
    checkServer();
    
    // Check every 3 seconds
    const interval = setInterval(checkServer, 3000);
    
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, expandedLogging]);

  // Add log helper
  const addLog = (message: string) => {
    if (message) {
      setLogs(prevLogs => [...prevLogs, message]);
    }
  };

  // Metallic button styling matching Figma design
  const metalButtonClass = (isDark: boolean, textColor?: string) => 
    isDark 
      ? `bg-gradient-to-b from-[#4a4a4c] to-[#3a3a3c] ${textColor || 'text-gray-200'} hover:from-[#5a5a5c] hover:to-[#4a4a4c] border-[#5a5a5c] shadow-black/50`
      : `bg-gradient-to-b from-[#d8d8dc] via-[#c8c8cc] to-[#b8b8bc] ${textColor || 'text-gray-800'} hover:from-[#e0e0e4] hover:to-[#c8c8cc] border-gray-400 shadow-gray-500/50`;

  const metalButtonStyle = (isDark: boolean): React.CSSProperties | undefined => isDark 
    ? undefined 
    : {
        backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.15) 25%, transparent 50%, rgba(0,0,0,0.05) 75%, rgba(0,0,0,0.15) 100%), linear-gradient(180deg, #e8e8ec 0%, #d8d8dc 20%, #c8c8cc 50%, #b8b8bc 80%, #a8a8ac 100%)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.5), inset 0 -1px 0 rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.2)'
      };

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
        addLog(`❌ Error: ${result.error}`);
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
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Process quizzes
  const handleProcessQuizzes = async () => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

    setProcessing(true);
    addLog('🔍 Searching for Canvas ZIP in Downloads...');
    
    try {
      const result = await processQuizzes(drive, selectedClass, addLog);
      
      if (result.success) {
        addLog('✅ Quiz processing completed!');
        addLog('📂 Combined PDF ready for manual grading');
      } else if (result.error === 'Multiple ZIP files found') {
        setZipFiles(result.zip_files || []);
        setZipSelectionMode('quiz');
        setShowZipSelection(true);
        addLog('📁 Multiple ZIP files found - please select one');
        return;
      } else {
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setProcessing(false);
    }
  };

  // Handle ZIP file selection for quizzes
  const handleZipSelection = async (zipPath: string) => {
    setShowZipSelection(false);
    setProcessing(true);
    const zipFilename = zipPath.split('\\').pop() || '';
    addLog(`📁 Processing selected ZIP file: ${zipFilename}`);
    
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
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setProcessing(false);
    }
  };

  // Process completion
  const handleProcessCompletion = async () => {
    if (!selectedClass) {
      addLog('❌ Please select a class first');
      return;
    }

    setProcessingCompletion(true);
    addLog('🔍 Searching for Canvas ZIP in Downloads...');
    
    try {
      const result = await processCompletion(drive, selectedClass, dontOverride, addLog);
      
      if (result.success) {
        addLog('✅ Completion processing completed!');
        addLog('✅ Auto-assigned 10 points to all submissions');
      } else if (result.error === 'Multiple ZIP files found') {
        setZipFiles(result.zip_files || []);
        setZipSelectionMode('completion');
        setShowZipSelection(true);
        addLog('📁 Multiple ZIP files found - please select one');
        return;
      } else {
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setProcessingCompletion(false);
    }
  };

  // Handle ZIP file selection for completions
  const handleCompletionZipSelection = async (zipPath: string) => {
    setShowZipSelection(false);
    setProcessingCompletion(true);
    const zipFilename = zipPath.split('\\').pop() || '';
    addLog(`📁 Processing selected ZIP file: ${zipFilename}`);
    
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
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setProcessingCompletion(false);
    }
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
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
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
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
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
        if (result.message?.includes('no grade processing folder found')) {
          addLog('📁 Class folder opened (no grade processing folder found)');
        } else {
          addLog('✅ Grade processing folder opened!');
        }
      } else {
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
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
        addLog(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setClearing(false);
    }
  };

  // Filter logs for regular logging mode
  const shouldShowLog = (log: string): boolean => {
    if (expandedLogging) return true;
    
    const logLower = log.toLowerCase();
    const logTrimmed = log.trim();
    
    // Show emoji messages
    if (/^[🔬📦✅❌⚠️📡🔍📁📄📊📝📂🗑️]/.test(logTrimmed)) {
      return true;
    }
    
    // Show errors
    if (logLower.includes('error') || logLower.includes('❌') || logLower.includes('failed')) {
      return true;
    }
    
    // Hide technical messages
    if (logLower.includes('📡 sending')) {
      return false;
    }
    
    return true;
  };

  const filteredLogs = expandedLogging ? logs : logs.filter(shouldShowLog);

  return (
    <div className={`h-screen flex flex-col transition-colors ${isDark ? 'bg-[#0a0e1a]' : 'bg-[#d0d0d2]'}`}>
      {/* Top Navigation Bar */}
      <div className={`border-b ${
        isDark 
          ? 'bg-[#0f1729] border-[#1a2942]' 
          : 'bg-[#e0e0e3] border-gray-400'
      }`}>
        <div 
          className="flex items-center justify-between px-6 py-3"
          style={{ WebkitAppRegion: 'drag' } as React.CSSProperties}
        >
          <div className="flex items-center gap-3" style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
            <h1 className={`font-bold tracking-wider ${isDark ? 'text-cyan-400' : 'text-[#1a2942]'}`}>
              QUIZ GRADER
            </h1>
            
            {/* Server Status Indicator */}
            <div 
              className="flex items-center gap-2 px-3 py-1 rounded-full border"
              style={{
                backgroundColor: serverStatus === 'online' 
                  ? (isDark ? 'rgba(34, 197, 94, 0.2)' : 'rgba(34, 197, 94, 0.15)')
                  : serverStatus === 'offline'
                  ? (isDark ? 'rgba(239, 68, 68, 0.2)' : 'rgba(239, 68, 68, 0.15)')
                  : (isDark ? 'rgba(234, 179, 8, 0.2)' : 'rgba(234, 179, 8, 0.15)'),
                borderColor: serverStatus === 'online' 
                  ? (isDark ? 'rgb(34, 197, 94)' : 'rgb(22, 163, 74)')
                  : serverStatus === 'offline'
                  ? (isDark ? 'rgb(239, 68, 68)' : 'rgb(220, 38, 38)')
                  : (isDark ? 'rgb(234, 179, 8)' : 'rgb(202, 138, 4)'),
              }}
              title={serverStatus === 'online' ? 'Backend server is running' : serverStatus === 'offline' ? 'Backend server is NOT running' : 'Checking server...'}
            >
              {/* Pulsing dot */}
              <div 
                className={`w-3 h-3 rounded-full ${serverStatus === 'online' ? 'animate-pulse' : ''}`}
                style={{
                  backgroundColor: serverStatus === 'online' 
                    ? 'rgb(34, 197, 94)' 
                    : serverStatus === 'offline'
                    ? 'rgb(239, 68, 68)'
                    : 'rgb(234, 179, 8)',
                  boxShadow: serverStatus === 'online'
                    ? '0 0 8px rgb(34, 197, 94)'
                    : serverStatus === 'offline'
                    ? '0 0 8px rgb(239, 68, 68)'
                    : '0 0 8px rgb(234, 179, 8)',
                }}
              />
              <span 
                className="text-xs font-semibold uppercase"
                style={{
                  color: serverStatus === 'online' 
                    ? (isDark ? 'rgb(134, 239, 172)' : 'rgb(22, 163, 74)')
                    : serverStatus === 'offline'
                    ? (isDark ? 'rgb(252, 165, 165)' : 'rgb(220, 38, 38)')
                    : (isDark ? 'rgb(253, 224, 71)' : 'rgb(161, 98, 7)'),
                }}
              >
                {serverStatus === 'online' ? 'SERVER ON' : serverStatus === 'offline' ? 'SERVER OFF' : 'CHECKING...'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2" style={{ WebkitAppRegion: 'no-drag' } as React.CSSProperties}>
            <select
              value={selectedClass}
              onChange={handleClassChange}
              className={`px-3 py-1.5 rounded-lg border text-sm ${
                isDark
                  ? 'bg-[#1a2942] border-[#2a3952] text-gray-300'
                  : 'bg-white border-gray-400 text-gray-800'
              }`}
            >
              {CLASS_OPTIONS.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>

            <button
              onClick={handleRefresh}
              className={`px-3 py-1.5 rounded-lg transition-all border shadow-lg text-sm font-medium ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
            >
              REFRESH
            </button>

            <button
              onClick={handleOpenDownloads}
              className={`px-3 py-1.5 rounded-lg transition-all border shadow-lg flex items-center gap-2 text-sm font-medium ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
            >
              <Folder size={14} />
              DOWNLOADS
            </button>

            <div className="w-px h-6 bg-gray-400 mx-2"></div>

            <button
              onClick={() => setIsDark(!isDark)}
              className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
              title={isDark ? 'Light Mode' : 'Dark Mode'}
            >
              {isDark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
            
            <button
              className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
              title="Settings"
            >
              <Settings size={16} />
            </button>

            <button
              onClick={reloadWindow}
              className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
              title="Reload"
            >
              <RotateCw size={16} />
            </button>

            <div className="w-px h-6 bg-gray-400 mx-2"></div>

            <button
              onClick={minimizeWindow}
              className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
              title="Minimize"
            >
              <Minus size={16} />
            </button>

            <button
              onClick={maximizeWindow}
              className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
              style={metalButtonStyle(isDark)}
              title="Maximize"
            >
              <Square size={16} />
            </button>

            <button
              onClick={closeWindow}
              className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark, isDark ? 'text-red-400' : 'text-red-700')}`}
              style={{
                ...metalButtonStyle(isDark),
                backgroundImage: isDark 
                  ? undefined 
                  : 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.15) 25%, transparent 50%, rgba(0,0,0,0.05) 75%, rgba(0,0,0,0.15) 100%), linear-gradient(180deg, #f0c0c0 0%, #e0a0a0 20%, #d08080 50%, #c06060 80%, #b04040 100%)'
              }}
              title="Close"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* ZIP File Selection Popup Menu */}
      {showZipSelection && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 999999,
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowZipSelection(false);
              setProcessing(false);
              setProcessingCompletion(false);
            }
          }}
        >
          <div 
            style={{
              width: '550px',
              maxWidth: '95vw',
              maxHeight: '80vh',
              backgroundColor: isDark ? '#1a2942' : '#d0d0d4',
              borderRadius: '12px',
              border: isDark ? '2px solid #3a4962' : '2px solid #888',
              boxShadow: '0 25px 60px rgba(0, 0, 0, 0.5)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div 
              style={{
                padding: '16px 20px',
                backgroundColor: isDark ? '#0f1729' : '#c0c0c4',
                borderBottom: isDark ? '2px solid #3a4962' : '2px solid #999',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexShrink: 0,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Folder className={isDark ? 'text-cyan-400' : 'text-[#1a2942]'} size={20} />
                <span style={{ 
                  fontWeight: 'bold', 
                  fontSize: '14px',
                  color: isDark ? '#fff' : '#1a2942'
                }}>
                  SELECT ZIP FILE
                </span>
                <span style={{ 
                  fontSize: '12px',
                  color: isDark ? '#888' : '#666'
                }}>
                  ({zipFiles.length} found)
                </span>
              </div>
              <button
                onClick={() => {
                  setShowZipSelection(false);
                  setProcessing(false);
                  setProcessingCompletion(false);
                }}
                style={{
                  padding: '4px',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  cursor: 'pointer',
                  color: isDark ? '#888' : '#666',
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#ff4444'}
                onMouseLeave={(e) => e.currentTarget.style.color = isDark ? '#888' : '#666'}
              >
                <X size={20} />
              </button>
            </div>

            {/* Scrollable File List */}
            <div 
              style={{
                flex: 1,
                overflowY: 'auto',
                backgroundColor: isDark ? '#0f1729' : '#b8b8bc',
                maxHeight: 'calc(80vh - 140px)',
              }}
            >
              {zipFiles.map((zipFile) => (
                <button
                  key={zipFile.index}
                  onClick={() => {
                    if (zipSelectionMode === 'quiz') {
                      handleZipSelection(zipFile.path);
                    } else {
                      handleCompletionZipSelection(zipFile.path);
                    }
                  }}
                  style={{
                    width: '100%',
                    padding: '12px 20px',
                    textAlign: 'left',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    backgroundColor: 'transparent',
                    border: 'none',
                    borderBottom: isDark ? '1px solid #2a3952' : '1px solid #999',
                    cursor: 'pointer',
                    transition: 'background-color 0.15s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDark ? 'rgba(0, 200, 255, 0.15)' : 'rgba(255, 255, 255, 0.5)'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <Folder 
                    size={16} 
                    style={{ 
                      flexShrink: 0,
                      color: isDark ? '#00c8ff' : '#1a2942'
                    }} 
                  />
                  <span style={{ 
                    fontSize: '13px',
                    color: isDark ? '#e0e0e0' : '#333',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {zipFile.filename}
                  </span>
                </button>
              ))}
            </div>

            {/* Footer */}
            <div 
              style={{
                padding: '16px 20px',
                backgroundColor: isDark ? '#1a2942' : '#c0c0c4',
                borderTop: isDark ? '2px solid #3a4962' : '2px solid #999',
                flexShrink: 0,
              }}
            >
              <button
                onClick={() => {
                  setShowZipSelection(false);
                  setProcessing(false);
                  setProcessingCompletion(false);
                }}
                className={`w-full px-4 py-2 rounded-lg transition-all text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
                style={metalButtonStyle(isDark)}
              >
                CANCEL
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-3 gap-4 h-full max-h-full">
          {/* Left Column - Actions */}
          <div className="space-y-4">
            {/* Process Quizzes */}
            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <h3 className={`mb-3 text-base font-bold ${isDark ? 'text-gray-300' : 'text-[#1a2942]'}`}>PROCESS QUIZZES</h3>
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
            </div>

            {/* Extract Grades */}
            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <h3 className={`mb-3 text-base font-bold ${isDark ? 'text-gray-300' : 'text-[#1a2942]'}`}>EXTRACT GRADES</h3>
              <button
                onClick={handleExtractGrades}
                disabled={!selectedClass || extracting}
                className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
              >
                {extracting ? 'EXTRACTING...' : 'EXTRACT GRADES'}
              </button>
            </div>

            {/* Split PDF */}
            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <h3 className={`mb-3 text-base font-bold ${isDark ? 'text-gray-300' : 'text-[#1a2942]'}`}>SPLIT PDF</h3>
              
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
            </div>

            {/* Clear Data */}
            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <h3 className={`mb-3 text-base font-bold ${isDark ? 'text-red-400' : 'text-red-700'}`}>CLEAR DATA</h3>
              <button
                onClick={handleClearAllData}
                disabled={!selectedClass || clearing}
                className={`w-full rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)} disabled:opacity-50 disabled:cursor-not-allowed`}
                style={{ ...metalButtonStyle(isDark), padding: '16px 16px', fontSize: '16px' }}
              >
                {clearing ? 'CLEARING...' : 'CLEAR ALL DATA'}
              </button>
            </div>
          </div>

          {/* Right Column Spanning 2/3 - Log Terminal */}
          <div className={`col-span-2 rounded-lg border overflow-hidden flex flex-col ${
            isDark 
              ? 'bg-[#0f1729] border-[#1a2942]' 
              : 'bg-[#e0e0e3] border-gray-400'
          }`}>
            <div className={`p-3 border-b ${
              isDark 
                ? 'border-[#1a2942]' 
                : 'border-gray-400'
            }`}>
              <div className="flex items-center justify-between">
                <span className={`font-bold ${isDark ? 'text-gray-400' : 'text-[#1a2942]'}`}>LOG TERMINAL</span>
                <div className="flex items-center gap-3">
                  <button
                    onClick={async () => {
                      try {
                        addLog('🔄 Killing all Node processes...');
                        const response = await fetch('http://localhost:5000/api/kill-processes', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' }
                        });
                        const result = await response.json();
                        if (result.success) {
                          addLog(`✅ Killed ${result.killed || 0} processes`);
                        } else {
                          addLog(`❌ Error: ${result.error}`);
                        }
                      } catch (err) {
                        addLog('❌ Error killing processes');
                      }
                    }}
                    className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                      isDark 
                        ? 'bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/50' 
                        : 'bg-red-100 hover:bg-red-200 text-red-700 border border-red-300'
                    }`}
                    title="Kill all Node processes"
                  >
                    🔄 Kill Processes
                  </button>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={expandedLogging}
                      onChange={(e) => setExpandedLogging(e.target.checked)}
                      className="rounded"
                    />
                    <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-700'}`}>
                      Expanded Logging
                    </span>
                  </label>
                </div>
              </div>
            </div>
            <div 
              ref={logContainerRef}
              className={`flex-1 p-4 text-base overflow-auto ${
                isDark ? 'text-green-400 bg-[#0a0e1a]' : 'text-[#006600] bg-[#c8c8cc]'
              }`}
            >
              {filteredLogs.length === 0 ? (
                <div className="opacity-60">Awaiting commands...</div>
              ) : (
                filteredLogs.map((log, index) => {
                  const isError = log.includes('❌') || log.toLowerCase().includes('error');
                  
                  // Check for student PDF patterns:
                  // "   StudentName: PDF found"
                  // "   StudentName: 2 PDFs found, combining"
                  // "   StudentName: PDF found → 10 points"
                  // Simple check: contains ": PDF found" or ": X PDFs found"
                  const hasPdfFound = log.includes(': PDF found') || log.match(/: \d+ PDFs? found/i);
                  const isStudentLine = hasPdfFound && !log.toLowerCase().includes('combined pdf') && !log.toLowerCase().includes('created');
                  
                  if (isStudentLine) {
                    // Extract student name - everything before ": PDF" or ": X PDF"
                    const colonIndex = log.indexOf(':');
                    const extractedName = colonIndex > 0 ? log.substring(0, colonIndex).trim() : '';
                    const hasMultiple = log.match(/(\d+) PDFs? found/i);
                    const pdfCount = hasMultiple ? parseInt(hasMultiple[1]) : 1;
                    const suffix = pdfCount > 1 ? ` (${pdfCount} PDFs combined)` : '';
                    
                    if (extractedName && extractedName.length > 0) {
                      return (
                        <div key={index} className={isError ? 'text-red-500' : ''}>
                          <span>   </span>
                          <button
                            onClick={async () => {
                              addLog(`📂 Opening PDF for: ${extractedName}`);
                              try {
                                const response = await fetch('http://localhost:5000/api/open-student-pdf', {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  body: JSON.stringify({ drive, className: selectedClass, studentName: extractedName })
                                });
                                const result = await response.json();
                                if (result.success) {
                                  addLog(`✅ Opened PDF for ${extractedName}`);
                                } else {
                                  addLog(`❌ ${result.error}`);
                                }
                              } catch { addLog('❌ Error opening PDF'); }
                            }}
                            className={`underline cursor-pointer hover:opacity-70 font-medium ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'}`}
                            style={{ textDecoration: 'underline', textUnderlineOffset: '2px' }}
                          >
                            📄 {extractedName}
                          </button>
                          <span className={isDark ? 'text-gray-400' : 'text-gray-600'}> — PDF{suffix}</span>
                        </div>
                      );
                    }
                  }
                  
                  // Check for "Created combined PDF" message
                  const combinedMatch = log.match(/Created combined PDF[:\s]*(\d+)\s*submissions/i);
                  if (combinedMatch) {
                    const submissionCount = combinedMatch[1];
                    return (
                      <div key={index} className={isError ? 'text-red-500' : ''}>
                        <span>✅ Created </span>
                        <button
                          onClick={async () => {
                            addLog('📂 Opening combined PDF...');
                            try {
                              const response = await fetch('http://localhost:5000/api/open-combined-pdf', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ drive, className: selectedClass })
                              });
                              const result = await response.json();
                              if (result.success) {
                                addLog('✅ Combined PDF opened');
                              } else {
                                addLog(`❌ ${result.error}`);
                              }
                            } catch { addLog('❌ Error opening PDF'); }
                          }}
                          className={`underline cursor-pointer hover:opacity-70 font-bold ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'}`}
                          style={{ textDecoration: 'underline', textUnderlineOffset: '3px' }}
                        >
                          📄 Combined PDF
                        </button>
                        <span className={isDark ? 'text-gray-300' : 'text-gray-700'}> — {submissionCount} submissions (click to open)</span>
                      </div>
                    );
                  }
                  
                  // Skip "Opening combined PDF for manual grading" and "Combined PDF ready for manual grading" - these are just status messages
                  if (log.toLowerCase().includes('opening combined pdf') || 
                      log.toLowerCase().includes('combined pdf ready for manual grading')) {
                    return null; // Don't show these lines at all
                  }
                  
                  return (
                    <div key={index} className={isError ? 'text-red-500' : ''}>
                      {log}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
