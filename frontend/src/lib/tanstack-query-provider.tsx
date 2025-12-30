import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { getCacheScope } from './cache-config';

// Singleton QueryClient instance
// Created once and shared across the app for consistent caching
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Dynamic stale time based on query key pattern
      // Uses getCacheScope() to determine cache lifetime:
      staleTime: (query) => getCacheScope(query.queryKey),
      retry: (failureCount, error) => {
        // Only retry on network errors and specific recoverable status codes
        if (error && typeof error === 'object' && 'status' in error) {
          const status = error.status as number;
          // Only retry on 503 Service Unavailable (temporary overload)
          if (status === 503) {
            return failureCount < 3;
          }
          // Don't retry on any other HTTP status codes (4xx, 5xx, etc.)
          return false;
        }
        // Retry on network errors (no status code means network/connection issue)
        return failureCount < 3;
      },
    },
  },
});

export function TanstackQueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
