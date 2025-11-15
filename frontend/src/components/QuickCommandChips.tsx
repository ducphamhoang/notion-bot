import { cn } from '../lib/utils';

const COMMANDS = ['/task list', '/task create', '/help'];

interface QuickCommandChipsProps {
  onCommandSelect: (command: string) => void;
  disabled?: boolean;
}

export function QuickCommandChips({ onCommandSelect, disabled }: QuickCommandChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {COMMANDS.map((command) => (
        <button
          key={command}
          type="button"
          onClick={() => onCommandSelect(command)}
          disabled={disabled}
          className={cn(
            'px-3 py-1 text-xs font-medium rounded-full border border-slate-200/80 text-slate-600/90 transition-colors',
            'bg-white/70 backdrop-blur-sm hover:bg-white dark:bg-glass-dark/70 dark:text-slate-200 dark:border-slate-700/60',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          {command}
        </button>
      ))}
    </div>
  );
}
