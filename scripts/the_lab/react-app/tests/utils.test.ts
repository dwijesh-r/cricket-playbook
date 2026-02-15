import { describe, it, expect, vi } from 'vitest';
import { formatStat, formatPercent, getRatingClass, clamp, debounce } from '../src/utils';

describe('formatStat', () => {
  it('formats a number with default 2 decimal places', () => {
    expect(formatStat(45.678)).toBe('45.68');
  });

  it('formats with custom decimal places', () => {
    expect(formatStat(7.5, 1)).toBe('7.5');
  });

  it('returns dash for NaN', () => {
    expect(formatStat(NaN)).toBe('-');
  });

  it('returns dash for Infinity', () => {
    expect(formatStat(Infinity)).toBe('-');
  });
});

describe('formatPercent', () => {
  it('formats a percentage with 1 decimal place by default', () => {
    expect(formatPercent(67.89)).toBe('67.9%');
  });

  it('returns dash for NaN', () => {
    expect(formatPercent(NaN)).toBe('-');
  });
});

describe('getRatingClass', () => {
  it('returns elite for 8.0+', () => {
    expect(getRatingClass(8.5)).toBe('rating-elite');
  });

  it('returns strong for 6.5-7.9', () => {
    expect(getRatingClass(7.0)).toBe('rating-strong');
  });

  it('returns average for 5.0-6.4', () => {
    expect(getRatingClass(5.5)).toBe('rating-average');
  });

  it('returns below for 3.5-4.9', () => {
    expect(getRatingClass(4.0)).toBe('rating-below');
  });

  it('returns poor for below 3.5', () => {
    expect(getRatingClass(2.0)).toBe('rating-poor');
  });
});

describe('clamp', () => {
  it('clamps value to max', () => {
    expect(clamp(150, 0, 100)).toBe(100);
  });

  it('clamps value to min', () => {
    expect(clamp(-5, 0, 100)).toBe(0);
  });

  it('returns value when in range', () => {
    expect(clamp(50, 0, 100)).toBe(50);
  });
});

describe('debounce', () => {
  it('debounces function calls', async () => {
    vi.useFakeTimers();
    const fn = vi.fn();
    const debounced = debounce(fn, 100);

    debounced();
    debounced();
    debounced();

    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });
});
