import { cn } from '../lib/utils';

interface TypingIndicatorProps {
  className?: string;
}

export function TypingIndicator({ className }: TypingIndicatorProps) {
  return (
    <div className={cn('flex items-center gap-1 text-slate-500 dark:text-slate-300', className)}>
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          className="inline-block h-2 w-2 rounded-full bg-slate-400/70 dark:bg-slate-200/70 animate-bounce-dots"
          style={{ animationDelay: `${delay}ms` }}
        >
          <span className="sr-only">Typing</span>
        </span>
      ))}
    </div>
  );
}
