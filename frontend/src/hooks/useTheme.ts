import { useCallback, useEffect, useState } from 'react';

const THEME_STORAGE_KEY = 'notion-bot-theme';

export type ThemeMode = 'light' | 'dark' | 'system';

type ResolvedTheme = 'light' | 'dark';

const getStoredTheme = (): ThemeMode => {
  if (typeof window === 'undefined') return 'system';
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null;
  return stored ?? 'system';
};

const getSystemTheme = (): ResolvedTheme => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const applyThemeClass = (theme: ResolvedTheme) => {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  const opposite = theme === 'dark' ? 'light' : 'dark';
  root.classList.remove(opposite);
  root.classList.add(theme);
};

export function useTheme() {
  const [theme, setThemeState] = useState<ThemeMode>(() => getStoredTheme());
  const [resolvedTheme, setResolvedTheme] = useState<ResolvedTheme>(() =>
    theme === 'system' ? getSystemTheme() : theme
  );

  useEffect(() => {
    const updateTheme = () => {
      const nextResolved = theme === 'system' ? getSystemTheme() : theme;
      setResolvedTheme(nextResolved);
      applyThemeClass(nextResolved);
    };

    updateTheme();

    if (typeof window === 'undefined') return;
    const media = window.matchMedia('(prefers-color-scheme: dark)');

    const handleChange = () => {
      if (theme === 'system') {
        updateTheme();
      }
    };

    media.addEventListener('change', handleChange);
    return () => media.removeEventListener('change', handleChange);
  }, [theme]);

  const setTheme = useCallback((nextTheme: ThemeMode) => {
    setThemeState(nextTheme);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    }
  }, []);

  return { theme, setTheme, resolvedTheme };
}
