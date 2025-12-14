import React from 'react';

/**
 * Hook for metallic button styling matching Figma design
 * Provides consistent styling functions for dark/light themes
 */
export function useThemeStyles() {
  const metalButtonClass = (isDark: boolean, textColor?: string) => 
    isDark 
      ? `bg-gradient-to-b from-[#4a4a4c] to-[#3a3a3c] ${textColor || 'text-gray-200'} hover:from-[#5a5a5c] hover:to-[#4a4a4c] border-[#5a5a5c] shadow-black/50`
      : `bg-gradient-to-b from-[#d8d8dc] via-[#c8c8cc] to-[#b8b8bc] ${textColor || 'text-gray-800'} hover:from-[#e0e0e4] hover:to-[#c8c8cc] border-gray-400 shadow-gray-500/50`;

  const metalButtonStyle = (isDark: boolean): React.CSSProperties | undefined => isDark 
    ? undefined 
    : {
        backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.15) 25%, transparent 50%, rgba(0,0,0,0.05) 75%, rgba(0,0,0,0.15) 100%), linear-gradient(180deg, #e8e8ec 0%, #d8d8dc 20%, #c8c8cc 50%, #b8b8bc 80%, #a8a8ac 100%)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.5), inset 0 -1px 0 rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.2)'
      };

  return { metalButtonClass, metalButtonStyle };
}

