import { formatDistanceToNow } from 'date-fns';
import { ExternalLink, CheckCircle2 } from 'lucide-react';
import type { TaskSummary } from '../types/task';
import { useChatStore } from '../store/chatStore';
import { cn } from '../lib/utils';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';

interface TaskCardProps {
  task: TaskSummary;
}

export function TaskCard({ task }: TaskCardProps) {
  const sendCommand = useChatStore((state) => state.sendCommand);

  const statusAccentMap: Record<string, string> = {
    Done: 'border-l-4 border-l-emerald-400',
    Completed: 'border-l-4 border-l-emerald-400',
    'In Progress': 'border-l-4 border-l-indigo-400',
    'Not Started': 'border-l-4 border-l-slate-300',
  };

  const priorityColors = {
    High: 'bg-rose-50 text-rose-700 border-rose-200',
    Medium: 'bg-amber-50 text-amber-700 border-amber-200',
    Low: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  } as const;

  type TaskWithOptionalDescription = TaskSummary & {
    description?: string;
    properties?: {
      description?: string;
      [key: string]: unknown;
    };
  };

  const taskWithExtras = task as TaskWithOptionalDescription;
  const description =
    taskWithExtras.description ??
    (typeof taskWithExtras.properties?.description === 'string'
      ? taskWithExtras.properties.description
      : undefined);

  const handleMarkDone = () => {
    void sendCommand(`/task update task_id:"${task.notion_task_id}" status:"Done"`);
  };

  const openInNotion = () => {
    window.open(task.url, '_blank', 'noopener,noreferrer');
  };

  return (
    <Card
      className={cn(
        'group border border-white/60 bg-white/90 shadow-glass transition-all duration-300 hover:-translate-y-0.5 hover:shadow-float dark:border-slate-800/80 dark:bg-slate-900/80',
        statusAccentMap[task.status ?? ''] ?? 'border-l-4 border-l-slate-200'
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <h3 className="truncate text-sm font-semibold text-slate-900 dark:text-slate-100">
              {task.title}
            </h3>

            <div className="mt-2 flex flex-wrap items-center gap-2">
              {task.status && (
                <span className="inline-flex items-center rounded-full border border-slate-200/80 bg-slate-50 px-2.5 py-0.5 text-[11px] font-medium uppercase tracking-wide text-slate-600 dark:border-slate-700/80 dark:bg-slate-800/80 dark:text-slate-200">
                  {task.status}
                </span>
              )}

              {task.priority && (
                <span
                  className={cn(
                    'inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium',
                    priorityColors[task.priority] || 'bg-slate-100 text-slate-800'
                  )}
                >
                  {task.priority}
                </span>
              )}
            </div>

            {description && (
              <p
                className="mt-3 text-sm text-slate-600 dark:text-slate-300"
                style={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                }}
              >
                {description}
              </p>
            )}

            <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-500 dark:text-slate-400">
              {task.assignees.length > 0 && <span>👤 {task.assignees.join(', ')}</span>}
              {task.due_date && (
                <span>
                  📅 Due {formatDistanceToNow(new Date(task.due_date), { addSuffix: true })}
                </span>
              )}
            </div>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="flex-shrink-0"
            onClick={openInNotion}
            title="Open in Notion"
          >
            <ExternalLink className="h-4 w-4" />
          </Button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Button type="button" variant="outline" size="sm" className="gap-1" onClick={openInNotion}>
            <ExternalLink className="h-3.5 w-3.5" />
            View in Notion
          </Button>

          {task.status?.toLowerCase() !== 'done' && (
            <Button size="sm" className="gap-1" onClick={handleMarkDone}>
              <CheckCircle2 className="h-3.5 w-3.5" />
              Mark Done
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
