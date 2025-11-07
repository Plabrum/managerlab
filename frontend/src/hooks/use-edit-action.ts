'use client';

import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { useCallback, useEffect } from 'react';
import type { ActionDTO } from '@/openapi/managerLab.schemas';

/**
 * Hook to manage edit mode via URL parameters with permission checking
 *
 * @param actions - Array of available actions from the API
 * @param editActionPattern - Pattern to identify edit/update actions (default: '_update')
 * @returns Object with edit state, handlers, and permission info
 *
 * Features:
 * - Automatically finds the edit/update action from available actions
 * - Checks if user has permission to edit
 * - Clears ?edit param if user navigates to it without permission
 * - Prevents opening edit mode if not available
 *
 * @example
 * ```tsx
 * const { isEditMode, openEdit, closeEdit, isEditAvailable } = useEditAction({
 *   actions: data.actions,
 * });
 *
 * // Edit button only shows if available
 * {isEditAvailable && <Button onClick={openEdit}>Edit</Button>}
 *
 * // Form controlled by URL + permissions
 * <UpdateForm isOpen={isEditMode} onClose={closeEdit} />
 * ```
 */
export function useEditAction({
  actions,
  editActionPattern = '_update',
}: {
  actions: ActionDTO[];
  editActionPattern?: string;
}) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // Find the edit/update action from available actions
  const editAction = actions.find((action) =>
    action.action.includes(editActionPattern)
  );

  // Check if edit action exists and is available
  const isEditAvailable = editAction?.available !== false;

  // Check if edit mode is active via URL parameter
  const hasEditParam = searchParams.get('edit') !== null;

  // Handler to remove ?edit parameter from URL
  const clearEdit = useCallback(() => {
    const params = new URLSearchParams(searchParams.toString());
    params.delete('edit');
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
  }, [searchParams, pathname, router]);

  // If edit mode is active but user doesn't have permission, clear it
  useEffect(() => {
    if (hasEditParam && !isEditAvailable) {
      clearEdit();
    }
  }, [hasEditParam, isEditAvailable, clearEdit]);

  // Handler to add ?edit parameter to URL (only if available)
  const openEdit = useCallback(() => {
    if (!isEditAvailable) {
      console.warn('Edit action is not available');
      return;
    }
    const params = new URLSearchParams(searchParams.toString());
    params.set('edit', 'true');
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
  }, [isEditAvailable, searchParams, pathname, router]);

  return {
    /** Whether edit mode is currently active (URL param + permission check) */
    isEditMode: hasEditParam && isEditAvailable,
    /** Open edit mode (sets ?edit=true) - no-op if not available */
    openEdit,
    /** Close edit mode (removes ?edit param) */
    closeEdit: clearEdit,
    /** Whether user has permission to edit */
    isEditAvailable,
    /** The edit action object (if found) */
    editAction,
  };
}
