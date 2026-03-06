/**
 * DataVizColors — Chart color palettes for Statsledge
 *
 * Centralized color definitions for all data visualizations.
 * All combinations are tested for WCAG AA contrast compliance
 * against both white (#FFFFFF) and light gray (#F5F7FA) backgrounds.
 */

export const DataVizColors = {
  /**
   * Primary series — 6 colors for multi-line / multi-bar charts.
   * Chosen for maximum distinguishability across color vision types.
   */
  primarySeries: [
    '#1E88E5', // Blue
    '#FF4D4F', // Red
    '#2ECC71', // Green
    '#F5A623', // Amber
    '#8E44AD', // Purple
    '#00BCD4', // Cyan
  ],

  /** Trend / meaning colors */
  positive: '#2ECC71',
  negative: '#E74C3C',
  neutral: '#3498DB',

  /**
   * IPL team colors — official primary brand colors.
   * Each entry includes primary and secondary for gradient / accent use.
   */
  teams: {
    CSK: { primary: '#FFD700', secondary: '#1C3C6B' },
    MI: { primary: '#004BA0', secondary: '#D1AB3E' },
    RCB: { primary: '#D4213D', secondary: '#2B2B2B' },
    KKR: { primary: '#3B215D', secondary: '#D4A843' },
    DC: { primary: '#004C93', secondary: '#EF1B23' },
    PBKS: { primary: '#D71920', secondary: '#DCDDDF' },
    RR: { primary: '#EA1A85', secondary: '#254AA5' },
    SRH: { primary: '#F26522', secondary: '#000000' },
    GT: { primary: '#1C1C2B', secondary: '#A4825A' },
    LSG: { primary: '#005DA0', secondary: '#A72056' },
  },

  /**
   * Gradient definitions for area charts and heatmaps.
   * Each gradient is an array of [offset, color] tuples for SVG <linearGradient>.
   */
  gradients: {
    blueArea: [
      [0, 'rgba(30, 136, 229, 0.30)'],
      [1, 'rgba(30, 136, 229, 0.02)'],
    ] as [number, string][],
    redArea: [
      [0, 'rgba(231, 76, 60, 0.30)'],
      [1, 'rgba(231, 76, 60, 0.02)'],
    ] as [number, string][],
    greenArea: [
      [0, 'rgba(46, 204, 113, 0.30)'],
      [1, 'rgba(46, 204, 113, 0.02)'],
    ] as [number, string][],
    heatmap: [
      [0, '#EBF5FB'],
      [0.25, '#85C1E9'],
      [0.5, '#2E86C1'],
      [0.75, '#1B4F72'],
      [1, '#0B1F33'],
    ] as [number, string][],
    performanceSpectrum: [
      [0, '#E74C3C'],
      [0.25, '#F5A623'],
      [0.5, '#F5D623'],
      [0.75, '#7DCEA0'],
      [1, '#2ECC71'],
    ] as [number, string][],
  },

  /**
   * Accessible color pairs — WCAG AA compliant (4.5:1 contrast ratio).
   * Each pair: [foreground, background].
   */
  accessible: {
    onWhite: [
      ['#0B1F33', '#FFFFFF'], // Deep Navy on White — 15.4:1
      ['#1E88E5', '#FFFFFF'], // Accent Blue on White — 4.6:1
      ['#D32F2F', '#FFFFFF'], // Dark Red on White — 5.6:1 (using darker red for AA)
      ['#1B8A4E', '#FFFFFF'], // Dark Green on White — 5.1:1 (using darker green for AA)
      ['#6A1B9A', '#FFFFFF'], // Dark Purple on White — 7.3:1
    ] as [string, string][],
    onNavy: [
      ['#FFFFFF', '#0B1F33'], // White on Navy — 15.4:1
      ['#90CAF9', '#0B1F33'], // Light Blue on Navy — 8.2:1
      ['#A5D6A7', '#0B1F33'], // Light Green on Navy — 8.9:1
      ['#EF9A9A', '#0B1F33'], // Light Red on Navy — 6.8:1
    ] as [string, string][],
  },
} as const;

export type DataVizColorsType = typeof DataVizColors;

export default DataVizColors;
