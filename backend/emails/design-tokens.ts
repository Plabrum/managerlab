/**
 * Premium design tokens inspired by Stripe/Linear
 * Modern, minimal, and sophisticated email styling
 */

export const colors = {
  // Light mode colors (default for emails)
  white: '#ffffff',
  black: '#000000',

  // Backgrounds
  background: '#ffffff',
  backgroundMuted: '#fafafa',

  // Text colors
  foreground: '#0a0a0a',
  foregroundMuted: '#737373',
  foregroundSubtle: '#a3a3a3',

  // Brand colors with gradient support
  primary: '#0a0a0a',
  primaryHover: '#171717',
  primaryForeground: '#ffffff',

  // Gradient colors for premium feel
  gradientFrom: '#0a0a0a',
  gradientTo: '#262626',

  // Borders and dividers
  border: '#e5e5e5',
  borderSubtle: '#f5f5f5',

  // Success/accent colors
  success: '#16a34a',
  successLight: '#dcfce7',
};

export const typography = {
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif",
  fontFamilyMono: "'Menlo', 'Monaco', 'Courier New', monospace",

  // Font weights
  weightNormal: 400,
  weightMedium: 500,
  weightSemibold: 600,
  weightBold: 700,

  // Line heights
  lineHeightTight: 1.25,
  lineHeightNormal: 1.5,
  lineHeightRelaxed: 1.75,
};

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
  '3xl': '64px',
};

export const borderRadius = {
  sm: '6px',
  md: '8px',
  lg: '12px',
  full: '9999px', // pill shape
};

export const shadows = {
  subtle: '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
};
