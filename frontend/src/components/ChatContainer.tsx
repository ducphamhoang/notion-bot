import { MessageList } from './MessageList';
import { CommandInput } from './CommandInput';
import { Settings } from 'lucide-react';
import { Button } from './ui/button';
import { useState } from 'react';
import { AuthModal } from './AuthModal';

export function ChatContainer() {
  const [showSettings, setShowSettings] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">Notion Task Bot</h1>
            <p className="text-xs text-gray-500">Chat interface for managing tasks</p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowSettings(true)}
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </Button>
        </div>
      </header>

      {/* Messages */}
      <MessageList />

      {/* Input */}
      <CommandInput />

      {/* Settings Modal */}
      {showSettings && <AuthModal onClose={() => setShowSettings(false)} />}
    </div>
  );
}
