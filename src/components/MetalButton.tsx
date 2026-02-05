/**
 * MetalButton - Reusable button component with metallic styling
 * Uses useButtonInteractions and useThemeStyles hooks internally
 */

import React, { ReactNode } from 'react';
import { Loader2 } from 'lucide-react';
import { useButtonInteractions } from './hooks/useButtonInteractions';
import { useThemeStyles } from './hooks/useThemeStyles';

export interface MetalButtonProps {
  onClick: () => void;
  disabled?: boolean;
  children: ReactNode;
  isDark: boolean;
  variant?: 'metal' | 'danger';
  loading?: boolean;
  loadingText?: string;
  icon?: ReactNode;
  title?: string;
  style?: React.CSSProperties;
  className?: string;
  scaleType?: 'normal' | 'small' | 'icon';
}

export default function MetalButton({
  onClick,
  disabled = false,
  children,
  isDark,
  variant = 'metal',
  loading = false,
  loadingText,
  icon,
  title,
  style = {},
  className = '',
  scaleType = 'normal'
}: MetalButtonProps) {
  const { metalButtonClass, metalButtonStyle, dangerButtonClass, dangerButtonStyle } = useThemeStyles();
  
  const isDisabled = disabled || loading;
  const buttonClass = variant === 'danger' ? dangerButtonClass(isDark) : metalButtonClass(isDark);
  const buttonStyle = variant === 'danger' ? dangerButtonStyle(isDark) : metalButtonStyle(isDark);
  
  const interactions = useButtonInteractions({
    disabled: isDisabled,
    scaleType,
    brightnessType: 'normal',
    isDark
  });

  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      className={`rounded-lg border shadow-lg font-medium ${buttonClass} disabled:cursor-not-allowed ${className}`}
      style={{
        ...buttonStyle,
        padding: scaleType === 'icon' ? '4px 8px' : '10px 12px',
        fontSize: scaleType === 'icon' ? '10px' : '14px',
        transition: 'all 0.15s ease',
        ...(isDisabled ? {
          opacity: 0.5,
          filter: 'saturate(0.2) brightness(0.85)',
          pointerEvents: 'none'
        } : {}),
        ...style
      }}
      title={title}
      {...interactions}
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" />
          {loadingText || 'LOADING...'}
        </span>
      ) : (
        <>
          {icon && <span className="inline-flex items-center">{icon}</span>}
          {children}
        </>
      )}
    </button>
  );
}
