import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { apiClient } from '../api/client';
import { useChatStore } from '../store/chatStore';

interface AuthModalProps {
  onClose: () => void;
}

export function AuthModal({ onClose }: AuthModalProps) {
  const [apiKey, setApiKey] = useState('');
  const [databaseId, setDatabaseId] = useState('');
  const { setDatabaseId: setStoreDbId, clearMessages } = useChatStore();

  useEffect(() => {
    // Load current values
    setApiKey(apiClient.getApiKey() || '');
    setDatabaseId(useChatStore.getState().databaseId || '');
  }, []);

  const handleSave = () => {
    if (apiKey.trim()) {
      apiClient.setApiKey(apiKey.trim());
    }
    if (databaseId.trim()) {
      setStoreDbId(databaseId.trim());
    }
    onClose();
  };

  const handleLogout = () => {
    apiClient.clearApiKey();
    setStoreDbId('');
    clearMessages();
    setApiKey('');
    setDatabaseId('');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Settings</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <CardDescription>
            Configure your Notion API credentials and database ID
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
              Notion API Key
            </label>
            <Input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="secret_..."
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              Get your API key from the Notion integration settings
            </p>
          </div>

          <div>
            <label htmlFor="databaseId" className="block text-sm font-medium text-gray-700 mb-1">
              Notion Database ID
            </label>
            <Input
              id="databaseId"
              value={databaseId}
              onChange={(e) => setDatabaseId(e.target.value)}
              placeholder="1a2b3c4d5e6f7890abcdef1234567890"
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">
              The ID of your Notion tasks database
            </p>
          </div>

          <div className="flex gap-2 pt-2">
            <Button onClick={handleSave} className="flex-1">
              Save
            </Button>
            <Button onClick={handleLogout} variant="outline">
              Logout
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
