import { Monitor, Moon, Sun } from 'lucide-react';
import { Button } from './ui/button';
import { useTheme, type ThemeMode } from '../hooks/useTheme';

const nextThemeMap: Record<ThemeMode, ThemeMode> = {
  system: 'light',
  light: 'dark',
  dark: 'system',
};

const iconMap = {
  light: <Sun className="h-4 w-4" />, 
  dark: <Moon className="h-4 w-4" />, 
  system: <Monitor className="h-4 w-4" />,
};

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();

  const handleClick = () => {
    setTheme(nextThemeMap[theme]);
  };

  const ariaLabel = `Current theme ${resolvedTheme}, click to change (mode: ${theme})`;

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      className="rounded-full border border-transparent hover:border-slate-200/60 dark:hover:border-slate-700/80"
      onClick={handleClick}
      aria-label={ariaLabel}
      title={ariaLabel}
    >
      {iconMap[theme] ?? iconMap[resolvedTheme]}
    </Button>
  );
}
