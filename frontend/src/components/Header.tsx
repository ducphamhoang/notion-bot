import { Settings } from 'lucide-react';
import { Button } from './ui/button';
import { ThemeToggle } from './ThemeToggle';
import { useChatStore } from '../store/chatStore';

interface HeaderProps {
  onSettingsClick: () => void;
}

export function Header({ onSettingsClick }: HeaderProps) {
  const databaseId = useChatStore((state) => state.databaseId);
  const isConnected = Boolean(databaseId);

  return (
    <header className="sticky top-0 z-20 w-full border-b border-glass-border/40 bg-white/80 backdrop-blur-glass shadow-glass dark:bg-slate-900/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 lg:px-6">
        <div>
          <div className="flex items-center gap-3">
            <div>
              <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Notion Task Bot</h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">Chat interface for managing tasks</p>
            </div>
            <span
              className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium ${
                isConnected
                  ? 'border-emerald-200/80 bg-emerald-50 text-emerald-600 dark:border-emerald-400/40 dark:bg-emerald-400/10 dark:text-emerald-300'
                  : 'border-amber-200/80 bg-amber-50 text-amber-600 dark:border-amber-400/40 dark:bg-amber-400/10 dark:text-amber-300'
              }`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-amber-500'}`} aria-hidden />
              {isConnected ? 'Connected' : 'Not configured'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="rounded-full border border-transparent hover:border-slate-200/60 dark:hover:border-slate-700/80"
            onClick={onSettingsClick}
            title="Open settings"
            aria-label="Open settings"
          >
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
