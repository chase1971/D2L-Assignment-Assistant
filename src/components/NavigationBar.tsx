import React from 'react';
import { Settings, RotateCw, X, Folder, Sun, Moon, Minus, Square } from 'lucide-react';
import ServerStatusIndicator from './ServerStatusIndicator';
import {
  closeWindow,
  reloadWindow,
  minimizeWindow,
  maximizeWindow
} from '../services/quizGraderService';

type ServerStatus = 'checking' | 'online' | 'offline';

interface ClassOption {
  value: string;
  label: string;
}

interface NavigationBarProps {
  isDark: boolean;
  setIsDark: (value: boolean) => void;
  selectedClass: string;
  handleClassChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  classOptions: ClassOption[];
  handleRefresh: () => void;
  handleOpenDownloads: () => void;
  serverStatus: ServerStatus;
  metalButtonClass: (isDark: boolean, textColor?: string) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
}

/**
 * Top navigation bar with class select, theme, and window controls
 */
export default function NavigationBar({
  isDark,
  setIsDark,
  selectedClass,
  handleClassChange,
  classOptions,
  handleRefresh,
  handleOpenDownloads,
  serverStatus,
  metalButtonClass,
  metalButtonStyle,
}: NavigationBarProps) {
  return (
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
          
          <ServerStatusIndicator serverStatus={serverStatus} isDark={isDark} />
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
            {classOptions.map(opt => (
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
  );
}

