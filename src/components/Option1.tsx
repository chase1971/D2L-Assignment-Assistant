import React, { useState } from 'react';
import { Settings, RotateCw, X, FolderOpen, Folder, Sun, Moon } from 'lucide-react';

// Option 1: Sidebar Navigation with Compact Main Area
export default function Option1() {
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
    <div className={`h-screen flex transition-colors ${isDark ? 'bg-[#0a0e1a]' : 'bg-[#d0d0d2]'}`}>
      {/* Left Sidebar */}
      <div className={`w-64 p-4 border-r ${
        isDark 
          ? 'bg-[#0f1729] border-[#1a2942]' 
          : 'bg-[#e0e0e3] border-gray-400'
      }`}>
        <h1 className={`tracking-wider mb-6 font-bold ${isDark ? 'text-cyan-400' : 'text-[#1a2942]'}`}>
          QUIZ GRADER
        </h1>
        
        <div className="space-y-3">
          <button
            onClick={() => setIsDark(!isDark)}
            className={`w-full px-3 py-2 rounded-lg transition-all border shadow-lg flex items-center gap-2 font-medium ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
            {isDark ? 'LIGHT' : 'DARK'}
          </button>
          
          <button
            className={`w-full px-3 py-2 rounded-lg transition-all border shadow-lg flex items-center gap-2 font-medium ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            <Settings size={16} />
            SETTINGS
          </button>

          <button
            className={`w-full px-3 py-2 rounded-lg transition-all border shadow-lg flex items-center gap-2 font-medium ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            <RotateCw size={16} />
            RELOAD
          </button>

          <button
            className={`w-full px-3 py-2 rounded-lg transition-all border shadow-lg flex items-center gap-2 font-medium ${metalButtonClass(isDark, isDark ? 'text-red-400' : 'text-red-700')}`}
            style={metalButtonStyle(isDark)}
          >
            <X size={16} />
            CLOSE
          </button>

          <div className="pt-4 border-t border-gray-600">
            <select
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
              className={`w-full px-3 py-2 rounded-lg border ${
                isDark
                  ? 'bg-[#1a2942] border-[#2a3952] text-gray-300'
                  : 'bg-white border-gray-400 text-gray-800'
              }`}
            >
              <option value="">Select Class</option>
              <option value="class1">Class 1</option>
              <option value="class2">Class 2</option>
            </select>
          </div>

          <button
            className={`w-full px-3 py-2 rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            REFRESH
          </button>

          <button
            className={`w-full px-3 py-2 rounded-lg transition-all border shadow-lg flex items-center gap-2 text-xs font-medium ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            <Folder size={14} />
            DOWNLOADS
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Action Buttons */}
        <div className={`p-4 border-b ${
          isDark 
            ? 'bg-[#0f1729] border-[#1a2942]' 
            : 'bg-[#e0e0e3] border-gray-400'
        }`}>
          <div className="grid grid-cols-2 gap-3 max-w-4xl">
            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#141d35] border-[#1a2942]' 
                : 'bg-[#d8d8dc] border-gray-400'
            }`}>
              <h3 className={`mb-3 font-bold ${isDark ? 'text-gray-300' : 'text-[#1a2942]'}`}>PROCESS QUIZZES</h3>
              <div className="flex gap-2 mb-3">
                <button
                  className={`flex-1 px-4 py-2 rounded-lg transition-all border shadow-lg text-sm font-medium ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                >
                  PROCESS QUIZZES
                </button>
                <button
                  className={`flex-1 px-4 py-2 rounded-lg transition-all border shadow-lg text-sm font-medium ${metalButtonClass(isDark)}`}
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
                <span className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-700'}`}>
                  Don't override existing grades
                </span>
              </label>
            </div>

            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#141d35] border-[#1a2942]' 
                : 'bg-[#d8d8dc] border-gray-400'
            }`}>
              <h3 className={`mb-3 font-bold ${isDark ? 'text-gray-300' : 'text-[#1a2942]'}`}>EXTRACT GRADES</h3>
              <button
                className={`w-full px-4 py-2 rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)}`}
                style={metalButtonStyle(isDark)}
              >
                EXTRACT GRADES
              </button>
            </div>

            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#141d35] border-[#1a2942]' 
                : 'bg-[#d8d8dc] border-gray-400'
            }`}>
              <h3 className={`mb-3 font-bold ${isDark ? 'text-gray-300' : 'text-[#1a2942]'}`}>SPLIT PDF</h3>
              <div className="flex gap-2">
                <button
                  className={`flex-1 px-4 py-2 rounded-lg transition-all border shadow-lg text-sm font-medium ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                >
                  SPLIT & REZIP
                </button>
                <button
                  className={`px-4 py-2 rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)}`}
                  style={metalButtonStyle(isDark)}
                >
                  <FolderOpen size={16} />
                </button>
              </div>
            </div>

            <div className={`p-4 rounded-lg border ${
              isDark 
                ? 'bg-[#141d35] border-[#1a2942]' 
                : 'bg-[#d8d8dc] border-gray-400'
            }`}>
              <h3 className={`mb-3 font-bold ${isDark ? 'text-red-400' : 'text-red-700'}`}>CLEAR DATA</h3>
              <button
                className={`w-full px-4 py-2 rounded-lg transition-all border shadow-lg font-medium ${metalButtonClass(isDark)}`}
                style={metalButtonStyle(isDark)}
              >
                CLEAR ALL DATA
              </button>
            </div>
          </div>
        </div>

        {/* Log Terminal */}
        <div className="flex-1 p-4 overflow-hidden">
          <div className={`h-full rounded-lg border ${
            isDark 
              ? 'bg-[#0a0e1a] border-[#1a2942]' 
              : 'bg-[#c8c8cc] border-gray-400'
          }`}>
            <div className={`p-3 border-b ${
              isDark 
                ? 'border-[#1a2942]' 
                : 'border-gray-400'
            }`}>
              <div className="flex items-center justify-between">
                <span className={`font-bold ${isDark ? 'text-gray-400' : 'text-[#1a2942]'}`}>LOG TERMINAL</span>
                <label className="flex items-center gap-2">
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
            <div className={`p-4 font-mono text-sm h-[calc(100%-60px)] overflow-auto ${
              isDark ? 'text-green-400' : 'text-[#006600]'
            }`}>
              {logs}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
