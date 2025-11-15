// API client with authentication and error handling

import type { ErrorResponse, ApiError } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const REQUEST_TIMEOUT = 30000; // 30 seconds

export interface ApiClientConfig {
  apiKey?: string;
  timeout?: number;
}

class ApiClient {
  private apiKey: string | null = null;
  private timeout: number = REQUEST_TIMEOUT;

  constructor(config?: ApiClientConfig) {
    if (config?.apiKey) {
      this.apiKey = config.apiKey;
    }
    if (config?.timeout) {
      this.timeout = config.timeout;
    }
  }

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
    // Store in sessionStorage for persistence across page reloads
    sessionStorage.setItem('apiKey', apiKey);
  }

  getApiKey(): string | null {
    if (!this.apiKey) {
      // Try to load from sessionStorage
      this.apiKey = sessionStorage.getItem('apiKey');
    }
    return this.apiKey;
  }

  clearApiKey() {
    this.apiKey = null;
    sessionStorage.removeItem('apiKey');
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    const apiKey = this.getApiKey();
    if (apiKey) {
      // Use X-API-Key header for authentication
      headers['X-API-Key'] = apiKey;
    }

    return headers;
  }

  private async fetchWithTimeout(
    url: string,
    options: RequestInit
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw this.createApiError('TIMEOUT', 'Request timeout', 408);
      }
      throw error;
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      await this.handleErrorResponse(response);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json();
    return data as T;
  }

  private async handleErrorResponse(response: Response): Promise<never> {
    let errorData: ErrorResponse | undefined;

    try {
      errorData = await response.json();
    } catch {
      // Response doesn't contain JSON
    }

    if (errorData?.error) {
      throw this.createApiError(
        errorData.error.code,
        errorData.error.message,
        response.status,
        errorData.error.details
      );
    }

    // Fallback error messages
    const message = this.getDefaultErrorMessage(response.status);
    throw this.createApiError('UNKNOWN_ERROR', message, response.status);
  }

  private createApiError(
    code: string,
    message: string,
    status: number,
    details?: Record<string, any>
  ): ApiError {
    return {
      code,
      message,
      status,
      details,
    };
  }

  private getDefaultErrorMessage(status: number): string {
    switch (status) {
      case 400:
        return 'Invalid request data';
      case 401:
        return 'Authentication required';
      case 403:
        return 'Access denied';
      case 404:
        return 'Resource not found';
      case 409:
        return 'Resource already exists';
      case 429:
        return 'Rate limit exceeded. Please try again later.';
      case 502:
        return 'Notion API error. Please try again.';
      case 503:
        return 'Service temporarily unavailable';
      case 504:
        return 'Request timeout';
      default:
        return 'An unexpected error occurred';
    }
  }

  async get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${API_BASE_URL}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    const response = await this.fetchWithTimeout(url.toString(), {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(endpoint: string, body: any): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await this.fetchWithTimeout(url, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });

    return this.handleResponse<T>(response);
  }

  async patch<T>(endpoint: string, body: any): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await this.fetchWithTimeout(url, {
      method: 'PATCH',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });

    return this.handleResponse<T>(response);
  }

  async delete<T>(endpoint: string): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await this.fetchWithTimeout(url, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    return this.handleResponse<T>(response);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
