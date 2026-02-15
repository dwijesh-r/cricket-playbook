import { useState, useEffect, useCallback } from 'react';
import type { Theme } from '../types';

/**
 * Custom hook for managing the dark/light theme toggle.
 * Persists preference to localStorage and syncs with the
 * data-theme attribute on the <html> element (matching the
 * existing Lab dashboard convention).
 */
export function useTheme(): {
  theme: Theme;
  toggleTheme: () => void;
} {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('cricket-playbook-theme');
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }
    }
    return 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('cricket-playbook-theme', theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  return { theme, toggleTheme };
}
