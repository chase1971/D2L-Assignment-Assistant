import React from 'react';
import { X, LucideIcon } from 'lucide-react';
import { DARK_THEME, LIGHT_THEME, Z_INDEX } from './constants/ui-constants';

interface BaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  isDark: boolean;
  title: string;
  icon?: LucideIcon;
  iconColor?: string;
  width?: string;
  maxHeight?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

/**
 * BaseModal - Reusable modal wrapper component
 *
 * Provides consistent modal structure with:
 * - Fixed overlay backdrop with click-to-close
 * - Header with icon, title, and close button
 * - Scrollable content area
 * - Optional footer section
 */
export default function BaseModal({
  isOpen,
  onClose,
  isDark,
  title,
  icon: Icon,
  iconColor,
  width = '450px',
  maxHeight = '90vh',
  children,
  footer,
}: BaseModalProps) {
  if (!isOpen) return null;

  const theme = isDark ? DARK_THEME : LIGHT_THEME;

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
        backgroundColor: theme.overlayBg,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: Z_INDEX.modal,
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        style={{
          width,
          maxWidth: '95vw',
          maxHeight,
          backgroundColor: isDark ? DARK_THEME.bgTertiary : LIGHT_THEME.bgTertiary,
          borderRadius: '12px',
          border: `2px solid ${isDark ? DARK_THEME.borderTertiary : '#888'}`,
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
            backgroundColor: isDark ? DARK_THEME.bgSecondary : LIGHT_THEME.bgQuaternary,
            borderBottom: `2px solid ${isDark ? DARK_THEME.borderTertiary : '#999'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {Icon && (
              <Icon
                size={20}
                style={{ color: iconColor || (isDark ? '#60a5fa' : '#2563eb') }}
              />
            )}
            <span
              style={{
                fontWeight: 'bold',
                fontSize: '14px',
                color: isDark ? DARK_THEME.textPrimary : LIGHT_THEME.textPrimary,
              }}
            >
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
              transition: 'color 0.15s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = '#ff4444')}
            onMouseLeave={(e) => (e.currentTarget.style.color = isDark ? '#888' : '#666')}
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div
          style={{
            padding: '20px',
            backgroundColor: isDark ? DARK_THEME.bgSecondary : '#b8b8bc',
            flex: 1,
            overflowY: 'auto',
          }}
        >
          {children}
        </div>

        {/* Footer (optional) */}
        {footer && (
          <div
            style={{
              padding: '16px 20px',
              backgroundColor: isDark ? DARK_THEME.bgTertiary : LIGHT_THEME.bgQuaternary,
              borderTop: `2px solid ${isDark ? DARK_THEME.borderTertiary : '#999'}`,
              flexShrink: 0,
            }}
          >
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
