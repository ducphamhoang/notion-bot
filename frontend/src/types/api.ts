// Common API types

export interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  status?: number;
}
