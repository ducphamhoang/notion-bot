/**
 * API client for Notion API token management.
 */

import { apiClient } from './client';
import type {
  NotionToken,
  CreateTokenRequest,
  UpdateTokenRequest,
  TokenListResponse,
} from '../types/token';

/**
 * Token management API client.
 */
export const tokenApi = {
  /**
   * List all Notion API tokens.
   * @param activeOnly - Filter to only active tokens (default: true)
   * @returns Promise resolving to TokenListResponse
   */
  async listTokens(activeOnly: boolean = true): Promise<TokenListResponse> {
    return apiClient.get<TokenListResponse>('/tokens', {
      active_only: activeOnly.toString(),
    });
  },

  /**
   * Create a new Notion API token.
   * @param data - Token creation request data
   * @returns Promise resolving to created token
   */
  async createToken(data: CreateTokenRequest): Promise<NotionToken> {
    return apiClient.post<NotionToken>('/tokens', data);
  },

  /**
   * Get a single Notion API token by ID.
   * @param id - Token ID to retrieve
   * @returns Promise resolving to token
   */
  async getToken(id: string): Promise<NotionToken> {
    return apiClient.get<NotionToken>(`/tokens/${id}`);
  },

  /**
   * Update an existing Notion API token.
   * @param id - Token ID to update
   * @param data - Token update request data
   * @returns Promise resolving to updated token
   */
  async updateToken(
    id: string,
    data: UpdateTokenRequest
  ): Promise<NotionToken> {
    return apiClient.patch<NotionToken>(`/tokens/${id}`, data);
  },

  /**
   * Delete a Notion API token.
   * @param id - Token ID to delete
   * @returns Promise resolving when deletion is complete
   */
  async deleteToken(id: string): Promise<void> {
    return apiClient.delete<void>(`/tokens/${id}`);
  },
};
