import { useEffect, useRef, useState, type KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { QuickCommandChips } from './QuickCommandChips';
import { TypingIndicator } from './TypingIndicator';
import { useChatStore } from '../store/chatStore';

interface CommandInputProps {
  onRegisterFill?: (fill: ((command: string) => void) | null) => void;
}

export function CommandInput({ onRegisterFill }: CommandInputProps) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const { sendCommand, isLoading } = useChatStore();

  const handleSubmit = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    setInput('');
    await sendCommand(trimmed);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const fillInput = (value: string) => {
    setInput(value);
    inputRef.current?.focus();
  };

  useEffect(() => {
    onRegisterFill?.(fillInput);
    return () => onRegisterFill?.(null);
  }, [onRegisterFill]);

  return (
    <div className="border-t border-white/50 bg-white/80 px-4 py-4 shadow-[0_-20px_45px_-35px_rgba(15,23,42,0.5)] backdrop-blur-glass dark:border-slate-800/80 dark:bg-slate-900/80">
      <div className="mx-auto flex max-w-4xl flex-col gap-3">
        <QuickCommandChips
          onCommandSelect={(command) => fillInput(`${command} `)}
          disabled={isLoading}
        />

        <div className="flex items-center gap-2 rounded-2xl border border-white/60 bg-white/90 px-3 py-2 shadow-glass dark:border-slate-800/80 dark:bg-slate-900/80">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command (e.g., /task list) or / for help..."
            disabled={isLoading}
            className="flex-1 border-none bg-transparent shadow-none focus-visible:ring-0"
            autoFocus
          />
          <Button
            onClick={handleSubmit}
            disabled={isLoading || !input.trim()}
            size="icon"
            className="flex-shrink-0 rounded-full"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Processing command...</span>
            <TypingIndicator />
          </div>
        ) : (
          <div className="text-xs text-slate-400">
            Need ideas? Try <code className="rounded bg-slate-100 px-1 dark:bg-slate-800">/task list status:"In Progress"</code>
          </div>
        )}
      </div>
    </div>
  );
}
