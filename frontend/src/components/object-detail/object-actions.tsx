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
import type { ActionDTO } from '@/openapi/ariveAPI.schemas';
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
  const actions = isObjectAction
    ? (props.data.actions ?? [])
    : (props.actions ?? []);
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

  // Sort by priority and extract primary and secondary actions
  const sortedActions = availableActions.sort(
    (a: ActionDTO, b: ActionDTO) => (a.priority || 0) - (b.priority || 0)
  );
  const [primaryAction, secondaryAction, ...remainingActions] = sortedActions;

  // Helper to check if an action is an edit-mode action (distinct from update actions)
  // Edit actions toggle edit mode UI, while update actions show forms to modify data
  const isEditModeAction = (action: ActionDTO) => {
    return action.action.endsWith('__edit');
  };

  // Find the edit action (needed for external edit mode handling)
  const editAction = availableActions.find(isEditModeAction);

  // Handler for action clicks - uses external edit mode for edit actions if provided
  const handleActionClick = (action: ActionDTO) => {
    if (isEditModeAction(action) && props.editMode) {
      // Toggle between open and close based on current state
      if (props.editMode.isOpen) {
        props.editMode.onClose();
      } else {
        props.editMode.onOpen();
      }
    } else {
      executor.initiateAction(action);
    }
  };

  // Helper to get the action label - returns "Finish editing" for edit actions when in edit mode
  const getActionLabel = (action: ActionDTO) => {
    if (isEditModeAction(action) && props.editMode?.isOpen) {
      return 'Finish editing';
    }
    return action.label;
  };

  // Determine which action/state to use for form rendering
  // External edit mode takes precedence for edit actions
  const formAction =
    props.editMode?.isOpen && editAction ? editAction : executor.pendingAction;
  const formIsOpen =
    props.editMode?.isOpen && editAction
      ? props.editMode.isOpen
      : executor.showForm;
  const formOnClose =
    props.editMode?.isOpen && editAction
      ? props.editMode.onClose
      : executor.cancelAction;

  return (
    <>
      <div className="flex items-center gap-2">
        {/* Primary action button - hidden on mobile */}
        <Button
          variant="default"
          size="sm"
          onClick={() => handleActionClick(primaryAction)}
          className="hidden md:inline-flex"
        >
          {getActionLabel(primaryAction)}
        </Button>

        {/* Secondary action button - hidden on mobile, shown on desktop if exists */}
        {secondaryAction && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleActionClick(secondaryAction)}
            className="hidden md:inline-flex"
          >
            {getActionLabel(secondaryAction)}
          </Button>
        )}

        {/* Dropdown menu - shows all actions on mobile, remaining actions on desktop */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {/* On mobile: show primary action */}
            <DropdownMenuItem
              onClick={() => handleActionClick(primaryAction)}
              className="cursor-pointer md:hidden"
            >
              {getActionLabel(primaryAction)}
            </DropdownMenuItem>
            {/* On mobile: show secondary action if exists */}
            {secondaryAction && (
              <DropdownMenuItem
                onClick={() => handleActionClick(secondaryAction)}
                className="cursor-pointer md:hidden"
              >
                {getActionLabel(secondaryAction)}
              </DropdownMenuItem>
            )}
            {/* Remaining actions shown on all screen sizes */}
            {remainingActions.map((action: ActionDTO, index: number) => (
              <DropdownMenuItem
                key={`${action.action}-${index}`}
                onClick={() => handleActionClick(action)}
                className="cursor-pointer"
              >
                {getActionLabel(action)}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
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
