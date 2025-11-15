import { useState, useEffect } from 'react';
import { Database, Info, Key, KeyRound, Trash2, X } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { apiClient } from '../api/client';
import { useChatStore } from '../store/chatStore';
import { useTokens } from '../hooks/useTokens';

interface AuthModalProps {
  onClose: () => void;
}

export function AuthModal({ onClose }: AuthModalProps) {
  const [apiKey, setApiKey] = useState(() => apiClient.getApiKey() || '');
  const [databaseId, setDatabaseId] = useState(() => useChatStore.getState().databaseId || '');
  const [activeTab, setActiveTab] = useState<'api' | 'tokens' | 'workspace'>('api');
  const { setDatabaseId: setStoreDbId, clearMessages, selectedTokenId, setSelectedTokenId } = useChatStore();
  
  // Token management
  const { tokens, isLoading: tokensLoading, error: tokensError, loadTokens, createToken, deleteToken } = useTokens();
  const [newTokenName, setNewTokenName] = useState('');
  const [newTokenValue, setNewTokenValue] = useState('');
  const [newTokenDescription, setNewTokenDescription] = useState('');
  const [isCreatingToken, setIsCreatingToken] = useState(false);

  // Load tokens when component mounts
  useEffect(() => {
    loadTokens();
  }, [loadTokens]);

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

  const handleCreateToken = async () => {
    if (!newTokenName.trim() || !newTokenValue.trim()) {
      return;
    }

    setIsCreatingToken(true);
    try {
      await createToken({
        name: newTokenName.trim(),
        token: newTokenValue.trim(),
        description: newTokenDescription.trim() || undefined,
      });
      // Clear form
      setNewTokenName('');
      setNewTokenValue('');
      setNewTokenDescription('');
    } catch (error) {
      console.error('Failed to create token:', error);
    } finally {
      setIsCreatingToken(false);
    }
  };

  const handleSelectToken = (tokenId: string) => {
    setSelectedTokenId(tokenId === selectedTokenId ? null : tokenId);
  };

  const handleDeleteToken = async (tokenId: string) => {
    try {
      await deleteToken(tokenId);
      // If deleted token was selected, clear selection
      if (tokenId === selectedTokenId) {
        setSelectedTokenId(null);
      }
    } catch (error) {
      console.error('Failed to delete token:', error);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 px-4 py-6 backdrop-blur-lg">
      <div className="relative w-full max-w-2xl rounded-3xl border border-white/20 bg-white/95 p-6 shadow-2xl dark:border-slate-800/80 dark:bg-slate-900/95">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-5 top-5 rounded-full border border-transparent p-2 text-slate-500 transition hover:border-slate-200 hover:text-slate-900 dark:text-slate-300 dark:hover:border-slate-700"
          aria-label="Close settings"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="mb-6 pr-10">
          <p className="text-xs uppercase tracking-wide text-slate-500">Workspace</p>
          <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">Notion Integration Settings</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Manage your API credentials and workspace status.
          </p>
        </div>

        <div className="mb-6 flex flex-wrap gap-2 rounded-2xl bg-slate-100/70 p-2 dark:bg-slate-800/60">
          {[
            { id: 'api', label: 'API Configuration', icon: KeyRound },
            { id: 'tokens', label: 'Manage Tokens', icon: Key },
            { id: 'workspace', label: 'Workspace Info', icon: Info },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as 'api' | 'tokens' | 'workspace')}
                className={`flex flex-1 items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-white text-slate-900 shadow dark:bg-slate-900 dark:text-white'
                    : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white'
                }`}
                aria-pressed={isActive}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {activeTab === 'api' ? (
          <div className="space-y-5">
            <div>
              <label htmlFor="apiKey" className="mb-1 flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-200">
                <KeyRound className="h-4 w-4" /> Notion API Key
              </label>
              <Input
                id="apiKey"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="secret_..."
                className="w-full"
              />
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                Stored locally in this browser. Generate from Notion integrations.
              </p>
            </div>

            <div>
              <label htmlFor="databaseId" className="mb-1 flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-200">
                <Database className="h-4 w-4" /> Notion Database ID
              </label>
              <Input
                id="databaseId"
                value={databaseId}
                onChange={(e) => setDatabaseId(e.target.value)}
                placeholder="1a2b3c4d5e6f7890abcdef1234567890"
                className="w-full"
              />
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                Reachable under Settings → Notion when viewing your database.
              </p>
            </div>

            <div className="flex flex-wrap gap-2 pt-2">
              <Button onClick={handleSave} className="flex-1 min-w-[120px]">
                Save
              </Button>
              <Button onClick={handleLogout} variant="outline" className="min-w-[120px]">
                Logout
              </Button>
            </div>
          </div>
        ) : activeTab === 'tokens' ? (
          <div className="space-y-5">
            {/* Add Token Form */}
            <div className="rounded-2xl border border-slate-200/70 bg-slate-50/70 p-4 dark:border-slate-700/70 dark:bg-slate-800/70">
              <h3 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-200">Add New Token</h3>
              <div className="space-y-3">
                <div>
                  <Input
                    type="text"
                    value={newTokenName}
                    onChange={(e) => setNewTokenName(e.target.value)}
                    placeholder="Token Name"
                    className="w-full"
                  />
                </div>
                <div>
                  <Input
                    type="password"
                    value={newTokenValue}
                    onChange={(e) => setNewTokenValue(e.target.value)}
                    placeholder="secret_..."
                    className="w-full"
                  />
                </div>
                <div>
                  <Input
                    type="text"
                    value={newTokenDescription}
                    onChange={(e) => setNewTokenDescription(e.target.value)}
                    placeholder="Description (optional)"
                    className="w-full"
                  />
                </div>
                <Button
                  onClick={handleCreateToken}
                  disabled={!newTokenName.trim() || !newTokenValue.trim() || isCreatingToken}
                  className="w-full"
                >
                  {isCreatingToken ? 'Adding...' : 'Add Token'}
                </Button>
              </div>
            </div>

            {/* Error Display */}
            {tokensError && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700 dark:border-rose-800 dark:bg-rose-900/30 dark:text-rose-300">
                {tokensError}
              </div>
            )}

            {/* Token List */}
            <div>
              <h3 className="mb-3 text-sm font-medium text-slate-700 dark:text-slate-200">Your Tokens</h3>
              {tokensLoading ? (
                <div className="text-center text-sm text-slate-500">Loading tokens...</div>
              ) : tokens.length === 0 ? (
                <div className="rounded-xl border border-dashed border-slate-300 p-4 text-center text-sm text-slate-500 dark:border-slate-700">
                  No tokens yet. Add one above to get started.
                </div>
              ) : (
                <div className="space-y-2">
                  {tokens.map((token) => (
                    <div
                      key={token.id}
                      className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-900"
                    >
                      <input
                        type="radio"
                        name="selectedToken"
                        checked={token.id === selectedTokenId}
                        onChange={() => handleSelectToken(token.id)}
                        className="h-4 w-4"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-slate-900 dark:text-white">{token.name}</div>
                        <div className="text-xs text-slate-500 dark:text-slate-400">{token.token_preview}</div>
                        {token.description && (
                          <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">{token.description}</div>
                        )}
                      </div>
                      <Button
                        onClick={() => handleDeleteToken(token.id)}
                        variant="outline"
                        size="sm"
                        className="text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-900/30"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-slate-200/70 bg-white/70 p-4 dark:border-slate-700/70 dark:bg-slate-900/70">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-500 dark:text-slate-400">
                <Database className="h-4 w-4" /> Database ID
              </div>
              <p className="mt-2 text-base font-semibold text-slate-900 dark:text-white">
                {databaseId || 'Not configured'}
              </p>
            </div>
            <div className="rounded-2xl border border-slate-200/70 bg-white/70 p-4 dark:border-slate-700/70 dark:bg-slate-900/70">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-500 dark:text-slate-400">
                <Info className="h-4 w-4" /> Session Status
              </div>
              <p className="mt-2 text-base font-semibold text-emerald-600 dark:text-emerald-300">
                {databaseId ? 'Connected' : 'Waiting for credentials'}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {databaseId ? 'Commands can access your Notion database.' : 'Enter your API key and database ID to begin.'}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
