/** Generic API response wrapper matching backend schema */
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

/** Paginated response for list endpoints (matches BE snake_case) */
export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/** Error response from the API */
export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

/** API request options */
export interface RequestOptions {
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

/** SSE event for streaming responses */
export interface SSEEvent {
  event: string;
  data: string;
}
