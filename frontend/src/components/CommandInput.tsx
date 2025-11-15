import { useState, type KeyboardEvent } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Send, Loader2 } from 'lucide-react';
import { useChatStore } from '../store/chatStore';

export function CommandInput() {
  const [input, setInput] = useState('');
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

  return (
    <div className="border-t bg-white p-4">
      <div className="flex items-center gap-2 max-w-4xl mx-auto">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a command (e.g., /task list) or / for help..."
          disabled={isLoading}
          className="flex-1"
          autoFocus
        />
        <Button
          onClick={handleSubmit}
          disabled={isLoading || !input.trim()}
          size="icon"
          className="flex-shrink-0"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
        </Button>
      </div>
      
      {isLoading && (
        <div className="text-xs text-gray-500 text-center mt-2">
          Processing command...
        </div>
      )}
    </div>
  );
}
