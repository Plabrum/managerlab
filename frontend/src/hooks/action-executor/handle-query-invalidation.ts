import type { ActionExecutionResponse } from '@/openapi/ariveAPI.schemas';
import type { QueryClient } from '@tanstack/react-query';

/**
 * Handle query invalidation after action execution
 * Uses backend's invalidate_queries and optionally calls custom invalidation logic
 */
export function handleQueryInvalidation(
  queryClient: QueryClient,
  response: ActionExecutionResponse,
  onInvalidate?: (queryClient: QueryClient, backendQueryKeys: string[]) => void
): void {
  const backendQueryKeys = response.invalidate_queries || [];

  if (backendQueryKeys.length > 0) {
    // Use invalidation queries from backend response
    backendQueryKeys.forEach((queryKey) => {
      queryClient.invalidateQueries({
        queryKey: [queryKey],
        refetchType: 'active',
      });
    });
  }

  // Allow frontend to perform additional custom invalidation
  if (onInvalidate) {
    onInvalidate(queryClient, backendQueryKeys);
  }
}
