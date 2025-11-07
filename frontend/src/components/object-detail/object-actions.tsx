'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal } from 'lucide-react';
import type { ObjectActionData, TopLevelActionData } from '@/types/actions';
import type { ActionDTO } from '@/openapi/managerLab.schemas';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';

type ObjectActionsProps = (ObjectActionData | TopLevelActionData) & {
  /** External edit mode state (controlled by URL params) */
  editMode?: {
    isOpen: boolean;
    onOpen: () => void;
    onClose: () => void;
  };
};

export function ObjectActions(props: ObjectActionsProps) {
  // Type narrow to determine if this is object-level or top-level actions
  const isObjectAction = 'data' in props;

  const actionGroup = props.actionGroup;
  const onActionComplete = props.onActionComplete;

  // Extract appropriate values based on action type
  const objectId = isObjectAction ? String(props.data.id) : undefined;
  const actions = isObjectAction ? props.data.actions : (props.actions ?? []);
  const objectData = isObjectAction ? props.data : undefined;

  // Use the centralized registry
  const formRenderer = useActionFormRenderer(objectData);

  const executor = useActionExecutor({
    actionGroup,
    objectId,
    renderActionForm: formRenderer,
    onInvalidate:
      isObjectAction && props.onRefetch
        ? () => props.onRefetch?.()
        : !isObjectAction && props.onInvalidate
          ? () => props.onInvalidate?.()
          : undefined,
    onSuccess: (action, response) => {
      onActionComplete?.(action, response);
    },
  });

  const availableActions = actions.filter(
    (action: ActionDTO) => action.available !== false
  );

  if (availableActions.length === 0) {
    return null;
  }

  // Sort by priority and extract primary action
  const sortedActions = availableActions.sort(
    (a: ActionDTO, b: ActionDTO) => (a.priority || 0) - (b.priority || 0)
  );
  const [primaryAction, ...remainingActions] = sortedActions;

  // Helper to check if an action is an update/edit action
  const isUpdateAction = (action: ActionDTO) => {
    return action.action.includes('_update') || action.action.includes('_edit');
  };

  // Find the update action (needed for external edit mode rendering)
  const updateAction = availableActions.find(isUpdateAction);

  // Handler for action clicks - uses external edit mode for update actions if provided
  const handleActionClick = (action: ActionDTO) => {
    if (isUpdateAction(action) && props.editMode) {
      props.editMode.onOpen();
    } else {
      executor.initiateAction(action);
    }
  };

  // Determine which action/state to use for form rendering
  // External edit mode takes precedence for update actions
  const formAction =
    props.editMode?.isOpen && updateAction
      ? updateAction
      : executor.pendingAction;
  const formIsOpen =
    props.editMode?.isOpen && updateAction
      ? props.editMode.isOpen
      : executor.showForm;
  const formOnClose =
    props.editMode?.isOpen && updateAction
      ? props.editMode.onClose
      : executor.cancelAction;

  return (
    <>
      <div className="flex items-center gap-2">
        {/* Primary action button */}
        <Button
          variant="default"
          size="sm"
          onClick={() => handleActionClick(primaryAction)}
        >
          {primaryAction.label}
        </Button>

        {/* Dropdown for remaining actions */}
        {remainingActions.length > 0 && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {remainingActions.map((action: ActionDTO, index: number) => (
                <DropdownMenuItem
                  key={`${action.action}-${index}`}
                  onClick={() => handleActionClick(action)}
                  className="cursor-pointer"
                >
                  {action.label}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>

      <ActionConfirmationDialog
        open={executor.showConfirmation}
        action={executor.pendingAction}
        isExecuting={executor.isExecuting}
        onConfirm={executor.confirmAction}
        onCancel={executor.cancelAction}
      />

      {/* Unified form rendering - works with both internal and external state */}
      {formAction &&
        executor.renderActionForm &&
        executor.renderActionForm({
          action: formAction,
          onSubmit: executor.executeWithData,
          onClose: formOnClose,
          isSubmitting: executor.isExecuting,
          isOpen: formIsOpen,
          actionLabel: formAction.label,
        })}
    </>
  );
}
