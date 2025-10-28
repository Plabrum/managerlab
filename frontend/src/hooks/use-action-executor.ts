import { useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import type {
  ActionDTO,
  ActionGroupType,
  ActionExecutionResponse,
  ActionsActionGroupExecuteActionBody,
  ActionsActionGroupObjectIdExecuteObjectActionBody,
} from '@/openapi/managerLab.schemas';
import {
  useActionsActionGroupExecuteAction,
  useActionsActionGroupObjectIdExecuteObjectAction,
} from '@/openapi/actions/actions';

export type ActionExecutorState = {
  isExecuting: boolean;
  pendingAction: ActionDTO | null;
  showConfirmation: boolean;
  showForm: boolean;
  error: string | null;
};

export type ActionFormRenderer = (props: {
  action: ActionDTO;
  onSubmit: (
    data:
      | ActionsActionGroupExecuteActionBody
      | ActionsActionGroupObjectIdExecuteObjectActionBody
  ) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}) => React.ReactNode | null;

export type ActionExecutorOptions = {
  actionGroup: ActionGroupType;
  objectId?: string;
  onSuccess?: (action: ActionDTO, response: ActionExecutionResponse) => void;
  onError?: (action: ActionDTO, error: Error) => void;
  renderActionForm?: ActionFormRenderer;
  onInvalidate?: (
    queryClient: ReturnType<typeof useQueryClient>,
    action: ActionDTO,
    response: ActionExecutionResponse
  ) => void;
};

/**
 * Hook to handle action execution with confirmation and form dialogs
 */
export function useActionExecutor({
  actionGroup,
  objectId,
  onSuccess,
  onError,
  renderActionForm,
  onInvalidate,
}: ActionExecutorOptions) {
  const queryClient = useQueryClient();
  const router = useRouter();
  const [state, setState] = useState<ActionExecutorState>({
    isExecuting: false,
    pendingAction: null,
    showConfirmation: false,
    showForm: false,
    error: null,
  });

  // Mutations for executing actions
  const executeGroupActionMutation = useActionsActionGroupExecuteAction();
  const executeObjectActionMutation =
    useActionsActionGroupObjectIdExecuteObjectAction();

  /**
   * Execute an action with optional data
   */
  const executeAction = useCallback(
    async (
      action: ActionDTO,
      actionBody?:
        | ActionsActionGroupExecuteActionBody
        | ActionsActionGroupObjectIdExecuteObjectActionBody
    ) => {
      setState((prev) => ({ ...prev, isExecuting: true, error: null }));

      try {
        // Use provided action body or build default one
        const requestBody =
          actionBody || ({ action: action.action, data: {} } as const);

        let response: ActionExecutionResponse;

        // Execute with proper typing based on whether we have an objectId
        if (objectId) {
          response = await executeObjectActionMutation.mutateAsync({
            actionGroup,
            objectId,
            data: requestBody as ActionsActionGroupObjectIdExecuteObjectActionBody,
          });
        } else {
          response = await executeGroupActionMutation.mutateAsync({
            actionGroup,
            data: requestBody as ActionsActionGroupExecuteActionBody,
          });
        }

        // Show success toast using response message
        toast.success(
          response.message || `${action.label} completed successfully`
        );

        // Invalidate queries based on response metadata
        if (onInvalidate) {
          // Custom invalidation logic provided
          onInvalidate(queryClient, action, response);
        } else if (
          response.invalidate_queries &&
          response.invalidate_queries.length > 0
        ) {
          // Use invalidation queries from response
          response.invalidate_queries.forEach((queryKey) => {
            queryClient.invalidateQueries({
              queryKey: [queryKey],
              refetchType: 'active',
            });
          });
        }

        // Call success callback
        onSuccess?.(action, response);

        // Handle action result based on response metadata
        if (response.action_result) {
          // Type narrowing based on which fields are present
          if ('path' in response.action_result) {
            // RedirectActionResult
            const path = (response.action_result as { path: string }).path;
            if (path === '..') {
              // Navigate to parent (for delete actions)
              const currentPath = window.location.pathname;
              const parentPath = currentPath.substring(
                0,
                currentPath.lastIndexOf('/')
              );
              if (parentPath) {
                router.push(parentPath);
              }
            } else {
              // Navigate to specific path (for create actions)
              router.push(path);
            }
          } else if (
            'url' in response.action_result &&
            'filename' in response.action_result
          ) {
            // DownloadFileActionResult - trigger browser download
            const { url, filename } = response.action_result as {
              url: string;
              filename: string;
            };
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }
        }

        // Reset state
        setState({
          isExecuting: false,
          pendingAction: null,
          showConfirmation: false,
          showForm: false,
          error: null,
        });

        return response;
      } catch (err) {
        const error = err as Error;
        const errorMessage =
          error.message || `Failed to execute ${action.label}`;

        setState((prev) => ({
          ...prev,
          isExecuting: false,
          error: errorMessage,
        }));

        toast.error(errorMessage);
        onError?.(action, error);

        throw error;
      }
    },
    [
      actionGroup,
      objectId,
      queryClient,
      router,
      executeGroupActionMutation,
      executeObjectActionMutation,
      onInvalidate,
      onSuccess,
      onError,
    ]
  );

  /**
   * Initiate an action - will show confirmation or form if needed
   */
  const initiateAction = useCallback(
    (action: ActionDTO) => {
      // Check if this action has a custom form renderer
      const hasCustomForm = renderActionForm
        ? renderActionForm({
            action,
            onSubmit: () => {},
            onCancel: () => {},
            isSubmitting: false,
          }) !== null
        : false;

      // If action has custom form, show form dialog
      if (hasCustomForm) {
        setState((prev) => ({
          ...prev,
          pendingAction: action,
          showForm: true,
        }));
        return;
      }

      // If action has confirmation message, show confirmation dialog
      if (action.confirmation_message) {
        setState((prev) => ({
          ...prev,
          pendingAction: action,
          showConfirmation: true,
        }));
        return;
      }

      // Execute simple actions directly (no confirmation, no data needed)
      executeAction(action).catch((err) => {
        console.error('Action execution failed:', err);
      });
    },
    [executeAction, renderActionForm]
  );

  /**
   * Confirm and execute the pending action
   */
  const confirmAction = useCallback(() => {
    if (state.pendingAction) {
      executeAction(state.pendingAction);
    }
  }, [state.pendingAction, executeAction]);

  /**
   * Cancel the pending action
   */
  const cancelAction = useCallback(() => {
    setState({
      isExecuting: false,
      pendingAction: null,
      showConfirmation: false,
      showForm: false,
      error: null,
    });
  }, []);

  /**
   * Execute action with form data (full discriminated union)
   */
  const executeWithData = useCallback(
    (
      data:
        | ActionsActionGroupExecuteActionBody
        | ActionsActionGroupObjectIdExecuteObjectActionBody
    ) => {
      if (state.pendingAction) {
        executeAction(state.pendingAction, data);
      }
    },
    [state.pendingAction, executeAction]
  );

  /**
   * Show form for an action
   */
  const showFormForAction = useCallback((action: ActionDTO) => {
    setState((prev) => ({
      ...prev,
      pendingAction: action,
      showForm: true,
    }));
  }, []);

  return {
    ...state,
    initiateAction,
    confirmAction,
    cancelAction,
    executeWithData,
    showFormForAction,
    renderActionForm,
  };
}
