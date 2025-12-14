import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDark: boolean;
  metalButtonClass: (isDark: boolean) => string;
  metalButtonStyle: (isDark: boolean) => React.CSSProperties | undefined;
}

export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'CONFIRM',
  cancelText = 'CANCEL',
  isDark,
  metalButtonClass,
  metalButtonStyle,
}: ConfirmationModalProps) {
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
          width: '450px',
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

        {/* Message */}
        <div 
          style={{
            padding: '20px',
            backgroundColor: isDark ? '#0f1729' : '#b8b8bc',
            flex: 1,
          }}
        >
          <p style={{
            fontSize: '14px',
            color: isDark ? '#e0e0e0' : '#333',
            lineHeight: '1.5',
            margin: 0,
          }}>
            {message}
          </p>
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
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-2 rounded-lg transition-all text-sm font-medium border-2 shadow-lg font-bold"
            style={{
              backgroundColor: isDark ? '#dc2626' : '#ef4444',
              borderColor: isDark ? '#b91c1c' : '#dc2626',
              color: '#fff',
              backgroundImage: 'none',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = isDark ? '#b91c1c' : '#dc2626';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = isDark ? '#dc2626' : '#ef4444';
            }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
