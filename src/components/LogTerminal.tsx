import React, { useRef, useEffect } from 'react';
import { killProcesses, openStudentPdf, openCombinedPdf, openImportFile } from '../services/quizGraderService';

interface LogTerminalProps {
  logs: string[];
  isDark: boolean;
  expandedLogging: boolean;
  setExpandedLogging: (value: boolean) => void;
  addLog: (message: string) => void;
  drive: string;
  selectedClass: string;
}

/**
 * Log display terminal with filtering and clickable links
 * Shows processing logs with special handling for PDF links
 */
export default function LogTerminal({
  logs,
  isDark,
  expandedLogging,
  setExpandedLogging,
  addLog,
  drive,
  selectedClass,
}: LogTerminalProps) {
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, expandedLogging]);

  // Filter logs for regular logging mode
  // Since server.js now separates [USER] and [DEV] logs, we only receive user logs
  // So we just need minimal filtering for edge cases
  const shouldShowLog = (log: string, index: number, allLogs: string[]): boolean => {
    if (expandedLogging) return true;
    
    const logTrimmed = log.trim();
    
    // Hide empty lines
    if (!logTrimmed) return false;
    
    // Hide JSON formatted output (shouldn't happen, but just in case)
    if (logTrimmed.startsWith('{') && logTrimmed.includes('"success"')) {
      return false;
    }
    
    // Hide technical prefixes that might slip through (legacy format)
    if (logTrimmed.startsWith('[Python]') || logTrimmed.startsWith('[Python Error]')) {
      return false;
    }
    
    // Hide separator lines
    if (/^[-=]{10,}$/.test(logTrimmed)) {
      return false;
    }
    
    // Show everything else (server already filtered out [DEV] logs)
    return true;
  };

  // Filter and deduplicate logs
  const getFilteredLogs = () => {
    if (expandedLogging) return logs;
    
    const seen = new Set<string>();
    return logs.filter((log, index, arr) => {
      if (!shouldShowLog(log, index, arr)) return false;
      
      // Deduplicate error messages (same content shouldn't appear twice)
      const normalizedLog = log.trim().toLowerCase();
      if (normalizedLog.includes('❌') || normalizedLog.includes('error')) {
        if (seen.has(normalizedLog)) return false;
        seen.add(normalizedLog);
      }
      
      return true;
    });
  };
  
  const filteredLogs = getFilteredLogs();

  const handleKillProcesses = async () => {
    const result = await killProcesses(addLog);
    if (result.success) {
      addLog(`✅ Killed ${result.killed || 0} processes`);
    } else {
      addLog(`❌ ${result.error}`);
    }
  };

  const handleOpenStudentPdf = async (studentName: string) => {
    const result = await openStudentPdf(drive, selectedClass, studentName, addLog);
    if (result.success) {
      addLog(`✅ Opened PDF for ${studentName}`);
    } else {
      addLog(`❌ ${result.error}`);
    }
  };

  const handleOpenCombinedPdf = async () => {
    const result = await openCombinedPdf(drive, selectedClass, addLog);
    if (result.success) {
      addLog('✅ Combined PDF opened');
    } else {
      addLog(`❌ ${result.error}`);
    }
  };

  const handleOpenImportFile = async () => {
    const result = await openImportFile(drive, selectedClass, addLog);
    if (result.success) {
      addLog('✅ Import file opened');
    } else {
      addLog(`❌ ${result.error}`);
    }
  };

  return (
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
              onClick={handleKillProcesses}
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
            // Strip [LOG:LEVEL] prefix if it somehow made it through
            let cleanLog = log;
            const logMatch = log.match(/^\[LOG:(SUCCESS|ERROR|WARNING|INFO)\] (.+)$/);
            if (logMatch) {
              cleanLog = logMatch[2];  // Just the message without prefix
            }
            
            const isError = cleanLog.includes('❌') || cleanLog.toLowerCase().includes('error');
            
            // Check for student PDF patterns
            const hasPdfFound = cleanLog.includes(': PDF found') || cleanLog.match(/: \d+ PDFs? found/i);
            const isStudentLine = hasPdfFound && !cleanLog.toLowerCase().includes('combined pdf') && !cleanLog.toLowerCase().includes('created');
            
            if (isStudentLine) {
              const colonIndex = cleanLog.indexOf(':');
              const extractedName = colonIndex > 0 ? cleanLog.substring(0, colonIndex).trim() : '';
              const hasMultiple = cleanLog.match(/(\d+) PDFs? found/i);
              const pdfCount = hasMultiple ? parseInt(hasMultiple[1]) : 1;
              const suffix = pdfCount > 1 ? ` (${pdfCount} PDFs combined)` : '';
              
              if (extractedName && extractedName.length > 0) {
                return (
                  <div key={index} className={isError ? 'text-red-500' : ''}>
                    <span>   </span>
                    <button
                      onClick={() => handleOpenStudentPdf(extractedName)}
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
                    onClick={handleOpenCombinedPdf}
                    className={`underline cursor-pointer hover:opacity-70 font-bold ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'}`}
                    style={{ textDecoration: 'underline', textUnderlineOffset: '3px' }}
                  >
                    📄 Combined PDF
                  </button>
                  <span className={isDark ? 'text-gray-300' : 'text-gray-700'}> — {submissionCount} submissions (click to open)</span>
                </div>
              );
            }
            
            // Check for completion messages - show import file link
            if (cleanLog.includes('Completion processing completed!') || 
                cleanLog.includes('Grade extraction complete!') ||
                cleanLog.includes('Grade extraction completed successfully!')) {
              return (
                <div key={index} className={isError ? 'text-red-500' : ''}>
                  <div>{cleanLog}</div>
                  <div className="mt-1">
                    <button
                      onClick={handleOpenImportFile}
                      className={`underline cursor-pointer hover:opacity-70 font-bold ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'}`}
                      style={{ textDecoration: 'underline', textUnderlineOffset: '3px' }}
                    >
                      📋 Open Import File
                    </button>
                  </div>
                </div>
              );
            }
            
            // Skip status messages
            if (cleanLog.toLowerCase().includes('opening combined pdf') || 
                cleanLog.toLowerCase().includes('combined pdf ready for manual grading')) {
              return null;
            }
            
            return (
              <div key={index} className={isError ? 'text-red-500' : ''} style={{ whiteSpace: 'pre-wrap' }}>
                {cleanLog}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

