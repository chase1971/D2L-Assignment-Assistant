import React, { useRef, useEffect, useState } from 'react';
import { X } from 'lucide-react';
import { openStudentPdf, openCombinedPdf, openImportFile } from '../services/quizGraderService';

interface ConfidenceScore {
  name: string;
  grade: string;
  confidence: number;
}

interface LogTerminalProps {
  logs: string[];
  isDark: boolean;
  addLog: (message: string) => void;
  drive: string;
  selectedClass: string;
  confidenceScores?: ConfidenceScore[] | null;
}

/**
 * Log display terminal with filtering and clickable links
 * Shows processing logs with special handling for PDF links
 */
export default function LogTerminal({
  logs,
  isDark,
  addLog,
  drive,
  selectedClass,
  confidenceScores,
}: LogTerminalProps) {
  const [showConfidenceModal, setShowConfidenceModal] = useState(false);
  const logContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  // Filter logs for display
  // Since server.js now separates [USER] and [DEV] logs, we only receive user logs
  // So we just need minimal filtering for edge cases
  const shouldShowLog = (log: string): boolean => {
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
    
    // Show everything else (including separator lines, server already filtered out [DEV] logs)
    return true;
  };

  // Filter and deduplicate logs
  const getFilteredLogs = () => {
    const seen = new Set<string>();
    return logs.filter((log) => {
      if (!shouldShowLog(log)) return false;
      
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
        <span className={`font-bold ${isDark ? 'text-gray-400' : 'text-[#1a2942]'}`}>LOG TERMINAL</span>
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
            // Handle format: [LOG:LEVEL] message
            const logMatch = log.match(/^\[LOG:(SUCCESS|ERROR|WARNING|INFO)\] (.+)$/);
            if (logMatch) {
              cleanLog = logMatch[2];  // Just the message without prefix
            }
            // Handle format where [LOG:LEVEL] is on its own line - skip it
            if (log.trim() === '[LOG:INFO]' || log.trim() === '[LOG:WARNING]' || 
                log.trim() === '[LOG:ERROR]' || log.trim() === '[LOG:SUCCESS]') {
              return null;  // Don't render these lines
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
            
            // Check for "Combined PDF created" message with filename
            const combinedPdfMatch = cleanLog.match(/✅ Combined PDF created:\s*(.+)$/i);
            if (combinedPdfMatch) {
              const filename = combinedPdfMatch[1].trim();
              return (
                <div key={index} className={isError ? 'text-red-500' : ''}>
                  <span>✅ Combined PDF created: </span>
                  <button
                    onClick={handleOpenCombinedPdf}
                    className={`underline cursor-pointer hover:opacity-70 font-bold ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'}`}
                    style={{ textDecoration: 'underline', textUnderlineOffset: '3px' }}
                  >
                    📄 {filename}
                  </button>
                </div>
              );
            }
            
            // Legacy check for "Created combined PDF" message (old format)
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
            
            // Check for completion messages - show import file link and confidence scores link
            if (cleanLog.includes('Completion processing completed!') || 
                cleanLog.includes('Grade extraction complete!') ||
                cleanLog.includes('Grade extraction completed successfully!')) {
              return (
                <div key={index} className={isError ? 'text-red-500' : ''}>
                  <div>{cleanLog}</div>
                  <div className="mt-1 flex gap-4">
                    <button
                      onClick={handleOpenImportFile}
                      className={`underline cursor-pointer hover:opacity-70 font-bold ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'}`}
                      style={{ textDecoration: 'underline', textUnderlineOffset: '3px' }}
                    >
                      📋 Open Import File
                    </button>
                    {confidenceScores && confidenceScores.length > 0 && (
                      <button
                        onClick={() => setShowConfidenceModal(true)}
                        className={`underline cursor-pointer hover:opacity-70 font-bold ${isDark ? 'text-cyan-400 hover:text-cyan-300' : 'text-blue-600 hover:text-blue-500'}`}
                        style={{ textDecoration: 'underline', textUnderlineOffset: '3px' }}
                      >
                        📊 View Confidence Scores
                      </button>
                    )}
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
      
      {/* Confidence Scores Modal */}
      {showConfidenceModal && confidenceScores && (
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
          onClick={() => setShowConfidenceModal(false)}
        >
          <div 
            style={{
              width: '400px',
              maxWidth: '90vw',
              maxHeight: '70vh',
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
                padding: '12px 16px',
                backgroundColor: isDark ? '#0f1729' : '#c0c0c4',
                borderBottom: isDark ? '2px solid #3a4962' : '2px solid #999',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexShrink: 0,
              }}
            >
              <span style={{ 
                fontWeight: 'bold', 
                fontSize: '14px',
                color: isDark ? '#fff' : '#1a2942'
              }}>
                Confidence Scores
              </span>
              <button
                onClick={() => setShowConfidenceModal(false)}
                style={{
                  padding: '4px',
                  borderRadius: '4px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  cursor: 'pointer',
                  color: isDark ? '#888' : '#666',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#ff4444'}
                onMouseLeave={(e) => e.currentTarget.style.color = isDark ? '#888' : '#666'}
              >
                <X size={18} />
              </button>
            </div>
            
            {/* Scrollable Content */}
            <div 
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '12px',
                backgroundColor: isDark ? '#0f1729' : '#b8b8bc',
              }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {confidenceScores
                  .sort((a, b) => b.confidence - a.confidence)
                  .map((score, idx) => {
                    const confidenceColor = score.confidence >= 0.7 
                      ? (isDark ? '#4ade80' : '#16a34a')
                      : score.confidence >= 0.4
                      ? (isDark ? '#fbbf24' : '#ca8a04')
                      : (isDark ? '#f87171' : '#dc2626');
                    
                    return (
                      <div 
                        key={idx}
                        style={{
                          backgroundColor: isDark ? '#1a2942' : '#d0d0d4',
                          border: isDark ? '1px solid #3a4962' : '1px solid #999',
                          borderRadius: '6px',
                          padding: '10px 12px',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ 
                            fontWeight: '500',
                            fontSize: '13px',
                            color: isDark ? '#e0e0e0' : '#1a2942',
                            marginBottom: '4px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}>
                            {score.name}
                          </div>
                          <div style={{ 
                            fontSize: '11px',
                            color: isDark ? '#888' : '#666',
                          }}>
                            Grade: {score.grade}
                          </div>
                        </div>
                        <div style={{ 
                          color: confidenceColor,
                          fontWeight: '600',
                          fontSize: '13px',
                          marginLeft: '12px',
                          flexShrink: 0,
                        }}>
                          {(score.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                    );
                  })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

