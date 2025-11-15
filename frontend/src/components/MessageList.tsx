import { useEffect, useRef } from 'react';
import { Message } from './Message';
import { useChatStore } from '../store/chatStore';

export function MessageList() {
  const messages = useChatStore((state) => state.messages);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500 p-4">
        <div className="text-center max-w-md">
          <h3 className="text-lg font-semibold mb-2">Welcome to Notion Task Bot</h3>
          <p className="text-sm">
            Start by typing a command like <code className="bg-gray-100 px-1 rounded">/task list</code> to see your tasks.
          </p>
          <p className="text-xs mt-2">
            Type <code className="bg-gray-100 px-1 rounded">/</code> to see all available commands.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}
