import { useCallback } from 'react';
import type { DomainObject } from '@/types/domain-objects';
import type { ActionFormRenderer } from './use-action-executor';
import { getActionRenderer, type ActionType } from '@/lib/actions/registry';

/**
 * Hook that creates an ActionFormRenderer using the centralized action registry
 *
 * This eliminates the need for manual switch statements at each callsite.
 * The registry automatically looks up the correct render function for each action.
 *
 * @param objectData Optional object data to pass to the action's render function
 * @returns An ActionFormRenderer that can be passed to useActionExecutor
 */
export function useActionFormRenderer(
  objectData?: DomainObject
): ActionFormRenderer {
  return useCallback<ActionFormRenderer>(
    ({ action, onSubmit, onCancel, isSubmitting }) => {
      const actionType = action.action as ActionType;
      const render = getActionRenderer(actionType);

      // No render function registered - action will be executed directly
      if (!render) {
        return null;
      }

      // Call the render function with all parameters
      return render({
        objectData,
        onSubmit: (data) => {
          // Transform the form data into the action body format
          onSubmit({
            action: actionType,
            data,
          } as Parameters<typeof onSubmit>[0]);
        },
        onCancel,
        isSubmitting,
      });
    },
    [objectData]
  );
}

/**
 * @deprecated Use useActionFormRenderer with objectData instead
 *
 * Hook that creates an ActionFormRenderer with a specific context object
 *
 * @example
 * ```tsx
 * // Old way:
 * const renderForm = useActionFormRendererWithContext(data);
 *
 * // New way:
 * const renderForm = useActionFormRenderer(data);
 * ```
 */
export function useActionFormRendererWithContext(
  context: DomainObject
): ActionFormRenderer {
  return useActionFormRenderer(context);
}
