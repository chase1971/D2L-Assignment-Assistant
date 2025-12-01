import React, { useState } from 'react';
import { Settings, RotateCw, X, FolderOpen, Folder, Sun, Moon } from 'lucide-react';

// Option 3: Compact Dashboard with 50/50 Split (Actions Left, Logs Right)
export default function Option3() {
  const [isDark, setIsDark] = useState(false);
  const [selectedClass, setSelectedClass] = useState('');
  const [expandedLogging, setExpandedLogging] = useState(false);
  const [dontOverride, setDontOverride] = useState(false);
  const [logs, setLogs] = useState('Awaiting commands...');

  const metalButtonClass = (isDark: boolean, textColor?: string) => 
    isDark 
      ? `bg-gradient-to-b from-[#4a4a4c] to-[#3a3a3c] ${textColor || 'text-gray-200'} hover:from-[#5a5a5c] hover:to-[#4a4a4c] border-[#5a5a5c] shadow-black/50`
      : `bg-gradient-to-b from-[#d8d8dc] via-[#c8c8cc] to-[#b8b8bc] ${textColor || 'text-gray-800'} hover:from-[#e0e0e4] hover:to-[#c8c8cc] border-gray-400 shadow-gray-500/50`;

  const metalButtonStyle = (isDark: boolean) => isDark 
    ? undefined 
    : {
        backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.15) 25%, transparent 50%, rgba(0,0,0,0.05) 75%, rgba(0,0,0,0.15) 100%), linear-gradient(180deg, #e8e8ec 0%, #d8d8dc 20%, #c8c8cc 50%, #b8b8bc 80%, #a8a8ac 100%)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.5), inset 0 -1px 0 rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.2)'
      };

  return (
    <div className={`h-screen flex flex-col transition-colors ${isDark ? 'bg-[#0a0e1a]' : 'bg-[#d0d0d2]'}`}>
      {/* Compact Header */}
      <div className={`px-4 py-2 border-b flex items-center justify-between ${
        isDark 
          ? 'bg-[#0f1729] border-[#1a2942]' 
          : 'bg-[#e0e0e3] border-gray-400'
      }`}>
        <div className="flex items-center gap-4">
          <h1 className={`tracking-wider text-lg font-bold ${isDark ? 'text-cyan-400' : 'text-[#1a2942]'}`}>
            QUIZ GRADER
          </h1>
          
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className={`px-3 py-1 rounded-lg border text-sm ${
              isDark
                ? 'bg-[#1a2942] border-[#2a3952] text-gray-300'
                : 'bg-white border-gray-400 text-gray-800'
            }`}
          >
            <option value="">Select Class</option>
            <option value="class1">Class 1</option>
            <option value="class2">Class 2</option>
          </select>

          <button
            className={`px-3 py-1 rounded-lg transition-all border shadow-lg text-sm font-medium ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            REFRESH
          </button>

          <button
            className={`px-3 py-1 rounded-lg transition-all border shadow-lg flex items-center gap-1 text-sm font-medium ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            <Folder size={14} />
            DOWNLOADS
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsDark(!isDark)}
            className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            {isDark ? <Sun size={14} /> : <Moon size={14} />}
          </button>
          
          <button
            className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            <Settings size={14} />
          </button>

          <button
            className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            <RotateCw size={14} />
          </button>

          <button
            className={`p-1.5 rounded-lg transition-all border shadow-lg ${metalButtonClass(isDark, isDark ? 'text-red-400' : 'text-red-700')}`}
            style={metalButtonStyle(isDark)}
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Main 50/50 Split */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - All Actions */}
        <div className={`w-1/2 border-r overflow-auto ${
          isDark 
            ? 'bg-[#0a0e1a] border-[#1a2942]' 
            : 'bg-[#d0d0d2] border-gray-400'
        }`}>
          <div className="p-4 space-y-3">
            {/* Process Quizzes Section */}
            <div className={`rounded-lg border p-3 ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <div className={`mb-2 text-xs tracking-wide font-bold ${isDark ? 'text-gray-400' : 'text-[#1a2942]'}`}>
                PROCESS QUIZZES
              </div>
              <div className="grid grid-cols-2 gap-2 mb-2">
                <button
                  className={`px-3 py-1.5 rounded-lg transition-all border shadow-lg text-xs font-medium ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                >
                  QUIZZES
                </button>
                <button
                  className={`px-3 py-1.5 rounded-lg transition-all border shadow-lg text-xs font-medium ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                >
                  COMPLETION
                </button>
              </div>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={dontOverride}
                  onChange={(e) => setDontOverride(e.target.checked)}
                  className="rounded"
                />
                <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-700'}`}>
                  Don't override existing grades
                </span>
              </label>
            </div>

            {/* Extract Grades Section */}
            <div className={`rounded-lg border p-3 ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <div className={`mb-2 text-xs tracking-wide font-bold ${isDark ? 'text-gray-400' : 'text-[#1a2942]'}`}>
                EXTRACT GRADES
              </div>
              <button
                className={`w-full px-3 py-1.5 rounded-lg transition-all border shadow-lg text-xs font-medium ${metalButtonClass(isDark)}`}
                style={metalButtonStyle(isDark)}
              >
                EXTRACT GRADES
              </button>
            </div>

            {/* Split PDF Section */}
            <div className={`rounded-lg border p-3 ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <div className={`mb-2 text-xs tracking-wide font-bold ${isDark ? 'text-gray-400' : 'text-[#1a2942]'}`}>
                SPLIT PDF AND REZIP
              </div>
              <div className="grid grid-cols-2 gap-2">
                <button
                  className={`px-3 py-1.5 rounded-lg transition-all border shadow-lg text-xs font-medium ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                >
                  SPLIT & REZIP
                </button>
                <button
                  className={`px-3 py-1.5 rounded-lg transition-all border shadow-lg flex items-center justify-center gap-1 text-xs font-medium ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                >
                  <FolderOpen size={12} />
                  OPEN
                </button>
              </div>
            </div>

            {/* Clear All Data Section */}
            <div className={`rounded-lg border p-3 ${
              isDark 
                ? 'bg-[#0f1729] border-[#1a2942]' 
                : 'bg-[#e0e0e3] border-gray-400'
            }`}>
              <div className={`mb-2 text-xs tracking-wide font-bold ${isDark ? 'text-red-400' : 'text-red-700'}`}>
                CLEAR ALL DATA
              </div>
              <button
                className={`w-full px-3 py-1.5 rounded-lg transition-all border shadow-lg text-xs font-medium ${metalButtonClass(isDark)}`}
                style={metalButtonStyle(isDark)}
              >
                CLEAR ALL DATA
              </button>
            </div>
          </div>
        </div>

        {/* Right Panel - Log Terminal */}
        <div className={`w-1/2 flex flex-col ${
          isDark 
            ? 'bg-[#0a0e1a]' 
            : 'bg-[#d0d0d2]'
        }`}>
          <div className={`p-3 border-b ${
            isDark 
              ? 'bg-[#0f1729] border-[#1a2942]' 
              : 'bg-[#e0e0e3] border-gray-400'
          }`}>
            <div className="flex items-center justify-between">
              <span className={`text-xs tracking-wide font-bold ${isDark ? 'text-gray-400' : 'text-[#1a2942]'}`}>
                LOG TERMINAL
              </span>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={expandedLogging}
                  onChange={(e) => setExpandedLogging(e.target.checked)}
                  className="rounded"
                />
                <span className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-700'}`}>
                  Expanded Logging
                </span>
              </label>
            </div>
          </div>
          <div className={`flex-1 p-4 font-mono text-xs overflow-auto ${
            isDark ? 'text-green-400 bg-[#0a0e1a]' : 'text-[#006600] bg-[#c8c8cc]'
          }`}>
            {logs}
          </div>
        </div>
      </div>
    </div>
  );
}
