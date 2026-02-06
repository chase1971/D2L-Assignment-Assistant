import React from 'react';
import { X, Folder, Sun, Moon, Minus, Square } from 'lucide-react';
import ServerStatusIndicator from './ServerStatusIndicator';
import MetalButton from './MetalButton';
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
  onPatchManagerClick: () => void;
  serverStatus: ServerStatus;
  metalButtonClass?: (isDark: boolean, textColor?: string) => string;
  metalButtonStyle?: (isDark: boolean) => React.CSSProperties | undefined;
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
  onPatchManagerClick,
  serverStatus,
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
          <div className="flex items-baseline gap-2">
            <h1 className={`font-bold tracking-wider ${isDark ? 'text-cyan-400' : 'text-[#1a2942]'}`}>
              D2L ASSIGNMENT ASSISTANT
            </h1>
            <span className={`text-xs font-medium ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
              v0.0.1 beta
            </span>
          </div>

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

          <MetalButton
            onClick={reloadWindow}
            isDark={isDark}
            title="Reset application"
            style={{ padding: '6px 12px', fontSize: '12px' }}
          >
            RELOAD
          </MetalButton>

          <MetalButton
            onClick={handleOpenDownloads}
            isDark={isDark}
            icon={<Folder size={14} />}
            style={{ padding: '6px 12px', fontSize: '12px' }}
          >
            DOWNLOADS
          </MetalButton>

          <MetalButton
            onClick={onPatchManagerClick}
            isDark={isDark}
            title="Patch Manager"
            style={{ padding: '6px 12px', fontSize: '12px' }}
          >
            🔧 PATCHES
          </MetalButton>

          <div className="w-px h-6 bg-gray-400 mx-2"></div>

          <MetalButton
            onClick={() => setIsDark(!isDark)}
            isDark={isDark}
            title={isDark ? 'Light Mode' : 'Dark Mode'}
            scaleType="icon"
            style={{ padding: '6px' }}
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </MetalButton>

          <MetalButton
            onClick={onClassSetupClick}
            isDark={isDark}
            title="Manage class configurations"
            style={{ padding: '6px 12px', fontSize: '12px' }}
          >
            CLASS SETUP
          </MetalButton>

          <div className="w-px h-6 bg-gray-400 mx-2"></div>

          <MetalButton
            onClick={minimizeWindow}
            isDark={isDark}
            title="Minimize"
            scaleType="icon"
            style={{ padding: '6px' }}
          >
            <Minus size={16} />
          </MetalButton>

          <MetalButton
            onClick={maximizeWindow}
            isDark={isDark}
            title="Maximize"
            scaleType="icon"
            style={{ padding: '6px' }}
          >
            <Square size={16} />
          </MetalButton>

          <MetalButton
            onClick={closeWindow}
            isDark={isDark}
            variant="danger"
            title="Close"
            scaleType="icon"
            style={{ padding: '6px' }}
          >
            <X size={16} />
          </MetalButton>
        </div>
      </div>
    </div>
  );
}
