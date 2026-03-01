/**
 * Design System Tokens
 *
 * TypeScript representation of the CSS custom properties defined in index.css.
 * These tokens serve as the single source of truth for the design system,
 * enabling type-safe access to theme values in component logic.
 *
 * Actual rendering uses CSS variables; these tokens are for JS-side references
 * (e.g., conditional logic, inline styles, SVG fills).
 */

// ---------------------------------------------------------------------------
// Colors
// ---------------------------------------------------------------------------

export const colors = {
  brand: {
    accent: 'var(--accent)',
    purple: 'var(--accent-purple)',
    pink: 'var(--accent-pink)',
    teal: 'var(--accent-teal)',
  },
  semantic: {
    success: 'var(--accent-green)',
    warning: 'var(--accent-yellow)',
    error: 'var(--accent-red)',
    info: 'var(--accent)',
    orange: 'var(--accent-orange)',
  },
  surface: {
    primary: 'var(--bg-primary)',
    secondary: 'var(--bg-secondary)',
    tertiary: 'var(--bg-tertiary)',
    elevated: 'var(--bg-elevated)',
    glass: 'var(--glass)',
    glassBorder: 'var(--glass-border)',
  },
  text: {
    primary: 'var(--text-primary)',
    secondary: 'var(--text-secondary)',
    tertiary: 'var(--text-tertiary)',
  },
  border: 'var(--border)',
  shadow: 'var(--shadow)',

  /** IPL team colors for PlayerChip / team-specific UI */
  team: {
    CSK: '#ffd700',
    MI: '#004ba0',
    RCB: '#d4213d',
    KKR: '#3b215d',
    DC: '#004c93',
    PBKS: '#d71920',
    RR: '#ea1a85',
    SRH: '#f26522',
    GT: '#1c1c2b',
    LSG: '#005da0',
  },
} as const;

// ---------------------------------------------------------------------------
// Typography
// ---------------------------------------------------------------------------

export const typography = {
  fontFamily:
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  fontSize: {
    xs: '0.6875rem', // 11px
    sm: '0.75rem', // 12px
    base: '0.875rem', // 14px
    md: '1rem', // 16px
    lg: '1.25rem', // 20px
    xl: '1.5rem', // 24px
    '2xl': '2rem', // 32px
    '3xl': '2.5rem', // 40px
  },
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
} as const;

// ---------------------------------------------------------------------------
// Spacing
// ---------------------------------------------------------------------------

export const spacing = {
  '0': '0',
  '1': '4px',
  '2': '8px',
  '3': '12px',
  '4': '16px',
  '5': '20px',
  '6': '24px',
  '8': '32px',
  '10': '40px',
  '12': '48px',
  '16': '64px',
  '20': '80px',
} as const;

// ---------------------------------------------------------------------------
// Shadows
// ---------------------------------------------------------------------------

export const shadows = {
  sm: '0 1px 2px var(--shadow)',
  md: '0 4px 12px var(--shadow)',
  lg: '0 8px 32px var(--shadow)',
  xl: '0 16px 48px var(--shadow)',
  glass: '0 8px 32px rgba(0, 0, 0, 0.2)',
} as const;

// ---------------------------------------------------------------------------
// Border Radii
// ---------------------------------------------------------------------------

export const radii = {
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  '2xl': '24px',
  full: '9999px',
} as const;

// ---------------------------------------------------------------------------
// Breakpoints
// ---------------------------------------------------------------------------

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ---------------------------------------------------------------------------
// Theme Variants
// ---------------------------------------------------------------------------

export interface ThemeColors {
  bgPrimary: string;
  bgSecondary: string;
  bgTertiary: string;
  bgElevated: string;
  textPrimary: string;
  textSecondary: string;
  textTertiary: string;
  accent: string;
  accentGreen: string;
  accentYellow: string;
  accentOrange: string;
  accentRed: string;
  accentPurple: string;
  accentPink: string;
  accentTeal: string;
  border: string;
  glass: string;
  glassBorder: string;
  shadow: string;
}

export const darkTheme: ThemeColors = {
  bgPrimary: '#000000',
  bgSecondary: '#1c1c1e',
  bgTertiary: '#2c2c2e',
  bgElevated: '#3a3a3c',
  textPrimary: '#ffffff',
  textSecondary: '#8e8e93',
  textTertiary: '#636366',
  accent: '#0a84ff',
  accentGreen: '#30d158',
  accentYellow: '#ffd60a',
  accentOrange: '#ff9f0a',
  accentRed: '#ff453a',
  accentPurple: '#bf5af2',
  accentPink: '#ff375f',
  accentTeal: '#64d2ff',
  border: 'rgba(255, 255, 255, 0.1)',
  glass: 'rgba(255, 255, 255, 0.05)',
  glassBorder: 'rgba(255, 255, 255, 0.08)',
  shadow: 'rgba(0, 0, 0, 0.4)',
};

export const lightTheme: ThemeColors = {
  bgPrimary: '#f5f5f7',
  bgSecondary: '#ffffff',
  bgTertiary: '#e5e5ea',
  bgElevated: '#d1d1d6',
  textPrimary: '#1d1d1f',
  textSecondary: '#6e6e73',
  textTertiary: '#8e8e93',
  accent: '#007aff',
  accentGreen: '#28cd41',
  accentYellow: '#ffcc00',
  accentOrange: '#ff9500',
  accentRed: '#ff3b30',
  accentPurple: '#af52de',
  accentPink: '#ff2d55',
  accentTeal: '#5ac8fa',
  border: 'rgba(0, 0, 0, 0.08)',
  glass: 'rgba(0, 0, 0, 0.03)',
  glassBorder: 'rgba(0, 0, 0, 0.06)',
  shadow: 'rgba(0, 0, 0, 0.15)',
};

// ---------------------------------------------------------------------------
// Unified Theme Object
// ---------------------------------------------------------------------------

export const theme = {
  colors,
  typography,
  spacing,
  shadows,
  radii,
  breakpoints,
  dark: darkTheme,
  light: lightTheme,
} as const;

export type Theme = typeof theme;

export default theme;
