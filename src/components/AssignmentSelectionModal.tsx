import React, { useState, useMemo } from 'react';
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
  onSelectAll: (folderNames: string[]) => void;
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
  const [includeArchived, setIncludeArchived] = useState(false);
  const [pressedFolder, setPressedFolder] = useState<string | null>(null);

  // Filter folders based on checkbox
  const visibleFolders = useMemo(() => {
    if (includeArchived) {
      return folders; // Show all folders
    }
    // Only show unarchived (grade processing) folders
    return folders.filter(folder => folder.name.toLowerCase().startsWith('grade processing '));
  }, [folders, includeArchived]);

  if (!isOpen) return null;

  const allSelected = visibleFolders.length > 0 && visibleFolders.every(folder => selectedAssignments.has(folder.name));

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
              ({visibleFolders.length} {includeArchived ? 'total' : 'unarchived'} found)
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

        {/* Include Archived Checkbox and Select All / Deselect All Bar */}
        <div
          style={{
            padding: '10px 20px',
            backgroundColor: isDark ? '#0f1729' : '#b8b8bc',
            borderBottom: isDark ? '1px solid #2a3952' : '1px solid #999',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
            gap: '12px',
          }}
        >
          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              fontSize: '12px',
              color: isDark ? '#e0e0e0' : '#333',
              userSelect: 'none',
            }}
          >
            <input
              type="checkbox"
              checked={includeArchived}
              onChange={(e) => {
                setIncludeArchived(e.target.checked);
                // Deselect archived folders when unchecking
                if (!e.target.checked) {
                  folders
                    .filter(f => f.name.toLowerCase().startsWith('archived '))
                    .forEach(f => {
                      if (selectedAssignments.has(f.name)) {
                        onToggleAssignment(f.name);
                      }
                    });
                }
              }}
              style={{
                width: '16px',
                height: '16px',
                cursor: 'pointer',
              }}
            />
            <span>Include archived folders</span>
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{
              fontSize: '12px',
              color: isDark ? '#888' : '#666'
            }}>
              {selectedAssignments.size} selected
            </span>
            <button
              onClick={() => {
                if (allSelected) {
                  onDeselectAll();
                } else {
                  // Select only visible folders
                  onSelectAll(visibleFolders.map(f => f.name));
                }
              }}
              className={`px-3 py-1.5 text-xs rounded border font-medium ${metalButtonClass(isDark)}`}
              style={{
                ...metalButtonStyle(isDark),
                fontSize: '12px',
                padding: '6px 12px',
              }}
            >
              {allSelected ? 'Deselect All' : 'Select All'}
            </button>
          </div>
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
          {visibleFolders.map((folder, index) => {
            const isArchived = folder.name.toLowerCase().startsWith('archived ');
            const isSelected = selectedAssignments.has(folder.name);
            const isPressed = pressedFolder === folder.name;
            return (
              <button
                key={index}
                onClick={() => onToggleAssignment(folder.name)}
                onMouseDown={() => setPressedFolder(folder.name)}
                onMouseUp={() => setPressedFolder(null)}
                onMouseLeave={() => setPressedFolder(null)}
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
                  transition: 'all 0.15s ease',
                  transform: isPressed ? 'translateY(2px) scale(0.98)' : 'translateY(0) scale(1)',
                  boxShadow: isPressed 
                    ? (isDark ? 'inset 0 2px 4px rgba(0,0,0,0.6)' : 'inset 0 2px 4px rgba(0,0,0,0.4)')
                    : 'none',
                }}
                onMouseEnter={(e) => {
                  if (!isSelected && !isPressed) {
                    e.currentTarget.style.backgroundColor = isDark ? 'rgba(0, 200, 255, 0.15)' : 'rgba(100, 150, 255, 0.1)';
                    e.currentTarget.style.transform = 'scale(1.005)';
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
                      {isArchived && (
                        <span style={{
                          marginLeft: '8px',
                          fontSize: '11px',
                          color: isDark ? '#888' : '#666',
                          fontStyle: 'italic',
                        }}>
                          (archived)
                        </span>
                      )}
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
