'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function TanstackQueryProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
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
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
