import { useEffect } from 'react';

interface KeyboardShortcutOptions {
  key: string;
  ctrl?: boolean;
  meta?: boolean;
  shift?: boolean;
  alt?: boolean;
}

/**
 * Register a keyboard shortcut that calls a callback when triggered
 * @param options - Shortcut configuration (key, modifiers)
 * @param callback - Function to call when shortcut is triggered
 */
export function useKeyboardShortcut(
  options: KeyboardShortcutOptions,
  callback: () => void
) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const {
        key,
        ctrl = false,
        meta = false,
        shift = false,
        alt = false,
      } = options;

      // Check if key matches
      if (event.key !== key) return;

      // Check modifiers
      const ctrlOrMeta = ctrl || meta;
      const hasCtrlOrMeta = event.ctrlKey || event.metaKey;

      if (ctrlOrMeta && !hasCtrlOrMeta) return;
      if (!ctrlOrMeta && hasCtrlOrMeta) return;
      if (shift !== event.shiftKey) return;
      if (alt !== event.altKey) return;

      event.preventDefault();
      callback();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [options, callback]);
}
