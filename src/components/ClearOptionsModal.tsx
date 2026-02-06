import React, { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import BaseModal from './BaseModal';
import MetalButton from './MetalButton';
import { DARK_THEME } from './constants/ui-constants';

export type ClearOption = 'saveFoldersAndPdf' | 'saveCombinedPdf' | 'deleteAll' | 'deleteEverything';

interface ClearOptionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (option: ClearOption) => void;
  title: string;
  message: string;
  isDark: boolean;
  metalButtonClass?: (isDark: boolean) => string;
  metalButtonStyle?: (isDark: boolean) => React.CSSProperties | undefined;
  hasCurrentAssignment?: boolean;
  onBack?: () => void;
}

export default function ClearOptionsModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  isDark,
  onBack,
}: ClearOptionsModalProps) {
  const [selectedOption, setSelectedOption] = useState<ClearOption | null>(null);
  const [pressedOption, setPressedOption] = useState<ClearOption | null>(null);

  const handleConfirm = () => {
    if (selectedOption) {
      onConfirm(selectedOption);
      setSelectedOption(null);
    }
  };

  const handleClose = () => {
    setSelectedOption(null);
    onClose();
  };

  const options = [
    {
      value: 'saveFoldersAndPdf' as ClearOption,
      label: 'Save folders and single PDF',
      description: '(Creates archived folder)'
    },
    {
      value: 'saveCombinedPdf' as ClearOption,
      label: 'Save combined PDF',
      description: '(Creates archived folder)'
    },
    {
      value: 'deleteEverything' as ClearOption,
      label: 'Delete everything',
      description: ''
    },
  ];

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={handleClose}
      isDark={isDark}
      title={title}
      icon={AlertTriangle}
      iconColor={isDark ? '#facc15' : '#ca8a04'}
      width="500px"
      footer={
        <div style={{ display: 'flex', gap: '10px' }}>
          {onBack ? (
            <>
              <MetalButton onClick={onBack} isDark={isDark} className="flex-1">
                BACK
              </MetalButton>
              <MetalButton onClick={handleClose} isDark={isDark} className="flex-1">
                CANCEL
              </MetalButton>
            </>
          ) : (
            <MetalButton onClick={handleClose} isDark={isDark} className="flex-1">
              CANCEL
            </MetalButton>
          )}
          <MetalButton
            onClick={handleConfirm}
            isDark={isDark}
            disabled={!selectedOption}
            variant="danger"
            className="flex-1"
          >
            CLEAR
          </MetalButton>
        </div>
      }
    >
      <p style={{
        fontSize: '14px',
        color: isDark ? '#e0e0e0' : '#333',
        lineHeight: '1.5',
        margin: 0,
        marginBottom: '16px',
      }}>
        {message}
      </p>

      {/* Options */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {options.map((option) => {
          const isSelected = selectedOption === option.value;
          const isPressed = pressedOption === option.value;
          return (
            <button
              key={option.value}
              onClick={() => setSelectedOption(option.value)}
              onMouseDown={() => setPressedOption(option.value)}
              onMouseUp={() => setPressedOption(null)}
              style={{
                width: '100%',
                padding: '12px 16px',
                textAlign: 'left',
                backgroundColor: isSelected
                  ? (isDark ? 'rgba(0, 200, 255, 0.2)' : 'rgba(100, 150, 255, 0.2)')
                  : (isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'),
                border: isSelected
                  ? (isDark ? '2px solid #00c8ff' : '2px solid #1a2942')
                  : (isDark ? `2px solid ${DARK_THEME.borderTertiary}` : '2px solid #999'),
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                transform: isPressed ? 'translateY(2px) scale(0.98)' : 'translateY(0) scale(1)',
                boxShadow: isPressed
                  ? (isDark ? 'inset 0 2px 4px rgba(0,0,0,0.6)' : 'inset 0 2px 4px rgba(0,0,0,0.4)')
                  : isSelected
                    ? (isDark ? '0 2px 4px rgba(0, 200, 255, 0.3)' : '0 2px 4px rgba(100, 150, 255, 0.3)')
                    : 'none',
                color: isDark ? '#e0e0e0' : '#333',
                fontSize: '14px',
                fontWeight: isSelected ? '600' : '400',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '4px',
              }}
              onMouseEnter={(e) => {
                if (!isSelected && !isPressed) {
                  e.currentTarget.style.backgroundColor = isDark ? 'rgba(0, 200, 255, 0.15)' : 'rgba(100, 150, 255, 0.15)';
                  e.currentTarget.style.borderColor = isDark ? '#00c8ff' : '#1a2942';
                  e.currentTarget.style.transform = 'scale(1.01)';
                }
              }}
              onMouseLeave={(e) => {
                setPressedOption(null);
                if (!isSelected && !isPressed) {
                  e.currentTarget.style.backgroundColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
                  e.currentTarget.style.borderColor = isDark ? DARK_THEME.borderTertiary : '#999';
                  e.currentTarget.style.transform = 'scale(1)';
                }
              }}
            >
              <span>{option.label}</span>
              {option.description && (
                <span style={{
                  fontSize: '12px',
                  color: isDark ? '#888' : '#666',
                  fontStyle: 'italic',
                }}>
                  {option.description}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </BaseModal>
  );
}
