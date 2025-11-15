import { ClipboardList, Plus } from 'lucide-react';
import { Button } from './ui/button';
import { useChatStore } from '../store/chatStore';

interface SidebarProps {
  onQuickAction: (action: 'new-task' | 'view-tasks') => void;
}

export function Sidebar({ onQuickAction }: SidebarProps) {
  const messageCount = useChatStore((state) => state.messages.length);

  return (
    <aside className="hidden h-full flex-col gap-4 border-r border-glass-border/40 bg-white/60 p-4 backdrop-blur-glass dark:border-slate-800/70 dark:bg-slate-900/50 lg:flex">
      <div className="rounded-2xl border border-white/40 bg-white/80 p-4 shadow-glass dark:border-slate-800/80 dark:bg-slate-900/80">
        <p className="text-xs uppercase tracking-wide text-slate-400">Conversation</p>
        <h2 className="mt-1 text-2xl font-semibold text-slate-900 dark:text-slate-100">{messageCount}</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">messages in this session</p>
      </div>

      <div className="rounded-2xl border border-white/40 bg-white/80 p-4 shadow-glass dark:border-slate-800/80 dark:bg-slate-900/80">
        <p className="text-xs uppercase tracking-wide text-slate-400">Quick actions</p>
        <div className="mt-3 flex flex-col gap-2">
          <Button
            type="button"
            className="justify-start gap-2"
            onClick={() => onQuickAction('new-task')}
          >
            <Plus className="h-4 w-4" />
            New Task
          </Button>
          <Button
            type="button"
            variant="secondary"
            className="justify-start gap-2"
            onClick={() => onQuickAction('view-tasks')}
          >
            <ClipboardList className="h-4 w-4" />
            View All Tasks
          </Button>
        </div>
      </div>
    </aside>
  );
}
