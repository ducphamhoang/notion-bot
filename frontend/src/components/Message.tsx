import { formatDistanceToNow } from 'date-fns';
import type { Message as MessageType } from '../types/message';
import type { TaskSummary } from '../types/task';
import { TaskCard } from './TaskCard';
import { cn } from '../lib/utils';
import { Avatar } from './Avatar';

interface MessageProps {
  message: MessageType;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  const isError = message.role === 'error' || message.error;

  const roleLabel = isUser ? 'You' : isError ? 'Error' : 'Bot';
  const taskList: TaskSummary[] = Array.isArray(message.data?.data)
    ? (message.data?.data as TaskSummary[])
    : [];

  const bubbleClasses = cn(
    'max-w-[80%] rounded-3xl px-5 py-3 shadow-glass backdrop-blur-glass transition-all duration-300',
    isUser && 'bg-user-gradient text-white',
    !isUser && !isError && 'bg-white/90 text-slate-900 dark:bg-slate-900/70 dark:text-slate-100 border border-slate-100/70 dark:border-slate-800/70',
    isError && 'border-2 border-rose-400/70 bg-rose-50 text-rose-900 dark:bg-rose-500/10 dark:text-rose-100'
  );

  return (
    <div
      className={cn(
        'flex w-full gap-3 py-2 animate-slide-up',
        isUser && 'flex-row-reverse'
      )}
    >
      <Avatar role={isError ? 'error' : message.role} className={cn(isUser && 'order-2')} />

      <div className={bubbleClasses}>
        <div
          className={cn(
            'text-xs font-semibold uppercase tracking-wide',
            isUser ? 'text-white/70' : isError ? 'text-rose-600' : 'text-slate-500 dark:text-slate-400'
          )}
        >
          {roleLabel}
        </div>

        <div className="mt-1 text-sm whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {taskList.length > 0 && (
          <div className="mt-3 space-y-3">
            {taskList.map((task) => (
              <TaskCard key={task.notion_task_id} task={task} />
            ))}
          </div>
        )}

        <div
          className={cn(
            'mt-2 text-[11px]',
            isUser ? 'text-white/70' : isError ? 'text-rose-600' : 'text-slate-400 dark:text-slate-500'
          )}
        >
          {formatDistanceToNow(message.timestamp, { addSuffix: true })}
        </div>
      </div>
    </div>
  );
}
