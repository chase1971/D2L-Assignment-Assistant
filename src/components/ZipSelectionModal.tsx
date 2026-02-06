import React from 'react';
import { Folder } from 'lucide-react';
import BaseModal from './BaseModal';
import MetalButton from './MetalButton';
import { DARK_THEME } from './constants/ui-constants';

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
  metalButtonClass?: (isDark: boolean) => string;
  metalButtonStyle?: (isDark: boolean) => React.CSSProperties | undefined;
}

export default function ZipSelectionModal({
  isOpen,
  onClose,
  zipFiles,
  onSelect,
  isDark,
}: ZipSelectionModalProps) {
  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      isDark={isDark}
      title={`SELECT ZIP FILE (${zipFiles.length} found)`}
      icon={Folder}
      iconColor={isDark ? '#22d3ee' : '#1a2942'}
      width="550px"
      maxHeight="80vh"
      footer={
        <MetalButton onClick={onClose} isDark={isDark} className="w-full">
          CANCEL
        </MetalButton>
      }
    >
      <div style={{ margin: '-20px', marginBottom: '-20px' }}>
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
              borderBottom: isDark ? `1px solid ${DARK_THEME.bgQuaternary}` : '1px solid #999',
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
    </BaseModal>
  );
}
