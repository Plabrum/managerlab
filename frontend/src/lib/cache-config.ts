/**
 * TanStack Query Cache Configuration
 *
 * Automatically determines cache times based on query key patterns.
 * All cache configuration is centralized here - never set staleTime in individual queries.
 */

export enum CacheScope {
  SESSION_LIFETIME = Infinity, // Metadata cached until page refresh
  DATA_QUERY = 60 * 1000, // User data cached for 60 seconds
}

const SESSION_LIFETIME_PATTERNS = [
  '/schema',
  '/teams',
  '/dashboards',
  '/views/',
  '/actions/',
  '/users/current_user',
  '/db_health',
] as const;

export function getCacheScope(queryKey: readonly unknown[]): number {
  const key = queryKey[0];

  if (typeof key === 'string') {
    const isSessionLifetime = SESSION_LIFETIME_PATTERNS.some((pattern) =>
      key.includes(pattern)
    );

    return isSessionLifetime
      ? CacheScope.SESSION_LIFETIME
      : CacheScope.DATA_QUERY;
  }

  return CacheScope.DATA_QUERY;
}
