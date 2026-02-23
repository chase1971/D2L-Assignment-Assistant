/**
 * ThemeContext - Provides theme state to the entire application
 * Eliminates prop drilling for isDark/setIsDark through component hierarchy
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ThemeContextType {
  isDark: boolean;
  setIsDark: (value: boolean) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
  initialTheme?: boolean;
}

export function ThemeProvider({ children, initialTheme = false }: ThemeProviderProps) {
  const [isDark, setIsDark] = useState(initialTheme);

  const toggleTheme = () => {
    setIsDark(prev => !prev);
  };

  return (
    <ThemeContext.Provider value={{ isDark, setIsDark, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to access theme context
 * @throws Error if used outside of ThemeProvider
 * @returns ThemeContextType with isDark, setIsDark, and toggleTheme
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

/**
 * Optional hook that returns undefined if outside ThemeProvider
 * Useful for components that can work with or without theme context
 */
export function useThemeOptional(): ThemeContextType | undefined {
  return useContext(ThemeContext);
}

export { ThemeContext };
