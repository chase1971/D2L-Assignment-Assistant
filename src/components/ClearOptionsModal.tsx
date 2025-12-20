import React, { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';

export type ClearOption = 'saveFoldersAndPdf' | 'saveCombinedPdf' | 'deleteAll' | 'deleteEverything';

interface ClearOptionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (option: ClearOption) => void;
  title: string;
  message: string;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
  hasCurrentAssignment?: boolean; // Whether a current assignment is selected
  onBack?: () => void; // Optional back button handler
}

export default function ClearOptionsModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  isDark,
  metalButtonClass,
  metalButtonStyle,
  hasCurrentAssignment = false,
  onBack,
}: ClearOptionsModalProps) {
  const [selectedOption, setSelectedOption] = useState<ClearOption | null>(null);
  const [pressedOption, setPressedOption] = useState<ClearOption | null>(null);

  if (!isOpen) return null;

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

  // Always show 3 options (same for both with and without current assignment)
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
          handleClose();
        }
      }}
    >
      <div 
        style={{
          width: '500px',
          maxWidth: '95vw',
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
            <AlertTriangle className={isDark ? 'text-yellow-400' : 'text-yellow-600'} size={20} />
            <span style={{ 
              fontWeight: 'bold', 
              fontSize: '14px',
              color: isDark ? '#fff' : '#1a2942'
            }}>
              {title}
            </span>
          </div>
          <button
            onClick={handleClose}
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

        {/* Message */}
        <div 
          style={{
            padding: '20px',
            backgroundColor: isDark ? '#0f1729' : '#b8b8bc',
            flexShrink: 0,
          }}
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
                      : (isDark ? '2px solid #3a4962' : '2px solid #999'),
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
                      e.currentTarget.style.borderColor = isDark ? '#3a4962' : '#999';
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
          {onBack ? (
            <>
              <button
                onClick={onBack}
                className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
                style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.02)';
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
                  e.currentTarget.style.transform = 'scale(1.02)';
                  e.currentTarget.style.boxShadow = '';
                }}
              >
                BACK
              </button>
              <button
                onClick={handleClose}
                className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
                style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'scale(1.02)';
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
                  e.currentTarget.style.transform = 'scale(1.02)';
                  e.currentTarget.style.boxShadow = '';
                }}
              >
                CANCEL
              </button>
            </>
          ) : (
            <button
              onClick={handleClose}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
              style={{ ...metalButtonStyle(isDark), transition: 'all 0.15s ease' }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.02)';
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
                e.currentTarget.style.transform = 'scale(1.02)';
                e.currentTarget.style.boxShadow = '';
              }}
            >
              CANCEL
            </button>
          )}
          <button
            onClick={handleConfirm}
            disabled={!selectedOption}
            className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium border-2 shadow-lg font-bold ${
              selectedOption 
                ? `bg-gradient-to-b ${isDark ? 'from-[#dc2626] to-[#b91c1c]' : 'from-[#ef4444] to-[#dc2626]'} border-[#b91c1c] text-white`
                : 'bg-gray-500 border-gray-600 text-gray-300 cursor-not-allowed opacity-30 grayscale brightness-75'
            }`}
            style={selectedOption ? {
              ...(isDark ? undefined : {
                backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 25%, transparent 50%, rgba(0,0,0,0.1) 75%, rgba(0,0,0,0.2) 100%), linear-gradient(180deg, #f87171 0%, #ef4444 20%, #dc2626 50%, #b91c1c 80%, #991b1b 100%)',
                boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.3), inset 0 -1px 0 rgba(0,0,0,0.2), 0 2px 4px rgba(0,0,0,0.3)'
              }),
              transition: 'all 0.15s ease'
            } : undefined}
            onMouseEnter={(e) => {
              if (selectedOption) {
                e.currentTarget.style.transform = 'scale(1.05)';
                e.currentTarget.style.filter = 'brightness(1.15)';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedOption) {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.filter = 'brightness(1)';
              }
            }}
            onMouseDown={(e) => {
              if (selectedOption) {
                e.currentTarget.style.transform = 'translateY(2px) scale(0.98)';
                e.currentTarget.style.boxShadow = isDark 
                  ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
                  : 'inset 0 2px 4px rgba(0,0,0,0.4)';
              }
            }}
            onMouseUp={(e) => {
              if (selectedOption) {
                e.currentTarget.style.transform = 'scale(1.05)';
                e.currentTarget.style.boxShadow = '';
              }
            }}
          >
            CLEAR
          </button>
        </div>
      </div>
    </div>
  );
}

