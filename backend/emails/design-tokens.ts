/**
 * Design tokens matching frontend globals.css
 * Ensures email styling is consistent with the web application
 */

export const colors = {
  // Light mode colors (default for emails)
  white: 'hsl(0 0% 100%)',
  black: 'hsl(0 0% 0%)',

  background: 'hsl(0 0% 100%)',
  foreground: 'hsl(240 10% 3.9%)',

  primary: 'hsl(240 5.9% 10%)',
  primaryForeground: 'hsl(0 0% 98%)',

  secondary: 'hsl(240 4.8% 95.9%)',
  secondaryForeground: 'hsl(240 5.9% 10%)',

  muted: 'hsl(240 4.8% 95.9%)',
  mutedForeground: 'hsl(240 3.8% 46.1%)',

  border: 'hsl(240 5.9% 90%)',

  // For subtle accents
  accent: 'hsl(240 4.8% 95.9%)',
  accentForeground: 'hsl(240 5.9% 10%)',
};

export const typography = {
  fontFamily: "'Geist Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica', 'Arial', sans-serif",
  fontFamilyMono: "'Geist Mono', 'Menlo', 'Monaco', 'Courier New', monospace",
};

export const spacing = {
  xs: '8px',
  sm: '12px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
};

export const borderRadius = {
  default: '10px', // 0.625rem = 10px
  sm: '6px',
  lg: '12px',
};
