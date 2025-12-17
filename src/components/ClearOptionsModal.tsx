import React, { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';

export type ClearOption = 'saveFoldersAndPdf' | 'saveCombinedPdf' | 'deleteAll';

interface ClearOptionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (option: ClearOption) => void;
  title: string;
  message: string;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
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
}: ClearOptionsModalProps) {
  const [selectedOption, setSelectedOption] = useState<ClearOption | null>(null);

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

  const options = [
    { value: 'saveFoldersAndPdf' as ClearOption, label: 'Save folders and single PDF' },
    { value: 'saveCombinedPdf' as ClearOption, label: 'Save combined PDF' },
    { value: 'deleteAll' as ClearOption, label: 'Delete all data' },
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
              return (
                <button
                  key={option.value}
                  onClick={() => setSelectedOption(option.value)}
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
                    transition: 'all 0.15s',
                    color: isDark ? '#e0e0e0' : '#333',
                    fontSize: '14px',
                    fontWeight: isSelected ? '600' : '400',
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = isDark ? 'rgba(0, 200, 255, 0.1)' : 'rgba(100, 150, 255, 0.1)';
                      e.currentTarget.style.borderColor = isDark ? '#00c8ff' : '#1a2942';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.backgroundColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
                      e.currentTarget.style.borderColor = isDark ? '#3a4962' : '#999';
                    }
                  }}
                >
                  {option.label}
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
          <button
            onClick={handleClose}
            className={`flex-1 px-4 py-2 rounded-lg transition-all text-sm font-medium border shadow-lg ${metalButtonClass(isDark)}`}
            style={metalButtonStyle(isDark)}
          >
            CANCEL
          </button>
          <button
            onClick={handleConfirm}
            disabled={!selectedOption}
            className="flex-1 px-4 py-2 rounded-lg transition-all text-sm font-medium border-2 shadow-lg font-bold"
            style={{
              backgroundColor: selectedOption ? (isDark ? '#dc2626' : '#ef4444') : (isDark ? '#666' : '#999'),
              borderColor: selectedOption ? (isDark ? '#b91c1c' : '#dc2626') : (isDark ? '#555' : '#777'),
              color: '#fff',
              backgroundImage: 'none',
              cursor: selectedOption ? 'pointer' : 'not-allowed',
              opacity: selectedOption ? 1 : 0.5,
            }}
            onMouseEnter={(e) => {
              if (selectedOption) {
                e.currentTarget.style.backgroundColor = isDark ? '#b91c1c' : '#dc2626';
              }
            }}
            onMouseLeave={(e) => {
              if (selectedOption) {
                e.currentTarget.style.backgroundColor = isDark ? '#dc2626' : '#ef4444';
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

