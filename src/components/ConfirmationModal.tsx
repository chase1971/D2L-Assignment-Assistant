import React from 'react';
import { AlertTriangle } from 'lucide-react';
import BaseModal from './BaseModal';
import MetalButton from './MetalButton';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  isDark: boolean;
  metalButtonClass?: (isDark: boolean) => string;
  metalButtonStyle?: (isDark: boolean) => React.CSSProperties | undefined;
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
}: ConfirmationModalProps) {
  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      isDark={isDark}
      title={title}
      icon={AlertTriangle}
      iconColor={isDark ? '#facc15' : '#ca8a04'}
      footer={
        <div style={{ display: 'flex', gap: '10px' }}>
          <MetalButton
            onClick={onClose}
            isDark={isDark}
            className="flex-1"
          >
            {cancelText}
          </MetalButton>
          <MetalButton
            onClick={onConfirm}
            isDark={isDark}
            variant="danger"
            className="flex-1"
          >
            {confirmText}
          </MetalButton>
        </div>
      }
    >
      <p style={{
        fontSize: '14px',
        color: isDark ? '#e0e0e0' : '#333',
        lineHeight: '1.5',
        margin: 0,
      }}>
        {message}
      </p>
    </BaseModal>
  );
}
