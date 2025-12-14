import React from 'react';
import { Folder, X, Calendar, HardDrive, CheckSquare, Square } from 'lucide-react';

interface ProcessingFolder {
  name: string;
  path: string;
  size: string;
  modified: string;
}

interface AssignmentSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  folders: ProcessingFolder[];
  selectedAssignments: Set<string>;
  onToggleAssignment: (assignmentName: string) => void;
  onSelectAll: () => void;
  onDeselectAll: () => void;
  onConfirm: () => void;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
}

export default function AssignmentSelectionModal({
  isOpen,
  onClose,
  folders,
  selectedAssignments,
  onToggleAssignment,
  onSelectAll,
  onDeselectAll,
  onConfirm,
  isDark,
  metalButtonClass,
  metalButtonStyle,
}: AssignmentSelectionModalProps) {
  if (!isOpen) return null;

  const allSelected = folders.length > 0 && selectedAssignments.size === folders.length;

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
          width: '650px',
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
              SELECT ASSIGNMENTS TO CLEAR
            </span>
            <span style={{ 
              fontSize: '12px',
              color: isDark ? '#888' : '#666'
            }}>
              ({folders.length} found)
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

        {/* Select All / Deselect All Bar */}
        <div
          style={{
            padding: '10px 20px',
            backgroundColor: isDark ? '#0f1729' : '#b8b8bc',
            borderBottom: isDark ? '1px solid #2a3952' : '1px solid #999',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
          }}
        >
          <span style={{
            fontSize: '12px',
            color: isDark ? '#888' : '#666'
          }}>
            {selectedAssignments.size} selected
          </span>
          <button
            onClick={allSelected ? onDeselectAll : onSelectAll}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: '500',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: isDark ? '#3a4962' : '#999',
              color: '#fff',
              cursor: 'pointer',
              transition: 'background-color 0.15s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = isDark ? '#4a5972' : '#aaa'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = isDark ? '#3a4962' : '#999'}
          >
            {allSelected ? 'Deselect All' : 'Select All'}
          </button>
        </div>

        {/* Scrollable Folder List */}
        <div 
          style={{
            flex: 1,
            overflowY: 'auto',
            backgroundColor: isDark ? '#0f1729' : '#b8b8bc',
            maxHeight: 'calc(80vh - 220px)',
          }}
        >
          {folders.map((folder, index) => {
            const isSelected = selectedAssignments.has(folder.name);
            return (
              <button
                key={index}
                onClick={() => onToggleAssignment(folder.name)}
                style={{
                  width: '100%',
                  padding: '14px 20px',
                  textAlign: 'left',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  backgroundColor: isSelected 
                    ? (isDark ? 'rgba(0, 200, 255, 0.2)' : 'rgba(100, 150, 255, 0.2)')
                    : 'transparent',
                  border: 'none',
                  borderBottom: isDark ? '1px solid #2a3952' : '1px solid #999',
                  cursor: 'pointer',
                  transition: 'background-color 0.15s',
                }}
                onMouseEnter={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = isDark ? 'rgba(0, 200, 255, 0.1)' : 'rgba(255, 255, 255, 0.5)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isSelected) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                {/* Checkbox Icon */}
                <div style={{ flexShrink: 0, paddingTop: '2px' }}>
                  {isSelected ? (
                    <CheckSquare 
                      size={20} 
                      style={{ color: isDark ? '#00c8ff' : '#1a2942' }} 
                    />
                  ) : (
                    <Square 
                      size={20} 
                      style={{ color: isDark ? '#666' : '#999' }} 
                    />
                  )}
                </div>
                
                {/* Folder Info */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Folder 
                      size={18} 
                      style={{ 
                        flexShrink: 0,
                        color: isDark ? '#00c8ff' : '#1a2942'
                      }} 
                    />
                    <span style={{ 
                      fontSize: '14px',
                      fontWeight: '500',
                      color: isDark ? '#e0e0e0' : '#333',
                      flex: 1,
                    }}>
                      {folder.name}
                    </span>
                  </div>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '16px',
                    marginLeft: '26px',
                    fontSize: '12px',
                    color: isDark ? '#999' : '#666'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <HardDrive size={12} />
                      <span>{folder.size}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Calendar size={12} />
                      <span>{folder.modified}</span>
                    </div>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div 
          style={{
            padding: '16px 20px',
            backgroundColor: isDark ? '#1a2942' : '#c0c0c4',
            borderTop: isDark ? '2px solid #3a4962' : '2px solid #999',
            flexShrink: 0,
            display: 'flex',
            gap: '10px',
          }}
        >
          <button
            onClick={onClose}
            className={`flex-1 px-4 py-2 rounded-lg transition-all text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            CANCEL
          </button>
          <button
            onClick={onConfirm}
            disabled={selectedAssignments.size === 0}
            className={`flex-1 px-4 py-2 rounded-lg transition-all text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
            style={{
              ...metalButtonStyle(isDark),
              opacity: selectedAssignments.size === 0 ? 0.5 : 1,
              cursor: selectedAssignments.size === 0 ? 'not-allowed' : 'pointer',
            }}
          >
            CLEAR SELECTED ({selectedAssignments.size})
          </button>
        </div>
      </div>
    </div>
  );
}
