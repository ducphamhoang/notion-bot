import { Bot, TriangleAlert, User } from 'lucide-react';
import type { ReactElement } from 'react';
import { cn } from '../lib/utils';

type AvatarRole = 'user' | 'bot' | 'error';
type AvatarSize = 'sm' | 'md' | 'lg';

const sizeMap: Record<AvatarSize, string> = {
  sm: 'h-6 w-6 text-[10px]',
  md: 'h-8 w-8 text-xs',
  lg: 'h-10 w-10 text-sm',
};

const roleClassMap: Record<AvatarRole, string> = {
  user: 'bg-gradient-to-br from-userbubble-from to-userbubble-to text-white shadow-float',
  bot: 'bg-white/80 text-slate-900 shadow-glass dark:bg-glass-dark/80 dark:text-slate-100 border border-glass-border/70',
  error: 'bg-rose-500/90 text-white shadow-sm border border-rose-200/80',
};

const roleIconMap: Record<AvatarRole, ReactElement> = {
  user: <User className="h-4 w-4" strokeWidth={2} />,
  bot: <Bot className="h-4 w-4" strokeWidth={2} />,
  error: <TriangleAlert className="h-4 w-4" strokeWidth={2} />,
};

interface AvatarProps {
  role: AvatarRole;
  size?: AvatarSize;
  className?: string;
}

export function Avatar({ role, size = 'md', className }: AvatarProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-center rounded-full transition-transform duration-200',
        sizeMap[size],
        roleClassMap[role],
        className
      )}
    >
      {roleIconMap[role]}
    </div>
  );
}
