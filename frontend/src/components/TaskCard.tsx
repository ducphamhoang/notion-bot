import { Card, CardContent } from './ui/card';
import { ExternalLink } from 'lucide-react';
import type { TaskSummary } from '../types/task';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '../lib/utils';

interface TaskCardProps {
  task: TaskSummary;
}

export function TaskCard({ task }: TaskCardProps) {
  const priorityColors = {
    High: 'bg-red-100 text-red-800 border-red-300',
    Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    Low: 'bg-green-100 text-green-800 border-green-300',
  };

  return (
    <Card className="bg-white hover:shadow-md transition-shadow">
      <CardContent className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-sm text-gray-900 truncate">
              {task.title}
            </h3>
            
            <div className="flex flex-wrap items-center gap-2 mt-2">
              {task.status && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  {task.status}
                </span>
              )}
              
              {task.priority && (
                <span
                  className={cn(
                    'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border',
                    priorityColors[task.priority] || 'bg-gray-100 text-gray-800'
                  )}
                >
                  {task.priority}
                </span>
              )}
            </div>

            {task.assignees.length > 0 && (
              <div className="text-xs text-gray-600 mt-1">
                👤 {task.assignees.join(', ')}
              </div>
            )}

            {task.due_date && (
              <div className="text-xs text-gray-600 mt-1">
                📅 Due: {formatDistanceToNow(new Date(task.due_date), { addSuffix: true })}
              </div>
            )}
          </div>

          <a
            href={task.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-shrink-0 text-blue-600 hover:text-blue-800 transition-colors"
            title="Open in Notion"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
