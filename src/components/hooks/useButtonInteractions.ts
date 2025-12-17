/**
 * Custom hook for consistent button interaction handlers
 * Provides hover and press effects for buttons
 */

import { MouseEvent } from 'react';
import {
  BUTTON_HOVER_SCALE,
  BUTTON_HOVER_SCALE_SMALL,
  BUTTON_HOVER_SCALE_ICON,
  BUTTON_HOVER_BRIGHTNESS,
  BUTTON_HOVER_BRIGHTNESS_HIGH,
  BUTTON_PRESS_TRANSLATE_Y,
  BUTTON_PRESS_SCALE,
  BUTTON_PRESS_SCALE_ICON
} from '../constants/ui-constants';

interface ButtonInteractionOptions {
  disabled?: boolean;
  scaleType?: 'normal' | 'small' | 'icon';
  brightnessType?: 'normal' | 'high';
  isDark?: boolean;
}

export function useButtonInteractions(options: ButtonInteractionOptions = {}) {
  const {
    disabled = false,
    scaleType = 'normal',
    brightnessType = 'normal',
    isDark = false
  } = options;

  const scaleFactors = {
    normal: BUTTON_HOVER_SCALE,
    small: BUTTON_HOVER_SCALE_SMALL,
    icon: BUTTON_HOVER_SCALE_ICON
  };

  const pressScaleFactors = {
    normal: BUTTON_PRESS_SCALE,
    small: BUTTON_PRESS_SCALE,
    icon: BUTTON_PRESS_SCALE_ICON
  };

  const brightness = brightnessType === 'high' ? BUTTON_HOVER_BRIGHTNESS_HIGH : BUTTON_HOVER_BRIGHTNESS;
  const hoverScale = scaleFactors[scaleType];
  const pressScale = pressScaleFactors[scaleType];

  const handleMouseEnter = (e: MouseEvent<HTMLButtonElement>) => {
    if (!disabled) {
      e.currentTarget.style.transform = `scale(${hoverScale})`;
      e.currentTarget.style.filter = `brightness(${brightness})`;
    }
  };

  const handleMouseLeave = (e: MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.transform = 'scale(1)';
    e.currentTarget.style.filter = 'brightness(1)';
  };

  const handleMouseDown = (e: MouseEvent<HTMLButtonElement>) => {
    if (!disabled) {
      e.currentTarget.style.transform = `translateY(${BUTTON_PRESS_TRANSLATE_Y}px) scale(${pressScale})`;
      e.currentTarget.style.boxShadow = isDark 
        ? 'inset 0 2px 4px rgba(0,0,0,0.6)'
        : 'inset 0 2px 4px rgba(0,0,0,0.4)';
    }
  };

  const handleMouseUp = (e: MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.transform = `scale(${hoverScale})`;
    e.currentTarget.style.boxShadow = '';
  };

  return {
    onMouseEnter: handleMouseEnter,
    onMouseLeave: handleMouseLeave,
    onMouseDown: handleMouseDown,
    onMouseUp: handleMouseUp
  };
}

