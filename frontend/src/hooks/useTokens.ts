/**
 * React hook for managing Notion API tokens.
 */

import { useState } from 'react';
import { tokenApi } from '../api/tokenApi';
import type {
  NotionToken,
  CreateTokenRequest,
  UpdateTokenRequest,
} from '../types/token';

interface UseTokensReturn {
  tokens: NotionToken[];
  isLoading: boolean;
  error: string | null;
  loadTokens: () => Promise<void>;
  createToken: (data: CreateTokenRequest) => Promise<NotionToken>;
  updateToken: (id: string, data: UpdateTokenRequest) => Promise<NotionToken>;
  deleteToken: (id: string) => Promise<void>;
}

/**
 * Hook for managing Notion API tokens with state management.
 * @returns Token management state and methods
 */
export const useTokens = (): UseTokensReturn => {
  const [tokens, setTokens] = useState<NotionToken[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load all tokens from the API.
   */
  const loadTokens = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await tokenApi.listTokens();
      setTokens(response.tokens);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load tokens';
      setError(message);
      console.error('Failed to load tokens:', err);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Create a new token and add it to the list.
   * @param data - Token creation request data
   * @returns Promise resolving to created token
   */
  const createToken = async (data: CreateTokenRequest): Promise<NotionToken> => {
    setError(null);

    try {
      const newToken = await tokenApi.createToken(data);
      setTokens((prev) => [newToken, ...prev]);
      return newToken;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create token';
      setError(message);
      console.error('Failed to create token:', err);
      throw err;
    }
  };

  /**
   * Update an existing token and refresh the list.
   * @param id - Token ID to update
   * @param data - Token update request data
   * @returns Promise resolving to updated token
   */
  const updateToken = async (
    id: string,
    data: UpdateTokenRequest
  ): Promise<NotionToken> => {
    setError(null);

    try {
      const updatedToken = await tokenApi.updateToken(id, data);
      setTokens((prev) =>
        prev.map((token) => (token.id === id ? updatedToken : token))
      );
      return updatedToken;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update token';
      setError(message);
      console.error('Failed to update token:', err);
      throw err;
    }
  };

  /**
   * Delete a token and remove it from the list.
   * @param id - Token ID to delete
   * @returns Promise resolving when deletion is complete
   */
  const deleteToken = async (id: string): Promise<void> => {
    setError(null);

    try {
      await tokenApi.deleteToken(id);
      setTokens((prev) => prev.filter((token) => token.id !== id));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete token';
      setError(message);
      console.error('Failed to delete token:', err);
      throw err;
    }
  };

  return {
    tokens,
    isLoading,
    error,
    loadTokens,
    createToken,
    updateToken,
    deleteToken,
  };
};
