import React from 'react';

type ServerStatus = 'checking' | 'online' | 'offline';

interface ServerStatusIndicatorProps {
  serverStatus: ServerStatus;
  isDark: boolean;
}

/**
 * Server status badge
 * Shows online/offline/checking status with appropriate colors
 */
export default function ServerStatusIndicator({ serverStatus, isDark }: ServerStatusIndicatorProps) {
  return (
    <div 
      className="flex items-center justify-center px-3 py-1 rounded-full border"
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
  );
}

