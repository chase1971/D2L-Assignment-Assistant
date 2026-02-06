/**
 * UI Constants for D2L Assignment Assistant
 * 
 * Centralized constants for consistent UI behavior across the application.
 * Extracted from Option2.tsx per coding-standards.md refactoring guidelines.
 * 
 * @module ui-constants
 */

// Server status polling
export const SERVER_POLL_INTERVAL_MS = 3000;  // How often to check if backend is running
export const SERVER_CHECK_TIMEOUT_MS = 2000;  // Timeout for server health check

// Button interaction constants
export const BUTTON_HOVER_SCALE = 1.02;         // Scale factor for button hover (normal buttons)
export const BUTTON_HOVER_SCALE_SMALL = 1.05;  // Scale factor for small buttons
export const BUTTON_HOVER_SCALE_ICON = 1.1;    // Scale factor for icon buttons
export const BUTTON_HOVER_BRIGHTNESS = 1.1;    // Brightness increase on hover (normal)
export const BUTTON_HOVER_BRIGHTNESS_HIGH = 1.15;  // Brightness increase on hover (danger buttons)
export const BUTTON_PRESS_TRANSLATE_Y = 2;     // Pixels to move down when pressed
export const BUTTON_PRESS_SCALE = 0.98;        // Scale factor when pressed (normal)
export const BUTTON_PRESS_SCALE_ICON = 0.95;   // Scale factor when pressed (icon buttons)
export const BUTTON_TRANSITION_DURATION = '0.15s';  // CSS transition duration

// Disabled button styles
export const DISABLED_BUTTON_OPACITY = 0.5;      // Opacity for disabled buttons
export const DISABLED_BUTTON_SATURATION = 0.2;   // Color saturation for disabled
export const DISABLED_BUTTON_BRIGHTNESS = 0.85;  // Brightness for disabled

// Theme colors - Dark mode
export const DARK_THEME = {
  // Backgrounds
  bgPrimary: '#0a0e1a',      // Main app background
  bgSecondary: '#0f1729',    // Card/panel backgrounds
  bgTertiary: '#1a2942',     // Hover states, inputs
  bgQuaternary: '#2a3952',   // Selected states

  // Borders
  borderPrimary: '#1a2942',  // Main borders
  borderSecondary: '#2a3952', // Subtle borders
  borderTertiary: '#3a4962', // Input borders

  // Text
  textPrimary: '#ffffff',
  textSecondary: '#d0d0d4',
  textMuted: '#888888',

  // Accents
  accentBlue: '#3b82f6',
  accentRed: '#ef4444',

  // Modal overlay
  overlayBg: 'rgba(0, 0, 0, 0.7)',
} as const;

// Theme colors - Light mode
export const LIGHT_THEME = {
  // Backgrounds
  bgPrimary: '#d0d0d2',      // Main app background
  bgSecondary: '#e0e0e3',    // Card/panel backgrounds
  bgTertiary: '#d0d0d4',     // Hover states, inputs
  bgQuaternary: '#c0c0c4',   // Selected states

  // Borders
  borderPrimary: 'rgb(156, 163, 175)', // gray-400
  borderSecondary: 'rgb(209, 213, 219)', // gray-300
  borderTertiary: 'rgb(107, 114, 128)', // gray-500

  // Text
  textPrimary: '#1f2937',    // gray-800
  textSecondary: '#374151',  // gray-700
  textMuted: '#6b7280',      // gray-500

  // Accents
  accentBlue: '#2563eb',
  accentRed: '#dc2626',

  // Modal overlay
  overlayBg: 'rgba(0, 0, 0, 0.5)',
} as const;

// Helper to get theme based on isDark
export const getTheme = (isDark: boolean) => isDark ? DARK_THEME : LIGHT_THEME;

// Common z-index values
export const Z_INDEX = {
  modal: 999999,
  dropdown: 1000,
  tooltip: 2000,
} as const;

// Default values
export const DEFAULT_DRIVE = 'C';

