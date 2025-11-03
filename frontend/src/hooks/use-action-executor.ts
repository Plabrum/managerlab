import { useState } from 'react';
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
import { executeActionApi } from './action-executor/execute-action-api';
import { handleQueryInvalidation } from './action-executor/handle-query-invalidation';
import { handleActionResult } from './action-executor/handle-action-result';

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
    backendQueryKeys: string[]
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
  async function executeAction(
    action: ActionDTO,
    actionBody?:
      | ActionsActionGroupExecuteActionBody
      | ActionsActionGroupObjectIdExecuteObjectActionBody
  ) {
    setState((prev) => ({ ...prev, isExecuting: true, error: null }));

    try {
      // Execute API call
      const response = await executeActionApi({
        action,
        actionGroup,
        objectId,
        actionBody,
        executeGroupActionMutation,
        executeObjectActionMutation,
      });

      // Show success toast using response message
      toast.success(
        response.message || `${action.label} completed successfully`
      );

      // Handle query invalidation
      handleQueryInvalidation(queryClient, response, onInvalidate);

      // Call success callback
      onSuccess?.(action, response);

      // Handle action result (redirects, downloads)
      handleActionResult(response, router);

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
      const errorMessage = error.message || `Failed to execute ${action.label}`;

      setState((prev) => ({
        ...prev,
        isExecuting: false,
        error: errorMessage,
      }));

      toast.error(errorMessage);
      onError?.(action, error);

      throw error;
    }
  }

  /**
   * Check if action has a custom form
   */
  function hasCustomForm(action: ActionDTO): boolean {
    if (!renderActionForm) {
      return false;
    }
    return (
      renderActionForm({
        action,
        onSubmit: () => {},
        onCancel: () => {},
        isSubmitting: false,
      }) !== null
    );
  }

  /**
   * Initiate an action - will show confirmation or form if needed
   */
  function initiateAction(action: ActionDTO) {
    // If action has custom form, show form dialog
    if (hasCustomForm(action)) {
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
  }

  /**
   * Confirm and execute the pending action
   */
  function confirmAction() {
    if (state.pendingAction) {
      executeAction(state.pendingAction);
    }
  }

  /**
   * Cancel the pending action
   */
  function cancelAction() {
    setState({
      isExecuting: false,
      pendingAction: null,
      showConfirmation: false,
      showForm: false,
      error: null,
    });
  }

  /**
   * Execute action with form data (full discriminated union)
   */
  function executeWithData(
    data:
      | ActionsActionGroupExecuteActionBody
      | ActionsActionGroupObjectIdExecuteObjectActionBody
  ) {
    if (state.pendingAction) {
      executeAction(state.pendingAction, data);
    }
  }

  return {
    ...state,
    initiateAction,
    confirmAction,
    cancelAction,
    executeWithData,
    renderActionForm,
  };
}
