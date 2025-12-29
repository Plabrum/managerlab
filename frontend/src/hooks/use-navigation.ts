import { useCallback } from 'react';
import { useNavigate } from '@tanstack/react-router';
import type { NavigateOptions } from '@tanstack/react-router';

/**
 * Navigation utilities hook.
 * Provides helpers for common navigation patterns.
 *
 * NOTE: For type-safe navigation with route params, prefer using TanStack Router's
 * built-in navigate directly:
 *
 * @example Type-safe navigation (preferred)
 * ```tsx
 * import { useNavigate } from '@tanstack/react-router';
 *
 * function MyComponent() {
 *   const navigate = useNavigate();
 *
 *   // Type-safe with autocomplete and validation
 *   navigate({
 *     to: '/campaigns/$id',
 *     params: { id: '123' }, // TypeScript knows 'id' is required
 *     search: { tab: 'activity' } // TypeScript validates search params
 *   });
 * }
 * ```
 *
 * @example String-based navigation (when you need dynamic base URLs)
 * ```tsx
 * const { navigateToLink } = useNavigation('/base');
 * navigateToLink('campaigns/123'); // navigates to /base/campaigns/123
 * ```
 */
export function useNavigation(baseUrl = '') {
  const navigate = useNavigate();

  /**
   * Navigate to a link, optionally prefixed with a base URL.
   * Handles trailing/leading slashes properly.
   */
  const navigateToLink = useCallback(
    (link: string, options?: Omit<NavigateOptions, 'to'>) => {
      // Clean up slashes to prevent double slashes or missing slashes
      const cleanBase = baseUrl.replace(/\/+$/, ''); // Remove trailing slashes
      const cleanLink = link.replace(/^\/+/, ''); // Remove leading slashes
      const fullUrl = cleanBase ? `${cleanBase}/${cleanLink}` : `/${cleanLink}`;

      navigate({ to: fullUrl as '/', ...options });
    },
    [baseUrl, navigate]
  );

  return { navigateToLink, navigate };
}
