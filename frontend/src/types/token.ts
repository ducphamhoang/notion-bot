/**
 * Type definitions for Notion API token management.
 * These types mirror the backend DTOs for type safety.
 */

/**
 * Notion API token response with masked token value.
 */
export interface NotionToken {
  /** Token ID */
  id: string;
  /** Human-readable token name */
  name: string;
  /** Masked token value showing last 6 characters */
  token_preview: string;
  /** Optional token description */
  description?: string;
  /** Token creation timestamp */
  created_at: string;
  /** Token last update timestamp */
  updated_at: string;
  /** Whether the token is active and can be used */
  is_active: boolean;
}

/**
 * Request payload for creating a new Notion API token.
 */
export interface CreateTokenRequest {
  /** Human-readable token name (1-100 chars) */
  name: string;
  /** Raw Notion API token value (must start with 'secret_') */
  token: string;
  /** Optional description for this token */
  description?: string;
}

/**
 * Request payload for updating an existing Notion API token.
 */
export interface UpdateTokenRequest {
  /** Optional new name */
  name?: string;
  /** Optional new description */
  description?: string;
  /** Optional active status */
  is_active?: boolean;
}

/**
 * Response for listing Notion API tokens.
 */
export interface TokenListResponse {
  /** List of tokens with masked values */
  tokens: NotionToken[];
  /** Total number of tokens */
  total: number;
}
