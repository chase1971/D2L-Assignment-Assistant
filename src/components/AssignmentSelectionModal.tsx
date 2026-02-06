import React, { useState, useMemo } from 'react';
import { Folder, Calendar, HardDrive, CheckSquare, Square } from 'lucide-react';
import BaseModal from './BaseModal';
import MetalButton from './MetalButton';
import { DARK_THEME } from './constants/ui-constants';

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
  metalButtonClass?: (isDark: boolean) => string;
  metalButtonStyle?: (isDark: boolean) => React.CSSProperties | undefined;
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

  const allSelected = visibleFolders.length > 0 && visibleFolders.every(folder => selectedAssignments.has(folder.name));

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      isDark={isDark}
      title={`SELECT ASSIGNMENTS TO CLEAR (${visibleFolders.length} ${includeArchived ? 'total' : 'unarchived'} found)`}
      icon={Folder}
      iconColor={isDark ? '#22d3ee' : '#1a2942'}
      width="650px"
      maxHeight="80vh"
      footer={
        <div style={{ display: 'flex', gap: '10px' }}>
          <MetalButton onClick={onClose} isDark={isDark} className="flex-1">
            CANCEL
          </MetalButton>
          <MetalButton
            onClick={onConfirm}
            isDark={isDark}
            disabled={selectedAssignments.size === 0}
            className="flex-1"
          >
            CLEAR SELECTED ({selectedAssignments.size})
          </MetalButton>
        </div>
      }
    >
      <div style={{ margin: '-20px', marginBottom: '-20px' }}>
        {/* Include Archived Checkbox and Select All / Deselect All Bar */}
        <div
          style={{
            padding: '10px 20px',
            backgroundColor: isDark ? DARK_THEME.bgSecondary : '#b8b8bc',
            borderBottom: isDark ? `1px solid ${DARK_THEME.bgQuaternary}` : '1px solid #999',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
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
            <MetalButton
              onClick={() => {
                if (allSelected) {
                  onDeselectAll();
                } else {
                  onSelectAll(visibleFolders.map(f => f.name));
                }
              }}
              isDark={isDark}
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              {allSelected ? 'Deselect All' : 'Select All'}
            </MetalButton>
          </div>
        </div>

        {/* Scrollable Folder List */}
        <div
          style={{
            overflowY: 'auto',
            backgroundColor: isDark ? DARK_THEME.bgSecondary : '#b8b8bc',
            maxHeight: 'calc(80vh - 280px)',
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
                  borderBottom: isDark ? `1px solid ${DARK_THEME.bgQuaternary}` : '1px solid #999',
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
      </div>
    </BaseModal>
  );
}
