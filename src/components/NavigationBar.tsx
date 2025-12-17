import React from 'react';
import { X, Folder, Sun, Moon, Minus, Square } from 'lucide-react';
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
  handleOpenDownloads: () => void;
  onClassSetupClick: () => void;
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
  handleOpenDownloads,
  onClassSetupClick,
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
            D2L ASSIGNMENT ASSISTANT
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
            onClick={reloadWindow}
            className={`px-3 py-1.5 rounded-lg border shadow-lg text-sm font-medium ${metalButtonClass(isDark)}`}
            style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
            title="Reset application"
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.filter = 'brightness(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.filter = 'brightness(1)';
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translateY(2px) scale(0.98)';
              e.currentTarget.style.boxShadow = isDark 
                ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                : 'inset 0 2px 4px rgba(0,0,0,0.4)';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.boxShadow = '';
            }}
          >
            RELOAD
          </button>

          <button
            onClick={handleOpenDownloads}
            className={`px-3 py-1.5 rounded-lg border shadow-lg flex items-center gap-2 text-sm font-medium ${metalButtonClass(isDark)}`}
            style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.filter = 'brightness(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.filter = 'brightness(1)';
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translateY(2px) scale(0.98)';
              e.currentTarget.style.boxShadow = isDark 
                ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                : 'inset 0 2px 4px rgba(0,0,0,0.4)';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.boxShadow = '';
            }}
          >
            <Folder size={14} />
            DOWNLOADS
          </button>

          <div className="w-px h-6 bg-gray-400 mx-2"></div>

          <button
            onClick={() => setIsDark(!isDark)}
            className={`p-1.5 rounded-lg border shadow-lg ${metalButtonClass(isDark)}`}
            style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
            title={isDark ? 'Light Mode' : 'Dark Mode'}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.filter = 'brightness(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.filter = 'brightness(1)';
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translateY(2px) scale(0.95)';
              e.currentTarget.style.boxShadow = isDark 
                ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                : 'inset 0 2px 4px rgba(0,0,0,0.4)';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.boxShadow = '';
            }}
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          
          <button
            onClick={onClassSetupClick}
            className={`px-3 py-1.5 rounded-lg border shadow-lg text-sm font-medium ${metalButtonClass(isDark)}`}
            style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
            title="Manage class configurations"
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.filter = 'brightness(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.filter = 'brightness(1)';
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translateY(2px) scale(0.98)';
              e.currentTarget.style.boxShadow = isDark 
                ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                : 'inset 0 2px 4px rgba(0,0,0,0.4)';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.boxShadow = '';
            }}
          >
            CLASS SETUP
          </button>

          <div className="w-px h-6 bg-gray-400 mx-2"></div>

          <button
            onClick={minimizeWindow}
            className={`p-1.5 rounded-lg border shadow-lg ${metalButtonClass(isDark)}`}
            style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
            title="Minimize"
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.filter = 'brightness(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.filter = 'brightness(1)';
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translateY(2px) scale(0.95)';
              e.currentTarget.style.boxShadow = isDark 
                ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                : 'inset 0 2px 4px rgba(0,0,0,0.4)';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.boxShadow = '';
            }}
          >
            <Minus size={16} />
          </button>

          <button
            onClick={maximizeWindow}
            className={`p-1.5 rounded-lg border shadow-lg ${metalButtonClass(isDark)}`}
            style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
            title="Maximize"
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.filter = 'brightness(1.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.filter = 'brightness(1)';
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translateY(2px) scale(0.95)';
              e.currentTarget.style.boxShadow = isDark 
                ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                : 'inset 0 2px 4px rgba(0,0,0,0.4)';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.boxShadow = '';
            }}
          >
            <Square size={16} />
          </button>

          <button
            onClick={closeWindow}
            className={`p-1.5 rounded-lg border shadow-lg ${metalButtonClass(isDark, isDark ? 'text-red-400' : 'text-red-700')}`}
            style={{
              ...metalButtonStyle(isDark),
              backgroundImage: isDark 
                ? undefined 
                : 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.15) 25%, transparent 50%, rgba(0,0,0,0.05) 75%, rgba(0,0,0,0.15) 100%), linear-gradient(180deg, #f0c0c0 0%, #e0a0a0 20%, #d08080 50%, #c06060 80%, #b04040 100%)',
              transition: 'all 0.15s ease'
            }}
            title="Close"
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.filter = 'brightness(1.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.filter = 'brightness(1)';
            }}
            onMouseDown={(e) => {
              e.currentTarget.style.transform = 'translateY(2px) scale(0.95)';
              e.currentTarget.style.boxShadow = isDark 
                ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                : 'inset 0 2px 4px rgba(0,0,0,0.4)';
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = 'scale(1.1)';
              e.currentTarget.style.boxShadow = '';
            }}
          >
            <X size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

