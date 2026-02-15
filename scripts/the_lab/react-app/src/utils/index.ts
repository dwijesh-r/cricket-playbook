/**
 * Utility functions for the Cricket Playbook React Dashboard.
 */

/**
 * Format a number with appropriate precision for display.
 * Cricket stats typically show 2 decimal places for averages/rates.
 */
export function formatStat(value: number, decimals = 2): string {
  if (Number.isNaN(value) || !Number.isFinite(value)) {
    return '-';
  }
  return value.toFixed(decimals);
}

/**
 * Format a percentage value (0-100 scale).
 */
export function formatPercent(value: number, decimals = 1): string {
  if (Number.isNaN(value) || !Number.isFinite(value)) {
    return '-';
  }
  return `${value.toFixed(decimals)}%`;
}

/**
 * Get CSS class for a rating value (used in team/player cards).
 * Thresholds aligned with config/thresholds.yaml.
 */
export function getRatingClass(value: number): string {
  if (value >= 8.0) return 'rating-elite';
  if (value >= 6.5) return 'rating-strong';
  if (value >= 5.0) return 'rating-average';
  if (value >= 3.5) return 'rating-below';
  return 'rating-poor';
}

/**
 * Clamp a value between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Debounce a function call (useful for search inputs).
 */
export function debounce<T extends (...args: Parameters<T>) => void>(
  fn: T,
  delayMs: number,
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delayMs);
  };
}
