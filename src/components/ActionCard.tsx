import React from 'react';

interface ActionCardProps {
  title: string;
  isDark: boolean;
  titleColor?: string;
  children: React.ReactNode;
}

/**
 * Reusable card wrapper for action groups
 * Provides consistent styling for action sections
 */
export default function ActionCard({ title, isDark, titleColor, children }: ActionCardProps) {
  return (
    <div className={`p-2.5 rounded-lg border ${
      isDark 
        ? 'bg-[#0f1729] border-[#1a2942]' 
        : 'bg-[#e0e0e3] border-gray-400'
    }`}>
      <h3 className={`mb-2 text-sm font-bold ${titleColor || (isDark ? 'text-gray-300' : 'text-[#1a2942]')}`}>
        {title}
      </h3>
      {children}
    </div>
  );
}

