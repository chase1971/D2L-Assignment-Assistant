/**
 * Custom hook for modal state management
 * Provides consistent patterns for showing/hiding modals
 */

import { useState, useCallback } from 'react';

interface UseModalReturn<T = any> {
  isOpen: boolean;
  config: T | null;
  open: (configuration?: T) => void;
  close: () => void;
  updateConfig: (updates: Partial<T>) => void;
}

export function useModal<T = any>(initialConfig: T | null = null): UseModalReturn<T> {
  const [isOpen, setIsOpen] = useState(false);
  const [config, setConfig] = useState<T | null>(initialConfig);

  const open = useCallback((configuration?: T) => {
    if (configuration) {
      setConfig(configuration);
    }
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const updateConfig = useCallback((updates: Partial<T>) => {
    setConfig((prev) => (prev ? { ...prev, ...updates } : null));
  }, []);

  return {
    isOpen,
    config,
    open,
    close,
    updateConfig
  };
}

