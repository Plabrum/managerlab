'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal } from 'lucide-react';
import type {
  ActionDTO,
  ActionGroupType,
  ActionExecutionResponse,
  ObjectDetailDTO,
} from '@/openapi/managerLab.schemas';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { useActionFormRenderer } from '@/hooks/use-action-form-renderer';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

interface ObjectActionsProps {
  actions: ActionDTO[];
  actionGroup: ActionGroupType;
  objectId: string;
  onActionComplete?: (
    action: ActionDTO,
    response: ActionExecutionResponse
  ) => void;
  objectData?: ObjectDetailDTO;
}

export function ObjectActions({
  actions,
  actionGroup,
  objectId,
  onActionComplete,
  objectData,
}: ObjectActionsProps) {
  // Use the centralized registry
  const formRenderer = useActionFormRenderer(objectData);

  const executor = useActionExecutor({
    actionGroup,
    objectId,
    renderActionForm: formRenderer,
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

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm">
            <MoreHorizontal className="mr-2 h-4 w-4" />
            Actions
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {availableActions
            .sort((a, b) => (a.priority || 0) - (b.priority || 0))
            .map((action, index) => (
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
