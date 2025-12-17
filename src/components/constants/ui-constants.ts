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

