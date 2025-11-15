import { useCallback, useRef, useState } from 'react';
import { MessageList } from './MessageList';
import { CommandInput } from './CommandInput';
import { AuthModal } from './AuthModal';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { useTheme } from '../hooks/useTheme';

export function ChatContainer() {
  const [showSettings, setShowSettings] = useState(false);
  const fillCommandRef = useRef<((command: string) => void) | null>(null);
  const { resolvedTheme } = useTheme();

  const handleRegisterFill = useCallback((fill: ((command: string) => void) | null) => {
    fillCommandRef.current = fill;
  }, []);

  const handleQuickAction = (action: 'new-task' | 'view-tasks') => {
    const fill = fillCommandRef.current;
    switch (action) {
      case 'new-task':
        fill?.('/task create ');
        break;
      case 'view-tasks':
        fill?.('/task list ');
        break;
      default:
        fill?.('');
    }
  };

  return (
    <div
      data-theme={resolvedTheme}
      className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950"
    >
      <Header onSettingsClick={() => setShowSettings(true)} />

      <div className="mx-auto max-w-6xl px-4 py-6 lg:px-6">
        <div className="grid gap-6 lg:grid-cols-sidebar">
          <Sidebar onQuickAction={handleQuickAction} />

          <div className="flex h-[calc(100vh-140px)] flex-col overflow-hidden rounded-3xl border border-white/50 bg-white/90 shadow-glass backdrop-blur-glass dark:border-slate-800/80 dark:bg-slate-900/80">
            <MessageList />
            <CommandInput onRegisterFill={handleRegisterFill} />
          </div>
        </div>
      </div>

      {showSettings && <AuthModal onClose={() => setShowSettings(false)} />}
    </div>
  );
}
