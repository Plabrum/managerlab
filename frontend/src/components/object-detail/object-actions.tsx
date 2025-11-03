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

type ObjectActionsProps = ObjectActionData | TopLevelActionData;

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

  return (
    <>
      <div className="flex items-center gap-2">
        {/* Primary action button */}
        <Button
          variant="default"
          size="sm"
          onClick={() => executor.initiateAction(primaryAction)}
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
                  onClick={() => executor.initiateAction(action)}
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

      {executor.pendingAction &&
        executor.renderActionForm &&
        executor.renderActionForm({
          action: executor.pendingAction,
          onSubmit: executor.executeWithData,
          onClose: executor.cancelAction,
          isSubmitting: executor.isExecuting,
          isOpen: executor.showForm,
          actionLabel: executor.pendingAction.label,
        })}
    </>
  );
}
