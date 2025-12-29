import { AxiosError } from 'axios';
import { toast } from 'sonner';

/**
 * API error response structure from Litestar backend
 */
interface ApiErrorResponse {
  detail?: string;
  status_code?: number;
  extra?:
    | Array<{
        message?: string;
        key?: string;
        source?: string;
      }>
    | Record<string, unknown>;
}

/**
 * Options for handling errors
 */
interface HandleErrorOptions {
  /** Custom fallback message if no error detail is available */
  fallbackMessage?: string;
  /** Whether to show a toast notification (default: true) */
  showToast?: boolean;
  /** Custom toast function (default: toast.error) */
  toastFn?: (message: string) => void;
  /** Whether to log the error to console (default: true) */
  logError?: boolean;
}

/**
 * Extract a user-friendly error message from an error object
 */
export function getErrorMessage(
  error: unknown,
  fallbackMessage = 'An error occurred'
): string {
  // Handle Axios errors (from our API client)
  if (error && typeof error === 'object' && 'isAxiosError' in error) {
    const axiosError = error as AxiosError<ApiErrorResponse>;

    const responseData = axiosError.response?.data;

    // Try to extract validation errors from extra array (Litestar validation errors)
    if (responseData?.extra && Array.isArray(responseData.extra)) {
      const messages = responseData.extra
        .map((item) => item.message)
        .filter((msg): msg is string => typeof msg === 'string');

      if (messages.length > 0) {
        // Return first validation message or join multiple messages
        return messages.length === 1 ? messages[0] : messages.join('; ');
      }
    }

    // Try to extract detail from response
    if (responseData?.detail) {
      return responseData.detail;
    }

    // Handle specific HTTP status codes
    const status = axiosError.response?.status;
    if (status) {
      if (status === 401) {
        return 'Authentication required. Please sign in again.';
      }
      if (status === 403) {
        return 'You do not have permission to perform this action.';
      }
      if (status === 404) {
        return 'The requested resource was not found.';
      }
      if (status >= 500) {
        return 'Server error. Please try again later.';
      }
    }

    // Network errors
    if (axiosError.code === 'ERR_NETWORK') {
      return 'Network error. Please check your connection.';
    }

    // Request timeout
    if (axiosError.code === 'ECONNABORTED') {
      return 'Request timeout. Please try again.';
    }
  }

  // Handle standard Error objects
  if (error instanceof Error) {
    return error.message || fallbackMessage;
  }

  // Handle errors with 'detail' property (some API responses)
  if (error && typeof error === 'object' && 'detail' in error) {
    const detail = (error as { detail: unknown }).detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  // Handle errors with 'message' property
  if (error && typeof error === 'object' && 'message' in error) {
    const message = (error as { message: unknown }).message;
    if (typeof message === 'string') {
      return message;
    }
  }

  return fallbackMessage;
}

/**
 * Handle an error by extracting the message and optionally showing a toast
 *
 * @example
 * ```ts
 * try {
 *   await someApiCall();
 * } catch (error) {
 *   handleError(error, { fallbackMessage: 'Failed to save data' });
 * }
 * ```
 *
 * @example
 * ```ts
 * // In React Query mutation
 * const mutation = useMutation({
 *   onError: (error) => {
 *     handleError(error, { fallbackMessage: 'Failed to create item' });
 *   }
 * });
 * ```
 */
export function handleError(
  error: unknown,
  options: HandleErrorOptions = {}
): string {
  const {
    fallbackMessage = 'An error occurred',
    showToast = true,
    toastFn = toast.error,
    logError = true,
  } = options;

  const message = getErrorMessage(error, fallbackMessage);

  if (logError) {
    console.error('Error occurred:', error);
  }

  if (showToast) {
    toastFn(message);
  }

  return message;
}
