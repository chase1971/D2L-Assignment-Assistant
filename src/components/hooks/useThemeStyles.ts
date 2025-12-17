import React from 'react';

/**
 * Hook for metallic button styling matching Figma design
 * Provides consistent styling functions for dark/light themes with interactive states
 */
export function useThemeStyles() {
  const metalButtonClass = (isDark: boolean, textColor?: string) => 
    isDark 
      ? `bg-gradient-to-b from-[#4a4a4c] to-[#3a3a3c] ${textColor || 'text-gray-200'} hover:from-[#5a5a5c] hover:to-[#4a4a4c] border-[#5a5a5c] shadow-black/50 active:from-[#3a3a3c] active:to-[#2a2a2c] active:shadow-inner active:translate-y-[1px] transition-all duration-150`
      : `bg-gradient-to-b from-[#d8d8dc] via-[#c8c8cc] to-[#b8b8bc] ${textColor || 'text-gray-800'} hover:from-[#e0e0e4] hover:to-[#c8c8cc] border-gray-400 shadow-gray-500/50 active:from-[#c8c8cc] active:to-[#b8b8bc] active:shadow-inner active:translate-y-[1px] transition-all duration-150`;

  const metalButtonStyle = (isDark: boolean): React.CSSProperties | undefined => isDark 
    ? undefined 
    : {
        backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.15) 25%, transparent 50%, rgba(0,0,0,0.05) 75%, rgba(0,0,0,0.15) 100%), linear-gradient(180deg, #e8e8ec 0%, #d8d8dc 20%, #c8c8cc 50%, #b8b8bc 80%, #a8a8ac 100%)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.5), inset 0 -1px 0 rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.2)'
      };

  const metalButtonActiveStyle = (isDark: boolean): React.CSSProperties => ({
    transform: 'translateY(1px)',
    boxShadow: isDark 
      ? 'inset 0 1px 2px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.3)' 
      : 'inset 0 1px 2px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)',
    filter: 'brightness(0.9)'
  });

  const dangerButtonClass = (isDark: boolean) =>
    isDark
      ? `bg-gradient-to-b from-[#dc2626] to-[#b91c1c] text-white hover:from-[#ef4444] hover:to-[#dc2626] border-[#b91c1c] shadow-black/50 active:from-[#b91c1c] active:to-[#991b1b] active:shadow-inner active:translate-y-[1px] transition-all duration-150`
      : `bg-gradient-to-b from-[#ef4444] to-[#dc2626] text-white hover:from-[#f87171] hover:to-[#ef4444] border-[#dc2626] shadow-red-900/50 active:from-[#dc2626] active:to-[#b91c1c] active:shadow-inner active:translate-y-[1px] transition-all duration-150`;

  const dangerButtonStyle = (isDark: boolean): React.CSSProperties => isDark
    ? undefined
    : {
        backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 25%, transparent 50%, rgba(0,0,0,0.1) 75%, rgba(0,0,0,0.2) 100%), linear-gradient(180deg, #f87171 0%, #ef4444 20%, #dc2626 50%, #b91c1c 80%, #991b1b 100%)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.3), inset 0 -1px 0 rgba(0,0,0,0.2), 0 2px 4px rgba(0,0,0,0.3)'
      };

  return { 
    metalButtonClass, 
    metalButtonStyle, 
    metalButtonActiveStyle,
    dangerButtonClass,
    dangerButtonStyle
  };
}

