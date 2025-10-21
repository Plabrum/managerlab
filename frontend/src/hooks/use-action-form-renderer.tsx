import { useCallback } from 'react';
import type { ActionDTO, ObjectDetailDTO } from '@/openapi/managerLab.schemas';
import type { ActionFormRenderer } from './use-action-executor';
import {
  getActionFormComponent,
  getActionDefaultValuesExtractor,
  type ActionType,
} from '@/lib/actions/registry';

/**
 * Hook that creates an ActionFormRenderer using the centralized action registry
 *
 * This eliminates the need for manual switch statements at each callsite.
 * The registry automatically looks up the correct form component for each action.
 *
 * @param objectData Optional object data to automatically extract default values from
 * @param customExtractor Optional custom function to override registry's default value extraction
 * @returns An ActionFormRenderer that can be passed to useActionExecutor
 */
export function useActionFormRenderer(
  objectData?: ObjectDetailDTO,
  customExtractor?: (
    action: ActionDTO,
    objectData?: ObjectDetailDTO
  ) => Record<string, unknown> | undefined
): ActionFormRenderer {
  return useCallback<ActionFormRenderer>(
    ({ action, onSubmit, onCancel, isSubmitting }) => {
      const actionType = action.action as ActionType;
      const FormComponent = getActionFormComponent(actionType);

      // No form registered - action will be executed directly
      if (!FormComponent) {
        return null;
      }

      // Determine default values with priority:
      // 1. Custom extractor (if provided)
      // 2. Registry's extractor (if exists and objectData provided)
      // 3. No defaults
      let defaultValues: Record<string, unknown> | undefined;

      if (customExtractor) {
        // Custom extractor takes precedence
        defaultValues = customExtractor(action, objectData);
      } else if (objectData) {
        // Use registry's extractor if objectData is available
        const registryExtractor = getActionDefaultValuesExtractor(actionType);
        defaultValues = registryExtractor?.(objectData);
      }

      // Render the form with the registry's standardized props
      return (
        <FormComponent
          defaultValues={defaultValues}
          onSubmit={(data) => {
            // Transform the form data into the action body format
            onSubmit({
              action: actionType,
              data,
            } as Parameters<typeof onSubmit>[0]);
          }}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    },
    [objectData, customExtractor]
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
 * const renderForm = useActionFormRendererWithContext(data, extractor);
 *
 * // New way:
 * const renderForm = useActionFormRenderer(data, extractor);
 * ```
 */
export function useActionFormRendererWithContext(
  context: ObjectDetailDTO,
  defaultValuesExtractor?: (
    action: ActionDTO,
    context: ObjectDetailDTO
  ) => Record<string, unknown> | undefined
): ActionFormRenderer {
  return useActionFormRenderer(
    context,
    defaultValuesExtractor as
      | ((
          action: ActionDTO,
          objectData?: ObjectDetailDTO
        ) => Record<string, unknown> | undefined)
      | undefined
  );
}
