import { useNavigate, useSearch } from '@tanstack/react-router';
import { useCallback, useEffect } from 'react';
import type { ActionDTO } from '@/openapi/ariveAPI.schemas';

/**
 * Hook to manage edit mode via URL parameters with permission checking
 *
 * @param actions - Array of available actions from the API
 * @param editActionPattern - Pattern to identify edit actions (default: '__edit')
 * @returns Object with edit state, handlers, and permission info
 *
 * Features:
 * - Automatically finds the edit action from available actions
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
  editActionPattern = '__edit',
}: {
  actions: ActionDTO[];
  editActionPattern?: string;
}) {
  const navigate = useNavigate();
  const search = useSearch({ strict: false }) as { edit?: boolean };

  // Find the edit/update action from available actions
  const editAction = actions.find((action) =>
    action.action.includes(editActionPattern)
  );

  // Check if edit action exists and is available
  const isEditAvailable = editAction?.available !== false;

  // Check if edit mode is active via URL parameter
  const hasEditParam = search.edit === true;

  // Handler to remove ?edit parameter from URL
  const clearEdit = useCallback(() => {
    navigate({
      to: '.',
      search: (prev: Record<string, unknown>) => {
        const { edit, ...rest } = prev as { edit?: boolean };
        return rest;
      },
    });
  }, [navigate]);

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
    navigate({
      to: '.',
      search: (prev: Record<string, unknown>) => ({ ...prev, edit: true }),
    });
  }, [isEditAvailable, navigate]);

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
