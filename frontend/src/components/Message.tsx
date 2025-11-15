import { formatDistanceToNow } from 'date-fns';
import type { Message as MessageType } from '../types/message';
import { TaskCard } from './TaskCard';
import { cn } from '../lib/utils';

interface MessageProps {
  message: MessageType;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';
  const isError = message.role === 'error' || message.error;

  return (
    <div
      className={cn(
        'flex w-full mb-4',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-2 shadow-sm',
          isUser && 'bg-blue-600 text-white',
          !isUser && !isError && 'bg-gray-100 text-gray-900',
          isError && 'bg-red-100 text-red-900 border border-red-300'
        )}
      >
        <div className="text-sm whitespace-pre-wrap break-words">
          {message.content}
        </div>
        
        {/* Render task list if data is present */}
        {message.data?.data && Array.isArray(message.data.data) && (
          <div className="mt-3 space-y-2">
            {message.data.data.map((task: any) => (
              <TaskCard key={task.notion_task_id} task={task} />
            ))}
          </div>
        )}
        
        <div
          className={cn(
            'text-xs mt-1',
            isUser ? 'text-blue-200' : isError ? 'text-red-700' : 'text-gray-500'
          )}
        >
          {formatDistanceToNow(message.timestamp, { addSuffix: true })}
        </div>
      </div>
    </div>
  );
}
