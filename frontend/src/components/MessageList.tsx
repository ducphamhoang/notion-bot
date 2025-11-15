import { useEffect, useRef } from 'react';
import { Message } from './Message';
import { useChatStore } from '../store/chatStore';
import { TypingIndicator } from './TypingIndicator';

export function MessageList() {
  const messages = useChatStore((state) => state.messages);
  const isLoading = useChatStore((state) => state.isLoading);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center bg-gradient-to-b from-white/70 to-slate-50/80 px-6 py-10 text-center dark:from-slate-900/70 dark:to-slate-950/80">
        <div className="max-w-md space-y-3 rounded-3xl border border-dashed border-slate-200/70 bg-white/80 px-6 py-8 shadow-glass backdrop-blur-glass dark:border-slate-700/70 dark:bg-slate-900/60">
          <h3 className="text-xl font-semibold text-slate-900 dark:text-white">Welcome to Notion Task Bot</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Start by typing a command like <code className="rounded-md bg-slate-100 px-2 py-0.5 dark:bg-slate-800">/task list</code> to see your tasks.
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Tip: press <code className="rounded-md bg-slate-100 px-1 py-0.5 dark:bg-slate-800">/</code> to view all commands.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="scrollbar-thin flex-1 overflow-y-auto bg-gradient-to-b from-transparent via-white/60 to-transparent px-4 py-6 dark:via-slate-900/50">
      <div className="space-y-3">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        {isLoading && <TypingIndicator className="mt-2 pl-12" />}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
