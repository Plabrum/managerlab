'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal } from 'lucide-react';
import type { ActionData } from '@/components/header-provider';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

interface ObjectActionsProps {
  actionsData: ActionData;
}

export function ObjectActions({ actionsData }: ObjectActionsProps) {
  const {
    actions,
    actionGroup,
    objectId,
    objectData,
    onInvalidate,
    onActionComplete,
  } = actionsData;

  // Use the centralized registry
  const formRenderer = useActionFormRenderer(objectData);

  const executor = useActionExecutor({
    actionGroup,
    objectId,
    renderActionForm: formRenderer,
    onInvalidate,
    onSuccess: (action, response) => {
      onActionComplete?.(action, response);
    },
  });

  const availableActions = actions.filter(
    (action) => action.available !== false
  );

  if (availableActions.length === 0) {
    return null;
  }

  // Sort by priority and extract primary action
  const sortedActions = availableActions.sort(
    (a, b) => (a.priority || 0) - (b.priority || 0)
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
              {remainingActions.map((action, index) => (
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

      {executor.showForm &&
        executor.pendingAction &&
        executor.renderActionForm && (
          <ActionFormDialog
            open={executor.showForm}
            action={executor.pendingAction}
            isExecuting={executor.isExecuting}
            onCancel={executor.cancelAction}
          >
            {executor.renderActionForm({
              action: executor.pendingAction,
              onSubmit: executor.executeWithData,
              onCancel: executor.cancelAction,
              isSubmitting: executor.isExecuting,
            })}
          </ActionFormDialog>
        )}
    </>
  );
}
