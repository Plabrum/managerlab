'use client';

import { useTheme } from 'next-themes';
import { Monitor, Moon, Sun } from 'lucide-react';

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();

  // Calculate position for sliding background
  const position = theme === 'light' ? 0 : theme === 'dark' ? 1 : 2;

  return (
    <div className="bg-muted relative flex w-24 items-center gap-0.5 rounded-full p-0.5">
      {/* Sliding background */}
      <div
        className="bg-primary absolute h-6 w-[calc(33.333%-0.125rem)] rounded-full transition-all duration-300 ease-out"
        style={{
          left: `calc(${position * 33.333}% + 0.125rem)`,
        }}
      />

      {/* Theme buttons */}
      <button
        onClick={() => setTheme('light')}
        className="relative z-10 flex h-6 flex-1 items-center justify-center rounded-full transition-colors"
        aria-label="Light mode"
      >
        <Sun
          className={`h-3.5 w-3.5 transition-colors ${
            theme === 'light'
              ? 'text-primary-foreground'
              : 'text-muted-foreground'
          }`}
        />
      </button>

      <button
        onClick={() => setTheme('dark')}
        className="relative z-10 flex h-6 flex-1 items-center justify-center rounded-full transition-colors"
        aria-label="Dark mode"
      >
        <Moon
          className={`h-3.5 w-3.5 transition-colors ${
            theme === 'dark'
              ? 'text-primary-foreground'
              : 'text-muted-foreground'
          }`}
        />
      </button>

      <button
        onClick={() => setTheme('system')}
        className="relative z-10 flex h-6 flex-1 items-center justify-center rounded-full transition-colors"
        aria-label="System mode"
      >
        <Monitor
          className={`h-3.5 w-3.5 transition-colors ${
            theme === 'system'
              ? 'text-primary-foreground'
              : 'text-muted-foreground'
          }`}
        />
      </button>
    </div>
  );
}
