import React from 'react';
import { Folder, X } from 'lucide-react';

interface ZipFile {
  index: number;
  filename: string;
  path: string;
}

interface ZipSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  zipFiles: ZipFile[];
  onSelect: (zipPath: string) => void;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
}

export default function ZipSelectionModal({
  isOpen,
  onClose,
  zipFiles,
  onSelect,
  isDark,
  metalButtonClass,
  metalButtonStyle,
}: ZipSelectionModalProps) {
  if (!isOpen) return null;

  return (
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
          onClose();
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
            onClick={onClose}
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
              onClick={() => onSelect(zipFile.path)}
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
            onClick={onClose}
            className={`w-full px-4 py-2 rounded-lg transition-all text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            CANCEL
          </button>
        </div>
      </div>
    </div>
  );
}

